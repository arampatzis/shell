"""Installer package for handling different types of tool installations."""

from .base import Installer
from .binary import BinaryInstaller
from .script import ScriptInstaller
from .symlinker import SymlinkerInstaller
from .source import SourceInstaller

__all__ = [
    "Installer",
    "BinaryInstaller",
    "ScriptInstaller",
    "SymlinkerInstaller",
    "SourceInstaller",
]
