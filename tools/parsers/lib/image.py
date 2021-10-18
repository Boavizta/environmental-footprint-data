"""Modules for helper functions to manipulate images."""
import re
import typing

from typing import NamedTuple, Optional, Pattern

import cv2
import pytesseract

if typing.TYPE_CHECKING:
    from typing import Any
    import numpy as np


def crop(
    image: 'np.ndarray[Any, Any]', *,
    left: float = 0, right: float = 0, top: float = 0, bottom: float = 0,
) -> 'np.ndarray[Any, Any]':
    """Crop an image by removing a percent on one or multiple borders."""
    height, width = image.shape[:2]
    cropped = image[
        int(height * top):int(height * (1 - bottom)),
        int(width * left):int(width * (1 - right)),
    ]
    return typing.cast('np.ndarray[Any, Any]', cropped)


def binary_grey_threshold(
    image: 'np.ndarray[Any, Any]', threshold: float,
) -> 'np.ndarray[Any, Any]':
    """Apply a threhsold on the grayscale of an image. Below the threshold -> 0 and 255 above."""
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary_image = cv2.threshold(grey_image, threshold, 255, cv2.THRESH_BINARY)[1]
    return typing.cast('np.ndarray[Any, Any]', binary_image)


class ImageTextBlock(NamedTuple):
    """A block of an image corresponding to a text, parsed by Tesseract."""
    level: int
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    word_num: int
    left: int
    top: int
    width: int
    height: int
    conf: int
    text: str


def find_text_in_image(
    image: 'np.ndarray[Any, Any]', search_text: Pattern[str], *, min_confidence: int = 60,
    threshold: float = 128,
) -> Optional[ImageTextBlock]:
    binary_image = binary_grey_threshold(image, threshold)
    all_blocks = pytesseract.image_to_data(
        binary_image, output_type=pytesseract.Output.DICT, config='--psm 6 --dpi 200')
    for block_index, confidence in enumerate(all_blocks['conf']):
        if float(confidence) < min_confidence:
            continue
        if not search_text.match(all_blocks['text'][block_index]):
            continue
        return ImageTextBlock(**{
            key: all_blocks[key][block_index]
            for key in all_blocks
        })
    return None


def image_to_text(
    image: 'np.ndarray[Any, Any]', *, threshold: float = 128,
) -> str:
    binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)[1]
    text: str = pytesseract.image_to_string(binary_image, config='--psm 6 --dpi 200')
    return text
