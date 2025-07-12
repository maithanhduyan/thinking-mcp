# -*- coding: utf-8 -*-
"""
Six Thinking Hats implementation for thinking-mcp
Based on Edward de Bono's Six Thinking Hats methodology
Adapted for Python from Rust implementation
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union


class HatColor(Enum):
    """Six Thinking Hats colors with descriptions and emojis"""
    WHITE = "white"   # Facts and information
    RED = "red"       # Emotions and feelings
    BLACK = "black"   # Critical judgment
    YELLOW = "yellow" # Positive assessment
    GREEN = "green"   # Creativity and alternatives
    BLUE = "blue"     # Process control

    @property
    def description(self) -> str:
        """Get the description for each hat color"""
        descriptions = {
            HatColor.WHITE: "Facts and Information",
            HatColor.RED: "Emotions and Feelings", 
            HatColor.BLACK: "Critical Judgment",
            HatColor.YELLOW: "Positive Assessment",
            HatColor.GREEN: "Creativity and Alternatives",
            HatColor.BLUE: "Process Control"
        }
        return descriptions[self]

    @property
    def emoji(self) -> str:
        """Get the emoji for each hat color"""
        emojis = {
            HatColor.WHITE: "⚪",
            HatColor.RED: "🔴",
            HatColor.BLACK: "⚫",
            HatColor.YELLOW: "🟡",
            HatColor.GREEN: "🟢",
            HatColor.BLUE: "🔵"
        }
        return emojis[self]

    @property
    def guidelines(self) -> List[str]:
        """Get thinking guidelines for each hat"""
        guidelines = {
            HatColor.WHITE: [
                "Focus on facts, data, and information",
                "What do we know? What don't we know?",
                "What information is missing?",
                "How can we get the information we need?"
            ],
            HatColor.RED: [
                "Express emotions, feelings, and intuition", 
                "What are your gut feelings about this?",
                "How do you feel about this situation?",
                "What are your emotional reactions?"
            ],
            HatColor.BLACK: [
                "Critical thinking and caution",
                "What could go wrong?",
                "What are the risks and dangers?",
                "Why might this not work?"
            ],
            HatColor.YELLOW: [
                "Positive thinking and optimism",
                "What are the benefits and opportunities?",
                "Why will this work?",
                "What are the best-case scenarios?"
            ],
            HatColor.GREEN: [
                "Creative thinking and alternatives",
                "What are other ways to do this?",
                "What new ideas can we generate?",
                "How can we think outside the box?"
            ],
            HatColor.BLUE: [
                "Process control and meta-thinking",
                "What thinking process should we use?",
                "How should we approach this problem?",
                "What have we accomplished so far?"
            ]
        }
        return guidelines[self]


def validate_six_hats_params(params: Dict[str, Any]) -> None:
    """Validate Six Hats parameters following Python flexible approach"""
    if not isinstance(params, dict):
        raise ValueError("Parameters must be a dictionary")
    
    required_fields = ["hat_color", "perspective", "insights", "questions", "next_hat_needed", "session_complete"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    
    # Flexible validation - empty strings and lists are allowed
    hat_color = params.get("hat_color", "").lower()
    valid_colors = ["white", "red", "black", "yellow", "green", "blue"]
    if hat_color not in valid_colors:
        raise ValueError(f"Invalid hat_color: {hat_color}. Must be one of: {valid_colors}")
    
    # Type checking but flexible
    if not isinstance(params.get("insights", []), list):
        raise ValueError("insights must be a list")
    if not isinstance(params.get("questions", []), list):
        raise ValueError("questions must be a list")
    if not isinstance(params.get("next_hat_needed"), bool):
        raise ValueError("next_hat_needed must be a boolean")
    if not isinstance(params.get("session_complete"), bool):
        raise ValueError("session_complete must be a boolean")


def format_six_hats_output(hat_color: HatColor, perspective: str, insights: List[str], 
                          questions: List[str], session_complete: bool) -> str:
    """Format Six Hats output following thinking-mcp patterns"""
    emoji = hat_color.emoji
    description = hat_color.description
    hat_name = hat_color.name.title()
    
    # Create visual output similar to other thinking tools
    output = f"\n╔══════════════════════════════════════════════════════════════════════════════╗\n"
    output += f"║                    {emoji} SIX HATS: {hat_name.upper()} HAT                    ║\n"
    output += f"╠══════════════════════════════════════════════════════════════════════════════╣\n"
    output += f"║ PERSPECTIVE: {description}\n"
    output += f"║ \n"
    output += f"║ THINKING FOCUS:\n"
    output += f"║   {perspective}\n"
    output += f"║ \n"
    
    if insights:
        output += f"║ KEY INSIGHTS ({len(insights)}):\n"
        for i, insight in enumerate(insights, 1):
            output += f"║   {i}. {insight}\n"
        output += f"║ \n"
    
    if questions:
        output += f"║ QUESTIONS RAISED ({len(questions)}):\n"
        for i, question in enumerate(questions, 1):
            output += f"║   ❓ {question}\n"
        output += f"║ \n"
    
    # Add guidelines for this hat
    guidelines = hat_color.guidelines
    output += f"║ THINKING GUIDELINES:\n"
    for guideline in guidelines:
        output += f"║   • {guideline}\n"
    
    output += f"║ \n"
    output += f"║ SESSION STATUS: {'COMPLETE' if session_complete else 'IN PROGRESS'}\n"
    output += f"╚══════════════════════════════════════════════════════════════════════════════╝\n"
    
    return output


def create_six_hats_response(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create Six Hats response following Python thinking-mcp patterns"""
    hat_color_str = params["hat_color"].lower()
    hat_color = HatColor(hat_color_str)
    
    perspective = params["perspective"]
    insights = params["insights"]
    questions = params["questions"]
    next_hat_needed = params["next_hat_needed"]
    session_complete = params["session_complete"]
    
    # Format display output
    formatted_output = format_six_hats_output(
        hat_color, perspective, insights, questions, session_complete
    )
    
    # Create response following thinking-mcp pattern
    response = {
        "method": "six_thinking_hats",
        "hat_data": {
            "hat_color": hat_color_str,
            "hat_name": hat_color.name.title(),
            "description": hat_color.description,
            "emoji": hat_color.emoji,
            "perspective": perspective,
            "insights": insights,
            "insights_count": len(insights),
            "questions": questions,
            "questions_count": len(questions),
            "guidelines": hat_color.guidelines,
            "next_hat_needed": next_hat_needed,
            "session_complete": session_complete
        },
        "analysis_summary": {
            "hat_processed": hat_color_str,
            "insights_count": len(insights),
            "questions_count": len(questions),
            "session_complete": session_complete,
            "quality_level": "GOOD" if insights or questions else "BASIC",
            "next_hat_needed": next_hat_needed
        },
        "formatted_display": formatted_output,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"{hat_color.emoji} {hat_color.name.title()} Hat thinking completed successfully"
    }
    
    return response


def get_recommended_hat_sequence() -> List[Dict[str, str]]:
    """Get recommended sequence for Six Hats session"""
    return [
        {
            "order": "1",
            "hat": "blue",
            "purpose": "Define the problem and set thinking agenda",
            "focus": "What are we thinking about? How should we approach this?"
        },
        {
            "order": "2", 
            "hat": "white",
            "purpose": "Gather facts and information",
            "focus": "What do we know? What information do we need?"
        },
        {
            "order": "3",
            "hat": "red",
            "purpose": "Express emotions and feelings",
            "focus": "How do we feel about this? What are our gut reactions?"
        },
        {
            "order": "4",
            "hat": "black",
            "purpose": "Critical evaluation and risk assessment", 
            "focus": "What could go wrong? What are the risks?"
        },
        {
            "order": "5",
            "hat": "yellow",
            "purpose": "Positive assessment and benefits",
            "focus": "What are the benefits? Why will this work?"
        },
        {
            "order": "6",
            "hat": "green",
            "purpose": "Creative alternatives and new ideas",
            "focus": "What other options do we have? What new ideas can we generate?"
        },
        {
            "order": "7",
            "hat": "blue",
            "purpose": "Summarize and conclude",
            "focus": "What have we learned? What's our next step?"
        }
    ]
