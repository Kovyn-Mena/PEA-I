"""
Consola Autónoma de PEA-i (Python)
Paridad 100% con la versión C++:
- Lectura de teclas instantánea (tipo getch) multiplataforma.
- Borrado de pantalla multiplataforma.
- Protección contra interrupción accidental con Ctrl+C al copiar.
- Menús estandarizados con retorno en 0 y confirmación.
- Soporte para Pila Undo (LIFO) y Multilista ortogonal.
"""
import os
import sys
import signal

# Asegurar importación de estructuras y base de datos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from python.structures.multilista import Multilista
from python.structures.pila import Pila
from python.structures.cola import Cola
from python.core.db import GestorPersistencia

def manejador_sigint(sig, frame):
    """Evita que el usuario interrumpa el programa si intenta copiar con Ctrl+C"""
    sys.stdout.write("\n\n  [i] Recordatorio: En la terminal use Ctrl+Shift+C para copiar texto.\n"
                     "      (Para salir del programa, utilice la opción 0 en el menú).\n")
    sys.stdout.flush()

class ConsolaApp:
    def __init__(self, ruta_bd: str = "data/pea_investigacion.db"):
        self.ruta_bd = ruta_bd
        self.multi = Multilista()
        self.historial = Pila()
        self.cola_ingesta = Cola()

    # -----------------------------------------------------------------
    # HELPERS MULTIPLATAFORMA DE TECLADO Y PANTALLA
    # -----------------------------------------------------------------
    @staticmethod
    def limpiar_pantalla():
        if os.name == 'nt':
            os.system('cls')
        else:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()

    @staticmethod
    def leer_tecla() -> str:
        """Captura una sola tecla inmediatamente sin requerir ENTER"""
        if os.name == 'nt':
            import msvcrt
            return msvcrt.getch().decode('utf-8', errors='ignore')
        else:
            if sys.stdin.isatty():
                import termios
                import tty
                import select
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                    # Filtrar secuencias de escape ANSI (flechas o selección del ratón)
                    if ch == '\x1b':
                        r, _, _ = select.select([sys.stdin], [], [], 0.05)
                        if r:
                            sys.stdin.read(len(sys.stdin.readline()))
                        return ''
                    return ch
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            else:
                # Modo tubería o test automatizado
                c = sys.stdin.read(1)
                return c

    @staticmethod
    def pausar(mensaje: str = "\n[Presione cualquier tecla o ENTER para continuar / regresar]... "):
        sys.stdout.write(mensaje)
        sys.stdout.flush()
        while True:
            c = ConsolaApp.leer_tecla()
            if c:
                break
        sys.stdout.write("\n")

    @staticmethod
    def leer_opcion_menu(opciones_validas: str, mensaje: str = "Seleccione una opción: ") -> int:
        sys.stdout.write(mensaje)
        sys.stdout.flush()
        while True:
            tecla = ConsolaApp.leer_tecla()
            if not tecla:
                continue
            if tecla in opciones_validas:
                sys.stdout.write(tecla + "\n")
                sys.stdout.flush()
                return int(tecla)

    @staticmethod
    def leer_linea(mensaje: str, permitir_vacio: bool = False) -> str:
        while True:
            try:
                linea = input(mensaje).strip()
            except EOFError:
                return ""
            if permitir_vacio or linea:
                return linea
            print("  [!] El campo no puede estar vacío. Intente de nuevo.")

    @staticmethod
    def leer_entero(mensaje: str, valor_por_defecto: int = -1) -> int:
        while True:
            try:
                val = input(mensaje).strip()
            except EOFError:
                return valor_por_defecto
            if not val:
                if valor_por_defecto != -1:
                    return valor_por_defecto
                print("  [!] Ingrese un valor numérico (o 0 para cancelar).")
                continue
            try:
                return int(val)
            except ValueError:
                print("  [!] Entrada inválida. Ingrese un número.")

    # -----------------------------------------------------------------
    # PUNTO DE ENTRADA INTERACTIVO (Punto 10 pág 3)
    # -----------------------------------------------------------------
    def iniciar(self):
        signal.signal(signal.SIGINT, manejador_sigint)
        self.limpiar_pantalla()
        print("=================================================================")
        print("     PEA-i: PROGRAMA ESTADISTICO DE ANALISIS DE INVESTIGACION   ")
        print("    Universidad Popular del Cesar (UPC) - Estructura de Datos   ")
        print("=================================================================")
        print("Seleccione el modo de inicio del sistema:")
        print(f"  [1] Cargar datos persistidos desde la BD SQLite ({self.ruta_bd})")
        print("  [2] Iniciar con estructuras en memoria vacias")
        print("-----------------------------------------------------------------")

        opcion = self.leer_opcion_menu("12", "Opción [1 o 2]: ")
        if opcion == 1:
            print("\n[+] Cargando datos desde SQLite hacia la Multilista...")
            if GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd):
                print("[OK] Datos cargados exitosamente:")
                print(f"     • Grupos:         {self.multi.contar_grupos(False)}")
                print(f"     • Investigadores: {self.multi.contar_investigadores(False)}")
                print(f"     • Productos:      {self.multi.contar_productos(False)}")
            else:
                print("[!] No se pudo cargar la BD. Se iniciará en memoria vacía.")
        else:
            print("\n[+] Iniciando con estructuras en memoria vacías.")

        self.pausar("\n[Presione cualquier tecla o ENTER para ingresar al Menú Principal]... ")
        self.menu_principal()

    # -----------------------------------------------------------------
    # MENÚ PRINCIPAL
    # -----------------------------------------------------------------
    def menu_principal(self):
        op = -1
        while op != 0:
            self.limpiar_pantalla()
            print("=================================================================")
            print("                PEA-i UPC > MENU PRINCIPAL (Python)             ")
            print("=================================================================")
            print("  1. Gestion de Grupos de Investigacion (CRUD)")
            print("  2. Gestion de Investigadores (CRUD)")
            print("  3. Gestion de Productos de Investigacion (CRUD)")
            print(f"  4. Deshacer ultima accion (Pila Undo - LIFO) [{self.historial.tamano()} en pila]")
            print("  5. Resumen Estadistico y Filtro por Ventana de Años")
            print("  6. Guardar cambios en la Base de Datos (Persistencia)")
            print("  0. Salir del Sistema")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("0123456", "Presione una opción [0-6]: ")

            if op == 1:
                self.menu_grupos()
            elif op == 2:
                self.menu_investigadores()
            elif op == 3:
                self.menu_productos()
            elif op == 4:
                self.ejecutar_deshacer()
            elif op == 5:
                self.menu_estadisticas_y_filtro()
            elif op == 6:
                self.guardar_en_bd()
            elif op == 0:
                self.limpiar_pantalla()
                print("=================================================================")
                print("                       SALIDA DEL SISTEMA                        ")
                print("=================================================================")
                print("¿Desea guardar los cambios en SQLite antes de salir?")
                print("  [1] Sí, guardar y salir")
                print("  [2] No guardar y salir")
                print("  [0] Cancelar y regresar al menú")
                print("-----------------------------------------------------------------")
                confirm = self.leer_opcion_menu("012", "Presione opción [1/2/0]: ")
                if confirm == 1:
                    self.guardar_en_bd()
                    print("\n[+] Cambios guardados. ¡Éxitos en el taller!")
                elif confirm == 0:
                    op = -1
                else:
                    print("\n[+] Saliendo sin guardar cambios recientes.")

    # -----------------------------------------------------------------
    # CRUD: GRUPOS
    # -----------------------------------------------------------------
    def menu_grupos(self):
        op = -1
        while op != 0:
            self.limpiar_pantalla()
            print("=================================================================")
            print("     PEA-i UPC > Menú Principal > Gestión de Grupos             ")
            print("=================================================================")
            print("  1. Listar Grupos Registrados")
            print("  2. Incluir Nuevo Grupo")
            print("  3. Consultar Detalle de un Grupo (Hipercubo)")
            print("  4. Modificar Grupo")
            print("  5. Desactivar / Reactivar Grupo (Borrado Lógico)")
            print("  6. Eliminar Grupo Físicamente (Cascada)")
            print("  0. Anterior / Regresar al Menú Principal")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("0123456", "Presione una opción [0-6]: ")

            if op == 1:
                self.limpiar_pantalla()
                print("=========================================================================================")
                print("                             LISTADO DE GRUPOS DE INVESTIGACIÓN                          ")
                print("=========================================================================================")
                print(f"{'CODIGO':<14}{'NOMBRE':<35}{'CLASIF.':<12}{'LIDER':<20}{'ESTADO':<8}")
                print("-" * 89)
                g = self.multi.cabeza_grupos
                if not g:
                    print("  (No hay grupos registrados en memoria)")
                while g is not None:
                    nom_corto = g.nombre[:30] + "..." if len(g.nombre) > 33 else g.nombre
                    estado = "[ACTIVO]" if g.activo else "[INACT]"
                    print(f"{g.codigo_grupo:<14}{nom_corto:<35}{g.clasificacion:<12}{g.lider:<20}{estado:<8}")
                    g = g.sig_grupo
                print("=========================================================================================")
                self.pausar()
            elif op == 2:
                self.limpiar_pantalla()
                print("--- INCLUIR NUEVO GRUPO (Ingrese 0 para cancelar) ---")
                cod = self.leer_linea("Código MinCiencias (ej. COL0009999): ")
                if cod == "0":
                    continue
                nom = self.leer_linea("Nombre del Grupo: ")
                clas = self.leer_linea("Clasificación (A1, A, B, C, Reconocido): ")
                area = self.leer_linea("Área de Conocimiento: ")
                lid = self.leer_linea("Nombre del Líder: ")
                anio = self.leer_entero("Año de Creación: ")

                if self.multi.insertar_grupo(cod, nom, clas, area, lid, anio, True):
                    self.historial.push("CREAR", "GRUPO", cod, "")
                    print("\n[OK] Grupo registrado exitosamente en memoria.")
                else:
                    print(f"\n[!] Error: Ya existe un grupo con el código {cod}")
                self.pausar()
            elif op == 3:
                self.limpiar_pantalla()
                print("--- CONSULTAR DETALLE DE GRUPO (Ingrese 0 para regresar) ---")
                cod = self.leer_linea("Código del Grupo: ")
                if cod == "0":
                    continue
                g = self.multi.buscar_grupo(cod)
                if not g:
                    print("\n[!] Grupo no encontrado.")
                else:
                    print("\n=================================================================")
                    print(f"DETALLE DEL GRUPO: {g.nombre}")
                    print(f"Código: {g.codigo_grupo} | Clasificación: {g.clasificacion}")
                    print(f"Líder: {g.lider} | Área: {g.area_conocimiento} | Año: {g.anio_creacion}")
                    print(f"Estado: {'ACTIVO' if g.activo else 'DESACTIVADO (Borrado lógico)'}")

                    print("\n  -- Investigadores Adscritos --")
                    inv = g.primer_investigador
                    if not inv:
                        print("     (Sin investigadores registrados)")
                    while inv:
                        estado = "Activo" if inv.activo else "Inactivo"
                        print(f"     • {inv.nombre_completo} ({inv.categoria}) - {estado}")
                        inv = inv.sig_investigador

                    print("\n  -- Productos Generados (Hipercubo) --")
                    p = g.primer_producto
                    if not p:
                        print("     (Sin productos registrados)")
                    while p:
                        val = "Validado" if p.validado else "No validado"
                        estado = "Activo" if p.activo else "Inactivo"
                        print(f"     • [{p.tipo} {p.anio}] {p.titulo} (Cat: {p.categoria_minciencias}, {val}) [{estado}]")
                        p = p.sig_producto_grupo
                    print("=================================================================")
                self.pausar()
            elif op == 4:
                self.limpiar_pantalla()
                print("--- MODIFICAR GRUPO (Ingrese 0 para regresar) ---")
                cod = self.leer_linea("Código del Grupo a modificar: ")
                if cod == "0":
                    continue
                g = self.multi.buscar_grupo(cod)
                if not g:
                    print("\n[!] Grupo no encontrado.")
                else:
                    prev = f"nom={g.nombre};clas={g.clasificacion};lid={g.lider}"
                    g.nombre = self.leer_linea(f"Nuevo Nombre ({g.nombre}): ")
                    g.clasificacion = self.leer_linea(f"Nueva Clasificación ({g.clasificacion}): ")
                    g.lider = self.leer_linea(f"Nuevo Líder ({g.lider}): ")
                    self.historial.push("MODIFICAR", "GRUPO", cod, prev)
                    print("\n[OK] Grupo modificado exitosamente.")
                self.pausar()
            elif op == 5:
                self.limpiar_pantalla()
                print("--- DESACTIVAR / REACTIVAR GRUPO (Borrado Lógico) ---")
                cod = self.leer_linea("Código del Grupo (0 para regresar): ")
                if cod == "0":
                    continue
                g = self.multi.buscar_grupo(cod)
                if not g:
                    print("\n[!] Grupo no encontrado.")
                else:
                    nuevo_estado = not g.activo
                    self.multi.desactivar_grupo(cod, nuevo_estado)
                    self.historial.push("DESACTIVAR", "GRUPO", cod, "desactivar" if nuevo_estado else "activar")
                    estado_str = "ACTIVO" if nuevo_estado else "DESACTIVADO"
                    print(f"\n[OK] Estado lógico cambiado a: {estado_str}")
                self.pausar()
            elif op == 6:
                self.limpiar_pantalla()
                print("--- ELIMINAR GRUPO FÍSICAMENTE (Ingrese 0 para regresar) ---")
                cod = self.leer_linea("Código del Grupo a ELIMINAR: ")
                if cod == "0":
                    continue
                print("\n  [ADVERTENCIA] Se eliminará el grupo, sus investigadores y productos asociados.")
                conf = self.leer_opcion_menu("01", "¿Confirmar eliminación física definitiva? (1: Sí / 0: Cancelar): ")
                if conf == 1:
                    if self.multi.eliminar_grupo(cod):
                        self.historial.push("ELIMINAR", "GRUPO", cod, "")
                        print("\n[OK] Grupo y dependencias eliminados físicamente de memoria.")
                    else:
                        print("\n[!] Grupo no encontrado.")
                else:
                    print("\n[+] Operación cancelada.")
                self.pausar()

    # -----------------------------------------------------------------
    # CRUD: INVESTIGADORES
    # -----------------------------------------------------------------
    def menu_investigadores(self):
        op = -1
        while op != 0:
            self.limpiar_pantalla()
            print("=================================================================")
            print("   PEA-i UPC > Menú Principal > Gestión de Investigadores        ")
            print("=================================================================")
            print("  1. Listar Investigadores")
            print("  2. Incluir Nuevo Investigador")
            print("  3. Consultar Detalle (Productos Autorados)")
            print("  4. Modificar Investigador")
            print("  5. Desactivar / Reactivar Investigador (Borrado Lógico)")
            print("  6. Eliminar Investigador Físicamente")
            print("  0. Anterior / Regresar al Menú Principal")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("0123456", "Presione una opción [0-6]: ")

            if op == 1:
                self.limpiar_pantalla()
                print("=================================================================================")
                print("                             LISTADO DE INVESTIGADORES                           ")
                print("=================================================================================")
                print(f"{'DOCUMENTO/ID':<15}{'NOMBRE':<28}{'CATEGORIA':<15}{'GRUPO':<15}{'ESTADO':<8}")
                print("-" * 81)
                g = self.multi.cabeza_grupos
                hay_datos = False
                while g:
                    inv = g.primer_investigador
                    while inv:
                        hay_datos = True
                        estado = "[ACTIVO]" if inv.activo else "[INACT]"
                        print(f"{inv.documento_id:<15}{inv.nombre_completo:<28}{inv.categoria:<15}{inv.codigo_grupo:<15}{estado:<8}")
                        inv = inv.sig_investigador
                    g = g.sig_grupo
                if not hay_datos:
                    print("  (No hay investigadores registrados)")
                print("=================================================================================")
                self.pausar()
            elif op == 2:
                self.limpiar_pantalla()
                print("--- INCLUIR NUEVO INVESTIGADOR (Ingrese 0 para cancelar) ---")
                cod_g = self.leer_linea("Código del Grupo al que pertenece: ")
                if cod_g == "0":
                    continue
                if not self.multi.buscar_grupo(cod_g):
                    print(f"\n[!] El grupo {cod_g} no existe. Debe crearlo primero.")
                    self.pausar()
                    continue
                doc = self.leer_linea("Documento / ID CvLAC: ")
                if doc == "0":
                    continue
                nom = self.leer_linea("Nombre Completo: ")
                cat = self.leer_linea("Categoría (Senior, Asociado, Junior, Sin Categoria): ")
                form = self.leer_linea("Formación Académica: ")

                if self.multi.insertar_investigador(cod_g, doc, nom, cat, form, True):
                    self.historial.push("CREAR", "INVESTIGADOR", doc, cod_g)
                    print("\n[OK] Investigador registrado exitosamente.")
                else:
                    print("\n[!] Error: Ya existe un investigador con ese documento.")
                self.pausar()
            elif op == 3:
                self.limpiar_pantalla()
                print("--- CONSULTAR DETALLE DE INVESTIGADOR (Ingrese 0 para regresar) ---")
                doc = self.leer_linea("Documento del Investigador: ")
                if doc == "0":
                    continue
                inv = self.multi.buscar_investigador(doc)
                if not inv:
                    print("\n[!] Investigador no encontrado.")
                else:
                    print("\n=================================================================")
                    print(f"INVESTIGADOR: {inv.nombre_completo}")
                    print(f"Documento: {inv.documento_id} | Categoría: {inv.categoria}")
                    print(f"Formación: {inv.formacion_academica} | Grupo: {inv.codigo_grupo}")
                    print(f"Estado: {'ACTIVO' if inv.activo else 'DESACTIVADO'}")

                    print("\n  -- Producción Autorada (Hipercubo Ortogonal) --")
                    p = inv.primer_producto
                    if not p:
                        print("     (Sin productos asociados)")
                    while p:
                        val = "Validado" if p.validado else "No validado"
                        estado = "Activo" if p.activo else "Inactivo"
                        print(f"     • [{p.tipo} {p.anio}] {p.titulo} (Cat: {p.categoria_minciencias}, {val}) [{estado}]")
                        p = p.sig_producto_investigador
                    print("=================================================================")
                self.pausar()
            elif op == 4:
                self.limpiar_pantalla()
                print("--- MODIFICAR INVESTIGADOR (Ingrese 0 para regresar) ---")
                doc = self.leer_linea("Documento del Investigador: ")
                if doc == "0":
                    continue
                inv = self.multi.buscar_investigador(doc)
                if not inv:
                    print("\n[!] Investigador no encontrado.")
                else:
                    prev = f"nom={inv.nombre_completo};cat={inv.categoria}"
                    inv.nombre_completo = self.leer_linea(f"Nuevo Nombre ({inv.nombre_completo}): ")
                    inv.categoria = self.leer_linea(f"Nueva Categoría ({inv.categoria}): ")
                    inv.formacion_academica = self.leer_linea(f"Nueva Formación ({inv.formacion_academica}): ")
                    self.historial.push("MODIFICAR", "INVESTIGADOR", doc, prev)
                    print("\n[OK] Investigador modificado exitosamente.")
                self.pausar()
            elif op == 5:
                self.limpiar_pantalla()
                print("--- DESACTIVAR / REACTIVAR INVESTIGADOR (Borrado Lógico) ---")
                doc = self.leer_linea("Documento del Investigador (0 para regresar): ")
                if doc == "0":
                    continue
                inv = self.multi.buscar_investigador(doc)
                if not inv:
                    print("\n[!] Investigador no encontrado.")
                else:
                    nuevo = not inv.activo
                    self.multi.desactivar_investigador(doc, nuevo)
                    self.historial.push("DESACTIVAR", "INVESTIGADOR", doc, "desactivar" if nuevo else "activar")
                    estado_str = "ACTIVO" if nuevo else "DESACTIVADO"
                    print(f"\n[OK] Estado lógico cambiado a: {estado_str}")
                self.pausar()
            elif op == 6:
                self.limpiar_pantalla()
                print("--- ELIMINAR INVESTIGADOR FÍSICAMENTE (Ingrese 0 para regresar) ---")
                doc = self.leer_linea("Documento del Investigador a ELIMINAR: ")
                if doc == "0":
                    continue
                conf = self.leer_opcion_menu("01", "¿Confirmar eliminación física definitiva? (1: Sí / 0: Cancelar): ")
                if conf == 1:
                    if self.multi.eliminar_investigador(doc):
                        self.historial.push("ELIMINAR", "INVESTIGADOR", doc, "")
                        print("\n[OK] Investigador y sus productos eliminados de la memoria.")
                    else:
                        print("\n[!] Investigador no encontrado.")
                else:
                    print("\n[+] Operación cancelada.")
                self.pausar()

    # -----------------------------------------------------------------
    # CRUD: PRODUCTOS
    # -----------------------------------------------------------------
    def menu_productos(self):
        op = -1
        while op != 0:
            self.limpiar_pantalla()
            print("=================================================================")
            print("     PEA-i UPC > Menú Principal > Gestión de Productos           ")
            print("=================================================================")
            print("  1. Listar Productos")
            print("  2. Incluir Nuevo Producto")
            print("  3. Consultar Detalle de Producto")
            print("  4. Modificar Producto (Categoría y Validación)")
            print("  5. Desactivar / Reactivar Producto (Borrado Lógico)")
            print("  6. Eliminar Producto Físicamente")
            print("  0. Anterior / Regresar al Menú Principal")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("0123456", "Presione una opción [0-6]: ")

            if op == 1:
                self.limpiar_pantalla()
                print("===================================================================================")
                print("                            LISTADO DE PRODUCTOS DE INVESTIGACIÓN                  ")
                print("===================================================================================")
                print(f"{'ID':<12}{'TIPO':<12}{'TITULO':<32}{'AÑO':<6}{'CAT':<6}{'VAL':<7}{'ESTADO':<8}")
                print("-" * 83)
                g = self.multi.cabeza_grupos
                hay_datos = False
                while g:
                    p = g.primer_producto
                    while p:
                        hay_datos = True
                        tit_corto = p.titulo[:27] + "..." if len(p.titulo) > 30 else p.titulo
                        val_str = "SI" if p.validado else "NO"
                        act_str = "[ACT]" if p.activo else "[INA]"
                        print(f"{p.id_producto:<12}{p.tipo:<12}{tit_corto:<32}{p.anio:<6}{p.categoria_minciencias:<6}{val_str:<7}{act_str:<8}")
                        p = p.sig_producto_grupo
                    g = g.sig_grupo
                if not hay_datos:
                    print("  (No hay productos registrados)")
                print("===================================================================================")
                self.pausar()
            elif op == 2:
                self.limpiar_pantalla()
                print("--- INCLUIR NUEVO PRODUCTO (Ingrese 0 para cancelar) ---")
                cod_g = self.leer_linea("Código del Grupo asociado: ")
                if cod_g == "0":
                    continue
                id_inv = self.leer_linea("Documento del Investigador autor: ")
                if id_inv == "0":
                    continue
                if not self.multi.buscar_grupo(cod_g) or not self.multi.buscar_investigador(id_inv):
                    print("\n[!] Error: El Grupo o el Investigador no existen en la Multilista.")
                    self.pausar()
                    continue
                id_p = self.leer_linea("ID del Producto (ej. PROD-999): ")
                if id_p == "0":
                    continue
                tipo = self.leer_linea("Tipo (Articulo, Libro, Capitulo, Software, Patente): ")
                tit = self.leer_linea("Título de la obra: ")
                anio = self.leer_entero("Año de publicación: ")
                cat = self.leer_linea("Categoría MinCiencias (A1, A, B, C): ")
                val = self.leer_opcion_menu("01", "¿Validado/Avalado por MinCiencias? (1: Sí / 0: No): ")

                if self.multi.insertar_producto(cod_g, id_inv, id_p, tipo, tit, anio, cat, val == 1, True):
                    self.historial.push("CREAR", "PRODUCTO", id_p, cod_g)
                    print("\n[OK] Producto registrado y enlazado ortogonalmente en el Hipercubo.")
                else:
                    print(f"\n[!] Ya existe un producto con el ID {id_p}")
                self.pausar()
            elif op == 3:
                self.limpiar_pantalla()
                print("--- CONSULTAR DETALLE DE PRODUCTO (0 para regresar) ---")
                id_p = self.leer_linea("ID del Producto: ")
                if id_p == "0":
                    continue
                p = self.multi.buscar_producto(id_p)
                if not p:
                    print("\n[!] Producto no encontrado.")
                else:
                    print("\n=================================================================")
                    print(f"PRODUCTO: [{p.id_producto}] {p.titulo}")
                    print(f"Tipo: {p.tipo} | Año: {p.anio}")
                    val_str = "VALIDADO" if p.validado else "NO VALIDADO"
                    print(f"Categoría MinCiencias: {p.categoria_minciencias} | Aval MinCiencias: {val_str}")
                    print(f"Grupo: {p.codigo_grupo} | Investigador Autor: {p.id_investigador}")
                    print(f"Estado: {'ACTIVO' if p.activo else 'DESACTIVADO'}")
                    print("=================================================================")
                self.pausar()
            elif op == 4:
                self.limpiar_pantalla()
                print("--- MODIFICAR PRODUCTO (0 para regresar) ---")
                id_p = self.leer_linea("ID del Producto a modificar: ")
                if id_p == "0":
                    continue
                p = self.multi.buscar_producto(id_p)
                if not p:
                    print("\n[!] Producto no encontrado.")
                else:
                    prev = f"tit={p.titulo};cat={p.categoria_minciencias}"
                    p.titulo = self.leer_linea(f"Nuevo Título ({p.titulo}): ")
                    p.anio = self.leer_entero("Nuevo Año: ")
                    p.categoria_minciencias = self.leer_linea(f"Nueva Categoría ({p.categoria_minciencias}): ")
                    val = self.leer_opcion_menu("01", "¿Validado? (1: Sí / 0: No): ")
                    p.validado = (val == 1)
                    self.historial.push("MODIFICAR", "PRODUCTO", id_p, prev)
                    print("\n[OK] Producto actualizado exitosamente.")
                self.pausar()
            elif op == 5:
                self.limpiar_pantalla()
                print("--- DESACTIVAR / REACTIVAR PRODUCTO (Borrado Lógico) ---")
                id_p = self.leer_linea("ID del Producto (0 para regresar): ")
                if id_p == "0":
                    continue
                p = self.multi.buscar_producto(id_p)
                if not p:
                    print("\n[!] Producto no encontrado.")
                else:
                    nuevo = not p.activo
                    self.multi.desactivar_producto(id_p, nuevo)
                    self.historial.push("DESACTIVAR", "PRODUCTO", id_p, "desactivar" if nuevo else "activar")
                    estado_str = "ACTIVO" if nuevo else "DESACTIVADO"
                    print(f"\n[OK] Estado lógico cambiado a: {estado_str}")
                self.pausar()
            elif op == 6:
                self.limpiar_pantalla()
                print("--- ELIMINAR PRODUCTO FÍSICAMENTE (0 para regresar) ---")
                id_p = self.leer_linea("ID del Producto a ELIMINAR: ")
                if id_p == "0":
                    continue
                conf = self.leer_opcion_menu("01", "¿Confirmar eliminación física? (1: Sí / 0: Cancelar): ")
                if conf == 1:
                    if self.multi.eliminar_producto(id_p):
                        self.historial.push("ELIMINAR", "PRODUCTO", id_p, "")
                        print("\n[OK] Producto desenlazado ortogonalmente y liberado de memoria.")
                    else:
                        print("\n[!] Producto no encontrado.")
                else:
                    print("\n[+] Operación cancelada.")
                self.pausar()

    # -----------------------------------------------------------------
    # DESHACER (PILA UNDO - LIFO)
    # -----------------------------------------------------------------
    def ejecutar_deshacer(self):
        self.limpiar_pantalla()
        print("=================================================================")
        print("           DESHACER ÚLTIMA ACCIÓN (TDA PILA - LIFO)              ")
        print("=================================================================")

        acc = self.historial.pop()
        if not acc:
            print("\n[!] La Pila de historial está vacía. No hay acciones por deshacer.")
            self.pausar()
            return

        print(f"\n[<-- Deshacer] Revertiendo última acción: {acc.tipo_operacion} en {acc.tipo_entidad} ({acc.id_registro})...")

        if acc.tipo_operacion == "DESACTIVAR":
            if acc.tipo_entidad == "GRUPO":
                g = self.multi.buscar_grupo(acc.id_registro)
                if g:
                    g.activo = not g.activo
            elif acc.tipo_entidad == "INVESTIGADOR":
                inv = self.multi.buscar_investigador(acc.id_registro)
                if inv:
                    inv.activo = not inv.activo
            elif acc.tipo_entidad == "PRODUCTO":
                p = self.multi.buscar_producto(acc.id_registro)
                if p:
                    p.activo = not p.activo
            print("[OK] Estado lógico restaurado con éxito mediante pop() de la Pila.")
        elif acc.tipo_operacion == "CREAR":
            if acc.tipo_entidad == "GRUPO":
                self.multi.eliminar_grupo(acc.id_registro)
            elif acc.tipo_entidad == "INVESTIGADOR":
                self.multi.eliminar_investigador(acc.id_registro)
            elif acc.tipo_entidad == "PRODUCTO":
                self.multi.eliminar_producto(acc.id_registro)
            print("[OK] Inserción revertida (registro retirado de memoria).")
        else:
            print("[OK] Acción procesada desde la cima de la Pila.")

        print(f"\nAcciones restantes en la Pila: {self.historial.tamano()}")
        self.pausar()

    # -----------------------------------------------------------------
    # RESUMEN ESTADÍSTICO Y FILTRO POR VENTANA DE AÑOS
    # -----------------------------------------------------------------
    def menu_estadisticas_y_filtro(self):
        self.limpiar_pantalla()
        print("=================================================================")
        print("           RESUMEN ESTADÍSTICO INSTITUCIONAL (SCIENTI - UPC)    ")
        print("=================================================================")

        total_grupos_act = self.multi.contar_grupos(True)
        total_grupos_tot = self.multi.contar_grupos(False)
        total_inv_act = self.multi.contar_investigadores(True)
        total_prod_act = self.multi.contar_productos(True)

        print(f"• Grupos de Investigación:  {total_grupos_act} activos ({total_grupos_tot} en total)")
        print(f"• Investigadores Activos:   {total_inv_act}")
        print(f"• Productos Activos:        {total_prod_act}")

        articulos = libros = software = capitulos = patentes = 0
        cat_a1 = cat_a = cat_b = cat_c = validados = 0

        g = self.multi.cabeza_grupos
        while g:
            p = g.primer_producto
            while p:
                if p.activo and g.activo:
                    if p.tipo == "Articulo": articulos += 1
                    elif p.tipo == "Libro": libros += 1
                    elif p.tipo == "Software": software += 1
                    elif p.tipo == "Capitulo": capitulos += 1
                    elif p.tipo == "Patente": patentes += 1

                    if p.categoria_minciencias == "A1": cat_a1 += 1
                    elif p.categoria_minciencias == "A": cat_a += 1
                    elif p.categoria_minciencias == "B": cat_b += 1
                    elif p.categoria_minciencias == "C": cat_c += 1

                    if p.validado: validados += 1
                p = p.sig_producto_grupo
            g = g.sig_grupo

        print("\n--- Desglose por Tipo de Producto ---")
        print(f"  - Artículos científicos: {articulos}")
        print(f"  - Libros / Obras:        {libros}")
        print(f"  - Capítulos de libro:    {capitulos}")
        print(f"  - Desarrollos software:  {software}")
        print(f"  - Patentes registradas:  {patentes}")

        print("\n--- Calidad MinCiencias & Validación ---")
        print(f"  - Categoría A1: {cat_a1} | Categoría A: {cat_a} | Categoría B: {cat_b} | Categoría C: {cat_c}")
        porc = (validados * 100 // total_prod_act) if total_prod_act > 0 else 0
        print(f"  - Avalados por MinCiencias: {validados} ({porc}%)")

        print("\n-----------------------------------------------------------------")
        print("FILTRO POR VENTANA DE OBSERVACIÓN (Años MinCiencias)")
        print("  [1] Últimos 2 años (2024 - 2026)")
        print("  [2] Últimos 5 años (2021 - 2026)")
        print("  [3] Rango de años personalizado")
        print("  [0] Anterior / Regresar al Menú Principal")
        print("-----------------------------------------------------------------")
        op_filtro = self.leer_opcion_menu("0123", "Presione opción [0-3]: ")

        if op_filtro == 1:
            inicio, fin = 2024, 2026
        elif op_filtro == 2:
            inicio, fin = 2021, 2026
        elif op_filtro == 3:
            inicio = self.leer_entero("Año inicial: ")
            fin = self.leer_entero("Año final: ")
        else:
            return

        prods_ventana = self.multi.contar_productos_por_ventana(inicio, fin, True)
        print(f"\n[RESULTADO VENTANA {inicio} - {fin}]")
        print(f"Total de productos en la ventana: {prods_ventana}\n")
        print(f"{'ID':<12}{'AÑO':<6}{'TIPO':<12}{'TITULO':<35}{'GRUPO':<14}")
        print("-" * 79)

        g = self.multi.cabeza_grupos
        while g:
            p = g.primer_producto
            while p:
                if p.activo and g.activo and inicio <= p.anio <= fin:
                    tit_corto = p.titulo[:30] + "..." if len(p.titulo) > 33 else p.titulo
                    print(f"{p.id_producto:<12}{p.anio:<6}{p.tipo:<12}{tit_corto:<35}{p.codigo_grupo:<14}")
                p = p.sig_producto_grupo
            g = g.sig_grupo

        print("=================================================================")
        self.pausar()

    def guardar_en_bd(self):
        self.limpiar_pantalla()
        print("=================================================================")
        print("       PERSISTENCIA: GUARDAR DATOS EN SQLITE (data.db)           ")
        print("=================================================================")
        print("[+] Sincronizando Multilista en memoria con SQLite...")
        if GestorPersistencia.guardar_en_bd(self.multi, self.ruta_bd):
            print(f"[OK] Todos los registros fueron persistidos exitosamente en {self.ruta_bd}")
        else:
            print("[!] Error al guardar datos en SQLite.")
        self.pausar()
