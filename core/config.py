import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProfileConfig:
    name: str = "Developer"
    title: str = "Software Engineer"
    bio: str = ""
    avatar: str | None = None
    social: dict = field(default_factory=dict)


@dataclass
class ScanConfig:
    paths: list[str] = field(default_factory=lambda: ["~/projects"])
    exclude: list[str] = field(
        default_factory=lambda: ["**/.git", "**/node_modules", "**/dist", "**/.venv"]
    )
    min_commits: int = 1
    max_age_days: int = 730
    include_patterns: list[str] = field(default_factory=list)
    exclude_paths: list[str] = field(default_factory=list)


@dataclass
class SiteConfig:
    theme: str = "dark"
    accent_color: str = "#6366f1"
    language: str = "en"


@dataclass
class CacheConfig:
    enabled: bool = True
    dir: str = "~/.cache/auto-portfolio"


@dataclass
class AppConfig:
    profile: ProfileConfig = field(default_factory=ProfileConfig)
    scan: ScanConfig = field(default_factory=ScanConfig)
    site: SiteConfig = field(default_factory=SiteConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    @classmethod
    def from_toml(cls, path: Path = Path("config.toml")) -> "AppConfig":
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        cfg = cls()
        if "profile" in data:
            for k, v in data["profile"].items():
                if hasattr(cfg.profile, k):
                    setattr(cfg.profile, k, v)
        if "scan" in data:
            for k, v in data["scan"].items():
                if hasattr(cfg.scan, k):
                    setattr(cfg.scan, k, v)
        if "site" in data:
            for k, v in data["site"].items():
                if hasattr(cfg.site, k):
                    setattr(cfg.site, k, v)
        return cfg
