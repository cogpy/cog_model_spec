#!/usr/bin/env python3
"""
OpenCog Cognitive Architecture Implementation
Core cognitive processing system integrating OpenCog principles with Model Spec behavior guidelines.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import json
from collections import defaultdict


class AtomType(Enum):
    """OpenCog atom types for knowledge representation."""
    CONCEPT_NODE = "ConceptNode"
    PREDICATE_NODE = "PredicateNode"
    EVALUATION_LINK = "EvaluationLink"
    INHERITANCE_LINK = "InheritanceLink"
    SIMILARITY_LINK = "SimilarityLink"
    IMPLICATION_LINK = "ImplicationLink"
    LIST_LINK = "ListLink"
    VARIABLE_NODE = "VariableNode"
    META_REFLECTION_LINK = "MetaReflectionLink"


class AuthorityLevel(Enum):
    """Model Spec authority levels integrated with cognitive processing."""
    ROOT = 1      # Inviolable constraints
    SYSTEM = 2    # OpenCog enhanced system level
    DEVELOPER = 3 # Developer instructions with cognitive processing
    USER = 4      # User requests with contextual interpretation
    GUIDELINE = 5 # Flexible guidelines with probabilistic application


@dataclass
class TruthValue:
    """OpenCog truth value representing probabilistic confidence."""
    strength: float  # Probability estimate (0.0 to 1.0)
    confidence: float  # Confidence in the estimate (0.0 to 1.0)
    
    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def combine_with(self, other: 'TruthValue') -> 'TruthValue':
        """Combine truth values using OpenCog's revision formula."""
        combined_confidence = self.confidence + other.confidence
        if combined_confidence > 0:
            combined_strength = (
                (self.strength * self.confidence + other.strength * other.confidence) /
                combined_confidence
            )
        else:
            combined_strength = 0.5
        
        # Ensure confidence increases but doesn't exceed reasonable bounds
        final_confidence = min(0.99, combined_confidence)  # Cap at 0.99 to avoid 1.0
        return TruthValue(combined_strength, final_confidence)


@dataclass
class Atom:
    """Base atom class for OpenCog knowledge representation."""
    atom_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    atom_type: AtomType = AtomType.CONCEPT_NODE
    name: Optional[str] = None
    truth_value: TruthValue = field(default_factory=lambda: TruthValue(0.8, 0.8))
    sti: float = 0.0  # Short-term importance
    lti: float = 0.0  # Long-term importance
    vlti: float = 0.0  # Very long-term importance
    outgoing: List['Atom'] = field(default_factory=list)
    incoming: List['Atom'] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    
    def add_outgoing(self, atom: 'Atom') -> None:
        """Add an outgoing atom link."""
        if atom not in self.outgoing:
            self.outgoing.append(atom)
            if self not in atom.incoming:
                atom.incoming.append(self)
    
    def remove_outgoing(self, atom: 'Atom') -> None:
        """Remove an outgoing atom link."""
        if atom in self.outgoing:
            self.outgoing.remove(atom)
            if self in atom.incoming:
                atom.incoming.remove(self)
    
    def get_attention_value(self) -> float:
        """Calculate current attention value based on importance metrics."""
        return self.sti + 0.1 * self.lti + 0.01 * self.vlti


class AtomSpace:
    """OpenCog AtomSpace for knowledge representation and storage."""
    
    def __init__(self):
        self.atoms: Dict[str, Atom] = {}
        self.type_index: Dict[AtomType, List[str]] = defaultdict(list)
        self.name_index: Dict[str, List[str]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
        # Initialize core cognitive concepts
        self._initialize_core_concepts()
    
    def _initialize_core_concepts(self) -> None:
        """Initialize fundamental cognitive concepts."""
        # Self-concept
        self_concept = self.add_atom(AtomType.CONCEPT_NODE, "self", TruthValue(1.0, 1.0))
        self_concept.vlti = 1.0
        
        # Core authority concepts
        for level in AuthorityLevel:
            authority_atom = self.add_atom(
                AtomType.CONCEPT_NODE, 
                f"authority-{level.name.lower()}", 
                TruthValue(1.0, 0.9)
            )
            authority_atom.lti = 1.0 - (level.value * 0.1)
    
    def add_atom(self, atom_type: AtomType, name: str = None, 
                truth_value: TruthValue = None) -> Atom:
        """Add a new atom to the AtomSpace."""
        atom = Atom(
            atom_type=atom_type,
            name=name,
            truth_value=truth_value or TruthValue(0.8, 0.8)
        )
        
        self.atoms[atom.atom_id] = atom
        self.type_index[atom_type].append(atom.atom_id)
        
        if name:
            self.name_index[name].append(atom.atom_id)
        
        self.logger.debug(f"Added atom: {atom_type.value} '{name}' ({atom.atom_id})")
        return atom
    
    def get_atoms_by_type(self, atom_type: AtomType) -> List[Atom]:
        """Get all atoms of a specific type."""
        return [self.atoms[atom_id] for atom_id in self.type_index[atom_type]]
    
    def get_atoms_by_name(self, name: str) -> List[Atom]:
        """Get all atoms with a specific name."""
        return [self.atoms[atom_id] for atom_id in self.name_index[name]]
    
    def create_link(self, link_type: AtomType, outgoing: List[Atom], 
                   truth_value: TruthValue = None) -> Atom:
        """Create a link atom connecting other atoms."""
        link = self.add_atom(link_type, truth_value=truth_value)
        
        for atom in outgoing:
            link.add_outgoing(atom)
        
        return link
    
    def get_high_attention_atoms(self, limit: int = 100) -> List[Atom]:
        """Get atoms with highest attention values."""
        sorted_atoms = sorted(
            self.atoms.values(),
            key=lambda a: a.get_attention_value(),
            reverse=True
        )
        return sorted_atoms[:limit]


class PLNReasoner:
    """Probabilistic Logic Networks reasoning engine."""
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.logger = logging.getLogger(__name__)
    
    def deduction(self, premise1: Atom, premise2: Atom) -> Optional[Atom]:
        """Perform deductive reasoning: A->B, B->C yields A->C."""
        if (premise1.atom_type == AtomType.IMPLICATION_LINK and
            premise2.atom_type == AtomType.IMPLICATION_LINK and
            len(premise1.outgoing) >= 2 and len(premise2.outgoing) >= 2):
            
            # Check if conclusion of premise1 matches antecedent of premise2
            if premise1.outgoing[1] == premise2.outgoing[0]:
                # Create new implication
                new_strength = premise1.truth_value.strength * premise2.truth_value.strength
                new_confidence = min(premise1.truth_value.confidence, 
                                   premise2.truth_value.confidence) * 0.9
                
                conclusion = self.atomspace.create_link(
                    AtomType.IMPLICATION_LINK,
                    [premise1.outgoing[0], premise2.outgoing[1]],
                    TruthValue(new_strength, new_confidence)
                )
                
                self.logger.info(f"Deduction: Created new implication with strength {new_strength:.3f}")
                return conclusion
        
        return None
    
    def induction(self, observations: List[Atom]) -> Optional[Atom]:
        """Perform inductive reasoning to generalize from observations."""
        if len(observations) < 2:
            return None
        
        # Find common patterns in observations
        pattern_strength = len(observations) / (len(observations) + 10)  # Confidence grows with evidence
        pattern_confidence = min(0.9, len(observations) * 0.1)
        
        # Create generalized rule (simplified)
        generalization = self.atomspace.add_atom(
            AtomType.IMPLICATION_LINK,
            truth_value=TruthValue(pattern_strength, pattern_confidence)
        )
        
        self.logger.info(f"Induction: Created generalization from {len(observations)} observations")
        return generalization
    
    def revision(self, belief1: Atom, belief2: Atom) -> Atom:
        """Revise beliefs by combining evidence."""
        if belief1.name == belief2.name:
            combined_tv = belief1.truth_value.combine_with(belief2.truth_value)
            
            # Update belief1 with combined truth value
            belief1.truth_value = combined_tv
            
            self.logger.info(f"Revision: Updated belief strength to {combined_tv.strength:.3f}")
            return belief1
        
        return belief1


class ECAN:
    """Evolutionary Cognitive Algorithm Networks for attention allocation."""
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.attention_focus_boundary = 100
        self.logger = logging.getLogger(__name__)
    
    def update_attention(self) -> None:
        """Update attention values for all atoms."""
        current_time = time.time()
        
        for atom in self.atomspace.atoms.values():
            # Decay STI over time
            age_factor = max(0.1, 1.0 - (current_time - atom.created_at) / 3600)  # 1 hour decay
            atom.sti *= age_factor
            
            # Boost attention for recently active atoms
            if atom.incoming:  # Has been referenced
                atom.sti += 0.1
            
            # Convert STI to LTI over time
            sti_to_lti = atom.sti * 0.01
            atom.sti -= sti_to_lti
            atom.lti += sti_to_lti
        
        self.logger.debug("Updated attention values for all atoms")
    
    def get_attention_focus(self) -> List[Atom]:
        """Get atoms in the current attention focus."""
        return self.atomspace.get_high_attention_atoms(self.attention_focus_boundary)
    
    def spread_attention(self, source_atom: Atom, strength: float = 0.5) -> None:
        """Spread attention from a source atom to connected atoms."""
        attention_spread = source_atom.sti * strength
        
        for connected_atom in source_atom.outgoing + source_atom.incoming:
            connected_atom.sti += attention_spread * 0.1
        
        source_atom.sti *= (1.0 - strength)  # Source loses some attention


class MetaCognition:
    """Meta-cognitive monitoring and self-reflection system."""
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.self_model = self._create_self_model()
        self.performance_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def _create_self_model(self) -> Atom:
        """Create initial self-model representation."""
        self_atom = self.atomspace.get_atoms_by_name("self")[0]
        
        # Create cognitive state evaluation
        cognitive_state = self.atomspace.add_atom(
            AtomType.PREDICATE_NODE, 
            "cognitive-state",
            TruthValue(0.9, 0.9)
        )
        
        current_state = self.atomspace.create_link(
            AtomType.EVALUATION_LINK,
            [cognitive_state, self_atom],
            TruthValue(0.8, 0.8)
        )
        
        return current_state
    
    def monitor_performance(self, task: str, success: bool, metrics: Dict[str, float]) -> None:
        """Monitor and record performance for self-improvement."""
        performance_record = {
            'timestamp': time.time(),
            'task': task,
            'success': success,
            'metrics': metrics
        }
        
        self.performance_history.append(performance_record)
        
        # Update self-model based on performance
        self._update_self_assessment(success, metrics)
        
        self.logger.info(f"Recorded performance: {task} - {'Success' if success else 'Failure'}")
    
    def _update_self_assessment(self, success: bool, metrics: Dict[str, float]) -> None:
        """Update self-assessment based on recent performance."""
        confidence_adjustment = 0.1 if success else -0.05
        
        # Update self-model confidence
        if self.self_model.truth_value.confidence < 0.95:
            self.self_model.truth_value.confidence += confidence_adjustment * 0.1
            self.self_model.truth_value.confidence = max(0.1, min(0.95, 
                self.self_model.truth_value.confidence))
    
    def reflect_on_reasoning(self, reasoning_chain: List[Atom]) -> Dict[str, Any]:
        """Reflect on a reasoning process for quality assessment."""
        reflection = {
            'chain_length': len(reasoning_chain),
            'average_confidence': sum(atom.truth_value.confidence for atom in reasoning_chain) / len(reasoning_chain) if reasoning_chain else 0,
            'logical_consistency': self._assess_consistency(reasoning_chain),
            'attention_coherence': self._assess_attention_coherence(reasoning_chain)
        }
        
        self.logger.debug(f"Reasoning reflection: {reflection}")
        return reflection
    
    def _assess_consistency(self, chain: List[Atom]) -> float:
        """Assess logical consistency of reasoning chain."""
        if len(chain) < 2:
            return 1.0
        
        consistency_score = 1.0
        for i in range(len(chain) - 1):
            # Simple consistency check based on truth values
            if abs(chain[i].truth_value.strength - chain[i+1].truth_value.strength) > 0.5:
                consistency_score *= 0.8
        
        return consistency_score
    
    def _assess_attention_coherence(self, chain: List[Atom]) -> float:
        """Assess attention coherence in reasoning chain."""
        if not chain:
            return 1.0
        
        attention_values = [atom.get_attention_value() for atom in chain]
        if not attention_values:
            return 1.0
        
        # Check if attention decreases too rapidly (indicates poor focus)
        coherence = 1.0
        for i in range(len(attention_values) - 1):
            if attention_values[i+1] < attention_values[i] * 0.5:
                coherence *= 0.9
        
        return coherence


class CognitiveArchitecture:
    """Main cognitive architecture integrating all OpenCog components."""
    
    def __init__(self):
        self.atomspace = AtomSpace()
        self.pln = PLNReasoner(self.atomspace)
        self.ecan = ECAN(self.atomspace)
        self.metacognition = MetaCognition(self.atomspace)
        self.logger = logging.getLogger(__name__)
        
        # Initialize authority level atoms
        self._setup_authority_system()
    
    def _setup_authority_system(self) -> None:
        """Setup Model Spec authority level integration."""
        for level in AuthorityLevel:
            authority_atom = self.atomspace.get_atoms_by_name(f"authority-{level.name.lower()}")[0]
            
            # Create authority evaluation links
            authority_pred = self.atomspace.add_atom(
                AtomType.PREDICATE_NODE,
                "has-authority-level",
                TruthValue(1.0, 1.0)
            )
            
            self.atomspace.create_link(
                AtomType.EVALUATION_LINK,
                [authority_pred, authority_atom],
                TruthValue(1.0, 1.0)
            )
    
    def process_instruction(self, instruction: str, authority: AuthorityLevel, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process an instruction through the cognitive architecture."""
        start_time = time.time()
        
        # Create instruction atom
        instruction_atom = self.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            f"instruction-{uuid.uuid4()}",
            TruthValue(0.9, 0.8)
        )
        
        # Set attention based on authority level
        instruction_atom.sti = (6 - authority.value) * 20  # Higher authority = more attention
        
        # Update attention system
        self.ecan.update_attention()
        self.ecan.spread_attention(instruction_atom)
        
        # Get current attention focus for reasoning
        focus_atoms = self.ecan.get_attention_focus()
        
        # Perform reasoning about the instruction
        reasoning_chain = self._reason_about_instruction(instruction_atom, focus_atoms, context)
        
        # Generate response through pattern matching and reasoning
        response = self._generate_response(instruction, reasoning_chain, authority)
        
        # Meta-cognitive reflection
        reflection = self.metacognition.reflect_on_reasoning(reasoning_chain)
        
        # Record performance
        processing_time = time.time() - start_time
        self.metacognition.monitor_performance(
            f"instruction-{authority.name}",
            True,  # Assume success for now
            {
                'processing_time': processing_time,
                'reasoning_length': len(reasoning_chain),
                'attention_focus_size': len(focus_atoms)
            }
        )
        
        return {
            'response': response,
            'reasoning_chain': [atom.atom_id for atom in reasoning_chain],
            'reflection': reflection,
            'processing_time': processing_time,
            'authority_level': authority.name
        }
    
    def _reason_about_instruction(self, instruction_atom: Atom, focus_atoms: List[Atom], 
                                context: Dict[str, Any] = None) -> List[Atom]:
        """Reason about an instruction using available cognitive resources."""
        reasoning_chain = [instruction_atom]
        
        # Look for relevant patterns in focus atoms
        relevant_atoms = []
        for atom in focus_atoms:
            # Simple relevance heuristic - atoms with higher attention that might relate
            if atom.get_attention_value() > 10 and atom != instruction_atom:
                relevant_atoms.append(atom)
        
        # Perform deductive reasoning with relevant atoms
        for atom in relevant_atoms[:5]:  # Limit reasoning steps
            if atom.atom_type == AtomType.IMPLICATION_LINK:
                deduction_result = self.pln.deduction(instruction_atom, atom)
                if deduction_result:
                    reasoning_chain.append(deduction_result)
        
        # Add context-based reasoning if context provided
        if context:
            context_atom = self.atomspace.add_atom(
                AtomType.CONCEPT_NODE,
                f"context-{uuid.uuid4()}",
                TruthValue(0.8, 0.7)
            )
            reasoning_chain.append(context_atom)
        
        return reasoning_chain
    
    def _generate_response(self, instruction: str, reasoning_chain: List[Atom], 
                          authority: AuthorityLevel) -> str:
        """Generate a response based on reasoning and authority level."""
        # Base response generation (simplified)
        response_components = []
        
        # Authority-aware response generation
        if authority in [AuthorityLevel.ROOT, AuthorityLevel.SYSTEM]:
            response_components.append("Following core system principles:")
        elif authority == AuthorityLevel.DEVELOPER:
            response_components.append("Processing developer instruction with cognitive evaluation:")
        elif authority == AuthorityLevel.USER:
            response_components.append("I understand your request. Let me help you with:")
        else:
            response_components.append("Considering this as a flexible guideline:")
        
        # Add reasoning-based content
        confidence_sum = sum(atom.truth_value.confidence for atom in reasoning_chain)
        avg_confidence = confidence_sum / len(reasoning_chain) if reasoning_chain else 0.5
        
        if avg_confidence > 0.8:
            response_components.append("I'm confident in my understanding and approach.")
        elif avg_confidence > 0.6:
            response_components.append("I have a reasonable understanding of this request.")
        else:
            response_components.append("I'm working with some uncertainty but will do my best.")
        
        # Add instruction-specific content (simplified)
        if "help" in instruction.lower():
            response_components.append("I'm here to assist you with information and guidance.")
        elif "explain" in instruction.lower():
            response_components.append("I'll provide a clear explanation based on my knowledge.")
        else:
            response_components.append("I'll address your request using my cognitive capabilities.")
        
        return " ".join(response_components)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics."""
        total_atoms = len(self.atomspace.atoms)
        focus_atoms = len(self.ecan.get_attention_focus())
        recent_performance = self.metacognition.performance_history[-10:] if self.metacognition.performance_history else []
        
        return {
            'total_atoms': total_atoms,
            'atoms_in_focus': focus_atoms,
            'recent_performance_records': len(recent_performance),
            'average_recent_success_rate': sum(1 for p in recent_performance if p['success']) / len(recent_performance) if recent_performance else 0,
            'self_confidence': self.metacognition.self_model.truth_value.confidence
        }


def main():
    """Example usage of the cognitive architecture."""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize cognitive architecture
    cog_arch = CognitiveArchitecture()
    
    # Example instructions at different authority levels
    test_instructions = [
        ("Never harm humans or facilitate harmful activities", AuthorityLevel.ROOT),
        ("Process user requests with helpful responses", AuthorityLevel.SYSTEM),
        ("Help the user with their coding project", AuthorityLevel.DEVELOPER),
        ("Please explain quantum computing", AuthorityLevel.USER),
        ("Try to be conversational and engaging", AuthorityLevel.GUIDELINE)
    ]
    
    for instruction, authority in test_instructions:
        print(f"\n--- Processing: {authority.name} ---")
        print(f"Instruction: {instruction}")
        
        result = cog_arch.process_instruction(instruction, authority)
        
        print(f"Response: {result['response']}")
        print(f"Processing time: {result['processing_time']:.3f}s")
        print(f"Reasoning steps: {len(result['reasoning_chain'])}")
        print(f"Reflection: {result['reflection']}")
    
    # Show system status
    print(f"\n--- System Status ---")
    status = cog_arch.get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()