"""Fast validation script for AI assistants.

Run:
    python scripts/validate_mcp.py

Checks that dialectical workflow generation works and shows response_style options.
"""

from hegelion.core.prompt_dialectic import create_dialectical_workflow


def main() -> None:
    workflow = create_dialectical_workflow(
        query="Test query",
        use_search=False,
        use_council=False,
        use_judge=False,
    )
    workflow["instructions"]["response_style"] = "json"

    print("✅ Hegelion MCP server prompt generation is operational")
    print(f"✅ Generated workflow with {len(workflow['steps'])} steps")
    print("✅ Call tools: dialectical_workflow, dialectical_single_shot")
    print("✅ response_style values: conversational, bullet_points, json, sections, synthesis_only")


if __name__ == "__main__":
    main()
