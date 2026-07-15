# Inventario de literatura

Se verificaron visualmente las primeras páginas y los metadatos de los seis PDFs locales. Los nombres fueron normalizados. `pdfs/` está ignorado por Git para no redistribuir copias editoriales; el equipo debe usar los DOI o enlaces abiertos siguientes.

| Papel en el proyecto | Referencia | Archivo local verificado | Acceso |
|---|---|---|---|
| Modelo base y plasticidad recurrente | Feulner & Clopath (2021) | `feulner_clopath_2021_neural_manifold_plasticity.pdf` | [PLOS, acceso abierto](https://doi.org/10.1371/journal.pcbi.1008621) |
| FORCE/RLS | Sussillo & Abbott (2009) | `sussillo_abbott_2009_force_learning.pdf` | [DOI](https://doi.org/10.1016/j.neuron.2009.07.018) |
| Reservoirs dispersos | Jaeger & Haas (2004) | `jaeger_haas_2004_echo_state_networks.pdf` | [DOI](https://doi.org/10.1126/science.1091277) |
| Conectividad y manifolds | Wärnberg & Kumar (2019) | `waernberg_kumar_2019_low_dimensional_manifolds.pdf` | [PLOS, acceso abierto](https://doi.org/10.1371/journal.pcbi.1007074) |
| Complejidad/dimensionalidad | Gao et al. (2017) | `gao_etal_2017_neural_task_complexity_biorxiv.pdf` | [bioRxiv](https://doi.org/10.1101/214262) |
| Puente: RNNs dispersas | Khona et al. (2022/2023) | `khona_etal_2022_sparse_rnns_arxiv.pdf` | [arXiv](https://arxiv.org/abs/2207.03523) |

## ¿Está toda la literatura necesaria?

Sí, para la pregunta congelada están los cinco trabajos centrales solicitados por la plantilla y el artículo puente sobre RNNs dispersas. No hace falta buscar una base de datos adicional de modelos para ejecutar este proyecto: la implementación base y su código original ya están incluidos en `vendor/`.

Para la escritura metodológica también son útiles, sin necesidad de almacenar otro PDF:

- Blohm, Kording & Schrater, *A How-to-Model Guide for Neuroscience*.
- Mensh & Kording, *Ten simple rules for structuring papers*.

Si el equipo amplía la pregunta a presupuesto fijo de plasticidad, tamaño de red o complejidad de tarea, deberá hacer una búsqueda nueva antes de interpretar esos análisis.

## Duplicados detectados

- Había dos copias idénticas del artículo de Feulner & Clopath; una quedó en `archive/duplicates/` local.
- Había dos copias del prompt/guía NMA; la copia redundante también quedó archivada localmente.
