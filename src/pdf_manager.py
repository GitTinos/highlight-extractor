from pdf2image import convert_from_path


class PDFManager:
    @staticmethod
    def convert_pdf_to_images(pdf_path):
        return convert_from_path(pdf_path, dpi=300)
