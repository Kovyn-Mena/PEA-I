# Módulo Complementario en Rust — PEA-i (Punto 14.f)
**Universidad Popular del Cesar (UPC) — Taller 2 Estructura de Datos**  
**Docente:** Ing. Adith Pérez  
**Estudiante:** Kovyn B. Mena (`kbmena@unicesar.edu.co`)

---

## 🎯 Propósito
Este módulo complementario cumple con el **Punto 14.f ("¿Rust?")** de la guía del taller para optar por la calificación máxima (5.0 / 5.0).

Implementa:
1. **Auditoría de Invariantes del Hipercubo 3D:** Valida la integridad referencial ortogonal entre Grupos, Investigadores y Productos.
2. **Verificación de Invariantes de Borrado Lógico vs. Físico:** Comprueba que los nodos desactivados permanezcan en la estructura sin romper los punteros ni contaminar los reportes activos.
3. **Micro-benchmarking a nivel de microsegundos ($\mu$s):** Evalúa la velocidad de lectura y consistencia del archivo SQLite (`pea_investigacion.db`).

---

## 🚀 Compilación y Ejecución

Si tienes el compilador de Rust (`cargo`) instalado:

```bash
cd src/rust
cargo run --release
```

O desde la raíz del proyecto si configuras el target en el Makefile:
```bash
cargo run --manifest-path src/rust/Cargo.toml
```
