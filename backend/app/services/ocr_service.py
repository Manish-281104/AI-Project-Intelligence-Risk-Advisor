import io
import logging
from typing import Tuple, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Try to initialize RapidOCR engine
_rapid_ocr_engine = None
try:
    from rapidocr_onnxruntime import RapidOCR
    _rapid_ocr_engine = RapidOCR()
    logger.info("RapidOCR (ONNX runtime) engine initialized successfully.")
except Exception as e:
    logger.warning("Could not initialize RapidOCR: %s", e)

# Try to check pytesseract availability
_pytesseract_available = False
try:
    import pytesseract
    import shutil
    if shutil.which("tesseract"):
        _pytesseract_available = True
        logger.info("pytesseract engine with system tesseract binary is available.")
except Exception:
    pass


class OCRService:
    """
    Robust OCR extraction service for scanned and image-only PDF pages.
    Supports local ONNX-based RapidOCR and fallback to pytesseract.
    """

    def __init__(self):
        self.rapid_engine = _rapid_ocr_engine
        self.has_pytesseract = _pytesseract_available

    def is_available(self) -> bool:
        """Returns True if any OCR engine is ready to process images."""
        return self.rapid_engine is not None or self.has_pytesseract

    @staticmethod
    def is_image_blank(img: Image.Image, threshold_std: float = 3.0) -> bool:
        """
        Check whether an image is completely blank (uniform white, black, or grey).
        Computes standard deviation of pixel intensities.
        """
        try:
            gray = np.array(img.convert("L"))
            std = float(np.std(gray))
            mean = float(np.mean(gray))
            # If standard deviation is very low, image is uniform
            if std < threshold_std:
                return True
            # Near pure white with negligible variation
            if mean > 252.0 and std < 6.0:
                return True
            return False
        except Exception:
            return False

    def extract_text_from_image(self, img: Image.Image) -> Tuple[str, float]:
        """
        Run OCR on PIL Image.
        Returns (extracted_text, average_confidence).
        """
        if self.is_image_blank(img):
            return "", 0.0

        # 1. Try RapidOCR first (high speed, accurate orientation detection)
        if self.rapid_engine is not None:
            try:
                img_array = np.array(img.convert("RGB"))
                result, _ = self.rapid_engine(img_array)
                if result:
                    lines = []
                    confidences = []
                    for item in result:
                        text = item[1].strip()
                        conf = float(item[2])
                        if text:
                            lines.append(text)
                            confidences.append(conf)
                    extracted = "\n".join(lines).strip()
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                    return extracted, avg_conf
            except Exception as e:
                logger.warning("RapidOCR extraction failed: %s", e)

        # 2. Try pytesseract fallback if system tesseract is available
        if self.has_pytesseract:
            try:
                import pytesseract
                text = pytesseract.image_to_string(img)
                cleaned = text.strip()
                if cleaned:
                    return cleaned, 0.85
            except Exception as e:
                logger.warning("pytesseract fallback extraction failed: %s", e)

        return "", 0.0


ocr_service = OCRService()
