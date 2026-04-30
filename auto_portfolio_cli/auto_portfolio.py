"""Auto-Portfolio CLI — zero-input portfolio generator from git history."""

from pathlib import Path

import typer

app = typer.Typer(name="auto-portfolio", help="Zero-input portfolio generator from git history.")


@app.command()
def setup():
    """Interactive setup: generate config.toml and prepare the site."""
    from rich.console import Console
    from rich.prompt import Prompt

    console = Console()
    console.print("[bold]Auto-Portfolio Setup[/bold]\n")

    dest = Path("config.toml")
    if dest.exists():
        console.print("[yellow]config.toml already exists. Editing it directly instead.[/yellow]")
    else:
        name = Prompt.ask("Your name", default="Developer")
        title = Prompt.ask("Your title", default="Software Engineer")
        bio = Prompt.ask("Short bio", default="I build things.")

        config_content = f'''[profile]
name = "{name}"
title = "{title}"
bio = "{bio}"

[scan]
paths = ["~/projects"]
exclude = ["**/.git", "**/node_modules", "**/dist", "**/.venv"]
min_commits = 1
max_age_days = 730

[site]
theme = "dark"
accent_color = "#6366f1"

[deploy]
target = "github-pages"
'''
        dest.write_text(config_content)
        console.print("[green]Created config.toml[/green]")

    console.print("\nNext steps:")
    console.print("  auto-portfolio generate   — scan repos and build site")
    console.print("  auto-portfolio preview    — preview site locally")


@app.command()
def generate(
    config: str = typer.Option("config.toml", "--config", "-c"),
    site_dir: str = typer.Option("site", "--site-dir"),
    no_build: bool = typer.Option(False, "--no-build", help="Skip Astro build"),
):
    """Scan all repos and generate the portfolio site."""
    from rich.console import Console

    from core.config import AppConfig
    from core.repo_scanner import scan_root
    from core.site_generator import build_astro_site, write_profile_json, write_projects_json

    console = Console()
    cfg = AppConfig.from_toml(Path(config))

    console.print(f"[bold]Scanning {len(cfg.scan.paths)} path(s)...[/bold]")
    all_records = []
    for raw_path in cfg.scan.paths:
        root = Path(raw_path).expanduser()
        console.print(f"  Scanning {root}...")
        records = scan_root(
            root,
            min_commits=cfg.scan.min_commits,
        )
        all_records.extend(records)
        console.print(f"  Found {len(records)} projects")

    console.print(f"\n[green]Total: {len(all_records)} projects[/green]")

    # Write data files
    site_data_dir = Path(site_dir) / "src" / "data"
    write_projects_json(all_records, site_data_dir)
    write_profile_json(cfg.profile, site_data_dir)
    console.print(f"[green]Data written to {site_data_dir}[/green]")

    # Build site
    if not no_build:
        site_path = Path(site_dir)
        if (site_path / "package.json").exists():
            console.print("\n[bold]Building Astro site...[/bold]")
            ok = build_astro_site(site_path)
            if ok:
                console.print(f"[green]Site built to {site_path / 'dist'}[/green]")
            else:
                console.print("[red]Astro build failed. Check site/package.json.[/red]")
        else:
            msg = "No site/package.json found. Run npm install in site/."
            console.print(f"[yellow]{msg}[/yellow]")
    else:
        console.print("[dim]Skipping build (--no-build)[/dim]")

    console.print("\n[bold green]Done![/bold green]")
    console.print("  Preview: auto-portfolio preview")


@app.command()
def preview(
    site_dir: str = typer.Option("site", "--site-dir"),
    port: int = typer.Option(4321, "--port"),
):
    """Preview the generated site locally."""
    import subprocess

    from rich.console import Console

    console = Console()
    site_path = Path(site_dir)
    if not (site_path / "dist").exists():
        console.print("[red]No dist/ found. Run: auto-portfolio generate[/red]")
        raise typer.Exit(1)
    console.print(f"[bold]Previewing at http://localhost:{port}[/bold]")
    subprocess.run(["npm", "run", "preview", "--", f"--port={port}"], cwd=site_path)


@app.command()
def health(
    config: str = typer.Option("config.toml", "--config"),
    site_dir: str = typer.Option("site", "--site-dir"),
):
    """Show portfolio status and stats."""
    import json

    from rich.console import Console

    console = Console()

    data_file = Path(site_dir) / "src" / "data" / "projects.json"
    if not data_file.exists():
        console.print("[yellow]No data generated yet. Run: auto-portfolio generate[/yellow]")
        return

    data = json.loads(data_file.read_text())
    projects = data.get("projects", [])
    console.print("\n[bold]Auto-Portfolio Health[/bold]")
    console.print(f"  Projects: {len(projects)}")
    if projects:
        langs = {}
        for p in projects:
            for lang, pct in (p.get("languages") or {}).items():
                langs[lang] = langs.get(lang, 0) + pct
        top3 = sorted(langs.items(), key=lambda x: -x[1])[:5]
        console.print(f"  Top languages: {', '.join(item[0] for item in top3)}")
    console.print(f"  Generated: {data.get('generated_at', 'unknown')[:10]}")
    console.print(f"  Site built: {(Path(site_dir) / 'dist').exists()}")


if __name__ == "__main__":
    app()
