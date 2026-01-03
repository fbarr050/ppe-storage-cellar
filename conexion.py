import sqlite3

def conectar():
    try:
        conexion = sqlite3.connect('panol.db')
        print('Se ha conectado a la base de datos')
        return conexion
    except sqlite3.Error as err:
        print('Ha ocurrido un error', err)

def crear_tabla_epp(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''CREATE TABLE IF NOT EXISTS epp(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_epp INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    cantidad_stock INTEGER NOT NULL,
    id_categoria,
    marca
    )'''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_trabajador(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''CREATE TABLE IF NOT EXISTS trabajador(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rut TEXT,
    nombre TEXT,
    apellido_paterno TEXT,
    apellido_materno TEXT,
    talla_zapatos INT,
    talla_pantalon INT,
    talla_camisa TEXT
    )'''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_vsalida(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''
    CREATE TABLE IF NOT EXISTS vale_salida(
    id_vale_salida INTEGER PRIMARY KEY AUTOINCREMENT,
    rut TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    ubicacion TEXT NOT NULL
    )
    '''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_ventrada(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''
    CREATE TABLE IF NOT EXISTS vale_entrada(
    id_vale_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
    rut TEXT NOT NULL,
    codigo_epp INTEGER NOT NULL,
    precio REAL,
    fecha_entrada TEXT NOT NULL,
    fecha_expiracion TEXT NOT NULL,
    cantidad INTEGER NOT NULL
    )
    '''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_marca(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''
    CREATE TABLE IF NOT EXISTS marca(
        id_marca INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_marca TEXT NOT NULL,
        tipo TEXT,
        modelo TEXT        
    )
    '''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_categoria(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''
    CREATE TABLE IF NOT EXISTS categoria(
        id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT NOT NULL
    )
    '''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_pedido(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''
    CREATE TABLE IF NOT EXISTS pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo INTEGER NOT NULL,
        descripcion TEXT NOT NULL,
        cantidad INTEGER NOT NULL
    )
    '''
    cursor.execute(sentencia_sql)
    conexion.commit

def crear_tabla_pedido_final(conexion):
    cursor = conexion.cursor()
    sentencia_sql = '''
    CREATE TABLE IF NOT EXISTS pedido_final (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo INTEGER NOT NULL,
        descripcion TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        rut TEXT NOT NULL
    )
    '''
    cursor.execute(sentencia_sql)
    conexion.commit

def cerrar_conexion(conexion):
    conexion.close()
