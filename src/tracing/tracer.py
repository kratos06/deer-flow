# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace import SpanKind

from .config import get_tracing_config

logger = logging.getLogger(__name__)

class DeerFlowTracer:
    """OpenTelemetry tracer wrapper for DeerFlow.
    
    This class provides a simplified interface to OpenTelemetry tracing
    functionality specifically tailored for DeerFlow's multi-agent system.
    """
    
    def __init__(self, service_name=None):
        """Initialize the tracer with configuration from conf.yaml.
        
        Args:
            service_name: Optional override for the service name.
                          If not provided, uses the name from config.
        """
        config = get_tracing_config()
        self.enabled = config.get("enabled", False)
        
        if not self.enabled:
            logger.info("Tracing is disabled. Set TRACING.enabled=true in conf.yaml to enable.")
            return
            
        self.service_name = service_name or config.get("service_name", "deerflow")
        self.endpoint = config.get("endpoint", "http://localhost:4317")
        self.sampling_rate = config.get("sampling_rate", 1.0)
        
        self._init_tracer()
        logger.info(f"DeerFlow tracer initialized for service '{self.service_name}'")
    
    def _init_tracer(self):
        """Initialize the OpenTelemetry tracer with configured parameters."""
        if not self.enabled:
            return
            
        try:
            # Create a resource to identify the service
            resource = Resource.create({"service.name": self.service_name})
            
            # Create the tracer provider with the resource
            tracer_provider = TracerProvider(resource=resource)
            
            # Create an OTLP exporter to send spans to Jaeger
            otlp_exporter = OTLPSpanExporter(endpoint=self.endpoint)
            
            # Create a BatchSpanProcessor for efficient span processing
            span_processor = BatchSpanProcessor(otlp_exporter)
            
            # Add the span processor to the tracer provider
            tracer_provider.add_span_processor(span_processor)
            
            # Set the global tracer provider
            trace.set_tracer_provider(tracer_provider)
            
            # Get a tracer from the provider
            self.tracer = trace.get_tracer(__name__)
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry tracer: {e}")
            self.enabled = False
    
    def trace_event(self, name, metadata=None):
        """Record an event without creating a separate span.
        
        This is a convenience method that creates a small span just to record the event,
        then immediately ends it.
        
        Args:
            name: Name of the event
            metadata: Optional dict of event attributes
        """
        if not self.enabled:
            return
            
        try:
            with self.start_span(f"event.{name}", kind=SpanKind.INTERNAL) as span:
                if metadata:
                    # Convert any non-serializable objects to strings
                    safe_metadata = {}
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool, type(None))):
                            safe_metadata[key] = value
                        else:
                            safe_metadata[key] = str(value)
                    
                    span.set_attributes(safe_metadata)
        except Exception as e:
            logger.error(f"Failed to record trace event: {e}")
    
    def start_span(self, name, context=None, kind=None, attributes=None):
        """Start a new span with the given name and attributes.
        
        Args:
            name: Name of the span
            context: Optional context for the span
            kind: Optional span kind (defaults to SpanKind.INTERNAL)
            attributes: Optional dict of span attributes
            
        Returns:
            The created span, or a no-op span if tracing is disabled
        """
        if not self.enabled:
            # Return a dummy context manager if tracing is disabled
            return _DummySpan()
            
        # Default to INTERNAL kind if not specified
        if kind is None:
            kind = SpanKind.INTERNAL
            
        return self.tracer.start_as_current_span(
            name, 
            context=context, 
            kind=kind, 
            attributes=attributes or {}
        )
    
    def record_exception(self, span, exception):
        """Record an exception in the given span.
        
        Args:
            span: The span to record the exception in
            exception: The exception to record
        """
        if not self.enabled or not span:
            return
            
        span.record_exception(exception)
        span.set_status(Status(StatusCode.ERROR))
        
    def add_event(self, span, name, attributes=None):
        """Add an event to the given span.
        
        Args:
            span: The span to add the event to
            name: The name of the event
            attributes: Optional dict of event attributes
        """
        if not self.enabled or not span:
            return
            
        span.add_event(name, attributes=attributes or {})


class _DummySpan:
    """A dummy context manager to use when tracing is disabled."""
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def record_exception(self, exception):
        pass
        
    def add_event(self, name, attributes=None):
        pass
        
    def set_status(self, status):
        pass

