"""
LLM Config Loader for SENTI OS FAZA 16

Reads and validates LLM configuration from llm_config.json.
Supports environment variable references using ENV: prefix.
Validates schema and normalizes configuration for system use.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a single LLM model."""
    model_id: str
    provider: str
    model_name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_token: float = 0.0
    enabled: bool = True
    roles: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """Complete LLM configuration."""
    models: List[ModelConfig]
    default_model: Optional[str] = None
    fallback_chain: List[str] = field(default_factory=list)
    health_check_interval: int = 300
    max_retries: int = 3
    timeout: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class LLMConfigLoader:
    """
    Loads and validates LLM configuration from JSON files.

    Features:
    - Schema validation
    - Environment variable substitution (ENV:VAR_NAME)
    - Default value handling
    - Configuration normalization
    """

    REQUIRED_MODEL_FIELDS = ["model_id", "provider", "model_name"]
    VALID_PROVIDERS = ["openai", "anthropic", "google", "local", "custom"]

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            config_path: Path to llm_config.json (defaults to ~/senti_system/llm_config.json)
        """
        if config_path is None:
            config_path = os.path.expanduser("~/senti_system/llm_config.json")

        self.config_path = Path(config_path)
        self.config: Optional[LLMConfig] = None
        logger.info(f"LLM Config Loader initialized with path: {self.config_path}")

    def load_config(self) -> LLMConfig:
        """
        Load and validate configuration from file.

        Returns:
            LLMConfig instance

        Raises:
            ConfigValidationError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return self._create_default_config()

        try:
            with open(self.config_path, 'r') as f:
                raw_config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigValidationError(f"Failed to read config file: {e}")

        self._validate_schema(raw_config)

        self.config = self._parse_config(raw_config)

        logger.info(f"Loaded configuration with {len(self.config.models)} models")
        return self.config

    def _validate_schema(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration schema.

        Args:
            config: Raw configuration dictionary

        Raises:
            ConfigValidationError: If schema is invalid
        """
        if "models" not in config:
            raise ConfigValidationError("Configuration must contain 'models' field")

        if not isinstance(config["models"], list):
            raise ConfigValidationError("'models' must be a list")

        if len(config["models"]) == 0:
            raise ConfigValidationError("At least one model must be defined")

        for idx, model in enumerate(config["models"]):
            if not isinstance(model, dict):
                raise ConfigValidationError(f"Model {idx} must be a dictionary")

            for field in self.REQUIRED_MODEL_FIELDS:
                if field not in model:
                    raise ConfigValidationError(
                        f"Model {idx} missing required field: {field}"
                    )

            provider = model.get("provider", "").lower()
            if provider not in self.VALID_PROVIDERS:
                logger.warning(
                    f"Model {idx} has unknown provider: {provider}. Valid: {self.VALID_PROVIDERS}"
                )

    def _parse_config(self, raw_config: Dict[str, Any]) -> LLMConfig:
        """
        Parse and normalize configuration.

        Args:
            raw_config: Raw configuration dictionary

        Returns:
            LLMConfig instance
        """
        models = []

        for model_data in raw_config["models"]:
            model = ModelConfig(
                model_id=model_data["model_id"],
                provider=model_data["provider"].lower(),
                model_name=model_data["model_name"],
                api_key=self._resolve_env_var(model_data.get("api_key")),
                endpoint=model_data.get("endpoint"),
                max_tokens=model_data.get("max_tokens", 4096),
                temperature=model_data.get("temperature", 0.7),
                cost_per_token=model_data.get("cost_per_token", 0.0),
                enabled=model_data.get("enabled", True),
                roles=model_data.get("roles", []),
                capabilities=model_data.get("capabilities", []),
                metadata=model_data.get("metadata", {}),
            )
            models.append(model)

        config = LLMConfig(
            models=models,
            default_model=raw_config.get("default_model"),
            fallback_chain=raw_config.get("fallback_chain", []),
            health_check_interval=raw_config.get("health_check_interval", 300),
            max_retries=raw_config.get("max_retries", 3),
            timeout=raw_config.get("timeout", 30),
            metadata=raw_config.get("metadata", {}),
        )

        return config

    def _resolve_env_var(self, value: Optional[str]) -> Optional[str]:
        """
        Resolve environment variable references.

        Args:
            value: Value that may contain ENV: prefix

        Returns:
            Resolved value or None
        """
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        if value.startswith("ENV:"):
            env_var = value[4:].strip()
            resolved = os.getenv(env_var)

            if resolved is None:
                logger.warning(f"Environment variable not found: {env_var}")
            else:
                logger.debug(f"Resolved ENV:{env_var}")

            return resolved

        return value

    def _create_default_config(self) -> LLMConfig:
        """
        Create default configuration when no file exists.

        Returns:
            Default LLMConfig instance
        """
        logger.info("Creating default configuration")

        default_model = ModelConfig(
            model_id="local_default",
            provider="local",
            model_name="local-llm",
            enabled=True,
            max_tokens=4096,
            cost_per_token=0.0,
            roles=["general"],
            capabilities=["text_generation"],
        )

        return LLMConfig(
            models=[default_model],
            default_model="local_default",
            fallback_chain=["local_default"],
        )

    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """
        Get configuration for a specific model.

        Args:
            model_id: Model identifier

        Returns:
            ModelConfig or None if not found
        """
        if self.config is None:
            self.load_config()

        for model in self.config.models:
            if model.model_id == model_id:
                return model

        return None

    def get_models_by_role(self, role: str) -> List[ModelConfig]:
        """
        Get all models that support a specific role.

        Args:
            role: Role name (e.g., "code_generation", "reasoning")

        Returns:
            List of ModelConfig instances
        """
        if self.config is None:
            self.load_config()

        return [
            model for model in self.config.models
            if role in model.roles and model.enabled
        ]

    def get_models_by_capability(self, capability: str) -> List[ModelConfig]:
        """
        Get all models with a specific capability.

        Args:
            capability: Capability name

        Returns:
            List of ModelConfig instances
        """
        if self.config is None:
            self.load_config()

        return [
            model for model in self.config.models
            if capability in model.capabilities and model.enabled
        ]

    def get_enabled_models(self) -> List[ModelConfig]:
        """
        Get all enabled models.

        Returns:
            List of enabled ModelConfig instances
        """
        if self.config is None:
            self.load_config()

        return [model for model in self.config.models if model.enabled]

    def reload_config(self) -> LLMConfig:
        """
        Reload configuration from file.

        Returns:
            Updated LLMConfig instance
        """
        logger.info("Reloading configuration")
        return self.load_config()


def create_loader(config_path: Optional[str] = None) -> LLMConfigLoader:
    """
    Create and return a configured LLM config loader.

    Args:
        config_path: Optional path to config file

    Returns:
        LLMConfigLoader instance
    """
    loader = LLMConfigLoader(config_path)
    loader.load_config()
    return loader
