"""Unit tests for cathodescope.config.settings.

9 tests covering settings loading, env var handling, JSON merging, and validation.
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cathodescope.config.settings import CathodescopeSettings


def test_settings_loads_defaults_when_no_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings load default values when no config file is provided."""
    monkeypatch.setenv("MP_API_KEY", "test-key-123")
    settings = CathodescopeSettings.load()
    assert settings.relaxation.fmax == 0.01
    assert settings.relaxation.max_steps == 500
    assert settings.comparison.lattice_tolerance == 2.0
    assert settings.comparison.volume_tolerance == 5.0
    assert settings.validation.min_bond == 1.0
    assert settings.validation.max_bond == 4.0


def test_settings_reads_mp_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings read MP_API_KEY from the MP_API_KEY environment variable."""
    monkeypatch.setenv("MP_API_KEY", "my-secret-api-key-abc")
    settings = CathodescopeSettings.load()
    assert settings.mp_api_key == "my-secret-api-key-abc"


def test_settings_missing_mp_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings raises a clear ValueError when MP_API_KEY is not set."""
    monkeypatch.delenv("MP_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MP_API_KEY"):
        CathodescopeSettings.load()


def test_settings_load_from_json_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Settings load and apply values from a JSON config file."""
    monkeypatch.setenv("MP_API_KEY", "test-key-123")
    config = {"relaxation": {"fmax": 0.05, "max_steps": 200}}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    settings = CathodescopeSettings.load(config_path=config_file)
    assert settings.relaxation.fmax == 0.05
    assert settings.relaxation.max_steps == 200


def test_settings_json_partial_override_preserves_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Partial JSON override only changes specified fields; all others keep defaults."""
    monkeypatch.setenv("MP_API_KEY", "test-key-123")
    config = {"relaxation": {"fmax": 0.05}}
    config_file = tmp_path / "partial.json"
    config_file.write_text(json.dumps(config))
    settings = CathodescopeSettings.load(config_path=config_file)
    assert settings.relaxation.fmax == 0.05
    # unspecified sub-field must still be default
    assert settings.relaxation.max_steps == 500
    # unspecified sub-config must still be default
    assert settings.comparison.lattice_tolerance == 2.0
    assert settings.comparison.volume_tolerance == 5.0


def test_settings_invalid_fmax_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Settings raises ValidationError when fmax is not positive (fmax=0)."""
    monkeypatch.setenv("MP_API_KEY", "test-key-123")
    bad_config = {"relaxation": {"fmax": 0.0}}
    config_file = tmp_path / "bad.json"
    config_file.write_text(json.dumps(bad_config))
    with pytest.raises(ValidationError):
        CathodescopeSettings.load(config_path=config_file)


def test_settings_invalid_tolerance_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Settings raises ValidationError when lattice_tolerance is negative."""
    monkeypatch.setenv("MP_API_KEY", "test-key-123")
    bad_config = {"comparison": {"lattice_tolerance": -1.0}}
    config_file = tmp_path / "bad_tol.json"
    config_file.write_text(json.dumps(bad_config))
    with pytest.raises(ValidationError):
        CathodescopeSettings.load(config_path=config_file)


def test_strict_config_file_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """The strict_config.json fixture has tighter tolerances than defaults."""
    monkeypatch.setenv("MP_API_KEY", "test-key-123")
    strict_path = (
        Path(__file__).parent.parent.parent
        / "fixtures"
        / "configs"
        / "strict_config.json"
    )
    settings = CathodescopeSettings.load(config_path=strict_path)
    assert settings.comparison.lattice_tolerance < 2.0
    assert settings.comparison.volume_tolerance < 5.0
    assert settings.relaxation.fmax < 0.01


def test_settings_serializes_to_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings round-trips through JSON serialization without loss."""
    monkeypatch.setenv("MP_API_KEY", "test-key-abc")
    settings = CathodescopeSettings.load()
    json_str = settings.model_dump_json()
    assert '"mp_api_key"' in json_str
    assert '"fmax"' in json_str
    assert '"lattice_tolerance"' in json_str
