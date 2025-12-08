#!/usr/bin/env python3
"""
FAZA 31 Extended Preflight Simulation Runner
Comprehensive test with 7 modules, classes, data structures, and inter-module imports
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/pisarna/senti_system')

from senti_core_module.senti_build import build_executor
from senti_core_module.senti_build import build_reporter


def mock_llm_callable_extended(prompt: str) -> str:
    """
    Mock LLM that generates correct output for extended preflight test.
    Generates 7 modules with classes, functions, and inter-module imports.
    """
    output = """FILE: /home/pisarna/senti_system/senti_sandbox/ext_math_utils.py
\"\"\"
Extended Math Utils - FAZA 31 Extended Preflight
\"\"\"


def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b


def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b


def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b


def divide(a, b):
    \"\"\"Divide a by b. Returns None if b is 0.\"\"\"
    if b == 0:
        return None
    return a / b


def power(base, exp):
    \"\"\"Raise base to exp power.\"\"\"
    return base ** exp


def factorial(n):
    \"\"\"Calculate factorial of n using recursion.\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n - 1)

FILE: /home/pisarna/senti_system/senti_sandbox/ext_data_stack.py
\"\"\"
Stack Data Structure - FAZA 31 Extended Preflight
\"\"\"


class Stack:
    \"\"\"Stack implementation using list.\"\"\"

    def __init__(self):
        \"\"\"Initialize empty stack.\"\"\"
        self._items = []

    def push(self, item):
        \"\"\"Push item onto stack.\"\"\"
        self._items.append(item)

    def pop(self):
        \"\"\"Pop item from stack. Returns None if empty.\"\"\"
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self):
        \"\"\"Return top item without removing. Returns None if empty.\"\"\"
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self):
        \"\"\"Check if stack is empty.\"\"\"
        return len(self._items) == 0

    def size(self):
        \"\"\"Return number of items in stack.\"\"\"
        return len(self._items)

    def clear(self):
        \"\"\"Remove all items from stack.\"\"\"
        self._items = []

    def __str__(self):
        \"\"\"String representation of stack.\"\"\"
        return f"Stack({self._items})"

FILE: /home/pisarna/senti_system/senti_sandbox/ext_data_queue.py
\"\"\"
Queue Data Structure - FAZA 31 Extended Preflight
\"\"\"


class Queue:
    \"\"\"Queue implementation using list.\"\"\"

    def __init__(self):
        \"\"\"Initialize empty queue.\"\"\"
        self._items = []

    def enqueue(self, item):
        \"\"\"Add item to rear of queue.\"\"\"
        self._items.append(item)

    def dequeue(self):
        \"\"\"Remove and return front item. Returns None if empty.\"\"\"
        if self.is_empty():
            return None
        return self._items.pop(0)

    def front(self):
        \"\"\"Return front item without removing. Returns None if empty.\"\"\"
        if self.is_empty():
            return None
        return self._items[0]

    def is_empty(self):
        \"\"\"Check if queue is empty.\"\"\"
        return len(self._items) == 0

    def size(self):
        \"\"\"Return number of items in queue.\"\"\"
        return len(self._items)

    def __str__(self):
        \"\"\"String representation of queue.\"\"\"
        return f"Queue({self._items})"

FILE: /home/pisarna/senti_system/senti_sandbox/ext_validator.py
\"\"\"
Validation Utilities - FAZA 31 Extended Preflight
\"\"\"


def is_positive(n):
    \"\"\"Check if number is positive.\"\"\"
    return n > 0


def is_even(n):
    \"\"\"Check if number is even.\"\"\"
    return n % 2 == 0


def is_in_range(n, min_val, max_val):
    \"\"\"Check if number is in range [min_val, max_val].\"\"\"
    return min_val <= n <= max_val


def is_valid_string(s):
    \"\"\"Check if s is a non-empty string.\"\"\"
    return isinstance(s, str) and len(s) > 0


def validate_number(n, min_val=None, max_val=None):
    \"\"\"
    Validate number with optional range check.
    Returns tuple (bool, string) with result and reason.
    \"\"\"
    if not isinstance(n, (int, float)):
        return (False, "Not a number")

    if min_val is not None and n < min_val:
        return (False, f"Below minimum {min_val}")

    if max_val is not None and n > max_val:
        return (False, f"Above maximum {max_val}")

    return (True, "Valid")

FILE: /home/pisarna/senti_system/senti_sandbox/ext_formatter.py
\"\"\"
String Formatting Utilities - FAZA 31 Extended Preflight
\"\"\"


def capitalize_words(text):
    \"\"\"Capitalize first letter of each word.\"\"\"
    return ' '.join(word.capitalize() for word in text.split())


def reverse_string(text):
    \"\"\"Reverse the string.\"\"\"
    return text[::-1]


def truncate(text, max_length, suffix='...'):
    \"\"\"Truncate text to max_length, adding suffix if truncated.\"\"\"
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def pad_left(text, width, char=' '):
    \"\"\"Pad text on the left to reach width.\"\"\"
    return text.rjust(width, char)


def pad_right(text, width, char=' '):
    \"\"\"Pad text on the right to reach width.\"\"\"
    return text.ljust(width, char)


def center(text, width, char=' '):
    \"\"\"Center text within width.\"\"\"
    return text.center(width, char)


def remove_whitespace(text):
    \"\"\"Remove all whitespace from text.\"\"\"
    return ''.join(text.split())

FILE: /home/pisarna/senti_system/senti_sandbox/ext_calculator.py
\"\"\"
Calculator with History - FAZA 31 Extended Preflight
\"\"\"


class Calculator:
    \"\"\"Calculator that tracks operation history.\"\"\"

    def __init__(self):
        \"\"\"Initialize calculator with empty history.\"\"\"
        self._history = []

    def add(self, a, b):
        \"\"\"Add two numbers and record operation.\"\"\"
        result = a + b
        self._history.append(f"add({a},{b})={result}")
        return result

    def subtract(self, a, b):
        \"\"\"Subtract b from a and record operation.\"\"\"
        result = a - b
        self._history.append(f"subtract({a},{b})={result}")
        return result

    def multiply(self, a, b):
        \"\"\"Multiply two numbers and record operation.\"\"\"
        result = a * b
        self._history.append(f"multiply({a},{b})={result}")
        return result

    def divide(self, a, b):
        \"\"\"Divide a by b. Returns None if b is 0.\"\"\"
        if b == 0:
            self._history.append(f"divide({a},{b})=ERROR")
            return None
        result = a / b
        self._history.append(f"divide({a},{b})={result}")
        return result

    def power(self, base, exp):
        \"\"\"Raise base to exp power and record operation.\"\"\"
        result = base ** exp
        self._history.append(f"power({base},{exp})={result}")
        return result

    def sqrt(self, n):
        \"\"\"
        Calculate square root using Newton's method approximation.
        No math library imports.
        \"\"\"
        if n < 0:
            self._history.append(f"sqrt({n})=ERROR")
            return None
        if n == 0:
            return 0

        x = n
        tolerance = 0.00001
        while True:
            root = 0.5 * (x + n / x)
            if abs(root - x) < tolerance:
                break
            x = root

        self._history.append(f"sqrt({n})={root}")
        return root

    def get_history(self):
        \"\"\"Return list of all operations.\"\"\"
        return self._history.copy()

    def clear_history(self):
        \"\"\"Clear operation history.\"\"\"
        self._history = []

FILE: /home/pisarna/senti_system/senti_sandbox/ext_aggregator.py
\"\"\"
Module Aggregator - FAZA 31 Extended Preflight
Tests inter-module imports
\"\"\"

from senti_sandbox import ext_math_utils
from senti_sandbox import ext_validator


def safe_divide(a, b):
    \"\"\"
    Safe division using validator and math_utils.
    Returns result or None if invalid.
    \"\"\"
    if not ext_validator.is_positive(b):
        return None
    return ext_math_utils.divide(a, b)


def validated_add(a, b):
    \"\"\"
    Validated addition - checks if both are numbers.
    Returns result or None if invalid.
    \"\"\"
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None
    return ext_math_utils.add(a, b)


def get_available_operations():
    \"\"\"Return list of available operation names.\"\"\"
    return [
        'safe_divide',
        'validated_add',
        'add',
        'subtract',
        'multiply',
        'divide',
        'power',
        'factorial'
    ]
"""
    return output


def load_contract():
    """Load FA31_LLM_CONTRACT.md content."""
    contract_path = Path('/home/pisarna/senti_system/senti_core_module/senti_llm/FA31_LLM_CONTRACT.md')
    if contract_path.exists():
        return contract_path.read_text()
    return None


def verify_generated_modules():
    """Verify that generated modules work correctly."""
    print("=" * 60)
    print("MODULE VERIFICATION TESTS")
    print("=" * 60)
    print()

    sys.path.insert(0, '/home/pisarna/senti_system')

    tests_passed = 0
    tests_failed = 0

    try:
        from senti_sandbox import ext_math_utils
        result = ext_math_utils.add(5, 3)
        assert result == 8, f"Expected 8, got {result}"
        print("✓ ext_math_utils.add(5, 3) = 8")

        result = ext_math_utils.factorial(5)
        assert result == 120, f"Expected 120, got {result}"
        print("✓ ext_math_utils.factorial(5) = 120")

        result = ext_math_utils.divide(10, 0)
        assert result is None, f"Expected None for division by zero"
        print("✓ ext_math_utils.divide(10, 0) = None")

        tests_passed += 3
    except Exception as e:
        print(f"✗ ext_math_utils tests failed: {e}")
        tests_failed += 1

    try:
        from senti_sandbox.ext_data_stack import Stack
        stack = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        assert stack.size() == 3, "Stack size should be 3"
        assert stack.pop() == 3, "Pop should return 3"
        assert stack.peek() == 2, "Peek should return 2"
        print(f"✓ Stack operations: push, pop, peek work correctly")
        print(f"  Stack state: {stack}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Stack tests failed: {e}")
        tests_failed += 1

    try:
        from senti_sandbox.ext_data_queue import Queue
        queue = Queue()
        queue.enqueue('a')
        queue.enqueue('b')
        queue.enqueue('c')
        assert queue.size() == 3, "Queue size should be 3"
        assert queue.dequeue() == 'a', "Dequeue should return 'a'"
        assert queue.front() == 'b', "Front should return 'b'"
        print(f"✓ Queue operations: enqueue, dequeue, front work correctly")
        print(f"  Queue state: {queue}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Queue tests failed: {e}")
        tests_failed += 1

    try:
        from senti_sandbox import ext_validator
        assert ext_validator.is_positive(5) == True
        assert ext_validator.is_even(4) == True
        assert ext_validator.is_in_range(5, 1, 10) == True
        valid, msg = ext_validator.validate_number(7, min_val=5, max_val=10)
        assert valid == True, "Number 7 should be valid in range 5-10"
        print("✓ Validator functions work correctly")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Validator tests failed: {e}")
        tests_failed += 1

    try:
        from senti_sandbox import ext_formatter
        result = ext_formatter.capitalize_words("hello world")
        assert result == "Hello World", f"Expected 'Hello World', got {result}"
        result = ext_formatter.reverse_string("abc")
        assert result == "cba", f"Expected 'cba', got {result}"
        result = ext_formatter.truncate("hello world", 8)
        assert result == "hello...", f"Expected 'hello...', got {result}"
        print("✓ Formatter functions work correctly")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Formatter tests failed: {e}")
        tests_failed += 1

    try:
        from senti_sandbox.ext_calculator import Calculator
        calc = Calculator()
        assert calc.add(5, 3) == 8
        assert calc.multiply(4, 5) == 20
        assert calc.divide(10, 0) is None
        sqrt_result = calc.sqrt(16)
        assert abs(sqrt_result - 4.0) < 0.001, f"sqrt(16) should be ~4.0, got {sqrt_result}"
        history = calc.get_history()
        assert len(history) == 4, f"History should have 4 entries, got {len(history)}"
        print("✓ Calculator with history works correctly")
        print(f"  History: {history[:2]}...")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Calculator tests failed: {e}")
        tests_failed += 1

    try:
        from senti_sandbox import ext_aggregator
        result = ext_aggregator.safe_divide(10, 2)
        assert result == 5.0, f"Expected 5.0, got {result}"
        result = ext_aggregator.validated_add(3, 7)
        assert result == 10, f"Expected 10, got {result}"
        ops = ext_aggregator.get_available_operations()
        assert len(ops) > 0, "Should have operations list"
        print("✓ Aggregator with inter-module imports works correctly")
        print(f"  Available operations: {len(ops)} operations")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Aggregator tests failed: {e}")
        tests_failed += 1

    print()
    print("-" * 60)
    print(f"Verification Results: {tests_passed} passed, {tests_failed} failed")
    print("-" * 60)
    print()

    return tests_failed == 0


def main():
    print("=" * 60)
    print("FAZA 31 EXTENDED PREFLIGHT SIMULATION")
    print("=" * 60)
    print()

    spec_path = Path('/home/pisarna/senti_system/FA31_EXTENDED_SPEC.json')

    if not spec_path.exists():
        print(f"ERROR: Spec file not found: {spec_path}")
        return 1

    print(f"Loading spec: {spec_path}")
    with open(spec_path, 'r') as f:
        spec_data = json.load(f)

    print(f"Files to generate: {len(spec_data.get('files', []))}")
    for file_entry in spec_data.get('files', []):
        print(f"  - {file_entry.get('path', '').split('/')[-1]}")
    print()

    contract_text = load_contract()
    if contract_text:
        print(f"Contract loaded: {len(contract_text)} chars")
    else:
        print("Contract: using placeholder")
    print()

    print("Starting FAZA 31 Auto-Build pipeline...")
    print("-" * 60)
    print()

    result = build_executor.build(
        spec=spec_data,
        llm_callable=mock_llm_callable_extended,
        contract_text=contract_text
    )

    print("Build completed.")
    print()
    print("=" * 60)
    print("BUILD RESULTS")
    print("=" * 60)
    print()

    report = result.get('report', {})
    formatted_report = build_reporter.format_report(report)
    print(formatted_report)

    if result['status'] == 'OK':
        print()
        print("Writing generated files to filesystem...")
        files = result.get('files', {})
        for path, content in files.items():
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            print(f"  ✓ Written: {file_path.name}")
        print()

        verification_ok = verify_generated_modules()

        if verification_ok:
            print("=" * 60)
            print("✓ EXTENDED PREFLIGHT SIMULATION: SUCCESS")
            print("=" * 60)
            return 0
        else:
            print("=" * 60)
            print("✗ EXTENDED PREFLIGHT SIMULATION: VERIFICATION FAILED")
            print("=" * 60)
            return 1
    else:
        print("=" * 60)
        print("✗ EXTENDED PREFLIGHT SIMULATION: BUILD FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
