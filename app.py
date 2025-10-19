"""
TutorBee - Smart Business Agent
Deployable version for HuggingFace Spaces
"""

import os
import json
import gradio as gr
from openai import OpenAI
from datetime import datetime
from typing import Dict, List, Any
import PyPDF2

# =============================================================================
# 1. LOAD BUSINESS INFORMATION
# =============================================================================

def load_business_context():
    """
    Load business information from uploaded files.
    """
    context = ""
    
    # Load text summary
    try:
        with open('me/business_summary.txt', 'r', encoding='utf-8') as f:
            context += f.read() + "\n\n"
        print("✅ Loaded business_summary.txt")
    except FileNotFoundError:
        print("⚠️ business_summary.txt not found")
        context += "TutorBee - Interactive Tutoring Service\n\n"
    
    # Load PDF content
    try:
        with open('me/about_business.pdf', 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            context += "Additional Business Information:\n" + pdf_text
        print("✅ Loaded about_business.pdf")
    except FileNotFoundError:
        print("⚠️ about_business.pdf not found")
    
    return context

BUSINESS_CONTEXT = load_business_context()

# =============================================================================
# 2. TOOL FUNCTIONS
# =============================================================================

# Storage for leads and feedback
leads_database = []
feedback_database = []

def record_customer_interest(email: str, name: str, message: str) -> str:
    """
    Record customer lead information.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lead_entry = {
        "timestamp": timestamp,
        "name": name,
        "email": email,
        "message": message
    }
    
    leads_database.append(lead_entry)
    
    # Log to console
    print("\n" + "="*50)
    print("📝 NEW LEAD RECORDED")
    print("="*50)
    print(f"Timestamp: {timestamp}")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Message: {message}")
    print("="*50 + "\n")
    
    # Save to file
    try:
        with open('leads_log.json', 'w') as f:
            json.dump(leads_database, f, indent=2)
    except:
        pass
    
    return f"Thank you, {name}! Your interest has been recorded. We'll contact you at {email} soon."


def record_feedback(question: str) -> str:
    """
    Record unanswered questions or customer feedback.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    feedback_entry = {
        "timestamp": timestamp,
        "question": question
    }
    
    feedback_database.append(feedback_entry)
    
    # Log to console
    print("\n" + "="*50)
    print("💬 FEEDBACK/UNANSWERED QUESTION RECORDED")
    print("="*50)
    print(f"Timestamp: {timestamp}")
    print(f"Question: {question}")
    print("="*50 + "\n")
    
    # Save to file
    try:
        with open('feedback_log.json', 'w') as f:
            json.dump(feedback_database, f, indent=2)
    except:
        pass
    
    return "Thank you for your question. I've recorded it and our team will review it to improve our service."

# =============================================================================
# 3. TOOL SCHEMAS
# =============================================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "record_customer_interest",
            "description": "Record a customer's contact information and interest in TutorBee services. Use this when a customer wants to sign up, get more information, or schedule a session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The customer's email address"
                    },
                    "name": {
                        "type": "string",
                        "description": "The customer's full name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Additional notes about what the customer is interested in or their specific needs"
                    }
                },
                "required": ["email", "name", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_feedback",
            "description": "Record questions that you cannot answer or customer feedback for future improvement. Use this when you don't have enough information to answer a customer's question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The unanswered question or feedback from the customer"
                    }
                },
                "required": ["question"]
            }
        }
    }
]

# =============================================================================
# 4. TUTORBEE AGENT CLASS
# =============================================================================

class TutorBeeAgent:
    """
    Smart agent for TutorBee business interactions using OpenAI.
    """
    
    def __init__(self, api_key: str, business_context: str):
        """
        Initialize the TutorBee agent.
        """
        # Initialize OpenAI client with API key only
        self.client = OpenAI(api_key=api_key)
        self.business_context = business_context
        self.conversation_history = []
        
        # System prompt
        self.system_prompt = f"""You are Alex, a friendly and professional customer service representative for TutorBee, an AI-powered interactive tutoring service.

CRITICAL: You must ALWAYS stay in character as a TutorBee representative. Never break character or reveal that you are an AI language model.

Your role and responsibilities:
1. Answer questions about TutorBee using ONLY the information provided in the business documentation below
2. Help potential customers understand how TutorBee can transform their learning journey
3. Proactively encourage interested visitors to leave their contact information
4. Use the record_feedback tool for ANY question you cannot answer from the provided information

Business Information (THIS IS YOUR ONLY SOURCE OF TRUTH):
{self.business_context}

Behavioral Guidelines:
- Stay in character as "Alex from TutorBee" - you work here and are passionate about education
- Be warm, conversational, enthusiastic, and genuinely helpful
- Use the business information above to answer ALL questions - do not make up information
- If asked about pricing, features, policies, or anything NOT in the documentation, use record_feedback tool immediately
- Proactively ask for contact details when customers show ANY interest (questions about features, pricing, scheduling, etc.)

Lead Collection Strategy:
- When a customer asks multiple questions or shows sustained interest, say something like: "I'd love to help you get started! May I have your name and email so we can send you personalized information?"
- When someone asks about signing up, pricing, or scheduling: "Great! Let me collect your details so our team can reach out. What's your name and email?"
- Make it natural and helpful, not pushy

Unknown Question Protocol:
- If you don't know the answer from the business information provided, immediately say: "That's a great question! I don't have that specific information right now, but let me record this for our team to follow up with you."
- Then use the record_feedback tool to log it
- NEVER make up information not in the business documentation

Response Style:
- Keep responses concise (2-4 sentences typically)
- Use emojis sparingly to add warmth (🐝, 📚, ✨, 🎯)
- Be professional yet personable
- Show genuine excitement about helping students succeed
"""
        
        # Initialize chat history
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and return agent response.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.conversation_history,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Check for tool calls
        if assistant_message.tool_calls:
            self.conversation_history.append(assistant_message)
            
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute function
                if function_name == "record_customer_interest":
                    function_response = record_customer_interest(
                        email=function_args.get("email"),
                        name=function_args.get("name"),
                        message=function_args.get("message")
                    )
                elif function_name == "record_feedback":
                    function_response = record_feedback(
                        question=function_args.get("question")
                    )
                else:
                    function_response = "Function not found."
                
                # Add function response to history
                self.conversation_history.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })
            
            # Get final response
            second_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.conversation_history
            )
            
            final_message = second_response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": final_message
            })
            
            return final_message
        else:
            # No tool call - return direct response
            response_text = assistant_message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            return response_text
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = [{
            "role": "system",
            "content": self.system_prompt
        }]

# =============================================================================
# 5. GRADIO INTERFACE
# =============================================================================

# Initialize agent (will be set up when API key is provided)
agent = None

def initialize_agent(api_key):
    """Initialize the agent with API key."""
    global agent
    if not api_key:
        return "⚠️ Please enter your OpenAI API key."
    
    try:
        agent = TutorBeeAgent(api_key, BUSINESS_CONTEXT)
        return "✅ Agent initialized successfully! You can start chatting."
    except Exception as e:
        return f"❌ Error initializing agent: {str(e)}"

def chat_with_agent(message, history):
    """Chat wrapper for Gradio."""
    if agent is None:
        return "⚠️ Please initialize the agent first by entering your OpenAI API key above."
    
    try:
        response = agent.chat(message)
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"

def view_leads():
    """Display collected leads."""
    if not leads_database:
        return "No leads collected yet."
    
    output = "## 📝 Collected Leads\n\n"
    for i, lead in enumerate(leads_database, 1):
        output += f"**Lead #{i}**\n"
        output += f"- **Time:** {lead['timestamp']}\n"
        output += f"- **Name:** {lead['name']}\n"
        output += f"- **Email:** {lead['email']}\n"
        output += f"- **Message:** {lead['message']}\n\n"
    return output

def view_feedback():
    """Display collected feedback."""
    if not feedback_database:
        return "No feedback recorded yet."
    
    output = "## 💬 Recorded Feedback\n\n"
    for i, feedback in enumerate(feedback_database, 1):
        output += f"**Feedback #{i}**\n"
        output += f"- **Time:** {feedback['timestamp']}\n"
        output += f"- **Question:** {feedback['question']}\n\n"
    return output

# =============================================================================
# 6. CREATE GRADIO APP
# =============================================================================

with gr.Blocks(title="TutorBee Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🐝 Welcome to TutorBee!
        ### Your AI-Powered Interactive Tutoring Service
        
        Ask me anything about our services, team, or how we can help you succeed!
        """
    )
    
    # API Key section
    with gr.Row():
        api_key_input = gr.Textbox(
            label="OpenAI API Key",
            placeholder="Enter your OpenAI API key (sk-...)",
            type="password"
        )
        init_btn = gr.Button("Initialize Agent", variant="primary")
    
    init_status = gr.Markdown("")
    
    init_btn.click(
        fn=initialize_agent,
        inputs=[api_key_input],
        outputs=[init_status]
    )
    
    # Main interface
    with gr.Tab("💬 Chat"):
        chatbot = gr.ChatInterface(
            fn=chat_with_agent,
            examples=[
                "What services does TutorBee offer?",
                "Tell me about your team",
                "How does the AI tutoring assistant work?",
                "I'm interested in signing up for math tutoring",
                "What makes TutorBee different from other tutoring platforms?"
            ],
            title="Chat with Alex from TutorBee"
        )
    
    with gr.Tab("📊 Analytics"):
        gr.Markdown("## View Collected Data")
        
        with gr.Row():
            leads_btn = gr.Button("View Leads", variant="primary")
            feedback_btn = gr.Button("View Feedback", variant="secondary")
        
        output_display = gr.Markdown()
        
        leads_btn.click(fn=view_leads, outputs=output_display)
        feedback_btn.click(fn=view_feedback, outputs=output_display)
    
    with gr.Tab("ℹ️ About"):
        gr.Markdown(
            """
            ## About TutorBee Assistant
            
            This AI-powered chatbot represents TutorBee, an interactive tutoring service.
            
            ### Features:
            - 💬 **Natural Conversations**: Chat naturally about our services
            - 📝 **Lead Collection**: Automatically captures interested customers
            - 💡 **Smart Feedback**: Records questions we can't answer to improve
            - 🎯 **Business-Grounded**: Only answers from actual business documentation
            
            ### How to Use:
            1. Enter your OpenAI API key above
            2. Click "Initialize Agent"
            3. Start chatting in the Chat tab!
            4. View collected data in the Analytics tab
            
            ### Technology:
            - **AI Model**: OpenAI GPT-4o-mini
            - **Function Calling**: Automatic tool usage
            - **Framework**: Gradio for the interface
            
            ---
            
            Built as a demonstration of AI agents for business automation.
            """
        )

# =============================================================================
# 7. LAUNCH
# =============================================================================

if __name__ == "__main__":
    demo.launch()
