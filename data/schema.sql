-- Base de Datos Relacional PEA-i (Programa Estadístico de Análisis de Investigación)
-- Universidad Popular del Cesar (UPC) — Estructura de Datos 2026-I

PRAGMA foreign_keys = ON;

-- 1. Tabla de Grupos de Investigación
CREATE TABLE IF NOT EXISTS Grupos (
    codigo_grupo VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    lider VARCHAR(255) NOT NULL,
    plan_investigacion TEXT NOT NULL,
    lineas_estrategicas TEXT NOT NULL,
    estado INTEGER DEFAULT 1 -- 1: Activo, 0: Desactivado
);

-- 2. Tabla de Investigadores
CREATE TABLE IF NOT EXISTS Investigadores (
    cod_rh VARCHAR(50) PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    correo VARCHAR(255) NOT NULL,
    categoria_minciencias VARCHAR(100) NOT NULL,
    cvlac_url TEXT NOT NULL,
    estado INTEGER DEFAULT 1 -- 1: Activo, 0: Desactivado
);

-- 3. Tabla de Productos de Investigación
CREATE TABLE IF NOT EXISTS Productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(500) NOT NULL,
    tipo_producto VARCHAR(100) NOT NULL, -- Artículo, Libro, Software, Patente
    categoria VARCHAR(50) NOT NULL,       -- A1, A, B, C, Reconocido
    estado_validacion VARCHAR(50) NOT NULL, -- Validado, Pendiente, Rechazado
    anio_publicacion INTEGER NOT NULL,
    codigo_grupo_fk VARCHAR(50) NOT NULL,
    cod_rh_investigador_fk VARCHAR(50) NOT NULL,
    estado INTEGER DEFAULT 1,             -- 1: Activo, 0: Desactivado
    FOREIGN KEY (codigo_grupo_fk) REFERENCES Grupos(codigo_grupo) ON DELETE CASCADE,
    FOREIGN KEY (cod_rh_investigador_fk) REFERENCES Investigadores(cod_rh) ON DELETE CASCADE
);

-- 4. Tabla de Adscripcion Investigador <-> Grupo (N:M)
-- Cada fila = un investigador adscrito a un grupo. Evita duplicar
-- investigadores en todos los grupos al cargar en RAM.
CREATE TABLE IF NOT EXISTS grupo_investigador (
    codigo_grupo_fk VARCHAR(50) NOT NULL,
    cod_rh_fk VARCHAR(50) NOT NULL,
    PRIMARY KEY (codigo_grupo_fk, cod_rh_fk),
    FOREIGN KEY (codigo_grupo_fk) REFERENCES Grupos(codigo_grupo) ON DELETE CASCADE,
    FOREIGN KEY (cod_rh_fk) REFERENCES Investigadores(cod_rh) ON DELETE CASCADE
);

-- 5. Tabla de Cache de Fuentes (ETag + hash SHA-256 + LRU; arquitectura S19)
-- url = URL exacta descargada (PK). sha256 = contenido (dedup: mismo hash = mismo byte).
-- etag/last_modified = validadores para 304 (SCIENTI hoy no los envia; se honran si aparecen).
-- ruta = snapshot vigente o zip del grupo. Solo GrupLAC guarda HTML; CvLAC vive en BD.
CREATE TABLE IF NOT EXISTS cache_fuentes (
    url TEXT PRIMARY KEY,
    sha256 VARCHAR(64) NOT NULL,
    etag TEXT DEFAULT '',
    last_modified TEXT DEFAULT '',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    ruta TEXT DEFAULT ''
);

-- 6. Tabla de Perfiles del Grupo (verPerfiles SCIENTI por convocatoria)
-- Guarda basicos (CCRG/COL, lider, programa) e indicadores por subtipo
-- (valor del grupo + cuartil). Fuente: verPerfiles.jsp (S28).
CREATE TABLE IF NOT EXISTS perfiles_grupo (
    codigo_grupo VARCHAR(50) NOT NULL,
    convocatoria VARCHAR(20) NOT NULL,
    seccion VARCHAR(120) NOT NULL,   -- integrantes | colaboracion | nuevo_conocimiento | des_tecnologico | apropiacion_social | formacion_rh | basicos
    subtipo VARCHAR(200) NOT NULL,
    abreviatura VARCHAR(20) DEFAULT '',
    valor_grupo VARCHAR(50) DEFAULT '',
    cuartil_grupo VARCHAR(10) DEFAULT '',
    PRIMARY KEY (codigo_grupo, convocatoria, seccion, subtipo),
    FOREIGN KEY (codigo_grupo) REFERENCES Grupos(codigo_grupo) ON DELETE CASCADE
);

-- 7. Tabla de Historial de Acciones (Soporte Undo LIFO)
CREATE TABLE IF NOT EXISTS HistorialAcciones (
    id_accion INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_operacion VARCHAR(50) NOT NULL, -- CREAR, EDITAR, DESACTIVAR, ELIMINAR
    entidad_afectada VARCHAR(50) NOT NULL, -- GRUPO, INVESTIGADOR, PRODUCTO
    json_datos TEXT NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. Hoja de vida CvLAC por investigador (S37, 1:1 con Investigadores)
CREATE TABLE IF NOT EXISTS perfil_investigador (
    cod_rh VARCHAR(50) PRIMARY KEY,
    par_evaluador VARCHAR(10) DEFAULT '',
    nombre_citaciones VARCHAR(255) DEFAULT '',
    nacionalidad VARCHAR(100) DEFAULT '',
    sexo VARCHAR(20) DEFAULT '',
    scholar_url TEXT DEFAULT '',
    orcid VARCHAR(100) DEFAULT '',
    formacion_academica TEXT DEFAULT '',
    formacion_complementaria TEXT DEFAULT '',
    experiencia TEXT DEFAULT '',
    areas TEXT DEFAULT '',
    idiomas VARCHAR(600) DEFAULT '',
    FOREIGN KEY (cod_rh) REFERENCES Investigadores(cod_rh) ON DELETE CASCADE
);
