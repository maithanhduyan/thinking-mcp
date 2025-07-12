# -*- coding: utf-8 -*-
# File: app/critical.py
# Critical Thinking Module for MCP Server
"""
Critical Thinking (Tư duy phản biện)
Phân tích, đánh giá thông tin
Tìm lỗ hổng trong lập luận
Kiểm tra tính hợp lý
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from app.logger import get_logger

logger = get_logger(__name__)


class CriticalAnalysis:
    """Data structure for critical analysis results"""
    
    def __init__(self, 
                 claim: str,
                 evidence: List[str],
                 assumptions: List[str],
                 counterarguments: List[str],
                 logical_fallacies: List[str],
                 credibility_assessment: str,
                 conclusion: str,
                 confidence_level: float,
                 next_analysis_needed: bool):
        self.claim = claim
        self.evidence = evidence
        self.assumptions = assumptions
        self.counterarguments = counterarguments
        self.logical_fallacies = logical_fallacies
        self.credibility_assessment = credibility_assessment
        self.conclusion = conclusion
        self.confidence_level = confidence_level
        self.next_analysis_needed = next_analysis_needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "claim": self.claim,
            "evidence": self.evidence,
            "assumptions": self.assumptions,
            "counterarguments": self.counterarguments,
            "logical_fallacies": self.logical_fallacies,
            "credibility_assessment": self.credibility_assessment,
            "conclusion": self.conclusion,
            "confidence_level": self.confidence_level,
            "next_analysis_needed": self.next_analysis_needed
        }


class CriticalThinkingProcessor:
    """Processor for critical thinking analysis"""
    
    def __init__(self):
        self.analyses: List[CriticalAnalysis] = []
        self.session_counter = 0
    
    def _validate_critical_data(self, data: Dict[str, Any]) -> CriticalAnalysis:
        """Validate and create CriticalAnalysis from input data"""
        
        # Validate claim
        claim = data.get("claim")
        if not claim or not isinstance(claim, str):
            raise ValueError("Invalid claim: must be a non-empty string")
        
        # Validate evidence
        evidence = data.get("evidence", [])
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise ValueError("Invalid evidence: must be an array of strings")
        
        # Validate assumptions
        assumptions = data.get("assumptions", [])
        if not isinstance(assumptions, list) or not all(isinstance(item, str) for item in assumptions):
            raise ValueError("Invalid assumptions: must be an array of strings")
        
        # Validate counterarguments
        counterarguments = data.get("counterarguments", [])
        if not isinstance(counterarguments, list) or not all(isinstance(item, str) for item in counterarguments):
            raise ValueError("Invalid counterarguments: must be an array of strings")
        
        # Validate logical fallacies
        logical_fallacies = data.get("logical_fallacies", [])
        if not isinstance(logical_fallacies, list) or not all(isinstance(item, str) for item in logical_fallacies):
            raise ValueError("Invalid logical_fallacies: must be an array of strings")
        
        # Validate credibility assessment
        credibility_assessment = data.get("credibility_assessment")
        if not credibility_assessment or not isinstance(credibility_assessment, str):
            raise ValueError("Invalid credibility_assessment: must be a non-empty string")
        
        # Validate conclusion
        conclusion = data.get("conclusion")
        if not conclusion or not isinstance(conclusion, str):
            raise ValueError("Invalid conclusion: must be a non-empty string")
        
        # Validate confidence level
        confidence_level = data.get("confidence_level")
        if not isinstance(confidence_level, (int, float)) or confidence_level < 0 or confidence_level > 100:
            raise ValueError("Invalid confidence_level: must be a number between 0-100")
        
        # Validate next analysis needed
        next_analysis_needed = data.get("next_analysis_needed")
        if not isinstance(next_analysis_needed, bool):
            raise ValueError("Invalid next_analysis_needed: must be a boolean")
        
        return CriticalAnalysis(
            claim=claim,
            evidence=evidence,
            assumptions=assumptions,
            counterarguments=counterarguments,
            logical_fallacies=logical_fallacies,
            credibility_assessment=credibility_assessment,
            conclusion=conclusion,
            confidence_level=float(confidence_level),
            next_analysis_needed=next_analysis_needed
        )
    
    def _format_critical_analysis(self, analysis: CriticalAnalysis) -> str:
        """Format critical analysis for display"""
        
        confidence_level = analysis.confidence_level
        confidence_status = "HIGH" if confidence_level >= 80 else "MEDIUM" if confidence_level >= 60 else "LOW"
        
        formatted_output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🔍 CRITICAL ANALYSIS                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CLAIM: {analysis.claim[:70]}{'...' if len(analysis.claim) > 70 else ''}
║ 
║ EVIDENCE:
"""
        
        for i, evidence in enumerate(analysis.evidence, 1):
            formatted_output += f"║   {i}. {evidence[:70]}{'...' if len(evidence) > 70 else ''}\n"
        
        formatted_output += f"""║ 
║ ASSUMPTIONS:
"""
        
        for i, assumption in enumerate(analysis.assumptions, 1):
            formatted_output += f"║   {i}. {assumption[:70]}{'...' if len(assumption) > 70 else ''}\n"
        
        formatted_output += f"""║ 
║ COUNTER-ARGUMENTS:
"""
        
        for i, counter in enumerate(analysis.counterarguments, 1):
            formatted_output += f"║   {i}. {counter[:70]}{'...' if len(counter) > 70 else ''}\n"
        
        formatted_output += f"""║ 
║ LOGICAL FALLACIES:
"""
        
        for i, fallacy in enumerate(analysis.logical_fallacies, 1):
            formatted_output += f"║   {i}. {fallacy[:70]}{'...' if len(fallacy) > 70 else ''}\n"
        
        formatted_output += f"""║ 
║ CREDIBILITY: {analysis.credibility_assessment[:50]}{'...' if len(analysis.credibility_assessment) > 50 else ''}
║ CONFIDENCE: {confidence_level:.1f}% ({confidence_status})
║ CONCLUSION: {analysis.conclusion[:60]}{'...' if len(analysis.conclusion) > 60 else ''}
║ NEXT ANALYSIS NEEDED: {"YES" if analysis.next_analysis_needed else "NO"}
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return formatted_output
    
    async def process_critical_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process critical thinking analysis"""
        
        try:
            # Validate input data
            validated_analysis = self._validate_critical_data(input_data)
            
            # Store analysis
            self.analyses.append(validated_analysis)
            self.session_counter += 1
            
            # Format analysis for logging
            formatted_analysis = self._format_critical_analysis(validated_analysis)
            logger.info(f"Critical Analysis #{self.session_counter}:\n{formatted_analysis}")
            
            # Create session ID
            session_id = f"critical_{int(datetime.now(timezone.utc).timestamp())}"
            
            # Prepare result
            result = {
                "session_id": session_id,
                "analysis_number": self.session_counter,
                "analysis_data": validated_analysis.to_dict(),
                "analysis_summary": {
                    "claim": validated_analysis.claim,
                    "evidence_count": len(validated_analysis.evidence),
                    "assumptions_count": len(validated_analysis.assumptions),
                    "counterarguments_count": len(validated_analysis.counterarguments),
                    "fallacies_count": len(validated_analysis.logical_fallacies),
                    "confidence_level": validated_analysis.confidence_level,
                    "credibility_rating": self._assess_credibility_rating(validated_analysis.credibility_assessment),
                    "recommendation": self._generate_recommendation(validated_analysis)
                },
                "formatted_display": formatted_analysis,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_analyses": len(self.analyses),
                    "analysis_type": "critical_thinking",
                    "version": "1.0.0"
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in critical thinking analysis: {e}")
            raise ValueError(f"Critical analysis failed: {str(e)}")
    
    def _assess_credibility_rating(self, credibility_assessment: str) -> str:
        """Assess credibility rating from text"""
        assessment_lower = credibility_assessment.lower()
        
        if any(word in assessment_lower for word in ["high", "excellent", "strong", "reliable", "trustworthy"]):
            return "HIGH"
        elif any(word in assessment_lower for word in ["medium", "moderate", "fair", "adequate"]):
            return "MEDIUM"
        elif any(word in assessment_lower for word in ["low", "poor", "weak", "unreliable", "questionable"]):
            return "LOW"
        else:
            return "UNKNOWN"
    
    def _generate_recommendation(self, analysis: CriticalAnalysis) -> str:
        """Generate recommendation based on analysis"""
        confidence = analysis.confidence_level
        evidence_count = len(analysis.evidence)
        fallacies_count = len(analysis.logical_fallacies)
        
        recommendations = []
        
        if confidence < 50:
            recommendations.append("Gather more evidence before drawing conclusions")
        
        if evidence_count < 3:
            recommendations.append("Seek additional supporting evidence")
        
        if fallacies_count > 0:
            recommendations.append("Address identified logical fallacies")
        
        if analysis.next_analysis_needed:
            recommendations.append("Conduct follow-up analysis as indicated")
        
        if len(analysis.counterarguments) == 0:
            recommendations.append("Consider potential counter-arguments")
        
        if not recommendations:
            recommendations.append("Analysis appears comprehensive")
        
        return "; ".join(recommendations)
    
    async def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get history of all analyses"""
        return [analysis.to_dict() for analysis in self.analyses]
    
    async def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about analyses performed"""
        if not self.analyses:
            return {
                "total_analyses": 0,
                "average_confidence": 0.0,
                "most_common_fallacies": [],
                "credibility_distribution": {}
            }
        
        total_analyses = len(self.analyses)
        average_confidence = sum(a.confidence_level for a in self.analyses) / total_analyses
        
        # Count fallacies
        fallacy_counts = {}
        for analysis in self.analyses:
            for fallacy in analysis.logical_fallacies:
                fallacy_counts[fallacy] = fallacy_counts.get(fallacy, 0) + 1
        
        most_common_fallacies = sorted(fallacy_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Credibility distribution
        credibility_counts = {}
        for analysis in self.analyses:
            rating = self._assess_credibility_rating(analysis.credibility_assessment)
            credibility_counts[rating] = credibility_counts.get(rating, 0) + 1
        
        return {
            "total_analyses": total_analyses,
            "average_confidence": round(average_confidence, 2),
            "most_common_fallacies": most_common_fallacies,
            "credibility_distribution": credibility_counts
        }


# Global critical thinking processor instance
_critical_thinking_processor = None


def get_critical_thinking_processor() -> CriticalThinkingProcessor:
    """Get the global critical thinking processor instance"""
    global _critical_thinking_processor
    if _critical_thinking_processor is None:
        _critical_thinking_processor = CriticalThinkingProcessor()
    return _critical_thinking_processor


# Convenience functions for external use
async def critical_thinking_analysis(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform critical thinking analysis"""
    processor = get_critical_thinking_processor()
    return await processor.process_critical_analysis(analysis_data)


async def get_critical_analysis_history() -> List[Dict[str, Any]]:
    """Get history of critical analyses"""
    processor = get_critical_thinking_processor()
    return await processor.get_analysis_history()


async def get_critical_analysis_stats() -> Dict[str, Any]:
    """Get statistics about critical analyses"""
    processor = get_critical_thinking_processor()
    return await processor.get_analysis_stats()
