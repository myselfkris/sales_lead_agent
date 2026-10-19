# Progress

## 19 Oct 2026 — Day 1
**Built**
- LangGraph research agent: load → research → save, loops over 5 companies
- 5 Tavily searches per company: general, news (last 180 days), people, official jobs, other jobs
- Pydantic schema with source URLs required; every run saved in its own folder

**Fixed**
- Old/undated news → separate news search + date rule
- Wrong contacts (board members, advisors) → people search + max 5 relevant roles
- Missing Yellow.ai merger → search_block was dropping Tavily's published_date
- Empty hiring → fallback to job sites when official page has no engineering roles
- Media contact email saved as company email → code check allows only careers@/hr@/jobs@

**Learned**
- Debug rule: print raw search results first. Not found = search problem; found but ignored = rules/plumbing problem
- Two correct rules can block each other (trusted source had no date, dated source wasn't trusted)
- Prompt rules aren't enough for hard limits — enforce them in code

**Next**
- Move checks into a separate clean node
- Error handling so one failed company doesn't crash the run
- Start the outreach message drafting