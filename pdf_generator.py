from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

def draw_wrapped_text(pdf, text, x, y, max_width, font_name="Times-Roman", font_size=12, leading=14):
    """
    Dibuja un texto envuelto en el lienzo pdf.
    Retorna la nueva posición en y luego de haber dibujado todas las líneas.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if pdf.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y

# Configuración de colores
COLOR_PRIMARIO   = HexColor("#2C3E50")  # Azul oscuro profesional
COLOR_SECUNDARIO = HexColor("#16A085")  # Verde agua elegante
COLOR_TEXTO      = HexColor("#2C3E50")  # Gris oscuro para texto
COLOR_BORDE      = HexColor("#BDC3C7")  # Gris claro para bordes

def split_date(date_str):
    """
    Dada una cadena en formato "YYYY-MM-DD", retorna un diccionario con claves "dia", "mes" y "año".
    Si falla, retorna valores vacíos.
    """
    try:
        parts = date_str.split("-")
        return {"dia": parts[2], "mes": parts[1], "año": parts[0]}
    except Exception:
        return {"dia": "", "mes": "", "año": ""}

def convert_month(month_str):
    """
    Convierte el número de mes en cadena a su nombre en español.
    """
    meses = {
        "01": "enero",
        "02": "febrero",
        "03": "marzo",
        "04": "abril",
        "05": "mayo",
        "06": "junio",
        "07": "julio",
        "08": "agosto",
        "09": "septiembre",
        "10": "octubre",
        "11": "noviembre",
        "12": "diciembre"
    }
    return meses.get(month_str, month_str)

# hacemos una constante con el nombre del administrdor 
ADMINISTRADOR = "Pbro. Jesus Fernandez"

def generate_pdf(document_type, details, file_path):
    """
    Genera un PDF basado en el tipo de documento y los detalles proporcionados.
    """
    if document_type.lower() in ["bautizo", "bautismo"]:
        # Preprocesamos las fechas a partir de las cadenas
        fecha_bautismo = split_date(details.get("bautizado", {}).get("fecha_bautismo", ""))
        fecha_nacimiento = split_date(details.get("bautizado", {}).get("fecha_nacimiento", ""))
        fecha_certificado = split_date(details.get("acta_civil", {}).get("fecha", ""))
        
        # Extraemos los datos principales
        nombre_bautizado = details.get("bautizado", {}).get("nombre", "")
        lugar_nacimiento = details.get("bautizado", {}).get("lugar_nacimiento", "")
        
        # Se esperan en claves separadas
        padre = details.get("informacion_familiar", {}).get("padre", "")
        madre = details.get("informacion_familiar", {}).get("madre", "")
        padrino = details.get("informacion_familiar", {}).get("padrino", "")
        madrina = details.get("informacion_familiar", {}).get("madrina", "")
        
        # Otros campos: se usa "Registro Civil" para el acta civil y el administrador es constante
        registro_civil = details.get("acta_civil", {}).get("acta", "")
        libro = details.get("acta_eclesiastica", {}).get("libro", "")
        folio = details.get("acta_eclesiastica", {}).get("folio", "")
        
        # Configuramos el PDF
        pdf = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Márgenes y offset
        border_margin  = 1.5 * cm
        content_margin = 2.5 * cm
        text_offset    = 1.0 * cm

        # Diseño de fondo
        pdf.setStrokeColor(COLOR_BORDE)
        pdf.setLineWidth(1.5)
        pdf.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin, stroke=1, fill=0)

        # Encabezado
        pdf.setFillColor(COLOR_PRIMARIO)
        pdf.setFont("Times-Roman", 12)
        pdf.drawCentredString(width/2, height - (2*cm + text_offset), "Iglesia Parroquial San Martín de Porres")
        pdf.drawCentredString(width/2, height - (2.5*cm + text_offset), "Calle Real de Montesano, Callejon Victoria,")
        pdf.drawCentredString(width/2, height - (3*cm + text_offset), "Carlos Soublette 1162")
        pdf.drawCentredString(width/2, height - (3.5*cm + text_offset), "Edo. La Guaira - Venezuela")

        # Logo representativo
        logo_size = 3.0 * cm
        logo_x = border_margin + 0.2*cm + 0.3*cm
        logo_y = height - 2*cm - logo_size
        pdf.drawImage("icono/sello.png", logo_x, logo_y, width=logo_size, height=logo_size, mask='auto')

        # Título estilizado
        pdf.setFillColor(COLOR_SECUNDARIO)
        pdf.setFont("Times-Roman", 16)
        pdf.drawCentredString(width/2, height - (5*cm + text_offset), "CERTIFICADO DE BAUTISMO")
        pdf.line(4*cm, height - (5.3*cm + text_offset), width - 4*cm, height - (5.3*cm + text_offset))

        # Cuerpo del documento
        pdf.setFillColor(COLOR_TEXTO)
        y_position = height - (6.5*cm + text_offset)

        # Texto con fecha de bautismo (se reduce la fuente a 10 para que se vea más pequeño)
        pdf.setFont("Times-Roman", 10)
        texto_fecha = (
            f"El Suscrito Párroco de San Martín de Porres, certifica que, el día "
            f"{fecha_bautismo.get('dia', '')} de {convert_month(fecha_bautismo.get('mes', ''))} de {fecha_bautismo.get('año', '')},"
        )
        y_position = draw_wrapped_text(pdf, texto_fecha, content_margin, y_position, width - 2*content_margin, "Times-Roman", 10, 12)

        # Texto destacado
        pdf.setFont("Times-Roman", 12)
        pdf.setFillColor(COLOR_SECUNDARIO)
        pdf.drawString(content_margin, y_position, "fue solemnemente BAUTIZADO (A):")
        pdf.setFillColor(COLOR_TEXTO)
        y_position -= 1.5 * cm

        # Nombre centrado con línea decorativa
        pdf.setFont("Times-Roman", 14)
        text_width = pdf.stringWidth(nombre_bautizado, "Times-Roman", 14)
        pdf.drawCentredString(width/2, y_position, nombre_bautizado)
        pdf.line((width/2) - (text_width/2) - 0.5*cm, y_position - 0.3*cm,
                 (width/2) + (text_width/2) + 0.5*cm, y_position - 0.3*cm)
        y_position -= 2 * cm

        # Sección central en dos columnas
        column_line_spacing = 1.2 * cm
        available_width = width - 2 * content_margin
        col1_x = content_margin
        col2_x = content_margin + available_width/2 + 0.5*cm
        col_y = y_position

        # Columna izquierda: Lugar y fecha de nacimiento, padres
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(col1_x, col_y, f"Lugar de nacimiento: {lugar_nacimiento}")
        pdf.drawString(col1_x, col_y - column_line_spacing, 
                       f"Fecha de nacimiento: {fecha_nacimiento.get('dia', '')} de {convert_month(fecha_nacimiento.get('mes', ''))} de {fecha_nacimiento.get('año', '')}")
        pdf.drawString(col1_x, col_y - 2*column_line_spacing, f"Padre: {padre}")
        pdf.drawString(col1_x, col_y - 3*column_line_spacing, f"Madre: {madre}")

        # Columna derecha: Padrino, Madrina y Administrador
        pdf.drawString(col2_x, col_y, f"Padrino: {padrino}")
        pdf.drawString(col2_x, col_y - column_line_spacing, f"Madrina: {madrina}")
        pdf.drawString(col2_x, col_y - 2*column_line_spacing, f"Administrador: {ADMINISTRADOR}")
        y_position = col_y - 3.5 * column_line_spacing

        # Se imprime "Finalidad: Registro Civil"
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(content_margin, y_position, "Finalidad: Registro Civil")
        y_position -= 1.5 * cm

        # Registro Civil y Fecha del certificado (con conversión de mes)
        registro_text = f"Registro Civil Nº: {registro_civil}"
        fecha_text = f"Fecha: {fecha_certificado.get('dia', '')}/{convert_month(fecha_certificado.get('mes', ''))}/{fecha_certificado.get('año', '')}"
        pdf.drawString(content_margin, y_position, registro_text)
        pdf.drawRightString(width - content_margin, y_position, fecha_text)
        y_position -= 2 * cm

        # Libro y Folio
        libro_text = f"Libro: {libro}"
        folio_text = f"Folio: {folio}"
        pdf.drawString(content_margin, y_position, libro_text)
        pdf.drawRightString(width - content_margin, y_position, folio_text)
        y_position -= 1.5 * cm

        # Firma: línea de firma y firma digital
        pdf.setFont("Times-Roman", 12)
        pdf.drawRightString(width - content_margin, y_position, "_________________________")
        signature_max_width = 4.0 * cm
        signature_width = signature_max_width
        signature_height = signature_width * (320/360)
        signature_x = width - content_margin - signature_width
        signature_y = y_position - 1.0 * cm
        pdf.drawImage("icono/firma.png", signature_x, signature_y, width=signature_width, height=signature_height, mask='auto')
        pdf.drawRightString(width - content_margin, y_position - 0.7 * cm, ADMINISTRADOR)
        pdf.drawString(content_margin, y_position - 0.7 * cm, 
                       f"El Nula, {fecha_certificado.get('dia', '')} de {convert_month(fecha_certificado.get('mes', ''))} de {fecha_certificado.get('año', '')}")
        y_position -= 2 * cm

        # Footer
        footer = [
            "Iglesia Parroquial San Martín de Porres",
            "Calle Real de Montesano, Callejon Victoria, Carlos Soublette 1162",
            "Edo. La Guaira - Venezuela",
            "✉ parroquiademontesano@gmail.com  ☎ 0212 355-47-46"
        ]
        pdf.setFillColor(COLOR_PRIMARIO)
        footer_font_size = 9
        pdf.setFont("Times-Roman", footer_font_size)
        footer_spacing = 0.4 * cm
        footer_bottom_margin = border_margin + 1.0 * cm
        y_footer = footer_bottom_margin + (len(footer) - 1) * footer_spacing
        for line in footer:
            pdf.drawCentredString(width/2, y_footer, line)
            y_footer -= footer_spacing

        pdf.save()
    else:
        # Plantilla simple para otros tipos de documento
        pdf = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, "Documento")
        pdf.setFont("Helvetica", 12)
        
        y = 720
        pdf.drawString(100, y, "Cédula: " + details.get("cedula", ""))
        y -= 20
        for section, content in details.items():
            pdf.drawString(100, y, f"--- {section.capitalize()} ---")
            y -= 20
            if isinstance(content, dict):
                for key, value in content.items():
                    pdf.drawString(100, y, f"{key.capitalize()}: {value}")
                    y -= 20
            elif isinstance(content, list):
                pdf.drawString(100, y, f"{section.capitalize()}: " + ", ".join(content))
                y -= 20
            else:
                pdf.drawString(100, y, f"{section.capitalize()}: {content}")
                y -= 20
        pdf.drawString(100, y - 20, "Que la bendición de Dios te acompañe siempre.")
        pdf.save()
