"""
CLI module

Command-line interface for the pipeline.

Exports:
    - build_arg_parser: Build CLI argument parser
    - main: Main entrypoint
"""

from .commands import build_arg_parser, main

__all__ = [
    "build_arg_parser",
    "main",
]

