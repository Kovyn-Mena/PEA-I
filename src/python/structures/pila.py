"""
TDA Pila (Stack - LIFO) para el Historial de Acciones y Función Deshacer
Implementación pura basada en Nodos enlazados (Sin usar list.pop() o collections.deque)
"""

class AccionHistorial:
    def __init__(self, tipo_operacion: str, tipo_entidad: str, id_registro: str, detalle_previo: str = ""):
        self.tipo_operacion = tipo_operacion  # "CREAR", "MODIFICAR", "DESACTIVAR", "ELIMINAR"
        self.tipo_entidad = tipo_entidad      # "GRUPO", "INVESTIGADOR", "PRODUCTO"
        self.id_registro = id_registro
        self.detalle_previo = detalle_previo


class NodoPila:
    def __init__(self, accion: AccionHistorial, siguiente=None):
        self.accion = accion
        self.siguiente = siguiente


class Pila:
    def __init__(self):
        self._cima = None
        self._cantidad = 0

    def push(self, tipo_operacion: str, tipo_entidad: str, id_registro: str, detalle_previo: str = ""):
        """Inserta una acción en el tope de la pila (LIFO) - O(1)"""
        accion = AccionHistorial(tipo_operacion, tipo_entidad, id_registro, detalle_previo)
        nuevo = NodoPila(accion, self._cima)
        self._cima = nuevo
        self._cantidad += 1

    def pop(self):
        """Extrae la última acción registrada - O(1)"""
        if self.esta_vacia():
            return None
        temp = self._cima
        accion = temp.accion
        self._cima = self._cima.siguiente
        self._cantidad -= 1
        return accion

    def top(self):
        """Consulta el tope sin extraerlo"""
        if self.esta_vacia():
            return None
        return self._cima.accion

    def esta_vacia(self) -> bool:
        return self._cima is None

    def tamano(self) -> int:
        return self._cantidad

    def liberar(self):
        self._cima = None
        self._cantidad = 0
