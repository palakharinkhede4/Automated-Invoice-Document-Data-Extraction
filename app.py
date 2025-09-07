import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime
from ocr_utils import process_image, extract_text_from_pdf
from analyzer import InvoiceAnalyzer
from sample_data import get_sample_data

# Page configuration
st.set_page_config(
    page_title="Invoice Data Extraction System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_invoices' not in st.session_state:
    st.session_state.processed_invoices = []
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = InvoiceAnalyzer()

def main():
    st.title("📄 Automated Invoice & Document Data Extraction")
    st.markdown("Upload invoices and documents to automatically extract and analyze key information using OCR technology.")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Select Page", ["Upload & Extract", "Analytics Dashboard", "Data Export", "Sample Data"])
        
        st.markdown("---")
        st.header("Quick Stats")
        if st.session_state.processed_invoices:
            total_invoices = len(st.session_state.processed_invoices)
            total_amount = sum([inv.get('total_amount', 0) for inv in st.session_state.processed_invoices])
            st.metric("Total Invoices", total_invoices)
            st.metric("Total Amount", f"${total_amount:,.2f}")
        else:
            st.info("No invoices processed yet")
    
    if page == "Upload & Extract":
        upload_and_extract_page()
    elif page == "Analytics Dashboard":
        analytics_dashboard_page()
    elif page == "Data Export":
        data_export_page()
    elif page == "Sample Data":
        sample_data_page()

def upload_and_extract_page():
    st.header("Upload & Extract Invoice Data")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose invoice files",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        accept_multiple_files=True,
        help="Upload PDF or image files (PNG, JPG, JPEG)"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader(f"Processing: {uploaded_file.name}")
                    
                    # Display file info
                    file_details = {
                        "Filename": uploaded_file.name,
                        "File size": f"{uploaded_file.size / 1024:.1f} KB",
                        "File type": uploaded_file.type
                    }
                    st.json(file_details)
                
                with col2:
                    if st.button(f"Extract Data from {uploaded_file.name}", key=f"extract_{uploaded_file.name}"):
                        with st.spinner("Processing document..."):
                            try:
                                # Process the file based on type
                                if uploaded_file.type == "application/pdf":
                                    extracted_text = extract_text_from_pdf(uploaded_file)
                                else:
                                    # Process as image
                                    image = Image.open(uploaded_file)
                                    extracted_text = process_image(image)
                                
                                if extracted_text:
                                    # Analyze the extracted text
                                    invoice_data = st.session_state.analyzer.analyze_invoice_text(extracted_text)
                                    invoice_data['filename'] = uploaded_file.name
                                    invoice_data['extracted_text'] = extracted_text
                                    invoice_data['processed_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    # Add to session state
                                    st.session_state.processed_invoices.append(invoice_data)
                                    
                                    st.success("✅ Document processed successfully!")
                                    
                                    # Display extracted data
                                    st.subheader("Extracted Information")
                                    
                                    # Key fields
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.write("**Invoice Number:**", invoice_data.get('invoice_number', 'Not found'))
                                        st.write("**Date:**", invoice_data.get('date', 'Not found'))
                                        st.write("**Vendor:**", invoice_data.get('vendor', 'Not found'))
                                    
                                    with col_b:
                                        st.write("**Total Amount:**", f"${invoice_data.get('total_amount', 0):.2f}")
                                        st.write("**Tax Amount:**", f"${invoice_data.get('tax_amount', 0):.2f}")
                                        st.write("**Category:**", invoice_data.get('category', 'Uncategorized'))
                                    
                                    # Items table
                                    if invoice_data.get('items'):
                                        st.subheader("Line Items")
                                        items_df = pd.DataFrame(invoice_data['items'])
                                        st.dataframe(items_df, use_container_width=True)
                                    
                                    # Raw extracted text
                                    with st.expander("View Raw Extracted Text"):
                                        st.text_area("Extracted Text", extracted_text, height=200)
                                
                                else:
                                    st.error("❌ Failed to extract text from document")
                            
                            except Exception as e:
                                st.error(f"❌ Error processing document: {str(e)}")
                
                st.markdown("---")

def analytics_dashboard_page():
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.processed_invoices:
        st.warning("No invoice data available. Please upload and process some invoices first.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(st.session_state.processed_invoices)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_invoices = len(df)
        st.metric("Total Invoices", total_invoices)
    
    with col2:
        total_amount = df['total_amount'].sum()
        st.metric("Total Amount", f"${total_amount:,.2f}")
    
    with col3:
        avg_amount = df['total_amount'].mean()
        st.metric("Average Invoice", f"${avg_amount:,.2f}")
    
    with col4:
        total_tax = df['tax_amount'].sum()
        st.metric("Total Tax", f"${total_tax:,.2f}")
    
    st.markdown("---")
    
    
    # Detailed data table
    st.subheader("All Processed Invoices")
    
    # Select columns to display
    display_cols = ['filename', 'invoice_number', 'date', 'vendor', 'category', 'total_amount', 'tax_amount', 'processed_date']
    display_df = df[display_cols].copy()
    # Format monetary values for display
    for idx in display_df.index:
        display_df.at[idx, 'total_amount'] = f"${display_df.at[idx, 'total_amount']:.2f}"
        display_df.at[idx, 'tax_amount'] = f"${display_df.at[idx, 'tax_amount']:.2f}"
    
    st.dataframe(display_df, use_container_width=True)
    
    # Insights
    st.subheader("💡 Insights & Recommendations")
    
    # Calculate insights without visualizations
    category_summary = df.groupby('category')['total_amount'].sum().reset_index()
    
    # Top spending category
    if not category_summary.empty:
        top_category_idx = category_summary['total_amount'].idxmax()
        top_category = category_summary.loc[top_category_idx, 'category']
        top_category_amount = category_summary.loc[top_category_idx, 'total_amount']
        
        st.info(f"**Highest spending category:** {top_category} (${top_category_amount:,.2f})")
    
    # Most frequent vendor
    top_vendor = df['vendor'].mode().iloc[0] if not df['vendor'].mode().empty else "N/A"
    st.info(f"**Most frequent vendor:** {top_vendor}")
    
    # Cost-saving opportunities
    if len(category_summary) > 1:
        sorted_categories = category_summary.sort_values('total_amount', ascending=False)
        second_highest = sorted_categories.iloc[1]['category']
        st.info(f"**Cost-saving opportunity:** Consider consolidating purchases in {second_highest} category")

def data_export_page():
    st.header("📤 Data Export")
    
    if not st.session_state.processed_invoices:
        st.warning("No invoice data available to export.")
        return
    
    df = pd.DataFrame(st.session_state.processed_invoices)
    
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel Export (using CSV format as openpyxl might not be available)
        st.download_button(
            label="📊 Download as Excel (CSV)",
            data=csv,
            file_name=f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    # Preview data
    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)
    
    # Export summary
    st.subheader("Export Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Total Columns", len(df.columns))
    
    with col3:
        file_size_mb = len(csv.encode('utf-8')) / (1024 * 1024)
        st.metric("File Size", f"{file_size_mb:.2f} MB")

def sample_data_page():
    st.header("📋 Sample Data & Testing")
    
    st.info("Load sample invoice data to test the system's capabilities.")
    
    if st.button("Load Sample Data"):
        sample_invoices = get_sample_data()
        st.session_state.processed_invoices.extend(sample_invoices)
        st.success(f"✅ Loaded {len(sample_invoices)} sample invoices!")
        st.rerun()
    
    if st.button("Clear All Data"):
        st.session_state.processed_invoices = []
        st.success("✅ All data cleared!")
        st.rerun()
    
    # Show current data count
    st.metric("Current Invoice Count", len(st.session_state.processed_invoices))
    
    # OCR Testing section
    st.subheader("🔧 OCR Testing")
    st.write("Upload a test image to see OCR extraction in action:")
    
    test_file = st.file_uploader("Test OCR", type=['png', 'jpg', 'jpeg'], key="test_ocr")
    
    if test_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            image = Image.open(test_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader("Extracted Text")
            if st.button("Extract Text", key="test_extract"):
                with st.spinner("Processing..."):
                    try:
                        extracted_text = process_image(image)
                        st.text_area("OCR Result", extracted_text, height=300)
                        
                        # Show confidence/accuracy info
                        st.info(f"Text length: {len(extracted_text)} characters")
                        
                    except Exception as e:
                        st.error(f"OCR failed: {str(e)}")

if __name__ == "__main__":
    main()
