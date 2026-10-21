"""Interactive CLI chat loop for the Offer Creation Bot."""

import json

from agents import Runner, SQLiteSession
from agents.items import HandoffOutputItem, ToolCallItem, ToolCallOutputItem
from dotenv import load_dotenv

from agency.agents.offer_agent import offer_agent
from agency.observability import configure_tracing, run_config
from agency.schemas import OfferPackage

load_dotenv()
configure_tracing()

SESSION_ID = "offer-bot-cli"


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
    if isinstance(final_output, OfferPackage):
        print(json.dumps(final_output.model_dump(), indent=2))
    else:
        print(final_output)


def main() -> None:
    session = SQLiteSession(session_id=SESSION_ID)
    current_agent = offer_agent

    print("Offer Creation Bot (type 'exit' to quit)\n")
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
            run_config=run_config("Offer Stage", SESSION_ID),
        )
        current_agent = result.last_agent

        _print_trace_items(result.new_items)
        print(f"\n[{current_agent.name}]")
        _print_final_output(result.final_output)
        print()


if __name__ == "__main__":
    main()
