"""Juego de batalla táctica por turnos para terminal.
Ejecución: python batalla_tactica.py"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple
from random import random, uniform
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


def iconos_estado(fighter: "Fighter") -> str:
    iconos: List[str] = []
    if "DEF" in fighter.estado:
        iconos.append("[🛡]")
    return " ".join(iconos)


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


def log_recarga(actor: Fighter, ganado: int, antes: int, despues: int) -> str:
    return f"{actor.nombre}: RECARGA +{ganado} EN ({antes}→{despues}/{actor.max_en})."


def log_defensa(actor: Fighter) -> str:
    return f"{actor.nombre}: DEFENSA [🛡]."


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


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------


def bucle_principal() -> None:
    jugador = Fighter("Jugador", 90, 18, 9, 4, 0.15, 0.08)
    enemigo = Fighter("Enemigo", 100, 16, 8, 5, 0.10, 0.06)

    ronda = 1
    jugador_recargo = False

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
            return

        jugador_recargo = False

        if accion == "A":
            log = ejecutar_ataque(jugador, enemigo, 8, 1.0, 0, "ATAQUE")
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

        slow_print(log_enemigo)
        defensa_cleanup(jugador)

        slow_print(resumen_ronda(ronda, jugador, enemigo))
        ronda += 1
        if jugador.vivo() and enemigo.vivo():
            input("Continuar... ")

    if jugador.vivo() and not enemigo.vivo():
        print("Victoria.")
    elif enemigo.vivo() and not jugador.vivo():
        print("Derrota.")
    else:
        print("Empate.")


def solicitar_accion() -> str:
    while True:
        respuesta = input("Acción: ").strip().upper()
        if respuesta in {"A", "D", "E", "R", "Q"}:
            return respuesta
        print("Entrada inválida.")


if __name__ == "__main__":
    try:
        bucle_principal()
    except KeyboardInterrupt:
        sys.exit("\nInterrumpido por el usuario.")
