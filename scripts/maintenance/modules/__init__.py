"""
Custom fix modules for the Unified Maintenance System.

Each module provides specialized fixes that can't be handled by standard tools.
"""


from .asyncio_patterns import AsyncioPatternFixModule
from .base import CustomFixModule, FixResult
from .docstrings import DocstringFixModule
from .exception_handling import ExceptionHandlingFixModule
from .imports import ImportFixModule
from .logging_patterns import LoggingPatternFixModule
from .performance import PerformanceFixModule
from .security import SecurityFixModule
from .type_annotations import TypeAnnotationFixModule

__all__ = [
    'CustomFixModule',
    'FixResult',
    'TypeAnnotationFixModule',
    'LoggingPatternFixModule',
    'ExceptionHandlingFixModule',
    'AsyncioPatternFixModule',
    'DocstringFixModule',
    'ImportFixModule',
    'SecurityFixModule',
    'PerformanceFixModule',
]

# Module registry
MODULE_REGISTRY = {
    'type_annotations': TypeAnnotationFixModule,
    'logging_patterns': LoggingPatternFixModule,
    'exception_handling': ExceptionHandlingFixModule,
    'asyncio_patterns': AsyncioPatternFixModule,
    'docstrings': DocstringFixModule,
    'imports': ImportFixModule,
    'security': SecurityFixModule,
    'performance': PerformanceFixModule,
}
