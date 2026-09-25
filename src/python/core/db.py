"""
Gestor de Persistencia SQLite (Python) - PEA-i
Sincronización bidireccional entre la base de datos SQLite y la Multilista en RAM
"""
import sqlite3
import os
import sys

# Asegurar importación del paquete structures
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from python.structures.multilista import Multilista

class GestorPersistencia:
    @staticmethod
    def cargar_desde_bd(multi: Multilista, ruta_bd: str = "data/pea_investigacion.db") -> bool:
        """Carga Grupos, Investigadores y Productos desde SQLite hacia la Multilista"""
        if not os.path.exists(ruta_bd):
            print(f"[!] No existe el archivo de base de datos: {ruta_bd}")
            return False

        try:
            conn = sqlite3.connect(ruta_bd)
            cursor = conn.cursor()

            # 1. Cargar Grupos
            cursor.execute("SELECT codigo_grupo, nombre, clasificacion, area_conocimiento, lider, anio_creacion, activo FROM Grupos;")
            for row in cursor.fetchall():
                cod, nom, clas, area, lid, anio, act = row
                multi.insertar_grupo(cod, nom, clas, area, lid, anio, bool(act))

            # 2. Cargar Investigadores
            cursor.execute("SELECT documento_id, nombre_completo, categoria, formacion_academica, codigo_grupo, activo FROM Investigadores;")
            for row in cursor.fetchall():
                doc, nom, cat, form, cod_g, act = row
                multi.insertar_investigador(cod_g, doc, nom, cat, form, bool(act))

            # 3. Cargar Productos (Ortogonal)
            cursor.execute("SELECT id_producto, tipo, titulo, anio, categoria_minciencias, validado, codigo_grupo, id_investigador, activo FROM Productos;")
            for row in cursor.fetchall():
                id_p, tipo, tit, anio, cat_m, val, cod_g, id_inv, act = row
                multi.insertar_producto(cod_g, id_inv, id_p, tipo, tit, anio, cat_m, bool(val), bool(act))

            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"[ERROR Persistencia Python] {e}")
            return False

    @staticmethod
    def guardar_en_bd(multi: Multilista, ruta_bd: str = "data/pea_investigacion.db") -> bool:
        """Sincroniza el estado de la Multilista en SQLite usando una transacción atómica"""
        try:
            conn = sqlite3.connect(ruta_bd)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("BEGIN TRANSACTION;")

            # Limpiar tablas para sobreescribir con el estado actual en memoria
            cursor.execute("DELETE FROM Productos;")
            cursor.execute("DELETE FROM Investigadores;")
            cursor.execute("DELETE FROM Grupos;")

            sql_grupo = "INSERT INTO Grupos VALUES (?, ?, ?, ?, ?, ?, ?);"
            sql_inv = "INSERT INTO Investigadores VALUES (?, ?, ?, ?, ?, ?);"
            sql_prod = "INSERT INTO Productos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"

            g = multi.cabeza_grupos
            while g is not None:
                cursor.execute(sql_grupo, (
                    g.codigo_grupo, g.nombre, g.clasificacion,
                    g.area_conocimiento, g.lider, g.anio_creacion,
                    1 if g.activo else 0
                ))

                # Investigadores del grupo
                inv = g.primer_investigador
                while inv is not None:
                    cursor.execute(sql_inv, (
                        inv.documento_id, inv.nombre_completo, inv.categoria,
                        inv.formacion_academica, inv.codigo_grupo,
                        1 if inv.activo else 0
                    ))
                    inv = inv.sig_investigador

                # Productos del grupo
                p = g.primer_producto
                while p is not None:
                    cursor.execute(sql_prod, (
                        p.id_producto, p.tipo, p.titulo, p.anio,
                        p.categoria_minciencias, 1 if p.validado else 0,
                        p.codigo_grupo, p.id_investigador,
                        1 if p.activo else 0
                    ))
                    p = p.sig_producto_grupo

                g = g.sig_grupo

            conn.commit()
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"[ERROR Guardar SQLite Python] {e}")
            return False
