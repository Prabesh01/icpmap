# https://github.com/matthuisman/gdrivedl/blob/master/gdrivedl.py

#!/usr/bin/env python
from __future__ import unicode_literals
import os
import re
import sys
import unicodedata
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from urllib.request import Request, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

from html import unescape

ITEM_URL = "https://drive.google.com/open?id={id}"
FILE_URL = "https://drive.usercontent.google.com/download?id={id}&export=download&authuser=0"
FOLDER_URL = "https://drive.google.com/embeddedfolderview?id={id}#list"
CHUNKSIZE = 64 * 1024
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

ID_PATTERNS = [
    re.compile("/file/d/([0-9A-Za-z_-]{10,})(?:/|$)", re.IGNORECASE),
    re.compile("/folders/([0-9A-Za-z_-]{10,})(?:/|$)", re.IGNORECASE),
    re.compile("id=([0-9A-Za-z_-]{10,})(?:&|$)", re.IGNORECASE),
    re.compile("([0-9A-Za-z_-]{10,})", re.IGNORECASE),
]
FOLDER_PATTERN = re.compile(
    '<a href="(https://drive.google.com/.*?)".*?<div class="flip-entry-title">(.*?)</div>.*?<div class="flip-entry-last-modified"><div>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
N_FOLDER_PATTERN = re.compile(
    r'<div class="flip-entry-info"><a\s+href="(https://(?:docs|drive)\.google\.com/.*?)".*?'
    r'<div class="flip-entry-title">(.*?)</div>.*?'
    r'<div class="flip-entry-last-modified">\s*<div>(.*?)</div>',
    re.DOTALL | re.IGNORECASE
)
CONFIRM_PATTERNS = [
    re.compile(b"confirm=([0-9A-Za-z_-]+)", re.IGNORECASE),
    re.compile(b"name=\"confirm\"\\s+value=\"([0-9A-Za-z_-]+)\"", re.IGNORECASE),
]
UUID_PATTERN = re.compile(b"name=\"uuid\"\\s+value=\"([0-9A-Za-z_-]+)\"", re.IGNORECASE)

FILENAME_PATTERN = re.compile('filename="(.*?)"', re.IGNORECASE)


def output(text):
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        sys.stdout.write(text.encode("utf8"))


# Big thanks to leo_wallentin for below sanitize function (modified slightly for this script)
# https://gitlab.com/jplusplus/sanitize-filename/-/blob/master/sanitize_filename/sanitize_filename.py
def sanitize(filename):
    blacklist = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "\0"]
    reserved = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]

    filename = unescape(filename).encode("utf8").decode("utf8")
    filename = unicodedata.normalize("NFKD", filename)

    filename = "".join(c for c in filename if c not in blacklist)
    filename = "".join(c for c in filename if 31 < ord(c))
    filename = filename.rstrip(". ")
    filename = filename.strip()

    if all([x == "." for x in filename]):
        filename = "_" + filename
    if filename in reserved:
        filename = "_" + filename
    if len(filename) == 0:
        filename = "_"
    if len(filename) > 255:
        parts = re.split(r"/|\\", filename)[-1].split(".")
        if len(parts) > 1:
            ext = "." + parts.pop()
            filename = filename[: -len(ext)]
        else:
            ext = ""
        if filename == "":
            filename = "_"
        if len(ext) > 254:
            ext = ext[254:]
        maxl = 255 - len(ext)
        filename = filename[:maxl]
        filename = filename + ext
        filename = filename.rstrip(". ")
        if len(filename) == 0:
            filename = "_"

    return filename


def url_to_id(url):
    for pattern in ID_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)


class GDriveDL(object):
    def __init__(self):
        self._continue_on_errors=False
        self._create_empty_dirs = True
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._processed = []
        self._errors = []

    def _error(self, message):
        logging.error(message)
        self._errors.append(message)
        if not self._continue_on_errors:
            sys.exit(1)

    @property
    def errors(self):
        return self._errors

    @contextmanager
    def _request(self, url):
        logging.debug("Requesting: {}".format(url))
        req = Request(url, headers={"User-Agent": USER_AGENT})

        f = self._opener.open(req)
        try:
            yield f
        finally:
            f.close()

    def process_url(self, url, directory, filename=None):
        id = url_to_id(url)
        if not id:
            self._error("{}: Unable to find ID from url".format(url))
            return

        url = url.lower()

        if "://" not in url:
            with self._request(ITEM_URL.format(id=id)) as resp:
                url = resp.geturl()

        if "/file/" in url or "/uc?" in url:
            self.process_file(id, directory, filename=filename)
        elif "/folders/" in url:
            if filename:
                logging.warning("Ignoring --output-document option for folder download")
            self.process_folder(id, directory)
        else:
            self._error("{}: returned an unknown url {}".format(id, url))
            return

    def process_folder(self, id, directory):
        if id in self._processed:
            logging.debug('Skipping already processed folder: {}'.format(id))
            return

        self._processed.append(id)
        with self._request(FOLDER_URL.format(id=id)) as resp:
            html = resp.read().decode("utf-8")

        logging.debug("HTML page contents:\n\n{}\n\n".format(html))

        matches = re.findall(N_FOLDER_PATTERN, html)

        if not matches and "ServiceLogin" in html:
            self._error("{}: does not have link sharing enabled".format(id))
            return

        for match in matches:
            url, item_name, modified = match
            id = url_to_id(url)
            if not id:
                self._error("{}: Unable to find ID from url".format(url))
                continue
            if 'docs.google.com' in url:
                docx_file_path=directory+'/'+item_name+'.docx'
                if not self._exists(docx_file_path, False):
                    logging.info("{file_path}".format(file_path=docx_file_path))
                    with self._request("https://docs.google.com/document/export?format=docx&id="+id) as resp:
                        with open(docx_file_path,'wb') as f:
                            f.write(resp.read())
                else:
                    logging.info("{file_path} [Exists]".format(file_path=docx_file_path))
            elif "/file/" in url.lower():
                self.process_file(
                    id, directory, filename=sanitize(item_name), modified=modified
                )
            elif "/folders/" in url.lower():
                self.process_folder(id, os.path.join(directory, sanitize(item_name)))

        if self._create_empty_dirs and not os.path.exists(directory):
            os.makedirs(directory)
            logging.info("Directory: {directory} [Created]".format(directory=directory))

    def _get_modified(self, modified):
        if not modified:
            return None

        try:
            if ":" in modified:
                hour, minute = modified.lower().split(":")
                if "pm" in minute:
                    hour = int(hour) + 12
                hour = int(hour)+7  # modified is UTC-7 so +7 to utc time
                minute = minute.split(" ")[0]
                now = datetime.utcnow().replace(hour=0, minute=int(minute), second=0, microsecond=0)
                modified = now + timedelta(hours=hour)
            elif "/" in modified:
                modified = datetime.strptime(modified, "%m/%d/%y")
            else:
                now = datetime.utcnow()
                modified = datetime.strptime(modified, "%b %d")
                modified = modified.replace(year=now.year)
        except:
            logging.debug("Failed to convert mtime: {}".format(modified))
            return None

        return int((modified - datetime(1970, 1, 1)).total_seconds())

    def _set_modified(self, file_path, timestamp):
        if not timestamp:
            return

        try:
            os.utime(file_path, (timestamp, timestamp))
        except:
            logging.debug("Failed to set mtime")

    def _exists(self, file_path, modified):
        file_name = os.path.basename(file_path)
        # if file_name.endswith('.iso'): return True
        file_dir = os.path.dirname(file_path)
        prefix = file_name[:2]
        if prefix.isdigit() and int(prefix) < 100:
            arranged_file_path=os.path.join(file_dir+'/'+prefix,file_name)
            if os.path.exists(arranged_file_path):
                file_path=arranged_file_path
            else:
                if not os.path.exists(file_path):
                    return False
        else:        
            if not os.path.exists(file_path):
                return False

        if modified:
            try:
                return int(os.path.getmtime(file_path)) == modified
            except:
                logging.debug("Failed to get mtime")

        return True

    def process_file(self, id, directory,  filename=None, modified=None, confirm="", uuid=""):
        file_path = None
        modified_ts = self._get_modified(modified)

        if filename:
            file_path = (
                filename
                if os.path.isabs(filename)
                else os.path.join(directory, filename)
            )
            if self._exists(file_path, modified_ts):
                logging.info("{file_path} [Exists]".format(file_path=file_path))
                return

        url = FILE_URL.format(id=id)
        if confirm:
            url += '&confirm={}'.format(confirm)
        if uuid:
            url += '&uuid={}'.format(uuid)

        logging.debug("Requesting: {}".format(url))
        with self._request(url) as resp:
            if "ServiceLogin" in resp.url:
                self._error("{}: does not have link sharing enabled".format(id))
                return

            headers = "\n".join(["{}: {}".format(h, resp.headers.get(h)) for h in resp.headers])
            logging.debug("Headers:\n{}".format(headers))

            content_disposition = resp.headers.get("content-disposition")
            if not content_disposition:
                if confirm:
                    # The content-disposition header is an indication that the download confirmation worked
                    self._error("{}: content-disposition not found and confirm={} did not work".format(id, confirm))
                    return

                html = resp.read(CHUNKSIZE)
                logging.debug("HTML:\n{}".format(html))

                if b"Google Drive - Quota exceeded" in html:
                    self._error("{}: Quota exceeded for this file".format(id))
                    return

                for pattern in CONFIRM_PATTERNS:
                    confirm = pattern.search(html)
                    if confirm:
                        break

                uuid = UUID_PATTERN.search(html)
                uuid = uuid.group(1).decode() if uuid else ''

                if confirm:
                    confirm = confirm.group(1).decode()
                    logging.debug("Found confirmation '{}', trying it".format(confirm))
                    return self.process_file(
                        id, directory, filename=filename, modified=modified, confirm=confirm, uuid=uuid
                    )
                else:
                    logging.debug("Trying confirmation 't' as a last resort")
                    return self.process_file(
                        id, directory, filename=filename, modified=modified, confirm='t', uuid=uuid
                    )

            if not file_path:
                filename = FILENAME_PATTERN.search(content_disposition).group(1)
                file_path = os.path.join(directory, sanitize(filename))
                if self._exists(file_path, modified_ts):
                    logging.info("{file_path} [Exists]".format(file_path=file_path))
                    return

            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                logging.info(
                    "Directory: {directory} [Created]".format(directory=directory)
                )

            try:
                with open(file_path, "wb") as f:
                    dl = 0
                    last_out = 0
                    while True:
                        chunk = resp.read(CHUNKSIZE)
                        if not chunk:
                            break

                        if (
                            b"Too many users have viewed or downloaded this file recently"
                            in chunk
                        ):
                            self._error("{}: Quota exceeded for this file".format(id))
                            return

                        dl += len(chunk)
                        f.write(chunk)
                        if (
                            not last_out or dl - last_out > 1048576
                        ):
                            output(
                                "\r{} {:.2f}MB".format(
                                    file_path,
                                    dl / 1024 / 1024,
                                )
                            )
                            last_out = dl
                            sys.stdout.flush()
            except:
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise
            else:
                self._set_modified(file_path, modified_ts)

        output("\n")


def donwload_gdrive(url,dir):
    gdrive = GDriveDL()

    level = logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)

    logging.info('Processing {}'.format(url))


    gdrive.process_url(
        url, directory=dir
    )

    if gdrive.errors:
        sys.exit(1)
