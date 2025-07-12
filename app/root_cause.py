# -*- coding: utf-8 -*-
# File: app/root_cause.py
# Root Cause Analysis Module for MCP Server - Systematic Problem Analysis

"""
Root Cause Analysis (RCA) - Phân tích nguyên nhân gốc rễ

Root Cause Analysis là quy trình có hệ thống để xác định nguyên nhân cơ bản của vấn đề hoặc sự cố.
Mục tiêu là giải quyết nguyên nhân gốc rễ thay vì chỉ điều trị các triệu chứng, 
dẫn đến các giải pháp hiệu quả và bền vững hơn.

Các kỹ thuật phổ biến:
- 5_whys: Hỏi "tại sao" liên tục để đi sâu vào nguyên nhân gốc
- fishbone: Sơ đồ Ishikawa để phân loại các nguyên nhân tiềm ẩn
- fault_tree: Phân tích thất bại từ trên xuống (top-down)
- timeline: Phân tích theo thời gian của các sự kiện dẫn đến vấn đề
- barrier_analysis: Phân tích các rào cản nào đã thất bại trong việc ngăn chặn vấn đề

RCA được sử dụng rộng rãi trong các lĩnh vực như kỹ thuật, y tế, và kinh doanh 
để cải thiện quy trình và ngăn chặn tái diễn vấn đề.
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Literal
from app.logger import get_logger

logger = get_logger(__name__)

# Type definitions for RCA techniques
RCATechnique = Literal[
    "5_whys", 
    "fishbone", 
    "fault_tree", 
    "timeline", 
    "barrier_analysis"
]


class RootCauseAnalysisData:
    """Data structure for root cause analysis results"""
    
    def __init__(self, 
                 problem_statement: str,
                 technique: RCATechnique,
                 symptoms: List[str],
                 immediate_actions: List[str],
                 root_causes: List[str],
                 contributing_factors: List[str],
                 preventive_actions: List[str],
                 verification: List[str],
                 next_analysis_needed: bool):
        self.problem_statement = problem_statement
        self.technique = technique
        self.symptoms = symptoms
        self.immediate_actions = immediate_actions
        self.root_causes = root_causes
        self.contributing_factors = contributing_factors
        self.preventive_actions = preventive_actions
        self.verification = verification
        self.next_analysis_needed = next_analysis_needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "problem_statement": self.problem_statement,
            "technique": self.technique,
            "symptoms": self.symptoms,
            "immediate_actions": self.immediate_actions,
            "root_causes": self.root_causes,
            "contributing_factors": self.contributing_factors,
            "preventive_actions": self.preventive_actions,
            "verification": self.verification,
            "next_analysis_needed": self.next_analysis_needed
        }


class RootCauseAnalysisProcessor:
    """Processor for root cause analysis"""
    
    def __init__(self):
        self.analyses: List[RootCauseAnalysisData] = []
        self.analysis_counter = 0
    
    def _validate_rca_data(self, data: Dict[str, Any]) -> RootCauseAnalysisData:
        """Validate and create RootCauseAnalysisData from input data"""
        
        # Validate problem_statement
        problem_statement = data.get("problem_statement")
        if not problem_statement or not isinstance(problem_statement, str):
            raise ValueError("Invalid problem_statement: must be a non-empty string")
        
        # Validate technique
        technique = data.get("technique")
        valid_techniques = ["5_whys", "fishbone", "fault_tree", "timeline", "barrier_analysis"]
        if not technique or technique not in valid_techniques:
            raise ValueError(f"Invalid technique: must be one of {valid_techniques}")
        
        # Validate symptoms
        symptoms = data.get("symptoms")
        if not isinstance(symptoms, list):
            raise ValueError("Invalid symptoms: must be a list")
        
        # Validate immediate_actions
        immediate_actions = data.get("immediate_actions")
        if not isinstance(immediate_actions, list):
            raise ValueError("Invalid immediate_actions: must be a list")
        
        # Validate root_causes
        root_causes = data.get("root_causes")
        if not isinstance(root_causes, list):
            raise ValueError("Invalid root_causes: must be a list")
        
        # Validate contributing_factors
        contributing_factors = data.get("contributing_factors")
        if not isinstance(contributing_factors, list):
            raise ValueError("Invalid contributing_factors: must be a list")
        
        # Validate preventive_actions
        preventive_actions = data.get("preventive_actions")
        if not isinstance(preventive_actions, list):
            raise ValueError("Invalid preventive_actions: must be a list")
        
        # Validate verification
        verification = data.get("verification")
        if not isinstance(verification, list):
            raise ValueError("Invalid verification: must be a list")
        
        # Validate next_analysis_needed
        next_analysis_needed = data.get("next_analysis_needed")
        if not isinstance(next_analysis_needed, bool):
            raise ValueError("Invalid next_analysis_needed: must be a boolean")
        
        return RootCauseAnalysisData(
            problem_statement=problem_statement,
            technique=technique,
            symptoms=symptoms,
            immediate_actions=immediate_actions,
            root_causes=root_causes,
            contributing_factors=contributing_factors,
            preventive_actions=preventive_actions,
            verification=verification,
            next_analysis_needed=next_analysis_needed
        )
    
    def _get_technique_emoji(self, technique: str) -> str:
        """Get emoji for RCA technique type"""
        technique_emojis = {
            '5_whys': '❓',
            'fishbone': '🐟',
            'fault_tree': '🌳',
            'timeline': '📅',
            'barrier_analysis': '🚧'
        }
        return technique_emojis.get(technique, '🔍')
    
    def _format_rca_analysis(self, analysis: RootCauseAnalysisData) -> str:
        """Format root cause analysis for display"""
        
        emoji = self._get_technique_emoji(analysis.technique)
        technique_name = analysis.technique.replace('_', ' ').title()
        
        formatted_output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    {emoji} ROOT CAUSE ANALYSIS: {technique_name.upper()}                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PROBLEM: {analysis.problem_statement[:65]}{'...' if len(analysis.problem_statement) > 65 else ''}
║ 
║ SYMPTOMS ({len(analysis.symptoms)} identified):
{self._format_list_items(analysis.symptoms, '║   - ', 70)}
║ 
║ IMMEDIATE ACTIONS ({len(analysis.immediate_actions)} taken):
{self._format_list_items(analysis.immediate_actions, '║   - ', 70)}
║ 
║ ROOT CAUSES ({len(analysis.root_causes)} found):
{self._format_list_items(analysis.root_causes, '║   • ', 70)}
║ 
║ CONTRIBUTING FACTORS ({len(analysis.contributing_factors)}):
{self._format_list_items(analysis.contributing_factors, '║   ◦ ', 70)}
║ 
║ PREVENTIVE ACTIONS ({len(analysis.preventive_actions)}):
{self._format_list_items(analysis.preventive_actions, '║   ✓ ', 70)}
║ 
║ VERIFICATION STEPS ({len(analysis.verification)}):
{self._format_list_items(analysis.verification, '║   ⚡ ', 70)}
║ 
║ NEXT ANALYSIS NEEDED: {"YES" if analysis.next_analysis_needed else "NO"}
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return formatted_output
    
    def _format_list_items(self, items: List[str], prefix: str, max_width: int) -> str:
        """Format list items with proper wrapping"""
        if not items:
            return f"{prefix}None"
        
        formatted_items = []
        for item in items:
            if len(item) <= max_width - len(prefix):
                formatted_items.append(f"{prefix}{item}")
            else:
                # Wrap long items
                truncated = item[:max_width - len(prefix) - 3] + "..."
                formatted_items.append(f"{prefix}{truncated}")
        
        return '\n'.join(formatted_items)
    
    def _generate_technique_guidance(self, technique: str) -> str:
        """Generate guidance for specific RCA technique"""
        
        guidance = {
            "5_whys": "Ask 'why' repeatedly (typically 5 times) to drill down from symptoms to root causes. Each answer becomes the basis for the next 'why' question.",
            "fishbone": "Use Ishikawa diagram to categorize potential causes into main categories (e.g., People, Process, Equipment, Environment, Material, Method).",
            "fault_tree": "Start with the undesired event and work backwards through logical gates to identify basic causes and their combinations.",
            "timeline": "Create a chronological sequence of events leading to the problem to identify critical decision points and failure moments.",
            "barrier_analysis": "Identify what barriers (controls, safeguards) were supposed to prevent the problem and analyze why they failed."
        }
        
        return guidance.get(technique, "Apply systematic analysis to identify root causes.")
    
    def _assess_analysis_quality(self, analysis: RootCauseAnalysisData) -> Dict[str, Any]:
        """Assess the quality and completeness of the RCA"""
        
        quality_score = 0
        max_score = 10
        
        # Check if root causes are deeper than symptoms
        if len(analysis.root_causes) > 0:
            quality_score += 2
        
        # Check if preventive actions address root causes
        if len(analysis.preventive_actions) >= len(analysis.root_causes):
            quality_score += 2
        
        # Check if verification steps are defined
        if len(analysis.verification) > 0:
            quality_score += 2
        
        # Check if immediate actions are defined
        if len(analysis.immediate_actions) > 0:
            quality_score += 1
        
        # Check if contributing factors are identified
        if len(analysis.contributing_factors) > 0:
            quality_score += 1
        
        # Check problem statement clarity
        if len(analysis.problem_statement) > 20:
            quality_score += 1
        
        # Check if multiple symptoms are identified
        if len(analysis.symptoms) > 1:
            quality_score += 1
        
        quality_percentage = (quality_score / max_score) * 100
        
        return {
            "quality_score": quality_score,
            "max_score": max_score,
            "quality_percentage": round(quality_percentage, 1),
            "quality_level": self._get_quality_level(quality_percentage)
        }
    
    def _get_quality_level(self, percentage: float) -> str:
        """Get quality level based on percentage"""
        if percentage >= 80:
            return "EXCELLENT"
        elif percentage >= 60:
            return "GOOD"
        elif percentage >= 40:
            return "FAIR"
        else:
            return "NEEDS_IMPROVEMENT"
    
    async def process_root_cause_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process root cause analysis"""
        
        try:
            # Validate input data
            validated_analysis = self._validate_rca_data(input_data)
            
            # Store analysis
            self.analyses.append(validated_analysis)
            self.analysis_counter += 1
            
            # Format analysis for logging
            formatted_analysis = self._format_rca_analysis(validated_analysis)
            logger.info(f"Root Cause Analysis #{self.analysis_counter}:\n{formatted_analysis}")
            
            # Create session ID
            session_id = f"rca_{int(datetime.now(timezone.utc).timestamp())}"
            
            # Generate technique guidance
            technique_guidance = self._generate_technique_guidance(validated_analysis.technique)
            
            # Assess analysis quality
            quality_assessment = self._assess_analysis_quality(validated_analysis)
            
            # Suggest next steps if needed
            next_steps = None
            if validated_analysis.next_analysis_needed:
                next_steps = self._suggest_next_analysis_steps(validated_analysis)
            
            # Prepare result
            result = {
                "session_id": session_id,
                "analysis_number": self.analysis_counter,
                "analysis_data": validated_analysis.to_dict(),
                "technique_info": {
                    "technique": validated_analysis.technique,
                    "emoji": self._get_technique_emoji(validated_analysis.technique),
                    "guidance": technique_guidance
                },
                "quality_assessment": quality_assessment,
                "analysis_summary": {
                    "problem_statement": validated_analysis.problem_statement,
                    "symptoms_count": len(validated_analysis.symptoms),
                    "root_causes_count": len(validated_analysis.root_causes),
                    "preventive_actions_count": len(validated_analysis.preventive_actions),
                    "verification_steps_count": len(validated_analysis.verification),
                    "quality_level": quality_assessment["quality_level"],
                    "next_analysis_needed": validated_analysis.next_analysis_needed
                },
                "next_steps": next_steps,
                "formatted_display": formatted_analysis,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_analyses": len(self.analyses),
                    "analysis_type": "root_cause_analysis",
                    "version": "1.0.0"
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in root cause analysis: {e}")
            raise ValueError(f"Root cause analysis failed: {str(e)}")
    
    def _suggest_next_analysis_steps(self, analysis: RootCauseAnalysisData) -> Dict[str, Any]:
        """Suggest next steps for further analysis"""
        
        suggestions = []
        
        # Suggest different technique if current one might be insufficient
        current_technique = analysis.technique
        if current_technique == "5_whys" and len(analysis.root_causes) < 2:
            suggestions.append("Consider using fishbone diagram to explore more cause categories")
        elif current_technique == "fishbone" and not analysis.verification:
            suggestions.append("Use fault tree analysis to validate cause-effect relationships")
        elif current_technique in ["5_whys", "fishbone"] and len(analysis.symptoms) > 3:
            suggestions.append("Consider timeline analysis to understand sequence of events")
        
        # Suggest barrier analysis if not used
        if current_technique != "barrier_analysis" and len(analysis.preventive_actions) > 0:
            suggestions.append("Perform barrier analysis to understand why existing controls failed")
        
        # General suggestions
        if len(analysis.verification) == 0:
            suggestions.append("Define verification steps to confirm root causes")
        
        if len(analysis.preventive_actions) < len(analysis.root_causes):
            suggestions.append("Develop preventive actions for each identified root cause")
        
        return {
            "suggestions": suggestions,
            "recommended_next_technique": self._recommend_next_technique(current_technique),
            "focus_areas": self._identify_focus_areas(analysis)
        }
    
    def _recommend_next_technique(self, current_technique: str) -> str:
        """Recommend next RCA technique based on current one"""
        
        recommendations = {
            "5_whys": "fishbone",
            "fishbone": "fault_tree", 
            "fault_tree": "timeline",
            "timeline": "barrier_analysis",
            "barrier_analysis": "5_whys"
        }
        
        return recommendations.get(current_technique, "fishbone")
    
    def _identify_focus_areas(self, analysis: RootCauseAnalysisData) -> List[str]:
        """Identify areas that need more focus in analysis"""
        
        focus_areas = []
        
        if len(analysis.root_causes) == 0:
            focus_areas.append("Root cause identification")
        
        if len(analysis.preventive_actions) == 0:
            focus_areas.append("Preventive action development")
        
        if len(analysis.verification) == 0:
            focus_areas.append("Verification methodology")
        
        if len(analysis.contributing_factors) == 0:
            focus_areas.append("Contributing factor analysis")
        
        return focus_areas
    
    async def get_rca_history(self) -> List[Dict[str, Any]]:
        """Get history of all root cause analyses"""
        return [analysis.to_dict() for analysis in self.analyses]
    
    async def get_rca_stats(self) -> Dict[str, Any]:
        """Get statistics about root cause analyses"""
        if not self.analyses:
            return {
                "total_analyses": 0,
                "techniques_used": [],
                "average_quality": 0.0,
                "quality_distribution": {}
            }
        
        total_analyses = len(self.analyses)
        techniques_used = list(set([analysis.technique for analysis in self.analyses]))
        
        # Count technique usage
        technique_counts = {}
        for analysis in self.analyses:
            technique_counts[analysis.technique] = technique_counts.get(analysis.technique, 0) + 1
        
        most_used_technique = max(technique_counts.items(), key=lambda x: x[1])[0] if technique_counts else None
        
        # Calculate average quality
        quality_scores = [self._assess_analysis_quality(analysis)["quality_percentage"] for analysis in self.analyses]
        average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "total_analyses": total_analyses,
            "techniques_used": techniques_used,
            "technique_usage": technique_counts,
            "most_used_technique": most_used_technique,
            "average_quality": round(average_quality, 2),
            "quality_distribution": {
                "excellent": len([s for s in quality_scores if s >= 80]),
                "good": len([s for s in quality_scores if 60 <= s < 80]),
                "fair": len([s for s in quality_scores if 40 <= s < 60]),
                "needs_improvement": len([s for s in quality_scores if s < 40])
            }
        }


# Global root cause analysis processor instance
_rca_processor = None


def get_rca_processor() -> RootCauseAnalysisProcessor:
    """Get the global root cause analysis processor instance"""
    global _rca_processor
    if _rca_processor is None:
        _rca_processor = RootCauseAnalysisProcessor()
    return _rca_processor


# Convenience functions for external use
async def root_cause_analysis(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform root cause analysis"""
    processor = get_rca_processor()
    return await processor.process_root_cause_analysis(analysis_data)


async def get_rca_history() -> List[Dict[str, Any]]:
    """Get history of root cause analyses"""
    processor = get_rca_processor()
    return await processor.get_rca_history()


async def get_rca_stats() -> Dict[str, Any]:
    """Get statistics about root cause analyses"""
    processor = get_rca_processor()
    return await processor.get_rca_stats()
