from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtGui import QIcon

from sqlite3 import Error
from conexion import *

import gc
import os
import cellarspark
import form_trabajador_mod

class EmployeesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usuarios")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))

        self.setMinimumWidth(1060)
        self.setMinimumHeight(480)
        
        self.init_ui()

    def init_ui(self):
        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Number of columns
        self.table.setHorizontalHeaderLabels(["RUT", "Nombres", "Apellido Paterno", "Apellido Materno", "T. de Zapatos", "T. de Pantalones", "T. de Camisa", "", ""])  # Column headers

        self.show_registered_employees()
        
        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.editar_trabajador = None



        
    def add_person(self, rut, name, apellidop, apellidom, tallaz, tallap, tallac):
        # Add an item to the inventory table
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(rut))
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(apellidop))
        self.table.setItem(row, 3, QTableWidgetItem(apellidom))
        self.table.setItem(row, 4, QTableWidgetItem(tallaz))
        self.table.setItem(row, 5, QTableWidgetItem(tallap))
        self.table.setItem(row, 6, QTableWidgetItem(tallac))



    def show_registered_employees(self):
        try:
            #self.table.clearContents()
            self.table.setRowCount(0)

            
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM trabajador'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                    rut1 = str(lista[1])
                    if len(rut1) == 9:
                        rut = f"{rut1[0]}{rut1[1]}.{rut1[2]}{rut1[3]}{rut1[4]}.{rut1[5]}{rut1[6]}{rut1[7]}-{rut1[8]}"
                    elif len(rut1) == 8:
                        rut = f"{rut1[0]}.{rut1[1]}{rut1[2]}{rut1[3]}.{rut1[4]}{rut1[5]}{rut1[6]}-{rut1[7]}"

                    self.add_person(rut, lista[2], lista[3], lista[4], str(lista[5]), str(lista[6]), lista[7])
            
            self.table.setColumnWidth(0, 150) 
            self.table.setColumnWidth(1, 180) 
            self.table.setColumnWidth(2, 120)
            self.table.setColumnWidth(3, 120)
            self.table.setColumnWidth(4, 80)
            self.table.setColumnWidth(5, 100)
            self.table.setColumnWidth(6, 80)
            self.table.setColumnWidth(7, 80)
            self.table.setColumnWidth(8, 80)


            column_index_with_button = 7  # Replace 2 with the actual index of the column where you want to add buttons.
            for row in range(self.table.rowCount()):
                update_button = QPushButton("Editar")
                update_button.clicked.connect(self.on_button_clicked)  # Connect the clicked signal to a slot
                self.table.setCellWidget(row, column_index_with_button, update_button)

            column_index_with_del_button = 8  # Replace 2 with the actual index of the column where you want to add buttons.
            for row in range(self.table.rowCount()):
                delete_button = QPushButton("Eliminar")
                delete_button.clicked.connect(self.on_del_button_clicked)  # Connect the clicked signal to a slot
                self.table.setCellWidget(row, column_index_with_del_button, delete_button)
            
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

    def on_button_clicked(self):
        button = self.sender()  # Get the button that was clicked
        index = self.table.indexAt(button.pos())  # Get the index of the clicked button
        if index.isValid():
            row = index.row()
            column = index.column()

            lista_rut = self.get_rut_list()
            rut = lista_rut[row]
            f = open("ppe-storage-cellar/rut.txt", "w")
            f.write(rut)
            f.close()
            self.editar_trabajador = form_trabajador_mod.TrabajadorForm()
            self.editar_trabajador.show()
            self.close()


    def get_rut_list(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT rut FROM trabajador"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                rut_list = []
                for dato in datos:
                    lista = list(dato)
                    rut = lista[0]
                    rut_list.append(rut)
                return rut_list
        except Error as err:
            print("Ha ocurrido un error: ", str(err))    

    def on_del_button_clicked(self):
        button = self.sender()  # Get the button that was clicked
        index = self.table.indexAt(button.pos())  # Get the index of the clicked button
        if index.isValid():
            row = index.row()
            column = index.column()

            lista_rut = self.get_rut_list()
            rut = lista_rut[row]
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Eliminar trabajador")
            dlg.setText("¿Está seguro de que desea eliminar este trabajador?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Warning)
            button = dlg.exec()

            if button == QMessageBox.Yes:
                print("Yes!")
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql = "DELETE FROM trabajador WHERE rut = ?"
                    cursor.execute(sentencia_sql, (rut,))
                    conexion.commit()
                    conexion.close()
                    self.show_registered_employees()
                except Error as err:
                    print("Ha ocurrido un error: ", str(err))
            else:
                print("No!")
            
        
        
    
