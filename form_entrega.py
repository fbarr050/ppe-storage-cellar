from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QHBoxLayout, QCompleter, QMessageBox
from sqlite3 import Error

from conexion import *

import pedido
import form_trabajador


class RequestForm(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create form widgets
        self.rut_label = QLabel("RUT del consumidor:")
        self.rut_input = QLineEdit()
        self.item_label = QLabel("Nombre del artículo:")
        self.item_input = QComboBox()
        self.item_input.setEditable(True)  # Allow user to enter custom items
        self.item_input.setInsertPolicy(QComboBox.InsertAtTop)  # Insert new items at the top
        self.quantity_label = QLabel("Cantidad:")
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000)
        self.more_ppe_button = QPushButton("Agregar")
        self.submit_button = QPushButton("Listo")
        self.cancel_button = QPushButton("Cancelar")

        self.item_model = QStandardItemModel()
        self.item_input.setModel(self.item_model)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.rut_label)
        layout.addWidget(self.rut_input)
        layout.addWidget(self.item_label)
        layout.addWidget(self.item_input)
        layout.addWidget(self.quantity_label)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(self.quantity_input)
        quantity_layout.addWidget(self.more_ppe_button)

        self.more_ppe_button.clicked.connect(self.more_ppe)
        self.cancel_button.clicked.connect(self.cancelar_pedido)
        self.submit_button.clicked.connect(self.normalizar_pedido)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)

        # Set layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(layout)
        self.main_layout.addLayout(quantity_layout)
        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)

        self.records = False
        
        self.check_existences()

        if self.records:
            items = [
                self.show_ppe_descs(),
                self.show_ppe_codes()
            ]

            model = QStandardItemModel()

            # Populate the model with QStandardItems
            for item in items:
                row = []
                for value in item:
                    row.append(QStandardItem(value))
                model.appendRow(row)

            # Create a QCompleter with the model
            completer = QCompleter(model)
            self.item_input.setCompleter(completer)

        self.mostrar_pedido = None
        self.registrar_trabajador = None


        
    def add_item(self, item):
        # Add an item to the dropdown
        standard_item = QStandardItem(item)
        self.item_model.appendRow(standard_item)
    
    def show_ppe_descs(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT descripcion FROM epp'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                descripciones = []
                for dato in datos:
                    lista = list(dato)
                    self.add_item(lista[0])
                    descripciones.append(lista[0])
                return descripciones
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def show_ppe_codes(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT codigo_epp FROM epp'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                codigos = []
                for dato in datos:
                    lista = list(dato)
                    codigos.append(str(lista[0]))
                return codigos
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def validate_quantity(self):
        quantity = self.quantity_input.value()
        if quantity == 0:
            self.quantity_input.setValue(1)

    def more_ppe(self):
        self.validate_quantity()
        ppe_name = self.item_input.currentText()
        quantity = self.quantity_input.value()
        ppe_code = None


        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT codigo_epp FROM epp WHERE descripcion = ?'''
            cursor.execute(sentencia_sql, (ppe_name,))
            datos = cursor.fetchall()
            if datos:
                nuevos_datos = []
                for dato in datos:
                    lista = list(dato)
                    ppe_code = lista[0]
                self.show_ppe_summary(ppe_code, ppe_name, quantity)
        except Error as err:
            print("Ha ocurrido un error: ", str(err))
       
        
        
                
    def show_ppe_summary(self, codigo, descripcion, cantidad):

        
        code = QLabel(f"{codigo}", self)
        description = QLabel(f"{descripcion}", self)
        quantity = QLabel(f"{cantidad}", self)

        layout = self.main_layout
        layout.addWidget(code)
        layout.addWidget(description)
        layout.addWidget(quantity)

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''INSERT INTO pedido (codigo, descripcion, cantidad)
            VALUES (?, ?, ?)'''
            cursor.execute(sentencia_sql, (codigo, descripcion, cantidad))
            conexion.commit()
            conexion.close()
            #self.resumen_pedido()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def validar_trabajador(self):
        rut = self.rut_input.text().strip().replace(".", "").replace("-", "")
        rut = rut.upper()
        print(rut)
    
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


    def validar_pedido(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM pedido'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if not datos:
                msgBox = QMessageBox()
                msgBox.setText("Debe agregar al menos un artículo para continuar.")
                msgBox.exec()
            else:
                codigos = {}
                for dato in datos:
                    lista = list(dato)
                    codigo = lista[1]
                    codigos[codigo] = None
                for x in codigos.keys():
                    try:
                        conexion = conectar()
                        cursor = conexion.cursor()
                        sentencia_sql = '''SELECT codigo, cantidad FROM pedido WHERE codigo = ?'''
                        cursor.execute(sentencia_sql, (x,))
                        datos = cursor.fetchall()
                        i = 0
                        for dato in datos:
                            lista = list(dato)
                            a = lista[0]
                            b = lista[1]
                            i += b
                        codigos[a] = i
                    except Error as err:
                        print('Ha ocurrido un error: ', str(err))
                return codigos
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def normalizar_pedido(self):
        self.validar_trabajador()
        nuevos_datos = self.validar_pedido()
        rut = self.rut_input.text().strip().replace(".", "").replace("-", "")
        rut = rut.upper()
        print(rut)

        for codigo in nuevos_datos.keys():
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = '''SELECT descripcion FROM epp WHERE codigo_epp = ?'''
                cursor.execute(sentencia_sql, (codigo,))
                datos = cursor.fetchall()
                descripcion = datos[0][0]
                cantidad = int(nuevos_datos[codigo])
                sentencia_sql = '''SELECT * FROM pedido_final WHERE codigo = ?'''
                cursor.execute(sentencia_sql, (codigo,))
                datos = cursor.fetchall()
                if datos:
                    try:
                        for dato in datos:
                            lista = list(dato)
                            cant_antigua = int(lista[3])
                        conexion = conectar()
                        cursor = conexion.cursor()
                        sentencia_sql = '''UPDATE pedido_final SET cantidad = ? WHERE codigo = ?'''
                        total = cant_antigua + cantidad
                        datos = (total, codigo)
                        cursor.execute(sentencia_sql, datos)
                        conexion.commit()
                        conexion.close()
                    except Error as err:
                        return 'Ha ocurrido un error ' + str(err)
                        conexion.close()
                else:
                    sentencia_sql = '''INSERT INTO pedido_final (codigo, descripcion, cantidad, rut) 
                    VALUES (?, ?, ?, ?)'''
                    cursor.execute(sentencia_sql, (codigo, descripcion, cantidad, rut))
                    conexion.commit()
                    conexion.close()
                
            except Error as err:
                print('Ha ocurrido un error: ', str(err))

        self.delete_volatile_request_data()
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
                    pass
                else:
                    self.mostrar_pedido = pedido.MostrarPedido()
                    self.mostrar_pedido.show()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))
        
        self.close()

    def delete_volatile_request_data(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "DELETE FROM pedido"
            cursor.execute(sentencia_sql)
            conexion.commit()
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ' + str(err))
        
    def check_existences(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM epp'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                self.records = True
            else:
                pass
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def clear_preview(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''DELETE FROM pedido'''
            cursor.execute(sentencia_sql)
            conexion.commit()
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))
    
    def clear_pedido_final(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''DELETE FROM pedido_final'''
            cursor.execute(sentencia_sql)
            conexion.commit()
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def resumen_pedido(self):
        self.mostrar_pedido = pedido.MostrarPedido()
        self.mostrar_pedido.show()

    def cancelar_pedido(self):
        self.clear_preview()
        self.clear_pedido_final()
        self.close()



    





    

