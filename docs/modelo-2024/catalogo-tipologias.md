# Catálogo Oficial de Tipologías y Ponderación — MinCiencias 2024
**Universidad Popular del Cesar (UPC) — Facultad de Ingeniería y Tecnológicas**  
**Asignatura:** Estructura de Datos (2026-I) | **Docente:** Ing. Adith Bismarck Pérez Orozco  
**Documento Oficial:** Convocatoria Nacional 957 de 2024 / Anexo 1 del Modelo de Medición MinCiencias  

---

## 📌 1. Justificación de la Transición al Modelo 2024

En versiones antiguas del modelo (pre-2022), los sistemas académicos solían utilizar una clasificación rudimentaria de productos (*"Artículo, Libro, Software"*), asignándoles indiscriminadamente etiquetas como *"A1, A, B, C"*.

En el **Modelo de Medición de Grupos e Investigadores MinCiencias 2024 (Convocatoria 957)**, MinCiencias introdujo una arquitectura rigurosa:
1. **Separación de Tipologías en 5 Familias Oficiales:** Se separó formalmente la Apropiación Social del Conocimiento (**ASC**) de la Divulgación Pública de la Ciencia (**DPC**), consolidando 5 familias.
2. **Asignación de Clases de Medición (`measurement_class`):** Cada producto se clasifica en clases jerárquicas (ej. `GNC-A`, `GNC-B`, `DTI-A`, `FRH-A`, etc.).
3. **Matriz de Pesos Relativos y Globales:** Cada tipología aporta un peso de calidad (`weight`, escala 1 a 10) y un peso global (`global_weight`, escala 10 a 100) en la fórmula de cohesión del grupo.

---

## 🏛️ 2. Las 5 Familias Oficiales MinCiencias 2024

| Familia | Nombre Oficial | Descripción y Ámbito MinCiencias | Subtipos |
| :---: | :--- | :--- | :---: |
| **GNC** | **Generación de Nuevo Conocimiento** | Aporte original al estado del arte: artículos indexados en Publindex/Scopus, libros de investigación, capítulos y patentes. | 10 |
| **DTI** | **Desarrollo Tecnológico e Innovación** | Desarrollos técnicos y soluciones prácticas: software registrado, prototipos industriales, diseños y regulaciones técnicas. | 26 |
| **ASC** | **Apropiación Social del Conocimiento** | Procesos de ciencia comunitaria, innovación social participativa y redes de conocimiento con impacto territorial. | 4 |
| **DPC** | **Divulgación Pública de la Ciencia** | Comunicación pública: conferencias, ponencias en eventos científicos, talleres especializados y documentos de trabajo. | 21 |
| **FRH** | **Formación de Recurso Humano** | Dirección de tesis doctorales, trabajos de grado de maestría/pregrado y asesorías de semilleros y Programa Ondas (`APO`). | 9 |

---

## 📊 3. Matriz Detallada de Subtipos, Referencias y Ponderaciones (Tabla 6 MinCiencias)

### 3.1 Familia GNC: Generación de Nuevo Conocimiento
| Código 2024 | Tipología Oficial MinCiencias | Ref. Modelo | Clase | Peso Relativo | Peso Global |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `ART_A1` | Artículo en revista científica indexada A1 (Q1) | 2.2.1.1.1 | GNC-A | 10 | 100 |
| `ART_A2` | Artículo en revista científica indexada A2 (Q2) | 2.2.1.1.2 | GNC-A | 8 | 80 |
| `ART_B` | Artículo en revista científica indexada B (Q3) | 2.2.1.1.3 | GNC-B | 6 | 60 |
| `ART_C` | Artículo en revista científica indexada C (Q4) | 2.2.1.1.4 | GNC-B | 4 | 40 |
| `LIB_A` | Libro de investigación evaluado por pares A | 2.2.1.2.1 | GNC-A | 10 | 100 |
| `LIB_B` | Libro de investigación evaluado por pares B | 2.2.1.2.2 | GNC-B | 7 | 70 |
| `CAP_LIB_A`| Capítulo en libro de investigación A | 2.2.1.3.1 | GNC-A | 5 | 50 |
| `CAP_LIB_B`| Capítulo en libro de investigación B | 2.2.1.3.2 | GNC-B | 3 | 30 |
| `PAT_INV` | Patente de invención otorgada | 2.2.1.4.1 | GNC-A | 10 | 100 |
| `PAT_UTI` | Patente de modelo de utilidad o variedad vegetal | 2.2.1.5.1 | GNC-B | 6 | 60 |

### 3.2 Familia DTI: Desarrollo Tecnológico e Innovación
| Código 2024 | Tipología Oficial MinCiencias | Ref. Modelo | Clase | Peso Relativo | Peso Global |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `SOFT_REG` | Software con soporte lógico ante DNDA | 2.2.2.1.1 | DTI-A | 9 | 90 |
| `SOFT_VALID`| Software/plataforma con contrato de validación | 2.2.2.1.2 | DTI-B | 7 | 70 |
| `PROT_IND` | Prototipo industrial / Planta piloto comercial | 2.2.2.2.1 | DTI-A | 8 | 80 |
| `DIS_IND` | Diseño industrial con registro oficial | 2.2.2.3.1 | DTI-A | 8 | 80 |
| `SEC_EMP` | Secreto empresarial documentado | 2.2.2.4.1 | DTI-B | 7 | 70 |
| `REG_TECN` | Regulación o norma técnica adoptada | 2.2.2.5.1 | DTI-A | 8 | 80 |
| `SPIN_OFF` | Empresa de base tecnológica Spin-off/Start-up | 2.2.2.7.1 | DTI-A | 10 | 100 |
| `LIC_TECN` | Contrato de licenciamiento y transferencia | 2.2.2.8.1 | DTI-A | 9 | 90 |

### 3.3 Familia FRH: Formación de Recurso Humano
| Código 2024 | Tipología Oficial MinCiencias | Ref. Modelo | Clase | Peso Relativo | Peso Global |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TES_DOC` | Tesis de Doctorado sustentada y aprobada | 2.2.4.1.1 | FRH-A | 10 | 100 |
| `TGM` | Trabajo de Grado de Maestría sustentado | 2.2.4.2.1 | FRH-A | 7 | 70 |
| `TGP` | Trabajo de Grado de Pregrado sustentado | 2.2.4.3.1 | FRH-B | 4 | 40 |
| `APO` | Acompañamiento Programa Ondas (MinCiencias) | 2.2.4.7.1 | FRH-B | 5 | 30 |
| `JOV_INV` | Tutoría de Joven Investigador MinCiencias | 2.2.4.4.1 | FRH-A | 6 | 60 |
| `PASANTIA` | Dirección de pasantía de investigación CTeI | 2.2.4.5.1 | FRH-B | 3 | 30 |

### 3.4 Familia ASC y DPC: Apropiación y Divulgación
| Código 2024 | Tipología Oficial MinCiencias | Familia | Clase | Peso Relativo | Peso Global |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `PROC_ASC` | Proceso de Apropiación Social de la CTeI | ASC | ASC-A | 8 | 80 |
| `INNOV_SOC`| Proyecto de Innovación Social Territorial | ASC | ASC-A | 9 | 90 |
| `EVT_INT` | Ponencia en Evento Científico Internacional | DPC | DPC-A | 6 | 60 |
| `EVT_NAC` | Ponencia en Evento Científico Nacional | DPC | DPC-B | 4 | 40 |
| `DOC_TRAB` | Documento de Trabajo / Informe Técnico Final | DPC | DPC-B | 5 | 50 |
| `TALLER_CTEI`| Taller especializado de difusión científica | DPC | DPC-B | 4 | 40 |

---

## 🧮 4. Fórmula Matemática del Índice de Producción Ponderada (IPP)

Para evaluar con objetividad la producción científica de los grupos de investigación de la UPC, el sistema implementa la ecuación de ponderación institucional:

$$\text{IPP} = \sum_{i=1}^{N} \left( W_{\text{global}}(P_i) \times \mathbb{I}_{\text{validado}}(P_i) \times \mathbb{I}_{\text{activo}}(P_i) \right)$$

Donde:
* $P_i$ es el $i$-ésimo producto en la Multilista Ortogonal.
* $W_{\text{global}}(P_i)$ es el peso global en el Modelo MinCiencias 2024.
* $\mathbb{I}_{\text{validado}} \in \{0, 1\}$ indica si el producto cuenta con Aval Institucional.
* $\mathbb{I}_{\text{activo}} \in \{0, 1\}$ garantiza el invariante de borrado lógico (excluyendo productos desactivados).
