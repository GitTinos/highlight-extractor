from typing import Generator


import os
import platform
import tempfile
import types
import subprocess
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Any, Union, Tuple, List, Dict, Callable
from pathlib import PurePath
from PIL import Image

from pdf2image.generators import uuid_generator, counter_generator, ThreadSafeGenerator

from pdf2image.parsers import (
    parse_buffer_to_pgm,
    parse_buffer_to_ppm,
    parse_buffer_to_jpeg,
    parse_buffer_to_png,
)

from pdf2image.exceptions import (
    PDFSyntaxError,
    PDFPopplerTimeoutError,
)

from pdf2image import pdfinfo_from_path


TRANSPARENT_FILE_TYPES = ["png", "tiff"]
PDFINFO_CONVERT_TO_INT = ["Pages"]


class PDFPathNotSpecified(Exception):
    def __init__(self, *args: object) -> types.NoneType:
        super().__init__(*args)


class PDF2Image:
    def __init__(self) -> types.NoneType:
        self._pdf_path = ''

    @property
    def pdf_path(self):
        return self._pdf_path

    @pdf_path.setter
    def pdf_path(self, value):
        self._pdf_path = value

    def generate_images(
        self,
        dpi: int = 200,
        output_folder: Union[str, PurePath] = None,
        first_page: int = None,
        last_page: int = None,
        fmt: str = "ppm",
        jpegopt: Dict = None,
        thread_count: int = 1,
        userpw: str = None,
        ownerpw: str = None,
        use_cropbox: bool = False,
        strict: bool = False,
        transparent: bool = False,
        single_file: bool = False,
        output_file: Any = uuid_generator(),
        poppler_path: Union[str, PurePath] = None,
        grayscale: bool = False,
        size: Union[Tuple, int] = None,
        paths_only: bool = False,
        use_pdftocairo: bool = False,
        timeout: int = None,
        hide_annotations: bool = False,
    ) -> Generator:
        """Function wrapping pdftoppm and pdftocairo

        :param dpi: Image quality in DPI (default 200), defaults to 200
        :type dpi: int, optional
        :param output_folder: Write the resulting images to a folder (instead of directly in memory), defaults to None
        :type output_folder: Union[str, PurePath], optional
        :param first_page: First page to process, defaults to None
        :type first_page: int, optional
        :param last_page: Last page to process before stopping, defaults to None
        :type last_page: int, optional
        :param fmt: Output image format, defaults to "ppm"
        :type fmt: str, optional
        :param jpegopt: jpeg options `quality`, `progressive`, and `optimize` (only for jpeg format), defaults to None
        :type jpegopt: Dict, optional
        :param thread_count: How many threads we are allowed to spawn for processing, defaults to 1
        :type thread_count: int, optional
        :param userpw: PDF's password, defaults to None
        :type userpw: str, optional
        :param ownerpw: PDF's owner password, defaults to None
        :type ownerpw: str, optional
        :param use_cropbox: Use cropbox instead of mediabox, defaults to False
        :type use_cropbox: bool, optional
        :param strict: When a Syntax Error is thrown, it will be raised as an Exception, defaults to False
        :type strict: bool, optional
        :param transparent: Output with a transparent background instead of a white one, defaults to False
        :type transparent: bool, optional
        :param single_file: Uses the -singlefile option from pdftoppm/pdftocairo, defaults to False
        :type single_file: bool, optional
        :param output_file: What is the output filename or generator, defaults to uuid_generator()
        :type output_file: Any, optional
        :param poppler_path: Path to look for poppler binaries, defaults to None
        :type poppler_path: Union[str, PurePath], optional
        :param grayscale: Output grayscale image(s), defaults to False
        :type grayscale: bool, optional
        :param size: Size of the resulting image(s), uses the Pillow (width, height) standard, defaults to None
        :type size: Union[Tuple, int], optional
        :param paths_only: Don't load image(s), return paths instead (requires output_folder), defaults to False
        :type paths_only: bool, optional
        :param use_pdftocairo: Use pdftocairo instead of pdftoppm, may help performance, defaults to False
        :type use_pdftocairo: bool, optional
        :param timeout: Raise PDFPopplerTimeoutError after the given time, defaults to None
        :type timeout: int, optional
        :param hide_annotations: Hide PDF annotations in the output, defaults to False
        :type hide_annotations: bool, optional
        :raises NotImplementedError: Raised when conflicting parameters are given (hide_annotations for pdftocairo)
        :raises PDFPopplerTimeoutError: Raised after the timeout for the image processing is exceeded
        :raises PDFSyntaxError: Raised if there is a syntax error in the PDF and strict=True
        :return: A list of Pillow images, one for each page between first_page and last_page
        :rtype: List[Image.Image]
        """

        if not self.pdf_path:
            raise PDFPathNotSpecified('You have to specify the .pdf file pagh using PDF2Image "pdf_path" property.')

        if use_pdftocairo and fmt == "ppm":
            fmt = "png"

        # We make sure that if passed arguments are Path objects, they're converted to strings
        pdf_path = self.pdf_path
        if isinstance(pdf_path, PurePath):
            pdf_path = pdf_path.as_posix()

        if isinstance(output_folder, PurePath):
            output_folder = output_folder.as_posix()

        if isinstance(poppler_path, PurePath):
            poppler_path = poppler_path.as_posix()

        page_count = pdfinfo_from_path(
            pdf_path, userpw, ownerpw, poppler_path=poppler_path
        )["Pages"]

        # We start by getting the output format, the buffer processing function and if we need pdftocairo
        parsed_fmt, final_extension, parse_buffer_func, use_pdfcairo_format = self._parse_format(
            fmt, grayscale
        )

        # We use pdftocairo is the format requires it OR we need a transparent output
        use_pdfcairo = (
            use_pdftocairo
            or use_pdfcairo_format
            or (transparent and parsed_fmt in TRANSPARENT_FILE_TYPES)
        )

        poppler_version_major, poppler_version_minor = self._get_poppler_version(
            "pdftocairo" if use_pdfcairo else "pdftoppm", poppler_path=poppler_path
        )

        if poppler_version_major == 0 and poppler_version_minor <= 57:
            jpegopt = None

        if poppler_version_major == 0 and poppler_version_minor <= 83:
            hide_annotations = False

        # If output_file isn't a generator, it will be turned into one
        if not isinstance(output_file, types.GeneratorType) and not isinstance(
            output_file, ThreadSafeGenerator
        ):
            if single_file:
                output_file = iter([output_file])
                thread_count = 1
            else:
                output_file = counter_generator(output_file)

        if thread_count < 1:
            thread_count = 1

        if first_page is None or first_page < 1:
            first_page = 1

        if last_page is None or last_page > page_count:
            last_page = page_count

        if first_page > last_page:
            return []

        try:
            auto_temp_dir = False
            if output_folder is None and use_pdfcairo:
                output_folder = tempfile.mkdtemp()
                auto_temp_dir = True

            # Recalculate page count based on first and last page
            page_count = last_page - first_page + 1

            if thread_count > page_count:
                thread_count = page_count

            reminder = page_count % thread_count
            current_page = first_page
            processes = []
            for _ in range(thread_count):
                thread_output_file = next(output_file)

                # Get the number of pages the thread will be processing
                thread_page_count = page_count // thread_count + int(reminder > 0)
                # Build the command accordingly
                args = self._build_command(
                    ["-r", str(dpi), pdf_path],
                    output_folder,
                    current_page,
                    current_page + thread_page_count - 1,
                    parsed_fmt,
                    jpegopt,
                    thread_output_file,
                    userpw,
                    ownerpw,
                    use_cropbox,
                    transparent,
                    single_file,
                    grayscale,
                    size,
                    hide_annotations,
                )

                if use_pdfcairo:
                    if hide_annotations:
                        raise NotImplementedError(
                            "Hide annotations flag not implemented in pdftocairo."
                        )
                    args = [self._get_command_path("pdftocairo", poppler_path)] + args
                else:
                    args = [self._get_command_path("pdftoppm", poppler_path)] + args

                # Update page values
                current_page = current_page + thread_page_count
                reminder -= int(reminder > 0)
                # Add poppler path to LD_LIBRARY_PATH
                env = os.environ.copy()
                if poppler_path is not None:
                    env["LD_LIBRARY_PATH"] = (
                        poppler_path + ":" + env.get("LD_LIBRARY_PATH", "")
                    )
                # Spawn the process and save its uuid
                startupinfo = None
                if platform.system() == "Windows":
                    # this startupinfo structure prevents a console window from popping up on Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                processes.append(
                    (
                        thread_output_file,
                        Popen(
                            args, env=env, stdout=PIPE, stderr=PIPE, startupinfo=startupinfo
                        ),
                    )
                )

            for uid, proc in processes:
                try:
                    data, err = proc.communicate(timeout=timeout)
                except TimeoutExpired:
                    proc.kill()
                    outs, errs = proc.communicate()
                    raise PDFPopplerTimeoutError("Run poppler timeout.")

                if b"Syntax Error" in err and strict:
                    raise PDFSyntaxError(err.decode("utf8", "ignore"))

                if output_folder is not None:
                    for image in self._load_from_output_folder(
                        output_folder,
                        uid,
                        final_extension,
                        paths_only,
                        in_memory=auto_temp_dir,
                    ):
                        yield image
                else:
                    for image in parse_buffer_func(data):
                        yield image
        finally:
            if auto_temp_dir:
                pass
                # shutil.rmtree(output_folder)

    def get_page_count(self):
        return pdfinfo_from_path(self.pdf_path)["Pages"]

    def _get_poppler_version(
        self, command: str, poppler_path: str = None, timeout: int = None
    ) -> Tuple[int, int]:
        command = [self._get_command_path(command, poppler_path), "-v"]

        env = os.environ.copy()
        if poppler_path is not None:
            env["LD_LIBRARY_PATH"] = poppler_path + ":" + env.get("LD_LIBRARY_PATH", "")
        proc = Popen(command, env=env, stdout=PIPE, stderr=PIPE)

        try:
            data, err = proc.communicate(timeout=timeout)
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            raise PDFPopplerTimeoutError("Run poppler poppler timeout.")

        try:
            # TODO: Make this more robust
            version = err.decode("utf8", "ignore").split("\n")[0].split(" ")[-1].split(".")
            return int(version[0]), int(version[1])
        except:
            # Lowest version that includes pdftocairo (2011)
            return 0, 17

    def _get_command_path(self, command: str, poppler_path: str = None) -> str:
        if platform.system() == "Windows":
            command = command + ".exe"

        if poppler_path is not None:
            command = os.path.join(poppler_path, command)

        return command

    def _load_from_output_folder(
        self,
        output_folder: str,
        output_file: str,
        ext: str,
        paths_only: bool,
        in_memory: bool = False,
    ) -> List[Image.Image]:
        images = []
        for f in sorted(os.listdir(output_folder)):
            if f.startswith(output_file) and f.split(".")[-1] == ext:
                if paths_only:
                    images.append(os.path.join(output_folder, f))
                else:
                    images.append(Image.open(os.path.join(output_folder, f)))
                    if in_memory:
                        images[-1].load()
        return images


    def _build_command(
        self,
        args: List,
        output_folder: str,
        first_page: int,
        last_page: int,
        fmt: str,
        jpegopt: Dict,
        output_file: str,
        userpw: str,
        ownerpw: str,
        use_cropbox: bool,
        transparent: bool,
        single_file: bool,
        grayscale: bool,
        size: Union[int, Tuple[int, int]],
        hide_annotations: bool,
    ) -> List[str]:
        if use_cropbox:
            args.append("-cropbox")

        if hide_annotations:
            args.append("-hide-annotations")

        if transparent and fmt in TRANSPARENT_FILE_TYPES:
            args.append("-transp")

        if first_page is not None:
            args.extend(["-f", str(first_page)])

        if last_page is not None:
            args.extend(["-l", str(last_page)])

        if fmt not in ["pgm", "ppm"]:
            args.append("-" + fmt)

        if fmt in ["jpeg", "jpg"] and jpegopt:
            args.extend(["-jpegopt", self._parse_jpegopt(jpegopt)])

        if single_file:
            args.append("-singlefile")

        if output_folder is not None:
            args.append(os.path.join(output_folder, output_file))

        if userpw is not None:
            args.extend(["-upw", userpw])

        if ownerpw is not None:
            args.extend(["-opw", ownerpw])

        if grayscale:
            args.append("-gray")

        if size is None:
            pass
        elif isinstance(size, tuple) and len(size) == 2:
            if size[0] is not None:
                args.extend(["-scale-to-x", str(int(size[0]))])
            else:
                args.extend(["-scale-to-x", str(-1)])
            if size[1] is not None:
                args.extend(["-scale-to-y", str(int(size[1]))])
            else:
                args.extend(["-scale-to-y", str(-1)])
        elif isinstance(size, tuple) and len(size) == 1:
            args.extend(["-scale-to", str(int(size[0]))])
        elif isinstance(size, int) or isinstance(size, float):
            args.extend(["-scale-to", str(int(size))])
        else:
            raise ValueError(f"Size {size} is not a tuple or an integer")

        return args


    def _parse_format(self, fmt: str, grayscale: bool = False) -> Tuple[str, str, Callable, bool]:
        fmt = fmt.lower()
        if fmt[0] == ".":
            fmt = fmt[1:]
        if fmt in ("jpeg", "jpg"):
            return "jpeg", "jpg", parse_buffer_to_jpeg, False
        if fmt == "png":
            return "png", "png", parse_buffer_to_png, False
        if fmt in ("tif", "tiff"):
            return "tiff", "tif", None, True
        if fmt == "ppm" and grayscale:
            return "pgm", "pgm", parse_buffer_to_pgm, False
        # Unable to parse the format so we'll use the default
        return "ppm", "ppm", parse_buffer_to_ppm, False


    def _parse_jpegopt(self, jpegopt: Dict) -> str:
        parts = []
        for k, v in jpegopt.items():
            if v is True:
                v = "y"
            if v is False:
                v = "n"
            parts.append("{}={}".format(k, v))
        return ",".join(parts)
