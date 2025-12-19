# MODULE REGISTRY SCHEMA

This document defines the normative structure of module entries in the Module Registry.

---

## PURPOSE OF THIS SCHEMA

This schema establishes the required fields and their meaning for module declarations.

The schema is descriptive, not executable.

---

## WHAT THE MODULE REGISTRY IS

The Module Registry is:
- a declarative record of module existence
- a structured documentation artifact
- an architectural reference for module state
- a canonical source of module metadata

The registry describes what exists, not what should happen.

---

## WHAT THE MODULE REGISTRY IS NOT

The Module Registry is NOT:
- runtime logic
- validation code
- an execution system
- a configuration loader
- an inference engine
- a decision-making system

The registry does not interpret, execute, or enforce.

---

## REQUIRED FIELDS

### `module_id`

**Type:** String

**Purpose:** Unique identifier for the module.

**Constraints:** Must be unique across all registry entries.

---

### `name`

**Type:** String

**Purpose:** Human-readable name of the module.

---

### `description`

**Type:** String

**Purpose:** Concise explanation of the module's purpose and role.

---

### `lifecycle`

**Type:** Object

**Purpose:** Declares the current lifecycle state of the module.

**Required subfield:**
- `status`: One of `DESIGN`, `ACTIVE`, `DEPRECATED`, `RETIRED`

**Meaning:**
- `DESIGN`: Module is being defined but not yet implemented
- `ACTIVE`: Module is implemented and available for use
- `DEPRECATED`: Module is discouraged for new use but remains supported
- `RETIRED`: Module is no longer available or maintained

---

### `scope`

**Type:** Object

**Purpose:** Defines what the module does and does not encompass.

**Required subfields:**
- `includes`: List of strings describing included capabilities or responsibilities
- `excludes`: List of strings describing explicitly excluded concerns

**Intent:** Establishes semantic boundaries.

---

### `capabilities`

**Type:** List of strings

**Purpose:** Enumerates the capabilities the module provides.

**Constraint:** Capabilities are descriptive, not procedural.

---

### `governance`

**Type:** Object

**Purpose:** Records the origin and authority of the module declaration.

**Required subfields:**
- `declared_by`: Human or process responsible for the declaration
- `declared_at`: Date of declaration in `YYYY-MM-DD` format
- `version`: Version identifier for the module

---

## PROHIBITED CONTENT

The Module Registry must NOT contain:
- code
- logic
- conditions
- execution instructions
- inference rules
- runtime behavior definitions

Any such content violates the declarative nature of the registry.

---

## INTERPRETATION PRINCIPLE

When reading this schema, plain language meaning prevails.

The registry serves architectural clarity, not operational automation.
