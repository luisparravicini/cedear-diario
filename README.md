
El script usa los datos que provee el sitio de Invertir Online para armar una lista de los 15 CEDEARs con más monto operado en el día (la lista queda guardaba en un .json para futuras corridas del script).

Luego por cada CEDEAR obtiene un gráfico de las operaciones del día (es un .svg) y también un .json con la lista de las operaciones diarias. Estos datos se guardan dentro de una estructura de directorio `data/YYY-MM-DD/{graphic.svg, data.json}`

