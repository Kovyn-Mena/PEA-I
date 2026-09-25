"""
TDA Cola (Queue - FIFO) para la Ingesta de Datos (Scraping, PDF, CSV)
Implementación pura basada en Nodos enlazados (Sin usar list ni collections.deque)
"""

class TareaIngesta:
    def __init__(self, tipo_fuente: str, ruta_o_url: str, descripcion: str = ""):
        self.tipo_fuente = tipo_fuente  # "URL_GRUPLAC", "URL_CVLAC", "ARCHIVO_PDF", "ARCHIVO_CSV"
        self.ruta_o_url = ruta_o_url
        self.descripcion = descripcion


class NodoCola:
    def __init__(self, tarea: TareaIngesta, siguiente=None):
        self.tarea = tarea
        self.siguiente = siguiente


class Cola:
    def __init__(self):
        self._primero = None
        self._ultimo = None
        self._cantidad = 0

    def encolar(self, tipo_fuente: str, ruta_o_url: str, descripcion: str = ""):
        """Inserta al final de la cola (FIFO) - O(1)"""
        tarea = TareaIngesta(tipo_fuente, ruta_o_url, descripcion)
        nuevo = NodoCola(tarea)
        if self.esta_vacia():
            self._primero = self._ultimo = nuevo
        else:
            self._ultimo.siguiente = nuevo
            self._ultimo = nuevo
        self._cantidad += 1

    def desencolar(self):
        """Extrae el elemento del frente de la cola - O(1)"""
        if self.esta_vacia():
            return None
        temp = self._primero
        tarea = temp.tarea
        self._primero = self._primero.siguiente
        if self._primero is None:
            self._ultimo = None
        self._cantidad -= 1
        return tarea

    def frente(self):
        """Consulta el elemento del frente sin extraerlo"""
        if self.esta_vacia():
            return None
        return self._primero.tarea

    def esta_vacia(self) -> bool:
        return self._primero is None

    def tamano(self) -> int:
        return self._cantidad

    def liberar(self):
        self._primero = None
        self._ultimo = None
        self._cantidad = 0
