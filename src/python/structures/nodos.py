"""
Definición de Entidades y Nodos para el Hipercubo de Información (Python)
Modelado mediante Multilista jerárquica ortogonal basada en referencias
"""

class NodoProducto:
    """Nodo correspondiente a la Dimensión 3: Productos de Investigación"""
    def __init__(self, id_producto: str, tipo: str, titulo: str, anio: int,
                 categoria_minciencias: str, validado: bool, codigo_grupo: str,
                 id_investigador: str, activo: bool = True):
        self.id_producto = id_producto
        self.tipo = tipo                  # Articulo, Libro, Capitulo, Software, Patente
        self.titulo = titulo
        self.anio = anio
        self.categoria_minciencias = categoria_minciencias
        self.validado = validado          # True / False
        self.codigo_grupo = codigo_grupo
        self.id_investigador = id_investigador
        self.activo = activo              # True: activo, False: desactivado

        # Punteros ortogonales (Hipercubo multidimensional)
        self.sig_producto_grupo = None        # Siguiente producto en el mismo Grupo
        self.sig_producto_investigador = None # Siguiente producto del mismo Investigador


class NodoInvestigador:
    """Nodo correspondiente a la Dimensión 2: Investigadores"""
    def __init__(self, documento_id: str, nombre_completo: str, categoria: str,
                 formacion_academica: str, codigo_grupo: str, activo: bool = True):
        self.documento_id = documento_id
        self.nombre_completo = nombre_completo
        self.categoria = categoria        # Senior, Asociado, Junior, Sin Categoria
        self.formacion_academica = formacion_academica
        self.codigo_grupo = codigo_grupo
        self.activo = activo

        self.sig_investigador = None      # Siguiente investigador en el grupo
        self.primer_producto = None       # Sublista de productos de este autor


class NodoGrupo:
    """Nodo correspondiente a la Dimensión 1: Grupos de Investigación"""
    def __init__(self, codigo_grupo: str, nombre: str, clasificacion: str,
                 area_conocimiento: str, lider: str, anio_creacion: int, activo: bool = True):
        self.codigo_grupo = codigo_grupo
        self.nombre = nombre
        self.clasificacion = clasificacion  # A1, A, B, C, Reconocido
        self.area_conocimiento = area_conocimiento
        self.lider = lider
        self.anio_creacion = anio_creacion
        self.activo = activo

        self.sig_grupo = None               # Siguiente grupo en la lista principal
        self.primer_investigador = None     # Sublista de investigadores adscritos
        self.primer_producto = None         # Sublista de todos los productos del grupo
