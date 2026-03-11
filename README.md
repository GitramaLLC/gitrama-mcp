# 🌿 Gitrama MCP Server

> AI-powered Git intelligence for your IDE — smart commits, branch names, PR descriptions, changelogs, and workflow management.

[![PyPI](https://img.shields.io/pypi/v/gitrama-mcp)](https://pypi.org/project/gitrama-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/gitrama-mcp)](https://pypi.org/project/gitrama-mcp/)
[![License](https://img.shields.io/badge/License-BSL%201.1-green.svg)](https://github.com/GitramaLLC/gitrama-mcp/blob/main/LICENSE)

## What is this?

Gitrama MCP Server exposes [Gitrama](https://gitrama.ai)'s intelligence engine as **11 MCP tools** that any AI assistant can use. Instead of switching to a terminal, your AI assistant calls the tools directly — analyzing your code, generating commit messages, reviewing diffs, and managing your workflow without breaking your focus.

**Works with:** Cursor · Claude Desktop · Claude Code · Windsurf · VS Code (Copilot) · Zed · any MCP-compatible client

---

## Install (< 60 seconds)

### Step 1 — Install the package

```bash
pip install gitrama-mcp
```

Or with uv:

```bash
uv pip install gitrama-mcp
```

### Step 2 — Connect to your IDE

**Cursor** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```

**Claude Desktop** — add to `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add gitrama gitrama-mcp
```

**VS Code (Copilot)** — add to `.vscode/settings.json`:

```json
{
  "mcp": {
    "servers": {
      "gitrama": {
        "command": "gitrama-mcp"
      }
    }
  }
}
```

**Windsurf** — add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```

**Zed** — add to Zed settings (`⌘,`):

```json
{
  "context_servers": {
    "gitrama": {
      "command": {
        "path": "gitrama-mcp"
      }
    }
  }
}
```

### Step 3 — Done

Ask your AI: *"Commit my staged changes"* — and watch it call `gitrama_commit`.

---

## Tools

### Repository Intelligence

| Tool | What it does |
|------|-------------|
| `gitrama_ask` | Ask any question about your repo — ownership, history, risk, recent changes |

### Commit Intelligence

| Tool | What it does |
|------|-------------|
| `gitrama_commit` | Generate an AI commit message for staged changes |
| `gitrama_stage_and_commit` | Stage files and commit in one step |
| `gitrama_commit_quality` | Score the quality of recent commit messages |

### Branch Management

| Tool | What it does |
|------|-------------|
| `gitrama_branch` | Create a new branch |
| `gitrama_branch_suggest` | Get AI-suggested branch names from a description |

### PR & Changelog

| Tool | What it does |
|------|-------------|
| `gitrama_pr` | Generate a PR description from your branch diff |
| `gitrama_changelog` | Generate a changelog between two refs |

### Stream (Workflow) Management

| Tool | What it does |
|------|-------------|
| `gitrama_stream_status` | Show your current workflow stream |
| `gitrama_stream_switch` | Switch to a different stream |
| `gitrama_stream_list` | List all streams in the repo |

---

## Tool Details

### `gitrama_ask`

Ask a natural language question about your repository.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | *required* | Any question about your repo |
| `scope` | string | `"auto"` | History depth: `"auto"`, `"branch"`, `"full"`, or `"staged"` |
| `model` | string | `""` | AI model override |

**Example prompts:**
- *"Who owns the auth module?"*
- *"When did we last touch the payment logic?"*
- *"What's the riskiest file right now?"*
- *"What changed in the last 3 days?"*
- *"Explain what src/utils/retry.py does"*

---

### `gitrama_commit`

Generate an AI-powered commit message for staged changes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message_type` | string | `"conventional"` | Style: `"conventional"`, `"detailed"`, or `"simple"` |
| `context` | string | `""` | Optional hint to guide the AI |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Commit my changes — context: refactoring the payment module"*

---

### `gitrama_stage_and_commit`

Stage files and commit in one step.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `files` | string | `"."` | Files to stage (`.` for all, or space-separated paths) |
| `message_type` | string | `"conventional"` | Commit style |
| `context` | string | `""` | Optional hint |
| `model` | string | `""` | AI model override |

---

### `gitrama_commit_quality`

Score the quality of recent commit messages.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | `10` | Commits to analyze (1–50) |

**Example prompt:** *"How good are our last 20 commit messages?"*

---

### `gitrama_branch_suggest`

Get AI-suggested branch names for a task.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | *required* | What you're working on |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Suggest a branch name for adding OAuth2 support"*

---

### `gitrama_pr`

Generate a PR description from your branch diff.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base` | string | `""` | Target branch (default: main/master) |
| `model` | string | `""` | AI model override |

---

### `gitrama_changelog`

Generate a changelog between two refs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `since` | string | `""` | Start ref (tag, branch, or hash) |
| `until` | string | `""` | End ref (default: HEAD) |
| `format` | string | `"markdown"` | `"markdown"` or `"json"` |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Generate a changelog since v1.0.0"*

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GTR_CWD` | current directory | Working directory for git operations |
| `GTR_MCP_TRANSPORT` | `"stdio"` | Transport: `"stdio"` or `"streamable-http"` |
| `GTR_MCP_HOST` | `"0.0.0.0"` | Host (HTTP transport only) |
| `GTR_MCP_PORT` | `"8765"` | Port (HTTP transport only) |

### HTTP Transport (CI/CD)

```bash
GTR_MCP_TRANSPORT=streamable-http GTR_MCP_PORT=8765 gitrama-mcp
```

---

## Requirements

- Git installed and in PATH
- A Gitrama API key ([get one at gitrama.ai](https://gitrama.ai))

Set your key after installing:

```bash
gtr setup
```

Or to use a local model:

```bash
gtr setup --provider ollama
```

---

## License

Business Source License 1.1. Free for individual and non-competing use.  
See [LICENSE](https://github.com/GitramaLLC/gitrama-mcp/blob/main/LICENSE) for full terms.

The Gitrama intelligence engine this server connects to is proprietary.  
The MCP integration layer is source-available under BSL 1.1.

---

Built by [Gitrama LLC](https://gitrama.ai) · [gitrama.ai](https://gitrama.ai)

🌿
