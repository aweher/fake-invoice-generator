# Fake Invoice Generator

A Python script that generates random invoices in PDF format with realistic Argentine business data.

## Features

- Generates multiple PDF invoices with sequential numbering
- Uses realistic Argentine company names and addresses
- Includes random products/services with prices
- Applies Argentine VAT rates (10.5% or 21%)
- Creates professional PDF layout with tables and formatting

## Requirements

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the script with the following arguments:

```bash
python3 ig.py "Company Name" number_of_invoices output_directory
```

## Example

```bash
python ig.py "Mi Empresa SA" 5 ./facturas
```

## Arguments

**Company Name:** The name of the company issuing the invoices
**number_of_invoices:** Number of invoices to generate
**output_directory:** Directory where PDF files will be saved

## Output

The script generates PDF files named factura_XXXXXXXXXXXXXXXX.pdf where X is a 16-digit sequential number.

### Each invoice includes

- Company and customer information
- Invoice number and dates
- Random line items with quantities and prices
- Subtotal, VAT calculation, and total amount
- Technical Details
- Uses Faker library to generate realistic Argentine business data
- PDF generation handled by reportlab
- Supports both common Argentine VAT rates (10.5% and 21%)
- Generates between 1-5 random items per invoice
- Prices range from $10 to $500 per unit
