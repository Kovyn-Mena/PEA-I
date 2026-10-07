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
    _indice_categorias = None

    @classmethod
    def obtener_catalogo(cls) -> Dict[str, Any]:
        if cls._datos is None:
            if os.path.exists(CATALOGO_PATH):
                with open(CATALOGO_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Construir vista dual: 'families' (oficial 70 subtipos) y 'familias' (compatibilidad)
                raw_fams = data.get("families") or data.get("types") or []
                if raw_fams and "familias" not in data:
                    familias = {}
                    indice_cat = {}
                    for fam in raw_fams:
                        f_code = fam.get("code", "")
                        subtipos_dict = {}
                        for sub in fam.get("subtypes", []):
                            s_code = sub.get("code", "")
                            cats = sub.get("categories", [])
                            if cats:
                                for c in cats:
                                    c_code = c.get("code", s_code)
                                    m_class = c.get("measurement_class") or f"{f_code}-B"
                                    if m_class in ("TOP", "A", "B"):
                                        m_class = f"{f_code}-{m_class}"
                                    w_val = c.get("weight") if c.get("weight") is not None else 5
                                    gw_val = c.get("global_weight") if c.get("global_weight") is not None else int(float(w_val) * 10)
                                    entry = {
                                        "familia": f_code,
                                        "subtype_code": s_code,
                                        "subtype_name": sub.get("name", ""),
                                        "codigo_2024": c_code,
                                        "nombre": f"{sub.get('name', '')} - {c.get('label', '')}",
                                        "model_ref": sub.get("model_ref", ""),
                                        "measurement_class": m_class,
                                        "weight": w_val,
                                        "global_weight": gw_val,
                                    }
                                    subtipos_dict[c_code] = entry
                                    indice_cat[c_code.upper()] = entry
                            else:
                                entry = {
                                    "familia": f_code,
                                    "subtype_code": s_code,
                                    "subtype_name": sub.get("name", ""),
                                    "codigo_2024": s_code,
                                    "nombre": sub.get("name", ""),
                                    "model_ref": sub.get("model_ref", ""),
                                    "measurement_class": f"{f_code}-B",
                                    "weight": 5,
                                    "global_weight": 50,
                                }
                                subtipos_dict[s_code] = entry
                                indice_cat[s_code.upper()] = entry
                        familias[f_code] = {
                            "nombre": fam.get("name", f_code),
                            "subtipos": subtipos_dict,
                            "subtypes_raw": fam.get("subtypes", []),
                        }
                    data["familias"] = familias
                    cls._indice_categorias = indice_cat
                cls._datos = data
            else:
                cls._datos = {"familias": {}, "families": []}
                cls._indice_categorias = {}
        return cls._datos

    @classmethod
    def obtener_estadisticas_catalogo(cls) -> Dict[str, Any]:
        """Retorna métricas del catálogo oficial MinCiencias 2024 cargado (5 familias, 70 subtipos)."""
        cat = cls.obtener_catalogo()
        types_list = cat.get("families") or cat.get("types") or []
        resumen_familias = {}
        total_subtipos = 0
        total_categorias = 0
        for fam in types_list:
            f_code = fam.get("code", "")
            subs = fam.get("subtypes", [])
            n_subs = len(subs)
            n_cats = sum(len(s.get("categories", [])) for s in subs)
            total_subtipos += n_subs
            total_categorias += n_cats
            resumen_familias[f_code] = {
                "nombre": fam.get("name", ""),
                "subtipos": n_subs,
                "categorias": n_cats,
            }
        return {
            "version": cat.get("catalog_version", "2024"),
            "source": cat.get("source", "MinCiencias Anexo 1"),
            "total_familias": len(types_list),
            "total_subtipos": total_subtipos,
            "total_categorias": total_categorias,
            "por_familia": resumen_familias,
        }

    @classmethod
    def buscar_por_codigo(cls, codigo: str) -> Optional[Dict[str, Any]]:
        """Busca directamente una categoría o subtipo por su código oficial 2024 (ej. 'ART_A1', 'SF', 'TD_A')."""
        cls.obtener_catalogo()
        if cls._indice_categorias and codigo:
            return cls._indice_categorias.get(codigo.strip().upper())
        return None

    @classmethod
    def clasificar_producto(cls, tipo: str, categoria: str = "A1", titulo: str = "") -> Dict[str, Any]:
        """
        Mapea un producto a su tipología oficial MinCiencias 2024 (70 subtipos del Anexo 1),
        retornando familia, código 2024, clase de medición y pesos.
        """
        t = (tipo or "").strip().lower()
        cat = (categoria or "").strip().upper()
        tit = (titulo or "").strip().lower()

        # Si la categoría ya viene como un código oficial del catálogo 2024, resolver directo
        directo = cls.buscar_por_codigo(cat)
        if directo:
            return cls._resultado(
                directo["familia"],
                directo["codigo_2024"],
                directo["nombre"],
                directo["model_ref"],
                directo["measurement_class"],
                directo["weight"],
                directo["global_weight"],
            )

        # 1. GNC: Generación de Nuevo Conocimiento (10 subtipos: ART, NCE, LIB, CAP, GC, PA, PMU, VV, NRA, PMR, AAD)
        if any(k in t for k in ["articulo", "artículo", "nota cientifica", "nota científica"]):
            if "NOTA" in t.upper() or "D" == cat:
                return cls._resultado("GNC", "NCE_A1", "Nota científica en revista indexada", "2.2.1.1", "GNC-B", 10, 20)
            elif "A1" in cat:
                return cls._resultado("GNC", "ART_A1", "Artículo de investigación A1 (Q1)", "2.2.1.1", "GNC-TOP", 10, 100)
            elif "A2" in cat or cat == "A":
                return cls._resultado("GNC", "ART_A2", "Artículo de investigación A2 (Q2)", "2.2.1.1", "GNC-TOP", 6, 60)
            elif "B" in cat:
                return cls._resultado("GNC", "ART_B", "Artículo de investigación B (Q3)", "2.2.1.1", "GNC-A", 3.5, 35)
            else:
                return cls._resultado("GNC", "ART_C", "Artículo de investigación C (Q4)", "2.2.1.1", "GNC-A", 2, 20)

        elif any(k in t for k in ["libro"]) and not any(k in t for k in ["capitulo", "capítulo", "formacion", "divulgacion"]):
            if "A1" in cat:
                return cls._resultado("GNC", "LIB_A1", "Libro resultado de investigación A1", "2.2.1.2", "GNC-TOP", 10, 300)
            elif "A" in cat:
                return cls._resultado("GNC", "LIB_A", "Libro resultado de investigación A", "2.2.1.2", "GNC-TOP", 9, 270)
            return cls._resultado("GNC", "LIB_B", "Libro resultado de investigación B", "2.2.1.2", "GNC-A", 8, 240)

        elif any(k in t for k in ["capitulo", "capítulo"]):
            if "A1" in cat:
                return cls._resultado("GNC", "CAP_A1", "Capítulo en libro resultado de investigación A1", "2.2.1.3", "GNC-TOP", 10, 100)
            elif "A" in cat:
                return cls._resultado("GNC", "CAP_A", "Capítulo en libro resultado de investigación A", "2.2.1.3", "GNC-TOP", 9, 90)
            return cls._resultado("GNC", "CAP_B", "Capítulo en libro resultado de investigación B", "2.2.1.3", "GNC-A", 8, 80)

        elif any(k in t for k in ["patente", "invencion", "invención", "modelo de utilidad"]):
            if "utilidad" in t:
                return cls._resultado("GNC", "PMU_A1", "Patente de modelo de utilidad A1", "2.2.1.5.2", "GNC-TOP", 10, 100)
            return cls._resultado("GNC", "PA_A1", "Patente de invención obtenida A1", "2.2.1.5.1", "GNC-TOP", 10, 300)

        elif any(k in t for k in ["variedad vegetal", "variedad", "raza", "pecuaria"]):
            return cls._resultado("GNC", "VV_A1", "Variedad vegetal o nueva raza animal", "2.2.1.6.1", "GNC-TOP", 10, 300)

        elif any(k in t for k in ["creacion", "creación", "obra", "arquitectura"]):
            return cls._resultado("GNC", "AAD_A", "Obra de investigación-creación en artes y diseño", "2.2.1.7", "GNC-TOP", 8, 80)

        # 2. DTI: Desarrollo Tecnológico e Innovación (25 subtipos: DI, ECI, SF, PP, PI, SD, PN, CC, NRC, SE, EBT, EC, RNL, GPC, GMI, etc.)
        elif any(k in t for k in ["software", "soporte logico", "algoritmo", "computacional"]):
            return cls._resultado("DTI", "SF", "Software registrado ante la DNDA", "2.2.2.1.3", "DTI-B", 8, 35)

        elif any(k in t for k in ["planta piloto"]):
            return cls._resultado("DTI", "PP", "Planta piloto registrada", "2.2.2.1.4", "DTI-A", 4, 35)

        elif any(k in t for k in ["prototipo", "planta"]):
            return cls._resultado("DTI", "PI", "Prototipo industrial registrado", "2.2.2.1.5", "DTI-A", 4, 35)

        elif any(k in t for k in ["diseno", "diseño"]):
            return cls._resultado("DTI", "DI_A", "Diseño industrial registrado", "2.2.2.1.1", "DTI-A", 10, 35)

        elif any(k in t for k in ["esquema", "circuito"]):
            return cls._resultado("DTI", "ECI", "Esquema de circuito integrado", "2.2.2.1.2", "DTI-A", 4, 35)

        elif any(k in t for k in ["signo", "marca"]):
            return cls._resultado("DTI", "SD", "Signo distintivo registrado (SIC)", "2.2.2.1.6", "DTI-A", 4, 35)

        elif any(k in t for k in ["nutraceutico", "nutracéutico"]):
            return cls._resultado("DTI", "PN", "Producto nutracéutico con registro INVIMA", "2.2.2.1.7", "DTI-B", 6, 35)

        elif any(k in t for k in ["coleccion", "colección"]):
            return cls._resultado("DTI", "CC", "Colección científica con curaduría vigente", "2.2.2.1.8", "DTI-B", 10, 35)

        elif any(k in t for k in ["secreto", "spin-off", "spinoff", "empresa de base"]):
            return cls._resultado("DTI", "EBT_A", "Empresa de base tecnológica (Spin-off / Start-up)", "2.2.2.2.2", "DTI-A", 10, 100)

        elif any(k in t for k in ["regulacion", "regulación", "norma", "guia", "protocolo"]):
            return cls._resultado("DTI", "RNL_A", "Regulación, norma o reglamento técnico", "2.2.2.3.1", "DTI-A", 10, 70)

        elif any(k in t for k in ["informe", "innovacion", "innovación"]):
            return cls._resultado("DTI", "INF_TEC", "Informe técnico final de investigación", "2.2.2.4", "DTI-B", 5, 50)

        elif any(k in t for k in ["consultoria", "consultoría"]):
            return cls._resultado("DTI", "CT_A", "Consultoría científico-tecnológica o en arte", "2.2.2.4.1", "DTI-B", 10, 50)

        # 3. FRH: Formación de Recurso Humano en CTeI (13 subtipos: TD, TM, TP, PID, PAI, PPC, PFM, PFP, JIN, APO, etc.)
        elif any(k in t for k in ["trabajo de grado", "tesis", "grado", "direccion", "dirección"]):
            if "doctor" in tit or "doc" in tit or "doctor" in t:
                return cls._resultado("FRH", "TD_A", "Dirección de tesis de doctorado con distinción", "2.2.5.1.1", "FRH-A", 10, 100)
            elif "maestr" in tit or "master" in tit or "mag" in tit or "maestr" in t:
                return cls._resultado("FRH", "TM_A", "Dirección de trabajo de grado de maestría", "2.2.5.1.2", "FRH-B", 10, 70)
            elif "ondas" in tit or "apo" in tit or "semillero" in tit or "joven" in tit:
                return cls._resultado("FRH", "APO", "Acompañamiento al Programa Ondas / Jóvenes Investigadores", "2.2.5.5", "FRH-B", 5, 30)
            return cls._resultado("FRH", "TP_A", "Dirección de trabajo de grado de pregrado", "2.2.5.1.3", "FRH-B", 10, 40)

        elif any(k in t for k in ["jurado", "evaluador"]):
            return cls._resultado("FRH", "JUR_EVAL", "Jurado o comité evaluador de trabajo de grado", "2.2.5.1", "FRH-B", 4, 40)

        elif any(k in t for k in ["cursocorto", "curso"]):
            return cls._resultado("FRH", "CUR_COR", "Curso de corta duración en programa de formación", "2.2.5.3", "FRH-B", 3, 30)

        # 4. ASC: Apropiación Social del Conocimiento (10 subtipos: PP, CC_ASC, FCSC, FCP, etc.)
        elif any(k in t for k in ["apropiacion", "apropiación", "innovacion social", "ciudadana", "comunidad"]):
            return cls._resultado("ASC", "PP_A", "Proceso de apropiación social del conocimiento", "2.2.3.1", "ASC-A", 10, 80)

        elif any(k in t for k in ["contenido", "audiovisual", "sonoro", "multimedia"]):
            return cls._resultado("DPC", "CD_AUD", "Contenido digital o producción audiovisual CTeI", "2.2.4.1", "DPC-B", 4, 40)

        # 5. DPC: Divulgación Pública de la Ciencia (12 subtipos: EC, RC, LFD, MFD, BF, DT, NC, etc.)
        elif any(k in t for k in ["evento", "ponencia", "conferencia", "taller", "documento de trabajo", "divulgacion", "divulgación", "boletin"]):
            if "evento" in t or "ponencia" in t:
                return cls._resultado("DPC", "EC_A", "Evento científico o artístico con componente de apropiación", "2.2.4.1", "DPC-A", 6, 60)
            elif "documento" in t:
                return cls._resultado("DPC", "DT", "Documento de trabajo (Working Paper)", "2.2.4.3", "DPC-B", 5, 50)
            return cls._resultado("DPC", "LFD", "Publicación o taller de divulgación pública CTeI", "2.2.4.2", "DPC-B", 4, 40)

        # Por defecto: GNC
        return cls._resultado("GNC", "ART_B", "Producto científico general (GNC)", "2.2.1.1", "GNC-A", 3.5, 35)

    @staticmethod
    def _resultado(familia: str, codigo: str, nombre: str, ref: str, clase: str, peso: float, peso_global: int) -> Dict[str, Any]:
        return {
            "familia": familia,
            "familia_2024": familia,
            "codigo_2024": codigo,
            "nombre": nombre,
            "model_ref": ref,
            "measurement_class": clase,
            "weight": peso,
            "global_weight": peso_global
        }

# Alias de compatibilidad
Catalogo2024 = CatalogoMinCiencias2024

