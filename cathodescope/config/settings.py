"""Settings loader for CathodeScope.

Provides pydantic config models for each configuration domain and a top-level
CathodescopeSettings model with a load() classmethod that:
- reads MP_API_KEY from the environment (never hardcoded)
- loads an optional JSON override file
- merges the override with defaults (fields not in the JSON keep their defaults)
- validates all values via pydantic

Implemented in T-05.
"""

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cathodescope.config.defaults import (
    DEFAULT_BENCHMARK_MATERIALS,
    DEFAULT_CACHE_DIR,
    DEFAULT_FMAX,
    DEFAULT_LATTICE_TOLERANCE,
    DEFAULT_MAX_BOND,
    DEFAULT_MAX_STEPS,
    DEFAULT_MIN_BOND,
    DEFAULT_OPTIMIZER,
    DEFAULT_REPORT_INDENT,
    DEFAULT_VOLUME_TOLERANCE,
)

# ---------------------------------------------------------------------------
# Sub-config models
# ---------------------------------------------------------------------------


class RelaxationConfig(BaseModel):
    """Configuration for MACE-MP-0 structure relaxation via ASE."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"fmax": 0.01, "max_steps": 500, "optimizer": "BFGS"}
        }
    )

    fmax: float = Field(
        default=DEFAULT_FMAX,
        gt=0,
        description="Force convergence criterion in eV/Å.",
    )
    max_steps: int = Field(
        default=DEFAULT_MAX_STEPS,
        gt=0,
        description="Maximum number of relaxation steps.",
    )
    optimizer: str = Field(
        default=DEFAULT_OPTIMIZER,
        description="ASE optimizer class name (e.g. 'BFGS', 'FIRE').",
    )


class ComparisonConfig(BaseModel):
    """Configuration for lattice/volume comparison against MP references."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"lattice_tolerance": 2.0, "volume_tolerance": 5.0}
        }
    )

    lattice_tolerance: float = Field(
        default=DEFAULT_LATTICE_TOLERANCE,
        ge=0,
        description=(
            "Maximum allowed lattice parameter deviation from MP reference (%)."
        ),
    )
    volume_tolerance: float = Field(
        default=DEFAULT_VOLUME_TOLERANCE,
        ge=0,
        description="Maximum allowed unit-cell volume deviation from MP reference (%).",
    )


class ValidationConfig(BaseModel):
    """Configuration for structural validation checks."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"min_bond": 1.0, "max_bond": 4.0}}
    )

    min_bond: float = Field(
        default=DEFAULT_MIN_BOND,
        gt=0,
        description="Minimum allowed interatomic distance in Å.",
    )
    max_bond: float = Field(
        default=DEFAULT_MAX_BOND,
        gt=0,
        description="Maximum allowed interatomic distance for bond detection in Å.",
    )


class ReportConfig(BaseModel):
    """Configuration for report generation."""

    model_config = ConfigDict(json_schema_extra={"example": {"indent": 2}})

    indent: int = Field(
        default=DEFAULT_REPORT_INDENT,
        ge=0,
        description="JSON indentation level for artifact and report files.",
    )


class CacheConfig(BaseModel):
    """Configuration for MP API response caching."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"cache_dir": "artifacts/cache/mp"}}
    )

    cache_dir: str = Field(
        default=DEFAULT_CACHE_DIR,
        description="Directory path for MP API cache files.",
    )


class BenchmarkConfig(BaseModel):
    """Configuration for benchmark runs."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"materials": ["mp-22526", "mp-19017", "mp-18767"]}
        }
    )

    materials: list[str] = Field(
        default_factory=lambda: list(DEFAULT_BENCHMARK_MATERIALS),
        description="Materials Project IDs to include in benchmark runs.",
    )


# ---------------------------------------------------------------------------
# Top-level settings
# ---------------------------------------------------------------------------


class CathodescopeSettings(BaseModel):
    """Top-level configuration model for CathodeScope.

    Contains all sub-configs as nested pydantic models. Use the
    ``load()`` classmethod to create an instance — it reads ``MP_API_KEY``
    from the environment and optionally merges a JSON override file.

    All fields not present in the JSON override file keep their default values.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mp_api_key": "<YOUR_MP_API_KEY>",
                "relaxation": {"fmax": 0.01, "max_steps": 500, "optimizer": "BFGS"},
                "comparison": {"lattice_tolerance": 2.0, "volume_tolerance": 5.0},
                "validation": {"min_bond": 1.0, "max_bond": 4.0},
                "report": {"indent": 2},
                "cache": {"cache_dir": "artifacts/cache/mp"},
                "benchmark": {"materials": ["mp-22526", "mp-19017", "mp-18767"]},
            }
        }
    )

    mp_api_key: str = Field(
        description=(
            "Materials Project API key. "
            "Set via MP_API_KEY environment variable; never hardcode this value."
        ),
    )
    relaxation: RelaxationConfig = Field(default_factory=RelaxationConfig)
    comparison: ComparisonConfig = Field(default_factory=ComparisonConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    benchmark: BenchmarkConfig = Field(default_factory=BenchmarkConfig)

    @classmethod
    def load(
        cls,
        config_path: Path | str | None = None,
    ) -> "CathodescopeSettings":
        """Load settings from environment and an optional JSON override file.

        Reads ``MP_API_KEY`` from the environment. If ``config_path`` is
        provided, loads that JSON file and uses it to override defaults.
        Fields absent from the JSON file keep their default values. All
        values are validated by pydantic after merging.

        Args:
            config_path: Optional path to a JSON configuration file.
                Fields in the file override defaults; absent fields keep
                their default values.

        Returns:
            A fully validated ``CathodescopeSettings`` instance.

        Raises:
            ValueError: If ``MP_API_KEY`` is not set or is empty.
            ValidationError: If any configuration value fails pydantic validation.
            FileNotFoundError: If ``config_path`` is given but does not exist.
            json.JSONDecodeError: If ``config_path`` is not valid JSON.
        """
        mp_api_key = os.environ.get("MP_API_KEY", "").strip()
        if not mp_api_key:
            raise ValueError(
                "MP_API_KEY environment variable is not set or is empty. "
                "Obtain a key at https://materialsproject.org/api and set it "
                "before using CathodeScope."
            )

        data: dict[str, Any] = {}
        if config_path is not None:
            data = json.loads(Path(config_path).read_text(encoding="utf-8"))

        return cls(mp_api_key=mp_api_key, **data)
