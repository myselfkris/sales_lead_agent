# Sales Research Agent

An AI agent that researches companies from public sources and returns a structured
profile — what they do, recent news, key people, and open engineering roles — so you
can write outreach that isn't generic.

Built with LangGraph, Tavily search, and Gemini.

## What it returns (per company)
- Description and the problem they solve
- Recent changes (last 6 months only, each with a date and source link)
- Contacts: founders, tech leaders, HR (max 5)
- Open engineering / AI roles
- Every fact links to its source; anything not found is left empty, never guessed

## How it works
load companies → research (5 web searches + Gemini) → save JSON → next company

Checks enforced in code (not just the prompt):
- News older than 180 days is dropped
- Only generic emails (careers@, hr@, jobs@) are kept
- If one company fails, it's skipped and the run continues

## Run it
1. `pip install -r requirements.txt`
2. Create `.env` with `GOOGLE_API_KEY` and `TAVILY_API_KEY`
3. Add companies to `data/companies.json`
4. `python -m app.graph`

Results are saved in `outputs/run_<date_time>/`.

## Example output
See `outputs/` for a sample run (Sarvam AI, Yellow.ai, Krutrim, Haptik, Gupshup).

## Next
- Outreach message writer
- Critic agent to catch wrong facts and contacts
- Eval set to score each run