from conexion import *
import sys 
import os, shutil
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QWidget, QPushButton, QMenu, QMenuBar, QMessageBox
from PySide6.QtGui import QIcon


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize


import form_entrega
import inventario
import form_entrada
import consumo
import pedido
import entradas
import trabajadores

from sqlite3 import Error


open_windows = []

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CellarSpark | Inicio")

        self.setWindowIcon(QIcon("ppe-storage-cellar/img/cellar-spark-logo.png"))

        self.setMinimumWidth(400)
        self.setMinimumHeight(250)
        
        self.con = conectar()
        crear_tabla_epp(self.con)
        crear_tabla_trabajador(self.con)
        crear_tabla_vsalida(self.con)
        crear_tabla_ventrada(self.con)
        crear_tabla_marca(self.con)
        crear_tabla_categoria(self.con)
        crear_tabla_pedido(self.con)
        crear_tabla_pedido_final(self.con)

        # BOTONES
        self.request_button = QPushButton("Registrar Entrega/Salidas")
        self.request_button.clicked.connect(self.show_request_form)
        self.view_inventory_button = QPushButton("Ver Inventario")
        self.view_inventory_button.clicked.connect(self.show_inventory_view)
        self.add_article_button = QPushButton("Registrar Nuevos Artículos/Entradas")
        self.add_article_button.clicked.connect(self.show_new_article_form)
        self.view_consumption_button = QPushButton("Ver Historial de Salidas")
        self.view_consumption_button.clicked.connect(self.show_consumption_view)
        self.view_entries_button = QPushButton("Ver Historial de Entradas")
        self.view_entries_button.clicked.connect(self.show_entries_view)
        self.view_employees_button = QPushButton("Ver Datos de los Usuarios")
        self.view_employees_button.clicked.connect(self.show_employees_view)        
        
        # Create layout and add button
        layout = QVBoxLayout()
        layout.addWidget(self.request_button)
        layout.addWidget(self.view_inventory_button)
        layout.addWidget(self.add_article_button)
        layout.addWidget(self.view_consumption_button)
        layout.addWidget(self.view_entries_button)
        layout.addWidget(self.view_employees_button)
        
        # Set central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Instance variable to hold request form
        self.request_form = None
        self.inventory_view = None
        self.new_article_form = None
        self.consumption_view = None
        self.entries_view = None
        self.employees_view = None

        open_windows.append(self)

        self.refresh_all_windows()


        # Create a menu bar
        menubar = self.menuBar()
        options_menu = menubar.addMenu('Opciones')

        # Add actions to the menu
        option1_action = QAction('Borrar historial de consumo', self)
        option1_action.triggered.connect(self.handle_option1)
        options_menu.addAction(option1_action)

        option2_action = QAction('Borrar historial de entradas', self)
        option2_action.triggered.connect(self.handle_option2)
        options_menu.addAction(option2_action)

        option3_action = QAction('Borrar todos los registros', self)
        option3_action.triggered.connect(self.handle_option3)
        options_menu.addAction(option3_action)

        self.db_path = "ppe-storage-cellar\\panol.db"
    #def handle_option_change(self, index):
    #    # Handle the combo box index change if needed
    #    pass

    def handle_option1(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Eliminar registros")
        dlg.setText("¿Está seguro de que desea eliminar el historial de consumo?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            print("Yes!")
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = "DROP TABLE IF EXISTS vale_salida"
                cursor.execute(sentencia_sql)
                conexion.commit()
                conexion.close()
            except Error as err:
                print("Ha ocurrido un error: ", str(err))
        else:
            print("No!")

    def handle_option2(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Eliminar registros")
        dlg.setText("¿Está seguro de que desea eliminar el historial de entradas?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            print("Yes!")
            try:
                conexion = conectar()
                cursor = conexion.cursor()
                sentencia_sql = "DROP TABLE IF EXISTS vale_entrada"
                cursor.execute(sentencia_sql)
                conexion.commit()
                conexion.close()
            except Error as err:
                print("Ha ocurrido un error: ", str(err))
        else:
            print("No!")

    def handle_option3(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Eliminar registros")
        dlg.setText("¿Está seguro de que desea eliminar todos los datos?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            print("Yes!")
            cerrar_conexion(self.con)

            # Try to delete the database file
            try:
                os.remove(self.db_path)
                QMessageBox.information(self, 'Success', 'Todos los registros han sido eliminados.')
                self.con = conectar()
                crear_tabla_epp(self.con)
                crear_tabla_trabajador(self.con)
                crear_tabla_vsalida(self.con)
                crear_tabla_ventrada(self.con)
                crear_tabla_marca(self.con)
                crear_tabla_categoria(self.con)
                crear_tabla_pedido(self.con)
                crear_tabla_pedido_final(self.con)
                
                folder = 'ppe-storage-cellar/receipts'
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error eliminando la base de datos: {e}')

            
            
        else:
            print("No!")

    def show_request_form(self):
        self.request_form = form_entrega.RequestForm()
        self.request_form.setWindowTitle("Formulario de Registro de Entrega EPP")
        self.request_form.show()

    def show_inventory_view(self):
        self.inventory_view = inventario.InventoryView()
        self.inventory_view.show()

    def show_new_article_form(self):
        self.new_article_form = form_entrada.NewArticleForm()
        self.new_article_form.show()

    def show_consumption_view(self):
        self.consumption_view = consumo.ConsumptionView()
        self.consumption_view.show()

    def show_entries_view(self):
        self.entries_view = entradas.EntriesView()
        self.entries_view.show()

    def show_employees_view(self):
        self.employees_view = trabajadores.EmployeesView()
        self.employees_view.show()

    def refresh_all_windows(self):

        for window in open_windows:
            window.update()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()