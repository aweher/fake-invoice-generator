import argparse
import os
import random
import logging
import configparser
from datetime import datetime, timedelta
from io import BytesIO
from faker import Faker
from typing import List, Tuple, Dict, Union
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker('es_AR')  # Configurar Faker para Argentina

def read_s3_config(config_file: str = 's3.ini') -> Dict[str, str]:
    """
    Read S3 configuration from INI file
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 's3' not in config:
        logger.warning("No S3 configuration found in config file")
        return {}
        
    return {
        'bucket': config['s3'].get('bucket'),
        'endpoint': config['s3'].get('endpoint'),
        'aws_access_key_id': config['s3'].get('aws_access_key_id'),
        'aws_secret_access_key': config['s3'].get('aws_secret_access_key'),
        'region': config['s3'].get('region')
    }

def upload_to_s3(file_obj: Union[str, BytesIO], bucket: str = None, s3_key: str = None, **kwargs) -> bool:
    """
    Upload a file or bytes to S3 bucket
    """
    if bucket is None:
        bucket = kwargs.pop('bucket')
        
    if s3_key is None:
        s3_key = os.path.basename(file_obj) if isinstance(file_obj, str) else s3_key
    
    client_config = {
        'endpoint_url': kwargs.get('endpoint'),
        'aws_access_key_id': kwargs.get('aws_access_key_id'),
        'aws_secret_access_key': kwargs.get('aws_secret_access_key')
    }
    
    if kwargs.get('region'):
        client_config['region_name'] = kwargs['region']
    
    s3_client = boto3.client('s3', **client_config)
    
    try:
        if isinstance(file_obj, BytesIO):
            s3_client.put_object(Bucket=bucket, Key=s3_key, Body=file_obj.getvalue())
        else:
            s3_client.upload_file(file_obj, bucket, s3_key)
        logger.info(f"Successfully uploaded to s3://{bucket}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {str(e)}")
        return False

def generate_invoice(company_name: str, output_dir: str, invoice_number: str, in_memory: bool = False) -> Union[str, BytesIO]:
    if not company_name or not invoice_number:
        raise ValueError("Required parameters cannot be empty")
    if not in_memory and (not output_dir or not os.path.isdir(output_dir)):
        raise ValueError("Output directory must be valid when not in memory mode")

    # Create buffer for in-memory PDF
    buffer = BytesIO() if in_memory else None
    filename = os.path.join(output_dir, f"factura_{invoice_number}.pdf") if not in_memory else None
    
    # Use buffer or filename depending on mode
    doc = SimpleDocTemplate(buffer if in_memory else filename, pagesize=letter)

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
    
    if in_memory:
        buffer.seek(0)
        return buffer
    return filename

def main():
    parser = argparse.ArgumentParser(description='Generador de facturas PDF')
    parser.add_argument('empresa', type=str, help='Nombre de la empresa que emite las facturas')
    parser.add_argument('cantidad', type=int, help='Cantidad de facturas a generar')
    parser.add_argument('directorio', type=str, help='Directorio de salida para los archivos PDF')
    parser.add_argument('--s3-prefix', type=str, default='', 
                       help='Prefijo para los archivos en S3 (default: "")')
    parser.add_argument('--disable-s3', action='store_true',
                       help='Deshabilita la subida a S3 incluso si existe configuración')

    args = parser.parse_args()

    # Check for s3.ini and load config if exists
    s3_config = {}
    if os.path.exists('s3.ini') and not args.disable_s3:
        s3_config = read_s3_config('s3.ini')
        logger.info("S3 configuration loaded - uploads enabled")

    # Crear directorio si no existe y S3 está deshabilitado
    if not s3_config.get('bucket') or args.disable_s3:
        os.makedirs(args.directorio, exist_ok=True)

    # Generar número inicial aleatorio de 16 dígitos
    max_start = 10**16 - args.cantidad
    if max_start < 0:
        raise ValueError("La cantidad solicitada excede el máximo posible de números secuenciales")

    start = random.randint(0, max_start)

    # Generar facturas con números secuenciales
    for i in range(args.cantidad):
        current_number = start + i
        formatted_number = f"{current_number:016d}"
        
        # Generate in memory if S3 enabled, otherwise save to disk
        result = generate_invoice(
            args.empresa, 
            args.directorio, 
            formatted_number,
            in_memory=(s3_config.get('bucket') and not args.disable_s3)
        )
        
        if s3_config.get('bucket') and not args.disable_s3:
            s3_key = f"{args.s3_prefix}factura_{formatted_number}.pdf"
            upload_to_s3(result, **s3_config, s3_key=s3_key)
        else:
            logger.info(f"Factura generada: {result}")

if __name__ == "__main__":
    main()
