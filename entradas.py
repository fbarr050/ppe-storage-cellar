from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PySide6.QtGui import QIcon

from sqlite3 import Error

import os

from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, "es_ES")

from conexion import *
import form_trabajador

class EntriesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Entradas")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))

        self.setMinimumWidth(770)
        self.setMinimumHeight(480)

        self.filas = []
        
        self.data = self.fetch_data()

        
        self.items_per_page = 15
        self.current_page = 1

        self.init_ui()
        
    def init_ui(self):

        # Create table widget
        title_label = QLabel("Historial de Entradas", self)

        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.table = QTableWidget()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title_layout = QVBoxLayout()
        layout.addLayout(title_layout)
        

        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)
        


        table_layout = QHBoxLayout()
        layout.addLayout(table_layout)

        table_layout.addWidget(self.table)
        



        navigation_layout = QHBoxLayout()
        layout.addLayout(navigation_layout)

        pagination_layout = QHBoxLayout()
        layout.addLayout(pagination_layout)

        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(1)
        self.spin_box.setFixedWidth(60)
        navigation_layout.addWidget(self.spin_box)
        navigation_layout.setAlignment(Qt.AlignCenter)

        self.pagination_label = QLabel()
        self.pagination_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        pagination_layout.addWidget(self.pagination_label)
        pagination_layout.setAlignment(Qt.AlignRight)

        self.spin_box.valueChanged.connect(self.go_to_page)

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

    def get_description(self, code):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT descripcion FROM epp WHERE codigo_epp = ?"
            cursor.execute(sentencia_sql, (code,))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                    desc = f"{str(lista[0])}"
                return desc
        except Error as err:
            print("Ha ocurrido un error: " + str(err))


    def row_count(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT * FROM vale_entrada"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                conteo = 0
                for dato in datos:
                    conteo += 1
                return conteo
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def fetch_data(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM vale_entrada'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                if self.row_count() == 1:
                    lista1 = list(datos)
                    for dato in lista1:
                        lista2 = list(dato)
                        timestamp = datetime.strptime(lista2[4], '%Y-%m-%d')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        #hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        #self.add_history_item(fecha.capitalize(), trabajador, self.get_description(lista2[2]), str(lista2[3]), str(lista2[6]))
                        self.filas.append({"Fecha":fecha.capitalize(), "Registra":trabajador, "Artículo":self.get_description(lista2[2]), "Precio":str(lista2[3]), "Cantidad":str(lista2[6])})
                elif self.row_count() == 0:
                    pass
                else:
                    lista1 = list(datos)
                    x = 1
                    for dato in lista1:
                        
                        lista2 = list(lista1[self.row_count() - x])
                        #lista = list(dato)
                        timestamp = datetime.strptime(lista2[4], '%Y-%m-%d')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        #hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        self.filas.append({"Fecha":fecha.capitalize(), "Registra":trabajador, "Artículo":self.get_description(lista2[2]), "Precio":str(lista2[3]), "Cantidad":str(lista2[6])})
                        #self.add_history_item(fecha.capitalize(), trabajador, self.get_description(lista2[2]), str(lista2[3]), str(lista2[6]))
                        #self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Trabajador":trabajador, "Cantidad":lista2[2]})
                        #self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                        #print(self.filas)
                        x += 1
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

        data = self.filas
        return data
    
    def update_table_and_pagination(self):
        try:
            self.table.clearContents()

            total_pages = (len(self.data) + self.items_per_page - 1) // self.items_per_page
            self.current_page = max(1, min(self.current_page, total_pages))

            start_index = (self.current_page - 1) * self.items_per_page
            end_index = min(start_index + self.items_per_page, len(self.data))

            self.table.setRowCount(end_index - start_index)
            self.table.setColumnCount(len(self.data[0]))


            self.table.setColumnWidth(0, 120) 
            self.table.setColumnWidth(1, 220) 
            self.table.setColumnWidth(2, 160)
            self.table.setColumnWidth(3, 120)
            self.table.setColumnWidth(4, 90)


            headers = list(self.data[0].keys())
            self.table.setHorizontalHeaderLabels(headers)

            for row, data_item in enumerate(self.data[start_index:end_index]):
                for col, value in enumerate(data_item.values()):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row, col, item)





            self.pagination_label.setText(f"Página {self.current_page}/{total_pages}")

            self.spin_box.setMaximum(total_pages)
            self.spin_box.setValue(self.current_page)
        except:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No existe registro")
            dlg.setText("Aún no se han registrado entradas de artículos.")
            dlg.setIcon(QMessageBox.Information)
            self.close()

    def go_to_page(self, page):
        self.current_page = page
        self.update_table_and_pagination()