import ast
import operator
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

# Safe arithmetic: only numeric constants and basic arithmetic operators are accepted.
_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent is too large.")
        return _BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression. Use numbers and +, -, *, /, //, %, **, and parentheses.")

@tool
def calculator(expression: str) -> str:
    """Calculate a numeric arithmetic expression accurately. Use for exact calculations, percentages, totals, and arithmetic based on search results. Input must be a mathematical expression only."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
        return f"Result: {result}"
    except Exception as exc:
        return f"Calculator error: {type(exc).__name__}: {exc}. Please try a valid arithmetic expression."

def build_agent():
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Missing GROQ_API_KEY. Copy .env.example to .env and add your Groq API key.")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("Missing TAVILY_API_KEY. Add your Tavily search API key to .env.")
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0,
    )
    search_tool = TavilySearch(max_results=3)
    return create_agent(
        model=llm,
        tools=[calculator, search_tool],
        system_prompt=(
            "You are a helpful tool-using assistant. Use calculator for exact arithmetic and "
            "web search for current or externally verifiable facts. Do not call tools for simple "
            "general questions that you can answer directly. For tasks that require finding facts "
            "and then calculating, search first and calculate from the retrieved values. If a tool "
            "returns an error or no results, explain the limitation and continue safely. Be clear "
            "about uncertainty. Do not reveal hidden chain-of-thought; tool actions and results are "
            "logged for transparency."
        ),
    )

def print_run(result):
    """Display user-visible tool calls/results and the final assistant answer."""
    messages = result.get("messages", [])
    print("\n" + "=" * 68)
    print("TOOL-USE LOG")
    print("=" * 68)
    for message in messages:
        name = getattr(message, "name", None)
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            for call in tool_calls:
                print(f"\n[TOOL CALL] {call.get('name', 'unknown')}")
                print(f"[INPUT] {call.get('args', {})}")
        if name:
            print(f"\n[TOOL RESULT: {name}]\n{getattr(message, 'content', '')}")
    print("\n" + "=" * 68)
    print("FINAL ANSWER")
    print("=" * 68)
    for message in reversed(messages):
        if getattr(message, "type", "") == "ai" and getattr(message, "content", ""):
            print(message.content)
            break
    print("=" * 68 + "\n")

def main():
    try:
        agent = build_agent()
    except Exception as exc:
        print(f"Setup error: {exc}")
        return

    print("LangChain Tool Agent")
    print("Tools: calculator + web search | type 'exit' to quit")
    print("Try: 'What is 17,825 * 4,906?'")
    print("Try: 'Search for the current population of Japan and calculate 2% of it.'")
    print("Try: 'Explain what an AI agent is in one sentence.'")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            continue
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": question}]})
            print_run(result)
        except Exception as exc:
            print(f"\nAgent run failed gracefully: {type(exc).__name__}: {exc}")
            print("Check your API keys, internet connection, and provider quota, then try again.")

if __name__ == "__main__":
    main()
