import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import PyPDF2
import streamlit as st
import re

def preprocess_image(image):
    """
    Preprocess image for better OCR accuracy using OpenCV
    """
    # Convert PIL image to OpenCV format
    opencv_image = np.array(image)
    
    # Convert to grayscale if needed
    if len(opencv_image.shape) == 3:
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)
    else:
        gray = opencv_image
    
    # Apply image preprocessing techniques
    # 1. Noise reduction
    denoised = cv2.medianBlur(gray, 5)
    
    # 2. Thresholding for better contrast
    # Use adaptive thresholding for better results with varying lighting
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # 3. Morphological operations to clean up the image
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # 4. Find and correct skew (basic implementation)
    coords = np.column_stack(np.where(cleaned > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only correct if skew is significant
        if abs(angle) > 0.5:
            (h, w) = cleaned.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            cleaned = cv2.warpAffine(cleaned, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # 5. Resize image if too small (OCR works better with larger images)
    height, width = cleaned.shape
    if height < 300 or width < 300:
        scale_factor = max(300 / height, 300 / width)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        cleaned = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    return cleaned

def process_image(image):
    """
    Process image and extract text using OCR
    """
    try:
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Configure Tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$%#@-/:() '
        
        # Extract text using Tesseract
        extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Clean up the extracted text
        cleaned_text = clean_extracted_text(extracted_text)
        
        return cleaned_text
        
    except Exception as e:
        st.error(f"Error in OCR processing: {str(e)}")
        return ""

def clean_extracted_text(text):
    """
    Clean and normalize extracted text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s.,/$#@()-:]', '', text)
    
    # Split into lines and remove empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    return '\n'.join(lines)

def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF file
    """
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        # Read PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        extracted_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        # Clean up the extracted text
        cleaned_text = clean_extracted_text(extracted_text)
        
        return cleaned_text
        
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def get_text_confidence(image):
    """
    Get OCR confidence score
    """
    try:
        processed_image = preprocess_image(image)
        
        # Get confidence data
        data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            return avg_confidence
        else:
            return 0
            
    except Exception as e:
        return 0

def detect_document_regions(image):
    """
    Detect different regions in the document (header, body, footer)
    """
    try:
        # Convert PIL image to OpenCV format
        opencv_image = np.array(image)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)
        
        # Find contours
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        regions = []
        height, width = gray.shape
        
        for contour in contours[:5]:  # Top 5 largest contours
            x, y, w, h = cv2.boundingRect(contour)
            
            # Classify region based on position
            if y < height * 0.2:
                region_type = "header"
            elif y > height * 0.8:
                region_type = "footer"
            else:
                region_type = "body"
            
            regions.append({
                'type': region_type,
                'bbox': (x, y, w, h),
                'area': w * h
            })
        
        return regions
        
    except Exception as e:
        return []
