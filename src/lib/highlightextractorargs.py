import argparse
from typing import Any


class HighlightExtractorArgsParseExcetion(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class HighlightExtractorArgs:
    GENERAL_DESCRIPTION = 'Extract text from yellow highlighted areas in a PDF.'

    PDF_PATH_ARG_NAME = 'pdf_filename'
    PDF_PATH_ARG_DESCRIPTION = 'The path to the PDF file to analyze.'

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description=self.GENERAL_DESCRIPTION
        )
        self.parser.add_argument(self.PDF_PATH_ARG_NAME, help=self.PDF_PATH_ARG_DESCRIPTION)

        self.args = None

    def parse(self):
        self.args = self.parser.parse_args()

    @property
    def pdf_filename(self) -> Any:
        if self.args is None:
            raise HighlightExtractorArgsParseExcetion('No args parsed, maybe you forgot to call parse() method?')
        return getattr(self.args, self.PDF_PATH_ARG_NAME)
