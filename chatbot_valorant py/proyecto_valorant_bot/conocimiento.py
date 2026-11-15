# =============================================================================
# UNIVERSIDAD ANDRÉS BELLO - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
# MÓDULO 1: BASE DE CONOCIMIENTO COMPLETA (TODOS LOS AGENTES Y ARMAS DE VALORANT)
# =============================================================================

# 1. HECHOS: Todos los Agentes de Valorant, sus Roles y Costo de Kit completo
AGENTES = {
    # --- DUELISTAS ---
    "jett":      {"rol": "duelista",    "costo_kit": 450},
    "reyna":     {"rol": "duelista",    "costo_kit": 500},
    "raze":      {"rol": "duelista",    "costo_kit": 600},
    "phoenix":   {"rol": "duelista",    "costo_kit": 550},
    "yoru":      {"rol": "duelista",    "costo_kit": 600},
    "neon":      {"rol": "duelista",    "costo_kit": 500},
    "iso":       {"rol": "duelista",    "costo_kit": 650},
    "waylay":    {"rol": "duelista",    "costo_kit": 600},

    # --- CONTROLADORES ---
    "omen":      {"rol": "controlador", "costo_kit": 400},
    "brimstone": {"rol": "controlador", "costo_kit": 500},
    "viper":     {"rol": "controlador", "costo_kit": 550},
    "astra":     {"rol": "controlador", "costo_kit": 450},
    "harbor":    {"rol": "controlador", "costo_kit": 500},
    "clove":     {"rol": "controlador", "costo_kit": 500},

    # --- INICIADORES ---
    "sova":      {"rol": "iniciador",   "costo_kit": 400},
    "fade":      {"rol": "iniciador",   "costo_kit": 600},
    "breach":    {"rol": "iniciador",   "costo_kit": 600},
    "skye":      {"rol": "iniciador",   "costo_kit": 650},
    "kayo":      {"rol": "iniciador",   "costo_kit": 550},
    "gekko":     {"rol": "iniciador",   "costo_kit": 550},
    "tejo":      {"rol": "iniciador",   "costo_kit": 600},

    # --- CENTINELAS ---
    "sage":      {"rol": "centinela",   "costo_kit": 700},
    "killjoy":   {"rol": "centinela",   "costo_kit": 600},
    "cypher":    {"rol": "centinela",   "costo_kit": 600},
    "chamber":   {"rol": "centinela",   "costo_kit": 800},
    "deadlock":  {"rol": "centinela",   "costo_kit": 600},
    "vyse":      {"rol": "centinela",   "costo_kit": 600},
    "veto":      {"rol": "centinela",   "costo_kit": 600},
}

# 2. HECHOS: Todas las Armas de Valorant, Categorías, Costos y Alcance Óptimo
ARMAS = {
    # Pistolas
    "classic":  {"tipo": "pistola",       "costo": 0,    "alcance": "corta"},
    "shorty":   {"tipo": "pistola",       "costo": 300,  "alcance": "corta"},
    "frenzy":   {"tipo": "pistola",       "costo": 450,  "alcance": "corta"},
    "ghost":    {"tipo": "pistola",       "costo": 500,  "alcance": "media"},
    "sheriff":  {"tipo": "pistola",       "costo": 800,  "alcance": "larga"},
    # Subfusiles
    "stinger":  {"tipo": "subfusil",      "costo": 1100, "alcance": "corta"},
    "spectre":  {"tipo": "subfusil",      "costo": 1600, "alcance": "media"},
    # Escopetas
    "bucky":    {"tipo": "escopeta",      "costo": 850,  "alcance": "corta"},
    "judge":    {"tipo": "escopeta",      "costo": 1850, "alcance": "corta"},
    # Rifles
    "bulldog":  {"tipo": "rifle",         "costo": 2050, "alcance": "larga"},
    "guardian": {"tipo": "rifle",         "costo": 2250, "alcance": "larga"},
    "phantom":  {"tipo": "rifle",         "costo": 2900, "alcance": "media"},
    "vandal":   {"tipo": "rifle",         "costo": 2900, "alcance": "larga"},
    # Francotiradores
    "marshal":  {"tipo": "francotirador", "costo": 950,  "alcance": "larga"},
    "outlaw":   {"tipo": "francotirador", "costo": 2400, "alcance": "larga"},
    "operator": {"tipo": "francotirador", "costo": 4700, "alcance": "larga"},
    # Ametralladoras pesadas
    "ares":     {"tipo": "ametralladora", "costo": 1600, "alcance": "media"},
    "odin":     {"tipo": "ametralladora", "costo": 3200, "alcance": "media"},
}

# 3. HECHOS: Escudos
ESCUDOS = {
    "ninguno":       0,
    "escudo_ligero": 400,
    "escudo_pesado": 1000,
}

# -----------------------------------------------------------------------------
# REGLAS LÓGICAS 
# -----------------------------------------------------------------------------

def creditos_validos(creditos: int) -> bool:
    return isinstance(creditos, int) and 0 <= creditos <= 9000

def mismo_rol(agente_nombre: str) -> list:
    if agente_nombre not in AGENTES:
        return []
    rol_actual = AGENTES[agente_nombre]["rol"]
    return [ag for ag, datos in AGENTES.items() if datos["rol"] == rol_actual and ag != agente_nombre]

def tipo_ronda(creditos: int) -> str:
    if not creditos_validos(creditos):
        return "invalido"
    if creditos < 2000:
        return "eco"
    elif creditos < 3900:
        return "semi_buy"
    else:
        return "full_buy"

def gasto_utilidad(agente: str, ronda: str) -> int:
    if agente not in AGENTES or ronda == "eco":
        return 0
    total = AGENTES[agente]["costo_kit"]
    if ronda == "semi_buy":
        return round(total / 2)
    elif ronda == "full_buy":
        return total
    return 0

def escudo_recomendado(saldo: int) -> str:
    if saldo >= ESCUDOS["escudo_pesado"]:
        return "escudo_pesado"
    elif saldo >= ESCUDOS["escudo_ligero"]:
        return "escudo_ligero"
    return "ninguno"

def recomendar_plan(creditos: int, agente: str, distancia: str = "corta") -> dict:
    """Replica exactamente el predicado recomendar_plan/8 de Prolog."""
    if not creditos_validos(creditos):
        return {"error": "En Valorant el saldo debe estar entre 0 y 9000 créditos."}
    if agente not in AGENTES:
        return {"error": f"El agente '{agente}' no está en la base de conocimiento."}

    ronda = tipo_ronda(creditos)
    gasto_hab = gasto_utilidad(agente, ronda)
    saldo_arma = creditos - gasto_hab

    if ronda == "full_buy":
        arma = "vandal" if distancia == "larga" else "phantom"
    elif ronda == "semi_buy":
        arma = "bulldog" if distancia == "larga" else "spectre"
    else:
        arma = "sheriff" if distancia == "larga" else "classic"

    costo_a = ARMAS[arma]["costo"]
    saldo_escudo = saldo_arma - costo_a
    escudo = escudo_recomendado(saldo_escudo)
    costo_e = ESCUDOS[escudo]
    resto = saldo_escudo - costo_e

    return {
        "agente": agente,
        "rol": AGENTES[agente]["rol"],
        "creditos_iniciales": creditos,
        "distancia": distancia,
        "tipo_ronda": ronda,
        "arma_sugerida": arma,
        "costo_arma": costo_a,
        "gasto_utilidad": gasto_hab,
        "blindaje": escudo,
        "costo_blindaje": costo_e,
        "saldo_restante": resto
    }

def obtener_contexto_para_llm() -> str:
    """Convierte toda la base de conocimiento en texto estructurado para inyectar al Prompt del LLM."""
    Lineas = ["=== BASE DE CONOCIMIENTO ESTRICTA DE VALORANT ==="]
    Lineas.append("\n1. AGENTES (Rol y Costo de Kit completo):")
    for ag, d in AGENTES.items():
        Lineas.append(f"  - {ag.capitalize()}: Rol={d['rol']}, Costo Kit={d['costo_kit']} cr.")

    Lineas.append("\n2. ARMAS (Tipo, Costo y Alcance Óptimo):")
    for ar, d in ARMAS.items():
        Lineas.append(f"  - {ar.capitalize()}: Tipo={d['tipo']}, Costo={d['costo']} cr., Alcance óptimo={d['alcance']}.")

    Lineas.append("\n3. ESCUDOS:")
    for esc, c in ESCUDOS.items():
        Lineas.append(f"  - {esc}: {c} cr.")

    Lineas.append("""
4. REGLAS LÓGICAS DE COMPRA E INFERENCIA:
  - Créditos válidos: Enteros entre 0 y 9000. Si pide fuera de este rango, indicar que es inválido.
  - Tipo de ronda según créditos:
      * Eco (eco): menos de 2000 créditos (< 2000).
      * Semi-buy (semi_buy): entre 2000 y 3899 créditos (2000 <= C < 3900).
      * Full-buy (full_buy): entre 3900 y 9000 créditos (3900 <= C <= 9000).
  - Gasto en utilidad (habilidades) según tipo de ronda:
      * En ronda 'eco': 0 créditos.
      * En ronda 'semi_buy': mitad del costo del kit redondeado (round(costo_kit / 2)).
      * En ronda 'full_buy': 100% del costo_kit del agente.
  - Selección de arma en plan de compra (según TipoRonda y Distancia [por defecto 'corta' si no se menciona]):
      * Si es 'full_buy': distancia 'larga' -> vandal (2900); distancia 'corta' o 'media' -> phantom (2900).
      * Si es 'semi_buy': distancia 'larga' -> bulldog (2050); distancia 'corta' o 'media' -> spectre (1600).
      * Si es 'eco': distancia 'larga' -> sheriff (800); distancia 'corta' o 'media' -> classic (0).
  - Cálculo de Escudo y Saldo Restante:
      * SaldoArma = Créditos - GastoUtilidad
      * SaldoEscudo = SaldoArma - CostoArma
      * Si SaldoEscudo >= 1000 -> recomienda 'escudo_pesado' (1000).
      * Si 400 <= SaldoEscudo < 1000 -> recomienda 'escudo_ligero' (400).
      * Si SaldoEscudo < 400 -> recomienda 'ninguno' (0).
      * SaldoRestante = SaldoEscudo - CostoEscudo.
""")
    return "\n".join(Lineas)