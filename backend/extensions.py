"""
Shared extension instances and service singletons for Adaptive E-Learning System.
"""
from knowledge_tracker import KnowledgeTracker
from llm_service import LLMService
from agents.coordinator_agent import CoordinatorAgent

knowledge_tracker = KnowledgeTracker()
llm_service = LLMService()
coordinator = CoordinatorAgent()

def update_bkt_mastery(current_mastery, is_correct, difficulty="beginner"):
    """
    Dynamic Bayesian Knowledge Tracing updating helper.
    Delegates to KnowledgeTracker core BKT Bayesian probability engine.
    """
    return knowledge_tracker.update_bkt_step(current_mastery, is_correct, difficulty=difficulty)
