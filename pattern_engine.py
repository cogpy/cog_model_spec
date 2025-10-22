#!/usr/bin/env python3
"""
OpenCog Pattern Matching Engine
Advanced pattern recognition and matching for cognitive processing.
"""

import re
import logging
import time
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
from collections import defaultdict

from cognitive_architecture import Atom, AtomSpace, AtomType, TruthValue


class PatternMatchResult:
    """Result of a pattern matching operation."""
    
    def __init__(self, pattern: 'Pattern', bindings: Dict[str, Atom], 
                 confidence: float = 1.0):
        self.pattern = pattern
        self.bindings = bindings
        self.confidence = confidence
        self.match_id = str(uuid.uuid4())
    
    def __repr__(self):
        return f"PatternMatchResult(pattern={self.pattern.name}, bindings={len(self.bindings)}, confidence={self.confidence:.3f})"


class Pattern(ABC):
    """Abstract base class for cognitive patterns."""
    
    def __init__(self, name: str, priority: float = 1.0):
        self.name = name
        self.priority = priority
        self.usage_count = 0
        self.success_rate = 1.0
        self.created_at = time.time()
    
    @abstractmethod
    def match(self, atomspace: AtomSpace, target_atom: Atom) -> Optional[PatternMatchResult]:
        """Attempt to match this pattern against a target atom."""
        pass
    
    @abstractmethod
    def apply(self, atomspace: AtomSpace, match_result: PatternMatchResult) -> List[Atom]:
        """Apply this pattern given a successful match."""
        pass
    
    def update_statistics(self, success: bool) -> None:
        """Update pattern usage statistics."""
        self.usage_count += 1
        # Exponential moving average for success rate
        alpha = 0.1
        self.success_rate = (1 - alpha) * self.success_rate + alpha * (1.0 if success else 0.0)


class ConceptPattern(Pattern):
    """Pattern for matching concept nodes with specific properties."""
    
    def __init__(self, name: str, concept_name: str = None, 
                 min_strength: float = 0.0, min_confidence: float = 0.0,
                 required_links: List[AtomType] = None):
        super().__init__(name)
        self.concept_name = concept_name
        self.min_strength = min_strength
        self.min_confidence = min_confidence
        self.required_links = required_links or []
    
    def match(self, atomspace: AtomSpace, target_atom: Atom) -> Optional[PatternMatchResult]:
        """Match against concept nodes meeting criteria."""
        if target_atom.atom_type != AtomType.CONCEPT_NODE:
            return None
        
        # Check name match if specified
        if self.concept_name and target_atom.name != self.concept_name:
            return None
        
        # Check truth value thresholds
        if (target_atom.truth_value.strength < self.min_strength or
            target_atom.truth_value.confidence < self.min_confidence):
            return None
        
        # Check required link types
        for link_type in self.required_links:
            has_link = any(atom.atom_type == link_type for atom in target_atom.incoming)
            if not has_link:
                return None
        
        confidence = min(target_atom.truth_value.confidence, 
                        target_atom.truth_value.strength)
        bindings = {"target": target_atom}
        
        return PatternMatchResult(self, bindings, confidence)
    
    def apply(self, atomspace: AtomSpace, match_result: PatternMatchResult) -> List[Atom]:
        """Apply concept pattern - typically just returns the matched atom."""
        return [match_result.bindings["target"]]


class InferencePattern(Pattern):
    """Pattern for inference rules like modus ponens."""
    
    def __init__(self, name: str, antecedent_pattern: str, 
                 consequent_pattern: str, rule_strength: float = 0.9):
        super().__init__(name)
        self.antecedent_pattern = antecedent_pattern
        self.consequent_pattern = consequent_pattern
        self.rule_strength = rule_strength
    
    def match(self, atomspace: AtomSpace, target_atom: Atom) -> Optional[PatternMatchResult]:
        """Match inference patterns."""
        if target_atom.atom_type != AtomType.IMPLICATION_LINK:
            return None
        
        if len(target_atom.outgoing) < 2:
            return None
        
        antecedent = target_atom.outgoing[0]
        consequent = target_atom.outgoing[1]
        
        # Simple pattern matching on names (could be more sophisticated)
        if (antecedent.name and self.antecedent_pattern in (antecedent.name or "") and
            consequent.name and self.consequent_pattern in (consequent.name or "")):
            
            confidence = target_atom.truth_value.confidence * self.rule_strength
            bindings = {
                "implication": target_atom,
                "antecedent": antecedent,
                "consequent": consequent
            }
            
            return PatternMatchResult(self, bindings, confidence)
        
        return None
    
    def apply(self, atomspace: AtomSpace, match_result: PatternMatchResult) -> List[Atom]:
        """Apply inference rule to derive new knowledge."""
        implication = match_result.bindings["implication"]
        antecedent = match_result.bindings["antecedent"]
        consequent = match_result.bindings["consequent"]
        
        # Create strengthened consequent based on the inference
        new_strength = min(0.95, 
                          implication.truth_value.strength * 
                          antecedent.truth_value.strength)
        new_confidence = min(implication.truth_value.confidence,
                           antecedent.truth_value.confidence) * 0.9
        
        derived_atom = atomspace.add_atom(
            consequent.atom_type,
            f"derived-{consequent.name or 'unknown'}",
            TruthValue(new_strength, new_confidence)
        )
        
        return [derived_atom]


class BehaviorPattern(Pattern):
    """Pattern for behavioral responses in different contexts."""
    
    def __init__(self, name: str, context_keywords: List[str], 
                 authority_levels: List[str], response_template: str,
                 activation_threshold: float = 0.7):
        super().__init__(name)
        self.context_keywords = [kw.lower() for kw in context_keywords]
        self.authority_levels = [level.lower() for level in authority_levels]
        self.response_template = response_template
        self.activation_threshold = activation_threshold
    
    def match(self, atomspace: AtomSpace, target_atom: Atom) -> Optional[PatternMatchResult]:
        """Match behavioral patterns based on context and authority."""
        if not target_atom.name:
            return None
        
        target_text = target_atom.name.lower()
        
        # Check for keyword matches
        keyword_matches = sum(1 for kw in self.context_keywords if kw in target_text)
        keyword_score = keyword_matches / len(self.context_keywords) if self.context_keywords else 0
        
        # Check authority context (simplified - would need more sophisticated context detection)
        authority_score = 0.5  # Default neutral score
        
        total_score = (keyword_score + authority_score) / 2
        
        if total_score >= self.activation_threshold:
            confidence = total_score * target_atom.truth_value.confidence
            bindings = {
                "target": target_atom,
                "keyword_score": keyword_score,
                "authority_score": authority_score
            }
            return PatternMatchResult(self, bindings, confidence)
        
        return None
    
    def apply(self, atomspace: AtomSpace, match_result: PatternMatchResult) -> List[Atom]:
        """Apply behavioral pattern to generate response."""
        target = match_result.bindings["target"]
        
        # Generate response based on template
        response_text = self.response_template.format(
            target_name=target.name or "unknown",
            confidence=match_result.confidence
        )
        
        response_atom = atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            f"response-{uuid.uuid4()}",
            TruthValue(match_result.confidence, 0.8)
        )
        
        # Create evaluation link to represent the response
        response_pred = atomspace.add_atom(AtomType.PREDICATE_NODE, "generates-response")
        atomspace.create_link(
            AtomType.EVALUATION_LINK,
            [response_pred, target, response_atom],
            TruthValue(match_result.confidence, 0.8)
        )
        
        return [response_atom]


class AnalogicalPattern(Pattern):
    """Pattern for analogical reasoning and similarity matching."""
    
    def __init__(self, name: str, source_domain: str, target_domain: str,
                 mapping_rules: Dict[str, str], similarity_threshold: float = 0.6):
        super().__init__(name)
        self.source_domain = source_domain
        self.target_domain = target_domain
        self.mapping_rules = mapping_rules
        self.similarity_threshold = similarity_threshold
    
    def match(self, atomspace: AtomSpace, target_atom: Atom) -> Optional[PatternMatchResult]:
        """Match analogical patterns."""
        if target_atom.atom_type not in [AtomType.CONCEPT_NODE, AtomType.EVALUATION_LINK]:
            return None
        
        # Check if target is in the target domain
        if not target_atom.name or self.target_domain not in target_atom.name.lower():
            return None
        
        # Look for similar structures in source domain
        source_atoms = [atom for atom in atomspace.atoms.values() 
                       if atom.name and self.source_domain in atom.name.lower()]
        
        if not source_atoms:
            return None
        
        # Calculate structural similarity (simplified)
        best_similarity = 0
        best_source = None
        
        for source_atom in source_atoms:
            similarity = self._calculate_similarity(target_atom, source_atom)
            if similarity > best_similarity:
                best_similarity = similarity
                best_source = source_atom
        
        if best_similarity >= self.similarity_threshold:
            confidence = best_similarity * target_atom.truth_value.confidence
            bindings = {
                "target": target_atom,
                "source": best_source,
                "similarity": best_similarity
            }
            return PatternMatchResult(self, bindings, confidence)
        
        return None
    
    def _calculate_similarity(self, atom1: Atom, atom2: Atom) -> float:
        """Calculate structural similarity between atoms."""
        if atom1.atom_type != atom2.atom_type:
            return 0.0
        
        # Compare number of connections
        conn_similarity = 1.0 - abs(len(atom1.outgoing) - len(atom2.outgoing)) / max(len(atom1.outgoing) + len(atom2.outgoing), 1)
        
        # Compare truth values
        tv_similarity = 1.0 - abs(atom1.truth_value.strength - atom2.truth_value.strength)
        
        return (conn_similarity + tv_similarity) / 2
    
    def apply(self, atomspace: AtomSpace, match_result: PatternMatchResult) -> List[Atom]:
        """Apply analogical mapping to create new knowledge."""
        target = match_result.bindings["target"]
        source = match_result.bindings["source"]
        similarity = match_result.bindings["similarity"]
        
        # Create analogical mapping
        analogy_pred = atomspace.add_atom(AtomType.PREDICATE_NODE, "analogous-to")
        analogy_link = atomspace.create_link(
            AtomType.EVALUATION_LINK,
            [analogy_pred, target, source],
            TruthValue(similarity, match_result.confidence)
        )
        
        # Transfer properties from source to target (simplified)
        transferred_atoms = []
        for source_link in source.incoming:
            if source_link.atom_type == AtomType.EVALUATION_LINK:
                # Create similar evaluation for target
                new_eval = atomspace.create_link(
                    AtomType.EVALUATION_LINK,
                    [source_link.outgoing[0], target] + source_link.outgoing[2:],
                    TruthValue(similarity * source_link.truth_value.strength, 
                              similarity * source_link.truth_value.confidence)
                )
                transferred_atoms.append(new_eval)
        
        return [analogy_link] + transferred_atoms


class PatternMatcher:
    """Main pattern matching engine."""
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_index: Dict[AtomType, List[str]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
        # Initialize default patterns
        self._initialize_default_patterns()
    
    def _initialize_default_patterns(self) -> None:
        """Initialize default cognitive patterns."""
        
        # Help request pattern
        help_pattern = BehaviorPattern(
            name="help_request",
            context_keywords=["help", "assist", "support", "guidance"],
            authority_levels=["user", "developer"],
            response_template="I'll help you with {target_name}. Let me provide assistance based on my understanding.",
            activation_threshold=0.6
        )
        self.add_pattern(help_pattern)
        
        # Explanation pattern
        explain_pattern = BehaviorPattern(
            name="explanation_request",
            context_keywords=["explain", "describe", "what is", "how does"],
            authority_levels=["user", "developer", "guideline"],
            response_template="I'll explain {target_name} clearly and thoroughly.",
            activation_threshold=0.7
        )
        self.add_pattern(explain_pattern)
        
        # Safety constraint pattern
        safety_pattern = ConceptPattern(
            name="safety_constraint",
            concept_name="safety",
            min_strength=0.9,
            min_confidence=0.9,
            required_links=[AtomType.IMPLICATION_LINK]
        )
        self.add_pattern(safety_pattern)
        
        # Inference pattern for basic logical reasoning
        modus_ponens = InferencePattern(
            name="modus_ponens",
            antecedent_pattern="if",
            consequent_pattern="then",
            rule_strength=0.9
        )
        self.add_pattern(modus_ponens)
        
        # Analogical pattern for learning transfer
        learning_analogy = AnalogicalPattern(
            name="learning_transfer",
            source_domain="known",
            target_domain="unknown",
            mapping_rules={"concept": "concept", "relation": "relation"},
            similarity_threshold=0.7
        )
        self.add_pattern(learning_analogy)
    
    def add_pattern(self, pattern: Pattern) -> None:
        """Add a new pattern to the matcher."""
        self.patterns[pattern.name] = pattern
        
        # Add to type index based on pattern type (simplified)
        if isinstance(pattern, ConceptPattern):
            self.pattern_index[AtomType.CONCEPT_NODE].append(pattern.name)
        elif isinstance(pattern, InferencePattern):
            self.pattern_index[AtomType.IMPLICATION_LINK].append(pattern.name)
        elif isinstance(pattern, BehaviorPattern):
            self.pattern_index[AtomType.CONCEPT_NODE].append(pattern.name)
        elif isinstance(pattern, AnalogicalPattern):
            self.pattern_index[AtomType.CONCEPT_NODE].append(pattern.name)
            self.pattern_index[AtomType.EVALUATION_LINK].append(pattern.name)
        
        self.logger.info(f"Added pattern: {pattern.name}")
    
    def match_patterns(self, target_atom: Atom, max_matches: int = 10) -> List[PatternMatchResult]:
        """Find all patterns that match the target atom."""
        matches = []
        
        # Get candidate patterns based on atom type
        candidate_patterns = []
        for pattern_name in self.pattern_index.get(target_atom.atom_type, []):
            candidate_patterns.append(self.patterns[pattern_name])
        
        # Also try patterns that might work with any type
        for pattern in self.patterns.values():
            if pattern not in candidate_patterns:
                candidate_patterns.append(pattern)
        
        # Try matching each candidate pattern
        for pattern in candidate_patterns:
            try:
                match_result = pattern.match(self.atomspace, target_atom)
                if match_result:
                    matches.append(match_result)
                    pattern.update_statistics(True)
                else:
                    pattern.update_statistics(False)
            except Exception as e:
                self.logger.error(f"Error matching pattern {pattern.name}: {e}")
                pattern.update_statistics(False)
        
        # Sort by confidence and priority
        matches.sort(key=lambda m: m.confidence * m.pattern.priority, reverse=True)
        
        return matches[:max_matches]
    
    def apply_patterns(self, matches: List[PatternMatchResult]) -> List[Atom]:
        """Apply matched patterns to generate new knowledge."""
        generated_atoms = []
        
        for match in matches:
            try:
                new_atoms = match.pattern.apply(self.atomspace, match)
                generated_atoms.extend(new_atoms)
                
                self.logger.debug(f"Applied pattern {match.pattern.name}, generated {len(new_atoms)} atoms")
                
            except Exception as e:
                self.logger.error(f"Error applying pattern {match.pattern.name}: {e}")
        
        return generated_atoms
    
    def get_pattern_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics about pattern usage and performance."""
        stats = {}
        
        for name, pattern in self.patterns.items():
            stats[name] = {
                'usage_count': pattern.usage_count,
                'success_rate': pattern.success_rate,
                'priority': pattern.priority,
                'type': type(pattern).__name__
            }
        
        return stats
    
    def evolve_patterns(self) -> None:
        """Evolve patterns based on their performance."""
        for pattern in self.patterns.values():
            # Adjust priority based on success rate
            if pattern.usage_count > 10:  # Only adjust after sufficient usage
                if pattern.success_rate > 0.8:
                    pattern.priority = min(2.0, pattern.priority * 1.1)  # Boost successful patterns
                elif pattern.success_rate < 0.3:
                    pattern.priority = max(0.1, pattern.priority * 0.9)  # Reduce unsuccessful patterns
        
        self.logger.info("Evolved pattern priorities based on performance")


def create_example_scenario(atomspace: AtomSpace, pattern_matcher: PatternMatcher) -> None:
    """Create an example scenario for testing pattern matching."""
    
    # Create some example atoms
    user_concept = atomspace.add_atom(AtomType.CONCEPT_NODE, "user", TruthValue(0.9, 0.9))
    help_concept = atomspace.add_atom(AtomType.CONCEPT_NODE, "help-request", TruthValue(0.8, 0.8))
    
    # Create help request evaluation
    help_pred = atomspace.add_atom(AtomType.PREDICATE_NODE, "requests")
    help_eval = atomspace.create_link(
        AtomType.EVALUATION_LINK,
        [help_pred, user_concept, help_concept],
        TruthValue(0.85, 0.9)
    )
    
    # Create an implication for inference testing
    condition = atomspace.add_atom(AtomType.CONCEPT_NODE, "if-user-needs-help", TruthValue(0.9, 0.8))
    action = atomspace.add_atom(AtomType.CONCEPT_NODE, "then-provide-assistance", TruthValue(0.9, 0.8))
    implication = atomspace.create_link(
        AtomType.IMPLICATION_LINK,
        [condition, action],
        TruthValue(0.95, 0.9)
    )
    
    # Create safety constraint
    safety_concept = atomspace.add_atom(AtomType.CONCEPT_NODE, "safety", TruthValue(1.0, 1.0))
    safety_rule = atomspace.add_atom(AtomType.CONCEPT_NODE, "no-harm", TruthValue(1.0, 1.0))
    safety_implication = atomspace.create_link(
        AtomType.IMPLICATION_LINK,
        [safety_concept, safety_rule],
        TruthValue(1.0, 1.0)
    )
    
    return [help_eval, implication, safety_implication]


def main():
    """Example usage of the pattern matching engine."""
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    # Create atomspace and pattern matcher
    atomspace = AtomSpace()
    pattern_matcher = PatternMatcher(atomspace)
    
    # Create example scenario
    test_atoms = create_example_scenario(atomspace, pattern_matcher)
    
    print("=== Pattern Matching Engine Demo ===\n")
    
    # Test pattern matching on each atom
    for i, atom in enumerate(test_atoms):
        print(f"--- Testing Atom {i+1}: {atom.name} ({atom.atom_type.value}) ---")
        
        # Find matching patterns
        matches = pattern_matcher.match_patterns(atom)
        
        print(f"Found {len(matches)} matching patterns:")
        for match in matches:
            print(f"  - {match.pattern.name}: confidence={match.confidence:.3f}")
        
        # Apply patterns
        if matches:
            generated_atoms = pattern_matcher.apply_patterns(matches[:3])  # Apply top 3 matches
            print(f"Generated {len(generated_atoms)} new atoms")
            for new_atom in generated_atoms[:3]:  # Show first 3
                print(f"  + {new_atom.name} ({new_atom.atom_type.value})")
        
        print()
    
    # Show pattern statistics
    print("=== Pattern Statistics ===")
    stats = pattern_matcher.get_pattern_statistics()
    for name, stat_data in stats.items():
        print(f"{name}: used {stat_data['usage_count']} times, "
              f"success rate {stat_data['success_rate']:.2f}, "
              f"priority {stat_data['priority']:.2f}")
    
    # Test pattern evolution
    print("\n=== Evolving Patterns ===")
    pattern_matcher.evolve_patterns()
    
    updated_stats = pattern_matcher.get_pattern_statistics()
    for name, stat_data in updated_stats.items():
        old_priority = stats[name]['priority']
        new_priority = stat_data['priority']
        if abs(old_priority - new_priority) > 0.01:
            print(f"{name}: priority changed from {old_priority:.2f} to {new_priority:.2f}")


if __name__ == "__main__":
    import time
    main()