from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QDialog, QHBoxLayout, QDateEdit
from PySide6.QtGui import QIcon

from conexion import *
from sqlite3 import Error

import form_epp
import form_trabajador

from cellarspark import *

class NewArticleForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingresar Nuevo Artículo")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))
        
        # Create form widgets
        self.rut_label = QLabel("Ingrese su RUT (bodeguero):")
        self.rut_input = QLineEdit()
        self.cod_label = QLabel("Código del artículo:")
        self.cod_input = QLineEdit()
        self.price_label = QLabel("Precio:")
        self.price_input = QLineEdit()
        self.fec_ingreso_label = QLabel("Fecha de ingreso:")
        self.fec_ingreso_input = QDateEdit()
        self.fec_ingreso_input.setCalendarPopup(True)
        self.fec_venc_label = QLabel("Fecha de expiración:")
        self.fec_venc_input = QDateEdit()
        self.fec_venc_input.setCalendarPopup(True)
        self.quantity_label = QLabel("Cantidad:")
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1000)  # Set the range of allowed values

        # Set default date to today
        self.fec_ingreso_input.setDate(QDate.currentDate())
        self.fec_venc_input.setDate(QDate.currentDate())
        
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.rut_label)
        layout.addWidget(self.rut_input)
        layout.addWidget(self.cod_label)
        layout.addWidget(self.cod_input)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(self.fec_ingreso_label)
        layout.addWidget(self.fec_ingreso_input)
        layout.addWidget(self.fec_venc_label)
        layout.addWidget(self.fec_venc_input)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)

        
        # Create button layout
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar")
        cancel_button = QPushButton("Cancelar")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        # Connect button signals
        save_button.clicked.connect(self.save_article)
        cancel_button.clicked.connect(self.close)
        
        # Set layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.nuevoepp_form = None
        
    def save_article(self):
        # Get the entered article details and save to the database
        self.validate_quantity()

        self.validar_trabajador()

        rut = self.rut_input.text().strip().replace(".", "").replace("-", "")
        rut = rut.upper()
        ppe_code = self.cod_input.text()
        precio = float(self.price_input.text())
        fecha_ingreso = self.fec_ingreso_input.date().toString(Qt.ISODate)
        fecha_venc = self.fec_venc_input.date().toString(Qt.ISODate)
        cantidad = self.quantity_input.value()

        
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''INSERT INTO vale_entrada (
            rut, codigo_epp, precio, fecha_entrada, fecha_expiracion, cantidad
            ) VALUES (?, ?, ?, ?, ?, ?)'''
            datos = (rut, ppe_code, precio, fecha_ingreso, fecha_venc, cantidad)
            cursor.execute(sentencia_sql, datos)
            conexion.commit()
            conexion.close()
            self.actualizar_epp(ppe_code, cantidad)
        except Error as err:
            return 'Ha ocurrido un error\t' + str(err)

        


    def actualizar_epp(self, codigo, cant):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM epp WHERE codigo_epp = ?'''
            cursor.execute(sentencia_sql, (codigo,))
            datos = cursor.fetchall()
            
            if datos:
                try:
                    for dato in datos:
                        lista = list(dato)
                        cant_antigua = int(lista[3])
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql = '''UPDATE epp SET cantidad_stock = ? WHERE codigo_epp = ?'''
                    #UNA TABLA Y UNA COLUMNA PUEDEN TENER EL MISMO NOMBRE
                    total = cant_antigua + cant
                    datos = (total, codigo)
                    cursor.execute(sentencia_sql, datos)
                    conexion.commit()
                    conexion.close()
                    print('Se modificó el stock del EPP')
                    self.close()
                except Error as err:
                    return 'Ha ocurrido un error ' + str(err)
            else:
                try:
                    self.show_newppe_form()
                except Error as err:
                    return 'Ha ocurrido un error\t' + str(err)
        except Error as err:
            print('Ha ocurrido un error ' + str(err))
        #return datos
            
        self.close()

    def show_newppe_form(self):
        self.nuevoepp_form = form_epp.AgregarEPPForm()
        self.nuevoepp_form.show()

    def validate_quantity(self):
        quantity = self.quantity_input.value()
        if quantity == 0:
            self.quantity_input.setValue(1)

    def validar_trabajador(self):
        rut = self.rut_input.text().strip().replace(".", "").replace("-", "")
        rut = rut.upper()
    
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT nombre FROM trabajador WHERE rut = ?'''
            cursor.execute(sentencia_sql, (rut,))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    nombre = dato[0]
                if nombre == None or not nombre:
                    try:
                        conexion = conectar()
                        cursor = conexion.cursor()
                        sentencia_sql = '''SELECT rut FROM trabajador WHERE rut = ?'''
                        cursor.execute(sentencia_sql, (rut,))
                        datos = cursor.fetchall()
                        if datos:
                            self.registrar_trabajador = form_trabajador.NuevoTrabajadorForm()
                            self.registrar_trabajador.show()
                        else:
                            try:
                                conexion = conectar()
                                cursor = conexion.cursor()
                                sentencia_sql = '''INSERT INTO trabajador (rut) VALUES (?)'''
                                cursor.execute(sentencia_sql, (rut,))
                                conexion.commit()
                                conexion.close()
                                self.registrar_trabajador = form_trabajador.NuevoTrabajadorForm()
                                self.registrar_trabajador.show()
                            except Error as err:
                                print('Ha ocurrido un error: ', str(err))
                    except Error as err:
                        print('Ha ocurrido un error:', str(err))
            else:
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql = '''INSERT INTO trabajador (rut) VALUES (?)'''
                    cursor.execute(sentencia_sql, (rut,))
                    conexion.commit()
                    conexion.close()
                    self.registrar_trabajador = form_trabajador.NuevoTrabajadorForm()
                    self.registrar_trabajador.show()
                except Error as err:
                    print('Ha ocurrido un error: ', str(err))
        except Error as err:
            print('Ha ocurrido un error: ', str(err))
