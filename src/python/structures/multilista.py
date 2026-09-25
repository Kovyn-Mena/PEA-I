"""
TDA Multilista / Hipercubo de Información (Python)
Enlace Ortogonal tridimensional: Grupos <-> Investigadores <-> Productos
"""
from .nodos import NodoGrupo, NodoInvestigador, NodoProducto

class Multilista:
    def __init__(self):
        self.cabeza_grupos = None

    # -----------------------------------------------------------------
    # 1. INSERCIÓN
    # -----------------------------------------------------------------
    def insertar_grupo(self, cod: str, nom: str, clas: str, area: str,
                       lid: str, anio: int, act: bool = True) -> bool:
        if self.buscar_grupo(cod) is not None:
            return False  # Ya existe
        nuevo = NodoGrupo(cod, nom, clas, area, lid, anio, act)
        nuevo.sig_grupo = self.cabeza_grupos
        self.cabeza_grupos = nuevo
        return True

    def insertar_investigador(self, cod_grupo: str, doc: str, nom: str,
                              cat: str, form: str, act: bool = True) -> bool:
        grupo = self.buscar_grupo(cod_grupo)
        if not grupo:
            return False
        if self.buscar_investigador(doc) is not None:
            return False  # Documento ya existe
        nuevo = NodoInvestigador(doc, nom, cat, form, cod_grupo, act)
        nuevo.sig_investigador = grupo.primer_investigador
        grupo.primer_investigador = nuevo
        return True

    def insertar_producto(self, cod_grupo: str, id_inv: str, id_prod: str,
                          tipo: str, titulo: str, anio: int, cat_min: str,
                          val: bool, act: bool = True) -> bool:
        grupo = self.buscar_grupo(cod_grupo)
        inv = self.buscar_investigador(id_inv)
        if not grupo or not inv:
            return False
        if self.buscar_producto(id_prod) is not None:
            return False

        # Creación de única instancia en memoria
        nuevo = NodoProducto(id_prod, tipo, titulo, anio, cat_min, val,
                             cod_grupo, id_inv, act)

        # 1. Enlace ortogonal en la dimensión Grupo
        nuevo.sig_producto_grupo = grupo.primer_producto
        grupo.primer_producto = nuevo

        # 2. Enlace ortogonal en la dimensión Investigador
        nuevo.sig_producto_investigador = inv.primer_producto
        inv.primer_producto = nuevo

        return True

    # -----------------------------------------------------------------
    # 2. BÚSQUEDA
    # -----------------------------------------------------------------
    def buscar_grupo(self, cod: str):
        act = self.cabeza_grupos
        while act is not None:
            if act.codigo_grupo == cod:
                return act
            act = act.sig_grupo
        return None

    def buscar_investigador(self, doc: str):
        g = self.cabeza_grupos
        while g is not None:
            inv = g.primer_investigador
            while inv is not None:
                if inv.documento_id == doc:
                    return inv
                inv = inv.sig_investigador
            g = g.sig_grupo
        return None

    def buscar_producto(self, id_prod: str):
        g = self.cabeza_grupos
        while g is not None:
            p = g.primer_producto
            while p is not None:
                if p.id_producto == id_prod:
                    return p
                p = p.sig_producto_grupo
            g = g.sig_grupo
        return None

    # -----------------------------------------------------------------
    # 3. DESACTIVACIÓN (Borrado Lógico)
    # -----------------------------------------------------------------
    def desactivar_grupo(self, cod: str, estado: bool = False) -> bool:
        g = self.buscar_grupo(cod)
        if not g:
            return False
        g.activo = estado
        return True

    def desactivar_investigador(self, doc: str, estado: bool = False) -> bool:
        inv = self.buscar_investigador(doc)
        if not inv:
            return False
        inv.activo = estado
        return True

    def desactivar_producto(self, id_prod: str, estado: bool = False) -> bool:
        p = self.buscar_producto(id_prod)
        if not p:
            return False
        p.activo = estado
        return True

    # -----------------------------------------------------------------
    # 4. ELIMINACIÓN FÍSICA (Desvinculación ortogonal)
    # -----------------------------------------------------------------
    def eliminar_producto(self, id_prod: str) -> bool:
        target = self.buscar_producto(id_prod)
        if not target:
            return False

        grupo = self.buscar_grupo(target.codigo_grupo)
        inv = self.buscar_investigador(target.id_investigador)

        # 1. Desenlazar del Grupo
        if grupo:
            if grupo.primer_producto == target:
                grupo.primer_producto = target.sig_producto_grupo
            else:
                ant = grupo.primer_producto
                while ant and ant.sig_producto_grupo != target:
                    ant = ant.sig_producto_grupo
                if ant:
                    ant.sig_producto_grupo = target.sig_producto_grupo

        # 2. Desenlazar del Investigador
        if inv:
            if inv.primer_producto == target:
                inv.primer_producto = target.sig_producto_investigador
            else:
                ant = inv.primer_producto
                while ant and ant.sig_producto_investigador != target:
                    ant = ant.sig_producto_investigador
                if ant:
                    ant.sig_producto_investigador = target.sig_producto_investigador

        return True

    def eliminar_investigador(self, doc: str) -> bool:
        target = self.buscar_investigador(doc)
        if not target:
            return False

        grupo = self.buscar_grupo(target.codigo_grupo)
        if not grupo:
            return False

        # Eliminar productos autorados por este investigador
        while target.primer_producto is not None:
            self.eliminar_producto(target.primer_producto.id_producto)

        # Desenlazar del grupo
        if grupo.primer_investigador == target:
            grupo.primer_investigador = target.sig_investigador
        else:
            ant = grupo.primer_investigador
            while ant and ant.sig_investigador != target:
                ant = ant.sig_investigador
            if ant:
                ant.sig_investigador = target.sig_investigador

        return True

    def eliminar_grupo(self, cod: str) -> bool:
        target = self.buscar_grupo(cod)
        if not target:
            return False

        # Eliminar todos sus investigadores
        while target.primer_investigador is not None:
            self.eliminar_investigador(target.primer_investigador.documento_id)

        # Desenlazar de la lista de grupos
        if self.cabeza_grupos == target:
            self.cabeza_grupos = target.sig_grupo
        else:
            ant = self.cabeza_grupos
            while ant and ant.sig_grupo != target:
                ant = ant.sig_grupo
            if ant:
                ant.sig_grupo = target.sig_grupo

        return True

    # -----------------------------------------------------------------
    # 5. ESTADÍSTICAS Y VENTANA DE OBSERVACIÓN
    # -----------------------------------------------------------------
    def contar_grupos(self, solo_activos: bool = True) -> int:
        c = 0
        g = self.cabeza_grupos
        while g is not None:
            if not solo_activos or g.activo:
                c += 1
            g = g.sig_grupo
        return c

    def contar_investigadores(self, solo_activos: bool = True) -> int:
        c = 0
        g = self.cabeza_grupos
        while g is not None:
            inv = g.primer_investigador
            while inv is not None:
                if not solo_activos or (inv.activo and g.activo):
                    c += 1
                inv = inv.sig_investigador
            g = g.sig_grupo
        return c

    def contar_productos(self, solo_activos: bool = True) -> int:
        c = 0
        g = self.cabeza_grupos
        while g is not None:
            p = g.primer_producto
            while p is not None:
                if not solo_activos or (p.activo and g.activo):
                    c += 1
                p = p.sig_producto_grupo
            g = g.sig_grupo
        return c

    def contar_productos_por_ventana(self, anio_inicio: int, anio_fin: int,
                                     solo_activos: bool = True) -> int:
        c = 0
        g = self.cabeza_grupos
        while g is not None:
            p = g.primer_producto
            while p is not None:
                if (not solo_activos or (p.activo and g.activo)) and (anio_inicio <= p.anio <= anio_fin):
                    c += 1
                p = p.sig_producto_grupo
            g = g.sig_grupo
        return c

    def liberar(self):
        self.cabeza_grupos = None
