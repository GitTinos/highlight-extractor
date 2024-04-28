import argparse

from utils import clean_text, start_progress_bar

import settings
from lib import HighlightExtractorArgs
from lib import PDFHighlighetTextExtractor, PDFImageOcrStrategy
from lib import ReportWriter


def main():
    args = HighlightExtractorArgs()
    args.parse()

    # Define the PDF highlighted text extractor strategy to use.
    #
    # The strategy used here is to convert the pdf into images and
    # then use the OCR for recognize the highlithed text.
    extract_strategy = PDFImageOcrStrategy()
    extract_strategy.threads_to_use = settings.PDF2IMAGE_THREADS_COUNT

    # Setup the PDF highlighted text extractor.
    pdf_extractor = PDFHighlighetTextExtractor()
    pdf_extractor.filename = args.pdf_filename
    pdf_extractor.extract_strategy = extract_strategy

    # Setup the report writer
    report_writer = ReportWriter()
    report_writer.format = ReportWriter.FORMAT_TXT

    # Perform the extraction
    pdf_extractor.write_report(report_writer=report_writer, output_filename=settings.OUTPUT_FILENAME)


if __name__ == "__main__":
    main()
