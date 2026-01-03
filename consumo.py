from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QCompleter, QMessageBox
from sqlite3 import Error
from PySide6.QtGui import QIcon

import os

from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, "es_ES")

from conexion import *
import historial



class ConsumptionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Consumo")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))

        self.setMinimumWidth(740)
        self.setMinimumHeight(620)
        
        self.filas = []
        
        self.data = self.fetch_data()

        

        
        self.items_per_page = 15
        self.current_page = 1

        

        self.init_ui()

    def init_ui(self):


        self.individual_history = None

        title_label = QLabel("Historial de Consumo", self)

        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        
        self.item_label = QLabel("Trabajador:")
        self.item_input = QComboBox()
        self.item_input.setEditable(True)  # Allow user to enter custom items
        self.item_input.setInsertPolicy(QComboBox.InsertAtTop)  # Insert new items at the top
        #self.item_input.setCompleter(None)  # Disable automatic completion
        submit_button = QPushButton("Buscar")
        submit_button.setFixedWidth(90)
        
        submit_button.clicked.connect(self.btn_action)

        # Create a model for the item dropdown
        self.item_model = QStandardItemModel()
        self.item_input.setModel(self.item_model)
        
        completer = QCompleter(self.get_names())
        self.item_input.setCompleter(completer)

        

        self.table = QTableWidget()


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title_layout = QVBoxLayout()
        self.layout.addLayout(title_layout)
        

        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)

        search_layout = QHBoxLayout()
        self.layout.addLayout(search_layout)

        search_layout.addWidget(self.item_label)
        #self.item_label.setAlignment(Qt.AlignCenter)
        search_layout.addWidget(self.item_input)
        search_layout.addWidget(submit_button)
        search_layout.setAlignment(Qt.AlignCenter)
        


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

        self.pagination_label = QLabel()
        self.pagination_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        pagination_layout.addWidget(self.pagination_label)
        pagination_layout.setAlignment(Qt.AlignRight)

        self.spin_box.valueChanged.connect(self.go_to_page)

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
                        self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Consumidor":trabajador, "Cantidad":lista2[2]})
                        #self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                elif self.row_count() == 0:
                    pass
                else:
                    lista1 = list(datos)
                    x = 1
                    for dato in lista1:
                        
                        lista2 = list(lista1[self.row_count() - x])
                        #lista = list(dato)
                        timestamp = datetime.strptime(lista2[3], '%d/%m/%Y %H:%M:%S')
                        fecha = timestamp.strftime("%a %d %b %Y")
                        hora = timestamp.strftime("%H:%M:%S")
                        trabajador = self.get_name(lista2[1])
                        self.filas.append({"Fecha":fecha.capitalize(), "Hora":hora, "Consumidor":trabajador, "Cantidad":lista2[2]})
                        #self.add_history_item(fecha.capitalize(), hora, trabajador, lista2[2])
                        print(self.filas)
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
            self.table.setColumnCount(len(self.data[0]) + 1)

            self.table.setColumnWidth(0, 140) 
            self.table.setColumnWidth(1, 80) 
            self.table.setColumnWidth(2, 250)
            self.table.setColumnWidth(3, 130)
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
        except:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No existe registro")
            dlg.setText("Aún no se han registrado salidas de artículos.")
            dlg.setIcon(QMessageBox.Information)
            self.close()


    def go_to_page(self, page):
        self.current_page = page
        self.update_table_and_pagination()
        
        
    def add_item(self, item):
        # Add an item to the dropdown
        standard_item = QStandardItem(item)
        self.item_model.appendRow(standard_item)


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
        button = self.sender()  # Get the button that was clicked
        index = self.table.indexAt(button.pos())  # Get the index of the clicked button
        if index.isValid():
            row = index.row()
            column = index.column()
            k = (self.current_page - 1) * 15
            fila = self.row_count() - (row + k)
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = '''SELECT ubicacion FROM vale_salida WHERE id_vale_salida = ?'''
                cursor.execute(sentencia_sql, (fila,))
                datos = cursor.fetchall()
                if datos:
                    for dato in datos:
                        lista = list(dato)
                        self.open_pdf(lista[0])
            except Error as err:
                print('Ha ocurrido un error: ', str(err))

    def row_count(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT * FROM vale_salida"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                conteo = 0
                for dato in datos:
                    conteo += 1
                return conteo
        except Error as err:
            print('Ha ocurrido un error: ', str(err))
    
        

    def btn_action(self):
        rut = self.get_rut(self.item_input.currentText())
        f = open("ppe-storage-cellar/rut.txt", "w")
        f.write(rut)
        f.close()
        self.individual_history = historial.HistoryView()
        self.individual_history.show()
        self.close()

    def get_names(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT rut FROM vale_salida"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                un_set = {}
                nombres0 = set(un_set)
                for dato in datos:
                    lista = list(dato)
                    nombres0.add(f"{self.get_name(lista[0])}")
                nombres = list(nombres0)
                for nombre in nombres:
                    self.add_item(nombre)
                return nombres
        except Error as err:
            print("Ha ocurrido un error: ", str(err))
                
    def add_item(self, item):
        # Add an item to the dropdown
        standard_item = QStandardItem(item)
        self.item_model.appendRow(standard_item)


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
