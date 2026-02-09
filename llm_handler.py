# llm_handler.py
import ollama
from config import OLLAMA_MODEL

class LLMHandler:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.conversation_history = []
        
    def generate_response(self, user_input):
        """Generate response from LLM"""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate response dengan system prompt
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful voice assistant. Keep responses concise and conversational, maximum 3-4 sentences. Avoid long explanations unless specifically asked. Never use emojis, emoticons, or any special characters in your responses. Use plain text only."
                }
            ] + self.conversation_history
            
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            assistant_message = response['message']['content']
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return assistant_message
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Sorry, I encountered an error processing your request."
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []