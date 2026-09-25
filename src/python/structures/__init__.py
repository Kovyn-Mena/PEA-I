"""
Paquete de Estructuras de Datos TDA basadas en Nodos (Python)
"""
from .nodos import NodoGrupo, NodoInvestigador, NodoProducto
from .pila import Pila, AccionHistorial
from .cola import Cola, TareaIngesta
from .multilista import Multilista

__all__ = [
    "NodoGrupo", "NodoInvestigador", "NodoProducto",
    "Pila", "AccionHistorial",
    "Cola", "TareaIngesta",
    "Multilista"
]
