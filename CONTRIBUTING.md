# Contributing

Este repositorio está diseñado para que el equipo trabaje con GitHub y Colab sin sobrescribir el trabajo de otras personas.

## Flujo recomendado

1. Sincroniza `main` y crea una rama corta:

   ```bash
   git switch main
   git pull --ff-only
   git switch -c nombre/tarea-breve
   ```

2. Haz un cambio acotado. Evita modificar el mismo notebook que otra persona al mismo tiempo.
3. Ejecuta las pruebas:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 -m json.tool notebooks/02_q2_connectivity_experiment.ipynb > /dev/null
   ```

4. Revisa exactamente qué vas a guardar:

   ```bash
   git status
   git diff --stat
   ```

5. Haz commit y publica la rama:

   ```bash
   git add <archivos>
   git commit -m "Describe brevemente el cambio"
   git push -u origin HEAD
   ```

6. Abre un Pull Request y pide revisión a la otra persona.

## Convenciones científicas

- Una semilla de red es una réplica; los ensayos de una misma red no son réplicas independientes.
- No reemplazar el decoder motor fijo por un decoder PCA reajustado para medir desempeño primario.
- Separar siempre `online_feedback_loss` de `heldout_nmse`.
- No cambiar hipótesis, semillas o métricas después de mirar resultados sin documentarlo como exploratorio.
- No eliminar resultados nulos o contradictorios; el piloto \(N=100\) forma parte del registro.
- No hacer commit de PDFs completos. Añadir DOI, URL y BibTeX a `literature/`.

## Notebooks

Los notebooks producen conflictos difíciles de resolver. Antes de editar uno, abre un issue o avisa al equipo. Al terminar, reinicia el runtime y ejecuta todas las celdas en orden. Los cambios reutilizables deben ir en `src/nma_motor_rnn/`; el notebook debe orquestarlos y explicarlos.
