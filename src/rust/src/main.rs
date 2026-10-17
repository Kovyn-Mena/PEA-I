// =====================================================================
// UNIVERSIDAD POPULAR DEL CESAR - FACULTAD DE INGENIERÍA Y TECNOLÓGICAS
// ASIGNATURA: ESTRUCTURA DE DATOS (TALLER 2) - 2026-I
// DOCENTE: ING. ADITH BISMARCK PÉREZ OROZCO
//
// MÓDULO COMPLEMENTARIO EN RUST (Punto 14.f - Complementos para 5.0)
// Archivo: src/rust/src/main.rs
// Propósito: Auditor de invariantes relacionales, integridad del Hipercubo 3D
//            y micro-benchmarking de alto rendimiento a nivel de microsegundos.
//
// Compilación:
//   cargo run --manifest-path src/rust/Cargo.toml            (auditoría real)
//   cargo run --manifest-path src/rust/Cargo.toml \
//       --no-default-features                                (modo sin SQLite)
// =====================================================================

use std::path::Path;
#[cfg(feature = "rusqlite")]
use std::time::Instant;

const DB_PATH: &str = "data/pea_investigacion.db";

fn main() {
    println!("\x1b[1;32m=================================================================\x1b[0m");
    println!("\x1b[1;32m      PEA-i: AUDITOR DE INVARIANTES Y BENCHMARK EN RUST (UPC)     \x1b[0m");
    println!("\x1b[1;32m               Punto 14.f - Complemento de Excelencia 5.0        \x1b[0m");
    println!("\x1b[1;32m=================================================================\x1b[0m");

    if !Path::new(DB_PATH).exists() {
        eprintln!("\x1b[1;31m[ERROR] No se encontró el archivo de base de datos: {}\x1b[0m", DB_PATH);
        eprintln!("Por favor ejecute primero 'python3 data/init_db.py' o 'make'.");
        std::process::exit(1);
    }

    println!("[RUST] Conectando a la persistencia: {}...", DB_PATH);

    #[cfg(feature = "rusqlite")]
    run_rusqlite_audit(DB_PATH);

    #[cfg(not(feature = "rusqlite"))]
    run_fallback_audit(DB_PATH);
}

/// Auditoría real contra SQLite. Ejecuta consultas de invariantes y
/// micro-benchmark. Sale con código 1 si algún invariante crítico falla.
#[cfg(feature = "rusqlite")]
fn run_rusqlite_audit(db_path: &str) {
    use rusqlite::Connection;

    let conn = match Connection::open(db_path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("\x1b[1;31m[ERROR] No se pudo abrir {}: {}\x1b[0m", db_path, e);
            std::process::exit(1);
        }
    };

    // helper: ejecuta un COUNT escalar
    let cuenta = |sql: &str| -> i64 {
        conn.query_row(sql, [], |r| r.get::<_, i64>(0)).unwrap_or(-1)
    };

    let t0 = Instant::now();
    let grupos = cuenta("SELECT COUNT(*) FROM Grupos");
    let grupos_act = cuenta("SELECT COUNT(*) FROM Grupos WHERE activo = 1");
    let inv = cuenta("SELECT COUNT(*) FROM Investigadores");
    let inv_act = cuenta("SELECT COUNT(*) FROM Investigadores WHERE activo = 1");
    let prod = cuenta("SELECT COUNT(*) FROM Productos");
    let prod_act = cuenta("SELECT COUNT(*) FROM Productos WHERE activo = 1");

    // Invariantes de integridad referencial (deben ser 0 huérfanos).
    let huerfanos_inv = cuenta(
        "SELECT COUNT(*) FROM Productos p \
         LEFT JOIN Investigadores i ON p.id_investigador = i.documento_id \
         WHERE i.documento_id IS NULL",
    );
    let huerfanos_grp = cuenta(
        "SELECT COUNT(*) FROM Productos p \
         LEFT JOIN Grupos g ON p.codigo_grupo = g.codigo_grupo \
         WHERE g.codigo_grupo IS NULL",
    );
    // Invariantes de dominio (valores fuera de catálogo).
    let fam_invalidas = cuenta(
        "SELECT COUNT(*) FROM Productos \
         WHERE familia NOT IN ('GNC','DTI','ASC','DPC','FRH','OTRO')",
    );
    let clas_invalidas = cuenta(
        "SELECT COUNT(*) FROM Grupos \
         WHERE clasificacion NOT IN ('A1','A','B','C','Reconocido','Sin Clasificacion')",
    );
    let cat_invalidas = cuenta(
        "SELECT COUNT(*) FROM Investigadores \
         WHERE categoria NOT IN ('Senior','Asociado','Junior','Sin Categoria')",
    );

    // Ventanas de observación (idénticas a C++/Python: solo activos y grupo activo).
    let ventana2 = cuenta(
        "SELECT COUNT(*) FROM Productos p JOIN Grupos g ON p.codigo_grupo = g.codigo_grupo \
         WHERE p.activo = 1 AND g.activo = 1 AND p.anio BETWEEN 2024 AND 2026",
    );
    let ventana5 = cuenta(
        "SELECT COUNT(*) FROM Productos p JOIN Grupos g ON p.codigo_grupo = g.codigo_grupo \
         WHERE p.activo = 1 AND g.activo = 1 AND p.anio BETWEEN 2021 AND 2026",
    );
    let modelo2024 = cuenta(
        "SELECT COUNT(*) FROM Productos p JOIN Grupos g ON p.codigo_grupo = g.codigo_grupo \
         WHERE p.activo = 1 AND g.activo = 1 AND p.anio BETWEEN \
         (CASE WHEN lower(p.tipo) LIKE '%libro%' OR lower(p.tipo) LIKE '%capitulo%' \
                    OR lower(p.tipo) LIKE '%capítulo%' OR lower(p.tipo) LIKE '%patente%' \
               THEN 2017 ELSE 2022 END) AND 2026",
    );
    let elapsed = t0.elapsed();

    println!("[RUST] Motor SQLite (rusqlite) activo. Benchmark de auditoría: {:?}", elapsed);

    println!("\n\x1b[1;36m+-------------------------------------------------------------+\x1b[0m");
    println!("\x1b[1;36m|             REPORTE DE INVARIANTES DEL HIPERCUBO            |\x1b[0m");
    println!("\x1b[1;36m+-------------------------------------------------------------+\x1b[0m");

    let mut fallos = 0usize;
    // (etiqueta, valor mostrado, aprobado)
    let mut check = |etiqueta: &str, valor: String, ok: bool| {
        let estado = if ok { "\x1b[1;32mAPROBADO\x1b[0m" } else { "\x1b[1;31mFALLIDO \x1b[0m" };
        if !ok {
            fallos += 1;
        }
        println!("| {:<45} : {} |", etiqueta, estado);
        if !valor.is_empty() {
            println!("|     -> {}", valor);
        }
    };

    check(
        "1. Integridad Referencial Producto<->Investigador",
        format!("{} huérfanos", huerfanos_inv),
        huerfanos_inv == 0,
    );
    check(
        "2. Integridad Referencial Producto<->Grupo",
        format!("{} huérfanos", huerfanos_grp),
        huerfanos_grp == 0,
    );
    check(
        "3. Dominio de Familia MinCiencias (Productos)",
        format!("{} fuera de catálogo", fam_invalidas),
        fam_invalidas == 0,
    );
    check(
        "4. Dominio de Clasificación (Grupos)",
        format!("{} fuera de catálogo", clas_invalidas),
        clas_invalidas == 0,
    );
    check(
        "5. Dominio de Categoría (Investigadores)",
        format!("{} fuera de catálogo", cat_invalidas),
        cat_invalidas == 0,
    );
    check(
        "6. Desactivación Lógica coherente (activos <= total)",
        format!("{} activos / {} total producto", prod_act, prod),
        prod_act <= prod && prod > 0,
    );
    println!("\x1b[1;36m+-------------------------------------------------------------+\x1b[0m");
    println!(
        "  Censo: {} grupos ({} activos) | {} investigadores ({} activos) | {} productos ({} activos)",
        grupos, grupos_act, inv, inv_act, prod, prod_act
    );
    println!(
        "  Ventanas: 2 años (2024-2026) = {} | 5 años (2021-2026) = {} | Modelo 2024 (5/10) = {}",
        ventana2, ventana5, modelo2024
    );
    println!("\x1b[1;36m+-------------------------------------------------------------+\x1b[0m");

    if fallos == 0 {
        println!("\x1b[1;32m[OK] Auditoría Rust finalizada: {} invariantes aprobados, 0 fallidos.\x1b[0m\n", 6);
    } else {
        println!("\x1b[1;31m[ALERTA] Auditoría Rust detectó {} invariante(s) FALLIDO(S).\x1b[0m\n", fallos);
        std::process::exit(1);
    }
}

/// Modo degradado sin SQLite (compilado con --no-default-features):
/// verifica únicamente la existencia y legibilidad del archivo. NO audita
/// invariantes; por eso se informa explícitamente en vez de simular un
/// resultado de aprobación.
#[cfg(not(feature = "rusqlite"))]
fn run_fallback_audit(db_path: &str) {
    println!("[RUST] Modo sin SQLite (--no-default-features): verificación básica de archivo.");

    let metadata = match std::fs::metadata(db_path) {
        Ok(m) => m,
        Err(e) => {
            eprintln!("\x1b[1;31m[ERROR] No se pudo leer metadatos de {}: {}\x1b[0m", db_path, e);
            std::process::exit(1);
        }
    };

    println!("  -> Archivo localizado: {} bytes ({:.2} KB)", metadata.len(), metadata.len() as f64 / 1024.0);
    println!("\x1b[1;33m[AVISO] Para ejecutar la auditoría REAL de invariantes compile con la");
    println!("        dependencia por defecto: cargo run --manifest-path src/rust/Cargo.toml\x1b[0m");
}
