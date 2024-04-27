import re
import fitz
from tqdm import tqdm

from .pdf2image import PDF2Image
from .ocr import OCRProcessor


class PDFReader:
    def __init__(self) -> None:
        self._filename = ''
        self._threads_to_use = 1

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def threads_to_use(self):
        return self._threads_to_use

    @threads_to_use.setter
    def threads_to_use(self, value):
        self._threads_to_use = value

    def write_report(self, report_writer, output_filename):
        # Setup PDF2Image
        pdf_2_image = PDF2Image()
        pdf_2_image.pdf_path = self.filename

        # Setup OCRProcessor
        ocr_processor = OCRProcessor()

        # Write the report file
        page_num = 1
        total_page_count = pdf_2_image.get_page_count()
        report_writer.filename = output_filename
        with tqdm(total=total_page_count, desc="Elaborazione", unit="pagina") as progress_bar:
            with report_writer as rw:
                for image in pdf_2_image.generate_images(thread_count=self.threads_to_use, output_folder='/tmp/'):
                    text = ocr_processor.find_yellow_highlights_and_extract_text(image)
                    cleaned_text = self._clean_text(text)
                    if cleaned_text:
                        rw.write_report_line(f"Page {page_num}: {cleaned_text}")
                    page_num += 1
                    progress_bar.update(1)

    def _clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        return text
