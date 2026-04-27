import re
from datetime import datetime

from pydantic import BaseModel, Field, computed_field


def slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class ProjectRecord(BaseModel):
    id: str
    path: str
    name: str
    slug: str
    description: str | None = None
    long_description: str | None = None
    remote_url: str | None = None
    created_at: datetime | None = None
    last_active: datetime | None = None
    total_commits: int = 0
    contributors: list[str] = Field(default_factory=list)
    primary_language: str | None = None
    languages: dict[str, float] = Field(default_factory=dict)
    stack: list[str] = Field(default_factory=list)
    has_tests: bool = False
    has_ci: bool = False
    has_docs: bool = False
    quality_score: float = 0.0
    tags: list[str] = Field(default_factory=list)
    screenshot_path: str | None = None
    size_bytes: int = 0
    preview_text: str | None = None

    @computed_field
    @property
    def last_active_display(self) -> str:
        if not self.last_active:
            return "Unknown"
        delta = datetime.utcnow() - self.last_active.replace(tzinfo=None)
        if delta.days == 0:
            return "Today"
        if delta.days == 1:
            return "Yesterday"
        if delta.days < 30:
            return f"{delta.days} days ago"
        if delta.days < 365:
            return f"{delta.days // 30} months ago"
        return f"{delta.days // 365} years ago"

    def to_json_dict(self) -> dict:
        """Serialize for site/src/data/projects.json"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "long_description": self.long_description,
            "path": self.path,
            "remote_url": self.remote_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "last_active_display": self.last_active_display,
            "total_commits": self.total_commits,
            "contributors": self.contributors,
            "primary_language": self.primary_language,
            "languages": self.languages,
            "stack": self.stack,
            "has_tests": self.has_tests,
            "has_ci": self.has_ci,
            "has_docs": self.has_docs,
            "quality_score": round(self.quality_score, 2),
            "tags": self.tags,
            "screenshot": self.screenshot_path,
            "preview_text": self.preview_text,
            "size_bytes": self.size_bytes,
        }
