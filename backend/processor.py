# processor.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MY_API_KEY")
if not api_key:
    raise ValueError("MY_API_KEY not found in environment variables")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",  # OpenRouter endpoint
)


def generate_response(user_input):
    system_prompt = """
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
"""

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error generating response: {str(e)}"
