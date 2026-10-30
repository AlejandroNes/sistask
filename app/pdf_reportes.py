"""Generación del PDF de reportes mensuales con ReportLab."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generar_pdf(mes, anio, categorias, cuentas, presupuestos):
    archivo = BytesIO()
    documento = SimpleDocTemplate(archivo, pagesize=(21 * cm, 29.7 * cm),
                                  leftMargin=2 * cm, rightMargin=2 * cm,
                                  topMargin=2 * cm, bottomMargin=2 * cm,
                                  title='Reportes mensuales - Mis gastos')
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='TituloReporte', parent=estilos['Title'], fontSize=19,
                              leading=23, textColor=colors.HexColor('#1d5c50'), spaceAfter=8))
    estilos.add(ParagraphStyle(name='SeccionReporte', parent=estilos['Heading2'], fontSize=12,
                              leading=15, spaceBefore=15, spaceAfter=7, textColor=colors.HexColor('#1d5c50')))
    estilos.add(ParagraphStyle(name='CeldaReporte', parent=estilos['BodyText'], fontSize=9, leading=12))
    estilos.add(ParagraphStyle(name='NumeroReporte', parent=estilos['CeldaReporte'], alignment=TA_RIGHT))
    contenido = [Paragraph('Mis gastos - Reportes mensuales', estilos['TituloReporte']),
                 Paragraph(f'Período: {mes:02d}/{anio}', estilos['Normal']), Spacer(1, 10)]

    def tabla(titulo, encabezados, filas, anchos):
        contenido.append(Paragraph(titulo, estilos['SeccionReporte']))
        if not filas:
            contenido.append(Paragraph('No hay datos para este período.', estilos['BodyText']))
            return
        datos = [[Paragraph(escape(str(celda)), estilos['CeldaReporte'] if i == 0 else estilos['NumeroReporte'])
                  for i, celda in enumerate(encabezados)]]
        for fila in filas:
            datos.append([Paragraph(escape(str(celda)), estilos['CeldaReporte'] if i == 0 else estilos['NumeroReporte'])
                          for i, celda in enumerate(fila)])
        elemento = Table(datos, colWidths=anchos, repeatRows=1, hAlign='LEFT')
        elemento.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5f2ed')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7faf9')]),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#b6d3ca')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        contenido.append(elemento)

    numero = lambda monto: f'{monto:,.2f}'
    tabla('Gastos por categoría', ['Categoría', 'Total'],
          [(fila['nombre'], numero(fila['total'])) for fila in categorias], [12 * cm, 5 * cm])
    tabla('Gastos por cuenta', ['Cuenta', 'Total'],
          [(fila['nombre'], numero(fila['total'])) for fila in cuentas], [12 * cm, 5 * cm])
    tabla('Presupuesto frente a gastos', ['Categoría', 'Presupuesto', 'Gastado', 'Restante'],
          [(fila['nombre'], numero(fila['monto_limite']), numero(fila['total']), numero(fila['restante']))
           for fila in presupuestos], [6.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])

    def pie(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#718486'))
        canvas.drawString(2 * cm, 1 * cm, 'Mis gastos - Reporte mensual')
        canvas.drawRightString(19 * cm, 1 * cm, f'Página {doc.page}')

    documento.build(contenido, onFirstPage=pie, onLaterPages=pie)
    archivo.seek(0)
    return archivo
