# Archivo generado automáticamente por el hook de Kiro al guardar agent.py.
# Última actualización: 2026-03-15 (model actualizado: arn:aws:bedrock:us-east-2:394072825848:application-inference-profile/l1xiytcm6srx)
# Nota: los tests llaman tools.py directamente, sin instanciar Agent.
# Pruebas unitarias para las herramientas definidas en tools.py.

import pytest
from tools import buscar_servicio_aws, estimar_costo_lambda, recomendar_arquitectura


# ---------------------------------------------------------------------------
# estimar_costo_lambda
# ---------------------------------------------------------------------------

class TestEstimarCostoLambda:

    def test_retorna_dict(self):
        result = estimar_costo_lambda(invocaciones=1_000_000, duracion_ms=200, memoria_mb=128)
        assert isinstance(result, dict)

    def test_campos_clave_presentes(self):
        result = estimar_costo_lambda(invocaciones=1_000_000, duracion_ms=200, memoria_mb=128)
        for campo in ("costo_requests_usd", "costo_computo_usd", "costo_total_usd",
                      "invocaciones", "duracion_ms", "memoria_mb", "gb_segundos_usados"):
            assert campo in result, f"Campo faltante: {campo}"

    def test_caso_feliz_valores_representativos(self):
        result = estimar_costo_lambda(invocaciones=5_000_000, duracion_ms=300, memoria_mb=512)
        assert result["costo_total_usd"] >= 0
        assert result["invocaciones"] == 5_000_000
        assert result["duracion_ms"] == 300
        assert result["memoria_mb"] == 512

    def test_dentro_del_tier_gratuito_costo_cero(self):
        # 500K invocaciones con mínima memoria/duración → dentro del free tier
        result = estimar_costo_lambda(invocaciones=500_000, duracion_ms=1, memoria_mb=128)
        assert result["costo_requests_usd"] == 0.0
        assert result["costo_computo_usd"] == 0.0
        assert result["costo_total_usd"] == 0.0

    def test_costo_total_es_suma_de_parciales(self):
        result = estimar_costo_lambda(invocaciones=10_000_000, duracion_ms=500, memoria_mb=1024)
        esperado = round(result["costo_requests_usd"] + result["costo_computo_usd"], 6)
        assert result["costo_total_usd"] == esperado

    def test_invocaciones_cero(self):
        result = estimar_costo_lambda(invocaciones=0, duracion_ms=200, memoria_mb=128)
        assert result["costo_total_usd"] == 0.0

    def test_duracion_cero(self):
        result = estimar_costo_lambda(invocaciones=5_000_000, duracion_ms=0, memoria_mb=128)
        assert result["costo_computo_usd"] == 0.0

    def test_memoria_maxima(self):
        result = estimar_costo_lambda(invocaciones=1_000_000, duracion_ms=100, memoria_mb=10240)
        assert isinstance(result["costo_total_usd"], float)
        assert result["memoria_mb"] == 10240

    def test_supera_free_tier_requests(self):
        # Más de 1M invocaciones → debe cobrar por requests
        result = estimar_costo_lambda(invocaciones=2_000_000, duracion_ms=1, memoria_mb=128)
        assert result["costo_requests_usd"] > 0.0

    def test_gb_segundos_calculados_correctamente(self):
        # 1M invocaciones × 1s × 0.125 GB = 125_000 GB-s (dentro del free tier de 400K)
        result = estimar_costo_lambda(invocaciones=1_000_000, duracion_ms=1000, memoria_mb=128)
        assert result["gb_segundos_usados"] == round(1_000_000 * 1.0 * (128 / 1024), 4)

    def test_supera_free_tier_computo(self):
        # 10M invocaciones × 1s × 0.125 GB = 1_250_000 GB-s → supera los 400K gratuitos
        result = estimar_costo_lambda(invocaciones=10_000_000, duracion_ms=1000, memoria_mb=128)
        assert result["costo_computo_usd"] > 0.0

    def test_duracion_ms_float(self):
        result = estimar_costo_lambda(invocaciones=1_000_000, duracion_ms=150.5, memoria_mb=256)
        assert isinstance(result["costo_total_usd"], float)
        assert result["duracion_ms"] == 150.5


# ---------------------------------------------------------------------------
# recomendar_arquitectura
# ---------------------------------------------------------------------------

class TestRecomendarArquitectura:

    def test_retorna_dict(self):
        result = recomendar_arquitectura(caso_de_uso="api_rest")
        assert isinstance(result, dict)

    def test_campos_clave_presentes(self):
        result = recomendar_arquitectura(caso_de_uso="api_rest")
        for campo in ("caso_de_uso", "descripcion", "servicios", "consideraciones"):
            assert campo in result, f"Campo faltante: {campo}"

    def test_servicios_es_lista(self):
        result = recomendar_arquitectura(caso_de_uso="streaming")
        assert isinstance(result["servicios"], list)
        assert len(result["servicios"]) > 0

    def test_consideraciones_es_lista(self):
        result = recomendar_arquitectura(caso_de_uso="ml_inference")
        assert isinstance(result["consideraciones"], list)
        assert len(result["consideraciones"]) > 0

    @pytest.mark.parametrize("caso", ["api_rest", "streaming", "ml_inference", "static_web", "batch"])
    def test_todos_los_casos_validos(self, caso):
        result = recomendar_arquitectura(caso_de_uso=caso)
        assert "error" not in result
        assert result["caso_de_uso"] == caso

    def test_caso_invalido_retorna_error(self):
        result = recomendar_arquitectura(caso_de_uso="caso_inexistente")
        assert "error" in result
        assert "casos_validos" in result
        assert isinstance(result["casos_validos"], list)

    def test_caso_invalido_no_lanza_excepcion(self):
        result = recomendar_arquitectura(caso_de_uso="")
        assert isinstance(result, dict)
        assert "error" in result

    def test_caso_con_mayusculas_normalizado(self):
        result = recomendar_arquitectura(caso_de_uso="API_REST")
        assert "error" not in result
        assert result["caso_de_uso"] == "api_rest"

    def test_caso_con_espacios_normalizado(self):
        result = recomendar_arquitectura(caso_de_uso="  batch  ")
        assert "error" not in result
        assert result["caso_de_uso"] == "batch"

    def test_api_rest_incluye_lambda(self):
        result = recomendar_arquitectura(caso_de_uso="api_rest")
        assert "AWS Lambda" in result["servicios"]

    def test_static_web_incluye_cloudfront(self):
        result = recomendar_arquitectura(caso_de_uso="static_web")
        assert "CloudFront" in result["servicios"]

    def test_casos_validos_en_error_son_cinco(self):
        result = recomendar_arquitectura(caso_de_uso="invalido")
        assert len(result["casos_validos"]) == 5

    def test_batch_incluye_step_functions(self):
        result = recomendar_arquitectura(caso_de_uso="batch")
        assert "Step Functions" in result["servicios"]

    def test_ml_inference_incluye_sagemaker(self):
        result = recomendar_arquitectura(caso_de_uso="ml_inference")
        assert "Amazon SageMaker" in result["servicios"]

    def test_streaming_incluye_kinesis(self):
        result = recomendar_arquitectura(caso_de_uso="streaming")
        assert "Amazon Kinesis" in result["servicios"]


# ---------------------------------------------------------------------------
# buscar_servicio_aws
# ---------------------------------------------------------------------------

class TestBuscarServicioAws:

    def test_retorna_dict(self):
        result = buscar_servicio_aws(categoria="compute")
        assert isinstance(result, dict)

    def test_campos_clave_presentes(self):
        result = buscar_servicio_aws(categoria="compute")
        for campo in ("categoria", "descripcion", "servicios"):
            assert campo in result, f"Campo faltante: {campo}"

    def test_servicios_es_dict(self):
        result = buscar_servicio_aws(categoria="storage")
        assert isinstance(result["servicios"], dict)
        assert len(result["servicios"]) > 0

    @pytest.mark.parametrize("cat", ["compute", "storage", "database", "ai", "networking"])
    def test_todas_las_categorias_validas(self, cat):
        result = buscar_servicio_aws(categoria=cat)
        assert "error" not in result
        assert result["categoria"] == cat

    def test_categoria_invalida_retorna_error(self):
        result = buscar_servicio_aws(categoria="categoria_inexistente")
        assert "error" in result
        assert "categorias_validas" in result
        assert isinstance(result["categorias_validas"], list)

    def test_categoria_invalida_no_lanza_excepcion(self):
        result = buscar_servicio_aws(categoria="")
        assert isinstance(result, dict)
        assert "error" in result

    def test_categoria_con_mayusculas_normalizada(self):
        result = buscar_servicio_aws(categoria="COMPUTE")
        assert "error" not in result
        assert result["categoria"] == "compute"

    def test_categoria_con_espacios_normalizada(self):
        result = buscar_servicio_aws(categoria="  ai  ")
        assert "error" not in result
        assert result["categoria"] == "ai"

    def test_compute_contiene_lambda(self):
        result = buscar_servicio_aws(categoria="compute")
        assert "AWS Lambda" in result["servicios"]

    def test_compute_contiene_ec2(self):
        result = buscar_servicio_aws(categoria="compute")
        assert "EC2" in result["servicios"]

    def test_database_contiene_aurora(self):
        result = buscar_servicio_aws(categoria="database")
        assert "Aurora" in result["servicios"]

    def test_database_contiene_dynamodb(self):
        result = buscar_servicio_aws(categoria="database")
        assert "DynamoDB" in result["servicios"]

    def test_networking_contiene_cloudfront(self):
        result = buscar_servicio_aws(categoria="networking")
        assert "CloudFront" in result["servicios"]

    def test_storage_contiene_s3(self):
        result = buscar_servicio_aws(categoria="storage")
        assert "S3" in result["servicios"]

    def test_ai_contiene_bedrock(self):
        result = buscar_servicio_aws(categoria="ai")
        assert "Amazon Bedrock" in result["servicios"]

    def test_categorias_validas_en_error_son_cinco(self):
        result = buscar_servicio_aws(categoria="invalida")
        assert len(result["categorias_validas"]) == 5

    def test_descripcion_es_string_no_vacio(self):
        result = buscar_servicio_aws(categoria="networking")
        assert isinstance(result["descripcion"], str)
        assert len(result["descripcion"]) > 0
