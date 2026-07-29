from groq import Groq
from flask import current_app

def get_groq_client():
    return Groq(
        api_key = current_app.config["GROQ_API_KEY"]
    )

def test_groq():
        client = get_groq_client()

        response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages=[
                {
                    "role":"user",
                    "content":"Give me the detailed summary of the play Julius Caesar by William Shakespeare. "
                }
            ]
        )

        return response.choices[0].message.content
