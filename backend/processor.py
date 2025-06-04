# processor.py
import os
import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))


def generate_response(user_input):
    prompt = f"""
You are a helpful AI assistant.

🧠 Always try to:
- Fully understand vague or unclear questions
- Answer all parts of multi-intent queries
- Be clear, polite, and helpful

📌 Example 1:
User: What’s the time and also tell me the capital of France?
Assistant: The current time is 3:45 PM. The capital of France is Paris.

📌 Example 2:
User: Remind me how to reset my password and check order status
Assistant: You can reset your password from the login page by clicking "Forgot password". To check your order status, go to the "Orders" section of your account.

Now respond to this:
User: {user_input}
Assistant:"""

    try:
        response = co.generate(
            model="command-r-plus",   # ✅ upgraded model
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error: {e}"
