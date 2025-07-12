# -*- coding: utf-8 -*-
# app/sequential.py
# Sequential Thinking Logic Module

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from app.logger import get_logger

logger = get_logger(__name__)


class SequentialThinking:
    """
    Sequential Thinking processor - handles step-by-step reasoning and analysis
    """
    
    def __init__(self):
        self.thinking_steps: List[Dict[str, Any]] = []
        self.session_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        
    async def process_sequential_thinking(
        self, 
        problem: str, 
        context: Optional[Dict[str, Any]] = None,
        max_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Process a problem using sequential thinking approach
        
        Args:
            problem: The problem statement to analyze
            context: Additional context information
            max_steps: Maximum number of thinking steps
            
        Returns:
            Dict containing the complete thinking process and result
        """
        self.start_time = datetime.now(timezone.utc)
        self.session_id = f"seq_{int(self.start_time.timestamp())}"
        self.thinking_steps = []
        
        logger.info(f"Starting sequential thinking session: {self.session_id}")
        
        try:
            # Step 1: Problem Analysis
            await self._add_thinking_step(
                "Problem Analysis",
                f"Analyzing the given problem: {problem}",
                {"original_problem": problem, "context": context}
            )
            
            # Step 2: Break down the problem
            breakdown = await self._break_down_problem(problem)
            await self._add_thinking_step(
                "Problem Breakdown",
                "Breaking down the problem into smaller components",
                breakdown
            )
            
            # Step 3: Identify key concepts
            key_concepts = await self._identify_key_concepts(problem, breakdown)
            await self._add_thinking_step(
                "Key Concepts Identification",
                "Identifying key concepts and relationships",
                key_concepts
            )
            
            # Step 4: Generate potential approaches
            approaches = await self._generate_approaches(problem, key_concepts)
            await self._add_thinking_step(
                "Approach Generation",
                "Generating potential solution approaches",
                approaches
            )
            
            # Step 5: Evaluate approaches
            evaluation = await self._evaluate_approaches(approaches, context)
            await self._add_thinking_step(
                "Approach Evaluation",
                "Evaluating and ranking potential approaches",
                evaluation
            )
            
            # Step 6: Select best approach
            selected_approach = await self._select_best_approach(evaluation)
            await self._add_thinking_step(
                "Approach Selection",
                "Selecting the most promising approach",
                selected_approach
            )
            
            # Step 7: Execute solution
            solution = await self._execute_solution(selected_approach, problem)
            await self._add_thinking_step(
                "Solution Execution",
                "Executing the selected approach to solve the problem",
                solution
            )
            
            # Step 8: Validate solution
            validation = await self._validate_solution(solution, problem)
            await self._add_thinking_step(
                "Solution Validation",
                "Validating the proposed solution",
                validation
            )
            
            # Generate final result
            final_result = await self._generate_final_result()
            
            return {
                "session_id": self.session_id,
                "problem": problem,
                "context": context,
                "thinking_process": {
                    "steps": self.thinking_steps,
                    "total_steps": len(self.thinking_steps),
                    "duration_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
                },
                "result": final_result,
                "metadata": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": datetime.now(timezone.utc).isoformat(),
                    "method": "sequential_thinking",
                    "version": "1.0.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sequential thinking process: {e}")
            await self._add_thinking_step(
                "Error",
                f"An error occurred during processing: {str(e)}",
                {"error_type": type(e).__name__, "error_message": str(e)}
            )
            raise
    
    async def _add_thinking_step(
        self, 
        step_name: str, 
        description: str, 
        details: Dict[str, Any]
    ) -> None:
        """Add a thinking step to the process"""
        step = {
            "step_number": len(self.thinking_steps) + 1,
            "step_name": step_name,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details
        }
        self.thinking_steps.append(step)
        logger.debug(f"Added thinking step: {step_name}")
        
        # Simulate thinking time
        await asyncio.sleep(0.1)
    
    async def _break_down_problem(self, problem: str) -> Dict[str, Any]:
        """Break down the problem into components"""
        # Simple heuristic-based breakdown
        words = problem.lower().split()
        
        # Identify question types
        question_indicators = ["what", "how", "why", "when", "where", "who", "which"]
        question_type = next((word for word in words if word in question_indicators), "unknown")
        
        # Identify domain indicators
        domain_indicators = {
            "math": ["calculate", "compute", "number", "equation", "formula"],
            "logic": ["if", "then", "because", "therefore", "logical"],
            "analysis": ["analyze", "compare", "evaluate", "assess"],
            "creative": ["design", "create", "generate", "brainstorm"]
        }
        
        domains = []
        for domain, indicators in domain_indicators.items():
            if any(indicator in problem.lower() for indicator in indicators):
                domains.append(domain)
        
        return {
            "problem_type": question_type,
            "estimated_domains": domains if domains else ["general"],
            "word_count": len(words),
            "complexity_estimate": "low" if len(words) < 10 else "medium" if len(words) < 20 else "high",
            "components": words[:10]  # First 10 words as components
        }
    
    async def _identify_key_concepts(
        self, 
        problem: str, 
        breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify key concepts from the problem"""
        # Extract key concepts based on problem analysis
        concepts = []
        
        # Add domain-specific concepts
        for domain in breakdown.get("estimated_domains", []):
            concepts.append(f"{domain}_reasoning")
        
        # Add question-type specific concepts
        question_type = breakdown.get("problem_type", "unknown")
        if question_type != "unknown":
            concepts.append(f"{question_type}_inquiry")
        
        return {
            "identified_concepts": concepts,
            "relationships": [f"{concepts[i]} -> {concepts[i+1]}" for i in range(len(concepts)-1)],
            "primary_concept": concepts[0] if concepts else "general_analysis"
        }
    
    async def _generate_approaches(
        self, 
        problem: str, 
        key_concepts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate potential solution approaches"""
        approaches = []
        
        # Generate different approaches based on concepts
        for concept in key_concepts.get("identified_concepts", []):
            if "math" in concept:
                approaches.append({
                    "name": "Mathematical Analysis",
                    "description": "Apply mathematical reasoning and computation",
                    "steps": ["Identify variables", "Set up equations", "Solve systematically"]
                })
            elif "logic" in concept:
                approaches.append({
                    "name": "Logical Reasoning",
                    "description": "Use logical deduction and inference",
                    "steps": ["Identify premises", "Apply logical rules", "Draw conclusions"]
                })
            elif "creative" in concept:
                approaches.append({
                    "name": "Creative Problem Solving",
                    "description": "Use creative thinking and brainstorming",
                    "steps": ["Generate ideas", "Combine concepts", "Iterate solutions"]
                })
        
        # Always add a general approach
        approaches.append({
            "name": "Systematic Analysis",
            "description": "Use systematic step-by-step analysis",
            "steps": ["Gather information", "Analyze patterns", "Synthesize solution"]
        })
        
        return {
            "generated_approaches": approaches,
            "approach_count": len(approaches),
            "recommended_parallel": min(3, len(approaches))
        }
    
    async def _evaluate_approaches(
        self, 
        approaches: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate the generated approaches"""
        evaluations = []
        
        for i, approach in enumerate(approaches.get("generated_approaches", [])):
            # Simple scoring based on approach characteristics
            score = 5.0  # Base score
            
            # Adjust score based on approach type
            if "Mathematical" in approach["name"]:
                score += 2.0  # Math is often precise
            if "Systematic" in approach["name"]:
                score += 1.5  # Systematic is reliable
            if "Creative" in approach["name"]:
                score += 1.0  # Creative can be innovative
            
            # Adjust for number of steps (simpler might be better)
            step_count = len(approach.get("steps", []))
            if step_count <= 3:
                score += 1.0
            elif step_count > 5:
                score -= 0.5
            
            evaluations.append({
                "approach": approach["name"],
                "score": round(score, 1),
                "pros": [f"Strength in {approach['description'].lower()}"],
                "cons": [f"May be limited in scope"],
                "feasibility": "high" if score > 6 else "medium" if score > 4 else "low"
            })
        
        # Sort by score
        evaluations.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "evaluations": evaluations,
            "top_approach": evaluations[0] if evaluations else None,
            "evaluation_criteria": ["accuracy", "feasibility", "efficiency", "completeness"]
        }
    
    async def _select_best_approach(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best approach based on evaluation"""
        top_approach = evaluation.get("top_approach")
        
        if not top_approach:
            return {
                "selected_approach": "Systematic Analysis",
                "reason": "Default fallback approach",
                "confidence": 0.5
            }
        
        return {
            "selected_approach": top_approach["approach"],
            "reason": f"Highest score ({top_approach['score']}) with {top_approach['feasibility']} feasibility",
            "confidence": min(top_approach["score"] / 10.0, 1.0),
            "expected_outcome": "Comprehensive solution"
        }
    
    async def _execute_solution(
        self, 
        selected_approach: Dict[str, Any], 
        problem: str
    ) -> Dict[str, Any]:
        """Execute the selected solution approach"""
        approach_name = selected_approach.get("selected_approach", "Systematic Analysis")
        
        # Simulate solution execution based on approach
        if "Mathematical" in approach_name:
            solution = {
                "type": "mathematical",
                "steps": [
                    "Identified numerical components in the problem",
                    "Applied appropriate mathematical operations",
                    "Computed final result"
                ],
                "result": "Mathematical solution derived through systematic computation"
            }
        elif "Logical" in approach_name:
            solution = {
                "type": "logical",
                "steps": [
                    "Established logical premises from the problem",
                    "Applied deductive reasoning rules",
                    "Reached logical conclusion"
                ],
                "result": "Logical conclusion based on sound reasoning"
            }
        elif "Creative" in approach_name:
            solution = {
                "type": "creative",
                "steps": [
                    "Generated multiple creative alternatives",
                    "Combined innovative concepts",
                    "Synthesized novel solution"
                ],
                "result": "Creative solution combining novel approaches"
            }
        else:
            solution = {
                "type": "systematic",
                "steps": [
                    "Systematically analyzed problem components",
                    "Identified patterns and relationships",
                    "Synthesized comprehensive solution"
                ],
                "result": "Systematic solution addressing all problem aspects"
            }
        
        return {
            "solution": solution,
            "execution_method": approach_name,
            "completion_status": "success",
            "execution_time": "simulated"
        }
    
    async def _validate_solution(
        self, 
        solution: Dict[str, Any], 
        problem: str
    ) -> Dict[str, Any]:
        """Validate the proposed solution"""
        # Simple validation checks
        checks = []
        
        # Check if solution exists
        if solution.get("solution"):
            checks.append({
                "check": "Solution Completeness",
                "status": "pass",
                "details": "Solution was generated successfully"
            })
        else:
            checks.append({
                "check": "Solution Completeness", 
                "status": "fail",
                "details": "No solution was generated"
            })
        
        # Check if solution has steps
        steps = solution.get("solution", {}).get("steps", [])
        if len(steps) > 0:
            checks.append({
                "check": "Solution Detail",
                "status": "pass",
                "details": f"Solution includes {len(steps)} detailed steps"
            })
        else:
            checks.append({
                "check": "Solution Detail",
                "status": "fail", 
                "details": "Solution lacks detailed steps"
            })
        
        # Check if solution has result
        result = solution.get("solution", {}).get("result")
        if result:
            checks.append({
                "check": "Solution Result",
                "status": "pass",
                "details": "Solution includes clear result statement"
            })
        else:
            checks.append({
                "check": "Solution Result",
                "status": "fail",
                "details": "Solution lacks clear result"
            })
        
        passed_checks = len([c for c in checks if c["status"] == "pass"])
        total_checks = len(checks)
        
        return {
            "validation_checks": checks,
            "validation_score": passed_checks / total_checks if total_checks > 0 else 0,
            "overall_status": "valid" if passed_checks == total_checks else "needs_improvement",
            "recommendations": ["Consider adding more detail", "Verify solution completeness"] if passed_checks < total_checks else ["Solution validated successfully"]
        }
    
    async def _generate_final_result(self) -> Dict[str, Any]:
        """Generate the final result summary"""
        if not self.thinking_steps:
            return {
                "summary": "No thinking steps completed",
                "conclusion": "Process was incomplete",
                "confidence": 0.0
            }
        
        # Extract key information from thinking steps
        solution_step = next((step for step in self.thinking_steps if step["step_name"] == "Solution Execution"), None)
        validation_step = next((step for step in self.thinking_steps if step["step_name"] == "Solution Validation"), None)
        
        if solution_step and validation_step:
            solution_details = solution_step["details"]
            validation_details = validation_step["details"]
            
            return {
                "summary": f"Completed sequential thinking process with {len(self.thinking_steps)} steps",
                "conclusion": solution_details.get("solution", {}).get("result", "Solution generated"),
                "confidence": validation_details.get("validation_score", 0.8),
                "method_used": solution_details.get("execution_method", "Unknown"),
                "validation_status": validation_details.get("overall_status", "unknown"),
                "recommendations": validation_details.get("recommendations", [])
            }
        
        return {
            "summary": f"Partial completion with {len(self.thinking_steps)} steps",
            "conclusion": "Process completed with limited results", 
            "confidence": 0.5
        }


# Helper functions for external use
async def think_sequentially(
    problem: str, 
    context: Optional[Dict[str, Any]] = None,
    max_steps: int = 10
) -> Dict[str, Any]:
    """
    Convenience function to perform sequential thinking
    
    Args:
        problem: Problem statement to analyze
        context: Additional context
        max_steps: Maximum thinking steps
        
    Returns:
        Complete thinking process result
    """
    thinking_processor = SequentialThinking()
    return await thinking_processor.process_sequential_thinking(problem, context, max_steps)


async def quick_analysis(problem: str) -> Dict[str, Any]:
    """
    Quick analysis function for simple problems
    
    Args:
        problem: Problem to analyze quickly
        
    Returns:
        Simplified analysis result
    """
    return await think_sequentially(problem, max_steps=5)
