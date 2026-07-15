# NMA Motor-RNN Connectivity

Proyecto de Neuromatch Academy sobre cómo la probabilidad de conexión recurrente afecta el aprendizaje held-out de una tarea de alcance *center-out* de seis direcciones.

> **Pregunta principal:** bajo una inicialización normalizada por varianza y una regla fija de aprendizaje recurrente, ¿cómo afecta la probabilidad de conexión recurrente \(p\) al aprendizaje held-out?

La dimensionalidad del manifold neural se analiza como explicación exploratoria, no como mecanismo confirmado.

## Estado actual

- **Q1 — completada como reproducción:** el notebook original entrena la RNN y grafica la pérdida online. Esa curva no es por sí sola una medida held-out.
- **Q2 — exploración histórica conservada:** la copia de trabajo ensayó varias densidades, pero mezclaba pérdida online, aleatoriedad no pareada y un decoder PCA reajustado.
- **Q2 — experimento corregido completado:** usa un decoder motor fijo, evaluación sin aprendizaje, ensayos balanceados y ocho semillas pareadas.

Resultado principal en \(N=200\): \(p=0.05\) tuvo mayor NMSE final que el promedio de \(p\in\{0.10,0.20,0.40\}\) en 8/8 semillas. La hipótesis de rendimientos decrecientes no recibió apoyo consistente. Véase [PROJECT_STATUS.md](docs/PROJECT_STATUS.md).

## Mapa del repositorio

```text
notebooks/
  00_nma_original_motor_rnns.ipynb       # plantilla original / Q1
  01_q1_q2_exploration.ipynb             # copia del equipo, archivo histórico
  02_q2_connectivity_experiment.ipynb     # análisis reproducible actual
src/nma_motor_rnn/connectivity.py         # modelo y análisis reutilizable
tests/test_connectivity.py                # controles científicos y de reproducibilidad
docs/                                     # estado, literatura y guías del equipo
literature/                               # índice y BibTeX; PDFs locales ignorados por git
results/pilot/                            # piloto N=100, 3 semillas
results/primary/                          # experimento N=200, 8 semillas
```

El detalle de qué notebook usar está en [NOTEBOOK_MAP.md](docs/NOTEBOOK_MAP.md).

## Abrir en Colab

Cuando el repositorio remoto esté publicado, abre el notebook principal con:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Thom-320/nma-motor-rnn-connectivity/blob/main/notebooks/02_q2_connectivity_experiment.ipynb)

Hasta entonces, puede ejecutarse localmente desde la raíz del repositorio. El notebook busca automáticamente el paquete en `src/`.

## Instalación y verificación local

Requiere Python 3.10 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
python3 -m json.tool notebooks/02_q2_connectivity_experiment.ipynb > /dev/null
```

## Trabajo colaborativo

Cada integrante debe trabajar en una rama y abrir un Pull Request; no conviene editar directamente `main`. Las instrucciones completas, incluyendo Colab, están en [COLLABORATION_GUIDE.md](docs/COLLABORATION_GUIDE.md) y las reglas para contribuir en [CONTRIBUTING.md](CONTRIBUTING.md).

## Literatura y documentación

- [Revisión de literatura y propuesta](docs/LITERATURE_REVIEW.md)
- [Inventario de artículos y enlaces legales](literature/README.md)
- [Checklist de entregables NMA](docs/DOCUMENTATION_CHECKLIST.md)
- [Guía/sistema de proyecto NMA](docs/reference/NMA_PROJECT_GUIDE.md)
- [Procedencia de repositorios y código](docs/PROVENANCE.md)

Los seis PDFs verificados están disponibles en `literature/pdfs/` en esta copia local, con nombres normalizados. Esa carpeta no se publica en GitHub; el repositorio comparte citas, DOI y enlaces abiertos.

La copia local también conserva el código original en `vendor/`, pero GitHub enlazará al repositorio de sus autores en lugar de duplicarlo.

## Límite de interpretación

Todas las conexiones recurrentes existentes son plásticas. Por eso el resultado compara arquitecturas completas dependientes de la densidad y no separa densidad estructural del número de parámetros plásticos. Tampoco demuestra un umbral crítico ni que la dimensionalidad cause el cambio de desempeño.
