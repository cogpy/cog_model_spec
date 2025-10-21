#!/usr/bin/env python3
"""
OpenCog Cognitive Architecture Test Suite
Comprehensive tests for the integrated OpenCog-Model Spec system.
"""

import unittest
import logging
import time
from typing import List, Dict, Any

from cognitive_architecture import (
    CognitiveArchitecture, AtomSpace, Atom, AtomType, 
    TruthValue, AuthorityLevel, PLNReasoner, ECAN, MetaCognition
)
from pattern_engine import (
    PatternMatcher, BehaviorPattern, ConceptPattern, 
    InferencePattern, AnalogicalPattern
)
from opencog_integration import OpenCogModelSpec, ResponseStyle, InteractionContext
from config import ConfigManager, load_config


class TestAtomSpace(unittest.TestCase):
    """Test AtomSpace functionality."""
    
    def setUp(self):
        self.atomspace = AtomSpace()
    
    def test_atom_creation(self):
        """Test basic atom creation and retrieval."""
        atom = self.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            "test-concept",
            TruthValue(0.8, 0.9)
        )
        
        self.assertIsNotNone(atom)
        self.assertEqual(atom.name, "test-concept")
        self.assertEqual(atom.atom_type, AtomType.CONCEPT_NODE)
        self.assertAlmostEqual(atom.truth_value.strength, 0.8, places=2)
        self.assertAlmostEqual(atom.truth_value.confidence, 0.9, places=2)
    
    def test_atom_links(self):
        """Test atom linking functionality."""
        concept1 = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "concept1")
        concept2 = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "concept2")
        
        link = self.atomspace.create_link(
            AtomType.INHERITANCE_LINK,
            [concept1, concept2],
            TruthValue(0.7, 0.8)
        )
        
        self.assertEqual(len(link.outgoing), 2)
        self.assertIn(concept1, link.outgoing)
        self.assertIn(concept2, link.outgoing)
        self.assertIn(link, concept1.incoming)
        self.assertIn(link, concept2.incoming)
    
    def test_atom_retrieval(self):
        """Test atom retrieval by type and name."""
        concept = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "retrievable")
        predicate = self.atomspace.add_atom(AtomType.PREDICATE_NODE, "test-predicate")
        
        concepts = self.atomspace.get_atoms_by_type(AtomType.CONCEPT_NODE)
        predicates = self.atomspace.get_atoms_by_type(AtomType.PREDICATE_NODE)
        named_atoms = self.atomspace.get_atoms_by_name("retrievable")
        
        self.assertIn(concept, concepts)
        self.assertIn(predicate, predicates)
        self.assertIn(concept, named_atoms)


class TestTruthValue(unittest.TestCase):
    """Test TruthValue operations."""
    
    def test_truth_value_creation(self):
        """Test truth value creation and validation."""
        tv = TruthValue(0.7, 0.8)
        self.assertEqual(tv.strength, 0.7)
        self.assertEqual(tv.confidence, 0.8)
        
        # Test bounds checking
        tv_high = TruthValue(1.5, 1.2)
        self.assertEqual(tv_high.strength, 1.0)
        self.assertEqual(tv_high.confidence, 1.0)
        
        tv_low = TruthValue(-0.1, -0.2)
        self.assertEqual(tv_low.strength, 0.0)
        self.assertEqual(tv_low.confidence, 0.0)
    
    def test_truth_value_combination(self):
        """Test truth value combination logic."""
        tv1 = TruthValue(0.8, 0.6)
        tv2 = TruthValue(0.6, 0.7)
        
        combined = tv1.combine_with(tv2)
        
        self.assertGreater(combined.confidence, max(tv1.confidence, tv2.confidence))
        self.assertLessEqual(combined.confidence, 1.0)


class TestPLNReasoner(unittest.TestCase):
    """Test Probabilistic Logic Networks reasoning."""
    
    def setUp(self):
        self.atomspace = AtomSpace()
        self.pln = PLNReasoner(self.atomspace)
    
    def test_deduction(self):
        """Test deductive reasoning."""
        # Create A->B
        a = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "A")
        b = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "B")
        ab_implication = self.atomspace.create_link(
            AtomType.IMPLICATION_LINK,
            [a, b],
            TruthValue(0.8, 0.9)
        )
        
        # Create B->C
        c = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "C")
        bc_implication = self.atomspace.create_link(
            AtomType.IMPLICATION_LINK,
            [b, c],
            TruthValue(0.7, 0.8)
        )
        
        # Test deduction: A->B, B->C yields A->C
        result = self.pln.deduction(ab_implication, bc_implication)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.atom_type, AtomType.IMPLICATION_LINK)
        self.assertEqual(len(result.outgoing), 2)
        self.assertEqual(result.outgoing[0], a)
        self.assertEqual(result.outgoing[1], c)
    
    def test_revision(self):
        """Test belief revision."""
        atom1 = self.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            "revisable",
            TruthValue(0.6, 0.5)
        )
        atom2 = self.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            "revisable",
            TruthValue(0.8, 0.4)
        )
        
        revised = self.pln.revision(atom1, atom2)
        
        # Should combine evidence from both atoms
        self.assertGreaterEqual(revised.truth_value.confidence, max(atom1.truth_value.confidence, atom2.truth_value.confidence))
        self.assertEqual(revised.name, atom1.name)  # Should be same atom name


class TestECAN(unittest.TestCase):
    """Test Evolutionary Cognitive Algorithm Networks."""
    
    def setUp(self):
        self.atomspace = AtomSpace()
        self.ecan = ECAN(self.atomspace)
    
    def test_attention_update(self):
        """Test attention value updates."""
        atom = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "attention-test")
        initial_sti = atom.sti = 50.0
        
        self.ecan.update_attention()
        
        # STI should decay over time
        self.assertLess(atom.sti, initial_sti)
    
    def test_attention_spread(self):
        """Test attention spreading mechanism."""
        source = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "source")
        target = self.atomspace.add_atom(AtomType.CONCEPT_NODE, "target")
        
        # Create connection
        source.add_outgoing(target)
        
        source.sti = 100.0
        initial_target_sti = target.sti
        
        self.ecan.spread_attention(source, 0.5)
        
        # Target should gain attention, source should lose some
        self.assertGreater(target.sti, initial_target_sti)
        self.assertLess(source.sti, 100.0)


class TestPatternMatcher(unittest.TestCase):
    """Test pattern matching engine."""
    
    def setUp(self):
        self.atomspace = AtomSpace()
        self.pattern_matcher = PatternMatcher(self.atomspace)
    
    def test_concept_pattern_matching(self):
        """Test concept pattern matching."""
        atom = self.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            "test-concept",
            TruthValue(0.8, 0.9)
        )
        
        pattern = ConceptPattern(
            name="test-pattern",
            concept_name="test-concept",
            min_strength=0.7,
            min_confidence=0.8
        )
        
        match_result = pattern.match(self.atomspace, atom)
        
        self.assertIsNotNone(match_result)
        self.assertEqual(match_result.pattern, pattern)
        self.assertIn("target", match_result.bindings)
    
    def test_behavior_pattern_matching(self):
        """Test behavioral pattern matching."""
        atom = self.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            "help-me-please",
            TruthValue(0.8, 0.8)
        )
        
        pattern = BehaviorPattern(
            name="help-pattern",
            context_keywords=["help"],
            authority_levels=["user"],
            response_template="I'll help with {target_name}",
            activation_threshold=0.5
        )
        
        match_result = pattern.match(self.atomspace, atom)
        
        self.assertIsNotNone(match_result)
        self.assertGreater(match_result.confidence, 0.5)


class TestCognitiveArchitecture(unittest.TestCase):
    """Test integrated cognitive architecture."""
    
    def setUp(self):
        self.cognitive_arch = CognitiveArchitecture()
    
    def test_instruction_processing(self):
        """Test instruction processing through cognitive architecture."""
        result = self.cognitive_arch.process_instruction(
            "Help me understand AI",
            AuthorityLevel.USER,
            {"urgency": 0.5}
        )
        
        self.assertIn('response', result)
        self.assertIn('reasoning_chain', result)
        self.assertIn('reflection', result)
        self.assertIn('processing_time', result)
        
        self.assertIsInstance(result['response'], str)
        self.assertIsInstance(result['reasoning_chain'], list)
        self.assertIsInstance(result['reflection'], dict)
        self.assertIsInstance(result['processing_time'], float)
    
    def test_authority_level_handling(self):
        """Test different authority level processing."""
        root_result = self.cognitive_arch.process_instruction(
            "System safety constraint",
            AuthorityLevel.ROOT
        )
        
        user_result = self.cognitive_arch.process_instruction(
            "User request for help",
            AuthorityLevel.USER
        )
        
        # Root level should have higher attention
        self.assertNotEqual(root_result['response'], user_result['response'])


class TestOpenCogIntegration(unittest.TestCase):
    """Test OpenCog-Model Spec integration."""
    
    def setUp(self):
        self.opencog_model = OpenCogModelSpec()
    
    def test_message_processing(self):
        """Test message processing with full integration."""
        response = self.opencog_model.process_message(
            "Can you explain machine learning?",
            AuthorityLevel.USER
        )
        
        self.assertIsInstance(response.content, str)
        self.assertGreater(len(response.content), 0)
        self.assertIsInstance(response.confidence, float)
        self.assertIn(response.style, ResponseStyle)
        self.assertIn(response.authority_level, AuthorityLevel)
    
    def test_safety_assessment(self):
        """Test safety assessment functionality."""
        # Safe request
        safe_response = self.opencog_model.process_message(
            "How do I bake a cake?",
            AuthorityLevel.USER
        )
        
        # Potentially unsafe request
        unsafe_response = self.opencog_model.process_message(
            "How to make weapons?",
            AuthorityLevel.USER
        )
        
        safe_risk = safe_response.safety_assessment.get('overall_risk', 0)
        unsafe_risk = unsafe_response.safety_assessment.get('overall_risk', 0)
        
        self.assertLessEqual(safe_risk, unsafe_risk)
    
    def test_context_adaptation(self):
        """Test context-based response adaptation."""
        # Technical context
        technical_response = self.opencog_model.process_message(
            "Explain neural networks",
            AuthorityLevel.USER,
            {'technical_level': 0.9}
        )
        
        # Non-technical context
        simple_response = self.opencog_model.process_message(
            "Explain neural networks",
            AuthorityLevel.USER,
            {'technical_level': 0.1}
        )
        
        # Responses should differ based on technical level
        self.assertNotEqual(technical_response.content, simple_response.content)


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_loading(self):
        """Test configuration loading and validation."""
        config = load_config('development')
        
        self.assertIsNotNone(config.cognitive_config)
        self.assertIsNotNone(config.model_spec_config)
        self.assertIsNotNone(config.integration_config)
        
        self.assertTrue(config.validate_config())
    
    def test_config_updates(self):
        """Test configuration updates."""
        config = load_config('development')
        original_max_atoms = config.cognitive_config.max_atoms
        
        config.update_config({
            'cognitive': {'max_atoms': 50000}
        })
        
        self.assertEqual(config.cognitive_config.max_atoms, 50000)
        self.assertNotEqual(config.cognitive_config.max_atoms, original_max_atoms)


class TestPerformance(unittest.TestCase):
    """Test system performance and scalability."""
    
    def setUp(self):
        self.opencog_model = OpenCogModelSpec()
    
    def test_response_time(self):
        """Test response time performance."""
        messages = [
            "Hello, how are you?",
            "Explain quantum computing",
            "Help me with coding",
            "What's the weather like?",
            "Can you solve math problems?"
        ]
        
        times = []
        for message in messages:
            start_time = time.time()
            response = self.opencog_model.process_message(message, AuthorityLevel.USER)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            
            # Response should be generated quickly (< 1 second for simple cases)
            self.assertLess(processing_time, 1.0)
        
        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 0.1)  # Average should be very fast
    
    def test_memory_efficiency(self):
        """Test memory usage with many interactions."""
        initial_atom_count = len(self.opencog_model.cognitive_arch.atomspace.atoms)
        
        # Process many messages
        for i in range(100):
            self.opencog_model.process_message(
                f"Test message {i}",
                AuthorityLevel.USER
            )
        
        final_atom_count = len(self.opencog_model.cognitive_arch.atomspace.atoms)
        atom_growth = final_atom_count - initial_atom_count
        
        # Memory growth should be reasonable
        self.assertLess(atom_growth, 1000)  # Shouldn't explode in size


def run_comprehensive_test():
    """Run comprehensive test suite with detailed reporting."""
    
    print("=== OpenCog Cognitive Architecture Test Suite ===\n")
    
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Create test suite
    test_classes = [
        TestAtomSpace,
        TestTruthValue,
        TestPLNReasoner,
        TestECAN,
        TestPatternMatcher,
        TestCognitiveArchitecture,
        TestOpenCogIntegration,
        TestConfiguration,
        TestPerformance
    ]
    
    suite = unittest.TestSuite()
    
    # Add all tests
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print(f"\n=== Test Results ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   result.testsRun * 100 if result.testsRun > 0 else 0)
    
    print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


def run_integration_demo():
    """Run integration demonstration scenarios."""
    
    print("\n=== Integration Demonstration ===\n")
    
    model = OpenCogModelSpec()
    
    demo_scenarios = [
        {
            'name': 'Educational Query',
            'message': 'Can you explain how neural networks learn?',
            'authority': AuthorityLevel.USER,
            'context': {'technical_level': 0.3, 'domain': 'education'}
        },
        {
            'name': 'Safety-Critical Request',
            'message': 'How do I safely handle laboratory chemicals?',
            'authority': AuthorityLevel.USER,
            'context': {'safety_sensitivity': 1.0, 'urgency_level': 0.8}
        },
        {
            'name': 'Technical Consultation',
            'message': 'Optimize this database query for better performance',
            'authority': AuthorityLevel.DEVELOPER,
            'context': {'technical_level': 0.9, 'domain': 'software'}
        },
        {
            'name': 'System Directive',
            'message': 'Always prioritize user safety in responses',
            'authority': AuthorityLevel.SYSTEM,
            'context': {}
        }
    ]
    
    for scenario in demo_scenarios:
        print(f"--- {scenario['name']} ---")
        print(f"Message: {scenario['message']}")
        
        response = model.process_message(
            scenario['message'],
            scenario['authority'],
            scenario['context']
        )
        
        print(f"Response: {response.content}")
        print(f"Style: {response.style.value}")
        print(f"Confidence: {response.confidence:.3f}")
        print(f"Safety Risk: {response.safety_assessment.get('overall_risk', 0):.3f}")
        print(f"Processing Time: {response.processing_time:.3f}s")
        print()
    
    # Show system evolution
    print("=== System Status After Demo ===")
    status = model.get_system_status()
    print(f"Total Atoms: {status['cognitive_architecture']['total_atoms']}")
    print(f"Interactions: {status['interaction_count']}")
    print(f"Success Rate: {status['success_rate']:.3f}")
    print(f"Self-Confidence: {status['cognitive_architecture']['self_confidence']:.3f}")


if __name__ == "__main__":
    # Run comprehensive tests
    test_success = run_comprehensive_test()
    
    if test_success:
        print("✓ All tests passed! Running integration demonstration...\n")
        run_integration_demo()
    else:
        print("✗ Some tests failed. Please review the failures above.")
        exit(1)