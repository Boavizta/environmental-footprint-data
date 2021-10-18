"""Common PDF tools to be used in our scrapers."""
from io import BytesIO
import typing
from typing import BinaryIO, Iterator

import fitz
import numpy as np
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage

if typing.TYPE_CHECKING:
    from typing import Any


def pdf2txt(pdf_file: BinaryIO) -> str:
    """Read all text from a PDF."""

    rsrcmgr = PDFResourceManager()
    with BytesIO() as retstr:
        with TextConverter(rsrcmgr, retstr) as device:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(pdf_file, check_extractable=True):
                interpreter.process_page(page)
        text = retstr.getvalue()
        return text.decode('utf-8')


def list_images(pdf_file: BinaryIO) -> Iterator['np.ndarray[Any, Any]']:
    """List all images from a PDF."""
    pdf_doc = fitz.open('pdf', pdf_file)
    for page in pdf_doc:
        for image in page.getImageList():
            xref = image[0]
            pix_image = fitz.Pixmap(pdf_doc, xref)
            numpy_array = np.frombuffer(pix_image.samples, dtype=np.uint8)  # type: ignore
            numpy_array = numpy_array.reshape(pix_image.h, pix_image.w, pix_image.n)
            numpy_image = np.ascontiguousarray(numpy_array[..., [2, 1, 0]])  # rgb to bgr
            yield numpy_image
