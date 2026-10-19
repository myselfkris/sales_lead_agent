import json, os
from datetime import datetime
from typing import TypedDict
from urllib.parse import urlparse
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
    run_dir: str  # every run saves into its own folder

def load(state: State):
    with open("data/companies.json") as f:
        companies = json.load(f)
    # one folder per run, e.g. outputs/run_20261019_1245 -> old runs are never overwritten
    run_dir = f"outputs/run_{datetime.now().strftime('%Y%m%d_%H%M')}"
    os.makedirs(run_dir, exist_ok=True)
    return {"companies": companies, "index": 0, "run_dir": run_dir}

BLOCKED = ["instagram.com", "facebook.com", "youtube.com", "x.com", "quora.com", "reddit.com"]

def search_block(results):
    return "\n\n".join(
        f"{r['url']}\nDate: {r.get('published_date', 'unknown')}\n{r['content']}"
        for r in results["results"]
    )


def research(state: State):
    c = state["companies"][state["index"]]
    domain = urlparse(c["website"]).netloc.replace("www.", "")  # https://www.sarvam.ai -> sarvam.ai
    print(f"Researching {c['name']} ...")

    # 1. General info
    general = tavily.search(f"{c['name']} company overview founders",
                            max_results=6, exclude_domains=BLOCKED)
    # 2. Fresh news (last 6 months)
    news = tavily.search(c["name"], topic="news", days=180,
                         max_results=6, exclude_domains=BLOCKED)
    # 3. People: tech leaders + HR  (NEW)
    people = tavily.search(
        f"{c['name']} CTO head of engineering VP engineering talent acquisition recruiter",
        max_results=6, exclude_domains=BLOCKED)
    # 4. Jobs: company's own website first  (UPGRADED)
    jobs_official = tavily.search(f"{c['name']} careers engineer AI jobs",
                                  max_results=5, include_domains=[domain])
    # 5. Jobs: other job sites, only as a backup
    jobs_other = tavily.search(f"{c['name']} AI engineer job opening",
                               max_results=4, exclude_domains=BLOCKED)

    prompt = f"""Research {c['name']} ({c['website']}) using ONLY the sources below.

RULES:
- If a fact isn't in the sources, leave it empty. Never guess names, emails or links.
- recent_changes: only real EVENTS at the company in the last 6 months (funding, launch,
  merger, acquisition, big hire, big customer). NOT articles that explain, review,
  price or compare the company. Look in ALL sections. Every item needs a date and URL.
  If two items describe the same event, keep one (prefer the company's own site).
- Big facts (funding, valuation, launches) only from {c['website']}, the company's investors,
  press release sites, or known news outlets (Economic Times, Moneycontrol, Inc42,
  YourStory, TechCrunch, Mint, NDTV). Skip random blogs.
- contacts: max 5. Only founders, CTO / engineering leaders, and HR / talent people.
  No board members, advisors, finance, legal, sales or marketing.
  Add profile_url only if that exact link is in the sources.
- hiring: engineering, AI and ML roles only. The company name must match exactly.
  Use OFFICIAL JOBS first. If there are no engineering roles there, use OTHER JOBS.
  Skip jobs marked closed or "no longer accepting applications".
- skills: only skills written in the source, otherwise leave empty.

GENERAL:
{search_block(general)}

NEWS (last 6 months):
{search_block(news)}

PEOPLE:
{search_block(people)}

OFFICIAL JOBS (company website):
{search_block(jobs_official)}

OTHER JOBS:
{search_block(jobs_other)}"""

    result = llm.invoke(prompt).model_dump()

    ALLOWED = ("careers@", "jobs@", "hr@", "hiring@", "talent@", "recruit")
    email = result.get("public_email")
    if email and not email.lower().startswith(ALLOWED):
        result["public_email"] = None

    return {"current": result}

def save(state: State):
    c = state["current"]
    path = f"{state['run_dir']}/{c['name'].replace(' ', '_')}.json"
    with open(path, "w") as f:
        json.dump(c, f, indent=2)
    print(f"  saved -> {path}")
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
    graph.invoke({"companies": [], "index": 0, "current": None, "run_dir": ""})
