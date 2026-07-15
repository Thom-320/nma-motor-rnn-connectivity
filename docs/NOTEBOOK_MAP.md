# Mapa de notebooks

| Notebook | Papel | Estado | ¿Usar para resultados finales? |
|---|---|---|---|
| `00_nma_original_motor_rnns.ipynb` | Plantilla NMA/Feulner–Clopath | Referencia sin modificar | No |
| `01_q1_q2_exploration.ipynb` | Copia del equipo con Q1 y primeras pruebas de Q2 | Histórico; contiene problemas metodológicos conocidos | No |
| `02_q2_connectivity_experiment.ipynb` | Pipeline pareado, evaluación held-out, tablas y figuras | Análisis principal | Sí |
| `archive/2026-07-13_q1_q2_exploration_earlier.ipynb` | Versión anterior de la copia | Archivo local | No |

## Qué aprender de cada uno

- El notebook 00 explica la arquitectura y el flujo del modelo base.
- El notebook 01 documenta cómo el equipo resolvió Q1 y empezó Q2; es valioso como cuaderno de laboratorio.
- El notebook 02 es la fuente reproducible para afirmaciones, figuras y tablas.

El código generalizable debe modificarse en `src/nma_motor_rnn/connectivity.py`. Así se puede revisar con `git diff` y probar sin depender del estado de una sesión de Colab.
