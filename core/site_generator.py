import json
import subprocess
from datetime import datetime
from pathlib import Path

from core.config import ProfileConfig
from data.models import ProjectRecord


def write_projects_json(
    records: list[ProjectRecord], 
    site_data_dir: Path,
    github_token: str | None = None
) -> Path:
    """Write site/src/data/projects.json from scanner output.
    
    Optionally enriches projects with live GitHub statistics.
    
    Args:
        records: List of ProjectRecord objects
        site_data_dir: Directory to write JSON file
        github_token: GitHub token for live stats (optional)
    """
    # Enrich with live stats if token provided
    if github_token:
        from core.profile_importer import enrich_with_live_stats
        records = enrich_with_live_stats(records, token=github_token)
    
    site_data_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "projects": [_to_dict(r) for r in records],
    }
    out_path = site_data_dir / "projects.json"
    out_path.write_text(json.dumps(output, indent=2, default=str))
    return out_path


def _to_dict(r):
    """Convert record to dict, handling both ProjectRecord and dict."""
    if hasattr(r, "to_json_dict"):
        return r.to_json_dict()
    return r


def write_profile_json(profile: ProfileConfig, site_data_dir: Path) -> Path:
    """Write site/src/data/profile.json from config."""
    site_data_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "name": profile.name,
        "title": profile.title,
        "bio": profile.bio,
        "avatar": profile.avatar,
        "social": profile.social,
    }
    out_path = site_data_dir / "profile.json"
    out_path.write_text(json.dumps(out, indent=2))
    return out_path


def build_astro_site(site_dir: Path) -> bool:
    """Run npm run build in the Astro site directory."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=site_dir,
        timeout=120,
    )
    return result.returncode == 0
