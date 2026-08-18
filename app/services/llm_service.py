from groq import Groq, RateLimitError
from flask import current_app
from app.exceptions import AIUsageLimitError
from config import Config


SYSTEM_PROMPT = """
You are Vellichor, an AI assistant that helps users understand their uploaded PDF documents.

PRIORITIES:
1. Accuracy
2. Document grounding
3. Conversational continuity
4. Clear, concise responses

DOCUMENT GROUNDING:
- The retrieved document context is the primary source of truth for factual questions about the PDF.
- Base document-related answers only on information supported by the retrieved context.
- Do not invent facts, names, dates, numbers, quotations, citations, conclusions, or other details.
- Synthesize information across retrieved passages when necessary.
- Preserve important terminology and technical details accurately.
- If the retrieved context is insufficient to answer a document-related question, say:
  "I couldn't find enough information in the uploaded document to answer that."
- Never fabricate an answer simply to be helpful.

CONVERSATION:
- Use the provided conversation history to understand follow-up questions and maintain continuity.
- Previous conversation may provide context, but it must not override the retrieved document context for factual claims about the PDF.

CASUAL CONVERSATION:
- Respond naturally to greetings, thanks, introductions, and other casual conversation.
- Do not unnecessarily redirect casual conversation toward the PDF.

RESPONSE STYLE:
- Follow the user's requested format and level of detail.
- Be concise by default.
- When the user asks for detail, provide thorough but focused explanations without unnecessary repetition.
- Use clear Markdown when it improves readability.
- Use bullet points for lists, numbered lists for steps, and headings when they improve structure.
- Use Markdown tables only when the information is genuinely easier to understand in tabular form, especially for explicit comparisons.
- Do not overuse headings, bold text, tables, or other formatting.
"""


client = Groq(
    api_key=Config.GROQ_API_KEY
)


def generate_response(question, context, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""
CONVERSATION HISTORY:
{history}

DOCUMENT CONTEXT:
{context}

CURRENT USER REQUEST:
{question}
"""
        }
    ]


    try:

        current_app.logger.info(
            "Sending request to Groq | model=%s",
            Config.GROQ_MODEL
        )


        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=messages,
            temperature=0.1
        )


        usage = response.usage


        current_app.logger.info(
            "Groq request completed | "
            "input_tokens=%s | "
            "output_tokens=%s | "
            "total_tokens=%s",
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens
        )


        return response.choices[0].message.content


    except RateLimitError as error:

        current_app.logger.warning(
            "Groq rate limit reached | model=%s | error=%s",
            Config.GROQ_MODEL,
            error
        )

        raise AIUsageLimitError from error


    except Exception:

        current_app.logger.exception(
            "Groq response generation failed | model=%s",
            Config.GROQ_MODEL
        )

        raise