prompt="""
give me a minimal python script that does the following:
- takes a path as input
- list the folders in the path. ignores the files. ignores the folder named "merged". goes inside each of the remaining folders in the path. remember the name of the folder. lets say it is "abc".
- delete the existing folder named "converted" and again creates a folder named "converted".
- processes all the files in folder. ignores the folders: if the file is pdf copy it to the converted folder. if the file is docx, txt or pptc convert it to pdf and save in "converted" folder.
- merge all the pdfs in the "converted" folder and save it in the "merged" folder inside the input path create. create the "merged" folder if not exists. save the file as "abc.pdf". abc is the folder name remembered earlier.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from pypdf import PdfWriter


def convert_to_pdf(file_path, output_dir):
    """Convert docx, txt, or pptx to pdf using LibreOffice."""
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(file_path)],
        check=True, capture_output=True
    )


def process_folder(folder_path, merged_dir):
    folder_name = folder_path.name
    converted_dir = folder_path / "converted"

    # Reset converted folder
    if converted_dir.exists():
        shutil.rmtree(converted_dir)
    converted_dir.mkdir()

    # Process files (ignore subfolders)
    for file in folder_path.iterdir():
        if not file.is_file():
            continue
        suffix = file.suffix.lower()
        if suffix == ".pdf":
            shutil.copy2(file, converted_dir / file.name)
        elif suffix in (".docx", ".txt", ".pptx"):
            convert_to_pdf(file, converted_dir)

    # Merge all PDFs in converted folder
    pdfs = sorted(converted_dir.glob("*.pdf"))
    if not pdfs:
        print(f"  No PDFs to merge in {folder_name}, skipping.")
        return

    writer = PdfWriter()
    for pdf in pdfs:
        writer.append(str(pdf))

    merged_dir.mkdir(exist_ok=True)
    output_path = merged_dir / f"{folder_name}.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"  Merged {len(pdfs)} PDFs -> {output_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python merge_docs.py <path>")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    merged_dir = input_path / "merged"

    folders = [
        f for f in input_path.iterdir()
        if f.is_dir() and f.name != "merged"
    ]

    if not folders:
        print("No folders found.")
        sys.exit(0)

    for folder in folders:
        print(f"Processing: {folder.name}")
        process_folder(folder, merged_dir)


if __name__ == "__main__":
    main()
