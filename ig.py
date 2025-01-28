import argparse
import os
import random
from datetime import datetime, timedelta
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

fake = Faker('es_AR')  # Configurar Faker para Argentina

def generate_invoice(company_name, output_dir, invoice_number):
    # Generar datos aleatorios
    customer_name = fake.company()
    customer_address = fake.address().replace('\n', ', ')
    invoice_date = fake.date_between(start_date='-1y', end_date='today')
    due_date = invoice_date + timedelta(days=30)
    items = []

    # Generar items aleatorios en español
    for _ in range(random.randint(1, 5)):
        item_name = fake.catch_phrase().title()
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(10, 500), 2)
        total = round(quantity * unit_price, 2)
        items.append([item_name, quantity, f"${unit_price:.2f}", f"${total:.2f}"])

    # Calcular totales
    subtotal = sum(float(item[3][1:]) for item in items)
    tax_rates = [0.105, 0.21]  # Tasas de IVA comunes en Argentina
    tax_rate = random.choice(tax_rates)
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    # Crear PDF
    filename = os.path.join(output_dir, f"factura_{invoice_number}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # Encabezado
    elements.append(Paragraph(company_name, styles['Title']))
    elements.append(Spacer(1, 12))

    # Información de la empresa y cliente
    company_address = fake.address().replace('\n', ', ')
    company_info = [
        ["Fecha de factura:", invoice_date.strftime("%d/%m/%Y")],
        ["Fecha de vencimiento:", due_date.strftime("%d/%m/%Y")],
        ["N° de factura:", invoice_number],
        ["Cliente:", customer_name],
        ["Dirección del cliente:", customer_address]
    ]

    company_table = Table(company_info, colWidths=[120, 300])
    company_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 24))

    # Tabla de items
    headers = ["Descripción", "Cantidad", "Precio Unitario", "Total"]
    item_data = [headers] + items
    item_table = Table(item_data, colWidths=[250, 70, 100, 100])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 24))

    # Totales
    totals = [
        ["Subtotal:", f"${subtotal:.2f}"],
        [f"IVA ({tax_rate*100:.1f}%):", f"${tax:.2f}"],
        ["Total:", f"${total:.2f}"]
    ]
    total_table = Table(totals, colWidths=[400, 100])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    elements.append(total_table)

    doc.build(elements)
    return filename

def main():
    parser = argparse.ArgumentParser(description='Generador de facturas PDF')
    parser.add_argument('empresa', type=str, help='Nombre de la empresa que emite las facturas')
    parser.add_argument('cantidad', type=int, help='Cantidad de facturas a generar')
    parser.add_argument('directorio', type=str, help='Directorio de salida para los archivos PDF')

    args = parser.parse_args()

    # Crear directorio si no existe
    os.makedirs(args.directorio, exist_ok=True)

    # Generar número inicial aleatorio de 16 dígitos
    max_start = 10**16 - args.cantidad
    if max_start < 0:
        raise ValueError("La cantidad solicitada excede el máximo posible de números secuenciales")

    start = random.randint(0, max_start)

    # Generar facturas con números secuenciales
    for i in range(args.cantidad):
        current_number = start + i
        formatted_number = f"{current_number:016d}"  # Rellenar con ceros a la izquierda
        filename = generate_invoice(args.empresa, args.directorio, formatted_number)
        print(f"Factura generada: {filename}")

if __name__ == "__main__":
    main()