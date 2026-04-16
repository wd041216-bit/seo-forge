# Contributing to SEO Forge

First off, thank you for considering contributing to SEO Forge! It's people like you that make this tool better for everyone.

## Quick Links

- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Adding New Templates](#adding-new-templates)
- [Adding New Agents](#adding-new-agents)

## Bug Reports

**Before submitting a bug:**

1. Search existing [Issues](https://github.com/wd041216-bit/seo-forge/issues) to avoid duplicates
2. Verify you're using the latest version
3. Collect relevant information: Python version, OS, error messages

**When filing a bug, include:**

- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error output
- Your `seo-forge.config.json` (remove any sensitive data)

## Feature Requests

We welcome feature requests! Please:

1. Check existing [Issues](https://github.com/wd041216-bit/seo-forge/issues) and [Discussions](https://github.com/wd041216-bit/seo-forge/discussions) first
2. Describe the use case and why it's valuable
3. If possible, suggest how it might work

## Pull Requests

### Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python -m pytest tests/ -v`
6. Commit with clear messages (see conventions below)
7. Push to your fork and open a PR against `main`

### Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new blog template for thought leadership
fix: correct keyword density calculation in scorer
docs: update README with Vercel deployment instructions
refactor: simplify pipeline state management
test: add tests for keyword grading logic
chore: update CI workflow
```

### PR Checklist

- [ ] Code follows project style conventions
- [ ] Tests added/updated and passing
- [ ] No hardcoded secrets or API keys
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventions

## Development Setup

```bash
# Clone your fork
git clone https://github.com/wd041216-bit/seo-forge.git
cd seo-forge

# Run the CLI to verify setup
python scripts/seo_forge.py --help

# Run tests
python -m pytest tests/ -v
```

No `pip install` needed — the project uses only Python standard library.

## Coding Standards

### Python

- Python 3.9+ compatibility
- No external dependencies in core scripts
- Follow PEP 8 style
- Use type hints for function signatures
- Functions should have clear docstrings

### Markdown (Agent & Reference Files)

- Use consistent heading hierarchy (H1 for title, H2 for sections)
- Include clear examples where applicable
- Keep files focused on a single topic
- Use tables for structured data

## Adding New Templates

Blog templates are defined in `references/blog-templates.md`. To add a new one:

1. Choose a unique template ID (e.g., `template_whitepaper`)
2. Define the voice, opening style, and focus
3. Create the 10-section H2 structure
4. List unique elements
5. Add signal detection rules in the Selection Logic table
6. Test by running the pipeline with `--template your_template_id`

### Template Structure

```markdown
## Template N: Name (`template_id`)

**Voice**: Description of writing voice
**Opening**: How the article opens
**Focus**: What the content emphasizes

### H2 Structure
1. Section Title 1
2. Section Title 2
...
10. References

### Unique Elements
- Element 1
- Element 2
```

## Adding New Agents

Agents are defined in `agents/` as Markdown files. Each agent has:

```markdown
# Agent Name

## Role
Brief description of what this agent does

## Capabilities
- Capability 1
- Capability 2

## Process
1. Step 1
2. Step 2

## Output Format
Description of expected output format
```

To register a new agent:

1. Create the agent definition file in `agents/`
2. Reference it in `SKILL.md` at the appropriate pipeline phase
3. Add any supporting reference material in `references/`
4. Test the agent within the pipeline

## Project Structure

```
seo-forge/
├── SKILL.md              # Main pipeline orchestration
├── scripts/              # CLI tools
├── agents/               # AI agent definitions
├── references/           # Knowledge base documents
├── templates/            # Configuration templates
├── tests/                # Test suite
└── .github/              # CI/CD workflows
```

## Code of Conduct

Be respectful, constructive, and inclusive. We're all here to make SEO Forge better.

## Questions?

Open a [Discussion](https://github.com/wd041216-bit/seo-forge/discussions) for questions, ideas, or general chat about SEO Forge.

---

Thank you for contributing! Every PR, issue, and star helps.
