Fake Invoice Generator

A Python script that generates random invoices in PDF format with realistic Argentine business data, with optional S3 storage support.

Features

- Generates multiple PDF invoices with sequential numbering
- Uses realistic Argentine company names and addresses
- Includes random products/services with prices
- Applies Argentine VAT rates (10.5% or 21%)
- Creates professional PDF layout with tables and formatting
- Optional S3 storage integration

Requirements

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Usage

Basic usage for local storage:

python3 ig.py "Company Name" number_of_invoices output_directory

With S3 upload:

python3 ig.py "Company Name" number_of_invoices output_directory --s3-prefix "invoices/"

S3 Configuration

Create an s3.ini file with your S3 credentials:

[s3]
bucket = your-bucket-name
endpoint = https://your-endpoint
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = your-region

Arguments

- Company Name: The name of the company issuing the invoices
- number_of_invoices: Number of invoices to generate
- output_directory: Directory where PDF files will be saved
- --s3-prefix: (Optional) Prefix for S3 object keys
- --disable-s3: (Optional) Disable S3 upload even if configured

Output

The script generates PDF files named factura_XXXXXXXXXXXXXXXX.pdf where X is a 16-digit sequential number.

Each invoice includes

- Company and customer information
- Invoice number and dates
- Random line items with quantities and prices
- Subtotal, VAT calculation, and total amount

Technical Details

- Uses Faker library to generate realistic Argentine business data
- PDF generation handled by reportlab
- Supports both common Argentine VAT rates (10.5% and 21%)
- Generates between 1-5 random items per invoice
- Prices range from $10 to $500 per unit
- Optional S3 integration using boto3
- Supports both file-based and in-memory PDF generation
