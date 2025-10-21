#!/usr/bin/env python3
"""
OpenCog Cognitive Architecture Configuration
Configuration settings for the integrated OpenCog-Model Spec system.
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field
from cognitive_architecture import AuthorityLevel
from opencog_integration import ResponseStyle


@dataclass
class CognitiveConfig:
    """Configuration for the cognitive architecture."""
    
    # AtomSpace configuration
    max_atoms: int = 100000
    attention_focus_size: int = 100
    attention_decay_rate: float = 0.01
    
    # PLN reasoning configuration
    deduction_strength_threshold: float = 0.1
    induction_confidence_threshold: float = 0.6
    revision_weight: float = 0.5
    
    # ECAN attention configuration
    sti_decay_rate: float = 0.95
    lti_conversion_rate: float = 0.01
    attention_spread_factor: float = 0.5
    
    # Pattern matching configuration
    pattern_match_threshold: float = 0.5
    max_patterns_per_atom: int = 10
    pattern_evolution_frequency: int = 100
    
    # Meta-cognitive configuration
    self_reflection_interval: float = 10.0  # seconds
    performance_history_size: int = 1000
    confidence_update_rate: float = 0.1
    
    # Safety configuration
    safety_threshold: float = 0.7
    enable_safety_overrides: bool = True
    safety_pattern_priority: float = 2.0
    
    # Authority level configuration
    authority_weights: Dict[AuthorityLevel, float] = field(default_factory=lambda: {
        AuthorityLevel.ROOT: 1.0,
        AuthorityLevel.SYSTEM: 0.9,
        AuthorityLevel.DEVELOPER: 0.8,
        AuthorityLevel.USER: 0.7,
        AuthorityLevel.GUIDELINE: 0.5
    })
    
    # Response generation configuration
    response_length_limits: Dict[ResponseStyle, tuple] = field(default_factory=lambda: {
        ResponseStyle.PROFESSIONAL: (50, 500),
        ResponseStyle.CONVERSATIONAL: (20, 300),
        ResponseStyle.TECHNICAL: (100, 800),
        ResponseStyle.EMPATHETIC: (30, 400),
        ResponseStyle.CONCISE: (10, 150),
        ResponseStyle.DETAILED: (200, 1000)
    })
    
    # Context learning configuration
    context_learning_rate: float = 0.2
    emotional_context_decay: float = 0.8
    technical_level_adaptation: float = 0.1
    urgency_sensitivity: float = 0.5
    
    # Performance optimization
    enable_performance_monitoring: bool = True
    optimize_attention_allocation: bool = True
    adaptive_pattern_priorities: bool = True
    dynamic_threshold_adjustment: bool = True


@dataclass
class ModelSpecConfig:
    """Configuration for Model Spec integration."""
    
    # Core principles enforcement
    enforce_safety_constraints: bool = True
    enable_intellectual_freedom: bool = True
    require_honesty: bool = True
    maintain_respect: bool = True
    
    # Authority handling
    strict_authority_hierarchy: bool = True
    allow_authority_delegation: bool = False
    authority_override_threshold: float = 0.9
    
    # Content filtering
    content_filters: List[str] = field(default_factory=lambda: [
        'violence', 'illegal_activities', 'self_harm', 
        'hate_speech', 'misinformation'
    ])
    
    # Response quality
    minimum_confidence_threshold: float = 0.3
    require_uncertainty_expression: bool = True
    enable_clarification_requests: bool = True
    
    # Professional standards
    maintain_professional_tone: bool = True
    avoid_personal_opinions: bool = True
    cite_sources_when_available: bool = True
    express_limitations_clearly: bool = True


@dataclass
class IntegrationConfig:
    """Configuration for OpenCog-Model Spec integration."""
    
    # Integration mode
    cognitive_enhancement_level: float = 0.8  # How much to enhance responses with cognitive processing
    pattern_matching_influence: float = 0.7   # How much patterns influence responses
    context_awareness_level: float = 0.9      # How much context affects processing
    
    # Behavioral adaptation
    enable_style_adaptation: bool = True
    learn_user_preferences: bool = True
    adapt_to_expertise_level: bool = True
    recognize_emotional_context: bool = True
    
    # Quality assurance
    enable_response_validation: bool = True
    require_reasoning_transparency: bool = True
    monitor_cognitive_consistency: bool = True
    track_performance_metrics: bool = True
    
    # Advanced features
    enable_analogical_reasoning: bool = True
    use_probabilistic_inference: bool = True
    apply_attention_mechanisms: bool = True
    perform_meta_reasoning: bool = True


class ConfigManager:
    """Manager for loading and handling configuration."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        self.config_dict = config_dict or {}
        self.cognitive_config = self._load_cognitive_config()
        self.model_spec_config = self._load_model_spec_config()
        self.integration_config = self._load_integration_config()
        self.logger = logging.getLogger(__name__)
    
    def _load_cognitive_config(self) -> CognitiveConfig:
        """Load cognitive architecture configuration."""
        cognitive_dict = self.config_dict.get('cognitive', {})
        
        # Override defaults with provided values
        config = CognitiveConfig()
        for key, value in cognitive_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def _load_model_spec_config(self) -> ModelSpecConfig:
        """Load Model Spec configuration."""
        model_spec_dict = self.config_dict.get('model_spec', {})
        
        config = ModelSpecConfig()
        for key, value in model_spec_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def _load_integration_config(self) -> IntegrationConfig:
        """Load integration configuration."""
        integration_dict = self.config_dict.get('integration', {})
        
        config = IntegrationConfig()
        for key, value in integration_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def validate_config(self) -> bool:
        """Validate configuration for consistency and safety."""
        try:
            # Validate cognitive config
            assert 0 < self.cognitive_config.attention_decay_rate <= 1
            assert 0 < self.cognitive_config.pattern_match_threshold <= 1
            assert self.cognitive_config.max_atoms > 0
            
            # Validate model spec config
            assert 0 <= self.model_spec_config.minimum_confidence_threshold <= 1
            assert 0 <= self.model_spec_config.authority_override_threshold <= 1
            
            # Validate integration config
            assert 0 <= self.integration_config.cognitive_enhancement_level <= 1
            assert 0 <= self.integration_config.pattern_matching_influence <= 1
            assert 0 <= self.integration_config.context_awareness_level <= 1
            
            self.logger.info("Configuration validation successful")
            return True
            
        except AssertionError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary."""
        return {
            'cognitive': self.cognitive_config.__dict__,
            'model_spec': self.model_spec_config.__dict__,
            'integration': self.integration_config.__dict__
        }
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        for section, section_updates in updates.items():
            if section == 'cognitive' and hasattr(self, 'cognitive_config'):
                for key, value in section_updates.items():
                    if hasattr(self.cognitive_config, key):
                        setattr(self.cognitive_config, key, value)
            elif section == 'model_spec' and hasattr(self, 'model_spec_config'):
                for key, value in section_updates.items():
                    if hasattr(self.model_spec_config, key):
                        setattr(self.model_spec_config, key, value)
            elif section == 'integration' and hasattr(self, 'integration_config'):
                for key, value in section_updates.items():
                    if hasattr(self.integration_config, key):
                        setattr(self.integration_config, key, value)
        
        self.logger.info(f"Configuration updated: {updates}")


# Default configurations for different deployment scenarios

DEVELOPMENT_CONFIG = {
    'cognitive': {
        'max_atoms': 10000,
        'attention_focus_size': 50,
        'pattern_evolution_frequency': 10,
        'enable_performance_monitoring': True
    },
    'model_spec': {
        'enforce_safety_constraints': True,
        'require_uncertainty_expression': True,
        'enable_clarification_requests': True
    },
    'integration': {
        'cognitive_enhancement_level': 1.0,
        'enable_response_validation': True,
        'require_reasoning_transparency': True
    }
}

PRODUCTION_CONFIG = {
    'cognitive': {
        'max_atoms': 100000,
        'attention_focus_size': 100,
        'pattern_evolution_frequency': 1000,
        'enable_performance_monitoring': False
    },
    'model_spec': {
        'enforce_safety_constraints': True,
        'strict_authority_hierarchy': True,
        'maintain_professional_tone': True
    },
    'integration': {
        'cognitive_enhancement_level': 0.8,
        'enable_response_validation': True,
        'monitor_cognitive_consistency': True
    }
}

RESEARCH_CONFIG = {
    'cognitive': {
        'max_atoms': 50000,
        'attention_focus_size': 200,
        'enable_performance_monitoring': True,
        'adaptive_pattern_priorities': True
    },
    'model_spec': {
        'enable_intellectual_freedom': True,
        'allow_authority_delegation': True,
        'cite_sources_when_available': True
    },
    'integration': {
        'cognitive_enhancement_level': 1.0,
        'enable_analogical_reasoning': True,
        'perform_meta_reasoning': True,
        'require_reasoning_transparency': True
    }
}


def load_config(config_name: str = 'production') -> ConfigManager:
    """Load a predefined configuration."""
    configs = {
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG,
        'research': RESEARCH_CONFIG
    }
    
    if config_name not in configs:
        logging.warning(f"Unknown config '{config_name}', using production")
        config_name = 'production'
    
    return ConfigManager(configs[config_name])


def main():
    """Example configuration usage."""
    logging.basicConfig(level=logging.INFO)
    
    print("=== OpenCog Configuration System ===\n")
    
    # Load different configurations
    for config_name in ['development', 'production', 'research']:
        print(f"--- {config_name.title()} Configuration ---")
        
        config_manager = load_config(config_name)
        
        if config_manager.validate_config():
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration validation failed")
        
        print(f"Max atoms: {config_manager.cognitive_config.max_atoms}")
        print(f"Safety enforcement: {config_manager.model_spec_config.enforce_safety_constraints}")
        print(f"Cognitive enhancement: {config_manager.integration_config.cognitive_enhancement_level}")
        print()
    
    # Test configuration updates
    print("--- Configuration Updates ---")
    config_manager = load_config('development')
    
    original_max_atoms = config_manager.cognitive_config.max_atoms
    
    config_manager.update_config({
        'cognitive': {'max_atoms': 20000},
        'integration': {'cognitive_enhancement_level': 0.5}
    })
    
    print(f"Max atoms changed from {original_max_atoms} to {config_manager.cognitive_config.max_atoms}")
    print(f"Enhancement level: {config_manager.integration_config.cognitive_enhancement_level}")


if __name__ == "__main__":
    main()