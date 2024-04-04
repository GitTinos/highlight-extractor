import argparse
import gc

from pdf_manager import PDFManager
from ocr import OCRProcessor
from utils import clean_text, start_progress_bar


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from yellow highlighted areas in a PDF."
    )
    parser.add_argument("pdf_path", help="The path to the PDF file to analyze.")
    args = parser.parse_args()

    total_pages = PDFManager.get_total_pages(args.pdf_path)
    ocr_processor = OCRProcessor()
    extractions = []

    # progress_bar = start_progress_bar(total_pages)

    # Imposta l'elaborazione pagina per pagina
    for start_page in range(1, total_pages + 1):
        images = PDFManager.convert_pdf_to_images(
            args.pdf_path, start_page=start_page, end_page=start_page
        )

        for page_num, image in enumerate(images, start=start_page):
            text = ocr_processor.find_yellow_highlights_and_extract_text(image)
            cleaned_text = clean_text(text)
            print((f"Page {page_num}: {cleaned_text}"))
            if cleaned_text:
                extractions.append(f"Page {page_num}: {cleaned_text}")
            # progress_bar.update(1)

        # Distruggi esplicitamente l'oggetto image e chiama il garbage collector
        del images
        gc.collect()

    # progress_bar.close()

    with open("text_extractions.txt", "w") as file:
        for extraction in extractions:
            file.write(f"- {extraction}\n")

    print("Extractions completed and saved to 'text_extractions.txt'.")


if __name__ == "__main__":
    main()
