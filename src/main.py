import argparse

from utils import clean_text, start_progress_bar

import settings
from lib import HighlightExtractorArgs
from lib import PDFReader
from lib import ReportWriter


def main():
    args = HighlightExtractorArgs()
    args.parse()

    pdf_reader = PDFReader()
    pdf_reader.filename = args.pdf_filename
    pdf_reader.threads_to_use = settings.PDF2IMAGE_THREADS_COUNT

    report_writer = ReportWriter()
    report_writer.format = ReportWriter.FORMAT_TXT

    pdf_reader.write_report(report_writer=report_writer, output_filename=settings.OUTPUT_FILENAME)


if __name__ == "__main__":
    main()
