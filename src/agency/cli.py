"""Interactive CLI chat loop for the agency pipeline."""

import json
import re

from agents import Runner, SQLiteSession
from agents.items import HandoffOutputItem, ToolCallItem, ToolCallOutputItem
from dotenv import load_dotenv

from agency.agents.offer_agent import offer_agent
from agency.observability import configure_tracing, run_config
from agency.schemas import LeadList, OfferPackage, OutboundPackage

load_dotenv()
configure_tracing()

SESSION_ID = "offer-bot-cli"

_RED = "\033[91m"
_GREEN = "\033[92m"
_RESET = "\033[0m"
_VIABILITY_PATTERN = re.compile(r"\bUNVIABLE\b|\bVIABLE\b")


def _highlight_viability(text: str) -> str:
    """Color VIABLE green and UNVIABLE red for terminal readability."""

    def _colorize(match: re.Match) -> str:
        color = _RED if match.group() == "UNVIABLE" else _GREEN
        return f"{color}{match.group()}{_RESET}"

    return _VIABILITY_PATTERN.sub(_colorize, text)


def _print_trace_items(new_items: list) -> None:
    """Print tool calls and handoffs so the agent's reasoning steps are visible."""
    for item in new_items:
        if isinstance(item, ToolCallItem):
            tool_name = getattr(item.raw_item, "name", "tool")
            tool_args = getattr(item.raw_item, "arguments", "")
            print(f"  \u2192 tool call: {tool_name}({tool_args})")
        elif isinstance(item, ToolCallOutputItem):
            print(f"    tool result: {item.output}")
        elif isinstance(item, HandoffOutputItem):
            print(f"  \u2192 handoff: {item.source_agent.name} -> {item.target_agent.name}")


def _print_final_output(final_output) -> None:
    if isinstance(final_output, (OfferPackage, LeadList, OutboundPackage)):
        print(json.dumps(final_output.model_dump(), indent=2))
    else:
        print(_highlight_viability(str(final_output)))


def main() -> None:
    session = SQLiteSession(session_id=SESSION_ID)
    current_agent = offer_agent

    print("=" * 70)
    print("Agency Builder")
    print("=" * 70)
    print(
        "This bot helps you decide WHAT to sell and to WHOM for your marketing\n"
        "agency. Tell it your target industry or experience, and it will search\n"
        "the web for promising niches, recommend one with real data behind it,\n"
        "and (once you confirm) produce a structured offer package. You can then\n"
        "find leads and draft outreach for them in the same conversation.\n"
    )
    print("Type 'exit' or 'quit' to leave at any time.\n")
    print("To get started, tell the bot about your industry/background, e.g.:")
    print('  "I have a background in real estate photography"\n')
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        result = Runner.run_sync(
            current_agent,
            user_input,
            session=session,
            run_config=run_config("Agency Pipeline", SESSION_ID),
        )
        current_agent = result.last_agent

        _print_trace_items(result.new_items)
        print(f"\n[{current_agent.name}]")
        _print_final_output(result.final_output)
        print()


if __name__ == "__main__":
    main()
