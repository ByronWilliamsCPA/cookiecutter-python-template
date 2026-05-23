"""Command-line interface for {{ cookiecutter.project_name }}.

Provides commands for common operations and demonstrates Click best practices
with structured logging integration.
"""

import sys
from dataclasses import dataclass
from typing import cast

import click
from structlog.stdlib import BoundLogger

from {{ cookiecutter.project_slug }}.core.config import settings
from {{ cookiecutter.project_slug }}.utils.logging import get_logger

logger: BoundLogger = get_logger(__name__)


@dataclass
class CLIContext:
    """Typed context object for Click commands."""

    debug: bool = False


def _get_context(ctx: click.Context) -> CLIContext:
    """Return ctx.obj typed as CLIContext.

    Click's stubs declare ctx.obj as Any. This helper narrows the type so
    callers receive a CLIContext without per-site casts. If ctx.obj is
    somehow not a CLIContext at runtime (e.g., subcommand invoked without
    the parent group running), fall back to a default CLIContext.
    """
    # Cast from Any to object so basedpyright can narrow via isinstance.
    obj: object = cast(object, ctx.obj)
    if isinstance(obj, CLIContext):
        return obj
    return CLIContext()


@click.group()
@click.version_option(version="{{ cookiecutter.version }}", prog_name="{{ cookiecutter.cli_tool_name }}")
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """{{ cookiecutter.project_name }} - {{ cookiecutter.project_short_description }}."""
    # Store typed context object for subcommands
    ctx.obj = CLIContext(debug=debug)

    if debug:
        logger.debug("Debug mode enabled")


@cli.command()
@click.option(
    "--name",
    "-n",
    type=str,
    default="World",
    help="Name to greet",
)
@click.pass_context
def hello(ctx: click.Context, name: str) -> None:
    """Greet the user with a personalized message."""
    try:
        cli_ctx = _get_context(ctx)

        logger.info(
            "Processing hello command",
            name=name,
            debug=cli_ctx.debug,
        )

        message = f"Hello, {name}!"
        click.echo(message)

        logger.info("Command completed successfully", result=message)

    except Exception as e:
        logger.exception("Command failed", error=str(e))
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Display current configuration settings.

    Shows configuration values from environment variables or defaults.
    """
    try:
        cli_ctx = _get_context(ctx)

        logger.info("Retrieving configuration")

        click.echo("Current Configuration:")
        click.echo("  Project: {{ cookiecutter.project_name }}")
        click.echo("  Version: {{ cookiecutter.version }}")
        click.echo(f"  Debug: {cli_ctx.debug}")
        click.echo(f"  Log Level: {settings.log_level}")

        logger.info("Configuration displayed successfully")

    except Exception as e:
        logger.exception("Failed to display configuration", error=str(e))
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
