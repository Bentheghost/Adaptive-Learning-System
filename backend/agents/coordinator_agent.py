"""
Coordinator Agent - Orchestrates all other agents
"""
from agents.base_agent import BaseAgent
from datetime import datetime

class CoordinatorAgent(BaseAgent):
    """Coordinates all agent activities and tracks performance"""
    
    def __init__(self):
        super().__init__("CA-001", "CoordinatorAgent")
        self.agents = {}
        self.active_agents = []
        self.total_tasks_coordinated = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        
    def perceive(self, environment):
        """Perceive task requirements"""
        self.update_state("perceiving")
        self.context = environment.get('context', {})
        self.task = environment.get('task')
        self.user_id = environment.get('user_id')
        
        # Inject necessary properties into context for child agents
        self.context['task'] = self.task
        self.context['user_id'] = self.user_id
        if 'message' in environment:
            self.context['message'] = environment['message']
        if 'history' in environment:
            self.context['history'] = environment['history']
            
        self.log(f"Task: {self.task}")
        
        return self
    
    def decide(self):
        """Decide which agents to activate"""
        self.update_state("deciding")
        
        if self.task == 'generate_lesson':
            self.active_agents = ['TeachingAgent']
        elif self.task == 'generate_review':
            self.active_agents = ['TeachingAgent']
        elif self.task == 'generate_quiz':
            self.active_agents = ['AssessmentAgent']
        elif self.task == 'recommend_topic':
            self.active_agents = ['RecommendationAgent']
        elif self.task == 'analyze_knowledge':
            self.active_agents = ['KnowledgeAgent']
        elif self.task in ['provide_hint', 'chat']:
            self.active_agents = ['TutorAgent']
        else:
            self.active_agents = []
        
        self.log(f"Activating agents: {self.active_agents}")
        
        return self
    
    def act(self):
        """Execute agent tasks"""
        self.update_state("acting")
        self.total_tasks_coordinated += 1
        
        results = {}
        success = True
        
        try:
            for agent_name in self.active_agents:
                if agent_name == 'TeachingAgent':
                    from agents.teaching_agent import TeachingAgent
                    agent = TeachingAgent()
                    result = agent.perceive(self.context).decide().act()
                    results[agent_name] = result
                    
                    # Track agent stats
                    if agent_name not in self.agents:
                        self.agents[agent_name] = {'tasks': 0, 'errors': 0}
                    self.agents[agent_name]['tasks'] += 1
                    if 'error' in result:
                        self.agents[agent_name]['errors'] += 1
                        
                elif agent_name == 'AssessmentAgent':
                    from agents.assessment_agent import AssessmentAgent
                    agent = AssessmentAgent()
                    result = agent.perceive(self.context).decide().act()
                    results[agent_name] = result
                    
                    if agent_name not in self.agents:
                        self.agents[agent_name] = {'tasks': 0, 'errors': 0}
                    self.agents[agent_name]['tasks'] += 1
                    if 'error' in result:
                        self.agents[agent_name]['errors'] += 1
                        
                elif agent_name == 'RecommendationAgent':
                    from agents.recommendation_agent import RecommendationAgent
                    agent = RecommendationAgent()
                    result = agent.perceive(self.context).decide().act()
                    results[agent_name] = result
                    
                    if agent_name not in self.agents:
                        self.agents[agent_name] = {'tasks': 0, 'errors': 0}
                    self.agents[agent_name]['tasks'] += 1
                        
                elif agent_name == 'KnowledgeAgent':
                    from agents.knowledge_agent import KnowledgeAgent
                    agent = KnowledgeAgent()
                    result = agent.perceive(self.context).decide().act()
                    results[agent_name] = result
                    
                    if agent_name not in self.agents:
                        self.agents[agent_name] = {'tasks': 0, 'errors': 0}
                    self.agents[agent_name]['tasks'] += 1
                        
                elif agent_name == 'TutorAgent':
                    from agents.tutor_agent import TutorAgent
                    agent = TutorAgent()
                    result = agent.perceive(self.context).decide().act()
                    results[agent_name] = result
                    
                    if agent_name not in self.agents:
                        self.agents[agent_name] = {'tasks': 0, 'errors': 0}
                    self.agents[agent_name]['tasks'] += 1
                    if 'error' in result:
                        self.agents[agent_name]['errors'] += 1
            
            self.successful_tasks += 1
            
        except Exception as e:
            self.log(f"Error in coordination: {str(e)}", "error")
            self.failed_tasks += 1
            success = False
            results['error'] = str(e)
        
        self.update_state("completed")
        
        return {
            "success": success,
            "results": results,
            "agent": self.name
        }
    
    def get_agent_status(self):
        """Get status of all agents"""
        return {
            "coordinator": {
                "name": self.name,
                "state": self.state,
                "active_agents": self.active_agents,
                "total_tasks": self.total_tasks_coordinated,
                "successful": self.successful_tasks,
                "failed": self.failed_tasks,
                "success_rate": round((self.successful_tasks / self.total_tasks_coordinated * 100) if self.total_tasks_coordinated > 0 else 0, 1)
            },
            "agents": self.agents
        }
    
    def get_comprehensive_stats(self):
        """Get detailed statistics for all agents"""
        stats = []
        
        # Get individual agent statistics
        agent_classes = {
            'TeachingAgent': 'Content Generation',
            'AssessmentAgent': 'Quiz Generation',
            'RecommendationAgent': 'Learning Path',
            'KnowledgeAgent': 'Progress Tracking'
        }
        
        for agent_name, description in agent_classes.items():
            agent_data = self.agents.get(agent_name, {'tasks': 0, 'errors': 0})
            
            stats.append({
                'name': agent_name,
                'description': description,
                'status': 'active' if agent_name in self.active_agents else 'idle',
                'total_tasks': agent_data.get('tasks', 0),
                'errors': agent_data.get('errors', 0),
                'success_rate': round(((agent_data.get('tasks', 0) - agent_data.get('errors', 0)) / agent_data.get('tasks', 1) * 100) if agent_data.get('tasks', 0) > 0 else 100, 1)
            })
        
        return stats