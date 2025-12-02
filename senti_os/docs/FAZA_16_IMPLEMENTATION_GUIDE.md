# FAZA 16 Implementation Guide
## LLM Control Layer & Knowledge Verification Engine

**Version:** 1.0.0
**System:** SENTI OS
**Date:** December 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Integration Guide](#integration-guide)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

---

## Introduction

This guide provides comprehensive instructions for implementing and integrating FAZA 16 into SENTI OS or other Python-based systems. FAZA 16 is designed to be modular, extensible, and production-ready.

### Prerequisites

- Python 3.10 or higher
- SENTI OS core modules (optional but recommended)
- Basic understanding of LLM concepts
- Familiarity with Python dataclasses and type hints

### Design Philosophy

FAZA 16 follows these principles:
1. **Zero External Calls**: No network access without explicit consent
2. **Privacy First**: Automatic PII sanitization
3. **Transparent Decisions**: Every decision is logged and explainable
4. **Modular Architecture**: Each component works independently
5. **Regulatory Compliance**: GDPR, ZVOP, EU AI Act ready

---

## Installation

### Step 1: Verify Directory Structure

Ensure FAZA 16 is installed in the correct location:

```
/home/pisarna/senti_system/
├── senti_os/
│   ├── core/
│   │   └── faza16/
│   │       ├── __init__.py
│   │       ├── llm_manager.py
│   │       ├── source_registry.py
│   │       ├── subscription_detector.py
│   │       ├── llm_router.py
│   │       ├── llm_rules.py
│   │       ├── fact_check_engine.py
│   │       ├── knowledge_validation_engine.py
│   │       ├── cross_verification_layer.py
│   │       └── retrieval_connector.py
│   ├── tests/
│   │   └── faza16/
│   │       └── test_faza16_comprehensive.py
│   └── docs/
│       ├── FAZA_16_SPEC.md
│       └── FAZA_16_IMPLEMENTATION_GUIDE.md
```

### Step 2: Python Path Configuration

Add SENTI OS to your Python path:

```bash
export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH
```

Or in Python:

```python
import sys
sys.path.insert(0, '/home/pisarna/senti_system')
```

### Step 3: Verify Installation

```python
from senti_os.core.faza16 import get_info

print(get_info())
# Should print FAZA 16 module information
```

---

## Configuration

### Environment Variables

FAZA 16 detects API keys through environment variables:

```bash
# ChatGPT
export OPENAI_API_KEY="sk-your-key-here"

# Claude
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Gemini
export GOOGLE_API_KEY="your-key-here"

# Local LLM
export LOCAL_LLM_ENDPOINT="http://localhost:8080"
```

### Configuration Files

Create `/home/pisarna/senti_system/config/llm_config.json`:

```json
{
  "local_llm_endpoint": "http://localhost:8080",
  "default_priority_mode": "balanced",
  "max_cost_per_request": 1.0,
  "min_reliability_threshold": 0.7,
  "enable_pii_sanitization": true,
  "freshness_thresholds": {
    "current_days": 7,
    "recent_days": 30,
    "stale_days": 90,
    "outdated_days": 365
  }
}
```

---

## Basic Usage

### Example 1: Simple Request Processing

```python
from senti_os.core.faza16 import (
    create_manager,
    LLMRequest,
    TaskType,
    PriorityMode,
    RequestStatus,
)

# Initialize manager
manager = create_manager()

# Create request
request = LLMRequest(
    request_id="req_001",
    prompt="Analyze this sales data and identify trends",
    task_type=TaskType.ANALYSIS,
    priority_mode=PriorityMode.QUALITY,
    user_consent=True,  # User has given consent
    max_cost=0.5,  # Maximum $0.50 per request
)

# Process request
response = manager.process_request(request)

# Check response
if response.status == RequestStatus.APPROVED:
    print(f"✓ Approved")
    print(f"Source: {response.selected_source}")
    print(f"Reasoning: {response.routing_reasoning}")
    print(f"Decision log: {response.decision_log}")
elif response.status == RequestStatus.REJECTED:
    print(f"✗ Rejected: {response.error_message}")
    if response.rule_check_result:
        print(f"Violations: {len(response.rule_check_result.violations)}")
else:
    print(f"⚠ Failed: {response.error_message}")
```

### Example 2: Fact Checking

```python
from senti_os.core.faza16 import (
    create_fact_checker,
    Fact,
    FactType,
    FactCheckStatus,
)

# Initialize fact checker
checker = create_fact_checker()

# Create fact to check
fact = Fact(
    fact_id="fact_001",
    content="2 + 2 = 4",
    fact_type=FactType.NUMERICAL,
    source="user_input",
)

# Check fact
result = checker.check_fact(fact)

print(f"Status: {result.status.value}")
print(f"Confidence: {result.confidence}")
print(f"Explanation: {result.explanation}")
```

### Example 3: Knowledge Validation

```python
from senti_os.core.faza16 import (
    create_validator,
    KnowledgeEntry,
)
from datetime import datetime

# Initialize validator
validator = create_validator()

# Add knowledge entry
entry = KnowledgeEntry(
    entry_id="entry_001",
    content="Python 3.12 was released in October 2023",
    source="official_documentation",
    timestamp=datetime.now().isoformat(),
    domain="technology",
)

validator.add_knowledge(entry)

# Validate entry
result = validator.validate_entry("entry_001")

print(f"Status: {result.status.value}")
print(f"Freshness: {result.freshness.value}")
print(f"Confidence: {result.confidence}")
print(f"Issues: {result.issues}")
print(f"Recommendations: {result.recommendations}")
```

### Example 4: Cross-Verification

```python
from senti_os.core.faza16 import (
    create_verifier,
    SourceResponse,
    ConsensusLevel,
)

# Initialize verifier
verifier = create_verifier()

# Create responses from multiple sources
responses = [
    SourceResponse(
        source_id="source_a",
        content="The Earth orbits the Sun",
        confidence=0.95,
    ),
    SourceResponse(
        source_id="source_b",
        content="The Earth revolves around the Sun",
        confidence=0.93,
    ),
    SourceResponse(
        source_id="source_c",
        content="Earth goes around the Sun",
        confidence=0.90,
    ),
]

# Verify
result = verifier.verify(responses)

print(f"Consensus: {result.consensus_level.value}")
print(f"Confidence: {result.confidence_score}")
print(f"Aggregated: {result.aggregated_content}")
print(f"Discrepancies: {len(result.discrepancies)}")
print(f"Recommendations: {result.recommendations}")
```

---

## Advanced Usage

### Custom Rules

```python
from senti_os.core.faza16 import (
    create_default_rules_engine,
    RuleViolation,
    RuleViolationSeverity,
)

# Create engine
engine = create_default_rules_engine()

# Define custom rule
def check_company_policy(prompt, context, result):
    """Custom rule for company-specific policies."""
    forbidden_keywords = ["competitor_name", "confidential"]

    for keyword in forbidden_keywords:
        if keyword in prompt.lower():
            result.violations.append(
                RuleViolation(
                    rule_name="company_policy",
                    severity=RuleViolationSeverity.CRITICAL,
                    message=f"Policy violation: {keyword} detected",
                )
            )

# Add custom rule
engine.add_custom_rule(check_company_policy)

# Use engine
result = engine.check_all_rules("Analyze competitor_name strategy")
print(f"Passed: {result.passed}")
```

### Custom Source Registration

```python
from senti_os.core.faza16 import (
    create_default_registry,
    LLMSource,
    SourceDomain,
    SubscriptionLevel,
)

# Create registry
registry = create_default_registry()

# Register custom source
custom_source = LLMSource(
    source_id="company_llm",
    domain=SourceDomain.CUSTOM,
    api_key_present=True,
    subscription_level=SubscriptionLevel.ENTERPRISE,
    reliability_score=0.95,
    cost_estimate=0.0,  # Internal, no cost
    endpoint="https://internal.company.com/llm",
    model_name="company-gpt-v1",
    max_tokens=16384,
)

registry.register_source(custom_source)
print(f"Registered: {custom_source.source_id}")
```

### Secure Document Retrieval

```python
from senti_os.core.faza16 import (
    create_connector,
    RetrievalQuery,
)

# Create connector
connector = create_connector()

# Create query
query = RetrievalQuery(
    query_text="installation",
    max_results=5,
    sanitize_pii=True,  # Automatically redact PII
)

# Retrieve documents
result = connector.retrieve(query)

print(f"Found: {result.total_found} documents")
for doc in result.documents:
    print(f"- {doc.document_id} ({doc.document_type.value})")
    print(f"  Access: {doc.access_level.value}")
    print(f"  Sanitized: {doc.sanitized}")
```

---

## Integration Guide

### Integration with SENTI OS Boot Process

```python
# In senti_os/boot/boot.py

from senti_os.core.faza16 import create_manager

def initialize_faza16():
    """Initialize FAZA 16 during system boot."""
    print("Initializing FAZA 16...")

    manager = create_manager()

    # Detect available sources
    summary = manager.refresh_sources()
    print(f"Available sources: {summary['available_sources']}")

    return manager

# Add to boot sequence
faza16_manager = initialize_faza16()
```

### Integration with EventBus

```python
from senti_core_module.senti_core.services.event_bus import EventBus
from senti_os.core.faza16 import create_manager, LLMRequest, TaskType

# Initialize
event_bus = EventBus()
manager = create_manager()

# Define event handler
def handle_llm_request(event):
    """Handle LLM request events."""
    request = LLMRequest(
        request_id=event.get("request_id"),
        prompt=event.get("prompt"),
        task_type=TaskType[event.get("task_type")],
        user_consent=event.get("user_consent", False),
    )

    response = manager.process_request(request)

    # Emit response event
    event_bus.emit("llm_response", {
        "request_id": request.request_id,
        "status": response.status.value,
        "selected_source": response.selected_source,
    })

# Subscribe to events
event_bus.subscribe("llm_request", handle_llm_request)
```

### RESTful API Wrapper

```python
from flask import Flask, request, jsonify
from senti_os.core.faza16 import create_manager, LLMRequest, TaskType

app = Flask(__name__)
manager = create_manager()

@app.route('/api/faza16/process', methods=['POST'])
def process_request():
    """Process LLM request via API."""
    data = request.json

    llm_request = LLMRequest(
        request_id=data['request_id'],
        prompt=data['prompt'],
        task_type=TaskType[data['task_type']],
        user_consent=data.get('user_consent', False),
    )

    response = manager.process_request(llm_request)

    return jsonify({
        "status": response.status.value,
        "selected_source": response.selected_source,
        "reasoning": response.routing_reasoning,
        "decision_log": response.decision_log,
    })

@app.route('/api/faza16/statistics', methods=['GET'])
def get_statistics():
    """Get FAZA 16 statistics."""
    stats = manager.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Testing

### Running Tests

```bash
# Run all tests
cd /home/pisarna/senti_system
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 -m pytest senti_os/tests/faza16/ -v

# Run specific test class
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 -m pytest senti_os/tests/faza16/test_faza16_comprehensive.py::TestLLMRulesEngine -v

# Run with coverage
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 -m pytest senti_os/tests/faza16/ --cov=senti_os.core.faza16 --cov-report=html
```

### Writing Custom Tests

```python
import unittest
from senti_os.core.faza16 import create_manager, LLMRequest, TaskType

class TestCustomIntegration(unittest.TestCase):
    """Custom integration tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = create_manager()

    def test_custom_workflow(self):
        """Test custom workflow."""
        request = LLMRequest(
            request_id="custom_001",
            prompt="Test prompt",
            task_type=TaskType.GENERAL_QUERY,
        )

        response = self.manager.process_request(request)
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'senti_os'`

**Solution:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH

# Or add to ~/.bashrc
echo 'export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc
```

#### Issue 2: No Available Sources

**Symptom:** All requests fail with "No suitable LLM source available"

**Solution:**
```python
# Check detection
manager = create_manager()
summary = manager.refresh_sources()
print(f"Available: {summary['available_sources']}")

# Manually add API key
manager.add_api_key(
    provider="chatgpt",
    api_key="sk-your-key-here",
    subscription_level="pro",
)
```

#### Issue 3: Rules Always Failing

**Symptom:** All prompts rejected by rules engine

**Solution:**
```python
# Check which rules are failing
engine = create_default_rules_engine()
result = engine.check_all_rules("Your prompt here")

for violation in result.violations:
    print(f"{violation.rule_name}: {violation.message}")

# Disable specific rule if necessary (use with caution)
engine.disable_rule("anti_hallucination")
```

#### Issue 4: PII Not Being Sanitized

**Symptom:** Sensitive data visible in retrieved documents

**Solution:**
```python
# Ensure sanitization is enabled
query = RetrievalQuery(
    query_text="search term",
    sanitize_pii=True,  # Must be True
)

# Check document sanitized flag
for doc in result.documents:
    print(f"Sanitized: {doc.sanitized}")
```

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
```

---

## Best Practices

### 1. Always Obtain User Consent

```python
# Good
request = LLMRequest(
    request_id="req_001",
    prompt="Process this",
    task_type=TaskType.GENERAL_QUERY,
    user_consent=True,  # Explicit consent
)

# Bad
request = LLMRequest(
    request_id="req_001",
    prompt="Process this",
    task_type=TaskType.GENERAL_QUERY,
    requires_external_access=True,
    user_consent=False,  # Will be rejected
)
```

### 2. Monitor Reliability Scores

```python
# Record outcomes to improve routing
manager.record_interaction_outcome(
    request_id="req_001",
    success=True,
)
```

### 3. Regular Source Detection

```python
# Refresh sources periodically
import schedule

def refresh_sources():
    manager.refresh_sources()

schedule.every(1).hours.do(refresh_sources)
```

### 4. Validate Knowledge Regularly

```python
# Periodic validation
validator = create_validator()
results = validator.validate_all()

outdated = [r for r in results if r.freshness == FreshnessLevel.OUTDATED]
print(f"Outdated entries: {len(outdated)}")
```

### 5. Use Appropriate Priority Modes

```python
# For critical analysis - use quality
request = LLMRequest(
    ...,
    priority_mode=PriorityMode.QUALITY,
)

# For quick lookups - use speed
request = LLMRequest(
    ...,
    priority_mode=PriorityMode.SPEED,
)

# For cost-sensitive operations - use cost
request = LLMRequest(
    ...,
    priority_mode=PriorityMode.COST,
)
```

---

## Examples

### Complete Application Example

```python
#!/usr/bin/env python3
"""
Complete FAZA 16 application example.
Demonstrates full integration and usage patterns.
"""

from senti_os.core.faza16 import (
    create_manager,
    create_verifier,
    LLMRequest,
    TaskType,
    PriorityMode,
    RequestStatus,
    SourceResponse,
)

class IntelligentAssistant:
    """Intelligent assistant using FAZA 16."""

    def __init__(self):
        """Initialize assistant."""
        self.manager = create_manager()
        self.verifier = create_verifier()
        print("✓ Assistant initialized")

        # Show available sources
        stats = self.manager.get_statistics()
        print(f"✓ Available sources: {stats['registry_stats']['available_sources']}")

    def ask_question(self, question: str, verify: bool = False):
        """
        Ask a question and optionally verify with multiple sources.

        Args:
            question: Question to ask
            verify: Whether to use cross-verification
        """
        print(f"\n? Question: {question}")

        # Create request
        request = LLMRequest(
            request_id=f"req_{hash(question)}",
            prompt=question,
            task_type=TaskType.GENERAL_QUERY,
            priority_mode=PriorityMode.BALANCED,
            user_consent=True,
        )

        # Process
        response = self.manager.process_request(request)

        if response.status == RequestStatus.APPROVED:
            print(f"✓ Status: {response.status.value}")
            print(f"✓ Source: {response.selected_source}")
            print(f"✓ Reasoning: {response.routing_reasoning}")

            if verify and len(self.manager.registry.get_available_sources()) > 1:
                self._verify_answer(question)
        else:
            print(f"✗ Status: {response.status.value}")
            print(f"✗ Error: {response.error_message}")

    def _verify_answer(self, question: str):
        """Verify answer using multiple sources."""
        print("\n⚡ Cross-verifying...")

        # Simulate responses from multiple sources
        responses = [
            SourceResponse(
                source_id="source_a",
                content="Sample answer A",
                confidence=0.9,
            ),
            SourceResponse(
                source_id="source_b",
                content="Sample answer A",
                confidence=0.85,
            ),
        ]

        result = self.verifier.verify(responses)

        print(f"✓ Consensus: {result.consensus_level.value}")
        print(f"✓ Confidence: {result.confidence_score:.2f}")

        if result.discrepancies:
            print(f"⚠ Discrepancies: {len(result.discrepancies)}")

    def show_statistics(self):
        """Show usage statistics."""
        print("\n📊 Statistics:")
        stats = self.manager.get_statistics()
        print(f"Total requests: {stats['total_requests']}")
        print(f"Approval rate: {stats['approval_rate']:.1%}")
        print(f"Local processed: {stats['local_processed']}")
        print(f"External processed: {stats['external_processed']}")

# Main execution
if __name__ == "__main__":
    assistant = IntelligentAssistant()

    # Ask questions
    assistant.ask_question(
        "What are the benefits of renewable energy?",
        verify=True,
    )

    assistant.ask_question(
        "How do I implement a binary search in Python?",
        verify=False,
    )

    # Show statistics
    assistant.show_statistics()

    print("\n✓ Complete!")
```

---

## Conclusion

This implementation guide provides everything needed to successfully integrate and use FAZA 16 in production environments. The system is designed to be robust, secure, and compliant with modern data protection regulations while maintaining high performance and usability.

For additional support:
- Review the FAZA 16 specification document
- Examine the comprehensive test suite
- Consult the inline code documentation

---

**Document Version:** 1.0.0
**Last Updated:** December 2025
**Maintained By:** SENTI OS Core Team
