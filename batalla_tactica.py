"""Juego de batalla táctica por turnos para terminal.
Ejecución: ``python batalla_tactica.py``.

Este archivo contiene la versión "grande" del proyecto, y ahora cuenta con
comentarios pensados para señalar qué parámetros son seguros de modificar sin
romper la lógica interna del combate.
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from itertools import zip_longest
from random import random, uniform
from typing import Dict, Iterable, List, Tuple

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


def iconos_estado(fighter: "Fighter") -> str:
    iconos: List[str] = []
    if "DEF" in fighter.estado:
        iconos.append("[🛡]")
    return " ".join(iconos)


# Paleta básica de la interfaz. Cambia los colores aquí para recolorear todo.
ACCENT = Fore.MAGENTA
FRAME = Style.DIM + Fore.WHITE

# Ajusta estos colores si cambias los nombres de los combatientes principales.
NOMBRE_COLORES = {
    "Jugador": Fore.CYAN,
    "Enemigo": Fore.RED,
}


def panel_lines(fighter: "Fighter", ancho: int = 32) -> List[str]:
    """Genera líneas estilizadas para mostrar la información esencial del combatiente."""
    hp_ratio = fighter.hp / fighter.max_hp if fighter.max_hp else 0
    color_hp = ratio_color(hp_ratio)
    barra_hp = barra(fighter.hp, fighter.max_hp, 18, "█", "·", color_hp)
    barra_en = barra(fighter.en, fighter.max_en, 18, "■", "·", Fore.CYAN)
    estados = iconos_estado(fighter) or "—"
    color_nombre = NOMBRE_COLORES.get(fighter.nombre, Fore.WHITE)
    nombre = f"{Style.BRIGHT}{color_nombre}{fighter.nombre}{Style.RESET_ALL}"

    lineas = [
        nombre,
        f"HP {Style.DIM}│{Style.RESET_ALL}{barra_hp}{Style.DIM}│{Style.RESET_ALL} {color_hp}{fighter.hp:>3}{Style.RESET_ALL}/{fighter.max_hp:<3}",
        f"EN {Style.DIM}│{Style.RESET_ALL}{barra_en}{Style.DIM}│{Style.RESET_ALL} {Fore.CYAN}{fighter.en:>3}{Style.RESET_ALL}/{fighter.max_en:<3}",
        f"⚡ {fighter.cargas:<2} Estado: {Style.DIM}{estados}{Style.RESET_ALL}",
    ]

    return [pad_ansi(linea, ancho) for linea in lineas]


def obtener_panel(fighter: "Fighter", ancho: int = 38) -> List[str]:
    """Devuelve las líneas del panel para reutilizar en interfaces personalizadas."""
    return panel_lines(fighter, ancho)


def pintar_panel(fighter: "Fighter", ancho: int = 38) -> None:
    """Mantiene la versión impresa del panel que existía antes de la refactorización."""
    for linea in panel_lines(fighter, ancho):
        print(linea)


def pad_lines(lines: List[str], largo: int) -> List[str]:
    if len(lines) >= largo:
        return lines
    return lines + [""] * (largo - len(lines))


def mostrar_paneles(izquierdo: "Fighter", derecho: "Fighter") -> None:
    """Muestra los paneles de jugador y enemigo en paralelo dentro de un marco limpio."""
    ancho = 32
    izquierda = panel_lines(izquierdo, ancho)
    derecha = panel_lines(derecho, ancho)
    altura = max(len(izquierda), len(derecha))
    izquierda = pad_lines(izquierda, altura)
    derecha = pad_lines(derecha, altura)
    izquierda = [pad_ansi(linea, ancho) for linea in izquierda]
    derecha = [pad_ansi(linea, ancho) for linea in derecha]

    top = f"{FRAME}╭{'─' * (ancho + 2)}┬{'─' * (ancho + 2)}╮{Style.RESET_ALL}"
    bottom = f"{FRAME}╰{'─' * (ancho + 2)}┴{'─' * (ancho + 2)}╯{Style.RESET_ALL}"

    print(top)
    for l, r in zip_longest(izquierda, derecha, fillvalue=""):
        l_render = pad_ansi(l, ancho)
        r_render = pad_ansi(r, ancho)
        print(
            f"{FRAME}│{Style.RESET_ALL} {l_render} {FRAME}│{Style.RESET_ALL} {r_render} {FRAME}│{Style.RESET_ALL}"
        )
    print(bottom)


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
        # Configuración inicial al crear un combatiente.
        # ➜ Ajusta estos valores si quieres que empiece con más/menos recursos.
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
    # Puedes tocar estos multiplicadores para personalizar el daño crítico
    # o la variación aleatoria, manteniendo los rangos razonables.
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
    # Parámetros que determinan el comportamiento de la IA.
    # ➜ Puedes ajustar los umbrales (energía necesaria, porcentajes de vida)
    #    manteniendo la estructura de decisiones en cascada.
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


def log_ataque_detallado(
    actor: Fighter,
    accion: str,
    coste: int,
    dano: int,
    etiquetas: Iterable[str],
    trazas: Dict[str, float],
    rival: Fighter,
) -> str:
    """Replica el formato anterior con el desglose matemático del daño."""
    prefijo = f"{actor.nombre}: {accion}"
    prefijo += f" (coste {coste})." if coste else "."

    if "ESQUIVA" in etiquetas:
        return f"{prefijo} ESQUIVA del {rival.nombre.lower()}. Daño 0."

    base_total = int(
        trazas.get(
            "base_total",
            trazas.get("base", 0) + trazas.get("atk", 0) - trazas.get("def", 0),
        )
    )
    var = trazas.get("var", 1.0)
    crit = trazas.get("crit", 0.0) >= 1.0
    def_mult = trazas.get("def_mult", 1.0)

    return (
        f"{prefijo} Base {int(trazas.get('base', 0))} + ATK {int(trazas.get('atk', 0))} "
        f"− DEF {int(trazas.get('def', 0))} = {base_total}; var {var:.2f}; "
        f"CRIT: {'sí' if crit else 'no'}; DEF rival: {def_mult:.1f} → daño {dano}."
    )


def log_recarga(actor: Fighter, ganado: int, antes: int, despues: int) -> str:
    return f"{actor.nombre}: RECARGA +{ganado} EN ({antes}→{despues}/{actor.max_en})."


def log_defensa(actor: Fighter) -> str:
    return f"{actor.nombre}: DEFENSA [🛡]."


HIGHLIGHT_TERMS = [
    # Añade o cambia palabras clave y colores del registro aquí.
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

def ejecutar_ataque(atacante: Fighter, defensor: Fighter, base: int, mult: float, coste: int, etiqueta: str) -> str:
    if coste and not atacante.gastar(coste):
        return f"{atacante.nombre}: Energía insuficiente."
    dano, etiquetas, trazas = calc_daño(atacante, defensor, base, mult)
    defensor.recibir(dano)
    # Cambia `log_ataque` por `log_ataque_detallado` si quieres el mensaje extendido.
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


def mostrar_historial(historial: List[str], limite: int = 3) -> None:
    ancho = 34
    print(f"{FRAME}╭{'─' * (ancho + 2)}╮{Style.RESET_ALL}")
    cabecera_texto = "EVENTOS RECIENTES".center(ancho)
    cabecera = f"{Style.BRIGHT}{ACCENT}{cabecera_texto}{Style.RESET_ALL}"
    print(f"{FRAME}│{Style.RESET_ALL} {pad_ansi(cabecera, ancho)} {FRAME}│{Style.RESET_ALL}")
    if not historial:
        linea = f"{Style.DIM}· Sin eventos previos.{Style.RESET_ALL}"
        print(f"{FRAME}│{Style.RESET_ALL} {pad_ansi(linea, ancho)} {FRAME}│{Style.RESET_ALL}")
    else:
        for linea in historial[-limite:]:
            contenido = f"{Style.DIM}·{Style.RESET_ALL} {linea}"
            print(f"{FRAME}│{Style.RESET_ALL} {pad_ansi(contenido, ancho)} {FRAME}│{Style.RESET_ALL}")
    print(f"{FRAME}╰{'─' * (ancho + 2)}╯{Style.RESET_ALL}")


def mostrar_encabezado(ronda: int) -> None:
    titulo = f"RONDA {ronda:02d}"
    subtitulo = "BATALLA TÁCTICA"
    ancho = max(len(titulo), len(subtitulo)) + 6
    print(f"{FRAME}╭{'─' * ancho}╮{Style.RESET_ALL}")
    print(
        f"{FRAME}│{Style.RESET_ALL} {Style.BRIGHT}{ACCENT}{subtitulo:^{ancho - 2}}{Style.RESET_ALL} {FRAME}│{Style.RESET_ALL}"
    )
    print(
        f"{FRAME}│{Style.RESET_ALL} {Style.BRIGHT}{Fore.WHITE}{titulo:^{ancho - 2}}{Style.RESET_ALL} {FRAME}│{Style.RESET_ALL}"
    )
    print(f"{FRAME}╰{'─' * ancho}╯{Style.RESET_ALL}")
# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------


def bucle_principal() -> None:
    # ➜ Ajusta aquí las estadísticas iniciales de cada combatiente.
    #    Respeta el orden Fighter(nombre, max_hp, max_en, atk, df, crit, evd)
    #    y utiliza valores coherentes para evitar desbalances extremos.
    jugador = Fighter("Jugador", 100, 18, 9, 4, 0.15, 0.08)
    enemigo = Fighter("Enemigo", 100, 16, 8, 5, 0.10, 0.06)

    ronda = 1
    jugador_recargo = False
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
            return

        jugador_recargo = False

        if accion == "A":
            # Daño básico (base=8, multiplicador=1.0) y coste 0 de energía.
            log = ejecutar_ataque(jugador, enemigo, 8, 1.0, 0, "ATAQUE")
            mostrado = resaltar_log(log)
            slow_print(mostrado)
            historial.append(mostrado)
        elif accion == "E":
            # Ataque especial: ajusta base/multiplicador/coste con cautela.
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

        mostrado_enemigo = resaltar_log(log_enemigo)
        slow_print(mostrado_enemigo)
        historial.append(mostrado_enemigo)
        defensa_cleanup(jugador)

        resumen_turno = resumen_ronda(ronda, jugador, enemigo)
        mostrado_resumen = resaltar_log(resumen_turno)
        slow_print(mostrado_resumen)
        historial.append(mostrado_resumen)
        ronda += 1
        if jugador.vivo() and enemigo.vivo():
            input("Continuar... ")

    if jugador.vivo() and not enemigo.vivo():
        print(f"{Style.BRIGHT}{Fore.GREEN}Victoria.{Style.RESET_ALL}")
    elif enemigo.vivo() and not jugador.vivo():
        print(f"{Style.BRIGHT}{Fore.RED}Derrota.{Style.RESET_ALL}")
    else:
        print(f"{Style.BRIGHT}{Fore.YELLOW}Empate.{Style.RESET_ALL}")


def solicitar_accion() -> str:
    while True:
        respuesta = input(
            f"{Style.BRIGHT}{Fore.CYAN}Acción{Style.RESET_ALL}: "
        ).strip().upper()
        if respuesta in {"A", "D", "E", "R", "Q"}:
            return respuesta
        print("Entrada inválida.")


if __name__ == "__main__":
    try:
        bucle_principal()
    except KeyboardInterrupt:
        sys.exit("\nInterrumpido por el usuario.")
