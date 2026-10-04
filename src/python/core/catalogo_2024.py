"""
=====================================================================
PEA-i: MOTOR DE RESOLUCIÓN Y CLASIFICACIÓN MINCIENCIAS 2024
Universidad Popular del Cesar — Estructura de Datos
Docente: Ing. Adith Bismarck Pérez Orozco
=====================================================================
Implementa la especificación formal del Modelo de Medición 2024
(Convocatoria Nacional 957 / Anexo 1):
  • 5 Familias Oficiales: GNC, DTI, ASC, DPC, FRH.
  • Mapeo dinámico desde registros de GrupLAC y CvLAC a códigos 2024.
  • Cálculo de Pesos Relativos (weight) y Pesos Globales (global_weight).
  • Determinación de Clases de Medición (measurement_class).
=====================================================================
"""

import os
import json
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
CATALOGO_PATH = os.path.join(PROJECT_ROOT, "data", "catalogo_minciencias_2024.json")

class CatalogoMinCiencias2024:
    _instancia = None
    _datos = None

    @classmethod
    def obtener_catalogo(cls) -> Dict[str, Any]:
        if cls._datos is None:
            if os.path.exists(CATALOGO_PATH):
                with open(CATALOGO_PATH, "r", encoding="utf-8") as f:
                    cls._datos = json.load(f)
            else:
                cls._datos = {"familias": {}}
        return cls._datos

    @classmethod
    def clasificar_producto(cls, tipo: str, categoria: str = "A1", titulo: str = "") -> Dict[str, Any]:
        """
        Mapea un producto a su tipología oficial MinCiencias 2024,
        retornando familia, código 2024, clase de medición y pesos.
        """
        t = tipo.strip().lower()
        cat = categoria.strip().upper()
        tit = titulo.strip().lower()

        # 1. GNC: Generación de Nuevo Conocimiento
        if any(k in t for k in ["articulo", "artículo"]):
            if "A1" in cat:
                return cls._resultado("GNC", "ART_A1", "Artículo indexado A1 (Q1)", "2.2.1.1.1", "GNC-A", 10, 100)
            elif "A2" in cat or cat == "A":
                return cls._resultado("GNC", "ART_A2", "Artículo indexado A2 (Q2)", "2.2.1.1.2", "GNC-A", 8, 80)
            elif "B" in cat:
                return cls._resultado("GNC", "ART_B", "Artículo indexado B (Q3)", "2.2.1.1.3", "GNC-B", 6, 60)
            else:
                return cls._resultado("GNC", "ART_C", "Artículo indexado C (Q4)", "2.2.1.1.4", "GNC-B", 4, 40)

        elif any(k in t for k in ["libro"]):
            if "A" in cat:
                return cls._resultado("GNC", "LIB_A", "Libro de investigación A", "2.2.1.2.1", "GNC-A", 10, 100)
            return cls._resultado("GNC", "LIB_B", "Libro de investigación B", "2.2.1.2.2", "GNC-B", 7, 70)

        elif any(k in t for k in ["capitulo", "capítulo"]):
            if "A" in cat:
                return cls._resultado("GNC", "CAP_LIB_A", "Capítulo de libro A", "2.2.1.3.1", "GNC-A", 5, 50)
            return cls._resultado("GNC", "CAP_LIB_B", "Capítulo de libro B", "2.2.1.3.2", "GNC-B", 3, 30)

        elif any(k in t for k in ["patente", "invencion", "invención"]):
            return cls._resultado("GNC", "PAT_INV", "Patente de invención", "2.2.1.4.1", "GNC-A", 10, 100)

        # 2. DTI: Desarrollo Tecnológico e Innovación
        elif any(k in t for k in ["software", "soporte logico", "algoritmo"]):
            return cls._resultado("DTI", "SOFT_REG", "Software con soporte lógico registrado", "2.2.2.1.1", "DTI-A", 9, 90)

        elif any(k in t for k in ["prototipo", "planta"]):
            return cls._resultado("DTI", "PROT_IND", "Prototipo industrial o planta piloto", "2.2.2.2.1", "DTI-A", 8, 80)

        elif any(k in t for k in ["diseno", "diseño"]):
            return cls._resultado("DTI", "DIS_IND", "Diseño industrial registrado", "2.2.2.3.1", "DTI-A", 8, 80)

        elif any(k in t for k in ["regulacion", "regulación", "norma"]):
            return cls._resultado("DTI", "REG_NORM", "Norma o regulación técnica", "2.2.2.4.1", "DTI-A", 7, 70)

        elif any(k in t for k in ["informe"]):
            return cls._resultado("DTI", "INF_TEC", "Informe técnico final de investigación", "2.2.2.5.1", "DTI-B", 5, 50)

        elif any(k in t for k in ["consultoria", "consultoría"]):
            return cls._resultado("DTI", "CONS_TEC", "Consultoría científico-tecnológica", "2.2.2.6.1", "DTI-B", 5, 50)

        # 3. FRH: Formación de Recurso Humano
        elif any(k in t for k in ["trabajo de grado", "tesis", "grado"]):
            if "doctor" in tit or "doc" in tit:
                return cls._resultado("FRH", "TES_DOC", "Tesis de Doctorado sustentada", "2.2.4.1.1", "FRH-A", 10, 100)
            elif "maestr" in tit or "master" in tit or "mag" in tit:
                return cls._resultado("FRH", "TGM", "Trabajo de Grado de Maestría sustentado", "2.2.4.2.1", "FRH-A", 7, 70)
            elif "ondas" in tit or "apo" in tit:
                return cls._resultado("FRH", "APO", "Acompañamiento Programa Ondas", "2.2.4.7.1", "FRH-B", 5, 30)
            return cls._resultado("FRH", "TGP", "Trabajo de Grado de Pregrado sustentado", "2.2.4.3.1", "FRH-B", 4, 40)

        elif any(k in t for k in ["jurado", "evaluador"]):
            return cls._resultado("FRH", "JUR_EVAL", "Jurado o comité evaluador de tesis", "2.2.4.4.1", "FRH-B", 4, 40)

        elif any(k in t for k in ["cursocorto", "curso"]):
            return cls._resultado("FRH", "CUR_COR", "Curso de corta duración dictado", "2.2.4.5.1", "FRH-B", 3, 30)

        # 4. ASC: Apropiación Social del Conocimiento
        elif any(k in t for k in ["apropiacion", "apropiación", "innovacion social"]):
            return cls._resultado("ASC", "PROC_ASC", "Proceso de apropiación social CTeI", "2.2.3.1.1", "ASC-A", 8, 80)

        elif any(k in t for k in ["contenido", "audiovisual"]):
            return cls._resultado("ASC", "CONT_DIG", "Contenido digital o audiovisual", "2.2.3.2.1", "ASC-B", 4, 40)

        # 5. DPC: Divulgación Pública de la Ciencia
        elif any(k in t for k in ["evento", "ponencia", "conferencia", "taller", "documento de trabajo", "divulgacion", "divulgación"]):
            if "evento" in t or "ponencia" in t:
                return cls._resultado("DPC", "EVT_INT", "Ponencia en evento científico", "2.2.5.1.1", "DPC-A", 6, 60)
            elif "documento" in t:
                return cls._resultado("DPC", "DOC_TRAB", "Documento de trabajo institucional", "2.2.5.3.1", "DPC-B", 5, 50)
            return cls._resultado("DPC", "TALLER_CTEI", "Taller especializado de difusión", "2.2.5.2.1", "DPC-B", 4, 40)

        # Por defecto: GNC
        return cls._resultado("GNC", "ART_B", "Producto científico general", "2.2.1.1.3", "GNC-B", 6, 60)

    @staticmethod
    def _resultado(familia: str, codigo: str, nombre: str, ref: str, clase: str, peso: int, peso_global: int) -> Dict[str, Any]:
        return {
            "familia": familia,
            "codigo_2024": codigo,
            "nombre": nombre,
            "model_ref": ref,
            "measurement_class": clase,
            "weight": peso,
            "global_weight": peso_global
        }

# Alias de compatibilidad
Catalogo2024 = CatalogoMinCiencias2024

