from pdf2image import convert_from_path
import fitz


class PDFManager:
    @staticmethod
    def convert_pdf_to_images(pdf_path, dpi=300, timeout=600, start_page=None, end_page=None):
        return convert_from_path(pdf_path, dpi=dpi, first_page=start_page, last_page=end_page, timeout=timeout)

    @staticmethod
    def get_total_pages(pdf_path):
        with fitz.open(pdf_path) as doc:
            return doc.page_count
