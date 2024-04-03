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

    # Ottiene il numero totale di pagine usando il PDFManager
    total_pages = PDFManager.get_total_pages(args.pdf_path)
    print("total pages", total_pages)

    ocr_processor = OCRProcessor()
    extractions = []

    page_block_size = 50  # Dimensione del blocco di pagine
    start_page = 1

    while start_page <= total_pages:
        end_page = min(start_page + page_block_size - 1, total_pages)
        print("l'ultima pagina del blocco", end_page)
        images = PDFManager.convert_pdf_to_images(
            args.pdf_path, start_page=start_page, end_page=end_page
        )

        for page_num, image in enumerate(images, start=start_page):
            print(f"Elaborazione pagina {page_num}")
            text = ocr_processor.find_yellow_highlights_and_extract_text(image)
            cleaned_text = clean_text(text)
            if cleaned_text:
                extractions.append(f"Page {page_num}: {cleaned_text}")

        start_page += page_block_size  # Prepara il blocco successivo

    with open("text_extractions.txt", "w") as file:
        for extraction in extractions:
            file.write(f"- {extraction}\n")

    print("Extractions completed and saved to 'text_extractions.txt'.")


if __name__ == "__main__":
    main()
