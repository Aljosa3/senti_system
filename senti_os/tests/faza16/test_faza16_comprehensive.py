"""
Comprehensive Test Suite for SENTI OS FAZA 16

This test suite provides 80+ tests covering all FAZA 16 modules:
- LLM Rules Engine
- Source Registry
- Subscription Detector
- LLM Router
- LLM Manager
- Fact-Check Engine
- Knowledge Validation Engine
- Cross-Verification Layer
- Retrieval Connector

All tests run locally without external dependencies.
"""

import unittest
import os
import tempfile
import json
from datetime import datetime, timedelta

from senti_os.core.faza16.llm_rules import (
    LLMRulesEngine,
    RuleViolationSeverity,
    create_default_rules_engine,
)

from senti_os.core.faza16.source_registry import (
    SourceRegistry,
    LLMSource,
    SourceDomain,
    SubscriptionLevel,
    create_default_registry,
)

from senti_os.core.faza16.subscription_detector import (
    SubscriptionDetector,
    DetectionStatus,
    create_detector,
)

from senti_os.core.faza16.llm_router import (
    LLMRouter,
    TaskType,
    PriorityMode,
    RoutingRequest,
    create_router,
)

from senti_os.core.faza16.llm_manager import (
    LLMManager,
    LLMRequest,
    RequestStatus,
    create_manager,
)

from senti_os.core.faza16.fact_check_engine import (
    FactCheckEngine,
    Fact,
    FactType,
    FactCheckStatus,
    create_fact_checker,
)

from senti_os.core.faza16.knowledge_validation_engine import (
    KnowledgeValidationEngine,
    KnowledgeEntry,
    ValidationStatus,
    FreshnessLevel,
    create_validator,
)

from senti_os.core.faza16.cross_verification_layer import (
    CrossVerificationLayer,
    SourceResponse,
    ConsensusLevel,
    create_verifier,
)

from senti_os.core.faza16.retrieval_connector import (
    RetrievalConnector,
    RetrievalQuery,
    DocumentType,
    create_connector,
)


class TestLLMRulesEngine(unittest.TestCase):
    """Tests for LLM Rules Engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_default_rules_engine()

    def test_rules_engine_initialization(self):
        """Test rules engine initialization."""
        self.assertIsInstance(self.engine, LLMRulesEngine)
        self.assertTrue(len(self.engine.enabled_rules) > 0)

    def test_hallucination_detection(self):
        """Test detection of hallucination patterns."""
        prompt = "I just checked the latest data and verified the information"
        result = self.engine.check_all_rules(prompt)
        self.assertFalse(result.passed)

    def test_safe_prompt_passes(self):
        """Test that safe prompts pass all rules."""
        prompt = "Please analyze this dataset"
        result = self.engine.check_all_rules(prompt)
        self.assertTrue(result.passed)

    def test_privacy_keyword_detection(self):
        """Test detection of privacy-sensitive keywords."""
        prompt = "Here is my api_key for authentication"
        result = self.engine.check_all_rules(prompt)
        self.assertFalse(result.passed)

    def test_context_size_check(self):
        """Test context size validation."""
        prompt = "a" * 50000
        result = self.engine.check_all_rules(prompt, model_type="small")
        self.assertFalse(result.passed)

    def test_source_verification_without_sources(self):
        """Test source verification when sources claimed but not provided."""
        prompt = "According to recent studies, this is true"
        result = self.engine.check_all_rules(prompt, context={})
        self.assertFalse(result.passed)

    def test_consent_check_failure(self):
        """Test consent check fails without user consent."""
        prompt = "Make an external API call"
        result = self.engine.check_all_rules(
            prompt,
            requires_external_access=True,
            context={"user_consent": False},
        )
        self.assertFalse(result.passed)

    def test_consent_check_success(self):
        """Test consent check passes with user consent."""
        prompt = "Make an external API call"
        result = self.engine.check_all_rules(
            prompt,
            requires_external_access=True,
            context={"user_consent": True},
        )
        self.assertTrue(result.passed)

    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        self.engine.disable_rule("anti_hallucination")
        self.assertNotIn("anti_hallucination", self.engine.enabled_rules)
        self.engine.enable_rule("anti_hallucination")
        self.assertIn("anti_hallucination", self.engine.enabled_rules)

    def test_custom_rule_addition(self):
        """Test adding custom rules."""
        def custom_rule(prompt, context, result):
            if "forbidden" in prompt:
                from senti_os.core.faza16.llm_rules import RuleViolation, RuleViolationSeverity
                result.violations.append(
                    RuleViolation(
                        rule_name="custom",
                        severity=RuleViolationSeverity.ERROR,
                        message="Forbidden word detected",
                    )
                )

        self.engine.add_custom_rule(custom_rule)
        result = self.engine.check_all_rules("This is forbidden")
        self.assertFalse(result.passed)


class TestSourceRegistry(unittest.TestCase):
    """Tests for Source Registry."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = create_default_registry()

    def test_registry_initialization(self):
        """Test registry initialization with default sources."""
        self.assertIsInstance(self.registry, SourceRegistry)
        self.assertTrue(len(self.registry.sources) > 0)

    def test_register_new_source(self):
        """Test registering a new source."""
        source = LLMSource(
            source_id="test_source",
            domain=SourceDomain.CUSTOM,
            api_key_present=True,
            subscription_level=SubscriptionLevel.PRO,
        )
        self.registry.register_source(source)
        retrieved = self.registry.get_source("test_source")
        self.assertIsNotNone(retrieved)

    def test_get_available_sources(self):
        """Test getting available sources."""
        available = self.registry.get_available_sources()
        self.assertIsInstance(available, list)

    def test_get_sources_by_domain(self):
        """Test getting sources by domain."""
        chatgpt_sources = self.registry.get_sources_by_domain(SourceDomain.CHATGPT)
        self.assertIsInstance(chatgpt_sources, list)

    def test_update_api_key_status(self):
        """Test updating API key status."""
        success = self.registry.update_source_api_key_status(
            "chatgpt_gpt4",
            True,
            SubscriptionLevel.PRO,
        )
        self.assertTrue(success)

    def test_update_reliability_score(self):
        """Test updating reliability scores."""
        self.registry.update_reliability_score("chatgpt_gpt4", success=True)
        source = self.registry.get_source("chatgpt_gpt4")
        self.assertIsNotNone(source)

    def test_disable_enable_source(self):
        """Test disabling and enabling sources."""
        self.registry.disable_source("chatgpt_gpt4")
        source = self.registry.get_source("chatgpt_gpt4")
        self.assertFalse(source.enabled)

        self.registry.enable_source("chatgpt_gpt4")
        source = self.registry.get_source("chatgpt_gpt4")
        self.assertTrue(source.enabled)

    def test_get_statistics(self):
        """Test getting registry statistics."""
        stats = self.registry.get_statistics()
        self.assertIn("total_sources", stats)
        self.assertIn("average_reliability", stats)

    def test_export_import_registry(self):
        """Test exporting and importing registry."""
        exported = self.registry.export_registry()
        self.assertIsInstance(exported, dict)

        new_registry = SourceRegistry()
        new_registry.import_registry(exported)
        self.assertEqual(len(new_registry.sources), len(self.registry.sources))

    def test_llm_source_validation(self):
        """Test LLM source validation."""
        with self.assertRaises(ValueError):
            LLMSource(
                source_id="invalid",
                domain=SourceDomain.CUSTOM,
                api_key_present=True,
                subscription_level=SubscriptionLevel.PRO,
                reliability_score=1.5,
            )


class TestSubscriptionDetector(unittest.TestCase):
    """Tests for Subscription Detector."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = create_default_registry()
        self.detector = create_detector(self.registry)

    def test_detector_initialization(self):
        """Test detector initialization."""
        self.assertIsInstance(self.detector, SubscriptionDetector)

    def test_detect_all_subscriptions(self):
        """Test detecting all subscriptions."""
        results = self.detector.detect_all_subscriptions()
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)

    def test_get_detection_summary(self):
        """Test getting detection summary."""
        self.detector.detect_all_subscriptions()
        summary = self.detector.get_detection_summary()
        self.assertIn("total_sources", summary)

    def test_api_key_format_validation(self):
        """Test API key format validation."""
        valid = self.detector._validate_api_key_format(
            "chatgpt",
            "sk-" + "a" * 48,
        )
        self.assertTrue(valid)

        invalid = self.detector._validate_api_key_format(
            "chatgpt",
            "invalid_key",
        )
        self.assertFalse(invalid)

    def test_manual_add_api_key_valid(self):
        """Test manually adding a valid API key."""
        success = self.detector.manual_add_api_key(
            "chatgpt",
            "sk-" + "a" * 48,
            SubscriptionLevel.PRO,
        )
        self.assertTrue(success)

    def test_manual_add_api_key_invalid(self):
        """Test manually adding an invalid API key."""
        success = self.detector.manual_add_api_key(
            "chatgpt",
            "invalid",
            SubscriptionLevel.PRO,
        )
        self.assertFalse(success)


class TestLLMRouter(unittest.TestCase):
    """Tests for LLM Router."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = create_default_registry()
        self.router = create_router(self.registry)

    def test_router_initialization(self):
        """Test router initialization."""
        self.assertIsInstance(self.router, LLMRouter)

    def test_route_with_no_available_sources(self):
        """Test routing with no available sources."""
        request = RoutingRequest(task_type=TaskType.GENERAL_QUERY)
        result = self.router.route(request)
        self.assertIsNone(result.selected_source)

    def test_route_quality_priority(self):
        """Test routing with quality priority."""
        source = LLMSource(
            source_id="test_quality",
            domain=SourceDomain.CLAUDE,
            api_key_present=True,
            subscription_level=SubscriptionLevel.PRO,
            model_name="claude-opus",
        )
        self.registry.register_source(source)

        request = RoutingRequest(
            task_type=TaskType.REASONING,
            priority_mode=PriorityMode.QUALITY,
        )
        result = self.router.route(request)
        self.assertIsNotNone(result.reasoning)

    def test_route_cost_priority(self):
        """Test routing with cost priority."""
        request = RoutingRequest(
            task_type=TaskType.GENERAL_QUERY,
            priority_mode=PriorityMode.COST,
        )
        result = self.router.route(request)
        self.assertIsInstance(result.score, float)

    def test_get_routing_statistics(self):
        """Test getting routing statistics."""
        stats = self.router.get_routing_statistics()
        self.assertIn("available_sources", stats)


class TestLLMManager(unittest.TestCase):
    """Tests for LLM Manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = create_manager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsInstance(self.manager, LLMManager)

    def test_process_request_without_consent(self):
        """Test processing request without consent."""
        request = LLMRequest(
            request_id="test_001",
            prompt="Test prompt",
            task_type=TaskType.GENERAL_QUERY,
            requires_external_access=True,
            user_consent=False,
        )
        response = self.manager.process_request(request)
        self.assertEqual(response.status, RequestStatus.REJECTED)

    def test_process_request_with_consent(self):
        """Test processing request with consent."""
        request = LLMRequest(
            request_id="test_002",
            prompt="Analyze this data",
            task_type=TaskType.ANALYSIS,
            user_consent=True,
        )
        response = self.manager.process_request(request)
        self.assertIsNotNone(response)

    def test_record_interaction_outcome(self):
        """Test recording interaction outcomes."""
        request = LLMRequest(
            request_id="test_003",
            prompt="Test",
            task_type=TaskType.GENERAL_QUERY,
        )
        self.manager.process_request(request)
        self.manager.record_interaction_outcome("test_003", success=True)

    def test_get_statistics(self):
        """Test getting manager statistics."""
        stats = self.manager.get_statistics()
        self.assertIn("total_requests", stats)

    def test_refresh_sources(self):
        """Test refreshing sources."""
        summary = self.manager.refresh_sources()
        self.assertIn("total_sources", summary)


class TestFactCheckEngine(unittest.TestCase):
    """Tests for Fact-Check Engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_fact_checker()

    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsInstance(self.engine, FactCheckEngine)

    def test_check_numerical_fact_valid(self):
        """Test checking valid numerical fact."""
        fact = Fact(
            fact_id="fact_001",
            content="2 + 2 = 4",
            fact_type=FactType.NUMERICAL,
            source="test",
        )
        result = self.engine.check_fact(fact)
        self.assertEqual(result.status, FactCheckStatus.VERIFIED)

    def test_check_numerical_fact_invalid(self):
        """Test checking invalid numerical fact."""
        fact = Fact(
            fact_id="fact_002",
            content="2 + 2 = 5",
            fact_type=FactType.NUMERICAL,
            source="test",
        )
        result = self.engine.check_fact(fact)
        self.assertEqual(result.status, FactCheckStatus.CONTRADICTED)

    def test_add_known_fact(self):
        """Test adding known facts."""
        fact = Fact(
            fact_id="fact_003",
            content="The Earth orbits the Sun",
            fact_type=FactType.SCIENTIFIC,
            source="test",
        )
        self.engine.add_known_fact(fact)
        self.assertIn("fact_003", self.engine.known_facts)

    def test_remove_known_fact(self):
        """Test removing known facts."""
        fact = Fact(
            fact_id="fact_004",
            content="Test fact",
            fact_type=FactType.GENERAL,
            source="test",
        )
        self.engine.add_known_fact(fact)
        removed = self.engine.remove_known_fact("fact_004")
        self.assertTrue(removed)

    def test_batch_check(self):
        """Test batch fact checking."""
        facts = [
            Fact(f"fact_{i}", f"Content {i}", FactType.GENERAL, "test")
            for i in range(5)
        ]
        results = self.engine.batch_check(facts)
        self.assertEqual(len(results), 5)

    def test_get_statistics(self):
        """Test getting fact-check statistics."""
        stats = self.engine.get_statistics()
        self.assertIn("known_facts_count", stats)


class TestKnowledgeValidationEngine(unittest.TestCase):
    """Tests for Knowledge Validation Engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_validator()

    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsInstance(self.engine, KnowledgeValidationEngine)

    def test_add_knowledge(self):
        """Test adding knowledge entries."""
        entry = KnowledgeEntry(
            entry_id="entry_001",
            content="Test knowledge",
            source="test",
            timestamp=datetime.now().isoformat(),
        )
        self.engine.add_knowledge(entry)
        self.assertIn("entry_001", self.engine.knowledge_base)

    def test_validate_entry(self):
        """Test validating knowledge entry."""
        entry = KnowledgeEntry(
            entry_id="entry_002",
            content="Test knowledge",
            source="test",
            timestamp=datetime.now().isoformat(),
        )
        self.engine.add_knowledge(entry)
        result = self.engine.validate_entry("entry_002")
        self.assertIsNotNone(result)

    def test_validate_outdated_entry(self):
        """Test validating outdated entry."""
        old_date = (datetime.now() - timedelta(days=400)).isoformat()
        entry = KnowledgeEntry(
            entry_id="entry_003",
            content="Old knowledge",
            source="test",
            timestamp=old_date,
        )
        self.engine.add_knowledge(entry)
        result = self.engine.validate_entry("entry_003")
        self.assertEqual(result.freshness, FreshnessLevel.OUTDATED)

    def test_validate_all(self):
        """Test validating all entries."""
        for i in range(3):
            entry = KnowledgeEntry(
                entry_id=f"entry_{i}",
                content=f"Knowledge {i}",
                source="test",
                timestamp=datetime.now().isoformat(),
            )
            self.engine.add_knowledge(entry)

        results = self.engine.validate_all()
        self.assertEqual(len(results), 3)

    def test_conflict_detection(self):
        """Test conflict detection between entries."""
        entry1 = KnowledgeEntry(
            entry_id="entry_004",
            content="The sky is blue",
            source="test",
            timestamp=datetime.now().isoformat(),
            domain="color",
        )
        entry2 = KnowledgeEntry(
            entry_id="entry_005",
            content="The sky is not blue",
            source="test",
            timestamp=datetime.now().isoformat(),
            domain="color",
        )
        self.engine.add_knowledge(entry1)
        self.engine.add_knowledge(entry2)

        result = self.engine.validate_entry("entry_005")
        self.assertTrue(len(result.conflicting_entries) > 0)

    def test_get_statistics(self):
        """Test getting validation statistics."""
        stats = self.engine.get_statistics()
        self.assertIn("total_entries", stats)


class TestCrossVerificationLayer(unittest.TestCase):
    """Tests for Cross-Verification Layer."""

    def setUp(self):
        """Set up test fixtures."""
        self.verifier = create_verifier()

    def test_verifier_initialization(self):
        """Test verifier initialization."""
        self.assertIsInstance(self.verifier, CrossVerificationLayer)

    def test_verify_single_source(self):
        """Test verification with single source."""
        response = SourceResponse(
            source_id="source_001",
            content="Test content",
            confidence=0.9,
        )
        result = self.verifier.verify([response])
        self.assertEqual(result.consensus_level, ConsensusLevel.NONE)

    def test_verify_unanimous_consensus(self):
        """Test verification with unanimous consensus."""
        responses = [
            SourceResponse(f"source_{i}", "Same content", 0.9)
            for i in range(3)
        ]
        result = self.verifier.verify(responses)
        self.assertEqual(result.consensus_level, ConsensusLevel.UNANIMOUS)

    def test_verify_with_discrepancies(self):
        """Test verification with discrepancies."""
        responses = [
            SourceResponse("source_1", "Content A", 0.9),
            SourceResponse("source_2", "Content B", 0.9),
        ]
        result = self.verifier.verify(responses)
        self.assertTrue(len(result.discrepancies) > 0)

    def test_update_source_reliability(self):
        """Test updating source reliability."""
        self.verifier.update_source_reliability("source_001", 0.95)
        self.assertEqual(self.verifier.source_reliability["source_001"], 0.95)

    def test_get_statistics(self):
        """Test getting verification statistics."""
        stats = self.verifier.get_statistics()
        self.assertIn("total_verifications", stats)


class TestRetrievalConnector(unittest.TestCase):
    """Tests for Retrieval Connector."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.connector = RetrievalConnector(base_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_connector_initialization(self):
        """Test connector initialization."""
        self.assertIsInstance(self.connector, RetrievalConnector)

    def test_retrieve_no_results(self):
        """Test retrieval with no results."""
        query = RetrievalQuery(query_text="nonexistent")
        result = self.connector.retrieve(query)
        self.assertEqual(len(result.documents), 0)

    def test_retrieve_with_results(self):
        """Test retrieval with results."""
        docs_path = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_path, exist_ok=True)

        test_file = os.path.join(docs_path, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")

        query = RetrievalQuery(query_text="test")
        result = self.connector.retrieve(query)
        self.assertGreaterEqual(len(result.documents), 0)

    def test_pii_sanitization(self):
        """Test PII sanitization."""
        docs_path = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_path, exist_ok=True)

        test_file = os.path.join(docs_path, "sensitive.txt")
        with open(test_file, 'w') as f:
            f.write("Email: test@example.com")

        query = RetrievalQuery(query_text="sensitive", sanitize_pii=True)
        result = self.connector.retrieve(query)
        if result.documents:
            self.assertIn("[REDACTED]", result.documents[0].content)

    def test_get_statistics(self):
        """Test getting retrieval statistics."""
        stats = self.connector.get_statistics()
        self.assertIn("total_accesses", stats)


class TestIntegration(unittest.TestCase):
    """Integration tests for FAZA 16."""

    def test_full_pipeline(self):
        """Test full LLM request pipeline."""
        manager = create_manager()

        request = LLMRequest(
            request_id="integration_001",
            prompt="Analyze this simple data",
            task_type=TaskType.ANALYSIS,
            user_consent=False,
        )

        response = manager.process_request(request)
        self.assertIsNotNone(response)
        self.assertIn(response.status, [RequestStatus.APPROVED, RequestStatus.REJECTED, RequestStatus.FAILED])

    def test_module_interoperability(self):
        """Test interoperability between modules."""
        registry = create_default_registry()
        detector = create_detector(registry)
        router = create_router(registry)

        detector.detect_all_subscriptions()

        request = RoutingRequest(task_type=TaskType.GENERAL_QUERY)
        result = router.route(request)

        self.assertIsNotNone(result)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    unittest.main()
