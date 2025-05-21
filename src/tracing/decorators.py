# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import functools
import inspect
from opentelemetry import trace
from opentelemetry.trace import SpanKind

logger = logging.getLogger(__name__)

def trace_agent(tracer):
    """Decorator to trace agent function calls.
    
    This decorator will create a span for each agent function call,
    recording the agent type and function name as attributes.
    
    Args:
        tracer: The DeerFlowTracer instance to use for tracing
        
    Returns:
        A decorator function that will wrap the agent function
    """
    def decorator(func):
        # Check if the function is async
        is_async = inspect.iscoroutinefunction(func)
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not tracer.enabled:
                    return await func(*args, **kwargs)
                
                # Extract agent_type from function's qualified name (Class.method)
                qualified_name = func.__qualname__
                agent_type = qualified_name.split(".")[0] if "." in qualified_name else "unknown"
                
                # Set span attributes
                attributes = {
                    "agent_type": agent_type,
                    "function_name": func.__name__
                }
                
                # Start span
                with tracer.start_span(
                    f"{agent_type}.{func.__name__}", 
                    kind=SpanKind.INTERNAL,
                    attributes=attributes
                ) as span:
                    try:
                        # Add agent invocation event
                        tracer.add_event(span, "agent_invocation_start")
                        
                        # Call the wrapped function
                        result = await func(*args, **kwargs)
                        
                        # Add agent completion event
                        tracer.add_event(span, "agent_invocation_end")
                        
                        return result
                    except Exception as e:
                        # Record exception in span
                        tracer.record_exception(span, e)
                        raise
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not tracer.enabled:
                    return func(*args, **kwargs)
                
                # Extract agent_type from function's qualified name (Class.method)
                qualified_name = func.__qualname__
                agent_type = qualified_name.split(".")[0] if "." in qualified_name else "unknown"
                
                # Set span attributes
                attributes = {
                    "agent_type": agent_type,
                    "function_name": func.__name__
                }
                
                # Start span
                with tracer.start_span(
                    f"{agent_type}.{func.__name__}", 
                    kind=SpanKind.INTERNAL,
                    attributes=attributes
                ) as span:
                    try:
                        # Add agent invocation event
                        tracer.add_event(span, "agent_invocation_start")
                        
                        # Call the wrapped function
                        result = func(*args, **kwargs)
                        
                        # Add agent completion event
                        tracer.add_event(span, "agent_invocation_end")
                        
                        return result
                    except Exception as e:
                        # Record exception in span
                        tracer.record_exception(span, e)
                        raise
            
            return sync_wrapper
            
    return decorator

