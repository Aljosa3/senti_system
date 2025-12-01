# FAZA 12 — Adaptive Memory Engine

**Location:** `senti_core_module/senti_memory/`
**Status:** ✅ Implemented
**Integration:** Senti OS Boot, AI Layer, Autonomous Task Loop

---

## Overview

FAZA 12 implements a three-layer adaptive memory system for Senti OS, enabling the system to maintain both short-term and long-term memory with automatic consolidation and intelligent management.

### Memory Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     MEMORY ENGINE                           │
│                   (High-Level API)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Working Memory  │  │   Episodic   │  │   Semantic   │  │
│  │  (Volatile)     │  │   Memory     │  │   Memory     │  │
│  │                 │  │ (Persistent) │  │ (Persistent) │  │
│  │ • TTL-based     │  │ • Time-      │  │ • Long-term  │  │
│  │ • Fast access   │  │   ordered    │  │   facts      │  │
│  │ • Auto-expire   │  │ • Events     │  │ • Knowledge  │  │
│  └─────────────────┘  └──────────────┘  └──────────────┘  │
│           │                  │                   │         │
│           └──────────────────┴───────────────────┘         │
│                              │                             │
├──────────────────────────────┼─────────────────────────────┤
│                      MEMORY STORE                          │
│                  (File-based JSON)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

### 1. Working Memory (`working_memory.py`)

**Purpose:** Short-term, volatile memory with automatic expiration

**Features:**
- TTL-based expiration (default: 3 minutes)
- Clears on system restart
- Thread-safe operations
- Fast in-memory access

**API:**
```python
working.add(key, value, ttl_seconds=180)
working.get(key)
working.remove(key)
working.cleanup_expired()
```

**Use Cases:**
- Temporary task state
- Active conversation context
- Session data
- Short-term caching

---

### 2. Episodic Memory (`episodic_memory.py`)

**Purpose:** Time-ordered event storage for system history

**Features:**
- Chronological event storage
- Category/type filtering
- Persistent storage
- Search capabilities

**API:**
```python
episodic.record(event_type, payload)
episodic.get_events(since=None, filter_type=None, limit=None)
episodic.prune_old_events(keep_count=1000)
```

**Use Cases:**
- System event logging
- Activity history
- Audit trail
- Pattern analysis

---

### 3. Semantic Memory (`semantic_memory.py`)

**Purpose:** Long-term consolidated knowledge storage

**Features:**
- Structured fact storage
- Pattern-based search
- Metadata support
- Fact merging and deduplication

**API:**
```python
semantic.save_fact(key, value, metadata=None)
semantic.get_fact(key)
semantic.search(pattern)
semantic.get_facts_by_metadata(key, value)
```

**Use Cases:**
- System knowledge base
- Learned patterns
- Configuration facts
- Historical insights

---

## Core Components

### Memory Store (`memory_store.py`)

Physical storage layer with:
- Atomic file writes (temp + rename)
- Thread-safe operations
- JSON serialization
- Separate episodic/semantic files

### Memory Rules (`memory_rules.py`)

FAZA 8 Security integration:
- Size limit validation
- Sensitive data detection
- Action whitelisting
- Privacy guards

**Limits:**
- Working memory: 1 MB per item
- Episodic events: 512 KB per event
- Semantic facts: 2 MB per fact
- Max episodic events: 100,000
- Max semantic facts: 50,000

### Memory Events (`memory_events.py`)

EventBus integration for:
- `memory.added` - Memory item stored
- `memory.retrieved` - Memory item accessed
- `memory.consolidated` - Consolidation completed
- `memory.cleaned` - Cleanup performed
- `memory.error` - Error occurred

### Consolidation Service (`consolidation_service.py`)

Converts episodic → semantic memory:

**Process:**
1. Analyze episodic events
2. Extract patterns and facts
3. Store in semantic memory
4. Prune old episodic events

**Triggered by:**
- Autonomous Task Loop (every ~1 minute)
- Manual invocation
- System maintenance

---

## Memory Engine (`memory_engine.py`)

High-level unified API used by AI agents and system components.

### Unified Remember API

```python
engine.remember(
    data={"key": "value"},
    memory_type="working",  # or "episodic" or "semantic"
    key="optional_key",
    ttl_seconds=180,
    event_type="optional_event_type",
    metadata={"source": "ai_agent"}
)
```

### Unified Recall API

```python
result = engine.recall(
    query="search_term",
    memory_type="semantic",
    event_type_filter=None,
    limit=10
)
# Returns: {"status": "success", "found": True, "data": [...]}
```

### Other Operations

```python
# Consolidation
engine.consolidate(min_events=10)

# Cleanup
engine.cleanup_working()

# Statistics
stats = engine.get_memory_stats()
health = engine.get_memory_health()
```

---

## Memory Manager (`memory_manager.py`)

Lifecycle orchestration and service registration.

### Initialization

```python
from senti_core_module.senti_memory import MemoryManager

manager = MemoryManager(
    project_root=Path("/path/to/project"),
    event_bus=event_bus,
    logger=logger
)

# Start system
result = manager.start()

# Get engine for use
engine = manager.get_engine()
```

### Maintenance

```python
# Called periodically by Autonomous Task Loop
result = manager.perform_maintenance()
# - Cleans up expired working memory
# - Consolidates episodic → semantic
# - Checks system health
```

---

## Integration Points

### 1. Boot System (`senti_os/boot/boot.py`)

```python
# Initialize after core
self.memory_manager = MemoryManager(self.project_root, self.core_event_bus, self.logger)
memory_init_result = self.memory_manager.start()

# Register as service
self.services.register_service("memory_manager", self.memory_manager)

# Pass to AI layer
ai_layer = setup_ai_operational_layer(
    ...,
    memory_manager=self.memory_manager
)
```

### 2. AI Layer (`senti_os/ai/os_ai_bootstrap.py`)

```python
def setup_ai_operational_layer(..., memory_manager=None):
    # Memory manager available to AI agents
    return {
        ...,
        "memory_manager": memory_manager
    }
```

### 3. Autonomous Task Loop (`senti_os/system/autonomous_task_loop_service.py`)

```python
# Periodic maintenance (every 12 iterations ≈ 1 minute)
if self._memory_manager and self._loop_count % 12 == 0:
    self._memory_manager.perform_maintenance()
```

---

## Usage Examples

### Example 1: AI Agent Remembering Context

```python
# Get engine from AI layer
memory_engine = ai_layer["memory_manager"].get_engine()

# Remember user context
memory_engine.remember(
    data={"user": "Alice", "task": "code_review", "status": "in_progress"},
    memory_type="working",
    key="current_task",
    ttl_seconds=600  # 10 minutes
)

# Recall later
result = memory_engine.recall("current_task", memory_type="working")
if result["found"]:
    context = result["data"]
    print(f"Resuming task: {context['task']}")
```

### Example 2: Logging System Events

```python
# Record significant events
memory_engine.remember(
    data={
        "action": "module_loaded",
        "module": "senti_expansion",
        "success": True,
        "duration_ms": 123
    },
    memory_type="episodic",
    event_type="system.module_lifecycle"
)
```

### Example 3: Learning System Patterns

```python
# After consolidation, semantic facts are created
result = memory_engine.recall("event_type_frequency", memory_type="semantic")
if result["found"]:
    frequency = result["data"]
    print(f"Most common event: {frequency}")
```

### Example 4: Manual Consolidation

```python
# Consolidate episodic events into semantic knowledge
result = memory_engine.consolidate(min_events=20)
print(f"Consolidated {result['events_processed']} events into {result['facts_created']} facts")
```

---

## Memory Lifecycle

### 1. Boot Sequence

```
1. Core initialized
2. MemoryManager created with EventBus
3. MemoryStore initialized (file storage)
4. Working, Episodic, Semantic layers initialized
5. MemoryRules loaded (FAZA 8)
6. MemoryEvents connected to EventBus
7. ConsolidationService configured
8. MemoryEngine created
9. Manager registered as OS service
10. Passed to AI layer
```

### 2. Runtime Operations

```
Continuous:
├─ Working memory: TTL expiration checks
├─ Episodic memory: Event recording
└─ Semantic memory: Fact storage

Every ~1 minute (Autonomous Loop):
├─ Cleanup expired working memory
├─ Consolidate episodic → semantic
└─ Health checks

On demand:
├─ AI agent memory operations
├─ Manual consolidation
└─ Stats/health queries
```

### 3. Shutdown

```
1. Clear working memory (volatile)
2. Persist episodic events to disk
3. Persist semantic facts to disk
4. Close file handles
5. Cleanup complete
```

---

## Data Flow

### Remember Flow

```
AI Agent/System Component
         ↓
   MemoryEngine.remember()
         ↓
   MemoryRules.validate()
         ↓
   [Working/Episodic/Semantic].add()
         ↓
   MemoryStore.save() [if persistent]
         ↓
   MemoryEvents.publish_memory_added()
         ↓
   EventBus → Subscribers
```

### Recall Flow

```
AI Agent/System Component
         ↓
   MemoryEngine.recall()
         ↓
   [Working/Episodic/Semantic].get()
         ↓
   MemoryEvents.publish_memory_retrieved()
         ↓
   Return data to caller
```

### Consolidation Flow

```
Autonomous Task Loop (periodic)
         ↓
   ConsolidationService.consolidate()
         ↓
   EpisodicMemory.get_events()
         ↓
   Extract patterns & facts
         ↓
   SemanticMemory.save_fact() (multiple)
         ↓
   EpisodicMemory.prune_old_events()
         ↓
   MemoryEvents.publish_memory_consolidated()
```

---

## Security Considerations (FAZA 8 Integration)

### Validation Rules

1. **Size Limits:** Prevent memory exhaustion
2. **Sensitive Data:** Detect and block passwords, keys, PII
3. **Action Whitelist:** Only allowed operations permitted
4. **Key Validation:** Prevent path traversal, injection
5. **Access Control:** Only whitelisted components can access

### Sensitive Pattern Detection

Automatically blocked:
- Social security numbers
- Credit card numbers
- Passwords in plain text
- API keys and secrets
- Email addresses (configurable)

---

## Performance Characteristics

### Working Memory
- **Read:** O(1) - Direct dict access
- **Write:** O(1) - Direct dict write
- **Cleanup:** O(n) - Scan all items

### Episodic Memory
- **Record:** O(1) - Append to list + file write
- **Retrieve:** O(n) - Filter/search
- **Prune:** O(n log n) - Sort + slice

### Semantic Memory
- **Save:** O(1) - Dict write + file write
- **Get:** O(1) - Dict access
- **Search:** O(n) - Regex scan

### Consolidation
- **Complexity:** O(n) where n = episodic events
- **Frequency:** Every ~1 minute
- **Duration:** Typically < 100ms for 1000 events

---

## Testing

Run comprehensive test suite:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH \
python3 tests/test_faza12_memory.py
```

### Test Coverage

- ✅ Working memory add/retrieve/expiration
- ✅ Episodic memory record/retrieve/filter
- ✅ Semantic memory save/retrieve/search
- ✅ Memory rules validation
- ✅ EventBus integration
- ✅ Consolidation service
- ✅ Memory engine unified API
- ✅ Memory manager lifecycle

---

## Troubleshooting

### Issue: Memory not persisting

**Solution:** Check that MemoryManager was properly started:
```python
result = manager.start()
print(result)  # Should be {"status": "success"}
```

### Issue: Working memory items disappearing

**Cause:** TTL expiration (default 3 minutes)
**Solution:** Use longer TTL or move to episodic/semantic:
```python
engine.remember(data, memory_type="working", ttl_seconds=600)
```

### Issue: Consolidation not running

**Check:**
1. Autonomous Task Loop is running
2. Memory manager passed to loop
3. Enough episodic events (min_events threshold)

### Issue: EventBus events not firing

**Verify:** EventBus properly connected:
```python
manager = MemoryManager(project_root, event_bus, logger)
# event_bus must be valid instance
```

---

## Future Enhancements

Planned for future FAZA phases:

- **FAZA 18:** Encryption for semantic memory storage
- **FAZA 20:** Distributed memory for multi-node systems
- **FAZA 22:** Neural memory embeddings for semantic search
- **FAZA 25:** Automatic memory optimization based on usage patterns

---

## API Reference

### MemoryEngine

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `remember()` | data, memory_type, key, ttl_seconds, event_type, metadata | dict | Store data in memory |
| `recall()` | query, memory_type, event_type_filter, limit | dict | Retrieve data from memory |
| `consolidate()` | min_events | dict | Trigger consolidation |
| `cleanup_working()` | - | dict | Clean expired items |
| `get_memory_stats()` | - | dict | Get statistics |
| `get_memory_health()` | - | dict | Get health status |

### MemoryManager

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start()` | - | dict | Initialize memory system |
| `stop()` | - | dict | Shutdown memory system |
| `get_engine()` | - | MemoryEngine | Get engine instance |
| `perform_maintenance()` | - | dict | Run maintenance tasks |
| `get_stats()` | - | dict | Get system statistics |
| `get_health()` | - | dict | Get system health |

---

## Conclusion

FAZA 12 provides Senti OS with a sophisticated, multi-layered memory system that enables:

- ✅ Short-term working memory for active tasks
- ✅ Event-based episodic history
- ✅ Long-term semantic knowledge
- ✅ Automatic consolidation
- ✅ Security integration (FAZA 8)
- ✅ EventBus integration
- ✅ AI layer accessibility
- ✅ Autonomous maintenance

The system is production-ready and fully integrated with Senti OS architecture.
