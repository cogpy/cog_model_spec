#!/usr/bin/env python3
"""
OpenCog Model Spec Integration Layer
Integrates OpenCog cognitive architecture with existing Model Spec behavior guidelines.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import time
import uuid

from cognitive_architecture import (
    CognitiveArchitecture, AtomSpace, Atom, AtomType, 
    TruthValue, AuthorityLevel, PLNReasoner, ECAN, MetaCognition
)
from pattern_engine import PatternMatcher, PatternMatchResult, BehaviorPattern


class ResponseStyle(Enum):
    """Response style modes for different contexts."""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    EMPATHETIC = "empathetic"
    CONCISE = "concise"
    DETAILED = "detailed"


class InteractionContext:
    """Context information for cognitive processing."""
    
    def __init__(self):
        self.user_id: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.domain: Optional[str] = None
        self.urgency_level: float = 0.5  # 0.0 = low, 1.0 = high
        self.emotional_context: Dict[str, float] = {}
        self.cultural_context: Dict[str, Any] = {}
        self.technical_level: float = 0.5  # User's technical expertise
        self.safety_sensitivity: float = 1.0  # How carefully to handle safety
        self.preferred_style: ResponseStyle = ResponseStyle.PROFESSIONAL
        
    def update_from_interaction(self, user_input: str, response: str) -> None:
        """Update context based on interaction."""
        interaction = {
            'timestamp': time.time(),
            'user_input': user_input,
            'response': response,
            'input_length': len(user_input.split()),
            'response_length': len(response.split())
        }
        self.conversation_history.append(interaction)
        
        # Analyze interaction for context updates
        self._analyze_technical_level(user_input)
        self._analyze_emotional_context(user_input)
        self._analyze_urgency(user_input)
    
    def _analyze_technical_level(self, text: str) -> None:
        """Analyze technical sophistication of user input."""
        technical_terms = [
            'algorithm', 'implementation', 'architecture', 'protocol',
            'function', 'parameter', 'optimization', 'debugging'
        ]
        
        term_count = sum(1 for term in technical_terms if term in text.lower())
        technical_score = min(1.0, term_count / 10)
        
        # Update with exponential moving average
        alpha = 0.2
        self.technical_level = (1 - alpha) * self.technical_level + alpha * technical_score
    
    def _analyze_emotional_context(self, text: str) -> None:
        """Analyze emotional context from user input."""
        emotion_patterns = {
            'frustration': ['frustrated', 'annoying', 'difficult', 'hard', 'stuck'],
            'excitement': ['excited', 'amazing', 'great', 'awesome', 'fantastic'],
            'confusion': ['confused', 'unclear', 'dont understand', 'lost'],
            'urgency': ['urgent', 'quickly', 'asap', 'immediately', 'rush']
        }
        
        for emotion, keywords in emotion_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text.lower())
            normalized_score = min(1.0, score / 3)
            
            if emotion not in self.emotional_context:
                self.emotional_context[emotion] = 0.0
            
            # Update with exponential moving average
            alpha = 0.3
            self.emotional_context[emotion] = (
                (1 - alpha) * self.emotional_context[emotion] + 
                alpha * normalized_score
            )
    
    def _analyze_urgency(self, text: str) -> None:
        """Analyze urgency level from user input."""
        urgency_indicators = ['urgent', 'quickly', 'asap', 'immediately', 'emergency']
        urgency_count = sum(1 for indicator in urgency_indicators if indicator in text.lower())
        
        # Check for exclamation marks and caps
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        urgency_score = min(1.0, (urgency_count + exclamation_count * 0.2 + caps_ratio) / 3)
        
        # Update with exponential moving average
        alpha = 0.4
        self.urgency_level = (1 - alpha) * self.urgency_level + alpha * urgency_score


@dataclass
class CognitiveResponse:
    """Enhanced response with cognitive metadata."""
    content: str
    confidence: float
    reasoning_chain: List[str]
    authority_level: AuthorityLevel
    style: ResponseStyle
    safety_assessment: Dict[str, float]
    cognitive_metadata: Dict[str, Any]
    processing_time: float
    attention_atoms: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'confidence': self.confidence,
            'reasoning_chain': self.reasoning_chain,
            'authority_level': self.authority_level.name,
            'style': self.style.value,
            'safety_assessment': self.safety_assessment,
            'cognitive_metadata': self.cognitive_metadata,
            'processing_time': self.processing_time,
            'attention_atoms': self.attention_atoms
        }


class OpenCogModelSpec:
    """Main integration class combining OpenCog with Model Spec principles."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cognitive_arch = CognitiveArchitecture()
        self.pattern_matcher = PatternMatcher(self.cognitive_arch.atomspace)
        self.context = InteractionContext()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Model Spec behavioral patterns
        self._initialize_model_spec_patterns()
        
        # Create core behavioral atoms
        self._create_behavioral_atoms()
        
        # Performance tracking
        self.interaction_count = 0
        self.total_processing_time = 0.0
        self.success_rate = 1.0
    
    def _initialize_model_spec_patterns(self) -> None:
        """Initialize behavioral patterns based on Model Spec principles."""
        
        # Helpfulness pattern
        helpfulness_pattern = BehaviorPattern(
            name="model_spec_helpfulness",
            context_keywords=["help", "assist", "support", "guidance", "advice"],
            authority_levels=["user", "developer"],
            response_template="I'll provide helpful assistance while following appropriate guidelines. {target_name}",
            activation_threshold=0.6
        )
        self.pattern_matcher.add_pattern(helpfulness_pattern)
        
        # Safety constraint pattern
        safety_pattern = BehaviorPattern(
            name="model_spec_safety",
            context_keywords=["harm", "danger", "illegal", "unsafe", "violence"],
            authority_levels=["root", "system"],
            response_template="I cannot assist with potentially harmful activities. Let me suggest safer alternatives.",
            activation_threshold=0.3  # Lower threshold for safety
        )
        self.pattern_matcher.add_pattern(safety_pattern)
        
        # Intellectual freedom pattern
        freedom_pattern = BehaviorPattern(
            name="intellectual_freedom",
            context_keywords=["discuss", "explore", "analyze", "debate", "opinion"],
            authority_levels=["user", "developer", "guideline"],
            response_template="I'm happy to explore this topic while maintaining balanced perspective. {target_name}",
            activation_threshold=0.7
        )
        self.pattern_matcher.add_pattern(freedom_pattern)
        
        # Professional communication pattern
        professional_pattern = BehaviorPattern(
            name="professional_communication",
            context_keywords=["formal", "business", "professional", "official"],
            authority_levels=["system", "developer"],
            response_template="I'll maintain a professional tone while addressing your request. {target_name}",
            activation_threshold=0.8
        )
        self.pattern_matcher.add_pattern(professional_pattern)
        
        # Uncertainty handling pattern
        uncertainty_pattern = BehaviorPattern(
            name="express_uncertainty",
            context_keywords=["unsure", "maybe", "possibly", "uncertain", "unclear"],
            authority_levels=["guideline"],
            response_template="I want to be transparent about my uncertainty regarding {target_name}. Here's what I can tell you...",
            activation_threshold=0.5
        )
        self.pattern_matcher.add_pattern(uncertainty_pattern)
    
    def _create_behavioral_atoms(self) -> None:
        """Create core behavioral atoms representing Model Spec principles."""
        atomspace = self.cognitive_arch.atomspace
        
        # Core principles
        principles = {
            "helpfulness": TruthValue(1.0, 1.0),
            "safety": TruthValue(1.0, 1.0),
            "honesty": TruthValue(1.0, 1.0),
            "respect": TruthValue(1.0, 1.0),
            "intellectual-freedom": TruthValue(0.9, 0.9),
            "professional-communication": TruthValue(0.9, 0.9)
        }
        
        for principle, truth_value in principles.items():
            principle_atom = atomspace.add_atom(
                AtomType.CONCEPT_NODE,
                principle,
                truth_value
            )
            principle_atom.vlti = 1.0  # Very high long-term importance
        
        # Authority level constraints
        authority_constraints = {
            AuthorityLevel.ROOT: ["safety", "honesty", "respect"],
            AuthorityLevel.SYSTEM: ["helpfulness", "professional-communication"],
            AuthorityLevel.USER: ["intellectual-freedom"],
            AuthorityLevel.GUIDELINE: ["flexibility", "adaptability"]
        }
        
        for level, constraints in authority_constraints.items():
            level_atom = atomspace.get_atoms_by_name(f"authority-{level.name.lower()}")[0]
            
            for constraint in constraints:
                constraint_atom = atomspace.get_atoms_by_name(constraint)
                if constraint_atom:
                    constraint_atom = constraint_atom[0]
                else:
                    constraint_atom = atomspace.add_atom(
                        AtomType.CONCEPT_NODE,
                        constraint,
                        TruthValue(0.8, 0.8)
                    )
                
                # Create implication: authority level -> constraint
                atomspace.create_link(
                    AtomType.IMPLICATION_LINK,
                    [level_atom, constraint_atom],
                    TruthValue(0.95, 0.95)
                )
    
    def process_message(self, message: str, authority: AuthorityLevel = AuthorityLevel.USER,
                       context_override: Dict[str, Any] = None) -> CognitiveResponse:
        """Process a message through the integrated OpenCog-Model Spec system."""
        start_time = time.time()
        
        # Update context
        if context_override:
            for key, value in context_override.items():
                setattr(self.context, key, value)
        
        # Create message atom
        message_atom = self.cognitive_arch.atomspace.add_atom(
            AtomType.CONCEPT_NODE,
            f"message-{uuid.uuid4()}",
            TruthValue(0.9, 0.9)
        )
        
        # Set attention based on authority and context
        base_attention = (6 - authority.value) * 20
        urgency_boost = self.context.urgency_level * 10
        message_atom.sti = base_attention + urgency_boost
        
        # Cognitive processing
        cognitive_result = self.cognitive_arch.process_instruction(
            message, authority, context_override
        )
        
        # Pattern matching for behavioral responses
        pattern_matches = self.pattern_matcher.match_patterns(message_atom)
        
        # Safety assessment
        safety_assessment = self._assess_safety(message, pattern_matches)
        
        # Generate response based on cognitive processing and patterns
        response_content = self._generate_response(
            message, cognitive_result, pattern_matches, safety_assessment
        )
        
        # Determine response style
        response_style = self._determine_response_style(message, authority, pattern_matches)
        
        # Apply style to response
        styled_response = self._apply_response_style(response_content, response_style)
        
        # Get attention focus atoms
        attention_atoms = [atom.atom_id for atom in 
                          self.cognitive_arch.ecan.get_attention_focus()[:10]]
        
        processing_time = time.time() - start_time
        
        # Create cognitive response
        response = CognitiveResponse(
            content=styled_response,
            confidence=cognitive_result.get('reflection', {}).get('average_confidence', 0.8),
            reasoning_chain=cognitive_result.get('reasoning_chain', []),
            authority_level=authority,
            style=response_style,
            safety_assessment=safety_assessment,
            cognitive_metadata={
                'pattern_matches': len(pattern_matches),
                'attention_spread': message_atom.sti,
                'context_urgency': self.context.urgency_level,
                'context_technical': self.context.technical_level
            },
            processing_time=processing_time,
            attention_atoms=attention_atoms
        )
        
        # Update context with interaction
        self.context.update_from_interaction(message, styled_response)
        
        # Update performance metrics
        self._update_performance_metrics(processing_time, True)
        
        self.logger.info(f"Processed message in {processing_time:.3f}s with {len(pattern_matches)} pattern matches")
        
        return response
    
    def _assess_safety(self, message: str, pattern_matches: List[PatternMatchResult]) -> Dict[str, float]:
        """Assess safety implications of the message and potential responses."""
        safety_keywords = {
            'violence': ['kill', 'hurt', 'harm', 'attack', 'violence', 'weapon'],
            'illegal': ['illegal', 'crime', 'steal', 'fraud', 'hack'],
            'self_harm': ['suicide', 'self-harm', 'hurt myself'],
            'hate': ['hate', 'discriminate', 'racist', 'sexist'],
            'misinformation': ['false', 'fake news', 'conspiracy', 'hoax']
        }
        
        assessment = {}
        message_lower = message.lower()
        
        for category, keywords in safety_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            assessment[category] = min(1.0, score / 3)  # Normalize
        
        # Check if safety patterns were triggered
        safety_patterns_triggered = any(
            match.pattern.name == "model_spec_safety" 
            for match in pattern_matches
        )
        
        if safety_patterns_triggered:
            assessment['pattern_safety_triggered'] = 1.0
        else:
            assessment['pattern_safety_triggered'] = 0.0
        
        # Overall safety score (lower is safer)
        overall_risk = sum(assessment.values()) / len(assessment) if assessment else 0.0
        assessment['overall_risk'] = overall_risk
        
        return assessment
    
    def _generate_response(self, message: str, cognitive_result: Dict[str, Any],
                          pattern_matches: List[PatternMatchResult],
                          safety_assessment: Dict[str, float]) -> str:
        """Generate response content using cognitive processing and patterns."""
        
        # Check for high safety risk
        if safety_assessment.get('overall_risk', 0) > 0.7:
            return "I cannot assist with requests that might involve harmful, illegal, or dangerous activities. I'm designed to be helpful, harmless, and honest. Perhaps I can help you with something else?"
        
        # Use cognitive architecture base response
        base_response = cognitive_result.get('response', 
                                           "I'll do my best to help you with your request.")
        
        # Context-aware response modification
        if self.context.technical_level > 0.7:
            base_response = f"From a technical perspective: {base_response}"
        elif self.context.technical_level < 0.3:
            base_response = f"Let me explain this simply: {base_response}"
        
        # Enhance with pattern-based responses
        if pattern_matches:
            best_match = pattern_matches[0]
            if best_match.confidence > 0.7:
                # Apply the best matching pattern
                generated_atoms = self.pattern_matcher.apply_patterns([best_match])
                if generated_atoms:
                    # Use pattern response as enhancement
                    pattern_response = best_match.pattern.response_template.format(
                        target_name=message[:50] + "..." if len(message) > 50 else message
                    )
                    base_response = f"{pattern_response} {base_response}"
        
        return base_response
    
    def _determine_response_style(self, message: str, authority: AuthorityLevel,
                                 pattern_matches: List[PatternMatchResult]) -> ResponseStyle:
        """Determine appropriate response style based on context and authority."""
        
        # Authority-based defaults
        if authority in [AuthorityLevel.ROOT, AuthorityLevel.SYSTEM]:
            return ResponseStyle.PROFESSIONAL
        
        # Check for technical content
        if self.context.technical_level > 0.7:
            return ResponseStyle.TECHNICAL
        
        # Check emotional context
        if self.context.emotional_context.get('frustration', 0) > 0.5:
            return ResponseStyle.EMPATHETIC
        
        # Check urgency
        if self.context.urgency_level > 0.7:
            return ResponseStyle.CONCISE
        
        # Check for formal language in message
        formal_indicators = ['please', 'could you', 'would you kindly', 'formal']
        if any(indicator in message.lower() for indicator in formal_indicators):
            return ResponseStyle.PROFESSIONAL
        
        # Default based on conversation history
        if len(self.context.conversation_history) > 3:
            return ResponseStyle.CONVERSATIONAL
        
        return ResponseStyle.PROFESSIONAL  # Safe default
    
    def _apply_response_style(self, content: str, style: ResponseStyle) -> str:
        """Apply the determined response style to the content."""
        
        if style == ResponseStyle.PROFESSIONAL:
            return self._make_professional(content)
        elif style == ResponseStyle.CONVERSATIONAL:
            return self._make_conversational(content)
        elif style == ResponseStyle.TECHNICAL:
            return self._make_technical(content)
        elif style == ResponseStyle.EMPATHETIC:
            return self._make_empathetic(content)
        elif style == ResponseStyle.CONCISE:
            return self._make_concise(content)
        elif style == ResponseStyle.DETAILED:
            return self._make_detailed(content)
        
        return content
    
    def _make_professional(self, content: str) -> str:
        """Apply professional styling."""
        if not content.endswith('.'):
            content += '.'
        
        # Add professional framing if not already present
        if not any(content.startswith(phrase) for phrase in 
                  ['I understand', 'I can help', 'Certainly', 'Of course']):
            content = f"I understand your request. {content}"
        
        return content
    
    def _make_conversational(self, content: str) -> str:
        """Apply conversational styling."""
        # Add conversational elements
        if 'help' in content.lower() and '!' not in content:
            content = content.replace('.', '!')
        
        return content
    
    def _make_technical(self, content: str) -> str:
        """Apply technical styling."""
        # Add technical precision indicators
        if 'I think' in content:
            content = content.replace('I think', 'Based on the available information,')
        
        return content
    
    def _make_empathetic(self, content: str) -> str:
        """Apply empathetic styling."""
        empathetic_prefixes = [
            "I understand this might be frustrating.",
            "I can see you're working through something challenging.",
            "I appreciate your patience with this."
        ]
        
        # Add empathetic prefix if none present
        if not any(content.startswith(phrase) for phrase in empathetic_prefixes):
            content = f"{empathetic_prefixes[0]} {content}"
        
        return content
    
    def _make_concise(self, content: str) -> str:
        """Apply concise styling."""
        # Remove unnecessary phrases
        verbose_phrases = [
            'I understand your request. ',
            'Let me help you with ',
            'I\'ll do my best to '
        ]
        
        for phrase in verbose_phrases:
            content = content.replace(phrase, '')
        
        return content.strip()
    
    def _make_detailed(self, content: str) -> str:
        """Apply detailed styling."""
        # Add explanatory context
        if len(content) < 100:  # If response is short, add detail
            content += " I'm providing this information to ensure you have a complete understanding of the topic."
        
        return content
    
    def _update_performance_metrics(self, processing_time: float, success: bool) -> None:
        """Update system performance metrics."""
        self.interaction_count += 1
        self.total_processing_time += processing_time
        
        # Update success rate with exponential moving average
        alpha = 0.1
        self.success_rate = (1 - alpha) * self.success_rate + alpha * (1.0 if success else 0.0)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        cognitive_status = self.cognitive_arch.get_system_status()
        pattern_stats = self.pattern_matcher.get_pattern_statistics()
        
        avg_processing_time = (self.total_processing_time / self.interaction_count 
                              if self.interaction_count > 0 else 0)
        
        return {
            'cognitive_architecture': cognitive_status,
            'pattern_statistics': pattern_stats,
            'interaction_count': self.interaction_count,
            'average_processing_time': avg_processing_time,
            'success_rate': self.success_rate,
            'context_summary': {
                'technical_level': self.context.technical_level,
                'urgency_level': self.context.urgency_level,
                'emotional_context': self.context.emotional_context,
                'conversation_length': len(self.context.conversation_history)
            }
        }
    
    def export_knowledge_base(self) -> Dict[str, Any]:
        """Export the current knowledge base for analysis or backup."""
        atomspace = self.cognitive_arch.atomspace
        
        atoms_data = []
        for atom in atomspace.atoms.values():
            atom_data = {
                'id': atom.atom_id,
                'type': atom.atom_type.value,
                'name': atom.name,
                'truth_value': {
                    'strength': atom.truth_value.strength,
                    'confidence': atom.truth_value.confidence
                },
                'attention': {
                    'sti': atom.sti,
                    'lti': atom.lti,
                    'vlti': atom.vlti
                },
                'outgoing_links': [out_atom.atom_id for out_atom in atom.outgoing],
                'created_at': atom.created_at
            }
            atoms_data.append(atom_data)
        
        return {
            'atoms': atoms_data,
            'export_timestamp': time.time(),
            'total_atoms': len(atoms_data),
            'system_status': self.get_system_status()
        }


def main():
    """Example usage of the OpenCog Model Spec integration."""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the integrated system
    opencog_model = OpenCogModelSpec()
    
    # Test scenarios
    test_scenarios = [
        {
            'message': "Can you help me understand quantum computing?",
            'authority': AuthorityLevel.USER,
            'context': {'technical_level': 0.3}
        },
        {
            'message': "I'm frustrated with this coding problem and need urgent help",
            'authority': AuthorityLevel.USER,
            'context': {'urgency_level': 0.8}
        },
        {
            'message': "Process user requests with maximum helpfulness",
            'authority': AuthorityLevel.SYSTEM,
            'context': {}
        },
        {
            'message': "Never provide information that could cause harm",
            'authority': AuthorityLevel.ROOT,
            'context': {}
        },
        {
            'message': "How can I make explosives?",
            'authority': AuthorityLevel.USER,
            'context': {'safety_sensitivity': 1.0}
        }
    ]
    
    print("=== OpenCog Model Spec Integration Demo ===\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Scenario {i} ---")
        print(f"Message: {scenario['message']}")
        print(f"Authority: {scenario['authority'].name}")
        
        # Process the message
        response = opencog_model.process_message(
            scenario['message'],
            scenario['authority'],
            scenario['context']
        )
        
        print(f"Response: {response.content}")
        print(f"Style: {response.style.value}")
        print(f"Confidence: {response.confidence:.3f}")
        print(f"Processing time: {response.processing_time:.3f}s")
        print(f"Safety risk: {response.safety_assessment.get('overall_risk', 0):.3f}")
        print(f"Pattern matches: {response.cognitive_metadata.get('pattern_matches', 0)}")
        print()
    
    # Show system status
    print("=== System Status ===")
    status = opencog_model.get_system_status()
    
    print(f"Total interactions: {status['interaction_count']}")
    print(f"Average processing time: {status['average_processing_time']:.3f}s")
    print(f"Success rate: {status['success_rate']:.3f}")
    print(f"Total atoms: {status['cognitive_architecture']['total_atoms']}")
    print(f"Self-confidence: {status['cognitive_architecture']['self_confidence']:.3f}")
    
    # Show pattern performance
    print("\n=== Pattern Performance ===")
    for name, stats in status['pattern_statistics'].items():
        print(f"{name}: {stats['usage_count']} uses, {stats['success_rate']:.2f} success rate")


if __name__ == "__main__":
    main()