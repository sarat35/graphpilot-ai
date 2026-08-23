from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ConversationState(TypedDict, total=False):
    message: str
    criteria: dict[str, str]
    reply: str


def build_conversation_graph():
    async def extract_criteria(state: ConversationState) -> dict[str, dict[str, str]]:
        text = state["message"].lower()
        criteria = dict(state.get("criteria", {}))
        city = next(
            (
                city
                for city in [
                    "ahmedabad",
                    "bengaluru",
                    "chennai",
                    "delhi",
                    "hyderabad",
                    "mumbai",
                    "pune",
                ]
                if city in text
            ),
            "",
        )
        fuel_type = next(
            (fuel for fuel in ["petrol", "diesel", "cng", "electric", "hybrid"] if fuel in text),
            "",
        )
        if city:
            criteria["city"] = city
        if fuel_type:
            criteria["fuel_type"] = fuel_type
        return {"criteria": criteria}

    async def write_reply(state: ConversationState) -> dict[str, str]:
        criteria = state.get("criteria", {})
        city = criteria.get("city")
        if not city:
            return {
                "reply": "Which city should I search in? I will ask for one preference at a time."
            }
        if not criteria.get("fuel_type"):
            return {"reply": (f"Great — I noted {city.title()}. Which fuel type should I use?")}
        return {
            "reply": (
                f"I noted {city.title()} and {criteria['fuel_type']}. "
                "What is your maximum budget in rupees?"
            )
        }

    graph = StateGraph(ConversationState)
    graph.add_node("extract_criteria", extract_criteria)
    graph.add_node("write_reply", write_reply)
    graph.add_edge(START, "extract_criteria")
    graph.add_edge("extract_criteria", "write_reply")
    graph.add_edge("write_reply", END)
    return graph.compile()
