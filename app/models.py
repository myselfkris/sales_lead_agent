from pydantic import BaseModel, Field

class OpenRole(BaseModel):
    title: str
    skills: list[str] = Field(default_factory=list)
    url: str  # job post or careers page, required

class NewsItem(BaseModel):
    title: str
    date: str | None = None
    url: str  # source link, required

class Contact(BaseModel):
    name: str
    role: str
    profile_url: str | None = None  # e.g. LinkedIn

class CompanyResearch(BaseModel):
    name: str
    website: str
    description: str
    problem_they_solve: str
    recent_changes: list[NewsItem] = Field(default_factory=list)
    contacts: list[Contact] = Field(default_factory=list)
    public_email: str | None = None  # official careers/contact email only
    sources: list[str] = Field(default_factory=list)
    hiring: list[OpenRole] = Field(default_factory=list)