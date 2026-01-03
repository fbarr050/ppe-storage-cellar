from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QHBoxLayout, QCompleter, QDialog, QTableView
from PySide6.QtGui import QIcon

from sqlite3 import Error

from conexion import *
import form_entrega

import trabajadores


class TrabajadorForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modificar Usuario")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))
        self.rut_label = QLabel("RUT:")
        self.rut_input = QLineEdit()
        self.nombre_label = QLabel("Nombres:")
        self.nombre_input = QLineEdit()
        self.apellidop_label = QLabel("Apellido paterno:")
        self.apellidop_input = QLineEdit()
        self.apellidom_label = QLabel("Apellido materno:")
        self.apellidom_input = QLineEdit()
        self.shoesize_label = QLabel("Talla de zapatos:")
        self.shoesize_input = QSpinBox()
        self.shoesize_input.setRange(36, 46)
        self.pantsize_label = QLabel("Talla de pantalón:")
        self.pantsize_input = QSpinBox()
        self.pantsize_input.setRange(42, 56)
        self.shirtsize_label = QLabel("Talla de camisa:")
        self.shirtsize_input = QComboBox()
        self.shirtsize_input.setEditable(True)  # Allow user to enter custom items
        self.shirtsize_input.setInsertPolicy(QComboBox.InsertAtTop)
        
        self.add_button = QPushButton("Guardar")
        self.cancel_button = QPushButton("Cancelar")

        self.rut_input.setText(self.get_rut())
        rut = self.get_rut()
        lista = self.get_data(rut)
        nombre = lista[0]
        apellidop = lista[1]
        apellidom = lista[2]
        tallaz = lista[3]
        tallap = lista[4]
        tallac = lista[5]

        self.nombre_input.setText(nombre)
        self.apellidop_input.setText(apellidom)
        self.apellidom_input.setText(apellidop)
        self.shoesize_input.setValue(tallaz)
        self.pantsize_input.setValue(tallap)
        

        self.shirt_model = QStandardItemModel()
        self.shirtsize_input.setModel(self.shirt_model)
    
        self.shirtsize_input.setCurrentText(str(tallac))

        layout = QVBoxLayout()
        layout.addWidget(self.rut_label)
        layout.addWidget(self.rut_input)
        layout.addWidget(self.nombre_label)
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.apellidop_label)
        layout.addWidget(self.apellidop_input)
        layout.addWidget(self.apellidom_label)
        layout.addWidget(self.apellidom_input)
        layout.addWidget(self.shoesize_label)
        layout.addWidget(self.shoesize_input)
        layout.addWidget(self.pantsize_label)
        layout.addWidget(self.pantsize_input)
        layout.addWidget(self.shirtsize_label)
        layout.addWidget(self.shirtsize_input)


        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.add_item("XS")
        self.add_item("S")
        self.add_item("M")
        self.add_item("L")
        self.add_item("XL")
        self.add_item("XXL")

        self.delete(rut)

        self.add_button.clicked.connect(self.agregar_trabajador)
        self.cancel_button.clicked.connect(self.close_window)

        self.datos_trabajadores = None
    #def enviar_sap(self):
    #    sap = self.sap_input.text()
    #    return sap
    def add_item(self, item):
        # Add an item to the dropdown
        standard_item = QStandardItem(item)
        self.shirt_model.appendRow(standard_item)


    def get_rut(self):
        f = open("ppe-storage-cellar/rut.txt", "r")
        rut = f.read()
        rut = rut.upper()
        print(rut)
        return rut
    
    def get_data(self, rut):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT nombre, apellido_paterno, apellido_materno, talla_zapatos, talla_pantalon, talla_camisa FROM trabajador WHERE rut = ?"
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                return lista
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

    def delete(self, rut):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "DELETE FROM trabajador WHERE rut = ?"
            cursor.execute(sentencia_sql, (rut,))
            conexion.commit()
            conexion.close()
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

    def agregar_trabajador(self):
        rut = self.rut_input.text().strip().replace(".", "").replace("-", "")
        rut = rut.upper()
        nombre = self.nombre_input.text().title()
        apellido_paterno = self.apellidop_input.text().title()
        apellido_materno = self.apellidom_input.text().title()
        talla_zapatos = self.shoesize_input.value()
        talla_pantalon = self.pantsize_input.value()
        talla_camisa = self.shirtsize_input.currentText()

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT rut FROM trabajador WHERE rut = ?'''
            print(rut)
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            for dato in datos:
                exists = dato[0]
            try:
                exists
            except:
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql='''INSERT INTO trabajador (rut, nombre, apellido_paterno, apellido_materno, talla_zapatos, talla_pantalon, talla_camisa)
                    VALUES (?, ?, ?, ?, ?, ?, ?)'''
                    cursor.execute(sentencia_sql, (rut, nombre, apellido_paterno, apellido_materno, talla_zapatos, talla_pantalon, talla_camisa))
                    conexion.commit()
                    conexion.close()
                    self.show_employees_view()
                    self.close()
                except Error as err:
                    print('Ha ocurrido un error: ', str(err))
            else:
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql='''UPDATE trabajador SET nombre = ?, apellido_paterno = ?, apellido_materno = ?, talla_zapatos = ?, talla_pantalon = ?, talla_camisa = ?
                    WHERE rut = ?'''
                    cursor.execute(sentencia_sql, (nombre, apellido_paterno, apellido_materno, talla_zapatos, talla_pantalon, talla_camisa, rut))
                    conexion.commit()
                    conexion.close()
                    self.show_employees_view()
                    self.close()
                except Error as err:
                    print('Ha ocurrido un error: ', str(err))
        except Error as err:
            print(str('Ha ocurrido un error: ', str(err)))   

    def delete_row(self):
        rut = self.rut_input.text().strip().replace(".", "").replace("-", "")
        rut = rut.upper()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''DELETE FROM trabajador WHERE rut = ?'''
            cursor.execute(sentencia_sql, (rut,))
            conexion.commit()
            conexion.close()
            self.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def close_window(self):
        self.close()



    def show_employees_view(self):
        self.datos_trabajadores = trabajadores.EmployeesView()
        self.datos_trabajadores.show()