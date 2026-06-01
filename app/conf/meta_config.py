from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnConfig:
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool
    examples: Optional[list] = None


@dataclass
class TableConfig:
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]
    layer: Optional[str] = None


@dataclass
class MetricConfig:
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]
    ambiguous: bool = False


@dataclass
class MetaConfig:
    tables: Optional[list[TableConfig]] = None
    metrics: Optional[list[MetricConfig]] = None
