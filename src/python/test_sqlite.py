#!/usr/bin/env python3
"""
Test de conectividad Python <-> SQLite (Contrato Fase 0)
"""
import sqlite3
import os

def test_python_sqlite():
    print("========================================")
    print("[Python] Test de Conectividad SQLite3")
    print("========================================")
    
    db_path = os.path.join("data", "pea_investigacion.db")
    if not os.path.exists(db_path):
        print(f"[ERROR Python] No se encontró el archivo: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"[OK Python] Base de datos conectada exitosamente: {db_path}\n")
    
    # 1. Conteo de Grupos
    cursor.execute("SELECT COUNT(*) FROM Grupos WHERE activo = 1;")
    num_grupos = cursor.fetchone()[0]
    
    # 2. Conteo de Investigadores
    cursor.execute("SELECT COUNT(*) FROM Investigadores WHERE activo = 1;")
    num_inv = cursor.fetchone()[0]
    
    # 3. Conteo de Productos
    cursor.execute("SELECT COUNT(*) FROM Productos WHERE activo = 1;")
    num_prod = cursor.fetchone()[0]
    
    print(f"• Total Grupos Activos:         {num_grupos}")
    print(f"• Total Investigadores Activos: {num_inv}")
    print(f"• Total Productos Activos:      {num_prod}")
    
    print("\n--- Investigadores y su Grupo ---")
    query = """
    SELECT i.nombre_completo, i.categoria, g.nombre 
    FROM Investigadores i
    JOIN Grupos g ON i.codigo_grupo = g.codigo_grupo
    WHERE i.activo = 1;
    """
    cursor.execute(query)
    for row in cursor.fetchall():
        print(f"• {row[0]} ({row[1]}) -> {row[2]}")
        
    conn.close()
    print("\n[OK Python] Prueba de persistencia finalizada exitosamente.")
    return True

if __name__ == "__main__":
    test_python_sqlite()
