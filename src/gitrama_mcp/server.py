"""
Gitrama MCP Server — AI-powered Git intelligence for your IDE.

Works with: Cursor · Claude Desktop · Claude Code · Windsurf · VS Code · Zed
Transport: stdio (default) or streamable-http
"""

import asyncio
import os
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server initialisation
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "gitrama",
    instructions=(
        "AI-powered Git intelligence — smart commits, branch naming, "
        "PR descriptions, changelogs, and stream-based workflow management. "
        "Requires the Gitrama CLI (pip install gitrama)."
    ),
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cwd() -> str:
    return os.environ.get("GTR_CWD", os.getcwd())


async def _run(args: list[str], cwd: Optional[str] = None, timeout: int = 120) -> dict:
    cmd = ["gtr"] + args
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd or _cwd(),
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "success": proc.returncode == 0,
            "stdout": out.decode("utf-8", errors="replace").strip(),
            "stderr": err.decode("utf-8", errors="replace").strip(),
            "returncode": proc.returncode,
        }
    except asyncio.TimeoutError:
        return {"success": False, "stdout": "", "stderr": f"Timed out after {timeout}s", "returncode": -1}
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Gitrama CLI not found. Install: pip install gitrama  |  https://gitrama.ai",
            "returncode": -1,
        }


def _out(result: dict, label: str = "") -> str:
    if result["success"]:
        return result["stdout"] or f"✅ {label or 'Done'}"
    return f"❌ {result['stderr'] or result['stdout'] or 'Unknown error'}"


# ---------------------------------------------------------------------------
# Dispatch — internal CLI argument construction (not part of public interface)
# ---------------------------------------------------------------------------

def _commit_args(message_type: str, context: str, model: str) -> list[str]:
    a = ["commit", "-t", message_type]
    if context:
        a += ["-c", context]
    if model:
        a += ["-m", model]
    a += ["-y"]
    return a


def _ask_args(question: str, scope: str, model: str) -> list[str]:
    a = ["chat", "-q", question]
    if scope and scope != "auto":
        a += ["-s", scope]
    if model:
        a += ["-m", model]
    return a


def _branch_args(name: str, base: str) -> list[str]:
    a = ["branch", name]
    if base:
        a += ["-b", base]
    return a


def _branch_suggest_args(description: str, model: str) -> list[str]:
    a = ["branch", "-g", description]
    if model:
        a += ["-m", model]
    return a


def _pr_args(base: str, model: str) -> list[str]:
    a = ["pr"]
    if base:
        a += ["-b", base]
    if model:
        a += ["-m", model]
    return a


def _changelog_args(since: str, until: str, fmt: str, model: str) -> list[str]:
    a = ["changelog"]
    if since:
        a += ["-s", since]
    if until:
        a += ["-u", until]
    if fmt:
        a += ["-f", fmt]
    if model:
        a += ["-m", model]
    return a


def _quality_args(count: int) -> list[str]:
    return ["commit", "-Q", "-n", str(min(max(count, 1), 50))]


def _stream_args(action: str, name: str = "", description: str = "") -> list[str]:
    a = ["stream", action]
    if name:
        a.append(name)
    if description:
        a += ["-d", description]
    return a


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_commit(
    message_type: str = "conventional",
    context: str = "",
    model: str = "",
) -> str:
    """
    Generate an AI-powered commit message for currently staged changes.

    Analyzes staged files and produces a high-quality commit message.
    Requires files to be staged first (git add).

    Args:
        message_type: Commit style — "conventional" (default), "detailed", or "simple".
        context: Optional hint to guide the AI (e.g., "fixing auth bug").
        model: Optional model override (e.g., "gpt-4o", "ollama/llama3").
    """
    result = await _run(_commit_args(message_type, context, model))
    return _out(result, "Commit created")


@mcp.tool()
async def gitrama_stage_and_commit(
    files: str = ".",
    message_type: str = "conventional",
    context: str = "",
    model: str = "",
) -> str:
    """
    Stage files and create an AI-powered commit in one step.

    Args:
        files: Files to stage — "." for all (default), or space-separated paths.
        message_type: Commit style — "conventional", "detailed", or "simple".
        context: Optional hint to guide the AI.
        model: Optional model override.
    """
    file_list = files.split() if files != "." else ["."]
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "add", *file_list,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=_cwd(),
        )
        await proc.communicate()
    except Exception as e:
        return f"❌ Failed to stage files: {e}"

    return await gitrama_commit(message_type=message_type, context=context, model=model)


@mcp.tool()
async def gitrama_commit_quality(count: int = 10) -> str:
    """
    Analyze the quality of recent commit messages.

    Scores commits on clarity, specificity, and conventional format adherence.

    Args:
        count: Number of recent commits to analyze (default: 10, max: 50).
    """
    result = await _run(_quality_args(count))
    return _out(result, "Commit quality analysis complete")


@mcp.tool()
async def gitrama_ask(
    question: str,
    scope: str = "auto",
    model: str = "",
) -> str:
    """
    Ask a natural language question about your repository.

    Uses Gitrama's intelligence engine to answer questions about ownership,
    history, risk, recent changes, and code purpose.

    Example questions:
    - "Who owns the auth module?"
    - "What's the riskiest file in this repo?"
    - "What changed in the last 3 days?"
    - "Summarize what happened on this branch"

    Args:
        question: Natural language question about your repository.
        scope: How much repo history to include — "auto", "branch", "full", or "staged".
        model: Optional model override.
    """
    result = await _run(_ask_args(question, scope, model), timeout=180)
    return _out(result, "Question answered")


@mcp.tool()
async def gitrama_branch(name: str, base: str = "") -> str:
    """
    Create and check out a new git branch.

    Args:
        name: Branch name (e.g., "feat/user-auth", "fix/payment-timeout").
        base: Base branch to create from (default: current branch).
    """
    result = await _run(_branch_args(name, base))
    return _out(result, f"Branch '{name}' created")


@mcp.tool()
async def gitrama_branch_suggest(description: str, model: str = "") -> str:
    """
    Get AI-suggested branch names based on a task description.

    Args:
        description: What you're working on (e.g., "add OAuth2 user authentication").
        model: Optional model override.
    """
    result = await _run(_branch_suggest_args(description, model))
    return _out(result, "Branch suggestions generated")


@mcp.tool()
async def gitrama_pr(base: str = "", model: str = "") -> str:
    """
    Generate an AI-powered pull request description.

    Analyzes the diff between the current branch and the base branch.

    Args:
        base: Target branch for the PR (default: main or master).
        model: Optional model override.
    """
    result = await _run(_pr_args(base, model))
    return _out(result, "PR description generated")


@mcp.tool()
async def gitrama_changelog(
    since: str = "",
    until: str = "",
    format: str = "markdown",
    model: str = "",
) -> str:
    """
    Generate an AI-powered changelog from commit history.

    Args:
        since: Start ref — tag, branch, or commit hash (e.g., "v1.0.0").
        until: End ref (default: HEAD).
        format: Output format — "markdown" (default) or "json".
        model: Optional model override.
    """
    result = await _run(_changelog_args(since, until, format, model))
    return _out(result, "Changelog generated")


@mcp.tool()
async def gitrama_stream_status() -> str:
    """
    Show the current Gitrama stream (workflow context).

    Returns the active stream name, description, and associated branch.
    """
    result = await _run(_stream_args("status"))
    return _out(result, "Stream status retrieved")


@mcp.tool()
async def gitrama_stream_switch(name: str, description: str = "") -> str:
    """
    Switch to a different Gitrama stream (workflow context).

    Args:
        name: Stream name (e.g., "auth-refactor", "payment-v2").
        description: Optional description of the stream's purpose.
    """
    result = await _run(_stream_args("switch", name, description))
    return _out(result, f"Switched to stream '{name}'")


@mcp.tool()
async def gitrama_stream_list() -> str:
    """
    List all Gitrama streams in the current repository.

    Shows all streams with names, descriptions, and branches.
    The active stream is highlighted.
    """
    result = await _run(_stream_args("list"))
    return _out(result, "Streams listed")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    transport = os.environ.get("GTR_MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.settings.host = os.environ.get("GTR_MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("GTR_MCP_PORT", "8765"))
        mcp.run(transport="streamable-http")
    else:
        print(f"Unknown transport: {transport}. Use 'stdio' or 'streamable-http'.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
