import argparse

from pdf_manager import PDFManager
from ocr import OCRProcessor
from utils import clean_text


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from yellow highlighted areas in a PDF."
    )
    parser.add_argument("pdf_path", help="The path to the PDF file to analyze.")
    args = parser.parse_args()

    ocr_processor = OCRProcessor()

    extractions = []
    images = PDFManager.convert_pdf_to_images(args.pdf_path)
    for page_num, image in enumerate(images):
        text = ocr_processor.find_yellow_highlights_and_extract_text(image)
        cleaned_text = clean_text(text)
        if cleaned_text:
            extractions.append(f"Page {page_num + 1}: {cleaned_text}")

    with open("text_extractions.txt", "w") as file:
        for extraction in extractions:
            file.write(f"- {extraction}\n")

    print("Extractions completed and saved to 'text_extractions.txt'.")


if __name__ == "__main__":
    main()
