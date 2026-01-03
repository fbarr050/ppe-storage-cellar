from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QCompleter
from sqlite3 import Error

import os

from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, "es_ES")

from conexion import *

import consumo



class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Consumo")

        self.setMinimumWidth(803)
        self.setMinimumHeight(480)
        
        self.filas = []
        
        self.data = self.show_certain_worker_history()

        


        self.items_per_page = 15
        self.current_page = 1

        

        self.init_ui()

    def init_ui(self):


        

        title_label = QLabel("Historial de Consumo", self)

        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.table = QTableWidget()
        

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title_layout = QVBoxLayout()
        self.layout.addLayout(title_layout)
        

        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)
        

        table_layout = QHBoxLayout()
        self.layout.addLayout(table_layout)

        table_layout.addWidget(self.table)
        

        navigation_layout = QHBoxLayout()
        self.layout.addLayout(navigation_layout)

        pagination_layout = QHBoxLayout()
        self.layout.addLayout(pagination_layout)

        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(1)
        self.spin_box.setFixedWidth(60)
        navigation_layout.addWidget(self.spin_box)
        navigation_layout.setAlignment(Qt.AlignCenter)

        self.back_button = QPushButton("< Atrás")
        pagination_layout.addWidget(self.back_button)


        self.pagination_label = QLabel()
        self.pagination_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        pagination_layout.addWidget(self.pagination_label)
        pagination_layout.setAlignment(Qt.AlignJustify)


        self.spin_box.valueChanged.connect(self.go_to_page)
        self.back_button.clicked.connect(self.volver)
        

        self.update_table_and_pagination()

        
    def fetch_data(self):

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM vale_salida'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                if self.row_count() == 1:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(dato)
                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista2[2]})

                elif self.row_count() == 0:
                    pass
                else:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(lista1[-1])

                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista2[2]})
                        lista1.pop()
                    lista3 = list(lista1[0])
                    timestamp = datetime.strptime(lista3[3], '%d/%m/%Y %H:%M:%S')
                    fecha = timestamp.strftime("%a %d %b %Y")
                    hora = timestamp.strftime("%H:%M:%S")
                    trabajador = self.get_name(lista3[1])
                    self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista3[2]})

        except Error as err:
            print("Ha ocurrido un error: ", str(err))

        data = self.filas
        return data

    def update_table_and_pagination(self):
        self.table.clearContents()

        total_pages = (len(self.data) + self.items_per_page - 1) // self.items_per_page
        self.current_page = max(1, min(self.current_page, total_pages))

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, len(self.data))

        self.table.setRowCount(end_index - start_index)
        self.table.setColumnCount(len(self.data[0]) + 1)

        self.table.setColumnWidth(0, 180) 
        self.table.setColumnWidth(1, 130) 
        self.table.setColumnWidth(2, 220)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 90)

        column_index_with_button = 4  # Replace 2 with the actual index of the column where you want to add buttons.
        for row in range(self.table.rowCount()):
            button = QPushButton("Ver detalles")
            button.clicked.connect(self.on_button_clicked)  # Connect the clicked signal to a slot
            self.table.setCellWidget(row, column_index_with_button, button)

        headers = list(self.data[0].keys())
        headers.append("Detalle")
        self.table.setHorizontalHeaderLabels(headers)

        for row, data_item in enumerate(self.data[start_index:end_index]):
            for col, value in enumerate(data_item.values()):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

        

        

        self.pagination_label.setText(f"Página {self.current_page}/{total_pages}")

        self.spin_box.setMaximum(total_pages)
        self.spin_box.setValue(self.current_page)


    def go_to_page(self, page):
        self.current_page = page
        self.update_table_and_pagination()
        
        


    def get_name(self, rut):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT nombre, apellido_paterno, apellido_materno FROM trabajador WHERE rut = ?"
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                    full_name = f"{str(lista[0])} {str(lista[1])} {str(lista[2])}"
                return full_name
        except Error as err:
            print("Ha ocurrido un error: " + str(err))



    def open_pdf(self, path):
        ubicacion = path.translate({ord("/") : 92})
        os.system(ubicacion)

    
    def on_button_clicked(self):
        f = open("ppe-storage-cellar/rut.txt", "r")
        rut = f.read()
        button = self.sender()  # Get the button that was clicked
        index = self.table.indexAt(button.pos())  # Get the index of the clicked button
        if index.isValid():
            row = index.row()
            column = index.column()
            print(self.row_count())
            #fila = self.row_count() - row
            fila = row
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = '''SELECT ubicacion FROM vale_salida WHERE rut = ?'''
                cursor.execute(sentencia_sql, (rut,))
                datos = cursor.fetchall()
                if datos:
                    lista_invertida = []
                    for x in range(self.row_count()):
                        y = datos[self.row_count() - (x + 1)]
                        lista_invertida.append(y)
                    print(lista_invertida[fila][0])
                    self.open_pdf(lista_invertida[fila][0])
            except Error as err:
                print('Ha ocurrido un error: ', str(err))

    def row_count(self):
        f = open("ppe-storage-cellar/rut.txt", "r")
        rut = f.read()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT * FROM vale_salida WHERE rut = ?"
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            if datos:
                conteo = 0
                for dato in datos:
                    conteo += 1
                return conteo
        except Error as err:
            print('Ha ocurrido un error: ', str(err))
    
    def show_consumption_history_upside_down(self):
        
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM vale_salida'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                if self.row_count() == 1:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(dato)
                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])

                        self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                elif self.row_count() == 0:
                    pass
                else:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(lista1[-1])
                        #lista = list(dato)
                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])

                        self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                        lista1.pop()
                    lista3 = list(lista1[0])
                    timestamp = datetime.strptime(lista3[3], '%d/%m/%Y %H:%M:%S')
                    fecha = timestamp.strftime("%a %d %b %Y")
                    hora = timestamp.strftime("%H:%M:%S")
                    trabajador = self.get_name(lista3[1])
                    self.add_history_item(fecha.capitalize(), hora, trabajador, lista3[2])
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

        

    def show_certain_worker_history(self):
        f = open("ppe-storage-cellar/rut.txt", "r")
        rut = f.read()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM vale_salida WHERE rut = ?'''
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            if datos:
                if self.row_count_rut(rut) == 1:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(dato)
                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista2[2]})
                        #self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                elif self.row_count_rut(rut) == 0:
                    pass
                else:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(lista1[-1])
                        #lista = list(dato)
                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista2[2]})
                        #self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                        lista1.pop()
                    lista3 = list(lista1[0])
                    timestamp = datetime.strptime(lista3[3], '%d/%m/%Y %H:%M:%S')
                    fecha = timestamp.strftime("%a %d %b %Y")
                    hora = timestamp.strftime("%H:%M:%S")
                    trabajador = self.get_name(lista3[1])
                    self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista3[2]})
                    #self.add_history_item(fecha.capitalize(), hora, trabajador, lista3[2])
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

        data = self.filas
        return data

    def get_rut(self, name):
        lista = name.split()
        if len(lista) == 4:
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = "SELECT rut FROM trabajador WHERE nombre = ? AND apellido_paterno = ? AND apellido_materno = ?"
                nombres = f"{lista[0]} {lista[1]}"
                cursor.execute(sentencia_sql, (nombres, lista[2], lista[3]))
                datos = cursor.fetchall()
                for dato in datos:
                    rut = dato[0]
                return rut
            except Error as err:
                print("ha ocurrido un error: ", str(err))
        elif len(lista) == 3:
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = "SELECT rut FROM trabajador WHERE nombre = ? AND apellido_paterno = ? AND apellido_materno = ?"
                cursor.execute(sentencia_sql, (lista[0], lista[1], lista[2]))
                datos = cursor.fetchall()
                for dato in datos:
                    rut = dato[0]
                print(rut)
                return rut
            except Error as err:
                print("ha ocurrido un error: ", str(err))
                
    def row_count_rut(self, rut):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT * FROM vale_salida WHERE rut = ?"
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            if datos:
                conteo = 0
                for dato in datos:
                    conteo += 1
                return conteo
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def volver(self):
        self.consumption_view = consumo.ConsumptionView()
        self.consumption_view.show()
        self.close()