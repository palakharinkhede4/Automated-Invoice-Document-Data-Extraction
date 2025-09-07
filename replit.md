# Overview

This is an automated invoice and document data extraction system built with Streamlit. The application uses OCR (Optical Character Recognition) technology to extract key information from uploaded invoices and documents, automatically categorizes expenses, and provides analytics dashboards for financial data analysis. The system is designed to streamline invoice processing workflows for businesses by reducing manual data entry and providing insights into spending patterns.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application with a multi-page interface
- **Layout**: Wide layout with expandable sidebar for navigation and quick stats
- **Pages**: Four main sections - Upload & Extract, Analytics Dashboard, Data Export, and Sample Data
- **State Management**: Streamlit session state for persistent data storage across page interactions
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts and analytics

## Backend Architecture
- **Core Processing**: Modular design with separate components for OCR, analysis, and data generation
- **OCR Engine**: PyTesseract integration with OpenCV for image preprocessing
- **Document Processing**: Support for both image files (PNG, JPG) and PDF documents via PyPDF2
- **Data Analysis**: Rule-based invoice analysis using regex patterns and keyword matching
- **Image Enhancement**: Advanced preprocessing pipeline including noise reduction, thresholding, morphological operations, and skew correction

## Data Processing Pipeline
- **Text Extraction**: Multi-format document processing with OCR fallback for images
- **Pattern Recognition**: Regex-based extraction for invoice numbers, amounts, dates, tax, and vendor information
- **Automatic Categorization**: Keyword-based classification system for expense categories (Office Supplies, Utilities, Travel, etc.)
- **Data Structure**: Dictionary-based invoice records with comprehensive metadata including confidence scores and processing timestamps

## Category Classification System
- **Predefined Categories**: 10 major expense categories with associated keyword dictionaries
- **Smart Matching**: Text-based classification using vendor names and item descriptions
- **Fallback Logic**: Default categorization when automated classification fails

# External Dependencies

## Core Libraries
- **Streamlit**: Web application framework for the user interface
- **OpenCV (cv2)**: Image processing and computer vision operations
- **PyTesseract**: OCR engine for text extraction from images
- **PIL (Pillow)**: Image manipulation and format conversion
- **PyPDF2**: PDF document parsing and text extraction

## Data Processing
- **Pandas**: Data manipulation and analysis for invoice records
- **NumPy**: Numerical operations and array processing for image data
- **Plotly**: Interactive visualization library for charts and dashboards

## Text Processing
- **Regular Expressions (re)**: Pattern matching for data extraction
- **DateTime**: Date parsing and timestamp management

## Development Dependencies
- **Base64**: File encoding for data transfer
- **IO**: In-memory file operations for document processing

The system is designed to be self-contained with no external API dependencies, making it suitable for local deployment and data privacy requirements.