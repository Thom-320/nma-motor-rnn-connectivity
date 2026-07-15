# Estado científico del proyecto

## Pregunta congelada

**Bajo una inicialización normalizada por varianza y una regla fija de aprendizaje recurrente, ¿cómo afecta la probabilidad de conexión recurrente \(p\) al aprendizaje held-out de una tarea de alcance center-out de seis direcciones?**

Pregunta secundaria exploratoria: ¿las diferencias de desempeño asociadas con la densidad están acompañadas por cambios en la dimensionalidad del manifold neural evocado por la tarea?

## Q1: reproducción del modelo

Q1 pedía entrenar la RNN durante aproximadamente 50 ensayos, graficar la pérdida y discutir convergencia. Está **operativamente resuelta** en `notebooks/01_q1_q2_exploration.ipynb`: el modelo se entrena y se muestra `reaching_loss`.

La interpretación tiene un límite: esa pérdida se calcula durante aprendizaje recurrente online, con objetivos y estados iniciales variables. No es una curva held-out y no tiene por qué ser monótona. Por eso Q1 sirve como reproducción y control de funcionamiento, no como evidencia confirmatoria del efecto de densidad.

## Q2: qué hizo la copia exploratoria

La copia histórica prueba densidades \(p=0.1,0.2,0.3,0.4,0.5\), guarda redes y genera curvas/trayectorias. Fue un avance útil, pero no permite una comparación científica limpia porque:

- usa una sola semilla y aleatoriedad diferente entre densidades;
- compara principalmente pérdida online;
- emplea autovectores PCA sin ordenar y redondea la participación;
- reajusta un decoder PCA para parte de la evaluación;
- una métrica mezcla posición integrada con velocidad objetivo;
- guarda `p` global en lugar de `p_value` en parte de los metadatos.

Se conserva como registro de trabajo, pero no debe usarse para las figuras finales.

## Q2: experimento corregido

`notebooks/02_q2_connectivity_experiment.ipynb` y `src/nma_motor_rnn/connectivity.py` implementan:

- máscaras anidadas y matrices aleatorias compartidas dentro de cada semilla;
- escala \(g/\sqrt{pN}\);
- mismo input, decoder fijo, calendario y estados iniciales entre densidades;
- evaluación cada cinco ensayos, sin modificar pesos;
- 30 ensayos held-out balanceados por dirección;
- NMSE de velocidad, área de la curva, cambio de pesos, grados, radio espectral, \(D_{PR}\) y \(D_{90}\).

## Resultados actuales

En el experimento primario \(N=200\), ocho semillas y 60 ensayos:

| p | NMSE final media | AUC media | D_PR media | D90 media |
|---:|---:|---:|---:|---:|
| 0.05 | 0.424 | 0.655 | 3.528 | 10.125 |
| 0.10 | 0.331 | 0.581 | 3.069 | 8.125 |
| 0.20 | 0.276 | 0.422 | 2.651 | 4.125 |
| 0.40 | 0.133 | 0.382 | 2.556 | 3.125 |

- **H1 apoyada:** el contraste pareado fue positivo en 8/8 semillas; media 0.177, bootstrap 95% [0.136, 0.219].
- **H2 no apoyada:** 3/8 contrastes positivos; media 0.005, bootstrap 95% [-0.081, 0.097].
- **Manifold exploratorio:** \(D_{PR}\) y NMSE se asociaron positivamente (\(r=0.671\)); en estos datos, mayor dimensionalidad acompañó peor desempeño. No es causal y está confundido con densidad.

El piloto \(N=100\), tres semillas, no apoyó H1. Esto puede reflejar sensibilidad al tamaño, pero la interacción tamaño × densidad no estaba preregistrada.

## Afirmación defendible

Con esta inicialización pareada, decoder fijo y regla donde todos los pesos recurrentes existentes son plásticos, las redes muy dispersas \(N=200\) rindieron peor que las redes de densidad moderada/alta. No se ha demostrado un umbral crítico, rendimientos decrecientes ni un mecanismo causal del manifold; tampoco se ha aislado densidad del presupuesto de plasticidad.
