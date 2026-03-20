"""
LLM service abstraction supporting Google Gemini and OpenAI.
Uses LangChain ChatModels for uniform interface.
"""
import json
from config import Config
from langchain_core.messages import HumanMessage, SystemMessage


def get_llm():
    """Return a LangChain ChatModel based on configured provider."""
    if Config.LLM_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.2,
        )
    else:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=Config.LLM_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.2,
        )


def call_llm(prompt: str, system_prompt: str = "", expect_json: bool = False) -> str:
    """
    Call the configured LLM with a prompt.
    
    Args:
        prompt: The user/task prompt.
        system_prompt: Optional system-level instruction.
        expect_json: If True, attempt to parse and return valid JSON from response.
    
    Returns:
        The LLM's response as a string.
    """
    llm = get_llm()
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    print(f"--- Calling LLM ({Config.LLM_MODEL}) ---")
    print(f"System Prompt: {system_prompt[:100]}...")
    print(f"User Prompt: {prompt[:100]}...")
    response = llm.invoke(messages)
    print("--- LLM Response Received ---")
    text = response.content.strip()

    if expect_json:
        # Try to extract JSON from the response
        text = _extract_json(text)

    return text


def _extract_json(text: str) -> str:
    """Extract JSON from LLM response, handling markdown code fences."""
    # Remove markdown code fences if present
    if "```json" in text:
        text = text.split("```json", 1)[1]
        text = text.rsplit("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1]
        text = text.rsplit("```", 1)[0]

    text = text.strip()

    # Validate it's parseable JSON
    try:
        json.loads(text)
    except json.JSONDecodeError:
        pass  # Return as-is if not valid JSON

    return text
