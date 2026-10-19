import json, os
from typing import TypedDict
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from app.models import CompanyResearch

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash").with_structured_output(CompanyResearch)

class State(TypedDict):
    companies: list[dict]
    index: int
    current: dict | None

def load(state: State):
    with open("data/companies.json") as f:
        companies = json.load(f)
    return {"companies": companies[:1], "index": 0}  # just 1 today

def research(state: State):
    c = state["companies"][state["index"]]
    results = tavily.search(f"{c['name']} company overview news founders team", max_results=8)
    context = "\n\n".join(f"{r['url']}\n{r['content']}" for r in results["results"])
    prompt = f"""Research {c['name']} ({c['website']}) using ONLY the sources below.
If a fact isn't in the sources, leave it empty. Never guess emails or names.
Every news item must include its source URL.

SOURCES:
{context}"""
    return {"current": llm.invoke(prompt).model_dump()}

def save(state: State):
    c = state["current"]
    os.makedirs("outputs", exist_ok=True)
    with open(f"outputs/{c['name'].replace(' ', '_')}.json", "w") as f:
        json.dump(c, f, indent=2)
    return {"index": state["index"] + 1}

def more_left(state: State):
    return "research" if state["index"] < len(state["companies"]) else END

g = StateGraph(State)
g.add_node("load", load)
g.add_node("research", research)
g.add_node("save", save)
g.set_entry_point("load")
g.add_edge("load", "research")
g.add_edge("research", "save")
g.add_conditional_edges("save", more_left)
graph = g.compile()

if __name__ == "__main__":
    graph.invoke({"companies": [], "index": 0, "current": None})