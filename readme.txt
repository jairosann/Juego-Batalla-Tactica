BATALLA TÁCTICA — MANUAL DEL JUGADOR
====================================

Requisitos previos
------------------
1. Python 3.13 instalado.
2. Instala la única dependencia externa ejecutando:
   ```bash
   pip install colorama
   ```
3. Asegúrate de situarte en la carpeta del proyecto en la terminal.

Inicio rápido
-------------
1. Enciende la aplicación con:
   ```bash
   python batalla_tactica.py
   ```
2. La terminal mostrará dos paneles: el **Jugador** a la izquierda y el **Enemigo** a la derecha. Cada panel incluye vida (HP), energía (EN), cargas restantes y estados activos.
3. Sigue las indicaciones del prompt `Acción:` para escribir la letra de la acción deseada y pulsa **Enter**.

Objetivo
--------
Reduce los puntos de vida (HP) del enemigo a cero antes de que él agote los tuyos. Ambos combatientes comienzan con dos cargas de recarga y valores iniciales equilibrados: tanto el jugador como el enemigo tienen 100 HP máximos; el jugador dispone de 18 EN y el enemigo de 16 EN máximos.

Controles del jugador
---------------------
Escribe una de las teclas indicadas durante tu turno.

- **A — Atacar:** golpe básico sin coste de energía (base 8). Ideal para mantener la presión cuando tu energía es baja.
- **D — Defender:** aplica el estado `[🛡] DEF` que reduce a 60 % el siguiente daño recibido durante la ronda actual. Se limpia al final del turno rival si no te golpean.
- **E — Especial:** consume 8 EN, usa base 12 y un multiplicador de 1.25. Mayor daño potencial, especialmente si logras críticos.
- **R — Recargar:** gasta una carga para recuperar energía. Añade el mayor valor entre 6 y la mitad de tu energía máxima (9 para el jugador) sin superar el máximo. Empieza la partida con 2 cargas.
- **Q — Quitar:** abandona la partida de inmediato.

Flujo de una ronda
------------------
1. Realiza tu acción y revisa el registro generado.
2. Si el enemigo sigue con vida, la IA decide su movimiento en función de su energía, tu estado actual y el daño estimado.
3. El resumen finaliza la ronda mostrando HP y EN de ambos. Pulsa **Enter** cuando se te solicite para continuar.

Cálculo de daño y estados
-------------------------
- **Evasión:** antes de cualquier cálculo, existe la posibilidad de que el defensor esquive completamente el golpe según su estadística `evd`. En ese caso el daño es 0 y el registro indica `ESQUIVA`.
- **Críticos:** si el ataque es crítico (probabilidad `crit`), el daño se multiplica por 1.5.
- **Variación:** cada golpe aplica una variación aleatoria entre 0.90 y 1.10 para evitar valores repetidos.
- **Defensa:** el estado `[🛡] DEF` multiplica el daño recibido por 0.6 y se elimina tras absorber un golpe o al terminar el turno del atacante rival.
- **Daño mínimo:** cualquier golpe que logre conectar y tenga resultado positivo inflige al menos 1 punto de daño.

Gestión de recursos
-------------------
- **Energía (EN):** se gasta al usar el especial. Administrarla es clave para encadenar ataques potentes.
- **Cargas:** cada recarga consume una carga. Sin cargas no podrás recuperar energía y el comando mostrará un aviso.
- **Registro reciente:** el cuadro de historial mantiene las tres últimas entradas para seguir la secuencia del combate.

Inteligencia artificial
-----------------------
El enemigo analiza la situación con la siguiente prioridad:
1. Usa el ataque o el especial si con alguno puede derrotarte inmediatamente.
2. Se defiende cuando su vida está a 30 % o menos y detecta que puedes lanzar un especial o que recargaste en el turno actual.
3. Recarga si tiene energía por debajo de 8 y aún conserva cargas.
4. Prefiere el especial sobre el ataque básico cuando su daño esperado es superior y dispone de la energía suficiente.
5. En cualquier otra circunstancia, ataca de forma estándar.

Pantallas y mensajes
--------------------
- Los paneles incluyen barras de color: verde (≥60 %), amarillo (≥30 %) o rojo (<30 %) para HP, y cian para EN.
- Los estados activos se muestran tras el nombre del combatiente; si no hay ninguno aparece `—`.
- El registro de combate detalla cada acción en una o dos líneas con cálculos de daño, mensajes de esquiva o resultados de recarga.
- Al finalizar la partida se imprime un mensaje destacado: `Victoria.`, `Derrota.` o `Empate.` con colores asociados.

Consejos estratégicos
---------------------
- Vigila tu energía antes de lanzarte al especial; evita quedarte sin recursos cuando el enemigo esté a punto de recargar.
- Aprovecha la defensa cuando preveas un contraataque fuerte o después de recargar.
- Observa la IA: si pierdes mucha vida y tienes energía alta, es probable que el enemigo se cubra; podrías usar ese turno para recargar o preparar un ataque posterior.

Solución de problemas
---------------------
- Si la terminal no muestra colores, verifica que `colorama` esté instalado correctamente y que la terminal admita códigos ANSI.
- Ante un cierre con `Ctrl+C`, el juego se interrumpe limpiamente mostrando `Interrumpido por el usuario.`
- Para reiniciar la partida basta con volver a ejecutar `python batalla_tactica.py`.

¡Disfruta la batalla y buena suerte!
