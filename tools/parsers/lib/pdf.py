"""Common PDF tools to be used in our scrapers."""
from io import BytesIO
import typing
from typing import BinaryIO, Iterator, Optional, Tuple

import fitz
import numpy as np
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage

if typing.TYPE_CHECKING:
    from typing import Any


def pdf2txt(pdf_file: BinaryIO, num_pages: Optional[int] = None) -> str:
    """Read all text from a PDF."""

    rsrcmgr = PDFResourceManager()
    with BytesIO() as retstr:
        with TextConverter(rsrcmgr, retstr) as device:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for index_page, page in enumerate(PDFPage.get_pages(pdf_file, check_extractable=True)):
                if num_pages and index_page >= num_pages:
                    break
                interpreter.process_page(page)
        text = retstr.getvalue()
        return text.decode('utf-8')


def search_text(pdf_file: BinaryIO, needle: str) -> Iterator[Tuple[fitz.Rect, fitz.Page]]:
    """Search for a text block in a PDF."""
    with fitz.open('pdf', pdf_file) as pdf_doc:
        for page in pdf_doc:
            text_page = page.get_textpage()
            for rect in text_page.search(needle, quads=False):
                yield rect, page


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

def pdf2img(pdf_file: BinaryIO, page_num: int = 0):
    """Converts pdf page page_num to an image"""
    with fitz.open('pdf', pdf_file) as pdf_doc:
        page = pdf_doc[page_num]
        rotate = int(0)
        zoom = 3
        mat = fitz.Matrix(zoom, zoom).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        numpy_array = np.frombuffer(pix.samples, dtype=np.uint8)
        numpy_array = numpy_array.reshape(pix.h, pix.w, pix.n)
        numpy_image = np.ascontiguousarray(numpy_array[..., [2, 1, 0]])  # rgb to bgr
        return numpy_image