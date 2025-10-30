"""Juego de batalla táctica por turnos para terminal.
Ejecución: python batalla_tactica.py"""

from __future__ import annotations

from dataclasses import dataclass, field
<<<<<<< HEAD
from typing import Dict, Iterable, List, Tuple
from random import random, uniform
=======
from itertools import zip_longest
from typing import Dict, Iterable, List, Tuple
from random import random, uniform
import re
>>>>>>> origin/codex/create-turn-based-combat-game-in-python
import sys
import time

from colorama import Fore, Style, init

init(autoreset=True)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def clamp(value: int, minimo: int, maximo: int) -> int:
    """Limita un entero al rango indicado."""
    return max(minimo, min(maximo, value))


def clear_screen() -> None:
    """Limpia la terminal."""
    print("\033[2J\033[H", end="")


def slow_print(texto: str, delay: float = 0.0) -> None:
    """Imprime con retardo opcional."""
    if delay <= 0:
        print(texto)
        return
    for char in texto:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def ratio_color(ratio: float) -> str:
    """Devuelve el color correspondiente al porcentaje de vida."""
    if ratio >= 0.6:
        return Fore.GREEN
    if ratio >= 0.3:
        return Fore.YELLOW
    return Fore.RED


def barra(actual: int, maximo: int, longitud: int, llenos: str, vacios: str, color: str) -> str:
    """Construye una barra con color."""
    if maximo <= 0:
        maximo = 1
    filled = int(round((actual / maximo) * longitud))
    filled = clamp(filled, 0, longitud)
    contenido = llenos * filled + vacios * (longitud - filled)
    return f"{color}{contenido}{Style.RESET_ALL}"


<<<<<<< HEAD
=======
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def ancho_visual(texto: str) -> int:
    """Longitud sin secuencias ANSI."""
    return len(ANSI_PATTERN.sub("", texto))


def pad_ansi(texto: str, ancho: int) -> str:
    """Rellena respetando códigos ANSI."""
    longitud = ancho_visual(texto)
    if longitud >= ancho:
        return texto
    return texto + " " * (ancho - longitud)


>>>>>>> origin/codex/create-turn-based-combat-game-in-python
def iconos_estado(fighter: "Fighter") -> str:
    iconos: List[str] = []
    if "DEF" in fighter.estado:
        iconos.append("[🛡]")
    return " ".join(iconos)


<<<<<<< HEAD
def pintar_panel(fighter: "Fighter") -> None:
    """Dibuja el panel de estado del combatiente."""
    nombre = fighter.nombre
    hp_ratio = fighter.hp / fighter.max_hp if fighter.max_hp else 0
    color_hp = ratio_color(hp_ratio)
    barra_hp = barra(fighter.hp, fighter.max_hp, 12, "█", "·", color_hp)
    barra_en = barra(fighter.en, fighter.max_en, 12, "■", "·", Fore.CYAN)
    estados = iconos_estado(fighter)
    encabezado = f"{Style.BRIGHT}{nombre}{Style.RESET_ALL}"
    if estados:
        encabezado += f" {estados}"
    print(encabezado)
    print(f" HP [{barra_hp}] {fighter.hp}/{fighter.max_hp}")
    print(f" EN [{barra_en}] {fighter.en}/{fighter.max_en}")
    print(f" Cargas: {fighter.cargas}")
=======
NOMBRE_COLORES = {
    "Jugador": Fore.CYAN,
    "Enemigo": Fore.RED,
}


def panel_lines(fighter: "Fighter", ancho: int = 38) -> List[str]:
    """Genera líneas simples para mostrar la información esencial del combatiente."""
    hp_ratio = fighter.hp / fighter.max_hp if fighter.max_hp else 0
    color_hp = ratio_color(hp_ratio)
    barra_hp = barra(fighter.hp, fighter.max_hp, 20, "█", "·", color_hp)
    barra_en = barra(fighter.en, fighter.max_en, 20, "■", "·", Fore.CYAN)
    estados = iconos_estado(fighter) or "—"
    color_nombre = NOMBRE_COLORES.get(fighter.nombre, Fore.WHITE)
    nombre = f"{color_nombre}{Style.BRIGHT}{fighter.nombre}{Style.RESET_ALL}"
    if estados != "—":
        nombre = f"{nombre} {Style.DIM}{estados}{Style.RESET_ALL}"

    lineas = [
        nombre,
        f"HP {Style.DIM}[{Style.RESET_ALL}{barra_hp}{Style.DIM}]{Style.RESET_ALL} {color_hp}{fighter.hp:>3}{Style.RESET_ALL}/{fighter.max_hp:<3}",
        f"EN {Style.DIM}[{Style.RESET_ALL}{barra_en}{Style.DIM}]{Style.RESET_ALL} {Fore.CYAN}{fighter.en:>3}{Style.RESET_ALL}/{fighter.max_en:<3}",
        f"⚡ Cargas: {fighter.cargas:<2} Estado: {Style.DIM}{estados}{Style.RESET_ALL}",
    ]

    return [pad_ansi(linea, ancho) for linea in lineas]


def pintar_panel(fighter: "Fighter") -> List[str]:
    """Compatibilidad: devuelve las líneas del panel."""
    return panel_lines(fighter)


def pad_lines(lines: List[str], largo: int) -> List[str]:
    if len(lines) >= largo:
        return lines
    return lines + [""] * (largo - len(lines))


def mostrar_paneles(izquierdo: "Fighter", derecho: "Fighter") -> None:
    """Muestra los paneles de jugador y enemigo en paralelo."""
    izquierda = panel_lines(izquierdo)
    derecha = panel_lines(derecho)
    altura = max(len(izquierda), len(derecha))
    izquierda = pad_lines(izquierda, altura)
    derecha = pad_lines(derecha, altura)
    ancho_izq = max(ancho_visual(linea) for linea in izquierda) if izquierda else 0
    separador = " " * 5
    for l, r in zip_longest(izquierda, derecha, fillvalue=""):
        print(f"{pad_ansi(l or '', ancho_izq)}{separador}{r}")
>>>>>>> origin/codex/create-turn-based-combat-game-in-python


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------


@dataclass
class Fighter:
    nombre: str
    max_hp: int
    max_en: int
    atk: int
    df: int
    crit: float
    evd: float
    estado: set[str] = field(default_factory=set)
    hp: int = field(init=False)
    en: int = field(init=False)
    cargas: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.max_hp
        self.en = self.max_en // 2
        self.cargas = 2

    def vivo(self) -> bool:
        return self.hp > 0

    def recibir(self, dano: int) -> None:
        self.hp = clamp(self.hp - dano, 0, self.max_hp)

    def recargar(self) -> Tuple[int, int, int]:
        if self.cargas <= 0:
            return (0, self.en, self.en)
        self.cargas -= 1
        cantidad = max(6, self.max_en // 2)
        antes = self.en
        self.en = clamp(self.en + cantidad, 0, self.max_en)
        return (self.en - antes, antes, self.en)

    def gastar(self, coste: int) -> bool:
        if self.en < coste:
            return False
        self.en -= coste
        return True


# ---------------------------------------------------------------------------
# Motor de combate
# ---------------------------------------------------------------------------


def calc_daño(atacante: Fighter, defensor: Fighter, base: int, multiplicador: float) -> Tuple[int, List[str], Dict[str, float]]:
    """Calcula el daño aplicado."""
    etiquetas: List[str] = []
    trazas: Dict[str, float] = {}

    if random() < defensor.evd:
        etiquetas.append("ESQUIVA")
        trazas.update({
            "evaded": 1.0,
            "base": base,
            "atk": atacante.atk,
            "def": defensor.df,
            "var": 1.0,
            "crit": 0.0,
            "def_mult": 1.0,
            "final": 0.0,
        })
        return 0, etiquetas, trazas

    critico = random() < atacante.crit
    crit_mult = 1.5 if critico else 1.0
    variacion = uniform(0.9, 1.1)

    base_total = base + atacante.atk - defensor.df
    bruto = base_total * multiplicador * crit_mult * variacion
    def_mult = 0.6 if "DEF" in defensor.estado else 1.0
    bruto *= def_mult

    dano = 0
    if base_total > 0:
        dano = int(max(1, bruto))
    else:
        dano = int(max(0, bruto))

    if critico:
        etiquetas.append("CRÍTICO")

    trazas.update({
        "evaded": 0.0,
        "base": float(base),
        "atk": float(atacante.atk),
        "def": float(defensor.df),
        "base_total": float(base_total),
        "var": float(variacion),
        "crit": 1.0 if critico else 0.0,
        "crit_mult": float(crit_mult),
        "def_mult": float(def_mult),
        "final": float(dano),
    })
    return dano, etiquetas, trazas


def defensa_cleanup(fighter: Fighter) -> None:
    fighter.estado.discard("DEF")


# ---------------------------------------------------------------------------
# IA
# ---------------------------------------------------------------------------


def esperanza_dano(atacante: Fighter, defensor: Fighter, base: int, mult: float) -> float:
    base_total = base + atacante.atk - defensor.df
    if base_total <= 0:
        return 0.0
    crit_mult = 1.5
    esperanza_crit = 1.0 + atacante.crit * (crit_mult - 1.0)
    defensa_mult = 0.6 if "DEF" in defensor.estado else 1.0
    dano_medio = base_total * mult * esperanza_crit * defensa_mult
    dano_medio *= (1 - defensor.evd)
    if dano_medio < 1.0 and base_total > 0:
        dano_medio = max(dano_medio, 1.0 * (1 - defensor.evd))
    return dano_medio


def decision_ia(enemy: Fighter, player: Fighter, jugador_recargo: bool) -> str:
    puede_especial = enemy.en >= 8
    puede_ataque = True
    puede_recarga = enemy.cargas > 0 and enemy.en < 8

    dano_ataque = dano_maximo(enemy, player, 8, 1.0)
    dano_especial = dano_maximo(enemy, player, 12, 1.2)

    if player.hp <= dano_especial and enemy.en >= 8:
        return "E"
    if player.hp <= dano_ataque:
        return "A"

    if enemy.hp <= int(enemy.max_hp * 0.3) and (player.en >= 8 or jugador_recargo):
        return "D"

    if puede_recarga:
        return "R"

    if puede_especial:
        exp_especial = esperanza_dano(enemy, player, 12, 1.2)
        exp_ataque = esperanza_dano(enemy, player, 8, 1.0)
        if exp_especial > exp_ataque:
            return "E"

    if puede_ataque:
        return "A"
    return "D"


def dano_maximo(atacante: Fighter, defensor: Fighter, base: int, mult: float) -> int:
    base_total = base + atacante.atk - defensor.df
    if base_total <= 0:
        return 0
    crit_mult = 1.5
    variacion_max = 1.1
    def_mult = 0.6 if "DEF" in defensor.estado else 1.0
    bruto = base_total * mult * crit_mult * variacion_max * def_mult
    return int(max(1, bruto))


# ---------------------------------------------------------------------------
# Interfaz y acciones
# ---------------------------------------------------------------------------


<<<<<<< HEAD
def log_ataque(actor: Fighter, accion: str, coste: int, dano: int, etiquetas: Iterable[str], trazas: Dict[str, float], rival: Fighter) -> str:
    prefijo = f"{actor.nombre}: {accion}"
    if coste:
        prefijo += f" (coste {coste})."
    else:
        prefijo += "."

    if "ESQUIVA" in etiquetas:
        return f"{prefijo} ESQUIVA del {rival.nombre.lower()}. Daño 0."

    base_total = int(trazas.get("base_total", trazas.get("base", 0) + trazas.get("atk", 0) - trazas.get("def", 0)))
    var = trazas.get("var", 1.0)
    crit = trazas.get("crit", 0.0) >= 1.0
    def_mult = trazas.get("def_mult", 1.0)
    prefijo_formulas = (
        f"{prefijo} Base {int(trazas.get('base', 0))} + ATK {int(trazas.get('atk', 0))} "
        f"− DEF {int(trazas.get('def', 0))} = {base_total}; var {var:.2f}; "
        f"CRIT: {'sí' if crit else 'no'}; DEF rival: {def_mult:.1f} → daño {dano}."
    )
    return prefijo_formulas
=======
def log_ataque(
    actor: Fighter,
    accion: str,
    coste: int,
    dano: int,
    etiquetas: Iterable[str],
    trazas: Dict[str, float],
    rival: Fighter,
) -> str:
    prefijo = f"{actor.nombre}: {accion}"
    if coste:
        prefijo += f" (coste {coste})"

    if "ESQUIVA" in etiquetas:
        return f"{prefijo}. ESQUIVA del {rival.nombre.lower()}. Daño 0."

    partes: List[str] = [f"{prefijo} → daño {dano}."]
    if "CRÍTICO" in etiquetas:
        partes.append("CRÍTICO.")

    def_mult = trazas.get("def_mult", 1.0)
    if def_mult < 1.0:
        partes.append("Defensa rival activa.")

    partes.append(f"HP rival {rival.hp}/{rival.max_hp}.")
    return " ".join(partes)
>>>>>>> origin/codex/create-turn-based-combat-game-in-python


def log_recarga(actor: Fighter, ganado: int, antes: int, despues: int) -> str:
    return f"{actor.nombre}: RECARGA +{ganado} EN ({antes}→{despues}/{actor.max_en})."


def log_defensa(actor: Fighter) -> str:
    return f"{actor.nombre}: DEFENSA [🛡]."


<<<<<<< HEAD
=======
HIGHLIGHT_TERMS = [
    ("ESPECIAL", Fore.MAGENTA),
    ("CRÍTICO", Fore.LIGHTRED_EX),
    ("ESQUIVA", Fore.LIGHTBLUE_EX),
    ("RECARGA", Fore.GREEN),
    ("DEFENSA", Fore.YELLOW),
]


def aplicar_resaltado(texto: str) -> str:
    resaltado = texto
    for termino, color in HIGHLIGHT_TERMS:
        resaltado = re.sub(
            rf"(?<!\w){termino}(?!\w)",
            lambda m: f"{Style.BRIGHT}{color}{m.group(0)}{Style.RESET_ALL}",
            resaltado,
        )
    return resaltado


def resaltar_log(linea: str) -> str:
    """Añade color según el emisor y resalta palabras clave."""
    if linea.startswith("Jugador:"):
        linea = f"{Style.BRIGHT}{Fore.CYAN}Jugador{Style.RESET_ALL}{linea[len('Jugador') :]}"
    elif linea.startswith("Enemigo:"):
        linea = f"{Style.BRIGHT}{Fore.RED}Enemigo{Style.RESET_ALL}{linea[len('Enemigo') :]}"
    elif linea.startswith("Ronda "):
        return f"{Style.DIM}{linea}{Style.RESET_ALL}"
    elif linea.startswith("Entrada inválida"):
        return f"{Fore.YELLOW}{linea}{Style.RESET_ALL}"
    elif linea.startswith("Salida del juego"):
        return f"{Fore.YELLOW}{linea}{Style.RESET_ALL}"
    return aplicar_resaltado(linea)


>>>>>>> origin/codex/create-turn-based-combat-game-in-python
def ejecutar_ataque(atacante: Fighter, defensor: Fighter, base: int, mult: float, coste: int, etiqueta: str) -> str:
    if coste and not atacante.gastar(coste):
        return f"{atacante.nombre}: Energía insuficiente."
    dano, etiquetas, trazas = calc_daño(atacante, defensor, base, mult)
    defensor.recibir(dano)
    log = log_ataque(atacante, etiqueta, coste, dano, etiquetas, trazas, defensor)
    return log


def ejecutar_recarga(actor: Fighter) -> Tuple[str, bool]:
    if actor.cargas <= 0:
        return f"{actor.nombre}: Sin cargas disponibles.", False
    ganado, antes, despues = actor.recargar()
    return log_recarga(actor, ganado, antes, despues), True


def ejecutar_defensa(actor: Fighter) -> str:
    actor.estado.add("DEF")
    return log_defensa(actor)


def resumen_ronda(n: int, jugador: Fighter, enemigo: Fighter) -> str:
    return (
        f"Ronda {n} — HP Jugador {jugador.hp}/{jugador.max_hp}, EN {jugador.en}/{jugador.max_en} | "
        f"HP Enemigo {enemigo.hp}/{enemigo.max_hp}, EN {enemigo.en}/{enemigo.max_en}"
    )


<<<<<<< HEAD
=======
def mostrar_historial(historial: List[str], limite: int = 3) -> None:
    if not historial:
        print(f"  {Style.DIM}• Sin eventos previos.{Style.RESET_ALL}")
        return
    for linea in historial[-limite:]:
        print(f"  {Style.DIM}•{Style.RESET_ALL} {linea}")


def mostrar_encabezado(ronda: int) -> None:
    titulo = f" BATALLA TÁCTICA — RONDA {ronda:02d} "
    borde = "═" * len(titulo)
    print(f"{Style.BRIGHT}{Fore.MAGENTA}╔{borde}╗{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}║{titulo}║{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}╚{borde}╝{Style.RESET_ALL}")


>>>>>>> origin/codex/create-turn-based-combat-game-in-python
# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------


def bucle_principal() -> None:
<<<<<<< HEAD
    jugador = Fighter("Jugador", 90, 18, 9, 4, 0.15, 0.08)
=======
    jugador = Fighter("Jugador", 100, 18, 9, 4, 0.15, 0.08)
>>>>>>> origin/codex/create-turn-based-combat-game-in-python
    enemigo = Fighter("Enemigo", 100, 16, 8, 5, 0.10, 0.06)

    ronda = 1
    jugador_recargo = False
<<<<<<< HEAD

    while jugador.vivo() and enemigo.vivo():
        clear_screen()
        pintar_panel(jugador)
        print()
        pintar_panel(enemigo)
        print()
        print("[A]tacar [D]efender [E]special [R]ecargar [Q]uitar")

        accion = solicitar_accion()
        if accion == "Q":
            print("Salida del juego.")
=======
    historial: List[str] = []

    while jugador.vivo() and enemigo.vivo():
        clear_screen()
        mostrar_encabezado(ronda)
        mostrar_paneles(jugador, enemigo)
        print()
        print(f"{Style.BRIGHT}Registro reciente:{Style.RESET_ALL}")
        mostrar_historial(historial)
        print()
        print(
            f"{Style.DIM}[A]tacar [D]efender [E]special [R]ecargar [Q]uitar{Style.RESET_ALL}"
        )

        accion = solicitar_accion()
        if accion == "Q":
            mensaje = resaltar_log("Salida del juego.")
            print(mensaje)
>>>>>>> origin/codex/create-turn-based-combat-game-in-python
            return

        jugador_recargo = False

        if accion == "A":
            log = ejecutar_ataque(jugador, enemigo, 8, 1.0, 0, "ATAQUE")
<<<<<<< HEAD
            slow_print(log)
        elif accion == "E":
            log = ejecutar_ataque(jugador, enemigo, 12, 1.25, 8, "ESPECIAL")
            slow_print(log)
        elif accion == "R":
            log, exito = ejecutar_recarga(jugador)
            slow_print(log)
            jugador_recargo = exito
        elif accion == "D":
            log = ejecutar_defensa(jugador)
            slow_print(log)
        else:
            slow_print("Entrada inválida.")

        if not enemigo.vivo():
            slow_print(resumen_ronda(ronda, jugador, enemigo))
=======
            mostrado = resaltar_log(log)
            slow_print(mostrado)
            historial.append(mostrado)
        elif accion == "E":
            log = ejecutar_ataque(jugador, enemigo, 12, 1.25, 8, "ESPECIAL")
            mostrado = resaltar_log(log)
            slow_print(mostrado)
            historial.append(mostrado)
        elif accion == "R":
            log, exito = ejecutar_recarga(jugador)
            mostrado = resaltar_log(log)
            slow_print(mostrado)
            jugador_recargo = exito
            historial.append(mostrado)
        elif accion == "D":
            log = ejecutar_defensa(jugador)
            mostrado = resaltar_log(log)
            slow_print(mostrado)
            historial.append(mostrado)
        else:
            mensaje = "Entrada inválida."
            mostrado = resaltar_log(mensaje)
            slow_print(mostrado)
            historial.append(mostrado)

        if not enemigo.vivo():
            resumen = resumen_ronda(ronda, jugador, enemigo)
            mostrado_resumen = resaltar_log(resumen)
            slow_print(mostrado_resumen)
            historial.append(mostrado_resumen)
>>>>>>> origin/codex/create-turn-based-combat-game-in-python
            break

        defensa_cleanup(enemigo)

        decision = decision_ia(enemigo, jugador, jugador_recargo)
        if decision == "E" and enemigo.en < 8:
            decision = "A"

        if decision == "A":
            log_enemigo = ejecutar_ataque(enemigo, jugador, 8, 1.0, 0, "ATAQUE")
        elif decision == "E":
            log_enemigo = ejecutar_ataque(enemigo, jugador, 12, 1.20, 8, "ESPECIAL")
        elif decision == "R":
            log_enemigo, _ = ejecutar_recarga(enemigo)
        else:
            log_enemigo = ejecutar_defensa(enemigo)

<<<<<<< HEAD
        slow_print(log_enemigo)
        defensa_cleanup(jugador)

        slow_print(resumen_ronda(ronda, jugador, enemigo))
=======
        mostrado_enemigo = resaltar_log(log_enemigo)
        slow_print(mostrado_enemigo)
        historial.append(mostrado_enemigo)
        defensa_cleanup(jugador)

        resumen_turno = resumen_ronda(ronda, jugador, enemigo)
        mostrado_resumen = resaltar_log(resumen_turno)
        slow_print(mostrado_resumen)
        historial.append(mostrado_resumen)
>>>>>>> origin/codex/create-turn-based-combat-game-in-python
        ronda += 1
        if jugador.vivo() and enemigo.vivo():
            input("Continuar... ")

    if jugador.vivo() and not enemigo.vivo():
<<<<<<< HEAD
        print("Victoria.")
    elif enemigo.vivo() and not jugador.vivo():
        print("Derrota.")
    else:
        print("Empate.")
=======
        print(f"{Style.BRIGHT}{Fore.GREEN}Victoria.{Style.RESET_ALL}")
    elif enemigo.vivo() and not jugador.vivo():
        print(f"{Style.BRIGHT}{Fore.RED}Derrota.{Style.RESET_ALL}")
    else:
        print(f"{Style.BRIGHT}{Fore.YELLOW}Empate.{Style.RESET_ALL}")
>>>>>>> origin/codex/create-turn-based-combat-game-in-python


def solicitar_accion() -> str:
    while True:
<<<<<<< HEAD
        respuesta = input("Acción: ").strip().upper()
=======
        respuesta = input(
            f"{Style.BRIGHT}{Fore.CYAN}Acción{Style.RESET_ALL}: "
        ).strip().upper()
>>>>>>> origin/codex/create-turn-based-combat-game-in-python
        if respuesta in {"A", "D", "E", "R", "Q"}:
            return respuesta
        print("Entrada inválida.")


if __name__ == "__main__":
    try:
        bucle_principal()
    except KeyboardInterrupt:
        sys.exit("\nInterrumpido por el usuario.")
