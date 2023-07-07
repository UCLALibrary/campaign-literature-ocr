import argparse
from pathlib import Path
from pdf2image import convert_from_path
from pytesseract import image_to_string, image_to_alto_xml, image_to_boxes

# For type-checking
from PIL.PpmImagePlugin import PpmImageFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file_spec",
        help="Files to process (default: all dated PDFs)",
        action="store",
        default="**/19*.pdf",
    )
    args = parser.parse_args()
    process_pdfs(file_spec=args.file_spec)


def process_pdfs(pdf_root: str = "pdfs", file_spec: str = "**/19*.pdf") -> None:
    """Process specified PDFs.  By default, looks for all dated PDFs in pdf_root
    and its subdirectories, skipping 'Campaign Literature Scanning Worksheet.pdf'.
    """
    p = Path(pdf_root)
    for pdf_file in sorted(p.glob(file_spec)):
        base_filename = _get_base_output_filename(pdf_file)
        images = convert_from_path(pdf_file)
        for index, image in enumerate(images, start=1):
            save_ocr_text(image, base_filename, index)
            # These are very verbose
            save_ocr_xml(image, base_filename, index)
            save_ocr_boxes(image, base_filename, index)


def save_ocr_text(image: PpmImageFile, base_filename: str, index: int) -> None:
    """Generate OCR text and save to file."""
    ocr_content = image_to_string(image)
    filename = f"{base_filename}-{index}.txt"
    write_file(filename, ocr_content)


def save_ocr_xml(image: PpmImageFile, base_filename: str, index: int) -> None:
    """Generate ALTO XML and save to file."""
    ocr_content = image_to_alto_xml(image)
    filename = f"{base_filename}-{index}.xml"
    write_file(filename, ocr_content)


def save_ocr_boxes(image: PpmImageFile, base_filename: str, index: int) -> None:
    """Generate bounding box data and save to file."""
    ocr_content = image_to_boxes(image)
    filename = f"{base_filename}-{index}.box"
    write_file(filename, ocr_content)


def write_file(filename: str, ocr_content: str) -> None:
    """Write provided content to provided file, based on filename extension."""

    # Create directory based on extension, if needed - skip the period.
    dirname = Path(filename).suffix[1:]
    directory = get_directory(dirname)
    file_to_write = Path(f"{directory}/{filename}")
    print(f"Writing {file_to_write}...")
    # XML is in bytes
    if dirname == "xml":
        file_to_write.write_bytes(ocr_content)
    else:
        file_to_write.write_text(ocr_content)


def get_directory(dirname: str) -> str:
    """Create specified directory, if needed."""

    # Directory of the currently running script
    parent = Path(__file__).parent
    # Make a subdirectory, if it doesn't already exist
    new_dir = f"{parent}/{dirname}"
    Path(new_dir).mkdir(exist_ok=True)
    return new_dir


def _get_base_output_filename(pdf_file_name: str) -> str:
    """Converts relative path / subdirectories to a flat string
    to be used as the base filename for derivatives.
    Example input: pdfs/1996- President- Perot- General/1996-396-002.pdf
    Example output: 1996-President-Perot-General_1996-396-002
    """
    p = Path(pdf_file_name)
    # Join all subdirectories - all parts except the last;
    # ignore initial directory if it is "pdfs", which it usually will be.
    dirs = "-".join([part for part in p.parts[:-1] if part != "pdfs"])
    # Append the input file name, without the suffix.
    combined = f"{dirs}_{p.stem}"
    # Strip spaces and return the result.
    return combined.replace(" ", "")


if __name__ == "__main__":
    main()
