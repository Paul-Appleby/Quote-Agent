import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from database import SalesDatabase

class WorkflowNode:
    def __init__(self, node_data: Dict[str, Any]):
        self.id = node_data['id']
        self.name = node_data['data'].get('name', '')
        self.prompt = node_data['data'].get('prompt', '')
        self.node_type = node_data['type']
        self.routes = node_data['data'].get('routes', [])
        self.model_options = node_data['data'].get('modelOptions', {})
        
    def get_temperature(self) -> float:
        return self.model_options.get('newTemperature', 0.2)

class WorkflowAgent:
    def __init__(self, workflow_file: str):
        self.workflow_file = workflow_file
        self.nodes = {}
        self.edges = []
        self.global_config = {}
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.db = SalesDatabase()
        self.load_workflow()
    
    def load_workflow(self):
        """Load the workflow from JSON file"""
        with open(self.workflow_file, 'r') as f:
            data = json.load(f)
        
        # Load nodes
        for node_data in data['nodes']:
            if 'id' in node_data:  # Skip global config
                node = WorkflowNode(node_data)
                self.nodes[node.id] = node
        
        # Load edges
        self.edges = data.get('edges', [])
        
        # Load global config
        for node_data in data['nodes']:
            if 'globalConfig' in node_data:
                self.global_config = node_data['globalConfig']
    
    def get_start_node(self) -> Optional[WorkflowNode]:
        """Find the start node"""
        for node in self.nodes.values():
            if node.node_type == 'Webhook' and node.name == 'GET User Info':
                return node
        return None
    
    def evaluate_route_conditions(self, conditions: list, context: Dict[str, Any]) -> bool:
        """Evaluate routing conditions"""
        for condition in conditions:
            field = condition.get('field')
            value = condition.get('value')
            operator = condition.get('operator')
            
            context_value = context.get(field)
            
            if operator == 'equals':
                if str(context_value) != str(value):
                    return False
            elif operator == 'greater than':
                if context_value is None or context_value <= value:
                    return False
        
        return True
    
    def get_next_node(self, current_node: WorkflowNode, context: Dict[str, Any]) -> Optional[WorkflowNode]:
        """Determine the next node based on routing logic"""
        if current_node.node_type == 'Route':
            for route in current_node.routes:
                conditions = route.get('conditions', [])
                if self.evaluate_route_conditions(conditions, context):
                    target_id = route.get('targetNodeId')
                    return self.nodes.get(target_id)
        
        # For non-route nodes, follow edges
        for edge in self.edges:
            if edge['source'] == current_node.id:
                target_id = edge['target']
                return self.nodes.get(target_id)
        
        return None
    
    def execute_node(self, node: WorkflowNode, context: Dict[str, Any], messages: list) -> str:
        """Execute a workflow node and return the response"""
        
        if node.node_type == 'Webhook':
            # Webhook nodes typically just pass through
            return "Webhook processed"
        
        elif node.node_type == 'Route':
            # Route nodes determine next step
            return "Routing to next node"
        
        elif node.node_type == 'Default':
            # Default nodes generate AI responses
            if not node.prompt:
                return "No prompt configured for this node"
            
            # Build the full prompt with context
            full_prompt = f"""
{self.global_config.get('globalPrompt', '')}

{node.prompt}

Current context:
- Customer ID: {context.get('customer_id', 'Unknown')}
- Pipeline Stage: {context.get('pipeline_stage', 'Unknown')}
- Current Message: {context.get('current_message', '')}

Previous conversation:
{self._format_conversation_history(messages)}

Please respond to the customer's message.
"""
            
            # Generate response
            response = self.llm.invoke([
                HumanMessage(content=full_prompt)
            ])
            
            return response.content
        
        return "Unknown node type"
    
    def _format_conversation_history(self, messages: list) -> str:
        """Format conversation history for context"""
        if not messages:
            return "No previous conversation."
        
        formatted = []
        for msg in messages[-5:]:  # Last 5 messages
            role = "Customer" if msg["role"] == "user" else "Agent"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def process_message(self, customer_id: str, message: str, pipeline_stage: str = "New Lead") -> Dict[str, Any]:
        """Process an incoming message through the workflow"""
        
        # Get or create conversation
        conversation_id = self.db.get_or_create_conversation(customer_id, pipeline_stage)
        
        # Load existing state
        existing_state = self.db.load_conversation_state(conversation_id)
        
        # Initialize context
        context = {
            'customer_id': customer_id,
            'pipeline_stage': pipeline_stage,
            'current_message': message,
            'pipe_status': 'Open' if pipeline_stage == 'New Lead' else 'Won',
            'pipeline_status': pipeline_stage
        }
        
        # Load or create messages
        if existing_state:
            messages = existing_state.messages
            current_node_id = existing_state.current_node
        else:
            messages = []
            current_node_id = None
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Find start node if needed
        if not current_node_id:
            start_node = self.get_start_node()
            if start_node:
                current_node_id = start_node.id
            else:
                return {"error": "No start node found in workflow"}
        
        # Execute workflow
        current_node = self.nodes.get(current_node_id)
        if not current_node:
            return {"error": f"Node {current_node_id} not found"}
        
        # Execute current node
        response = self.execute_node(current_node, context, messages)
        
        # Add AI response to messages
        messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Find next node
        next_node = self.get_next_node(current_node, context)
        next_node_id = next_node.id if next_node else None
        
        # Save state
        from agent import ConversationState
        state = ConversationState(
            customer_id=customer_id,
            pipeline_stage=pipeline_stage,
            current_node=next_node_id or current_node_id,
            context=context,
            messages=messages
        )
        
        self.db.save_conversation_state(conversation_id, state)
        
        return {
            'success': True,
            'response': response,
            'next_node': next_node_id,
            'pipeline_stage': pipeline_stage,
            'conversation_id': conversation_id
        }

def main():
    """Test the workflow agent"""
    workflow_file = "WAXD Inbound Call - 36e52fcb-543b-40a2-a82e-bb8bd2407dc3.json"
    
    if not os.path.exists(workflow_file):
        print(f"Workflow file {workflow_file} not found!")
        print("Please place the workflow JSON file in the current directory.")
        return
    
    agent = WorkflowAgent(workflow_file)
    
    print("=== WAXD Workflow Agent Test ===")
    print("Type 'exit' to quit")
    
    while True:
        message = input("\nCustomer: ")
        if message.lower() == 'exit':
            break
        
        result = agent.process_message(
            customer_id="test_customer_123",
            message=message,
            pipeline_stage="New Lead"
        )
        
        if result.get('success'):
            print(f"\nAgent: {result['response']}")
            print(f"Next Node: {result['next_node']}")
            print(f"Pipeline: {result['pipeline_stage']}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 