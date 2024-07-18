from . import settings

from litestar.contrib.opentelemetry import OpenTelemetryConfig

from opentelemetry.sdk.resources import SERVICE_NAME, Resource, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

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

    traceProvider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
    traceProvider.add_span_processor(processor)
    trace.set_tracer_provider(traceProvider)

    reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics"))
    meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meterProvider)

open_telemetry_config = OpenTelemetryConfig()
