# -*- coding: utf-8 -*-
# app/lateral.py
# Lateral Thinking Module for MCP Server - Edward de Bono's Creative Problem Solving

"""
Lateral Thinking (Tư duy ngang) - Edward de Bono's Creative Problem Solving Method

Lateral Thinking là phương pháp giải quyết vấn đề bằng cách tiếp cận phi tuyến tính, 
phi logic truyền thống, nhằm tạo ra những đột phá ý tưởng và giải pháp sáng tạo.

Đặc điểm:
- Không đi theo con đường hiển nhiên
- Phá vỡ mô thức (pattern breaking)  
- Sử dụng sự gián đoạn (disruption)
- Tạo kết nối bất ngờ

Techniques:
- random_word: Sử dụng từ ngẫu nhiên để tạo kết nối mới
- provocation: Tạo tuyên bố phi lý để kích thích ý tưởng mới
- alternative: Tạo ra nhiều phương án thay thế
- reversal: Đảo ngược vấn đề hoặc giả định
- metaphor: Sử dụng ẩn dụ và so sánh để có góc nhìn mới
- assumption_challenge: Thách thức các giả định cơ bản
"""

import json
import random
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Literal
from app.logger import get_logger

logger = get_logger(__name__)

# Type definitions for lateral thinking techniques
LateralTechnique = Literal[
    "random_word", 
    "provocation", 
    "alternative", 
    "reversal", 
    "metaphor", 
    "assumption_challenge"
]


class LateralThoughtData:
    """Data structure for lateral thinking results"""
    
    def __init__(self, 
                 technique: LateralTechnique,
                 stimulus: str,
                 connection: str,
                 idea: str,
                 evaluation: str,
                 next_technique_needed: bool):
        self.technique = technique
        self.stimulus = stimulus
        self.connection = connection
        self.idea = idea
        self.evaluation = evaluation
        self.next_technique_needed = next_technique_needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "technique": self.technique,
            "stimulus": self.stimulus,
            "connection": self.connection,
            "idea": self.idea,
            "evaluation": self.evaluation,
            "next_technique_needed": self.next_technique_needed
        }


class LateralThinkingProcessor:
    """Processor for lateral thinking analysis"""
    
    def __init__(self):
        self.techniques_used: List[str] = []
        self.ideas: List[LateralThoughtData] = []
        self.session_counter = 0
        
        # Random words pool for random_word technique
        self.random_words = [
            "ocean", "butterfly", "telescope", "rainbow", "volcano", "symphony", "diamond",
            "tornado", "galaxy", "waterfall", "clockwork", "labyrinth", "phoenix", "quantum",
            "kaleidoscope", "thunderstorm", "prism", "ecosystem", "constellation", "avalanche",
            "metamorphosis", "sanctuary", "resonance", "expedition", "crystalline", "oasis",
            "nebula", "cascade", "meridian", "aurora", "catalyst", "mosaic", "vortex", "zenith"
        ]
    
    def _validate_lateral_data(self, data: Dict[str, Any]) -> LateralThoughtData:
        """Validate and create LateralThoughtData from input data"""
        
        # Validate technique
        technique = data.get("technique")
        valid_techniques = ["random_word", "provocation", "alternative", "reversal", "metaphor", "assumption_challenge"]
        if not technique or technique not in valid_techniques:
            raise ValueError(f"Invalid technique: must be one of {valid_techniques}")
        
        # Validate stimulus
        stimulus = data.get("stimulus")
        if not stimulus or not isinstance(stimulus, str):
            raise ValueError("Invalid stimulus: must be a non-empty string")
        
        # Validate connection
        connection = data.get("connection")
        if not connection or not isinstance(connection, str):
            raise ValueError("Invalid connection: must be a non-empty string")
        
        # Validate idea
        idea = data.get("idea")
        if not idea or not isinstance(idea, str):
            raise ValueError("Invalid idea: must be a non-empty string")
        
        # Validate evaluation
        evaluation = data.get("evaluation")
        if not evaluation or not isinstance(evaluation, str):
            raise ValueError("Invalid evaluation: must be a non-empty string")
        
        # Validate next_technique_needed
        next_technique_needed = data.get("next_technique_needed")
        if not isinstance(next_technique_needed, bool):
            raise ValueError("Invalid next_technique_needed: must be a boolean")
        
        return LateralThoughtData(
            technique=technique,
            stimulus=stimulus,
            connection=connection,
            idea=idea,
            evaluation=evaluation,
            next_technique_needed=next_technique_needed
        )
    
    def _get_technique_emoji(self, technique: str) -> str:
        """Get emoji for technique type"""
        technique_emojis = {
            'random_word': '🎲',
            'provocation': '🚀',
            'alternative': '🔄',
            'reversal': '↩️',
            'metaphor': '🎭',
            'assumption_challenge': '❓'
        }
        return technique_emojis.get(technique, '💡')
    
    def _format_lateral_thought(self, thought: LateralThoughtData) -> str:
        """Format lateral thinking analysis for display"""
        
        emoji = self._get_technique_emoji(thought.technique)
        technique_name = thought.technique.replace('_', ' ').title()
        
        formatted_output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      {emoji} LATERAL THINKING: {technique_name.upper()}                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TECHNIQUE: {thought.technique}
║ 
║ STIMULUS: {thought.stimulus[:70]}{'...' if len(thought.stimulus) > 70 else ''}
║ 
║ CONNECTION: {thought.connection[:65]}{'...' if len(thought.connection) > 65 else ''}
║ 
║ CREATIVE IDEA: {thought.idea[:62]}{'...' if len(thought.idea) > 62 else ''}
║ 
║ EVALUATION: {thought.evaluation[:65]}{'...' if len(thought.evaluation) > 65 else ''}
║ 
║ NEXT TECHNIQUE NEEDED: {"YES" if thought.next_technique_needed else "NO"}
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return formatted_output
    
    def _generate_technique_guidance(self, technique: str) -> str:
        """Generate guidance for specific lateral thinking technique"""
        
        guidance = {
            "random_word": "Use a random word to break thinking patterns and create unexpected connections to your problem.",
            "provocation": "Create deliberately unreasonable or impossible statements, then explore how they might lead to practical solutions.",
            "alternative": "Generate multiple different approaches to the same problem, avoiding the first obvious solution.",
            "reversal": "Reverse the problem, assumptions, or desired outcome to gain new perspectives.",
            "metaphor": "Use analogies, metaphors, or comparisons from completely different domains.",
            "assumption_challenge": "Question and challenge every assumption underlying the problem or current approach."
        }
        
        return guidance.get(technique, "Apply creative thinking to break conventional patterns.")
    
    def _suggest_random_stimulus(self, technique: str) -> str:
        """Suggest random stimulus based on technique"""
        
        if technique == "random_word":
            return random.choice(self.random_words)
        elif technique == "provocation":
            provocations = [
                "What if gravity worked backwards?",
                "What if time moved sideways?",
                "What if money grew on trees?",
                "What if everyone could read minds?",
                "What if buildings could walk?"
            ]
            return random.choice(provocations)
        elif technique == "reversal":
            return "Consider the opposite of what you normally would do"
        elif technique == "metaphor":
            metaphors = [
                "like a symphony orchestra",
                "like a flowing river", 
                "like a growing garden",
                "like a complex recipe",
                "like a dance performance"
            ]
            return random.choice(metaphors)
        else:
            return "Challenge the fundamental assumptions"
    
    async def process_lateral_thinking(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process lateral thinking analysis"""
        
        try:
            # Validate input data
            validated_thought = self._validate_lateral_data(input_data)
            
            # Store thought
            self.ideas.append(validated_thought)
            self.techniques_used.append(validated_thought.technique)
            self.session_counter += 1
            
            # Format thought for logging
            formatted_thought = self._format_lateral_thought(validated_thought)
            logger.info(f"Lateral Thinking #{self.session_counter}:\n{formatted_thought}")
            
            # Create session ID
            session_id = f"lateral_{int(datetime.now(timezone.utc).timestamp())}"
            
            # Generate technique guidance
            technique_guidance = self._generate_technique_guidance(validated_thought.technique)
            
            # Suggest next technique if needed
            next_technique_suggestion = None
            next_stimulus = None
            if validated_thought.next_technique_needed:
                used_techniques = set(self.techniques_used)
                all_techniques = {"random_word", "provocation", "alternative", "reversal", "metaphor", "assumption_challenge"}
                unused_techniques = list(all_techniques - used_techniques)
                if unused_techniques:
                    next_technique_suggestion = random.choice(unused_techniques)
                    next_stimulus = self._suggest_random_stimulus(next_technique_suggestion)
                else:
                    next_technique_suggestion = random.choice(list(all_techniques))
                    next_stimulus = self._suggest_random_stimulus(next_technique_suggestion)
            
            # Prepare result
            result = {
                "session_id": session_id,
                "thought_number": self.session_counter,
                "thought_data": validated_thought.to_dict(),
                "technique_info": {
                    "technique": validated_thought.technique,
                    "emoji": self._get_technique_emoji(validated_thought.technique),
                    "guidance": technique_guidance,
                    "creativity_score": self._assess_creativity_score(validated_thought)
                },
                "session_summary": {
                    "total_ideas": len(self.ideas),
                    "techniques_used": list(set(self.techniques_used)),
                    "techniques_count": len(set(self.techniques_used)),
                    "pattern_breaking_score": self._calculate_pattern_breaking_score()
                },
                "next_technique": {
                    "suggested": next_technique_suggestion,
                    "stimulus": next_stimulus if next_technique_suggestion else None,
                    "needed": validated_thought.next_technique_needed
                } if validated_thought.next_technique_needed else None,
                "formatted_display": formatted_thought,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_thoughts": len(self.ideas),
                    "thinking_type": "lateral_thinking",
                    "version": "1.0.0"
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in lateral thinking analysis: {e}")
            raise ValueError(f"Lateral thinking analysis failed: {str(e)}")
    
    def _assess_creativity_score(self, thought: LateralThoughtData) -> int:
        """Assess creativity score (1-10) based on thought characteristics"""
        score = 5  # Base score
        
        # Check for unexpected connections
        if "unusual" in thought.connection.lower() or "unexpected" in thought.connection.lower():
            score += 2
        
        # Check for breakthrough potential
        if any(word in thought.evaluation.lower() for word in ["breakthrough", "innovative", "revolutionary", "disruptive"]):
            score += 2
        
        # Check for challenge to assumptions
        if "assumption" in thought.connection.lower() or "challenge" in thought.idea.lower():
            score += 1
        
        return min(score, 10)
    
    def _calculate_pattern_breaking_score(self) -> int:
        """Calculate pattern breaking score based on technique diversity"""
        if not self.techniques_used:
            return 0
        
        unique_techniques = len(set(self.techniques_used))
        total_techniques = 6  # Total available techniques
        
        # Score based on technique diversity
        diversity_score = (unique_techniques / total_techniques) * 100
        return int(diversity_score)
    
    async def get_lateral_thinking_history(self) -> List[Dict[str, Any]]:
        """Get history of all lateral thinking sessions"""
        return [thought.to_dict() for thought in self.ideas]
    
    async def get_lateral_thinking_stats(self) -> Dict[str, Any]:
        """Get statistics about lateral thinking sessions"""
        if not self.ideas:
            return {
                "total_thoughts": 0,
                "techniques_used": [],
                "most_creative_technique": None,
                "pattern_breaking_score": 0,
                "creativity_distribution": {}
            }
        
        total_thoughts = len(self.ideas)
        techniques_used = list(set(self.techniques_used))
        
        # Count technique usage
        technique_counts = {}
        for technique in self.techniques_used:
            technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        most_used_technique = max(technique_counts.items(), key=lambda x: x[1])[0] if technique_counts else None
        
        # Calculate average creativity
        creativity_scores = [self._assess_creativity_score(thought) for thought in self.ideas]
        average_creativity = sum(creativity_scores) / len(creativity_scores) if creativity_scores else 0
        
        return {
            "total_thoughts": total_thoughts,
            "techniques_used": techniques_used,
            "technique_usage": technique_counts,
            "most_used_technique": most_used_technique,
            "pattern_breaking_score": self._calculate_pattern_breaking_score(),
            "average_creativity": round(average_creativity, 2),
            "creativity_distribution": {
                "high": len([s for s in creativity_scores if s >= 8]),
                "medium": len([s for s in creativity_scores if 5 <= s < 8]),
                "low": len([s for s in creativity_scores if s < 5])
            }
        }


# Global lateral thinking processor instance
_lateral_thinking_processor = None


def get_lateral_thinking_processor() -> LateralThinkingProcessor:
    """Get the global lateral thinking processor instance"""
    global _lateral_thinking_processor
    if _lateral_thinking_processor is None:
        _lateral_thinking_processor = LateralThinkingProcessor()
    return _lateral_thinking_processor


# Convenience functions for external use
async def lateral_thinking_analysis(thinking_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform lateral thinking analysis"""
    processor = get_lateral_thinking_processor()
    return await processor.process_lateral_thinking(thinking_data)


async def get_lateral_thinking_history() -> List[Dict[str, Any]]:
    """Get history of lateral thinking sessions"""
    processor = get_lateral_thinking_processor()
    return await processor.get_lateral_thinking_history()


async def get_lateral_thinking_stats() -> Dict[str, Any]:
    """Get statistics about lateral thinking sessions"""
    processor = get_lateral_thinking_processor()
    return await processor.get_lateral_thinking_stats()
