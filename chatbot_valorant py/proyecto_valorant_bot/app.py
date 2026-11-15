# =============================================================================
# UNIVERSIDAD ANDRÉS BELLO - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
# MÓDULO 2: SERVIDOR WEB FLASK + AGENTE LLM (VÍA GROQ API)
# =============================================================================

import os
import re
import unicodedata
from flask import Flask, render_template, request, jsonify
from groq import Groq

import conocimiento as kb

app = Flask(__name__)

#  API Key Groq 
API_KEY = os.environ.get("GROQ_API_KEY", "")

def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def precalcular_inferencia(pregunta: str) -> str:
    """
    Detecta entidades en la pregunta (créditos, agente, distancia) y ejecuta
    las reglas lógicas exactas de Python para entregárselas resueltas al LLM.
    """
    texto_limpio = limpiar_texto(pregunta)
    palabras = re.findall(r'\w+', texto_limpio)

    numeros = [int(p) for p in palabras if p.isdigit()]
    creditos = numeros[0] if numeros else None
    agente = next((p for p in palabras if p in kb.AGENTES), None)

    if any(p in palabras for p in ["larga", "lejos", "largo"]):
        distancia = "larga"
    elif any(p in palabras for p in ["corta", "cerca", "corto", "media"]):
        distancia = "corta"
    else:
        distancia = "corta"

    notas_calculadas = []

    if creditos is not None:
        if not kb.creditos_validos(creditos):
            notas_calculadas.append(f"[CÁLCULO DEL MOTOR LÓGICO]: Créditos={creditos} es INVÁLIDO (debe estar entre 0 y 9000).")
        else:
            t_ronda = kb.tipo_ronda(creditos)
            notas_calculadas.append(f"[CÁLCULO DEL MOTOR LÓGICO]: Para {creditos} créditos, el tipo de ronda es '{t_ronda}'.")
            if agente:
                plan = kb.recomendar_plan(creditos, agente, distancia)
                notas_calculadas.append(f"[PLAN EXACTO CALCULADO]: {plan}")

    return "\n".join(notas_calculadas)

def limpiar_etiquetas_pensamiento(texto: str) -> str:
    """Elimina bloques <think>...</think> si el modelo razonador los incluye."""
    return re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL).strip()

def consultar_llm(pregunta_usuario: str) -> str:
    """Envía la consulta al LLM controlando max_tokens para no exceder límites gratuitos."""
    contexto_kb = kb.obtener_contexto_para_llm()
    inferencia_previa = precalcular_inferencia(pregunta_usuario)

    system_instruction = f"""Eres el 'Chatbot Asesor de VALORANT', un agente inteligente desarrollado para el curso Fundamentos de Inteligencia Artificial en la UNAB.
Tu única fuente de verdad es la siguiente BASE DE CONOCIMIENTO ESTRICTA:

{contexto_kb}

REGLAS DE COMPORTAMIENTO:
1. Responde de manera natural, clara, concisa y estructurada en español (directo al grano, sin rodeos).
2. Usa ÚNICAMENTE los hechos y reglas de la base de conocimiento proporcionada.
3. Si el usuario pregunta por un agente o arma que NO está en la lista, indícale amablemente que no se encuentra en tu base de conocimiento.
4. Si se te entrega un [PLAN EXACTO CALCULADO] o [CÁLCULO DEL MOTOR LÓGICO], DEBES usar exactamente esos números (arma, gasto de utilidad, escudo y saldo restante) sin alterarlos.
5. Si el usuario hace una pregunta fuera del dominio de Valorant, recuérdale que solo eres un experto en economía y equipamiento de Valorant.
"""

    prompt_final = pregunta_usuario
    if inferencia_previa:
        prompt_final += f"\n\n---\nDatos verificados por el motor de reglas interno:\n{inferencia_previa}"

    mensajes = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt_final}
    ]

    if API_KEY and API_KEY.startswith("gsk_"):
        try:
            client = Groq(api_key=API_KEY)

            todos = [m.id for m in client.models.list().data]
            excluidos = ["whisper", "tts", "guard", "orpheus", "playai", "embed", "vision"]
            candidatos = [m for m in todos if not any(ex in m.lower() for ex in excluidos)]

            # Priorizar modelos Llama e instruct que tienen límites de tokens más altos
            candidatos.sort(key=lambda x: (
                0 if "llama" in x.lower() else
                1 if "gemma" in x.lower() or "mixtral" in x.lower() else
                2 if "qwen" in x.lower() else 3
            ))

            ultimo_error = ""
            for mod in candidatos:
                try:
                    completion = client.chat.completions.create(
                        model=mod,
                        messages=mensajes,
                        temperature=0.1,
                        max_tokens=350,  # <-- Evita el error 429 (Limit 1000 OTPM)
                    )
                    respuesta_raw = completion.choices[0].message.content
                    return limpiar_etiquetas_pensamiento(respuesta_raw)
                except Exception as err_mod:
                    ultimo_error = str(err_mod)
                    continue

            return f"⚠️ Límite temporal alcanzado ({ultimo_error}).\n\n{motor_respaldo_local(pregunta_usuario)}"
        except Exception as e:
            return f"⚠️ Error al conectar con el LLM ({str(e)}).\n\n{motor_respaldo_local(pregunta_usuario)}"
    else:
        return motor_respaldo_local(pregunta_usuario)

def motor_respaldo_local(pregunta: str) -> str:
    texto = limpiar_texto(pregunta)
    ps = re.findall(r'\w+', texto)

    numeros = [int(p) for p in ps if p.isdigit()]
    creds = numeros[0] if numeros else None
    agente = next((p for p in ps if p in kb.AGENTES), None)
    arma = next((p for p in ps if p in kb.ARMAS), None)
    dist = "larga" if any(x in ps for x in ["larga", "lejos"]) else "corta"

    if any(x in ps for x in ["hola", "buenas", "hey"]):
        return "¡Hola! Pregúntame sobre compras, armas, agentes o precios en Valorant."

    if any(x in ps for x in ["compro", "comprar", "plan", "recomiendas"]) and creds is not None and agente:
        plan = kb.recomendar_plan(creds, agente, dist)
        if "error" in plan:
            return plan["error"]
        return (f"--- PLAN RECOMENDADO (Modo Local) ---\n"
                f"• Agente: {plan['agente'].capitalize()} ({plan['rol']})\n"
                f"• Tipo de ronda: {plan['tipo_ronda']}\n"
                f"• Arma sugerida: {plan['arma_sugerida'].capitalize()} ({plan['costo_arma']} cr.)\n"
                f"• Gasto utilidad: {plan['gasto_utilidad']} créditos\n"
                f"• Blindaje: {plan['blindaje']} ({plan['costo_blindaje']} cr.)\n"
                f"• Saldo restante: {plan['saldo_restante']} créditos")

    if arma and any(x in ps for x in ["cuesta", "precio", "costo", "vale", "tipo", "categoria"]):
        d = kb.ARMAS[arma]
        return f"La {arma.capitalize()} es un arma de tipo {d['tipo']}, cuesta {d['costo']} créditos y su alcance óptimo es a distancia {d['alcance']}."

    if agente and any(x in ps for x in ["rol", "comparte", "kit", "habilidades"]):
        d = kb.AGENTES[agente]
        otros = ", ".join(a.capitalize() for a in kb.mismo_rol(agente))
        return f"{agente.capitalize()} es {d['rol']} (comparten rol: {otros}) y su kit completo cuesta {d['costo_kit']} créditos."

    return "Intenta incluir un agente, un arma o tus créditos en la consulta."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    datos = request.get_json()
    mensaje_usuario = datos.get("mensaje", "").strip()
    if not mensaje_usuario:
        return jsonify({"respuesta": "Por favor escribe una consulta."})
    respuesta = consultar_llm(mensaje_usuario)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True, port=5000)