from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtGui import QIcon

from sqlite3 import Error
from conexion import *

from cellarspark import *
import form_epp_mod

class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario | Artículos disponibles")
        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))

        self.setMinimumWidth(870)
        self.setMinimumHeight(480)
        
        title_label = QLabel("Inventario", self)

        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Number of columns
        self.table.setHorizontalHeaderLabels(["Descripción", "Código", "Stock", "Categoría", "Marca", "", ""])  # Column headers
        
        self.show_ppe_inventory()
        
        #self.table.resizeColumnsToContents()

        
        # Set minimum width for the table
        #self.table.setMinimumWidth(self.table.horizontalHeader().length() + self.table.verticalScrollBar().width())

        

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.table)
        layout.setAlignment(Qt.AlignCenter)
        title_label.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        open_windows.append(self)

        self.editar_epp = None

        
    def add_inventory_item(self, desc, code, stock, category, brand):
        # Add an item to the inventory table
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(desc))
        self.table.setItem(row, 1, QTableWidgetItem(str(code)))
        self.table.setItem(row, 2, QTableWidgetItem(str(stock)))
        self.table.setItem(row, 3, QTableWidgetItem(category))
        self.table.setItem(row, 4, QTableWidgetItem(brand))

    def show_ppe_inventory(self):
        try:
            self.table.setRowCount(0)
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = '''SELECT * FROM epp'''
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                for dato in datos:
                    lista = list(dato)
                    self.add_inventory_item(lista[2], lista[1], lista[3], self.category_decode(lista[4]), lista[5])


                self.table.setColumnWidth(0, 260) 
                self.table.setColumnWidth(1, 100) 
                self.table.setColumnWidth(2, 100)
                self.table.setColumnWidth(3, 100)
                self.table.setColumnWidth(4, 80)
                self.table.setColumnWidth(5, 80)
                self.table.setColumnWidth(6, 80)

                column_index_with_button = 5  # Replace 2 with the actual index of the column where you want to add buttons.
                for row in range(self.table.rowCount()):
                    update_button = QPushButton("Editar")
                    update_button.clicked.connect(self.on_button_clicked)  # Connect the clicked signal to a slot
                    self.table.setCellWidget(row, column_index_with_button, update_button)

                column_index_with_del_button = 6  # Replace 2 with the actual index of the column where you want to add buttons.
                for row in range(self.table.rowCount()):
                    delete_button = QPushButton("Eliminar")
                    delete_button.clicked.connect(self.on_del_button_clicked)  # Connect the clicked signal to a slot
                    self.table.setCellWidget(row, column_index_with_del_button, delete_button)
            
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

    def on_button_clicked(self):
        button = self.sender()  # Get the button that was clicked
        index = self.table.indexAt(button.pos())  # Get the index of the clicked button
        if index.isValid():
            row = index.row()
            column = index.column()

            codes_list = self.get_codes_list()
            code = codes_list[row]
            f = open("ppe-storage-cellar/code.txt", "w")
            f.write(str(code))
            f.close()
            self.editar_trabajador = form_epp_mod.ModificarEPPForm()
            self.editar_trabajador.show()
            self.close()


    def get_codes_list(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            sentencia_sql = "SELECT codigo_epp FROM epp"
            cursor.execute(sentencia_sql)
            datos = cursor.fetchall()
            if datos:
                code_list = []
                for dato in datos:
                    lista = list(dato)
                    code = lista[0]
                    code_list.append(code)
                return code_list
        except Error as err:
            print("Ha ocurrido un error: ", str(err))    

    def on_del_button_clicked(self):
        button = self.sender()  # Get the button that was clicked
        index = self.table.indexAt(button.pos())  # Get the index of the clicked button
        if index.isValid():
            row = index.row()
            column = index.column()

            code_list = self.get_codes_list()
            codigo = code_list[row]
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Eliminar artículo")
            dlg.setText("¿Está seguro de que desea eliminar este artículo?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Warning)
            button = dlg.exec()

            if button == QMessageBox.Yes:
                print("Yes!")
                try:
                    conexion = conectar()
                    cursor = conexion.cursor()
                    sentencia_sql = "DELETE FROM epp WHERE codigo_epp = ?"
                    cursor.execute(sentencia_sql, (codigo,))
                    conexion.commit()
                    conexion.close()
                    self.show_ppe_inventory()
                except Error as err:
                    print("Ha ocurrido un error: ", str(err))
            else:
                print("No!")
