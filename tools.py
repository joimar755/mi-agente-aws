from strands import tool


@tool
def estimar_costo_lambda(
    invocaciones: int,
    duracion_ms: float,
    memoria_mb: int,
) -> dict:
    """
    Calcula el costo mensual estimado de AWS Lambda.

    Utiliza el modelo de precios público de AWS Lambda:
    - Primeros 1M de requests gratis, luego $0.20 por millón.
    - Costo de cómputo basado en GB-segundos: $0.0000166667 por GB-s.
    - Incluye 400,000 GB-s gratuitos por mes.

    Args:
        invocaciones: Número total de invocaciones por mes.
        duracion_ms: Duración promedio de cada invocación en milisegundos.
        memoria_mb: Memoria asignada a la función en MB (128 a 10240).

    Returns:
        dict con costo_requests_usd, costo_computo_usd y costo_total_usd.
    """
    # Costo por requests
    requests_gratis = 1_000_000
    precio_por_millon = 0.20
    requests_facturables = max(0, invocaciones - requests_gratis)
    costo_requests = (requests_facturables / 1_000_000) * precio_por_millon

    # Costo de cómputo (GB-segundos)
    duracion_s = duracion_ms / 1000
    memoria_gb = memoria_mb / 1024
    gb_segundos = invocaciones * duracion_s * memoria_gb
    gb_segundos_gratis = 400_000
    gb_segundos_facturables = max(0, gb_segundos - gb_segundos_gratis)
    precio_por_gb_s = 0.0000166667
    costo_computo = gb_segundos_facturables * precio_por_gb_s

    costo_total = costo_requests + costo_computo

    return {
        "invocaciones": invocaciones,
        "duracion_ms": duracion_ms,
        "memoria_mb": memoria_mb,
        "gb_segundos_usados": round(gb_segundos, 4),
        "costo_requests_usd": round(costo_requests, 6),
        "costo_computo_usd": round(costo_computo, 6),
        "costo_total_usd": round(costo_total, 6),
    }


@tool
def recomendar_arquitectura(caso_de_uso: str) -> dict:
    """
    Devuelve una arquitectura AWS recomendada según el caso de uso.

    Casos de uso soportados:
    - api_rest: API HTTP/REST con baja latencia.
    - streaming: Procesamiento de eventos o datos en tiempo real.
    - ml_inference: Inferencia de modelos de machine learning.
    - static_web: Sitio web o SPA estático.
    - batch: Procesamiento por lotes o jobs programados.

    Args:
        caso_de_uso: Identificador del caso de uso. Valores válidos:
                     'api_rest', 'streaming', 'ml_inference', 'static_web', 'batch'.

    Returns:
        dict con los servicios recomendados, descripción y consideraciones clave.
    """
    arquitecturas = {
        "api_rest": {
            "descripcion": "API REST serverless de alta disponibilidad",
            "servicios": ["API Gateway", "AWS Lambda", "DynamoDB", "Cognito", "CloudWatch"],
            "consideraciones": [
                "Usar Lambda con Provisioned Concurrency para reducir cold starts",
                "DynamoDB on-demand para escalar automáticamente",
                "Cognito para autenticación y autorización",
                "API Gateway con caché para reducir latencia",
            ],
        },
        "streaming": {
            "descripcion": "Pipeline de procesamiento de eventos en tiempo real",
            "servicios": ["Amazon Kinesis", "AWS Lambda", "DynamoDB Streams", "S3", "CloudWatch"],
            "consideraciones": [
                "Kinesis Data Streams para ingesta de alto volumen",
                "Lambda como consumidor con batch window configurable",
                "S3 como destino final (data lake)",
                "Kinesis Firehose para entrega a S3/Redshift sin código",
            ],
        },
        "ml_inference": {
            "descripcion": "Endpoint de inferencia de modelos ML escalable",
            "servicios": ["Amazon SageMaker", "API Gateway", "Lambda", "S3", "ECR"],
            "consideraciones": [
                "SageMaker Endpoints para modelos grandes con GPU",
                "Lambda + ONNX para modelos ligeros sin servidor",
                "S3 para almacenar artefactos del modelo",
                "ECR para imágenes Docker con dependencias ML",
            ],
        },
        "static_web": {
            "descripcion": "Sitio web estático o SPA con distribución global",
            "servicios": ["S3", "CloudFront", "Route 53", "ACM", "Lambda@Edge"],
            "consideraciones": [
                "S3 como origen con acceso bloqueado directamente",
                "CloudFront para CDN global y HTTPS",
                "ACM para certificados SSL/TLS gratuitos",
                "Lambda@Edge para lógica en el borde (auth, redirects)",
            ],
        },
        "batch": {
            "descripcion": "Procesamiento por lotes y jobs programados",
            "servicios": ["AWS Batch", "Step Functions", "S3", "EventBridge", "CloudWatch"],
            "consideraciones": [
                "AWS Batch para jobs con alta demanda de cómputo",
                "Step Functions para orquestar flujos de trabajo complejos",
                "EventBridge Scheduler para ejecución programada",
                "S3 como almacenamiento de entrada/salida de jobs",
            ],
        },
    }

    caso = caso_de_uso.lower().strip()
    if caso not in arquitecturas:
        casos_validos = list(arquitecturas.keys())
        return {
            "error": f"Caso de uso '{caso_de_uso}' no reconocido.",
            "casos_validos": casos_validos,
        }

    resultado = arquitecturas[caso]
    return {"caso_de_uso": caso, **resultado}


@tool
def buscar_servicio_aws(categoria: str) -> dict:
    """
    Lista los principales servicios AWS disponibles por categoría.

    Categorías soportadas:
    - compute: Servicios de cómputo (servidores, contenedores, serverless).
    - storage: Almacenamiento de objetos, bloques y archivos.
    - database: Bases de datos relacionales, NoSQL y en memoria.
    - ai: Inteligencia artificial y machine learning gestionado.
    - networking: Redes, DNS, balanceo de carga y CDN.

    Args:
        categoria: Categoría de servicios a consultar. Valores válidos:
                   'compute', 'storage', 'database', 'ai', 'networking'.

    Returns:
        dict con la lista de servicios y una breve descripción de cada uno.
    """
    catalogo = {
        "compute": {
            "descripcion": "Servicios de cómputo en la nube",
            "servicios": {
                "EC2": "Máquinas virtuales escalables en la nube",
                "AWS Lambda": "Funciones serverless sin gestión de servidores",
                "ECS": "Orquestación de contenedores Docker gestionada",
                "EKS": "Kubernetes gestionado en AWS",
                "Fargate": "Cómputo serverless para contenedores (ECS/EKS)",
                "Lightsail": "VPS simplificado para proyectos pequeños",
                "Elastic Beanstalk": "PaaS para despliegue automático de aplicaciones",
            },
        },
        "storage": {
            "descripcion": "Servicios de almacenamiento",
            "servicios": {
                "S3": "Almacenamiento de objetos escalable y duradero",
                "EBS": "Volúmenes de bloque para instancias EC2",
                "EFS": "Sistema de archivos NFS gestionado y elástico",
                "S3 Glacier": "Archivado de datos de bajo costo a largo plazo",
                "FSx": "Sistemas de archivos gestionados (Windows, Lustre, NetApp)",
                "Storage Gateway": "Integración de almacenamiento on-premises con AWS",
            },
        },
        "database": {
            "descripcion": "Servicios de bases de datos gestionadas",
            "servicios": {
                "RDS": "Bases de datos relacionales gestionadas (MySQL, PostgreSQL, etc.)",
                "Aurora": "Base de datos relacional compatible con MySQL/PostgreSQL de alto rendimiento",
                "DynamoDB": "Base de datos NoSQL serverless de baja latencia",
                "ElastiCache": "Caché en memoria gestionado (Redis, Memcached)",
                "Redshift": "Data warehouse para análisis a escala de petabytes",
                "DocumentDB": "Base de datos de documentos compatible con MongoDB",
                "Neptune": "Base de datos de grafos gestionada",
                "Timestream": "Base de datos de series temporales serverless",
            },
        },
        "ai": {
            "descripcion": "Servicios de inteligencia artificial y machine learning",
            "servicios": {
                "Amazon Bedrock": "Modelos fundacionales de IA generativa vía API",
                "SageMaker": "Plataforma completa para entrenar y desplegar modelos ML",
                "Rekognition": "Análisis de imágenes y video con visión por computadora",
                "Comprehend": "Procesamiento de lenguaje natural (NLP)",
                "Transcribe": "Conversión de voz a texto (STT)",
                "Polly": "Conversión de texto a voz (TTS)",
                "Translate": "Traducción automática de idiomas",
                "Textract": "Extracción de texto y datos de documentos escaneados",
                "Forecast": "Predicciones de series temporales con ML",
            },
        },
        "networking": {
            "descripcion": "Servicios de redes y entrega de contenido",
            "servicios": {
                "VPC": "Red privada virtual aislada en AWS",
                "CloudFront": "CDN global para entrega de contenido con baja latencia",
                "Route 53": "DNS escalable y registro de dominios",
                "API Gateway": "Creación y gestión de APIs REST, HTTP y WebSocket",
                "Elastic Load Balancing": "Balanceo de carga entre instancias y servicios",
                "Direct Connect": "Conexión dedicada entre on-premises y AWS",
                "Transit Gateway": "Hub central para conectar VPCs y redes on-premises",
                "WAF": "Firewall de aplicaciones web para proteger APIs y sitios",
            },
        },
    }

    cat = categoria.lower().strip()
    if cat not in catalogo:
        categorias_validas = list(catalogo.keys())
        return {
            "error": f"Categoría '{categoria}' no reconocida.",
            "categorias_validas": categorias_validas,
        }

    return {"categoria": cat, **catalogo[cat]}
