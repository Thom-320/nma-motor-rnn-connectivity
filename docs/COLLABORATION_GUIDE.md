# GitHub + Colab para dos integrantes

## Modelo de colaboración

GitHub será la fuente de verdad; Colab será el entorno de ejecución. Cada integrante clona el repositorio dentro de Colab, trabaja en una rama, descarga o hace push de cambios y abre un Pull Request.

## Primera configuración

1. Crear un repositorio privado llamado `nma-motor-rnn-connectivity`.
2. Invitar a la otra persona en **Settings → Collaborators**.
3. Proteger `main` para requerir Pull Request y una revisión.
4. Publicar esta copia local como primer commit.

No se deben subir tokens, credenciales ni PDFs editoriales.

## Abrir el notebook

Una vez publicado:

```text
https://colab.research.google.com/github/Thom-320/nma-motor-rnn-connectivity/blob/main/notebooks/02_q2_connectivity_experiment.ipynb
```

Para solo ejecutar, basta abrir el enlace y correr las celdas. Para guardar cambios duraderos, usar **File → Save a copy in GitHub**, seleccionar una rama propia y escribir un mensaje claro. Colab puede guardar el notebook, pero los cambios de módulos Python se manejan mejor con un clon y Git.

## Flujo con clon dentro de Colab

```python
!git clone https://github.com/Thom-320/nma-motor-rnn-connectivity.git
%cd nma-motor-rnn-connectivity
!git switch -c nombre/tarea
!pip install -e .
```

Para autenticar un push desde Colab se necesitaría un token personal; es más seguro descargar los archivos modificados o usar **Save a copy in GitHub** que pegar credenciales en celdas. Nunca guardar un token dentro del notebook.

## Reparto que evita conflictos

- Persona 1: literatura, texto científico y revisión de `docs/`.
- Persona 2: funciones y pruebas en `src/` y `tests/`.
- Ambos: revisar resultados y aprobar Pull Requests.
- Solo una persona edita `02_q2_connectivity_experiment.ipynb` a la vez.

Para una nueva idea, abrir primero un issue con: pregunta, cambio propuesto, métrica, archivos que se tocarán y condición de terminado.

## Regla de revisión

Un Pull Request científico debe indicar:

- qué afirmación o bug cambia;
- si el cambio estaba planeado o es exploratorio;
- qué prueba se ejecutó;
- si modifica resultados existentes;
- una captura o enlace a la figura, cuando corresponda.
