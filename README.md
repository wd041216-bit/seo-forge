<div align="center">

# 🔥 SEO Forge

**Universal Autonomous SEO Blog Engine**

_Turn any company or industry into a blog content machine — powered by AI agents._

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-green.svg)](https://github.com/seo-forge/seo-forge)
[![E-E-A-T](https://img.shields.io/badge/Google-E--E--A--T%20Compliant-brightgreen.svg)](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#-features) • [Quick Start](#-quick-start) • [How It Works](#-how-it-works) • [Architecture](#-architecture) • [CLI](#-cli) • [Templates](#-templates) • [Contributing](CONTRIBUTING.md)

</div>

---

## The Problem

Writing SEO blog content is **slow**, **expensive**, and **hard to scale**:

- ❌ Hiring writers costs $200-500+ per article
- ❌ Keyword research takes hours per topic
- ❌ E-E-A-T compliance requires expert knowledge
- ❌ Quality is inconsistent across articles
- ❌ Publishing workflow is manual and error-prone

## The Solution

SEO Forge is a **fully autonomous 10-phase pipeline** that goes from a company name to a published, SEO-optimized blog article — with zero human intervention.

```bash
# One command. That's it.
seo-forge "Your Company" --auto-push
```

**What happens automatically:**
1. 🔍 Discovers trending keywords in your industry
2. 📊 Scores keywords with SERP analysis (S+/S/A+/A/B/C tiers)
3. 📝 Selects from 8 rotating blog templates
4. ✍️ Generates E-E-A-T compliant articles
5. 📏 Scores on a 4-axis quality rubric (0-100)
6. 🔧 Iteratively optimizes until quality threshold (≥90/100)
7. 🚀 Pushes to GitHub + deploys via Vercel

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌍 **Universal** | Works for any company, any industry, any language |
| 🎯 **E-E-A-T First** | Google Experience, Expertise, Authoritativeness, Trustworthiness compliant |
| 📊 **4-Axis Scoring** | SEO Quality, E-E-A-T, Content Depth, Reference Authority |
| 🔄 **8 Templates** | Reviewer, Tutorial, Analyst, Problem-Solver, Beginner's Guide, Storyteller, Comparison, Case Study |
| 🔍 **Keyword Intelligence** | SERP analysis, intent classification, competition scoring, opportunity windows |
| ⚖️ **Honest Content** | Balanced pros/cons, real competitor comparisons, verified references |
| 🤖 **Auto-Push** | GitHub commit + PR + Vercel deployment in one shot |
| 📦 **Zero Dependencies** | Pure Python CLI — no pip install needed |
| 🔁 **Convergence Loop** | Iterates optimize → rescore until quality ≥ 90/100 |
| 🌐 **Multi-Platform** | Next.js, Astro, Hugo, Gatsby, WordPress, Ghost, Framer |

---

## Quick Start

### Prerequisites

- Python 3.9+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or compatible AI agent runtime
- MCP tools: `web-search-prime`, `web-reader`, `zread` (for web research)

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/seo-forge.git
cd seo-forge

# No pip install needed — zero dependencies!
python scripts/seo_forge.py --help
```

### Configuration

Create a `seo-forge.config.json` in your project root:

```json
{
  "company_name": "Your Company",
  "industry": "AI/SaaS",
  "site_url": "https://yourcompany.com",
  "blog_path": "/blog",
  "competitors": ["competitor1.com", "competitor2.com"],
  "target_keywords": ["ai writing tool", "content automation"],
  "language": "en",
  "cta_url": "https://yourcompany.com/signup",
  "brand_voice": "Professional but approachable. Evidence-based."
}
```

### Generate Your First Article

```
# In Claude Code or compatible agent:
/write blog about "AI content tools" for "Your Company"

# Or use batch mode:
/generate 5 blogs for "Your Company" on "AI/SaaS" --auto-push
```

---

## How It Works

### The 10-Phase Pipeline

```
CONFIG → TREND → KEYWORD → OUTLINE → DRAFT
                                        │
                             score < 100│
                                        ▼
        GAP_FILL ← RESCORE ← EDIT ← SCORE ← OPTIMIZE
            │
            │ score ≥ 90 + all checks pass
            ▼
         PUBLISH (GitHub commit + Vercel deploy)
```

| Phase | What It Does |
|-------|-------------|
| **CONFIG** | Parse input, load/create company configuration |
| **TREND** | Discover trending keywords via web search |
| **KEYWORD** | Deep SERP analysis, grade keywords S+ through C |
| **OUTLINE** | Generate article outlines with template selection |
| **DRAFT** | Write full E-E-A-T compliant articles |
| **SCORE** | 4-axis quality scoring (0-100) |
| **OPTIMIZE** | Surgical fixes for underperforming axes |
| **EDIT** | Final polish and quality gate |
| **RESCORE** | Confirm quality ≥ 90/100 (max 3 iterations) |
| **PUBLISH** | Git commit, PR creation, Vercel deployment |

### Quality Scoring

Every article is scored on 4 axes (25 points each, 100 total):

| Axis | Measures | Target |
|------|----------|--------|
| SEO Quality | Keyword density, headings, meta, slug | 22+/25 |
| E-E-A-T | First-person, experience evidence, balance | 20+/25 |
| Content Depth | Word count, FAQs, technical detail | 20+/25 |
| Reference Authority | Sources, URL validity, domain credibility | 22+/25 |

**Articles only publish when total ≥ 90/100.**

---

## Architecture

```
seo-forge/
├── SKILL.md                    # Pipeline orchestration (the "brain")
├── scripts/
│   └── seo_forge.py            # CLI tool for state management
├── agents/                     # AI agent role definitions
│   ├── keyword-hunter.md       # Keyword discovery & SERP analysis
│   ├── content-architect.md    # Outline & article generation
│   ├── quality-scorer.md       # 4-axis scoring engine
│   ├── seo-optimizer.md        # Targeted quality fixes
│   ├── competitor-spy.md       # Competitor research
│   └── publisher.md            # Git commit & deployment
├── references/                 # Knowledge base
│   ├── eeat-framework.md       # Google E-E-A-T compliance
│   ├── keyword-research.md     # Scoring formulas & tiers
│   ├── blog-templates.md       # 8 rotating templates
│   ├── maturity-scoring.md     # Quality rubric details
│   ├── competitor-analysis.md  # Fair comparison framework
│   ├── trusted-domains.md      # Approved reference sources
│   └── deployment.md           # GitHub + Vercel deploy guide
└── templates/
    └── blog-config.json        # JSON Schema for configuration
```

---

## CLI

The `seo_forge.py` CLI manages pipeline state:

```bash
# Initialize a new pipeline
python scripts/seo_forge.py init --domain "yourcompany.com" --topic "AI Tools"

# Record a trending keyword
python scripts/seo_forge.py trend --keyword "ai writing assistant" --intent commercial

# Score a keyword candidate
python scripts/seo_forge.py score-keyword --keyword "ai writing assistant" \
  --potential 8 --validation 7 --difficulty 3 --opportunity 4 \
  --win-prob 65 --roi 70

# Register a new article
python scripts/seo_forge.py article --keyword "ai writing assistant" --template tutorial

# Score an article
python scripts/seo_forge.py score-article --article-id "ai-writing-assistant_20260415" \
  --seo 22 --eeat 23 --depth 21 --refs 24

# Generate a report
python scripts/seo_forge.py report

# View pipeline state
python scripts/seo_forge.py state
```

---

## Templates

8 rotating templates prevent content similarity across articles:

| # | Template | Voice | Best For |
|---|----------|-------|----------|
| 1 | **Deep Reviewer** | Professional, systematic | Product reviews, evaluations |
| 2 | **Tutorial Expert** | Helpful, practical | How-to guides, tutorials |
| 3 | **Industry Analyst** | Authoritative, data-driven | Market analysis, trends |
| 4 | **Problem Solver** | Empathetic, solution-focused | Pain point articles |
| 5 | **Beginner's Guide** | Friendly, encouraging | Introductory content |
| 6 | **Storyteller** | Personal, authentic | Experience narratives |
| 7 | **Deep Comparison** | Objective, structured | A vs B comparisons |
| 8 | **Case Study** | Results-focused, credible | Use case deep dives |

Templates are auto-selected based on keyword intent signals (`how to` → Tutorial, `vs` → Comparison, etc.) and rotated to ensure diversity.

---

## Keyword Grading

Keywords are graded on a tier system:

| Grade | Criteria | Action |
|-------|----------|--------|
| **S+** | Score ≥ 25, Win ≥ 50%, ROI ≥ 55 | Priority target |
| **S** | Score ≥ 20, Win ≥ 50%, ROI ≥ 55 | Strong target |
| **A+** | Score ≥ 15, Win ≥ 50%, ROI ≥ 55 | Good target |
| **A** | Score ≥ 10, Win ≥ 40% | Viable target |
| **B** | Score ≥ 5 | Secondary target |
| **C** | Score < 5 | Deprioritize |

Scoring formula:
```
Final Score = (0.30 × Potential) + (0.20 × Validation) - (0.50 × Difficulty) + Opportunity
```

---

## Safety & Quality

- ✅ All reference URLs verified before inclusion
- ✅ Never fabricates quotes, statistics, or URLs
- ✅ Competitor comparisons against real named competitors only
- ✅ Transparent disclosure of affiliations
- ✅ Limited marketing superlatives
- ✅ Maximum 3 CTA buttons per article
- ✅ Convergence guaranteed (max 3 optimization iterations)

---

## Use Cases

| Who | How |
|-----|-----|
| **Startups** | Generate SEO blog content from day one, no writing team needed |
| **Marketing Teams** | Scale content production 10x with consistent quality |
| **SEO Agencies** | Deliver articles for multiple clients in parallel |
| **Developers** | Auto-publish technical blog posts to your static site |
| **Solo Founders** | Compete with bigger companies on content marketing |

---

## Contributing

We love contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- 🐛 Report bugs via [Issues](https://github.com/your-username/seo-forge/issues)
- 💡 Suggest features via [Discussions](https://github.com/your-username/seo-forge/discussions)
- 🔧 Submit pull requests
- ⭐ Star the repo if you find it useful!

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the AI-powered content era**

[⬆ Back to top](#-seo-forge)

</div>
