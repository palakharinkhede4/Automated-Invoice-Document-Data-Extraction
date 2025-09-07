import re
import pandas as pd
from datetime import datetime
import streamlit as st

class InvoiceAnalyzer:
    def __init__(self):
        # Category keywords for automatic classification
        self.category_keywords = {
            'Office Supplies': ['paper', 'pen', 'pencil', 'stapler', 'folder', 'binder', 'office', 'supplies', 'stationery'],
            'Utilities': ['electricity', 'gas', 'water', 'internet', 'phone', 'utility', 'power', 'energy', 'telecom'],
            'Travel': ['hotel', 'flight', 'taxi', 'uber', 'lyft', 'airline', 'travel', 'accommodation', 'transport'],
            'Meals & Entertainment': ['restaurant', 'cafe', 'food', 'meal', 'lunch', 'dinner', 'catering', 'entertainment'],
            'Technology': ['computer', 'laptop', 'software', 'hardware', 'tech', 'IT', 'system', 'device'],
            'Professional Services': ['consulting', 'legal', 'accounting', 'professional', 'service', 'advisory'],
            'Marketing': ['advertising', 'marketing', 'promotion', 'social media', 'campaign', 'branding'],
            'Maintenance': ['repair', 'maintenance', 'cleaning', 'janitorial', 'fix', 'service'],
            'Insurance': ['insurance', 'premium', 'coverage', 'policy', 'liability'],
            'Equipment': ['equipment', 'machinery', 'tools', 'furniture', 'fixture']
        }
        
        # Common invoice patterns
        self.patterns = {
            'invoice_number': [
                r'invoice\s*(?:number|no|#)?\s*:?\s*([A-Z0-9\-]+)',
                r'inv\s*(?:number|no|#)?\s*:?\s*([A-Z0-9\-]+)',
                r'#\s*([A-Z0-9\-]+)',
                r'invoice\s+([A-Z0-9\-]+)'
            ],
            'total_amount': [
                r'total\s*:?\s*\$?([0-9,]+\.?\d{0,2})',
                r'amount\s*due\s*:?\s*\$?([0-9,]+\.?\d{0,2})',
                r'grand\s*total\s*:?\s*\$?([0-9,]+\.?\d{0,2})',
                r'balance\s*due\s*:?\s*\$?([0-9,]+\.?\d{0,2})'
            ],
            'date': [
                r'date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'invoice\s*date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})'
            ],
            'tax': [
                r'tax\s*:?\s*\$?([0-9,]+\.?\d{0,2})',
                r'vat\s*:?\s*\$?([0-9,]+\.?\d{0,2})',
                r'sales\s*tax\s*:?\s*\$?([0-9,]+\.?\d{0,2})'
            ],
            'vendor': [
                r'^([A-Z][a-zA-Z\s&,.]+(?:Inc|LLC|Corp|Ltd|Company))',
                r'from\s*:?\s*([A-Z][a-zA-Z\s&,.]+)',
                r'bill\s*to\s*:?\s*([A-Z][a-zA-Z\s&,.]+)'
            ]
        }

    def analyze_invoice_text(self, text):
        """
        Analyze extracted text and return structured invoice data
        """
        if not text:
            return self._empty_invoice_data()
        
        invoice_data = {
            'invoice_number': self._extract_invoice_number(text),
            'date': self._extract_date(text),
            'vendor': self._extract_vendor(text),
            'total_amount': self._extract_total_amount(text),
            'tax_amount': self._extract_tax_amount(text),
            'items': self._extract_line_items(text),
            'category': self._categorize_invoice(text),
            'confidence': self._calculate_extraction_confidence(text)
        }
        
        return invoice_data

    def _extract_invoice_number(self, text):
        """Extract invoice number from text"""
        text_lower = text.lower()
        
        for pattern in self.patterns['invoice_number']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return "Not found"

    def _extract_date(self, text):
        """Extract date from text"""
        for pattern in self.patterns['date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse and format the date
                    parsed_date = self._parse_date(date_str)
                    return parsed_date.strftime("%Y-%m-%d") if parsed_date else date_str
                except:
                    return date_str
        
        return "Not found"

    def _parse_date(self, date_str):
        """Parse date string into datetime object"""
        date_formats = [
            "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y",
            "%m/%d/%y", "%m-%d-%y", "%d/%m/%y", "%d-%m-%y",
            "%Y/%m/%d", "%Y-%m-%d"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def _extract_vendor(self, text):
        """Extract vendor/company name from text"""
        lines = text.split('\n')
        
        # Look for vendor in first few lines
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d', line):
                # Check if it looks like a company name
                if any(word in line.lower() for word in ['inc', 'llc', 'corp', 'ltd', 'company', 'co']):
                    return line
                # If it's the first non-empty line with reasonable length
                elif i == 0 and len(line.split()) >= 2:
                    return line
        
        # Fallback: look for patterns
        for pattern in self.patterns['vendor']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return "Not found"

    def _extract_total_amount(self, text):
        """Extract total amount from text"""
        text_lower = text.lower()
        
        for pattern in self.patterns['total_amount']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        # Fallback: look for any dollar amount
        dollar_pattern = r'\$([0-9,]+\.?\d{0,2})'
        matches = re.findall(dollar_pattern, text)
        if matches:
            amounts = []
            for match in matches:
                try:
                    amounts.append(float(match.replace(',', '')))
                except ValueError:
                    continue
            
            if amounts:
                # Return the largest amount found (likely to be total)
                return max(amounts)
        
        return 0.0

    def _extract_tax_amount(self, text):
        """Extract tax amount from text"""
        text_lower = text.lower()
        
        for pattern in self.patterns['tax']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        
        return 0.0

    def _extract_line_items(self, text):
        """Extract line items from invoice text"""
        items = []
        lines = text.split('\n')
        
        # Look for lines that contain item descriptions and amounts
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip header-like lines
            if any(header in line.lower() for header in ['invoice', 'bill to', 'ship to', 'date', 'total']):
                continue
            
            # Look for lines with dollar amounts
            dollar_match = re.search(r'\$?([0-9,]+\.?\d{0,2})', line)
            if dollar_match:
                try:
                    amount = float(dollar_match.group(1).replace(',', ''))
                    
                    # Extract description (text before the amount)
                    description = re.sub(r'\$?[0-9,]+\.?\d{0,2}', '', line).strip()
                    description = re.sub(r'\s+', ' ', description)  # Clean whitespace
                    
                    if description and len(description) > 2:
                        # Try to extract quantity
                        qty_match = re.search(r'(\d+)\s*x\s*', description.lower())
                        quantity = int(qty_match.group(1)) if qty_match else 1
                        
                        items.append({
                            'description': description,
                            'amount': amount,
                            'quantity': quantity,
                            'unit_price': amount / quantity if quantity > 0 else amount
                        })
                except ValueError:
                    continue
        
        return items

    def _categorize_invoice(self, text):
        """Automatically categorize invoice based on content"""
        text_lower = text.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return "Uncategorized"

    def _calculate_extraction_confidence(self, text):
        """Calculate confidence score for data extraction"""
        if not text:
            return 0.0
        
        confidence_factors = []
        
        # Factor 1: Text length (longer text usually means better extraction)
        text_length_score = min(len(text) / 1000, 1.0) * 100
        confidence_factors.append(text_length_score)
        
        # Factor 2: Presence of key invoice elements
        key_elements = ['invoice', 'total', 'date', 'amount']
        element_score = sum(1 for element in key_elements if element in text.lower()) / len(key_elements) * 100
        confidence_factors.append(element_score)
        
        # Factor 3: Number format detection (invoices should have numbers)
        number_matches = len(re.findall(r'\d+', text))
        number_score = min(number_matches / 10, 1.0) * 100
        confidence_factors.append(number_score)
        
        # Calculate weighted average
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        return round(overall_confidence, 1)

    def _empty_invoice_data(self):
        """Return empty invoice data structure"""
        return {
            'invoice_number': 'Not found',
            'date': 'Not found',
            'vendor': 'Not found',
            'total_amount': 0.0,
            'tax_amount': 0.0,
            'items': [],
            'category': 'Uncategorized',
            'confidence': 0.0
        }

    def get_spending_insights(self, invoices_data):
        """Generate spending insights from invoice data"""
        if not invoices_data:
            return {}
        
        df = pd.DataFrame(invoices_data)
        
        insights = {
            'total_spending': df['total_amount'].sum(),
            'average_invoice': df['total_amount'].mean(),
            'top_category': df.groupby('category')['total_amount'].sum().idxmax(),
            'top_vendor': df.groupby('vendor')['total_amount'].sum().idxmax(),
            'highest_invoice': df['total_amount'].max(),
            'monthly_average': df['total_amount'].sum() / max(1, len(df.groupby('date').size())),
            'category_distribution': df.groupby('category')['total_amount'].sum().to_dict(),
            'vendor_distribution': df.groupby('vendor')['total_amount'].sum().to_dict()
        }
        
        return insights

    def suggest_cost_savings(self, invoices_data):
        """Suggest potential cost-saving opportunities"""
        if not invoices_data:
            return []
        
        df = pd.DataFrame(invoices_data)
        suggestions = []
        
        # High-spending categories
        category_spending = df.groupby('category')['total_amount'].sum()
        if len(category_spending) > 0:
            # Convert to series and sort
            spending_series = pd.Series(category_spending.values, index=category_spending.index)
            category_spending_sorted = spending_series.sort_values(ascending=False)
            top_category = category_spending_sorted.index[0]
            top_amount = category_spending_sorted.iloc[0]
            suggestions.append(f"Consider reviewing {top_category} expenses (${top_amount:,.2f} total)")
        
        # Duplicate vendors
        vendor_counts = df['vendor'].value_counts()
        frequent_vendors = vendor_counts[vendor_counts > 1]
        if len(frequent_vendors) > 0:
            # Get first vendor from the filtered Series
            vendor_name = frequent_vendors.index.tolist()[0]
            suggestions.append(f"Consolidate purchases with {vendor_name} for potential bulk discounts")
        
        # High individual invoices
        high_invoices = df[df['total_amount'] > df['total_amount'].quantile(0.9)]
        if len(high_invoices) > 0:
            suggestions.append(f"Review high-value invoices (${high_invoices['total_amount'].min():.2f}+ range)")
        
        return suggestions
