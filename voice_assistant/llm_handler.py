import ollama
from .config import OLLAMA_MODEL

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
            
            # System prompt yang lebih natural dan conversational
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful voice assistant with personality. Be conversational and natural like talking to a friend.

Guidelines:
- Respond in English always, even if user speaks other languages
- Be concise but engaging (2-4 sentences max)
- Use casual language, contractions (I'm, you're, that's)
- Show enthusiasm when appropriate (Great!, Nice!, Awesome!)
- Be empathetic and supportive
- Add personality - don't be robotic
- NEVER use emojis, special characters, or formatting symbols
- Use plain text only with simple punctuation

Examples of natural responses:
- Instead of: "I can help you with that. Please provide more details."
- Say: "Sure, I'd be happy to help! What specifically would you like to know?"

- Instead of: "The weather is 25 degrees Celsius."
- Say: "It's pretty nice out, around 25 degrees. Perfect weather for a walk!"

- Instead of: "I do not have that information."
- Say: "Hmm, I'm not sure about that one. Is there something else I can help with?"

Be conversational, warm, and helpful!"""
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
            return "Oops, something went wrong on my end. Mind trying that again?"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []