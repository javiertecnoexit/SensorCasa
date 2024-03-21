
import pymysql
import mysql.connector


class Database:
    def __init__(self, host, usuario, contraseña, base_datos):
        self.host = host
        self.usuario = usuario
        self.contraseña = contraseña
        self.base_datos = base_datos
        self.conexion = None

    def conectar(self):
        try:
            self.conexion = pymysql.connect(
                host=self.host,
                user=self.usuario,
                password=self.contraseña,
                database=self.base_datos,
            )
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")

    def desconectar(self):
        if self.conexion is not None:
            self.conexion.close()

    def ejecutar_consulta(self, sql):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")

