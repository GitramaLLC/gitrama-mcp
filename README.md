# 🌿 Gitrama MCP Server
 
> AI-powered Git intelligence for your IDE — smart commits, branch names, PR descriptions, diffs, code review, push, and workflow management.
 
[![PyPI](https://img.shields.io/pypi/v/gitrama-mcp)](https://pypi.org/project/gitrama-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/gitrama-mcp)](https://pypi.org/project/gitrama-mcp/)
![License: Proprietary](https://img.shields.io/badge/License-Proprietary-1A7A4A.svg)
 
## What is this?
 
Gitrama MCP Server exposes [Gitrama](https://gitrama.ai)'s CLI as **15 MCP tools** that any AI assistant can use. Instead of typing `gtr commit` in your terminal, your AI assistant calls the tool directly — analyzing your code changes, generating commit messages, suggesting branch names, reviewing code, and more.
 
**Works with:** Cursor · Claude Desktop · Claude Code · Windsurf · VS Code · Zed · any MCP-compatible client
 
---
 
## What's new in v1.3.2
 
- **5 new tools** — `gitrama_scan`, `gitrama_diff`, `gitrama_review`, `gitrama_status`, and `gitrama_push`
- **Version surfaced from health check** — `gitrama_health` now returns the MCP server version so you can confirm exactly what's running
- **Interactive HTML diff panel** — `gitrama_diff` launches a browser panel with risk-annotated diffs, churn rates, coupling context, and contributor info overlaid on every changed file
- **Push from chat** — `gitrama_push` supports upstream tracking, force-with-lease, and auto-resolves the current branch
- Tool count updated from 10 → 15
 
---
 
## Install (< 60 seconds)
 
### Step 1: Install the package
 
```bash
pip install gitrama-mcp
```
 
Or with uv:
```bash
uv pip install gitrama-mcp
```
 
This installs both the MCP server and the `gitrama` CLI.
 
### Step 2: Connect to your IDE
 
<details>
<summary><b>Cursor</b></summary>
 
Add to `.cursor/mcp.json` in your project (or global settings):
 
```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>
 
<details>
<summary><b>Claude Desktop</b></summary>
 
Add to `claude_desktop_config.json`:
 
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
 
```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>
 
<details>
<summary><b>Claude Code</b></summary>
 
```bash
claude mcp add gitrama gitrama-mcp
```
</details>
 
<details>
<summary><b>VS Code</b></summary>
 
Add to `.vscode/mcp.json`:
 
```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>
 
<details>
<summary><b>Windsurf</b></summary>
 
Add to `~/.codeium/windsurf/mcp_config.json`:
 
```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>
 
<details>
<summary><b>Zed</b></summary>
 
Add to Zed settings (`⌘,`):
 
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
</details>
 
### Step 3: Done.
 
Ask your AI: *"Commit my staged changes"* — and watch it call `gitrama_commit`.
 
---
 
## Tools (15)
 
### Health & Diagnostics
 
| Tool | Description |
|------|-------------|
| `gitrama_health` | Check AI server health and confirm MCP server version |
 
### Repository Intelligence
 
| Tool | Description |
|------|-------------|
| `gitrama_ask` | Ask any question about your repo — ownership, history, risk, changes |
| `gitrama_scan` | Full structural health scan — continuity risk, boundary entropy, recurrence patterns |
| `gitrama_status` | Show working tree status with AI interpretation |
 
### Code Review & Diff
 
| Tool | Description |
|------|-------------|
| `gitrama_diff` | Risk-annotated diff with interactive HTML panel — churn, coupling, contributor context |
| `gitrama_review` | AI code review before you push — security, correctness, risk, coupling |
 
### Commit Intelligence
 
| Tool | Description |
|------|-------------|
| `gitrama_commit` | Generate an AI commit message for staged changes |
| `gitrama_stage_and_commit` | Stage files + commit in one step |
| `gitrama_unstage` | Remove files from staging without discarding changes |
 
### Branch & Push Management
 
| Tool | Description |
|------|-------------|
| `gitrama_branch` | Create a branch from a natural language description |
| `gitrama_push` | Push current branch to remote with upstream and force-with-lease support |
 
### PR & Changelog
 
| Tool | Description |
|------|-------------|
| `gitrama_pr` | Generate a PR description from branch diff |
| `gitrama_changelog` | Generate a changelog between refs |
 
### Stream (Workflow) Management
 
| Tool | Description |
|------|-------------|
| `gitrama_stream_status` | Show current workflow stream |
| `gitrama_stream_switch` | Switch to a different stream |
| `gitrama_stream_list` | List all streams in the repo |
 
---
 
## Tool Details
 
### `gitrama_health`
 
Check AI server connectivity and confirm the running MCP server version.
 
**Example prompt:** *"Run a gitrama health check"*
 
**Example output:**
```
✅ AI server is healthy!
   🤖 Model: grok-4.20-reasoning
   🌐 Connected to: https://api.x.ai/v1
 
🔖 Gitrama MCP Server: v1.3.2
```
 
---
 
### `gitrama_scan`
 
Run a full structural health scan of the repository. Scores every file for continuity risk, boundary entropy, and recurrence patterns. Results are cached in `last_scan.json` for use by `gtr diff` and `gtr review`.
 
**Example prompt:** *"Run a full gitrama scan of my repo"*
 
---
 
### `gitrama_diff`
 
Show a risk-annotated diff of current changes. Opens an **interactive HTML browser panel** with Gitrama's structural intelligence overlaid — risk scores, churn rates, coupling gaps, and contributor context for every changed file.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | string | `""` | Branch or commit to diff against |
| `staged` | bool | `false` | Diff staged changes only |
 
**Example prompts:**
- *"Show me a diff of my staged changes"*
- *"Diff my branch against main"*
 
---
 
### `gitrama_review`
 
Run an AI code review on current changes **before committing**. Returns severity-graded findings — security, correctness, risk, coupling — plus a verdict and suggested commit message.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `"staged"` | `"staged"`, `"uncommitted"`, `"quick"`, `"full"` |
 
**Example prompts:**
- *"Review my staged changes"*
- *"Do a full review of all my uncommitted changes"*
 
---
 
### `gitrama_push`
 
Push the current branch to a remote repository. Uses `--force-with-lease` for safe force pushes and auto-resolves the current branch if none is specified.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `remote` | string | `"origin"` | Remote to push to |
| `branch` | string | `""` | Branch to push (default: current branch) |
| `force` | bool | `false` | Force push with `--force-with-lease` |
| `set_upstream` | bool | `false` | Set upstream tracking branch (`-u`) |
 
**Example prompts:**
- *"Push my changes"*
- *"Push this branch and set upstream"*
- *"Force push the current branch"*
 
---
 
### `gitrama_status`
 
Show the working tree status with AI interpretation of staged, unstaged, and untracked files.
 
**Example prompt:** *"What's my current git status?"*
 
---
 
### `gitrama_ask`
 
Ask a natural language question about your repository. Gitrama analyzes commit history, file structure, blame data, and diffs to answer.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | *required* | Any question about your repo |
| `stream` | string | `""` | Optional stream context override |
| `deep` | bool | `false` | Enable full repo history access |
 
**Example prompts:**
- *"Who owns the auth module?"*
- *"What's the riskiest file in this repo?"*
- *"What changed in the last 3 days?"*
- *"Explain the purpose of src/utils/retry.py"*
 
---
 
### `gitrama_commit`
 
Generate an AI-powered commit message for staged changes.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | string | `""` | Optional custom message (skips AI generation) |
 
**Example prompt:** *"Commit my staged changes"*
 
---
 
### `gitrama_stage_and_commit`
 
Stage files and commit in one step.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `files` | string | `"."` | Files to stage (`.` for all, or space-separated paths) |
| `message` | string | `""` | Optional custom message |
 
**Example prompt:** *"Stage and commit all my changes"*
 
---
 
### `gitrama_unstage`
 
Remove files from the staging area without discarding changes.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `files` | string | `""` | Space-separated file paths to unstage |
| `all_files` | bool | `false` | Unstage everything currently staged |
 
**Example prompt:** *"Unstage src/auth.py"*
 
---
 
### `gitrama_branch`
 
Generate an AI-powered branch name from a description and optionally create it.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | *required* | What you're working on |
| `create` | bool | `true` | Create and switch to the branch |
 
**Example prompts:**
- *"Create a branch for adding OAuth2 support"*
- *"Suggest a branch name for fixing the payment timeout, don't create it"*
 
---
 
### `gitrama_pr`
 
Generate a PR description from the diff between the current branch and base.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base` | string | `""` | Target branch (default: main/master) |
 
**Example prompt:** *"Write a PR description for this branch"*
 
---
 
### `gitrama_changelog`
 
Generate a changelog between refs.
 
**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `since` | string | `""` | Start ref (tag, branch, hash) |
| `until` | string | `""` | End ref (default: HEAD) |
| `format` | string | `"markdown"` | `"markdown"` or `"json"` |
 
**Example prompt:** *"Generate a changelog since v1.1.4"*
 
---
 
### Stream Tools
 
| Tool | Parameters | Example prompt |
|------|-----------|----------------|
| `gitrama_stream_status` | none | *"What stream am I on?"* |
| `gitrama_stream_switch` | `name`, `description` | *"Switch to the hotfix stream"* |
| `gitrama_stream_list` | none | *"List all my gitrama streams"* |
 
---
 
## The v1.3.2 Workflow
 
With all 15 tools connected, your full dev loop runs from chat:
 
```
describe intent  →  stream switch
write code
ask gitrama what changed  →  diff (HTML panel)
review before push
commit with AI message
push
PR description generated
```
 
No terminal. No manual git commands.
 
---
 
## Configuration
 
### Environment Variables
 
| Variable | Default | Description |
|----------|---------|-------------|
| `GTR_CWD` | `os.getcwd()` | Working directory for git operations |
| `GTR_MCP_TRANSPORT` | `"stdio"` | Transport: `"stdio"` or `"streamable-http"` |
| `GTR_MCP_HOST` | `"0.0.0.0"` | HTTP host (when using streamable-http) |
| `GTR_MCP_PORT` | `"8765"` | HTTP port (when using streamable-http) |
 
### HTTP Transport (for CI/CD)
 
```bash
GTR_MCP_TRANSPORT=streamable-http GTR_MCP_PORT=8765 gitrama-mcp
```
 
Then connect your client to `http://localhost:8765/mcp`.
 
---
 
## Requirements
 
- Python 3.10+
- Git installed and in PATH
- A Gitrama API key or local Ollama instance
 
Set your API key:
```bash
gtr config --key YOUR_API_KEY
```
 
Or use a local model:
```bash
gtr config --provider ollama --model llama3
```
 
---
 
## Development
 
```bash
git clone https://github.com/ahmaxdev/gitrama-mcp.git
cd gitrama-mcp
pip install -e ".[dev]"
 
# Test with MCP Inspector
mcp dev src/gitrama_mcp/server.py
```
 
---
 
## License
 
Proprietary — see [LICENSE](LICENSE).
 
---
 
Built by [Alfonso Harding](https://www.linkedin.com/in/alfonso-h-47396b5/) · [gitrama.ai](https://gitrama.ai)
 
🌿