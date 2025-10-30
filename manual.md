# Manual de Juego — Batalla Táctica

## Introducción
"Batalla Táctica" es un duelo por turnos pensado para ejecutarse en la terminal. Controlas a un combatiente que debe administrar salud, energía y cargas de recarga para derrotar al enemigo. El juego funciona en Windows, macOS y Linux con Python 3.13.

## Requisitos previos
- Python 3.13 instalado.
- Librería `colorama` (se instala con `pip install colorama`).
- Ejecuta el juego con `python batalla_tactica.py` desde la terminal o integrada en VS Code.

## Objetivo
Reduce los puntos de vida del enemigo a cero antes de que él haga lo mismo contigo. Si ambos llegan a cero en la misma ronda, el resultado es empate.

## Controles del jugador
Durante tu turno introduce la letra correspondiente y pulsa Enter:

| Acción | Tecla | Coste de energía | Descripción |
| ------ | ----- | ---------------- | ----------- |
| Atacar | `A`   | 0                | Golpe básico. Inflige daño basado en el ataque propio y la defensa rival. |
| Defender| `D`  | 0                | Activa el estado **DEF** que reduce un 40 % el próximo golpe recibido durante la ronda actual. |
| Especial| `E`  | 8                | Golpe potenciado con multiplicador 1.25. Consume energía. |
| Recargar| `R`  | 1 carga          | Recupera energía (`max(6, máximo de energía/2)`) hasta dos veces por combate. |
| Quitar | `Q`   | —                | Sale inmediatamente de la partida. |

Si introduces otra tecla, el juego avisará y pedirá una entrada válida.

## Recursos y estados
- **HP (salud)**: si llega a 0, el combatiente cae derrotado.
- **EN (energía)**: necesaria para usar habilidades especiales. Inicias con la mitad de tu máximo.
- **Cargas**: cada recarga consume una. Empiezas con dos.
- **DEF**: estado que aparece al defenderse y reduce el siguiente golpe recibido dentro de la ronda en curso.

## Flujo del turno
1. El jugador actúa primero eligiendo una acción.
2. Se muestran los resultados: daño, esquivas, críticos y estado de la vida rival.
3. Se limpia el estado DEF del objetivo al finalizar su turno defensivo.
4. El enemigo responde según su IA.
5. Se muestra un resumen de la ronda con HP y EN de ambos combatientes.
6. Continúa la siguiente ronda mientras ambos sigan con vida.

## Cálculo de daño
1. **Evasión**: cada combatiente tiene un porcentaje de esquiva. Si sucede, el daño es 0.
2. **Crítico**: los críticos multiplican el daño por 1.5.
3. **Variación**: cada golpe aplica un factor aleatorio entre 0.9 y 1.1.
4. **Base**: `(daño base + ATK atacante − DEF defensor)`.
5. **Defensa**: si el defensor tiene `DEF` activo, el daño final se multiplica por 0.6.
6. Siempre que la base sea positiva y el golpe conecte, se garantiza al menos 1 punto de daño.

## Inteligencia artificial enemiga
El enemigo evalúa la situación antes de actuar:
1. Remata con ataque o especial si puede derrotarte en el turno actual.
2. Si está por debajo del 30 % de salud y percibe peligro (tienes ≥ 8 de energía o recargaste en tu turno), se defiende.
3. Si le falta energía y aún tiene cargas, recarga.
4. Prefiere el especial si puede usarlo y su daño esperado supera al ataque básico.
5. En caso contrario, lanza un ataque normal.

## Consejos tácticos
- **Gestiona la energía**: reserva 8 puntos para el especial cuando puedas garantizar un golpe fuerte.
- **Observa las cargas**: agotar tus recargas demasiado pronto puede dejarte sin opciones en el tramo final.
- **Defiende inteligentemente**: activa DEF cuando preveas un especial enemigo o si necesitas sobrevivir un turno más.
- **Presiona cuando el enemigo recarga**: tras gastar energía, suele quedar expuesto.

## Solución de problemas
- Si la terminal no muestra colores, asegúrate de que `colorama` esté instalado y que `python` use la versión correcta.
- En Windows, ejecuta el script desde `cmd`, PowerShell o el terminal de VS Code.
- Para salir rápidamente, presiona `Q` durante tu turno o `Ctrl+C` en cualquier momento.

¡Buena suerte en la arena táctica!
