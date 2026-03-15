# Agente AWS con Strands Agents

Agente conversacional especializado en arquitecturas AWS, construido con [Strands Agents](https://strandsagents.com).


## Setup

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   pip install strands-agents strands-agents-tools boto3
   ```

2. Configurar credenciales:
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales AWS
   ```

3. Ejecutar el agente:
   ```bash
   python agent.py
   ```

## Herramientas disponibles

- `estimar_costo_lambda` — Calcula el costo mensual de AWS Lambda
- `recomendar_arquitectura` — Recomienda arquitecturas AWS por caso de uso
- `buscar_servicio_aws` — Lista servicios AWS por categoría

## Estructura

```
.
├── agent.py      # Agente principal con historial de conversación
├── tools.py      # Herramientas personalizadas con @tool
├── requirements.txt
├── .env.example
└── historial.json  # Generado automáticamente al conversar
```
