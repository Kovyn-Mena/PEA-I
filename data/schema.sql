-- =====================================================================
-- PEA-i (Programa Estadístico de Análisis de Investigación)
-- Esquema Relacional de Base de Datos SQLite (Contrato C++ <-> Python)
-- =====================================================================

PRAGMA foreign_keys = ON;

-- 1. Tabla de Grupos de Investigación
CREATE TABLE IF NOT EXISTS Grupos (
    codigo_grupo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    clasificacion TEXT CHECK(clasificacion IN ('A1', 'A', 'B', 'C', 'Reconocido', 'Sin Clasificacion')),
    area_conocimiento TEXT NOT NULL,
    lider TEXT NOT NULL,
    anio_creacion INTEGER NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 -- 1: Activo, 0: Desactivado (Borrado Lógico)
);

-- 2. Tabla de Investigadores
CREATE TABLE IF NOT EXISTS Investigadores (
    documento_id TEXT PRIMARY KEY,
    nombre_completo TEXT NOT NULL,
    categoria TEXT CHECK(categoria IN ('Senior', 'Asociado', 'Junior', 'Sin Categoria')),
    formacion_academica TEXT NOT NULL,
    codigo_grupo TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1, -- 1: Activo, 0: Desactivado
    FOREIGN KEY (codigo_grupo) REFERENCES Grupos(codigo_grupo) ON DELETE CASCADE
);

-- 3. Tabla de Productos de Investigación
CREATE TABLE IF NOT EXISTS Productos (
    id_producto TEXT PRIMARY KEY,
    tipo TEXT NOT NULL CHECK(tipo IN ('Articulo', 'Libro', 'Capitulo', 'Software', 'Patente', 'Trabajo de Grado')),
    titulo TEXT NOT NULL,
    anio INTEGER NOT NULL,
    categoria_minciencias TEXT NOT NULL DEFAULT 'A1',
    validado INTEGER NOT NULL DEFAULT 0, -- 1: Validado por MinCiencias, 0: No validado
    codigo_grupo TEXT NOT NULL,
    id_investigador TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1, -- 1: Activo, 0: Desactivado
    FOREIGN KEY (codigo_grupo) REFERENCES Grupos(codigo_grupo) ON DELETE CASCADE,
    FOREIGN KEY (id_investigador) REFERENCES Investigadores(documento_id) ON DELETE CASCADE
);

-- 4. Tabla de Auditoría / Historial de Acciones (Soporte complementario a la Pila)
CREATE TABLE IF NOT EXISTS HistorialAcciones (
    id_accion INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_operacion TEXT NOT NULL, -- CREAR, MODIFICAR, DESACTIVAR, ELIMINAR
    entidad_afectada TEXT NOT NULL, -- GRUPO, INVESTIGADOR, PRODUCTO
    id_registro TEXT NOT NULL,
    detalles TEXT,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar búsquedas y filtrados por año/grupo
CREATE INDEX IF NOT EXISTS idx_productos_anio ON Productos(anio);
CREATE INDEX IF NOT EXISTS idx_productos_grupo ON Productos(codigo_grupo);
CREATE INDEX IF NOT EXISTS idx_investigadores_grupo ON Investigadores(codigo_grupo);
