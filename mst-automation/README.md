windows setup:
- files_download.py:
  - git config --system core.longpaths true
  - change `%-I%p` in strftime to `%#I%p`
- convert_to_pdf_and_merge.py:
  - change `libreoffice` to `C:\Program Files\LibreOffice\program\soffice.exe`

requirements:
- files_download.py
```
pytz
requests
dateutil
python-dateutil
```
- convert_to_pdf_and_merge.py
```
pypdf
```
