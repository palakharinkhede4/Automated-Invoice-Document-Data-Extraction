from datetime import datetime, timedelta
import random

def get_sample_data():
    """
    Generate sample invoice data for testing purposes
    """
    sample_invoices = [
        {
            'filename': 'office_supplies_001.pdf',
            'invoice_number': 'OS-2024-001',
            'date': '2024-01-15',
            'vendor': 'Office Depot Inc.',
            'total_amount': 245.67,
            'tax_amount': 19.65,
            'category': 'Office Supplies',
            'items': [
                {'description': 'HP Printer Paper A4', 'quantity': 5, 'amount': 89.95, 'unit_price': 17.99},
                {'description': 'Stapler Heavy Duty', 'quantity': 2, 'amount': 45.98, 'unit_price': 22.99},
                {'description': 'File Folders Legal Size', 'quantity': 10, 'amount': 89.09, 'unit_price': 8.91}
            ],
            'confidence': 95.2,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extracted_text': 'OFFICE DEPOT INC.\nINVOICE: OS-2024-001\nDATE: 01/15/2024\nHP Printer Paper A4 $89.95\nStapler Heavy Duty $45.98\nFile Folders Legal Size $89.09\nSubtotal: $226.02\nTax: $19.65\nTOTAL: $245.67'
        },
        {
            'filename': 'utility_electric_002.pdf',
            'invoice_number': 'ELC-456789',
            'date': '2024-01-20',
            'vendor': 'City Electric Company',
            'total_amount': 487.23,
            'tax_amount': 38.98,
            'category': 'Utilities',
            'items': [
                {'description': 'Electricity Usage - Commercial', 'quantity': 1, 'amount': 487.23, 'unit_price': 487.23}
            ],
            'confidence': 92.7,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extracted_text': 'CITY ELECTRIC COMPANY\nAccount: 123456789\nInvoice: ELC-456789\nService Period: 12/20/2023 - 01/20/2024\nElectricity Usage - Commercial\nTotal Usage: 2,456 kWh\nRate: $0.18/kWh\nSubtotal: $448.25\nTax: $38.98\nTOTAL: $487.23'
        },
        {
            'filename': 'travel_hotel_003.pdf',
            'invoice_number': 'HTL-789123',
            'date': '2024-01-25',
            'vendor': 'Grand Plaza Hotel',
            'total_amount': 634.50,
            'tax_amount': 84.60,
            'category': 'Travel',
            'items': [
                {'description': 'Hotel Room - Executive Suite', 'quantity': 3, 'amount': 549.90, 'unit_price': 183.30},
                {'description': 'Room Service', 'quantity': 1, 'amount': 84.60, 'unit_price': 84.60}
            ],
            'confidence': 94.1,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extracted_text': 'GRAND PLAZA HOTEL\nInvoice Number: HTL-789123\nGuest: Business Traveler\nCheck-in: 01/22/2024\nCheck-out: 01/25/2024\nRoom Type: Executive Suite\n3 nights × $183.30 = $549.90\nRoom Service: $84.60\nTax: $84.60\nTOTAL AMOUNT: $634.50'
        },
        {
            'filename': 'software_license_004.pdf',
            'invoice_number': 'SW-2024-456',
            'date': '2024-02-01',
            'vendor': 'TechSoft Solutions LLC',
            'total_amount': 1299.00,
            'tax_amount': 103.92,
            'category': 'Technology',
            'items': [
                {'description': 'Annual Software License - Premium', 'quantity': 1, 'amount': 1299.00, 'unit_price': 1299.00}
            ],
            'confidence': 96.8,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extracted_text': 'TECHSOFT SOLUTIONS LLC\nSoftware License Invoice\nInvoice #: SW-2024-456\nDate: February 1, 2024\nProduct: Premium Business Suite\nLicense Type: Annual\nUsers: 25\nAmount: $1,195.08\nTax (8%): $103.92\nTOTAL: $1,299.00'
        },
        {
            'filename': 'catering_service_005.pdf',
            'invoice_number': 'CAT-567890',
            'date': '2024-02-05',
            'vendor': 'Delicious Catering Co.',
            'total_amount': 856.75,
            'tax_amount': 68.54,
            'category': 'Meals & Entertainment',
            'items': [
                {'description': 'Corporate Lunch Buffet', 'quantity': 50, 'amount': 750.00, 'unit_price': 15.00},
                {'description': 'Service Fee', 'quantity': 1, 'amount': 38.21, 'unit_price': 38.21}
            ],
            'confidence': 93.4,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extracted_text': 'DELICIOUS CATERING CO.\nCorporate Event Catering\nInvoice: CAT-567890\nEvent Date: 02/05/2024\nService: Corporate Lunch Buffet\nGuests: 50 people\nPer Person: $15.00\nSubtotal: $750.00\nService Fee: $38.21\nTax: $68.54\nTOTAL: $856.75'
        },
        {
            'filename': 'maintenance_repair_006.pdf',
            'invoice_number': 'MNT-234567',
            'date': '2024-02-10',
            'vendor': 'Reliable Maintenance Services',
            'total_amount': 325.00,
            'tax_amount': 26.00,
            'category': 'Maintenance',
            'items': [
                {'description': 'HVAC System Maintenance', 'quantity': 1, 'amount': 200.00, 'unit_price': 200.00},
                {'description': 'Air Filter Replacement', 'quantity': 4, 'amount': 99.00, 'unit_price': 24.75}
            ],
            'confidence': 91.6,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extracted_text': 'RELIABLE MAINTENANCE SERVICES\nWork Order: MNT-234567\nService Date: February 10, 2024\nHVAC System Maintenance - $200.00\nAir Filter Replacement (4 units) - $99.00\nSubtotal: $299.00\nTax: $26.00\nTOTAL: $325.00'
        }
    ]
    
    return sample_invoices

def generate_random_invoice():
    """
    Generate a single random invoice for testing
    """
    vendors = [
        'ABC Supply Company', 'Metro Office Solutions', 'Tech Innovation Inc.',
        'Global Services LLC', 'Premier Business Corp', 'Quality Equipment Co.'
    ]
    
    categories = [
        'Office Supplies', 'Technology', 'Professional Services',
        'Utilities', 'Travel', 'Equipment'
    ]
    
    vendor = random.choice(vendors)
    category = random.choice(categories)
    base_amount = random.uniform(100, 2000)
    tax_rate = 0.08
    tax_amount = base_amount * tax_rate
    total_amount = base_amount + tax_amount
    
    # Generate random date within last 30 days
    days_ago = random.randint(1, 30)
    invoice_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    invoice_number = f"INV-{random.randint(100000, 999999)}"
    
    return {
        'filename': f'random_invoice_{invoice_number}.pdf',
        'invoice_number': invoice_number,
        'date': invoice_date,
        'vendor': vendor,
        'total_amount': round(total_amount, 2),
        'tax_amount': round(tax_amount, 2),
        'category': category,
        'items': [
            {
                'description': f'{category} Services',
                'quantity': 1,
                'amount': round(base_amount, 2),
                'unit_price': round(base_amount, 2)
            }
        ],
        'confidence': random.uniform(85.0, 98.0),
        'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'extracted_text': f'{vendor}\nInvoice: {invoice_number}\nDate: {invoice_date}\n{category} Services: ${base_amount:.2f}\nTax: ${tax_amount:.2f}\nTotal: ${total_amount:.2f}'
    }
