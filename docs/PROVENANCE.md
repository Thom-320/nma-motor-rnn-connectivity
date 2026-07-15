# Procedencia del modelo y materiales

## Fuentes principales

- [babaf/neural-manifold-and-plasticity](https://github.com/babaf/neural-manifold-and-plasticity): código original asociado con Feulner & Clopath. Una instantánea local, fuera de Git, está en `vendor/feulner-clopath-original/`.
- [steevelaquitaine/neural-manifold-and-plasticity](https://github.com/steevelaquitaine/neural-manifold-and-plasticity): material limpiado para el proyecto NMA y origen de la plantilla Motor RNN.
- [NMA Behavior and Theory projects](https://compneuro.neuromatch.io/projects/behavior_and_theory/README.html): mapa de preguntas Q1–Q9 y contexto pedagógico.

## Qué se reutiliza

El proyecto conserva la tarea de alcance, la arquitectura rate-RNN y la lógica de aprendizaje recurrente del material de Feulner–Clopath/NMA. El pipeline en `src/` añade el diseño pareado entre densidades, evaluación held-out con decoder fijo, métricas de manifold ordenadas, metadatos reproducibles, tablas tidy y pruebas.

## Bases de modelos

ModelDB, Open Source Brain, BioModels, CRCNS e INCF son recursos útiles para buscar modelos o datos alternativos. No son dependencias necesarias aquí: ya existe un modelo publicado, código fuente y una plantilla NMA directamente alineados con la pregunta. Consultarlas tendría sentido si el equipo cambiara de modelo o necesitara una validación externa.

## Licencias y artículos

El código vendorizado conserva su licencia. El código nuevo del repositorio usa BSD-3-Clause. Los PDFs completos se mantienen fuera del control de versiones; `literature/README.md` proporciona DOI y enlaces de acceso.
