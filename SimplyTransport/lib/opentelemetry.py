from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from . import settings

# Don't enable OpenTelemetry in tests or development
if settings.app.ENVIRONMENT in ["PROD"]:
    resource = Resource(
        attributes={
            SERVICE_NAME: settings.app.NAME,
            SERVICE_VERSION: settings.app.VERSION,
            "service.debug": settings.app.DEBUG,
            "service.log_level": settings.app.LOG_LEVEL,
            DEPLOYMENT_ENVIRONMENT: settings.app.ENVIRONMENT,
        }
    )

    trace_provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
    trace_provider.add_span_processor(processor)
    trace.set_tracer_provider(trace_provider)

    reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics"))
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

open_telemetry_config = OpenTelemetryConfig()
open_telemetry_plugin = OpenTelemetryPlugin(config=open_telemetry_config)
