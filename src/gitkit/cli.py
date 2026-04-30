"""CLI entry points using Click."""

import json

import click
from rich.console import Console
from rich.table import Table

from gitkit import __version__
from gitkit.commands import clean_branches_impl, get_stats_impl, sync_fork_impl

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """gitkit - Fast Git workflow CLI tool."""
    if ctx.invoked_subcommand is None:
        console.print("[green]gitkit CLI ready[/green]")
        console.print(ctx.get_help())


@main.command()
@click.option("--dry-run", is_flag=True, default=True, help="Show what would be deleted")
@click.option("--remote", is_flag=True, help="Also delete from remote")
def clean_branches(dry_run: bool, remote: bool) -> None:
    """Delete merged branches."""
    try:
        deleted = clean_branches_impl(dry_run=dry_run, remote=remote)

        if not deleted:
            console.print("[yellow]No branches to delete[/yellow]")
            return

        if dry_run:
            console.print("[cyan]Branches that would be deleted (dry-run):[/cyan]")
        else:
            console.print("[green]Deleted branches:[/green]")

        for branch in deleted:
            console.print(f"  • {branch}")

        if dry_run:
            console.print("[green]Dry-run completed successfully[/green]")
        else:
            console.print("[green]Branch cleanup completed successfully[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@main.command()
@click.argument("branch", required=False, default="HEAD")
@click.option("--since", help="Show commits since (e.g., '2 weeks ago')")
@click.option("--json", "json_output", is_flag=True, help="Output stats as JSON")
def stats(branch: str, since: str | None, json_output: bool) -> None:
    """Show git statistics."""
    try:
        data = get_stats_impl(branch=branch, since=since)
        if json_output:
            click.echo(json.dumps(data))
            return

        table = Table(title=f"Stats for {branch}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Commits", str(data["total_commits"]))
        table.add_row("Period", data["since"])

        console.print(table)
        console.print("[green]Stats generated successfully[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@main.command()
def sync_fork() -> None:
    """Sync fork with upstream."""
    try:
        result = sync_fork_impl()
        if result["updated"]:
            console.print(
                f"[green]Synced from upstream/{result['upstream_branch']} "
                f"({result['commits']} new commit(s))[/green]"
            )
        else:
            console.print(
                f"[yellow]Already up to date with upstream/{result['upstream_branch']}[/yellow]"
            )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    main()
