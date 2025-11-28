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

### 2. `senti_core/` - Core Application Layer
The main application framework:
- **api/** - External interfaces and API endpoints
- **runtime/** - Runtime environment and execution context
- **services/** - Business logic and application services
- **utils/** - Shared utilities and helper functions

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
- Dependencies should flow from modules → senti_core → senti_os

### Layer Responsibilities
- **senti_os**: Low-level abstractions, no business logic
- **senti_core**: Application framework, orchestration, and service coordination
- **modules**: Domain-specific functionality, should be hot-swappable where possible
