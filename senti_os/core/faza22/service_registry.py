"""
FAZA 22 - Service Registry

Central registry for all FAZA stacks and services.

Responsibilities:
- Maintain mapping of all FAZA stack classes
- Provide singleton boot manager access
- Health check aggregation
- Stack metadata and information
- Dependency resolution

Stack Mapping:
    faza21 -> FAZA21Stack (Persistence Layer)
    faza19 -> FAZA19Stack (UIL & Multi-Device)
    faza20 -> FAZA20Stack (User Experience Layer)
    faza17 -> OrchestrationManager (Multi-Model Orchestration)
    faza16 -> LLMManager (LLM Control Layer)
    faza18 -> Auth Flow utilities

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, Optional, Type, List, Callable
from dataclasses import dataclass
from enum import Enum


class StackType(Enum):
    """Type of FAZA stack."""
    PERSISTENCE = "persistence"
    COMMUNICATION = "communication"
    ORCHESTRATION = "orchestration"
    CONTROL = "control"
    AUTH = "auth"
    EXPERIENCE = "experience"


@dataclass
class StackMetadata:
    """Metadata about a FAZA stack."""
    name: str
    faza_number: int
    display_name: str
    description: str
    stack_type: StackType
    has_start_method: bool
    has_stop_method: bool
    has_status_method: bool
    dependencies: List[str]
    factory_function: Optional[Callable] = None


class ServiceRegistry:
    """
    Central registry for all FAZA stacks and services.

    Provides unified access to stack information, factory functions,
    and manages the singleton boot manager instance.
    """

    # Stack metadata registry
    STACK_REGISTRY: Dict[str, StackMetadata] = {
        "faza21": StackMetadata(
            name="faza21",
            faza_number=21,
            display_name="FAZA 21 - Persistence Layer",
            description="Secure encrypted persistent storage with GDPR compliance",
            stack_type=StackType.PERSISTENCE,
            has_start_method=False,
            has_stop_method=True,
            has_status_method=True,
            dependencies=[],
            factory_function=None  # Loaded dynamically
        ),
        "faza19": StackMetadata(
            name="faza19",
            faza_number=19,
            display_name="FAZA 19 - UIL & Multi-Device Communication",
            description="Unified Interaction Layer with zero-trust architecture",
            stack_type=StackType.COMMUNICATION,
            has_start_method=True,
            has_stop_method=True,
            has_status_method=True,
            dependencies=["faza21"],
            factory_function=None
        ),
        "faza20": StackMetadata(
            name="faza20",
            faza_number=20,
            display_name="FAZA 20 - User Experience Layer",
            description="Human-centered interaction and observability",
            stack_type=StackType.EXPERIENCE,
            has_start_method=True,
            has_stop_method=True,
            has_status_method=True,
            dependencies=["faza21", "faza19", "faza16", "faza17", "faza18"],
            factory_function=None
        ),
        "faza17": StackMetadata(
            name="faza17",
            faza_number=17,
            display_name="FAZA 17 - Multi-Model Orchestration",
            description="Complex task orchestration across multiple models",
            stack_type=StackType.ORCHESTRATION,
            has_start_method=False,
            has_stop_method=False,
            has_status_method=True,
            dependencies=["faza16"],
            factory_function=None
        ),
        "faza16": StackMetadata(
            name="faza16",
            faza_number=16,
            display_name="FAZA 16 - LLM Control Layer",
            description="LLM management and knowledge verification",
            stack_type=StackType.CONTROL,
            has_start_method=False,
            has_stop_method=False,
            has_status_method=True,
            dependencies=[],
            factory_function=None
        ),
        "faza18": StackMetadata(
            name="faza18",
            faza_number=18,
            display_name="FAZA 18 - Auth Flow Handler",
            description="Secure authentication flow with privacy guarantees",
            stack_type=StackType.AUTH,
            has_start_method=False,
            has_stop_method=False,
            has_status_method=False,
            dependencies=[],
            factory_function=None
        ),
    }

    def __init__(self):
        """Initialize service registry."""
        self._boot_manager_instance: Optional[Any] = None
        self._stack_factories_loaded = False

    def get_stack_metadata(self, stack_name: str) -> Optional[StackMetadata]:
        """
        Get metadata for a specific stack.

        Args:
            stack_name: Name of stack (e.g., "faza21").

        Returns:
            StackMetadata or None if not found.
        """
        return self.STACK_REGISTRY.get(stack_name)

    def get_all_stacks(self) -> List[str]:
        """
        Get list of all registered stack names.

        Returns:
            List of stack names.
        """
        return list(self.STACK_REGISTRY.keys())

    def get_stack_dependencies(self, stack_name: str) -> List[str]:
        """
        Get dependencies for a stack.

        Args:
            stack_name: Name of stack.

        Returns:
            List of dependency stack names.
        """
        metadata = self.get_stack_metadata(stack_name)
        if metadata:
            return metadata.dependencies
        return []

    def get_stacks_by_type(self, stack_type: StackType) -> List[str]:
        """
        Get all stacks of a specific type.

        Args:
            stack_type: Type of stacks to retrieve.

        Returns:
            List of stack names matching the type.
        """
        return [
            name for name, metadata in self.STACK_REGISTRY.items()
            if metadata.stack_type == stack_type
        ]

    def load_stack_factories(self) -> bool:
        """
        Load factory functions for all stacks.

        Returns:
            True if all factories loaded successfully.
        """
        if self._stack_factories_loaded:
            return True

        success = True

        # Load FAZA 21
        try:
            from senti_os.core.faza21 import FAZA21Stack
            self.STACK_REGISTRY["faza21"].factory_function = lambda storage_dir: FAZA21Stack(storage_dir)
        except ImportError as e:
            success = False

        # Load FAZA 19
        try:
            from senti_os.core.faza19 import FAZA19Stack
            self.STACK_REGISTRY["faza19"].factory_function = lambda: FAZA19Stack()
        except ImportError as e:
            success = False

        # Load FAZA 20
        try:
            from senti_os.core.faza20 import FAZA20Stack
            self.STACK_REGISTRY["faza20"].factory_function = lambda **kwargs: FAZA20Stack(**kwargs)
        except ImportError as e:
            success = False

        # Load FAZA 17
        try:
            from senti_os.core.faza17 import create_orchestration_manager
            self.STACK_REGISTRY["faza17"].factory_function = lambda: create_orchestration_manager()
        except ImportError as e:
            success = False

        # Load FAZA 16
        try:
            from senti_os.core.faza16 import create_manager
            self.STACK_REGISTRY["faza16"].factory_function = lambda: create_manager()
        except ImportError as e:
            success = False

        # FAZA 18 is utility collection, no factory needed
        self.STACK_REGISTRY["faza18"].factory_function = lambda: None

        self._stack_factories_loaded = success
        return success

    def create_stack_instance(
        self,
        stack_name: str,
        **kwargs
    ) -> Optional[Any]:
        """
        Create an instance of a stack.

        Args:
            stack_name: Name of stack to create.
            **kwargs: Arguments to pass to factory function.

        Returns:
            Stack instance or None if failed.
        """
        if not self._stack_factories_loaded:
            self.load_stack_factories()

        metadata = self.get_stack_metadata(stack_name)
        if not metadata or not metadata.factory_function:
            return None

        try:
            if stack_name == "faza21":
                storage_dir = kwargs.get("storage_dir", "/home/pisarna/senti_system/data/faza21")
                return metadata.factory_function(storage_dir)
            elif stack_name == "faza20":
                return metadata.factory_function(**kwargs)
            else:
                return metadata.factory_function()
        except Exception as e:
            return None

    def get_boot_manager(
        self,
        storage_dir: str = "/home/pisarna/senti_system/data/faza21",
        **kwargs
    ) -> Any:
        """
        Get or create singleton boot manager instance.

        Args:
            storage_dir: Directory for FAZA 21 persistent storage.
            **kwargs: Additional boot manager configuration.

        Returns:
            BootManager instance.
        """
        if self._boot_manager_instance is None:
            from senti_os.core.faza22.boot_manager import BootManager

            self._boot_manager_instance = BootManager(
                storage_dir=storage_dir,
                **kwargs
            )

        return self._boot_manager_instance

    def reset_boot_manager(self):
        """Reset boot manager singleton (useful for testing)."""
        self._boot_manager_instance = None

    def check_stack_health(self, stack_instance: Any) -> Dict[str, Any]:
        """
        Check health of a stack instance.

        Args:
            stack_instance: Stack instance to check.

        Returns:
            Dictionary with health information.
        """
        health_info = {
            "has_instance": stack_instance is not None,
            "has_status_method": False,
            "status": None,
            "error": None
        }

        if stack_instance is None:
            return health_info

        # Check if has status method
        if hasattr(stack_instance, 'get_status'):
            health_info["has_status_method"] = True
            try:
                health_info["status"] = stack_instance.get_status()
            except Exception as e:
                health_info["error"] = str(e)
        elif hasattr(stack_instance, 'get_stack_status'):
            health_info["has_status_method"] = True
            try:
                health_info["status"] = stack_instance.get_stack_status()
            except Exception as e:
                health_info["error"] = str(e)

        return health_info

    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the service registry.

        Returns:
            Dictionary with registry information.
        """
        return {
            "total_stacks": len(self.STACK_REGISTRY),
            "factories_loaded": self._stack_factories_loaded,
            "boot_manager_active": self._boot_manager_instance is not None,
            "stacks": {
                name: {
                    "faza_number": metadata.faza_number,
                    "display_name": metadata.display_name,
                    "description": metadata.description,
                    "stack_type": metadata.stack_type.value,
                    "has_start_method": metadata.has_start_method,
                    "has_stop_method": metadata.has_stop_method,
                    "has_status_method": metadata.has_status_method,
                    "dependencies": metadata.dependencies,
                    "factory_loaded": metadata.factory_function is not None
                }
                for name, metadata in self.STACK_REGISTRY.items()
            }
        }

    def validate_boot_order(self, boot_order: List[str]) -> Dict[str, Any]:
        """
        Validate a proposed boot order against dependencies.

        Args:
            boot_order: Proposed boot order.

        Returns:
            Dictionary with validation results.
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        seen_stacks = set()

        for stack_name in boot_order:
            # Check if stack exists
            if stack_name not in self.STACK_REGISTRY:
                validation["valid"] = False
                validation["errors"].append(
                    f"Unknown stack: {stack_name}"
                )
                continue

            # Check dependencies
            dependencies = self.get_stack_dependencies(stack_name)
            for dep in dependencies:
                if dep not in seen_stacks:
                    validation["valid"] = False
                    validation["errors"].append(
                        f"Stack {stack_name} depends on {dep}, "
                        f"but {dep} appears later in boot order"
                    )

            seen_stacks.add(stack_name)

        # Check for missing stacks
        all_stacks = set(self.STACK_REGISTRY.keys())
        missing_stacks = all_stacks - seen_stacks
        if missing_stacks:
            validation["warnings"].append(
                f"Stacks not in boot order: {', '.join(missing_stacks)}"
            )

        return validation

    def get_stack_info_summary(self, stack_name: str) -> str:
        """
        Get a formatted summary of stack information.

        Args:
            stack_name: Name of stack.

        Returns:
            Formatted string with stack information.
        """
        metadata = self.get_stack_metadata(stack_name)
        if not metadata:
            return f"Unknown stack: {stack_name}"

        lines = [
            f"Stack: {metadata.display_name}",
            f"FAZA: {metadata.faza_number}",
            f"Type: {metadata.stack_type.value}",
            f"Description: {metadata.description}",
            f"Dependencies: {', '.join(metadata.dependencies) if metadata.dependencies else 'None'}",
            f"Capabilities:",
            f"  - Start: {'Yes' if metadata.has_start_method else 'No'}",
            f"  - Stop: {'Yes' if metadata.has_stop_method else 'No'}",
            f"  - Status: {'Yes' if metadata.has_status_method else 'No'}"
        ]

        return "\n".join(lines)


# Global registry instance
_service_registry_instance: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """
    Get or create service registry singleton.

    Returns:
        ServiceRegistry instance.
    """
    global _service_registry_instance

    if _service_registry_instance is None:
        _service_registry_instance = ServiceRegistry()

    return _service_registry_instance


def reset_service_registry():
    """Reset service registry singleton (useful for testing)."""
    global _service_registry_instance
    _service_registry_instance = None
