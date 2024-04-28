class MissingReportFileException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ReportWriter:
    FORMAT_TXT = 'txt'

    def __init__(self) -> None:
        self._filename = ''
        self._format = 'txt'

        self._file = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, name):
        self._filename = name

    def __enter__(self):
        if not self._filename:
            raise MissingReportFileException('You have to specify the report file filename!')

        self._file = open(self._filename, 'w')
        return self

    def write_report_line(self, line):
        self._file.write(f"{line}\n")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()



