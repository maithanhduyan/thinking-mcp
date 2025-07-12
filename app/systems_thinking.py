# -*- coding: utf-8 -*-
# File: app/systems_thinking.py
"""
Systems Thinking Module - Tư duy hệ thống

Phân tích toàn diện các hệ thống phức tạp, xác định mối quan hệ, 
pattern và leverage points để can thiệp hiệu quả.

Key concepts:
- System components và relationships
- Feedback loops (reinforcing và balancing)  
- Constraints và bottlenecks
- Emergent properties
- Leverage points for intervention
- Systemic issues vs symptoms
- Root cause analysis

When to use:
- Complex organizational problems
- Process improvement
- Understanding interconnected issues
- Strategic planning
- Root cause analysis
- Change management
- Policy design
- Business ecosystem analysis
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from app.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemComponent:
    """Component trong hệ thống"""
    name: str
    type: str  # 'input', 'process', 'output', 'feedback', 'environment'
    description: str
    relationships: List[str]


@dataclass
class SystemsAnalysis:
    """Kết quả phân tích hệ thống"""
    session_id: str
    analysis_number: int
    analysis_data: Dict[str, Any]
    system_info: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    analysis_summary: Dict[str, Any]
    next_steps: Optional[Dict[str, Any]]
    formatted_display: str
    metadata: Dict[str, Any]


class SystemsThinkingAnalyzer:
    """Analyzer cho Systems Thinking"""
    
    def __init__(self):
        self.analyses: List[SystemsAnalysis] = []
        self.session_counter = 0
    
    def validate_systems_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data cho systems analysis"""
        required_fields = [
            'system_name', 'purpose', 'components', 'feedback_loops',
            'constraints', 'emergent_properties', 'leverage_points',
            'systemic_issues', 'interventions', 'next_analysis_needed'
        ]
        
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate types
        if not isinstance(input_data['system_name'], str):
            raise ValueError("system_name must be string")
        if not isinstance(input_data['purpose'], str):
            raise ValueError("purpose must be string")
        if not isinstance(input_data['components'], list):
            raise ValueError("components must be list")
        if not isinstance(input_data['feedback_loops'], list):
            raise ValueError("feedback_loops must be list")
        if not isinstance(input_data['constraints'], list):
            raise ValueError("constraints must be list")
        if not isinstance(input_data['emergent_properties'], list):
            raise ValueError("emergent_properties must be list")
        if not isinstance(input_data['leverage_points'], list):
            raise ValueError("leverage_points must be list")
        if not isinstance(input_data['systemic_issues'], list):
            raise ValueError("systemic_issues must be list")
        if not isinstance(input_data['interventions'], list):
            raise ValueError("interventions must be list")
        if not isinstance(input_data['next_analysis_needed'], bool):
            raise ValueError("next_analysis_needed must be boolean")
        
        # Validate components structure
        for component in input_data['components']:
            if not isinstance(component, dict):
                raise ValueError("Each component must be a dict")
            required_comp_fields = ['name', 'type', 'description', 'relationships']
            for field in required_comp_fields:
                if field not in component:
                    raise ValueError(f"Component missing field: {field}")
            
            valid_types = ['input', 'process', 'output', 'feedback', 'environment']
            if component['type'] not in valid_types:
                raise ValueError(f"Component type must be one of: {valid_types}")
        
        return input_data
    
    def assess_analysis_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Đánh giá chất lượng phân tích"""
        score = 0
        max_score = 10
        
        # System definition quality (2 points)
        if len(data['system_name']) > 5 and len(data['purpose']) > 10:
            score += 2
        elif len(data['system_name']) > 0 and len(data['purpose']) > 0:
            score += 1
        
        # Components analysis (2 points)
        if len(data['components']) >= 5:
            score += 2
        elif len(data['components']) >= 3:
            score += 1
        
        # Feedback loops identification (2 points)
        if len(data['feedback_loops']) >= 3:
            score += 2
        elif len(data['feedback_loops']) >= 1:
            score += 1
        
        # Leverage points (2 points)
        if len(data['leverage_points']) >= 3:
            score += 2
        elif len(data['leverage_points']) >= 1:
            score += 1
        
        # Systemic vs symptomatic thinking (2 points)
        if len(data['systemic_issues']) >= 2 and len(data['interventions']) >= 2:
            score += 2
        elif len(data['systemic_issues']) >= 1 or len(data['interventions']) >= 1:
            score += 1
        
        quality_percentage = (score / max_score) * 100
        
        if quality_percentage >= 90:
            quality_level = "EXCELLENT"
        elif quality_percentage >= 70:
            quality_level = "GOOD"
        elif quality_percentage >= 50:
            quality_level = "AVERAGE"
        else:
            quality_level = "NEEDS_IMPROVEMENT"
        
        return {
            "quality_score": score,
            "max_score": max_score,
            "quality_percentage": quality_percentage,
            "quality_level": quality_level
        }
    
    def get_system_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Thông tin về hệ thống"""
        component_types = {}
        for component in data['components']:
            comp_type = component['type']
            component_types[comp_type] = component_types.get(comp_type, 0) + 1
        
        return {
            "system_name": data['system_name'],
            "emoji": "🔄",
            "guidance": "Analyze system holistically, focusing on relationships and feedback loops rather than individual components."
        }
    
    def format_systems_display(self, data: Dict[str, Any], quality: Dict[str, Any]) -> str:
        """Format display cho systems analysis"""
        
        header = "🔄 SYSTEMS THINKING ANALYSIS"
        
        # Component breakdown by type
        component_types = {}
        for component in data['components']:
            comp_type = component['type']
            component_types[comp_type] = component_types.get(comp_type, 0) + 1
        
        components_display = ""
        for comp_type, count in component_types.items():
            components_display += f"   - {comp_type.capitalize()}: {count}\n"
        
        feedback_display = ""
        for i, loop in enumerate(data['feedback_loops'][:3], 1):
            feedback_display += f"   {i}. {loop}\n"
        
        leverage_display = ""
        for i, point in enumerate(data['leverage_points'][:3], 1):
            leverage_display += f"   • {point}\n"
        
        issues_display = ""
        for i, issue in enumerate(data['systemic_issues'][:3], 1):
            issues_display += f"   ◦ {issue}\n"
        
        interventions_display = ""
        for i, intervention in enumerate(data['interventions'][:3], 1):
            interventions_display += f"   ✓ {intervention}\n"
        
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    {header}                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ SYSTEM: {data['system_name']}
║ PURPOSE: {data['purpose']}
║ 
║ COMPONENTS ({len(data['components'])} identified):
{components_display}║ 
║ FEEDBACK LOOPS ({len(data['feedback_loops'])} found):
{feedback_display}║ 
║ CONSTRAINTS ({len(data['constraints'])}):
║   {', '.join(data['constraints'][:3])}
║ 
║ EMERGENT PROPERTIES ({len(data['emergent_properties'])}):
║   {', '.join(data['emergent_properties'][:3])}
║ 
║ LEVERAGE POINTS ({len(data['leverage_points'])}):
{leverage_display}║ 
║ SYSTEMIC ISSUES ({len(data['systemic_issues'])}):
{issues_display}║ 
║ INTERVENTIONS ({len(data['interventions'])}):
{interventions_display}║ 
║ NEXT ANALYSIS NEEDED: {'YES' if data['next_analysis_needed'] else 'NO'}
║ QUALITY: {quality['quality_level']} ({quality['quality_percentage']:.0f}%)
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    def create_analysis_summary(self, data: Dict[str, Any], quality: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo summary cho analysis"""
        return {
            "system_name": data['system_name'],
            "components_count": len(data['components']),
            "feedback_loops_count": len(data['feedback_loops']),
            "leverage_points_count": len(data['leverage_points']),
            "systemic_issues_count": len(data['systemic_issues']),
            "interventions_count": len(data['interventions']),
            "quality_level": quality['quality_level'],
            "next_analysis_needed": data['next_analysis_needed']
        }
    
    def suggest_next_steps(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Đề xuất next steps"""
        if not data['next_analysis_needed']:
            return None
        
        suggestions = []
        
        if len(data['components']) < 5:
            suggestions.append("Identify more system components and their relationships")
        
        if len(data['feedback_loops']) < 2:
            suggestions.append("Analyze additional feedback loops in the system")
        
        if len(data['leverage_points']) < 3:
            suggestions.append("Identify more high-impact intervention points")
        
        if len(data['interventions']) < len(data['systemic_issues']):
            suggestions.append("Develop interventions for each systemic issue")
        
        return {
            "recommended_actions": suggestions,
            "focus_areas": ["component_mapping", "feedback_analysis", "leverage_identification"],
            "estimated_effort": "medium"
        }
    
    async def analyze_system(self, input_data: Dict[str, Any]) -> SystemsAnalysis:
        """Thực hiện systems thinking analysis"""
        
        # Validate input
        validated_data = self.validate_systems_data(input_data)
        
        # Generate session ID
        self.session_counter += 1
        session_id = f"sys_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Assess quality
        quality = self.assess_analysis_quality(validated_data)
        
        # Get system info
        system_info = self.get_system_info(validated_data)
        
        # Create summary
        summary = self.create_analysis_summary(validated_data, quality)
        
        # Suggest next steps
        next_steps = self.suggest_next_steps(validated_data)
        
        # Format display
        formatted_display = self.format_systems_display(validated_data, quality)
        
        # Create analysis result
        analysis = SystemsAnalysis(
            session_id=session_id,
            analysis_number=self.session_counter,
            analysis_data=validated_data,
            system_info=system_info,
            quality_assessment=quality,
            analysis_summary=summary,
            next_steps=next_steps,
            formatted_display=formatted_display,
            metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_analyses": self.session_counter,
                "analysis_type": "systems_thinking",
                "version": "1.0.0"
            }
        )
        
        # Store analysis
        self.analyses.append(analysis)
        
        logger.info(f"Systems thinking analysis completed: {session_id}")
        
        return analysis


# Global analyzer instance
systems_analyzer = SystemsThinkingAnalyzer()


async def systems_thinking_analysis(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main function để thực hiện systems thinking analysis"""
    try:
        analysis = await systems_analyzer.analyze_system(input_data)
        return asdict(analysis)
    except Exception as e:
        logger.error(f"Error in systems thinking analysis: {e}")
        raise


async def get_systems_thinking_history() -> List[Dict[str, Any]]:
    """Lấy lịch sử các phân tích systems thinking"""
    try:
        return [asdict(analysis) for analysis in systems_analyzer.analyses]
    except Exception as e:
        logger.error(f"Error getting systems thinking history: {e}")
        raise


async def get_systems_thinking_stats() -> Dict[str, Any]:
    """Lấy thống kê về các phân tích systems thinking"""
    try:
        analyses = systems_analyzer.analyses
        
        if not analyses:
            return {
                "total_analyses": 0,
                "average_quality": 0,
                "systems_analyzed": [],
                "common_leverage_points": [],
                "analysis_trends": {}
            }
        
        # Calculate stats
        total_analyses = len(analyses)
        average_quality = sum(a.quality_assessment['quality_percentage'] for a in analyses) / total_analyses
        
        systems_analyzed = [a.analysis_data['system_name'] for a in analyses]
        
        # Collect all leverage points
        all_leverage_points = []
        for analysis in analyses:
            all_leverage_points.extend(analysis.analysis_data['leverage_points'])
        
        # Count common leverage points
        leverage_counts = {}
        for point in all_leverage_points:
            leverage_counts[point] = leverage_counts.get(point, 0) + 1
        
        common_leverage_points = sorted(leverage_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Analysis trends
        quality_levels = [a.quality_assessment['quality_level'] for a in analyses]
        quality_distribution = {}
        for level in quality_levels:
            quality_distribution[level] = quality_distribution.get(level, 0) + 1
        
        return {
            "total_analyses": total_analyses,
            "average_quality": round(average_quality, 2),
            "systems_analyzed": systems_analyzed,
            "common_leverage_points": common_leverage_points,
            "analysis_trends": {
                "quality_distribution": quality_distribution,
                "average_components_per_system": sum(len(a.analysis_data['components']) for a in analyses) / total_analyses,
                "average_feedback_loops": sum(len(a.analysis_data['feedback_loops']) for a in analyses) / total_analyses,
                "average_leverage_points": sum(len(a.analysis_data['leverage_points']) for a in analyses) / total_analyses
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting systems thinking stats: {e}")
        raise
