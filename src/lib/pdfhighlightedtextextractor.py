import re
import fitz
from tqdm import tqdm

from .pdf2image import PDF2Image
from .ocr import OCRProcessor


class PDFImageOcrStrategy:
    """
    Convert the .pdf file into multiple images and use OCT for recognize
    highlighet text
    """
    def __init__(self) -> None:
        self._filename = ''
        self._threads_to_use = 1
        self.pdf_2_image = PDF2Image()
        self.ocr_processor = OCRProcessor()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self.pdf_2_image.pdf_path = value
        self._filename = value

    @property
    def threads_to_use(self):
        return self._threads_to_use

    @threads_to_use.setter
    def threads_to_use(self, value):
        self._threads_to_use = value

    def get_pages_count(self):
        return self.pdf_2_image.get_page_count()

    def read_highlighted_lines(self):
        for image in self.pdf_2_image.generate_images(thread_count=self.threads_to_use, output_folder='/tmp/'):
            text = self.ocr_processor.find_yellow_highlights_and_extract_text(image)
            yield self._clean_text(text)

    def _clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        return text


class PDFHighlighetTextExtractor:
    def __init__(self) -> None:
        self._filename = ''
        self._extract_strategy = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def extract_strategy(self):
        return self._extract_strategy

    @extract_strategy.setter
    def extract_strategy(self, value):
        self._extract_strategy = value

    def write_report(self, report_writer, output_filename):
        # Setup the strategy
        self.extract_strategy.filename = self.filename

        # Write the report file
        page_num = 1
        total_page_count = self.extract_strategy.get_pages_count()
        report_writer.filename = output_filename
        with tqdm(total=total_page_count, desc="Elaborazione", unit="pagina") as progress_bar:
            with report_writer as rw:
                for extracted_text in self.extract_strategy.read_highlighted_lines():
                    if extracted_text:
                        rw.write_report_line(f"Page {page_num}: {extracted_text}")
                    page_num += 1
                    progress_bar.update(1)
