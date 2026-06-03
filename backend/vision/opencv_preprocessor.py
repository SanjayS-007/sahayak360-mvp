"""
OpenCV Preprocessor — Stage 1 of the Vision pipeline.
Handles image enhancement, deskewing, and region detection.
"""

import logging
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class PreprocessingResult:
    """Result of image preprocessing."""

    def __init__(self):
        self.processed_image: Optional[np.ndarray] = None
        self.original_size: Tuple[int, int] = (0, 0)
        self.deskew_angle: float = 0.0
        self.quality_score: float = 0.0
        self.detected_regions: list[dict] = []
        self.is_acceptable: bool = False


def preprocess_answer_sheet(image_bytes: bytes) -> PreprocessingResult:
    """
    Full preprocessing pipeline for answer sheet images.
    Steps: Decode → Resize → Grayscale → Denoise → Threshold → Deskew → Quality check
    """
    result = PreprocessingResult()

    # Step 1: Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        logger.error("Failed to decode image")
        return result

    result.original_size = (img.shape[1], img.shape[0])

    # Step 2: Resize if too large (keep aspect ratio, max 2000px on longest side)
    max_dim = max(img.shape[:2])
    if max_dim > 2000:
        scale = 2000 / max_dim
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # Step 3: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 4: Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # Step 5: Adaptive threshold
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Step 6: Deskew
    deskewed, angle = _deskew(binary)
    result.deskew_angle = angle

    # Step 7: Quality assessment
    quality = _assess_quality(denoised)
    result.quality_score = quality
    result.is_acceptable = quality >= 0.4

    # Step 8: Detect answer regions (bubble areas)
    regions = _detect_answer_regions(deskewed)
    result.detected_regions = regions

    result.processed_image = deskewed
    return result


def extract_bubble_region(image_bytes: bytes) -> Optional[bytes]:
    """Extract and return the processed image as PNG bytes for Gemini."""
    result = preprocess_answer_sheet(image_bytes)
    if result.processed_image is None:
        return None

    # Encode back to PNG
    success, encoded = cv2.imencode(".png", result.processed_image)
    if success:
        return encoded.tobytes()
    return None


def _deskew(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """Deskew image using Hough line detection."""
    # Detect edges
    edges = cv2.Canny(image, 50, 150, apertureSize=3)

    # Detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    if lines is None or len(lines) == 0:
        return image, 0.0

    # Calculate average angle
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if abs(angle) < 15:  # Only consider near-horizontal lines
            angles.append(angle)

    if not angles:
        return image, 0.0

    median_angle = np.median(angles)

    # Only deskew if angle is significant
    if abs(median_angle) < 0.5:
        return image, 0.0

    # Rotate
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=255)

    return rotated, median_angle


def _assess_quality(gray_image: np.ndarray) -> float:
    """
    Assess image quality based on contrast and sharpness.
    Returns: 0.0 (poor) to 1.0 (excellent)
    """
    # Contrast (standard deviation of pixel values)
    contrast = gray_image.std() / 128.0  # normalize to 0-1 range

    # Sharpness (Laplacian variance)
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
    sharpness = min(1.0, laplacian.var() / 500.0)

    # Combined score
    quality = 0.5 * contrast + 0.5 * sharpness
    return round(min(1.0, max(0.0, quality)), 3)


def _detect_answer_regions(binary_image: np.ndarray) -> list[dict]:
    """
    Detect potential answer bubble regions using contour analysis.
    Returns list of detected regions with bounding boxes.
    """
    # Find contours
    contours, _ = cv2.findContours(
        cv2.bitwise_not(binary_image), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        # Filter by area (bubbles are typically small circular regions)
        if 100 < area < 5000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            # Bubbles are roughly circular (aspect ratio ~1)
            if 0.7 < aspect_ratio < 1.3:
                circularity = 4 * np.pi * area / (cv2.arcLength(contour, True) ** 2)
                if circularity > 0.7:
                    regions.append({
                        "x": int(x),
                        "y": int(y),
                        "w": int(w),
                        "h": int(h),
                        "area": int(area),
                        "circularity": round(circularity, 3),
                    })

    # Sort by y then x (top-to-bottom, left-to-right)
    regions.sort(key=lambda r: (r["y"], r["x"]))
    return regions
