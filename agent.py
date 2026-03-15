import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from strands import Agent
from strands_tools import calculator, current_time
from tools import buscar_servicio_aws, estimar_costo_lambda, recomendar_arquitectura

load_dotenv()

HISTORIAL_PATH = Path("historial.json")

# Model ID con cross-region inference (us-east-1 o us-west-2)
agent = Agent(
    model="arn:aws:bedrock:us-east-1:709052122064:application-inference-profile/a538dapui09k",
    tools=[
        estimar_costo_lambda,
        recomendar_arquitectura,
        buscar_servicio_aws,
        calculator,
        current_time,
    ],
    system_prompt=(
        "Eres un arquitecto de soluciones AWS experto. Siempre respondes en español. "
        "Tienes acceso a las siguientes capacidades:\n"
        "- estimar_costo_lambda: calcula el costo mensual de AWS Lambda\n"
        "- recomendar_arquitectura: sugiere arquitecturas AWS por caso de uso\n"
        "- buscar_servicio_aws: lista servicios AWS por categoría\n"
        "- calculator: realiza cálculos matemáticos\n"
        "- current_time: obtiene la fecha y hora actual"
    ),
)


def cargar_historial() -> list[dict]:
    """Carga el historial desde historial.json. Retorna lista vacía si no existe."""
    if HISTORIAL_PATH.exists():
        with HISTORIAL_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def guardar_entrada(historial: list[dict], pregunta: str, respuesta: str) -> None:
    """Agrega una entrada al historial y persiste el archivo JSON."""
    historial.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "respuesta": respuesta,
    })
    with HISTORIAL_PATH.open("w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)


def mostrar_resumen(historial: list[dict]) -> None:
    """Muestra un resumen del historial cargado al iniciar."""
    total = len(historial)
    if total == 0:
        print("Sin historial previo.\n")
        return

    primera = historial[0]["timestamp"][:10]
    ultima = historial[-1]["timestamp"][:10]
    print(f"Historial cargado: {total} conversación(es) entre {primera} y {ultima}.")
    print("Últimas 3 preguntas:")
    for entrada in historial[-3:]:
        ts = entrada["timestamp"][:16].replace("T", " ")
        pregunta_corta = entrada["pregunta"][:60]
        sufijo = "..." if len(entrada["pregunta"]) > 60 else ""
        print(f"  [{ts}] {pregunta_corta}{sufijo}")
    print()


def main():
    historial = cargar_historial()
    mostrar_resumen(historial)
    print("Agente listo. Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            break
        if not user_input:
            continue

        response = agent(user_input)
        respuesta_str = str(response)
        print(f"Agente: {respuesta_str}\n")

        guardar_entrada(historial, user_input, respuesta_str)


if __name__ == "__main__":
    main()