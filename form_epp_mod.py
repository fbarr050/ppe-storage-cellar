from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QDialog, QHBoxLayout, QDateEdit, QCompleter
from PySide6.QtGui import QIcon

from conexion import *
from sqlite3 import Error

import cellarspark
import inventario


class ModificarEPPForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editar Artículo")

        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))
        
        # Create form widgets
        self.code_label = QLabel("Código: ")
        self.code_input = QLineEdit()
        self.desc_label = QLabel("Descripción:")
        self.desc_input = QLineEdit()

        self.quantity_label = QLabel("Cantidad:")
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000000000)
        self.category_label = QLabel("Categoría:")
        self.category_input = QComboBox()
        self.category_input.setEditable(True)  # Allow user to enter custom items
        self.category_input.setInsertPolicy(QComboBox.InsertAtTop)  # Insert new items at the top
        self.category_input.setCompleter(None)
        self.marca_label = QLabel("Marca:")
        self.marca_input = QComboBox()
        self.marca_input.setEditable(True)  # Allow user to enter custom items
        self.marca_input.setInsertPolicy(QComboBox.InsertAtTop)  # Insert new items at the top
        #self.marca_input.setCompleter(None)
        self.add_button = QPushButton("Agregar")
        self.cancel_button = QPushButton("Cancelar")

        self.category_model = QStandardItemModel()
        self.category_input.setModel(self.category_model)
        self.marca_model = QStandardItemModel()
        self.marca_input.setModel(self.marca_model)

        #self.quantity_input.setValue(self.get_last_entry_qt())
        codigo = self.get_code()
        print(codigo)
        lista = self.get_data(codigo)
        descripcion = lista[0]
        categoria = self.category_decode(lista[1])
        marca = lista[2]
        cantidad = int(lista[3])
        self.code_input.setText(str(codigo))
        self.desc_input.setText(descripcion)
        self.category_input.setCurrentText(f"{str(lista[1])}. {str(categoria)}")
        self.marca_input.setCurrentText(str(marca))
        self.quantity_input.setValue(cantidad)
        
        # Create a model for the item dropdown
        
        
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.code_label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)
        #layout.addWidget(self.price_label)
        #layout.addWidget(self.price_input)
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_input)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.marca_label)
        layout.addWidget(self.marca_input)
        #layout.addWidget(self.quantity_label)
        #layout.addWidget(self.quantity_input)


        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar")
        cancel_button = QPushButton("Cancelar")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        save_button.clicked.connect(self.add_ppe)
        cancel_button.clicked.connect(self.delete_row)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # Example: Add some initial items to the dropdown
        self.add_item(0, "1. Cabeza")
        self.add_item(0, "2. Cuerpo")
        self.add_item(0, "3. Manos")
        self.add_item(0, "4. Calzado")
        self.add_item(0, "5. Visión")
        self.add_item(0, "6. Audición")
        self.add_item(0, "7. Respiración")
        self.add_item(0, "8. Otro")

        completer = QCompleter(self.show_brands())
        self.marca_input.setCompleter(completer)

    def add_item(self, field, item):
        # Add an item to the dropdown
        if field == 0:
            standard_item = QStandardItem(item)
            self.category_model.appendRow(standard_item)
        elif field == 1:
            standard_item = QStandardItem(item)
            self.marca_model.appendRow(standard_item)
        
    def show_brands(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM marca'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                marcas = []
                for dato in datos:
                    lista = list(dato)
                    nombre_marca = lista[1]
                    self.add_item(1, nombre_marca)
                    marcas.append(lista[1])
                return marcas
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def add_ppe(self):
        #self.validate_quantity()

        codigo = int(self.code_input.text())
        descripcion = self.desc_input.text().title()
        #precio = float(self.price_input.text())
        categoria = self.category_input.currentText()
        marca = self.marca_input.currentText().upper()
        cantidad = self.quantity_input.value()

        self.add_brand(marca)
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT codigo_epp FROM epp WHERE codigo_epp = ?'''
            cursor.execute(sentencia_sql, (codigo,))
            datos = cursor.fetchall()
            for dato in datos:
                exists = dato[0]
            if exists == None:
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql = '''INSERT INTO epp (
                    codigo_epp, descripcion, cantidad_stock, id_categoria, marca
                    ) VALUES (?, ?, ?, ?, ?)'''
                    datos = (codigo, descripcion, cantidad, categoria[0], marca)
                    cursor.execute(sentencia_sql, datos)
                    conexion.commit()
                    conexion.close()
                    self.show_inventory_view()
                    self.close()
                except Error as err:
                    print('Ha ocurrido un error ' + str(err))
            else:
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql='''UPDATE epp SET descripcion = ?, cantidad_stock = ?, id_categoria = ?, marca = ?
                    WHERE codigo_epp = ?'''
                    cursor.execute(sentencia_sql, (descripcion, cantidad, categoria[0], marca, codigo))
                    conexion.commit()
                    conexion.close()
                    self.show_inventory_view()
                    self.close()
                except Error as err:
                    print('Ha ocurrido un error: ', str(err))
        except Error as err:
            print(str('Ha ocurrido un error: ', str(err)))

        for window in cellarspark.open_windows:
            print(str(window))
            window.update()

    def add_brand(self, marca):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM marca WHERE nombre_marca = ?'''
            cursor.execute(sentencia_sql, (marca,))
            datos = cursor.fetchall()
            if datos:
                pass
            else:
                sentencia_sql = '''INSERT INTO marca (nombre_marca) VALUES (?)'''
                cursor.execute(sentencia_sql, (marca,))
                conexion.commit()
            conexion.close()
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

    def get_last_entry_qt(self):
        
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT id_vale_entrada FROM vale_entrada'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            for dato in datos:
                lista = list(dato)
            idult_ingreso = max(lista)
            sentencia_sql = '''SELECT cantidad FROM vale_entrada WHERE id_vale_entrada = ?'''
            cursor.execute(sentencia_sql, (idult_ingreso,))
            ult_ingreso = cursor.fetchall()
            return int(ult_ingreso[0][0])
        except Error as err:
            print('Ha ocurrido un error: ', str(err))

        
    def get_code(self):
        f = open("ppe-storage-cellar/code.txt", "r")
        code = int(f.read())
        return code
        

    def delete_row(self):
        self.close()

    def get_data(self, code):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT descripcion, id_categoria, marca, cantidad_stock FROM epp WHERE codigo_epp = ?"
            cursor.execute(sentencia_sql, (code,))
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                return lista
        except Error as err:
            print("Ha ocurrido un error: ", str(err))

    def category_decode(self, category):
        if category == '1':
            return "Cabeza"
        elif category == '2':
            return "Cuerpo"
        elif category == '3':
            return "Manos"
        elif category == '4':
            return "Calzado"
        elif category == '5':
            return "Visión"
        elif category == '6':
            return "Audición"
        elif category == '7':
            return "Respiración"
        elif category == '8':
            return "Otro"

    def show_inventory_view(self):
        self.inventory_view = inventario.InventoryView()
        self.inventory_view.show()            