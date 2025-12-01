# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Senti System is a modular system with an OS-like architecture. The codebase is currently in its initial setup phase with the following directory structure established.

## Architecture

The system is organized into three main layers:

### 1. `senti_os/` - Operating System Layer
The foundational layer providing system-level functionality:
- **boot/** - System initialization and startup procedures
- **kernel/** - Core system operations and process management
- **drivers/** - Hardware abstraction and device drivers
- **system/** - System-level services and utilities

### 2. `senti_core_module/` - Core Module Layer
A modular OS-level architecture containing:
- **senti_core/** - Core application framework (migrated)
  - **api/** - External interfaces and API endpoints
  - **runtime/** - Runtime environment and execution context
  - **services/** - Business logic and application services
  - **utils/** - Shared utilities and helper functions
- **senti_expansion/** - AI Expansion Engine (FAZA 10)
  - Dynamic module creation at runtime
  - AI-driven system expansion capabilities
  - Security-validated module generation
  - EventBus integration for expansion tracking
- **senti_refactor/** - Code refactoring and optimization modules
- **senti_memory_core/** - Memory management and persistence
- **senti_kernel/** - Additional kernel-level operations
- **senti_security_core/** - Core security modules

### 3. `modules/` - Modular Components
Pluggable functional modules:
- **sensors/** - Input and data collection modules
- **actuators/** - Output and action execution modules
- **processing/** - Data processing and transformation modules
- **communication/** - Inter-module and external communication

### Supporting Directories
- **config/** - Configuration files
- **scripts/** - Build, deployment, and utility scripts
- **tests/** - Test suites
- **docs/** - Documentation

## Development Guidelines

### Module Development
- Modules should be self-contained and follow a plugin architecture
- Each module category (sensors, actuators, processing, communication) should have a common interface
- Dependencies should flow from modules → senti_core_module → senti_os

### Layer Responsibilities
- **senti_os**: Low-level abstractions, no business logic
- **senti_core_module**: Modular OS-level architecture with specialized components
  - **senti_core**: Application framework, orchestration, and service coordination
  - **senti_expansion**: AI-driven expansion capabilities (FAZA 10)
    - Allows system to create new modules dynamically
    - Enforces security rules and validation
    - Integrates with AI Operational Layer
  - **senti_kernel**: Extended kernel operations
  - **senti_security_core**: Security framework
  - **senti_memory_core**: Memory management
  - **senti_refactor**: Code optimization tools
- **modules**: Domain-specific functionality, should be hot-swappable where possible

## FAZA System Integration

The Senti System implements multiple FAZA (phase) layers:

- **FAZA 5**: AI Operational Layer - AI agent orchestration and task management
- **FAZA 6**: Autonomous Task Loop - Self-directed system operations
- **FAZA 7**: Data Integrity Engine - Ensures data authenticity and validation
- **FAZA 8**: Security Manager - System-wide security policy enforcement
- **FAZA 10**: AI Expansion Engine - Dynamic module creation and system expansion

### FAZA 10 - AI Expansion Engine

Location: `senti_core_module/senti_expansion/`

The Expansion Engine enables the system to dynamically create new modules at runtime:

```python
from senti_core_module.senti_expansion import ExpansionManager

# Create new module via AI
manager.create_module(name="new_sensor", directory="modules/sensors")
```

**Key Features:**
- Secure module generation with name and directory validation
- Protected core directories (senti_os, senti_core_module)
- EventBus integration for expansion tracking
- Standardized module templates
- AI-driven expansion request handling

See `docs/FAZA_10_EXPANSION_ENGINE.md` for complete documentation.

## Getting Started

### Starting the System

```bash
# Option 1: Use launch script
./scripts/start_senti.sh

# Option 2: Manual start with PYTHONPATH
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 senti_os/boot/boot.py
```

### Testing FAZA 10

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza10_expansion.py
```

## Import Guidelines

All imports must use the new modular structure:

```python
# Correct
from senti_core_module.senti_core.services.event_bus import EventBus
from senti_core_module.senti_expansion import ExpansionManager

# Incorrect (old structure)
from senti_core.services.event_bus import EventBus
```

