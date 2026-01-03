from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QHBoxLayout, QCompleter, QDialog, QTableView, QTableWidget, QTableWidgetItem

from PySide6.QtGui import QIcon

from sqlite3 import Error

import sqlite3

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize

from datetime import datetime

import os

now = datetime.now()

year = now.strftime("%Y")

month = now.strftime("%m")

day = now.strftime("%d")

time = now.strftime("%H:%M:%S")

date = now.strftime("%d/%m/%Y")

PAGE_WIDTH  = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]

directory = "receipts"

# Check if the directory exists
if not os.path.exists(directory):
    # If it doesn't exist, create it
    #dir = directory.translate({ord("/") : 92})
    os.makedirs(directory)

from conexion import *


class MostrarPedido(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Resumen pedido")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))


        self.setMinimumWidth(504)
        self.setMinimumHeight(520)

        layout = QVBoxLayout(self)


        # Create a QLabel for the title

        title_label = QLabel("Resumen del pedido", self)

        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        title_label.setAlignment(Qt.AlignCenter)


        # Add the title label to the layout

        layout.addWidget(title_label)
        



        self.table = QTableWidget()

        self.table.setColumnCount(3)  # Number of columns

        self.table.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad"])  # Column headers
        
        self.table.setColumnWidth(0, 100) 
        self.table.setColumnWidth(1, 280) 
        self.table.setColumnWidth(2, 80)

        layout.addWidget(self.table)


        



        #self.table.resizeColumnsToContents()

        

        # Set minimum width for the table

        #self.table.setMinimumWidth(self.table.horizontalHeader().length() + self.table.verticalScrollBar().width())


        label_layout = QHBoxLayout(self)

        nombre_label = QLabel('Nombre del trabajador', self)

        #self.nombre_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        label_layout.addWidget(nombre_label)

        total_label = QLabel('Cantidad total de artículos', self)

        #self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        label_layout.addWidget(total_label)

        layout.addLayout(label_layout)



        self.data_layout = QHBoxLayout()

        #self.collected_name = QLabel(self)

        #self.collected_name.setStyleSheet("font-size: 16px; font-weight: bold;")

        #data_layout.addWidget(self.collected_name)

        #self.collected_quantity = QLabel(self)

        #self.collected_quantity.setStyleSheet("font-size: 16px; font-weight: bold;")

        #data_layout.addWidget(self.collected_quantity)

        layout.addLayout(self.data_layout)


        button_layout = QHBoxLayout()
        discard_button = QPushButton("Descartar")
        button_layout.addWidget(discard_button)
        confirm_button = QPushButton("Confirmar")
        button_layout.addWidget(confirm_button)

        confirm_button.clicked.connect(self.generate_pdf)

        discard_button.clicked.connect(self.go_back)
        
        layout.addLayout(button_layout)

        # Set layout

        #layout = QVBoxLayout()

        #layout.addWidget(self.table)

        self.setLayout(layout)

        self.show_summary()



    def add_item(self, code, desc, quantity):

        # Add an item to the inventory table

        row = self.table.rowCount()

        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(code)))

        self.table.setItem(row, 1, QTableWidgetItem(desc))

        self.table.setItem(row, 2, QTableWidgetItem(str(quantity)))


    #def get_worker(self, ):




    def show_summary(self):

        
        #nombre = self.collected_name
        #dotacion = self.collected_quantity

        try:

            conexion = conectar()

            cursor = conexion.cursor()

            sentencia_sql = '''SELECT * FROM pedido_final'''

            cursor.execute(sentencia_sql)

            datos = cursor.fetchall()

            if datos:

                suma = 0

                for dato in datos:

                    lista = list(dato)

                    self.add_item(dato[1], dato[2], dato[3])

                    suma += dato[3]

                rut = f"{lista[4]}"
                rut = rut.upper()

                
                #dotacion.setText(str(suma))
                dotacion = str(suma)

            conexion = conectar()

            cursor = conexion.cursor()

            sentencia_sql = '''SELECT nombre, apellido_paterno, apellido_materno FROM trabajador WHERE rut = ?'''

            cursor.execute(sentencia_sql, (rut,))

            datos = cursor.fetchall()

            if datos:

                for dato in datos:
                    lista = list(dato)
                nombre = f"{lista[0]} {lista[1]}" #MOSTRANDO SOLO APELLIDO PATERNO

            

            a = QLabel(nombre, self)
            a.setStyleSheet("font-size: 16px; font-weight: bold;")
            b = QLabel(dotacion, self)
            b.setStyleSheet("font-size: 16px; font-weight: bold;")

            layout = self.data_layout
            layout.addWidget(a)
            layout.addWidget(b)


                    

        except Error as err:

            print('Ha ocurrido un error: ', str(err) )

    def generate_pdf(self):

        my_string = f"{date}{time}{str(self.get_rut())}"

        auto_generated_filename = my_string.translate( { ord("/"): None, ord(":"): None } )
        

        print(auto_generated_filename)

        file_path = f"ppe-storage-cellar/receipts/{auto_generated_filename}.pdf"

    
        w, h = letter
        c = canvas.Canvas(file_path, pagesize=letter)
        #c.drawString(30, h - 50, "Línea")
        x = 120
        y = h - 45
        #c.line(x, y, x + 100, y)
        #c.drawString(30, h - 100, "Rectángulo")
        #c.rect(x, h - 120, 100, 50)
        #c.drawString(30, h - 170, "Círculo")
        #c.circle(170, h - 165, 20)
        #c.drawString(30, h - 240, "Elipse")
        #c.ellipse(x, y - 170, x + 100, y - 220)

        c.setFillColorCMYK(0.0, 0.0, 0.0, 0.93)
        #c.drawString(50, h - 50, "¡Hola, mundo!")
        #c.rect(50, h - 150, 50, 50, fill=True)

        c.setStrokeColorRGB(0, 0, 0)

        c.setFont("Helvetica-Bold", 16)
        #c.drawString(50, h - 50, "¡Hola, mundo!")
        #c.setFont("Times-Roman", 20)
        #c.drawString(130, h - 50, "¡Hola, mundo!")
        c.drawImage("ppe-storage-cellar/img/cellar-spark-logo.png", 32, 710, width=60, height=60, mask='auto')
        text = c.beginText(125, 735)
        text.textLine("ENTREGA DE ARTÍCULOS DESDE BODEGA")
        #text.textLine("¡Desde ReportLab y Python!")
        c.drawText(text)

        line1 = 'Fecha de entrega: '
        line2 = 'Hora: '

        x = 180
        y = 720


        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, line1)
        c.setFont('Helvetica', 10)
        textWidth = stringWidth(line1, 'Helvetica-Bold', 10) 
        x += textWidth + 2
        ejex = x
        c.drawString(x, y, date)

        x = ejex + stringWidth(date, 'Helvetica', 10) + 20

        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, line2)
        c.setFont('Helvetica', 10)
        textWidth = stringWidth(line2, 'Helvetica-Bold', 10) 
        x += textWidth + 2
        c.drawString(x, y, time)


        

        line1 = 'Nombre del consumidor: '
        line2 = 'RUT: '

        nombre = str(self.get_name())
        rut1 = str(self.get_rut())

        if len(rut1) == 9:
            rut = f"{rut1[0]}{rut1[1]}.{rut1[2]}{rut1[3]}{rut1[4]}.{rut1[5]}{rut1[6]}{rut1[7]}-{rut1[8]}"
        elif len(rut1) == 8:
            rut = f"{rut1[0]}.{rut1[1]}{rut1[2]}{rut1[3]}.{rut1[4]}{rut1[5]}{rut1[6]}-{rut1[7]}"


        x = 90
        y = 660


        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, line1)
        c.setFont('Helvetica', 12)
        textWidth = stringWidth(line1, 'Helvetica-Bold', 10) 
        x += textWidth + 2
        ejex = x
        c.drawString(x, y, nombre)

        x = ejex + stringWidth(nombre, 'Helvetica', 12) + 20

        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, line2)
        c.setFont('Helvetica', 12)
        textWidth = stringWidth(line2, 'Helvetica-Bold', 10) 
        x += textWidth + 2
        c.drawString(x, y, rut)

        c.setStrokeColorCMYK(0.0, 0.0, 0.0, 0.5)

        x = 60
        y = 650
        c.line(x, y, x + 480, y)

        c.setFont("Helvetica-Bold", 10)
        code_header = c.beginText(70, 635)
        code_header.textLine("Código")
        c.drawText(code_header)

        c.setFont("Helvetica-Bold", 10)
        description_header = c.beginText(180, 635)
        description_header.textLine("Descripción")
        c.drawText(description_header)

        c.setFont("Helvetica-Bold", 10)
        quantity_header = c.beginText(480, 635)
        quantity_header.textLine("Cantidad")
        c.drawText(quantity_header)

        x = 60
        y = 625
        c.line(x, y, x + 480, y)

        try:

            conexion = conectar()

            cursor = conexion.cursor()

            sentencia_sql = '''SELECT * FROM pedido_final'''

            cursor.execute(sentencia_sql)

            datos = cursor.fetchall()

            if datos:

                suma = 0

                j = 635
                n = 25
                i = 1

                for dato in datos:

                    y = j - (i * n)
                    lista = list(dato)


                    c.setFont("Helvetica", 10)
                    code = c.beginText(70, y)
                    code.textLine(str(dato[1]))
                    c.drawText(code)

                    c.setFont("Helvetica", 10)
                    description = c.beginText(180, y)
                    description.textLine(f"{dato[2]} ({self.get_brand(dato[1])})")
                    c.drawText(description)

                    c.setFont("Helvetica", 10)
                    quantity = c.beginText(480, y)
                    quantity.textLine(str(dato[3]))
                    c.drawText(quantity)

                    suma += dato[3]

                    i += 1
                    linex = 60
                    liney = y - 10
                    c.line(linex, liney, linex + 480, liney)

                    try:
                        cant_actual = int(self.get_stock(dato[1]))
                        cant_final = cant_actual - dato[3]
                        conexion = conectar()
                        cursor = conexion.cursor()
                        sentencia_sql = '''UPDATE epp SET cantidad_stock = ? WHERE codigo_epp = ?'''
                        cursor.execute(sentencia_sql, (cant_final, dato[1]))
                        conexion.commit()
                        conexion.close()
                    except Error as err:
                        print('Ha ocurrido un error', str(err))



                rut = lista[4]
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql = '''INSERT INTO vale_salida (rut, cantidad, timestamp, ubicacion) VALUES (?, ?, ?, ?)'''
                    cursor.execute(sentencia_sql, (rut, self.get_total_quantity(), f"{date} {time}", file_path))
                    conexion.commit()
                    conexion.close()
                except Error as err:
                    print('Ha ocurrido un error: ', str(err))



        except Error as err:
            print('Ha ocurrido un error', str(err))


        total_articulos_label = "Cantidad total de artículos entregados: "


        cant_articulos = str(self.get_total_quantity())

        x = 60
        y = 180


        c.setFont("Helvetica", 12)
        c.drawString(x, y, total_articulos_label)
        c.setFont('Helvetica-Bold', 12)
        textWidth = stringWidth(total_articulos_label, 'Helvetica', 12) 
        x += textWidth + 2
        c.drawString(x, y, cant_articulos)


        x = 70
        y = 90
        c.line(x, y, x + 200, y)

        x = 350
        y = 90
        c.line(x, y, x + 200, y)

        c.setFont("Helvetica-Bold", 9)
        
        
        text1 = c.beginText(90, 79)
        text2 = c.beginText(377, 79)
        text1.textLine("(Nombre y Firma del Bodeguero)")
        c.drawText(text1)
        text2.textLine("(Nombre y Firma del Consumidor)")
        c.drawText(text2)
        

        nombre_med = stringWidth(nombre, 'Helvetica', 12)
        mitad = nombre_med / 2
        punto_inicio = 450 - mitad
        c.setFont("Helvetica", 12)
        text3 = c.beginText(punto_inicio, 93)
        text3.textLine(nombre)
        c.drawText(text3)
        

        c.setFont("Helvetica", 8)

        #text1 = "Este documento registra la entrega de elementos de protección personal que el trabajador recibe en conformidad, de acuerdo a los "
        #text2 = "Artículos 151 al 156 del reglamento interno."
        #text1_width = stringWidth(text1, 'Helvetica', 8)
        #text2_width = stringWidth(text2, 'Helvetica', 8)
        #y = 50 # wherever you want your text to appear
        #pdf_text1_object = c.beginText((PAGE_WIDTH - text1_width) / 2.0, 29)
        #pdf_text2_object = c.beginText((PAGE_WIDTH - text2_width) / 2.0, 20)
        #pdf_text1_object.textLine(text1) # or: pdf_text_object.textLine(text) etc.
        #pdf_text2_object.textLine(text2)
#
        ##text1 = c.beginText(25, 50)
        ##text1.textLine("Este documento registra la entrega de elementos de protección personal que el trabajador recibe en")
        ##text1.textLine("conformidad de acuerdo al Artículo 151 al 156 del reglamento interno.")
        #c.drawText(pdf_text1_object)
        #c.drawText(pdf_text2_object)


        c.showPage()
        c.save()

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "DELETE FROM pedido_final"
            cursor.execute(sentencia_sql)
            conexion.commit()
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

        self.close()

        self.open_pdf(file_path)


    def open_pdf(self, path):
        ubicacion = path.translate({ord("/") : 92})
        os.system(ubicacion)

    def go_back(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "DELETE FROM pedido_final"
            cursor.execute(sentencia_sql)
            conexion.commit()
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))
        
        self.close()


    def get_rut(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT rut FROM pedido_final"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    rut = dato[0]
                    rut = rut.upper()
                    return rut
        except Error as err:
            print("Ha ocurrido un error: " + str(err))

    def get_name(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT nombre, apellido_paterno, apellido_materno FROM trabajador WHERE rut = ?"
            cursor.execute(sentencia_sql, (self.get_rut(),))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                    full_name = f"{str(lista[0])} {str(lista[1])} {str(lista[2])}"
                return full_name
        except Error as err:
            print("Ha ocurrido un error: " + str(err))

    def get_total_quantity(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT cantidad FROM pedido_final"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                total_quantity = 0
                for dato in datos:
                    lista = list(dato)
                    total_quantity += dato[0]
                return total_quantity
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def get_stock(self, code):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT cantidad_stock FROM epp WHERE codigo_epp = ?'''
            cursor.execute(sentencia_sql, (code,))
            datos = cursor.fetchall()
            for dato in datos:
                lista = list(dato)
                cantidad = lista[0]
            return cantidad
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def get_brand(self, code):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT marca FROM epp WHERE codigo_epp = ?"
            cursor.execute(sentencia_sql, (code,))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                    marca = lista[0]
                return marca
        except Error as err:
            print("Ha ocurrido un error: ", str(err))


            



