#!/usr/bin/env python
"""CLI for Hegelion dialectical reasoning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from importlib.resources import files

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.theme import Theme

    custom_theme = Theme({
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red"
    })
    console = Console(theme=custom_theme)
except ImportError:
    console = None

if __package__ is None or __package__ == "":  # pragma: no cover - direct execution fallback
    sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.core.config import ConfigurationError, get_config, set_config_value
from hegelion import run_dialectic
from hegelion import HegelionResult
from hegelion.scripts.mcp_setup import print_setup_instructions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Hegelion dialectical reasoning on a single query."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question or topic to analyze dialectically (optional when using --interactive or --demo).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include debug information and internal diagnostics",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the structured result",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary", "rich"],
        default="json",
        help="Output format (default: json). Use 'rich' for formatted terminal output.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show a cached example trace without calling any live backend",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode for an exploratory session",
    )
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _load_demo_examples() -> list[dict]:
    """Load bundled demo examples from the installed package."""
    try:
        data = files("hegelion.examples_data").joinpath("glm4_6_examples.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in data.splitlines() if line.strip()]
    except Exception:
        return []


def print_cached_example(format_type: str = "json") -> None:
    """Print a cached example result for demo mode."""
    examples = _load_demo_examples()
    if not examples:
        print("Demo data is not available in this installation.", file=sys.stderr)
        return

    example_data = examples[0]

    if format_type == "summary":
        result = HegelionResult(**example_data)
        print(format_summary(result))
    elif format_type == "rich" and console:
        result = HegelionResult(**example_data)
        print_rich_result(result)
    else:
        print(json.dumps(example_data, indent=2, ensure_ascii=False))


def format_summary(result) -> str:
    """Format result as a human-readable summary."""
    metadata = result.metadata or {}

    def _fmt_time(key: str) -> str:
        value = metadata.get(key)
        if isinstance(value, (int, float)):
            return f"{value:.0f}ms"
        return "n/a"

    lines = [
        f"Query: {result.query}",
        f"Mode: {result.mode}",
        f"Contradictions Found: {len(result.contradictions)}",
        f"Research Proposals: {len(result.research_proposals)}",
    ]

    backend_provider = metadata.get("backend_provider")
    backend_model = metadata.get("backend_model")
    if backend_provider or backend_model:
        backend_parts = [
            str(part).strip()
            for part in (backend_provider, backend_model)
            if part is not None and str(part).strip()
        ]
        if backend_parts:
            lines.append("Backend: " + ", ".join(backend_parts))

    lines.extend(
        [
            "",
            "=== THESIS ===",
            result.thesis,
            "",
            "=== ANTITHESIS ===",
            result.antithesis,
            "",
            "=== SYNTHESIS ===",
            result.synthesis,
            "",
        ]
    )

    if result.contradictions:
        lines.append("=== CONTRADICTIONS ===")
        for i, contradiction in enumerate(result.contradictions, 1):
            lines.append(f"{i}. {contradiction.get('description', 'No description')}")
            evidence = contradiction.get("evidence")
            if evidence:
                lines.append(f"   Evidence: {evidence}")
        lines.append("")

    if result.research_proposals:
        lines.append("=== RESEARCH PROPOSALS ===")
        for i, proposal in enumerate(result.research_proposals, 1):
            lines.append(f"{i}. {proposal.get('description', 'No description')}")
            prediction = proposal.get("testable_prediction")
            if prediction:
                lines.append(f"   Prediction: {prediction}")
        lines.append("")

    lines.append("=== TIMING ===")
    lines.append(f"Thesis: {_fmt_time('thesis_time_ms')}")
    lines.append(f"Antithesis: {_fmt_time('antithesis_time_ms')}")
    lines.append(f"Synthesis: {_fmt_time('synthesis_time_ms')}")
    lines.append(f"Total: {_fmt_time('total_time_ms')}")

    debug_info = metadata.get("debug")
    if isinstance(debug_info, dict) and debug_info:
        lines.append("")
        lines.append("=== DEBUG METRICS ===")
        for key, value in debug_info.items():
            lines.append(f"{key}: {value}")

    return "\n".join(lines)

def print_rich_result(result: HegelionResult):
    """Print the result using Rich panels and markdown."""
    if not console:
        print(format_summary(result))
        return

    console.print(f"\n[bold]Query:[/bold] {result.query}")
    
    console.print(Panel(Markdown(result.thesis), title="[bold cyan]Thesis[/]", border_style="cyan"))
    console.print(Panel(Markdown(result.antithesis), title="[bold magenta]Antithesis[/]", border_style="magenta"))
    console.print(Panel(Markdown(result.synthesis), title="[bold green]Synthesis[/]", border_style="green"))
    
    if result.contradictions:
        console.print("\n[bold red]Contradictions Identified:[/]")
        for i, c in enumerate(result.contradictions, 1):
            console.print(f"{i}. {c.get('description', 'No description')}", style="red")

    if result.research_proposals:
        console.print("\n[bold blue]Research Proposals:[/]")
        for i, p in enumerate(result.research_proposals, 1):
            console.print(f"{i}. {p.get('description', 'No description')}", style="blue")
            if p.get("testable_prediction"):
                console.print(f"   [dim]Prediction: {p['testable_prediction']}[/]")


async def async_input(prompt: str) -> str:
    """Non-blocking input for async context."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: input(prompt))


async def interactive_session() -> None:
    """Run the Hegelion CLI in an interactive REPL session."""
    if console:
        console.print("[bold green]Welcome to the Hegelion Interactive Dialectic Explorer.[/]")
        console.print("Type a query to start, or 'help' for a list of commands.")
    else:
        print("Welcome to the Hegelion Interactive Dialectic Explorer.")
        print("Type a query to start, or 'help' for a list of commands.")

    history: List[str] = []
    latest_result: Optional[HegelionResult] = None
    debug_mode = get_config().debug

    while True:
        try:
            query = (await async_input("Hegelion> ")).strip()
            if not query:
                continue

            history.append(query)
            parts = query.split()
            command = parts[0].lower()

            if command in ("exit", "quit"):
                break
            elif command == "help":
                print_interactive_help()
            elif command == "history":
                for i, item in enumerate(history, 1):
                    print(f"{i}: {item}")
            elif command == "show":
                if not latest_result:
                    print("Run a query first.")
                    continue
                if len(parts) < 2:
                    print(
                        "Usage: show <thesis|antithesis|synthesis|contradictions|research|metadata|summary|rich>"
                    )
                    continue
                show_what = parts[1].lower()
                if show_what == "thesis":
                    print(latest_result.thesis)
                elif show_what == "antithesis":
                    print(latest_result.antithesis)
                elif show_what == "synthesis":
                    print(latest_result.synthesis)
                elif show_what in ("contradictions", "cons"):
                    print(json.dumps(latest_result.contradictions, indent=2, ensure_ascii=False))
                elif show_what in ("research", "proposals"):
                    print(
                        json.dumps(
                            latest_result.research_proposals,
                            indent=2,
                            ensure_ascii=False,
                        )
                    )
                elif show_what == "metadata":
                    print(json.dumps(latest_result.metadata, indent=2, ensure_ascii=False))
                elif show_what == "summary":
                    print(format_summary(latest_result))
                elif show_what == "rich" and console:
                    print_rich_result(latest_result)
                else:
                    print(f"Unknown section: {show_what}")
            elif command == "set":
                if len(parts) < 3:
                    print("Usage: set <model|provider|debug> <value>")
                    continue
                setting, value = parts[1].lower(), " ".join(parts[2:])
                if setting == "model":
                    set_config_value("model", value)
                    print(f"Model set to: {value}")
                elif setting == "provider":
                    set_config_value("provider", value)
                    print(f"Provider set to: {value}")
                elif setting == "debug":
                    debug_mode = value.lower() in ("true", "on", "1")
                    set_config_value("debug", debug_mode)
                    print(f"Debug mode set to: {debug_mode}")
                else:
                    print(f"Unknown setting: {setting}")
            else:
                # Treat as a new query
                if console:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True,
                    ) as progress:
                        progress.add_task(description="Running dialectic...", total=None)
                        latest_result = await run_dialectic(query=query, debug=debug_mode)
                    print_rich_result(latest_result)
                else:
                    print("Running dialectic...")
                    latest_result = await run_dialectic(query=query, debug=debug_mode)
                    print(format_summary(latest_result))

        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        except Exception as exc:
            print(f"An error occurred: {exc}", file=sys.stderr)


def print_interactive_help() -> None:
    """Print the help message for the interactive mode."""
    print("\nHegelion Interactive Commands:")
    print("  <query>                  - Run a new dialectical query.")
    print("  show <section>           - Show a section of the last result.")
    print(
        "    Sections: thesis, antithesis, synthesis, contradictions, research, metadata, summary, rich"
    )
    print("  set <setting> <value>    - Change a setting for the session.")
    print("    Settings: model, provider, debug (on/off)")
    print("  history                  - Show a history of queries from this session.")
    print("  help                     - Show this help message.")
    print("  exit, quit               - Exit the interactive session.\n")


async def _run(args: argparse.Namespace) -> None:
    if args.interactive:
        await interactive_session()
        return

    if args.query == "setup-mcp":
        print_setup_instructions()
        print("\nTip: use the dedicated 'hegelion-setup-mcp' command for streamlined setup.")
        return

    if args.demo:
        print_cached_example(format_type=args.format)
        return

    if not args.query:
        raise SystemExit("Error: QUERY is required unless --interactive or --demo is specified.")

    try:
        if console and args.format == "rich":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task(description="Synthesizing Truth...", total=None)
                result = await run_dialectic(query=args.query, debug=args.debug)
        else:
            result = await run_dialectic(query=args.query, debug=args.debug)

    except ConfigurationError as exc:
        message = str(exc)
        guidance = (
            "No LLM backend is configured.\n"
            "Run `hegelion --demo` to see a cached example without API keys,\n"
            "or set ANTHROPIC_API_KEY / OPENAI_API_KEY / GOOGLE_API_KEY and HEGELION_PROVIDER."
        )
        # Always print errors to stderr for proper Unix behavior
        print(f"Error: {message}", file=sys.stderr)
        print(guidance, file=sys.stderr)
        raise SystemExit(1)

    # Prepare file output data (always JSON for file writes)
    output_data = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

    # Display based on format
    if args.format == "summary":
        print(format_summary(result))
    elif args.format == "rich" and console:
        print_rich_result(result)
    else:
        print(output_data)

    # Write to file if specified
    if args.output:
        if args.output.suffix == ".jsonl":
            with args.output.open("a", encoding="utf-8") as handle:
                json.dump(result.to_dict(), handle, ensure_ascii=False)
                handle.write("\n")
        else:
            args.output.write_text(output_data, encoding="utf-8")
        print(f"Result saved to {args.output}", file=sys.stderr)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    try:
        asyncio.run(_run(args))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
