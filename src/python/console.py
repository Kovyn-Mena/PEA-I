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
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)
pylib_dir = os.path.join(ROOT_DIR, "pylib")
if os.path.exists(pylib_dir) and pylib_dir not in sys.path:
    sys.path.insert(0, pylib_dir)

from python.structures.multilista import Multilista
from python.structures.pila import Pila
from python.structures.cola import Cola
from python.core.db import GestorPersistencia
from python.core.catalogo_2024 import CatalogoMinCiencias2024

def manejador_sigint(sig, frame):
    """Evita que el usuario interrumpa el programa si intenta copiar con Ctrl+C"""
    sys.stdout.write("\n\n  [i] Recordatorio: En la terminal use Ctrl+Shift+C para copiar texto.\n"
                     "      (Para salir del programa, utilice la opción 0 en el menú).\n")
    sys.stdout.flush()

def espaciar(s: str) -> str:
    """Repara palabras pegadas del HTML de SCIENTI
    ('Septiembrede2007' -> 'Septiembre de 2007'; 'paraLa' -> 'para La').
    Solo para texto libre (áreas, formación); nunca en nombres ni títulos/URLs."""
    if not s:
        return s
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "dD" and i > 0 and i + 6 <= n and s[i + 1] in "eE" \
                and s[i + 2:i + 6].isdigit() and s[i - 1].islower():
            out.append(" de ")
            out.append(s[i + 2:i + 6])
            i += 6
            continue
        out.append(c)
        if i + 1 < n:
            a, b = s[i], s[i + 1]
            if a.islower() and (b.isupper() or b.isdigit()):
                out.append(" ")
        i += 1
    return "".join(out)

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
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                (void_code := msvcrt.getch()) # Consumir el segundo byte de flechas/teclas especiales
                return ''
            return ch.decode('utf-8', errors='ignore')
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
    def pausar(mensaje: str = "\n[Presione ENTER para continuar / regresar]... "):
        try:
            input(mensaje)
        except (EOFError, KeyboardInterrupt):
            pass

    @staticmethod
    def leer_opcion_menu(opciones_validas: str, mensaje: str = "Seleccione una opción: "):
        while True:
            try:
                linea = input(mensaje).strip()
            except (EOFError, KeyboardInterrupt):
                return 0
            if not linea:
                continue
            if linea in opciones_validas or linea.upper() in opciones_validas:
                if linea.isdigit():
                    return int(linea)
                return linea.upper()
            print(f"  [!] Opción inválida '{linea}'. Por favor ingrese una opción válida y presione ENTER.")

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
    # VALIDACIÓN DE ACCESO PREVIA (LOGIN)
    # -----------------------------------------------------------------
    def autenticar_usuario(self) -> bool:
        for intento in range(1, 4):
            self.limpiar_pantalla()
            print("=================================================================")
            print("     PEA-i UPC: VALIDACION DE ACCESO INSTITUCIONAL (LOGIN)       ")
            print("=================================================================")
            print("  Credenciales por defecto -> Usuario: admin | Contraseña: 1234")
            print("-----------------------------------------------------------------")
            try:
                user = input("  Usuario: ").strip()
                pw = input("  Contraseña: ").strip()
            except (EOFError, KeyboardInterrupt):
                return False

            if not user or not pw:
                print(f"\n  [!] El usuario y la contraseña son obligatorios (Intento {intento}/3).")
                self.pausar("  [Presione ENTER para intentar nuevamente]... ")
                continue

            if user.lower() in ("admin", "upc", "docente") and pw in ("1234", "admin", "upc2026"):
                print(f"\n  [OK] Acceso concedido. Bienvenido ({user}).")
                return True
            print(f"\n  [!] Credenciales incorrectas (Intento {intento}/3).")
            self.pausar("  [Presione ENTER para intentar nuevamente]... ")
        print("\n  [X] Número máximo de intentos alcanzado. Saliendo...")
        return False

    # -----------------------------------------------------------------
    # PUNTO DE ENTRADA INTERACTIVO (Flujo de Arranque Dinámico)
    # -----------------------------------------------------------------
    def menu_buscar_y_cargar_grupo_inicio(self):
        print("\n=================================================================")
        print("  --- BUSCAR Y CARGAR GRUPO POR NOMBRE EN SCIENTI / MINCIENCIAS ---")
        print("=================================================================")
        q = self.leer_linea("Nombre o sigla a buscar (ej. GISICO, Biotecnología): ").strip()
        if not q or q == "0":
            return False

        print("\n[Buscando en ScienTI / Catálogo Institucional UPC...]")
        from python.core.busqueda_scienti import buscar_grupo_en_indices
        cands = buscar_grupo_en_indices(q)
        if not cands:
            print(f"[AVISO] Grupo no existente (sin coincidencias para '{q}').")
            self.pausar()
            return False

        print(f"\nCoincidencias encontradas ({len(cands)} grupos):")
        print(f"{'No.':<4}{'CÓDIGO':<12}{'GRUPO':<45}{'LÍDER':<25}")
        print("-" * 88)
        for i, g in enumerate(cands[:20], 1):
            nom = g.get("nombre", "")[:42]
            lid = g.get("lider", "")[:23]
            print(f"{i:<4}{g.get('col',''):<12}{nom:<45}{lid:<25}")
        print("-" * 88)

        sel = self.leer_linea(f"Seleccione opción [1-{min(len(cands),20)}] para descargar y cargar (0 cancela): ", permitir_vacio=True)
        if not sel or sel == "0" or not sel.isdigit() or not (1 <= int(sel) <= min(len(cands), 20)):
            print("[CANCELADO].")
            self.pausar()
            return False

        elegido = cands[int(sel) - 1]
        nro = elegido.get("nro", "")
        cod = elegido.get("col", "")
        nombre = elegido.get("nombre", "")

        print(f"\n[+] Conectando a ScienTI y descargando grupo: {nombre} ({cod} / nro={nro})...")
        from python.core.ingesta import MotorIngesta, _buscar_snapshot_gruplac
        motor = MotorIngesta(self.ruta_bd)
        url = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={nro}" if nro else f"COL:{cod}"
        if nro and _buscar_snapshot_gruplac(nro):
            print(f"[i] Snapshot local disponible: scrape offline instantáneo.")
        else:
            print(f"[i] Sin snapshot local: intentará descarga en vivo "
                  f"(MinCiencias responde en 10-30 s, sea paciente).")
        self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
        if motor.ejecutar_ingesta("URL_GRUPLAC", url):
            self.multi = Multilista()
            GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
            print(f"\n[OK] ¡Grupo {nombre} ({cod}) descargado e ingestados sus datos a la Multilista!")
            return True
        return False

    def iniciar(self):
        if os.name == 'nt':
            os.system("chcp 65001 > nul 2>&1")
        signal.signal(signal.SIGINT, manejador_sigint)
        if not self.autenticar_usuario():
            return
        self.limpiar_pantalla()
        print("=================================================================")
        print("     PEA-i: PROGRAMA ESTADISTICO DE ANALISIS DE INVESTIGACION   ")
        print("    Universidad Popular del Cesar (UPC) - Estructura de Datos   ")
        print("=================================================================")

        while True:
            resp = self.leer_linea("¿Desea cargar algún grupo de investigación de la Universidad Popular del Cesar? (si/no): ").strip().lower()
            if resp in ("si", "s", "sí"):
                ok = self.menu_buscar_y_cargar_grupo_inicio()
                if ok:
                    self.pausar("\n[Presione cualquier tecla o ENTER para ingresar al Menú Principal]... ")
                    self.menu_principal()
                    return
                # Sin carga nueva (cancelado/fallo): submenú espejo
                print("\n-----------------------------------------------------------------")
                print(" [SIN CARGA NUEVA] Elija la modalidad de arranque inicial:")
                print("  [1] Volver a buscar otro grupo")
                print(f"  [2] Precargar datos de la Universidad desde SQLite ({self.ruta_bd})")
                print("  [3] Iniciar con estructuras vacías en memoria RAM (Ejecutar sin datos)")
                print("-----------------------------------------------------------------")
                sub = self.leer_opcion_menu("123", "Seleccione una opción [1-3]: ")
                if sub == 1:
                    continue
                elif sub == 2:
                    print("\n[+] Cargando datos desde SQLite hacia la Multilista...")
                    if GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd):
                        print(f"[OK] {self.multi.contar_grupos(False)} grupos, {self.multi.contar_investigadores(False)} investigadores, {self.multi.contar_productos(False)} productos cargados.")
                else:
                    print("\n[+] Iniciando con estructuras en memoria vacías.")
                self.pausar("\n[Presione cualquier tecla o ENTER para ingresar al Menú Principal]... ")
                self.menu_principal()
                return
            elif resp in ("no", "n"):
                print("\n-----------------------------------------------------------------")
                print(" [NOTA 10] Elija la modalidad de arranque inicial:")
                print(f"  [1] Cargar datos persistidos desde la BD SQLite ({self.ruta_bd})")
                print("  [2] Iniciar con estructuras vacías en memoria RAM (Ejecutar sin datos)")
                print("-----------------------------------------------------------------")
                opcion = self.leer_opcion_menu("12", "Opción [1 o 2]: ")
                if opcion == 1:
                    print("\n[+] Cargando datos desde SQLite hacia la Multilista...")
                    if GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd):
                        print(f"[OK] {self.multi.contar_grupos(False)} grupos, {self.multi.contar_investigadores(False)} investigadores, {self.multi.contar_productos(False)} productos cargados.")
                    else:
                        print("[!] No se pudo cargar la BD. Se iniciará en memoria vacía.")
                else:
                    print("\n[+] Iniciando con estructuras en memoria vacías.")
                self.pausar("\n[Presione cualquier tecla o ENTER para ingresar al Menú Principal]... ")
                self.menu_principal()
                return
            else:
                print("[AVISO] Por favor responda 'si' o 'no'.")

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
            print("  7. Portal Institucional de Investigacion y Dashboard (GUI Python / Web)")
            print("  8. Ingesta de Datos MinCiencias (Web Scraping / PDF / CSV - Cola FIFO)")
            print("  9. Generar Informe PDF Institucional de Grupo (Estilo GrupLAC - ReportLab)")
            print("  G. Guia Oficial del Sistema y Manual de Sustentacion")
            print("  0. Salir del Sistema")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("0123456789Gg", "Presione una opción [0-9 o G]: ")

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
            elif op == 7:
                self.menu_gui_portal()
            elif op == 8:
                self.menu_ingesta()
            elif op == 9:
                self.menu_generar_informe_pdf()
            elif op == 'G':
                self.mostrar_guia_sistema()
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
    # PORTAL VISUALIZADOR & DASHBOARD (GUI PYTHON / WEB)
    # -----------------------------------------------------------------
    def menu_gui_portal(self):
        """Lanza el Dashboard Gráfico & Portal Ejecutivo (GUI Python)"""
        self.limpiar_pantalla()
        print("=================================================================")
        print("    PEA-i UPC > Portal Institucional y Dashboard (GUI Python)   ")
        print("=================================================================")
        print("  1. Abrir Portal Institucional C++ (HTML5 / Zero-Dependencies)")
        print("  2. Abrir Dashboard Analítico Python (HTML5 + 3 Vistas + PDFs)")
        print("  3. Ejecutar ingesta masiva UPC (66) y regenerar Dashboard")
        print("  0. Regresar al Menú Principal")
        print("-----------------------------------------------------------------")
        op = self.leer_opcion_menu("0123", "Seleccione una opción [0-3]: ")
        if op == 1:
            ruta_html = os.path.abspath(os.path.join(ROOT_DIR, "dist", "visualizador_hipercubo.html"))
            print(f"\n[+] Abriendo Portal Web Ejecutivo en el navegador...")
            try:
                import webbrowser
                from pathlib import Path
                # Path.as_uri() produce 'file:///C:/...' válido en Windows
                # (un f-string 'file://{ruta}' daría 'file://C:\...', inválido).
                webbrowser.open(Path(ruta_html).resolve().as_uri())
                print(f"[OK] Portal abierto exitosamente desde: {ruta_html}")
            except Exception as e:
                print(f"[!] Error al abrir el navegador: {e}")
            self.pausar()
        elif op == 2:
            print("\n[+] Inicializando Dashboard Analítico Python (HTML5 + 3 Vistas)...")
            try:
                from python.gui import DashboardApp
                app_gui = DashboardApp(self.ruta_bd)
                app_gui.iniciar()
            except Exception as e:
                print(f"[!] Error al iniciar Dashboard Python: {e}")
            self.pausar()
        elif op == 3:
            print("\n[+] Ejecutando ingesta masiva UPC (66 grupos, GISICO al final)...")
            try:
                from python.core.ingesta import MotorIngesta
                from python.gui import DashboardApp
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                motor = MotorIngesta(self.ruta_bd)
                if motor.ejecutar_ingesta_automatica():
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                    DashboardApp(self.ruta_bd).iniciar()
            except Exception as e:
                print(f"[!] Error en ingesta masiva desde GUI: {e}")
            self.pausar()

    # -----------------------------------------------------------------
    # GUÍA DEL SISTEMA & MANUAL DE SUSTENTACIÓN
    # -----------------------------------------------------------------
    def mostrar_guia_sistema(self):
        """Muestra la Guía Oficial del Sistema y Manual de Sustentación"""
        self.limpiar_pantalla()
        print("=================================================================")
        print("       PEA-i UPC: GUÍA OFICIAL DEL SISTEMA & SUSTENTACIÓN        ")
        print("=================================================================")
        print("  Universidad Popular del Cesar — Facultad de Ingeniería")
        print("  Asignatura: Estructura de Datos (Taller 2) | Semestre: 2026-I")
        print("  Docente Evaluador: Ing. Adith Bismarck Pérez Orozco")
        print("  Estudiante: Kovyn B. Mena (kbmena@unicesar.edu.co)")
        print("-----------------------------------------------------------------")
        print("  1. FILOSOFÍA CONSOLA PRIMERO & TDAs PUROS EN RAM:")
        print("     • Multilista Ortogonal 3D: Modela el Hipercubo conectando")
        print("       Grupos (Eje X), Investigadores (Eje Y) y Productos (Eje Z)")
        print("       sin matrices densas, ahorrando el 99.8% de memoria.")
        print("     • Pila (Stack LIFO): Motor de Deshacer (Undo) instantáneo O(1).")
        print("     • Cola (Queue FIFO): Motor de Ingesta por lotes (Scraping/PDF/CSV).")
        print("")
        print("  2. MODELO DE MEDICIÓN MINCIENCIAS 2024:")
        print("     • 5 Macro-familias oficiales: GNC, DTI, ASC, DPC y FRH.")
        print("     • Cálculo del Índice de Producción Ponderada (IPP).")
        print("     • Detección oficial de aval en GrupLAC con chulo_1.jpg.")
        print("     • Hojas de vida CvLAC con Par Evaluador, Scholar y ORCID.")
        print("")
        print("  3. NAVEGACIÓN Y ATAJOS DE TECLADO:")
        print("     • Ingrese [0] en cualquier submenú para regresar al anterior.")
        print("     • En tablas largas: [S] siguiente, [A] anterior, [B] buscar.")
        print("     • Para copiar en terminal use Ctrl+Shift+C (evita interrumpir).")
        print("")
        print("  4. MODOS DE VISUALIZACIÓN GRÁFICA (GUI):")
        print("     • Opción 7: Portal Ejecutivo Web (dist/visualizador_hipercubo.html)")
        print("     • Opción 7 -> 2: Dashboard interactivo de 3 vistas (HTML5)")
        print("-----------------------------------------------------------------")
        self.pausar()

    # -----------------------------------------------------------------
    # INGESTA DE DATOS & WEB SCRAPING (TDA COLA FIFO)
    # -----------------------------------------------------------------
    def menu_ingesta(self):
        try:
            from python.core.ingesta import MotorIngesta
        except ImportError as e:
            self.limpiar_pantalla()
            print("=================================================================")
            print("  PEA-i UPC > Ingesta de Datos & Web Scraping (TDA Cola FIFO)    ")
            print("=================================================================")
            print("\n  [!] Módulo de scraping/PDF no disponible por falta de librerías.")
            print(f"      Detalle: {e}")
            print("\n  [i] Para habilitar esta función, instale los requisitos:")
            print("      pip install -r requirements.txt")
            print("-----------------------------------------------------------------")
            self.pausar()
            return

        op = -1
        while op != 0:
            self.limpiar_pantalla()
            print("=================================================================")
            print("  PEA-i UPC > Ingesta de Datos & Web Scraping (TDA Cola FIFO)    ")
            print("=================================================================")
            print("  1. Buscar Universidad / Institución en MinCiencias (Directorio Nacional)")
            print("  2. Explorar y Descargar Grupos de la UPC (66 Grupos Institucionales)")
            print("  3. Buscar Grupo por Nombre o Sigla en MinCiencias (ScienTI)")
            print("  4. Web Scraping de Grupo Directo (URL o Código nro MinCiencias)")
            print("  5. Ingesta Automática Masiva de Todos los Grupos UPC (GrupLAC + CvLACs)")
            print("  6. Web Scraping de Investigador Individual (CvLAC)")
            print("  7. Procesar Archivo CSV de Investigación (data/muestra_upc.csv)")
            print("  8. Procesar Archivo PDF de Producción Científica")
            print("  9. Auditoría Datos Abiertos Colombia (Socrata) & Catálogo 2024")
            print("  0. Anterior / Regresar al Menú Principal")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("0123456789", "Presione una opción [0-9]: ")

            motor = MotorIngesta(self.ruta_bd)

            if op == 1:
                self._subopcion_buscar_universidad(motor)
            elif op == 2:
                self._subopcion_explorar_upc(motor)
            elif op == 3:
                self._subopcion_buscar_grupo(motor)
            elif op == 4:
                self.limpiar_pantalla()
                print("=================================================================")
                print("--- WEB SCRAPING: GRUPO MINCIENCIAS (GrupLAC) ---")
                print("URL oficial del taller: Grupo GISICO (00000000002099)")
                print("[Presione ENTER para usar la URL oficial, o 0 para cancelar]")
                print("=================================================================")
                url = self.leer_linea("URL o NRO GrupLAC: ", permitir_vacio=True)
                if url == "0": continue
                if not url:
                    url = "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099"
                elif url.isdigit():
                    url = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={url}"
                import re as _re
                from python.core.ingesta import _buscar_snapshot_gruplac as _snap_g
                _m = _re.search(r"nro=(\d+)", url)
                if _m and _snap_g(_m.group(1)):
                    print(f"[i] Snapshot local disponible: scrape offline instantáneo.")
                else:
                    print(f"[i] Sin snapshot local: intentará descarga en vivo "
                          f"(MinCiencias responde en 10-30 s, sea paciente).")
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta("URL_GRUPLAC", url):
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                self.pausar()

            elif op == 5:
                self.limpiar_pantalla()
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta_automatica():
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                self.pausar()

            elif op == 6:
                self.limpiar_pantalla()
                print("=================================================================")
                print("--- WEB SCRAPING: INVESTIGADOR MINCIENCIAS (CvLAC) ---")
                print("URL oficial del taller: Ing. Adith Pérez (0000494917)")
                print("[Presione ENTER para usar la URL oficial, o 0 para cancelar]")
                print("=================================================================")
                url = self.leer_linea("URL o COD_RH CvLAC: ", permitir_vacio=True)
                if url == "0": continue
                if not url:
                    url = "https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000494917"
                elif url.isdigit():
                    url = f"https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh={url}"
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta("URL_CVLAC", url):
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                self.pausar()

            elif op == 7:
                self.limpiar_pantalla()
                print("=================================================================")
                print("--- PROCESAMIENTO DE ARCHIVO CSV ---")
                print("[Presione ENTER para usar 'data/muestra_upc.csv', o 0 para cancelar]")
                print("=================================================================")
                ruta = self.leer_linea("Ruta del archivo CSV: ", permitir_vacio=True)
                if ruta == "0": continue
                if not ruta:
                    ruta = "data/muestra_upc.csv"
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta("ARCHIVO_CSV", ruta):
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                self.pausar()

            elif op == 8:
                self.limpiar_pantalla()
                print("=================================================================")
                print("--- PROCESAMIENTO DE ARCHIVO PDF ---")
                print("[Presione ENTER para usar 'data/muestra_articulo.pdf', o 0 para cancelar]")
                print("=================================================================")
                ruta = self.leer_linea("Ruta del archivo PDF: ", permitir_vacio=True)
                if ruta == "0": continue
                if not ruta:
                    ruta = "data/muestra_articulo.pdf"
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta("ARCHIVO_PDF", ruta):
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                self.pausar()

            elif op == 9:
                self.limpiar_pantalla()
                print("=================================================================")
                print("--- DATOS ABIERTOS DE COLOMBIA (SOCRATA) & CATALOGO 2024 ---")
                print("=================================================================")
                from python.core.datos_abiertos import auditar_grupos_e_investigadores_locales
                stats_cat = CatalogoMinCiencias2024.obtener_estadisticas_catalogo()
                print(f"[Catalogo Oficial MinCiencias {stats_cat['version']} - Anexo 1]")
                print(f"  * Familias Oficiales:   {stats_cat['total_familias']}")
                print(f"  * Subtipos Oficiales:   {stats_cat['total_subtipos']}")
                print(f"  * Categorias de Peso:   {stats_cat['total_categorias']}")
                for f_code, f_info in stats_cat["por_familia"].items():
                    print(f"    - [{f_code}] {f_info['nombre']}: {f_info['subtipos']} subtipos ({f_info['categorias']} categorias)")
                aud = auditar_grupos_e_investigadores_locales(self.ruta_bd)
                print("\n[Auditoria Local Datos Abiertos / Scienti (Modo Offline Seguro)]")
                print(f"  * Grupos Activos Verificados:         {aud['total_grupos']}")
                print(f"  * Investigadores Activos Verificados: {aud['total_investigadores']}")
                print(f"  * Investigadores con CvLAC / ORCID:   {aud['investigadores_con_orcid_o_cvlac']}")
                print("  * Distribucion de Grupos por Clasificacion MinCiencias:")
                for c_k, c_v in aud["grupos_por_categoria"].items():
                    print(f"    - {c_k}: {c_v} grupo(s)")
                print("=================================================================")
                self.pausar()

    def _subopcion_buscar_universidad(self, motor):
        self.limpiar_pantalla()
        print("=================================================================")
        print("   BÚSQUEDA DE UNIVERSIDADES / INSTITUCIONES EN MINCIENCIAS     ")
        print("=================================================================")
        texto = self.leer_linea("Nombre o sigla a buscar (ej: Cesar, Andes, Valle, 947): ")
        if not texto or texto == "0":
            return
        from python.core.busqueda_scienti import buscar_universidad, obtener_grupos_institucion
        resultados = buscar_universidad(texto)
        if not resultados:
            print(f"\n[!] No se encontraron instituciones con el término '{texto}'.")
            self.pausar()
            return

        print(f"\nSe encontraron {len(resultados)} instituciones:")
        print(f"{'#':<4}{'CÓDIGO':<10}{'INSTITUCIÓN':<48}{'GRUPOS':<10}")
        print("-" * 74)
        for i, inst in enumerate(resultados[:25], 1):
            nom_c = inst.get("nombre", "")[:45]
            print(f"{i:<4}{inst.get('codinst',''):<10}{nom_c:<48}{inst.get('n_grupos',0):<10}")

        sel = self.leer_linea("\nSeleccione [#] para ver sus grupos (o ENTER para regresar): ", permitir_vacio=True)
        if sel.isdigit() and 1 <= int(sel) <= min(len(resultados), 25):
            inst_sel = resultados[int(sel) - 1]
            codinst = inst_sel.get("codinst", "")
            grupos = obtener_grupos_institucion(codinst, inst_sel.get("nombre", ""))
            print(f"\n--- GRUPOS DE: {inst_sel.get('nombre','')} ({len(grupos)} grupos) ---")
            for j, g in enumerate(grupos[:30], 1):
                print(f"  {j:02d}. [{g.get('nro','')}] {g.get('col','')} - {g.get('nombre','')[:48]} ({g.get('categoria','')})")

            sel_g = self.leer_linea("\nIngrese [#] de grupo para ingestar automáticamente (o 0 para omitir): ", permitir_vacio=True)
            if sel_g.isdigit() and 1 <= int(sel_g) <= min(len(grupos), 30):
                g_target = grupos[int(sel_g) - 1]
                nro = g_target.get("nro", "")
                if nro:
                    url = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={nro}"
                    print(f"\n[+] Ingestando grupo {g_target.get('nombre','')} (nro={nro})...")
                    self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                    if motor.ejecutar_ingesta("URL_GRUPLAC", url):
                        self.multi = Multilista()
                        GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
        self.pausar()

    def _subopcion_explorar_upc(self, motor):
        from python.core.busqueda_scienti import listar_grupos_upc
        grupos = listar_grupos_upc()
        if not grupos:
            print("\n[!] No se encontraron grupos de la UPC en el índice local.")
            self.pausar()
            return

        tam_pag = 15
        total_pags = (len(grupos) + tam_pag - 1) // tam_pag
        pag = 0

        while True:
            self.limpiar_pantalla()
            print("=========================================================================================")
            print(f"   GRUPOS INSTITUCIONALES UNIVERSIDAD POPULAR DEL CESAR (Página {pag + 1}/{total_pags})")
            print("=========================================================================================")
            print(f"{'#':<4}{'CÓDIGO':<12}{'NOMBRE DEL GRUPO':<45}{'LÍDER':<25}{'CATEGORÍA':<10}")
            print("-" * 98)

            inicio = pag * tam_pag
            fin = min(inicio + tam_pag, len(grupos))
            for i in range(inicio, fin):
                g = grupos[i]
                nom = g.get("nombre", "")[:42]
                lid = g.get("lider", "")[:23]
                print(f"{i + 1:<4}{g.get('col',''):<12}{nom:<45}{lid:<25}{g.get('estado',''):<10}")

            print("-----------------------------------------------------------------------------------------")
            print("Controles: [S]iguiente página | [A]nterior página | [1-66] Ingestar Grupo | [0] Regresar")
            cmd = self.leer_linea("Selección: ", permitir_vacio=True).upper()

            if cmd in ("0", ""):
                break
            elif cmd == "S" and pag + 1 < total_pags:
                pag += 1
            elif cmd == "A" and pag > 0:
                pag -= 1
            elif cmd.isdigit() and 1 <= int(cmd) <= len(grupos):
                idx = int(cmd) - 1
                g_sel = grupos[idx]
                nro = g_sel.get("nro", "")
                url = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={nro}"
                print(f"\n[+] Ingestando automáticamente grupo UPC: {g_sel.get('nombre','')} (nro={nro})...")
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta("URL_GRUPLAC", url):
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
                self.pausar()
                break

    def _subopcion_buscar_grupo(self, motor):
        self.limpiar_pantalla()
        print("=================================================================")
        print("       BÚSQUEDA DE GRUPOS EN MINCIENCIAS (ScienTI)               ")
        print("=================================================================")
        termino = self.leer_linea("Palabra clave a buscar (ej: GISICO, Biotecnología, Software, Patino): ")
        if not termino or termino == "0":
            return
        from python.core.busqueda_scienti import buscar_grupo_en_indices
        cands = buscar_grupo_en_indices(termino)
        if not cands:
            print(f"\n[!] No se encontraron grupos con el término '{termino}'.")
            self.pausar()
            return

        print(f"\nSe encontraron {len(cands)} grupos:")
        print(f"{'#':<4}{'CÓDIGO':<12}{'NOMBRE DEL GRUPO':<45}{'LÍDER':<25}")
        print("-" * 88)
        for i, g in enumerate(cands[:25], 1):
            nom = g.get("nombre", "")[:42]
            lid = g.get("lider", "")[:23]
            print(f"{i:<4}{g.get('col',''):<12}{nom:<45}{lid:<25}")

        sel = self.leer_linea("\nIngrese [#] para ingestar automáticamente el grupo (o ENTER para cancelar): ", permitir_vacio=True)
        if sel.isdigit() and 1 <= int(sel) <= min(len(cands), 25):
            g_sel = cands[int(sel) - 1]
            nro = g_sel.get("nro", "")
            if nro:
                url = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={nro}"
                print(f"\n[+] Ingestando grupo {g_sel.get('nombre','')} (nro={nro})...")
                self.guardar_ram_si_hay_datos("respaldo pre-ingesta")
                if motor.ejecutar_ingesta("URL_GRUPLAC", url):
                    self.multi = Multilista()
                    GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
        self.pausar()

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
            print("  7. Generar Informe PDF Institucional de Grupo (ReportLab)")
            print("  0. Anterior / Regresar al Menú Principal")
            print("-----------------------------------------------------------------")
            op = self.leer_opcion_menu("01234567", "Presione una opción [0-7]: ")

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
                print("=================================================================")
                print("--- CONSULTAR DETALLE DE GRUPO ---")
                print("Búsqueda por Código o Nombre (ej: COL0018706 o GISICO)")
                print("[Sugerencia: Presione ENTER para ver un ejemplo aleatorio, o 0 para regresar]")
                print("=================================================================")
                busqueda = self.leer_linea("Término de búsqueda: ", True)
                if busqueda == "0":
                    continue
                g = None
                if not busqueda:
                    g = self.multi.obtener_grupo_aleatorio()
                    if g:
                        print(f"\n[i] Mostrando ejemplo aleatorio: [{g.codigo_grupo}] {g.nombre}")
                else:
                    g = self.multi.buscar_grupo_por_texto(busqueda)

                if not g:
                    print(f"\n[!] No se encontró ningún grupo que coincida con '{busqueda}'.")
                else:
                    print("\n=================================================================")
                    print(f"DETALLE DEL GRUPO: {g.nombre}")
                    print(f"Código: {g.codigo_grupo} | Clasificación: {g.clasificacion}")
                    print(f"Líder: {g.lider} | Área: {espaciar(g.area_conocimiento)} | Año: {g.anio_creacion}")
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
                    g = self.multi.buscar_grupo(cod)
                    if g:
                        prev = f"nom={g.nombre};clas={g.clasificacion};area={g.area_conocimiento};lid={g.lider};anio={g.anio_creacion};act={int(g.activo)}"
                        if self.multi.eliminar_grupo(cod):
                            self.historial.push("ELIMINAR", "GRUPO", cod, prev)
                            print("\n[OK] Grupo y dependencias eliminados físicamente de memoria.")
                        else:
                            print("\n[!] Error al eliminar grupo.")
                    else:
                        print("\n[!] Grupo no encontrado.")
                else:
                    print("\n[+] Operación cancelada.")
                self.pausar()
            elif op == 7:
                self.menu_generar_informe_pdf()

    def menu_generar_informe_pdf(self, codigo_defecto: str = ""):
        from python.core.reporte_pdf import generar_informe_grupo_pdf
        self.limpiar_pantalla()
        print("=================================================================")
        print("     PEA-i UPC > GENERADOR DE INFORMES PDF (ESTILO GRUPLAC)      ")
        print("=================================================================")
        if not codigo_defecto:
            print("Grupos registrados en memoria:")
            g = self.multi.cabeza_grupos
            count = 0
            while g and count < 10:
                print(f"  • {g.codigo_grupo}: {g.nombre[:45]}")
                g = g.sig_grupo
                count += 1
            if count == 0:
                print("  (Consultando directamente la base de datos institucional)")
            print("-----------------------------------------------------------------")
            cod = self.leer_linea("Ingrese el código del grupo [ej. COL0018706 o COL0043834]: ", permitir_vacio=False)
        else:
            cod = codigo_defecto

        try:
            print(f"\n[+] Generando informe formal en PDF para {cod}...")
            ruta = generar_informe_grupo_pdf(cod, self.ruta_bd)
            print(f"\n[OK] ¡Informe institucional en PDF generado exitosamente!")
            print(f"     Archivo: {ruta}")
            print("     (Puede abrir este archivo con cualquier visor de PDF en su sistema)")
        except Exception as e:
            print(f"\n[!] Error al generar el informe PDF: {e}")
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
                print("=================================================================")
                print("--- CONSULTAR DETALLE DE INVESTIGADOR ---")
                print("Búsqueda por Documento/ID o Nombre (ej: 0000494917 o Adith)")
                print("[Sugerencia: Presione ENTER para ver un ejemplo aleatorio, o 0 para regresar]")
                print("=================================================================")
                busqueda = self.leer_linea("Término de búsqueda: ", True)
                if busqueda == "0":
                    continue
                inv = None
                if not busqueda:
                    inv = self.multi.obtener_investigador_aleatorio()
                    if inv:
                        print(f"\n[i] Mostrando ejemplo aleatorio: [{inv.documento_id}] {inv.nombre_completo}")
                else:
                    inv = self.multi.buscar_investigador_por_texto(busqueda)

                if not inv:
                    print(f"\n[!] No se encontró ningún investigador que coincida con '{busqueda}'.")
                else:
                    print("\n=================================================================")
                    print(f"INVESTIGADOR: {inv.nombre_completo}")
                    print(f"Documento: {inv.documento_id} | Categoría: {inv.categoria}")
                    print(f"Formación: {espaciar(inv.formacion_academica)} | Grupo: {inv.codigo_grupo}")
                    print(f"Estado: {'ACTIVO' if inv.activo else 'DESACTIVADO'}")

                    try:
                        import sqlite3
                        conn_p = sqlite3.connect(self.ruta_bd, timeout=3.0)
                        cur_p = conn_p.cursor()
                        cur_p.execute("SELECT par_evaluador, scholar_url, orcid FROM PerfilInvestigador WHERE documento_id = ?;", (inv.documento_id,))
                        row_p = cur_p.fetchone()
                        conn_p.close()
                        if row_p:
                            print("\n  -- Hoja de Vida CvLAC Oficial (MinCiencias) --")
                            print(f"  • Par Evaluador MinCiencias: [{'SÍ (Reconocido)' if row_p[0] == 'Si' else 'No'}]")
                            if row_p[1]: print(f"  • Google Scholar: {row_p[1]}")
                            if row_p[2]: print(f"  • Código ORCID:  {row_p[2]}")
                    except Exception:
                        pass

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
                    prev = f"nom={inv.nombre_completo};cat={inv.categoria};form={inv.formacion_academica}"
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
                    inv = self.multi.buscar_investigador(doc)
                    if inv:
                        prev = f"cod_g={inv.codigo_grupo};nom={inv.nombre_completo};cat={inv.categoria};form={inv.formacion_academica};act={int(inv.activo)}"
                        if self.multi.eliminar_investigador(doc):
                            self.historial.push("ELIMINAR", "INVESTIGADOR", doc, prev)
                            print("\n[OK] Investigador y sus productos eliminados de la memoria.")
                        else:
                            print("\n[!] Error al eliminar investigador.")
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
                # Recolectar productos para navegación paginada
                todos_prods = []
                g = self.multi.cabeza_grupos
                while g:
                    p = g.primer_producto
                    while p:
                        todos_prods.append(p)
                        p = p.sig_producto_grupo
                    g = g.sig_grupo

                if not todos_prods:
                    self.limpiar_pantalla()
                    print("\n  (No hay productos registrados en el sistema)")
                    self.pausar()
                    continue

                pagina = 0
                por_pagina = 12
                filtro_busqueda = ""

                while True:
                    self.limpiar_pantalla()
                    # Filtrar según búsqueda
                    filtrados = [
                        p for p in todos_prods
                        if not filtro_busqueda or
                        filtro_busqueda.lower() in p.titulo.lower() or
                        filtro_busqueda.lower() in p.id_producto.lower() or
                        filtro_busqueda.lower() in p.tipo.lower()
                    ]

                    total_filtrados = len(filtrados)
                    total_paginas = 1 if total_filtrados == 0 else (total_filtrados + por_pagina - 1) // por_pagina
                    if pagina >= total_paginas: pagina = total_paginas - 1

                    print("========================================================================================")
                    print("                         LISTADO DE PRODUCTOS CIENTÍFICOS (PAGINADO)                    ")
                    print("========================================================================================")
                    if filtro_busqueda:
                        print(f"  [Filtro activo: '{filtro_busqueda}' - Coincidencias: {total_filtrados}]")
                    print(f"{'ID':<15}{'TIPO':<12}{'TITULO':<36}{'AÑO':<6}{'CAT':<6}{'AVAL':<6}{'ESTADO':<8}")
                    print("-" * 88)

                    inicio = pagina * por_pagina
                    fin = min(inicio + por_pagina, total_filtrados)

                    if total_filtrados == 0:
                        print("  (No se encontraron productos con el filtro especificado)")
                    else:
                        for i in range(inicio, fin):
                            p = filtrados[i]
                            tit_corto = p.titulo[:33] + "..." if len(p.titulo) > 34 else p.titulo
                            val_str = "SI" if p.validado else "NO"
                            act_str = "[ACT]" if p.activo else "[INA]"
                            print(f"{p.id_producto:<15}{p.tipo:<12}{tit_corto:<36}{p.anio:<6}{p.categoria_minciencias:<6}{val_str:<6}{act_str:<8}")

                    print("========================================================================================")
                    print(f"  Página {pagina + 1} de {total_paginas} | Mostrando {0 if total_filtrados == 0 else inicio + 1}-{fin} de {total_filtrados} productos")
                    print("  [S] Siguiente | [A] Anterior | [B] Buscar | [T] Todos | [0] Regresar al Menú")
                    print("----------------------------------------------------------------------------------------")
                    t = self.leer_linea("Seleccione una opción [S/A/B/T/0] y presione ENTER: ", permitir_vacio=True).lower()
                    if t == '0':
                        break
                    elif t == 's':
                        if pagina + 1 < total_paginas: pagina += 1
                    elif t == 'a':
                        if pagina > 0: pagina -= 1
                    elif t == 'b':
                        filtro_busqueda = self.leer_linea("Texto a buscar (o ENTER para limpiar): ", permitir_vacio=True)
                        pagina = 0
                    elif t == 't':
                        filtro_busqueda = ""
                        pagina = 0
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
                print("=================================================================")
                print("--- CONSULTAR DETALLE DE PRODUCTO ---")
                print("Búsqueda por ID o Título (ej: PROD-001 o Hipercubo)")
                print("[Sugerencia: Presione ENTER para ver un ejemplo aleatorio, o 0 para regresar]")
                print("=================================================================")
                busqueda = self.leer_linea("Término de búsqueda: ", True)
                if busqueda == "0":
                    continue
                p = None
                if not busqueda:
                    p = self.multi.obtener_producto_aleatorio()
                    if p:
                        print(f"\n[i] Mostrando ejemplo aleatorio: [{p.id_producto}] {p.titulo}")
                else:
                    p = self.multi.buscar_producto_por_texto(busqueda)

                if not p:
                    print(f"\n[!] No se encontró ningún producto que coincida con '{busqueda}'.")
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
                    prev = f"tit={p.titulo};anio={p.anio};cat={p.categoria_minciencias};val={int(p.validado)}"
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
                    p = self.multi.buscar_producto(id_p)
                    if p:
                        prev = f"cod_g={p.codigo_grupo};id_inv={p.id_investigador};tipo={p.tipo};tit={p.titulo};anio={p.anio};cat={p.categoria_minciencias};val={int(p.validado)};act={int(p.activo)}"
                        if self.multi.eliminar_producto(id_p):
                            self.historial.push("ELIMINAR", "PRODUCTO", id_p, prev)
                            print("\n[OK] Producto desenlazado ortogonalmente y liberado de memoria.")
                        else:
                            print("\n[!] Error al eliminar producto.")
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
            self.guardar_ram_si_hay_datos("respaldo deshacer", forzar=True)

        elif acc.tipo_operacion == "CREAR":
            if acc.tipo_entidad == "GRUPO":
                self.multi.eliminar_grupo(acc.id_registro)
            elif acc.tipo_entidad == "INVESTIGADOR":
                self.multi.eliminar_investigador(acc.id_registro)
            elif acc.tipo_entidad == "PRODUCTO":
                self.multi.eliminar_producto(acc.id_registro)
            print("[OK] Inserción revertida (registro retirado de memoria).")
            self.guardar_ram_si_hay_datos("respaldo deshacer", forzar=True)

        elif acc.tipo_operacion == "MODIFICAR":
            campos = {}
            for part in acc.detalle_previo.split(";"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    campos[k.strip()] = v.strip()

            if acc.tipo_entidad == "GRUPO":
                g = self.multi.buscar_grupo(acc.id_registro)
                if g:
                    if "nom" in campos: g.nombre = campos["nom"]
                    if "clas" in campos: g.clasificacion = campos["clas"]
                    if "lid" in campos: g.lider = campos["lid"]
                    print(f"[OK] Grupo {acc.id_registro} restaurado a valores previos.")
                else:
                    print(f"[!] Grupo {acc.id_registro} no encontrado en memoria.")
            elif acc.tipo_entidad == "INVESTIGADOR":
                inv = self.multi.buscar_investigador(acc.id_registro)
                if inv:
                    if "nom" in campos: inv.nombre_completo = campos["nom"]
                    if "cat" in campos: inv.categoria = campos["cat"]
                    if "form" in campos: inv.formacion_academica = campos["form"]
                    print(f"[OK] Investigador {acc.id_registro} restaurado a valores previos.")
                else:
                    print(f"[!] Investigador {acc.id_registro} no encontrado en memoria.")
            elif acc.tipo_entidad == "PRODUCTO":
                p = self.multi.buscar_producto(acc.id_registro)
                if p:
                    if "tit" in campos: p.titulo = campos["tit"]
                    if "anio" in campos: p.anio = int(campos["anio"])
                    if "cat" in campos: p.categoria_minciencias = campos["cat"]
                    if "val" in campos: p.validado = (campos["val"] == "1" or campos["val"].lower() == "true")
                    print(f"[OK] Producto {acc.id_registro} restaurado a valores previos.")
                else:
                    print(f"[!] Producto {acc.id_registro} no encontrado en memoria.")
            self.guardar_ram_si_hay_datos("respaldo deshacer", forzar=True)

        elif acc.tipo_operacion == "ELIMINAR":
            campos = {}
            for part in acc.detalle_previo.split(";"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    campos[k.strip()] = v.strip()

            if acc.tipo_entidad == "GRUPO":
                nom = campos.get("nom", "Grupo Restaurado")
                clas = campos.get("clas", "Reconocido")
                area = campos.get("area", "General")
                lid = campos.get("lid", "Líder")
                anio = int(campos.get("anio", 2000))
                act = (campos.get("act", "1") == "1")
                if self.multi.insertar_grupo(acc.id_registro, nom, clas, area, lid, anio, act):
                    print(f"[OK] Grupo {acc.id_registro} reinsertado en la Multilista.")
                else:
                    print(f"[!] Error: no se pudo reinsertar grupo {acc.id_registro}.")
            elif acc.tipo_entidad == "INVESTIGADOR":
                cod_g = campos.get("cod_g", "")
                nom = campos.get("nom", "Investigador")
                cat = campos.get("cat", "Junior")
                form = campos.get("form", "Pregrado")
                act = (campos.get("act", "1") == "1")
                if self.multi.insertar_investigador(cod_g, acc.id_registro, nom, cat, form, act):
                    print(f"[OK] Investigador {acc.id_registro} reinsertado en la Multilista.")
                else:
                    print(f"[!] Error: no se pudo reinsertar investigador {acc.id_registro} (verifique grupo {cod_g}).")
            elif acc.tipo_entidad == "PRODUCTO":
                cod_g = campos.get("cod_g", "")
                id_inv = campos.get("id_inv", "")
                tipo = campos.get("tipo", "Articulo")
                tit = campos.get("tit", "Sin Titulo")
                anio = int(campos.get("anio", 2024))
                cat = campos.get("cat", "B")
                val = (campos.get("val", "1") == "1")
                act = (campos.get("act", "1") == "1")
                if self.multi.insertar_producto(cod_g, id_inv, acc.id_registro, tipo, tit, anio, cat, val, act):
                    print(f"[OK] Producto {acc.id_registro} reinsertado ortogonalmente en la Multilista.")
                else:
                    print(f"[!] Error: no se pudo reinsertar producto {acc.id_registro} (verifique grupo e investigador).")
            self.guardar_ram_si_hay_datos("respaldo deshacer", forzar=True)

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
        cat_a1 = cat_a2 = cat_a = cat_b = cat_c = validados = 0
        fam_gnc = fam_dti = fam_asc = fam_dpc = fam_frh = 0
        puntos_ponderados = 0

        g = self.multi.cabeza_grupos
        while g:
            p = g.primer_producto
            while p:
                if p.activo and g.activo:
                    info = CatalogoMinCiencias2024.clasificar_producto(getattr(p, 'subtipo_codigo', '') or p.tipo, p.categoria_minciencias, p.titulo)
                    f = getattr(p, 'familia', '') or info["familia"]
                    if f == "GNC": fam_gnc += 1
                    elif f == "DTI": fam_dti += 1
                    elif f == "ASC": fam_asc += 1
                    elif f == "DPC": fam_dpc += 1
                    elif f == "FRH": fam_frh += 1

                    if p.tipo == "Articulo": articulos += 1
                    elif p.tipo == "Libro": libros += 1
                    elif p.tipo == "Software": software += 1
                    elif p.tipo == "Capitulo": capitulos += 1
                    elif p.tipo == "Patente": patentes += 1

                    if p.categoria_minciencias == "A1": cat_a1 += 1
                    elif p.categoria_minciencias == "A2": cat_a2 += 1
                    elif p.categoria_minciencias == "A": cat_a += 1
                    elif p.categoria_minciencias == "B": cat_b += 1
                    elif p.categoria_minciencias == "C": cat_c += 1

                    peso_base = getattr(p, 'peso_calculado', 0.0)
                    if peso_base <= 0.0:
                        peso_base = float(info["global_weight"])
                    if p.validado:
                        validados += 1
                        puntos_ponderados += int(peso_base)
                    else:
                        puntos_ponderados += int(peso_base // 2)
                p = p.sig_producto_grupo
            g = g.sig_grupo

        print("\n--- Modelo MinCiencias 2024: 5 Familias Oficiales (Convocatoria 957) ---")
        print(f"  • [GNC] Generación Nuevo Conocimiento:   {fam_gnc} (Artículos, Libros, Capítulos, Patentes)")
        print(f"  • [DTI] Desarrollo Tecnológico e Innov.: {fam_dti} (Software, Diseños, Prototipos)")
        print(f"  • [ASC] Apropiación Social Conocimiento: {fam_asc} (Procesos CTeI e Innovación Social)")
        print(f"  • [DPC] Divulgación Pública Ciencia:    {fam_dpc} (Eventos, Talleres, Informes Técnicos)")
        print(f"  * [FRH] Formación Recurso Humano CTeI:   {fam_frh} (Tesis doctorales, Trabajos de Grado, APO)")
        print(f"  [IPP] Índice de Producción Ponderada:    {puntos_ponderados} pts MinCiencias")

        print("\n--- Desglose por Tipo Específico de Producto ---")
        print(f"  - Artículos científicos: {articulos}")
        print(f"  - Libros / Obras:        {libros}")
        print(f"  - Capítulos de libro:    {capitulos}")
        print(f"  - Desarrollos software:  {software}")
        print(f"  - Patentes registradas:  {patentes}")

        print("\n--- Calidad Editorial Publindex & Validación ---")
        cat_str = f"A1: {cat_a1}"
        if cat_a2 > 0: cat_str += f" | A2: {cat_a2}"
        cat_str += f" | A: {cat_a} | B: {cat_b} | C: {cat_c}"
        print(f"  - {cat_str}")
        porc = (validados * 100 // total_prod_act) if total_prod_act > 0 else 0
        print(f"  - Avalados por MinCiencias: {validados} ({porc}%)")

        print("\n-----------------------------------------------------------------")
        print("FILTRO POR VENTANA DE OBSERVACIÓN (Años MinCiencias)")
        print("  [1] Últimos 2 años (2024 - 2026)")
        print("  [2] Últimos 5 años (2021 - 2026)")
        print("  [3] Rango de años personalizado")
        print("  [4] Corte Oficial Modelo 2024 (5 años general / 10 años Libros y Patentes)")
        print("  [0] Anterior / Regresar al Menú Principal")
        print("-----------------------------------------------------------------")
        op_filtro = self.leer_opcion_menu("01234", "Presione opción [0-4]: ")

        es_modelo_2024 = False
        inicio, fin = 0, 9999
        if op_filtro == 1:
            inicio, fin = 2024, 2026
        elif op_filtro == 2:
            inicio, fin = 2021, 2026
        elif op_filtro == 3:
            inicio = self.leer_entero("Año inicial: ")
            fin = self.leer_entero("Año final: ")
        elif op_filtro == 4:
            es_modelo_2024 = True
            inicio, fin = 2017, 2026
        else:
            return

        if es_modelo_2024:
            prods_ventana = self.multi.contar_productos_modelo_2024(2026, True)
            print("\n[RESULTADO CORTE OFICIAL MODELO MINCIENCIAS 2024 (5/10 AÑOS)]")
        else:
            prods_ventana = self.multi.contar_productos_por_ventana(inicio, fin, True)
            print(f"\n[RESULTADO VENTANA {inicio} - {fin}]")
        print(f"Total de productos en la ventana: {prods_ventana}\n")
        print(f"{'ID':<12}{'AÑO':<6}{'TIPO':<12}{'TITULO':<35}{'GRUPO':<14}")
        print("-" * 79)

        g = self.multi.cabeza_grupos
        while g:
            p = g.primer_producto
            while p:
                cumple = self.multi.cumple_ventana_modelo_2024(p, 2026) if es_modelo_2024 else (inicio <= p.anio <= fin)
                if p.activo and g.activo and cumple:
                    tit_corto = p.titulo[:30] + "..." if len(p.titulo) > 33 else p.titulo
                    print(f"{p.id_producto:<12}{p.anio:<6}{p.tipo:<12}{tit_corto:<35}{p.codigo_grupo:<14}")
                p = p.sig_producto_grupo
            g = g.sig_grupo

        print("=================================================================")
        self.pausar()

    def guardar_ram_si_hay_datos(self, motivo: str = "respaldo", forzar: bool = False) -> bool:
        """Guarda la RAM en SQLite salvo que esté vacía (anti-wipe).

        `guardar_en_bd` hace DELETE+INSERT total: con RAM vacía borraría la BD.
        Los respaldos pre-ingesta se omiten si no hay datos; las mutaciones
        deliberadas (deshacer) usan forzar=True para persistir el vaciado real.
        """
        if not forzar and (self.multi.contar_grupos(False) == 0
                           and self.multi.contar_investigadores(False) == 0
                           and self.multi.contar_productos(False) == 0):
            print(f"[i] RAM vacía: se omite {motivo} para no borrar la BD.")
            return False
        return GestorPersistencia.guardar_en_bd(self.multi, self.ruta_bd)

    def guardar_en_bd(self):
        self.limpiar_pantalla()
        print("=================================================================")
        print("       PERSISTENCIA: GUARDAR DATOS EN SQLITE (data.db)           ")
        print("=================================================================")
        if (self.multi.contar_grupos(False) == 0
                and self.multi.contar_investigadores(False) == 0
                and self.multi.contar_productos(False) == 0):
            print("[AVISO] La memoria RAM está vacía: guardar ahora dejaría la BD vacía.")
        print("[+] Sincronizando Multilista en memoria con SQLite...")
        if GestorPersistencia.guardar_en_bd(self.multi, self.ruta_bd):
            print(f"[OK] Todos los registros fueron persistidos exitosamente en {self.ruta_bd}")
        else:
            print("[!] Error al guardar datos en SQLite.")
        self.pausar()
