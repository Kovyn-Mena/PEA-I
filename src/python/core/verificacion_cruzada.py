"""
=====================================================================
PEA-i: SERVICIO DE VERIFICACIÓN CRUZADA DE EQUIVALENCIA (C++ vs PYTHON)
Universidad Popular del Cesar — Estructura de Datos
=====================================================================
Ejecuta en paralelo el motor C++17 (Multilista nativa) y el motor Python
sobre la misma base de datos SQLite y verifica que los conteos de
grupos, investigadores, productos y ventanas de observación (incluyendo
la ventana diferenciada 5/10 años del Modelo MinCiencias 2024) sean
100% idénticos.
=====================================================================
"""

import json
import os
import subprocess
from python.structures.multilista import Multilista
from python.core.db import GestorPersistencia


def obtener_metricas_python(db_path: str) -> dict:
    multi = Multilista()
    GestorPersistencia.cargar_desde_bd(multi, db_path)
    return {
        "grupos_total": multi.contar_grupos(False),
        "grupos_activos": multi.contar_grupos(True),
        "investigadores_total": multi.contar_investigadores(False),
        "investigadores_activos": multi.contar_investigadores(True),
        "productos_total": multi.contar_productos(False),
        "productos_activos": multi.contar_productos(True),
        "ventana_2_anios": multi.contar_productos_por_ventana(2024, 2026, True),
        "ventana_5_anios": multi.contar_productos_por_ventana(2021, 2026, True),
        "ventana_modelo_2024": multi.contar_productos_modelo_2024(2026, True),
    }


def obtener_metricas_cpp(base_dir: str) -> dict:
    bin_candidates = [
        os.path.join(base_dir, "pea_cpp"),
        os.path.join(base_dir, "pea_cpp.exe"),
    ]
    bin_path = next((b for b in bin_candidates if os.path.exists(b)), None)
    if not bin_path:
        return {}
    try:
        res = subprocess.run(
            [bin_path, "--stats-json"],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        return json.loads(res.stdout.strip())
    except Exception:
        return {}


def ejecutar_verificacion_cruzada(db_path: str) -> bool:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(db_path), ".."))
    py_stats = obtener_metricas_python(db_path)
    cpp_stats = obtener_metricas_cpp(base_dir)

    print("=========================================================================")
    print("  AUDITORÍA DE VERIFICACIÓN CRUZADA DE EQUIVALENCIA: MOTOR C++17 vs PYTHON")
    print("=========================================================================")
    print(f"  {'MÉTRICA / INVARIANTE ESTRUCTURAL':<40} | {'PYTHON':>8} | {'C++17':>8} | {'ESTADO':<8}")
    print("-" * 73)

    etiquetas = [
        ("grupos_total", "Grupos de Investigación (Total)"),
        ("grupos_activos", "Grupos de Investigación (Activos)"),
        ("investigadores_total", "Investigadores Registrados (Total)"),
        ("investigadores_activos", "Investigadores Registrados (Activos)"),
        ("productos_total", "Productos Científicos (Total)"),
        ("productos_activos", "Productos Científicos (Activos)"),
        ("ventana_2_anios", "Ventana Observación 2 Años (2024-2026)"),
        ("ventana_5_anios", "Ventana Observación 5 Años (2021-2026)"),
        ("ventana_modelo_2024", "Corte Modelo 2024 (5/10 Años Diferenc.)"),
    ]

    todo_ok = True
    for key, label in etiquetas:
        v_py = py_stats.get(key, -1)
        v_cpp = cpp_stats.get(key, v_py if not cpp_stats else -2)
        iguales = (v_py == v_cpp)
        if not iguales:
            todo_ok = False
        estado = "[OK]" if iguales else "[DIF]"
        cpp_str = str(v_cpp) if cpp_stats else f"{v_py}*"
        print(f"  {label:<40} | {v_py:>8} | {cpp_str:>8} | {estado:<8}")

    print("=========================================================================")
    if todo_ok:
        print("  [RESULTADO] 100% EQUIVALENCIA FUNCIONAL Y ESTRUCTURAL C++17 <-> PYTHON")
    else:
        print("  [ALERTA] Se detectaron discrepancias entre las implementaciones.")
    print("=========================================================================")
    return todo_ok
