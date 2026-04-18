# Agent Deployment Guide

SEO Forge is designed to run as a portable skill bundle, not as a runtime-specific plugin. Any agent can use it if the agent exposes the capability contract in `skill.json`.

## 1. Validate the Bundle

From the repository root:

```bash
python scripts/seo_forge.py doctor
```

For automation:

```bash
python scripts/seo_forge.py doctor --json
```

The doctor checks Python compatibility, required bundle files, optional deployment files, local `git` / `gh` commands, and common integration environment variables.

## 2. Install Into an Agent

Install to an agent skill directory:

```bash
python scripts/seo_forge.py install-skill --target ~/.codex/skills
python scripts/seo_forge.py install-skill --target ~/.claude/skills
python scripts/seo_forge.py install-skill --target ~/.config/opencode/skills
```

If the directory already exists:

```bash
python scripts/seo_forge.py install-skill --target ~/.codex/skills --overwrite
```

By default the installer copies only the portable skill bundle: `SKILL.md`, `skill.json`, `scripts/`, `agents/`, `references/`, `templates/`, and `docs/`. Generated `expert-forum/` artifacts are excluded unless you pass `--include-expert-forum`.

## 3. Export a Zip Bundle

Use this when an agent runtime cannot read directly from this repository:

```bash
python scripts/seo_forge.py export-skill --output seo-forge-skill.zip
```

The zip omits `.git/`, `.github/`, tests, caches, and generated expert artifacts by default.

## 4. Map Capabilities

SEO Forge needs capabilities, not exact tool names:

| Capability | Required | Examples |
| --- | --- | --- |
| `file_read` / `file_write` | Yes | native file tools |
| `shell` | Yes | bash, terminal, command runner |
| `web_search` | Yes | GLM, Tavily, Exa, Brave, native web search |
| `web_fetch` | Yes | GLM Web Reader, Tavily Extract, Fetch MCP, browser fetch |
| `repo_read` | Optional | GitHub MCP, GLM zread, `gh`, `git clone` |
| `pull_request` | Optional | GitHub MCP, `gh pr create` |
| `deployment_checks` | Optional | GitHub Actions, Vercel, platform-specific checks |

Use `templates/agent-capabilities.json` as the machine-readable mapping template for runtimes that support capability manifests.

## 5. Recommended Environment Variables

Pick one search/fetch provider, then add repository credentials only if publishing is needed:

```bash
export ZHIPU_API_KEY="..."   # GLM search, reader, zread
export TAVILY_API_KEY="..."  # Tavily search/extract alternative
export EXA_API_KEY="..."     # Exa search alternative
export GH_TOKEN="..."        # GitHub CLI and private repo access
```

## 6. Runtime Notes

Codex: install into `~/.codex/skills/seo-forge`; use native web/search tools and GitHub/Vercel plugins where available.

Claude Code: install into `~/.claude/skills/seo-forge`; the included `.mcp.json` works with the GLM default, but Tavily/Exa/Fetch can replace those tools.

OpenCode: install into your OpenCode skills directory and point MCP servers to the providers in `docs/mcp-tools.md`.

Generic agents: read `skill.json`, expose the required capabilities, and invoke `SKILL.md` as the task guide. If an exact MCP tool name is unavailable, map the capability to the closest native equivalent.

## 7. Deployment Rule

Do not fabricate SEO evidence. If a runtime cannot provide web search and page fetch, SEO Forge should stop and request those inputs instead of inventing trends, SERP results, competitor data, or reference URLs.
