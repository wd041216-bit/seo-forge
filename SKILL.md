---
name: seo-forge
description: >-
  Universal autonomous SEO blog forge for any company and any industry.
  Auto-discovers trending keywords via web search, generates SEO-optimized
  blog articles with E-E-A-T compliance, 8 rotating content templates,
  competitor analysis, keyword density tuning, authority references, and
  auto-pushes finished blog to GitHub / Vercel.
  Combines expert-distiller pipeline patterns with industrial-grade SEO
  optimization distilled from production-grade SEO systems.
  TRIGGER when: user says "seo blog", "write blog", "blog forge",
  "auto blog", "seo optimize", "keyword research blog", "generate article",
  or provides a company/industry name wanting SEO content.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Agent
  - mcp__web-search-prime__web_search_prime
  - mcp__web_reader__webReader
  - mcp__zread__read_file
  - mcp__zread__get_repo_structure
model: opus
argument-hint: "<company-or-industry> [--site URL] [--keywords k1,k2] [--count N] [--auto-push] [--lang en|zh|...]"
---

# SEO Forge — Universal Autonomous Blog Engine

Turn any company or industry into a blog content machine. The pipeline discovers trending keywords, generates SEO-optimized articles, scores quality on a 4-axis rubric, iterates until the quality council awards 100/100, then pushes to GitHub / Vercel.

## Core Principles

1. **Universal**: Works for any company, any industry, any language
2. **E-E-A-T First**: Every article meets Google's Experience, Expertise, Authoritativeness, Trustworthiness standards
3. **Evidence-Based**: All claims backed by real data, no fabricated quotes or URLs
4. **Template Diversity**: 8 rotating templates prevent content similarity
5. **Auto-Push**: Finished articles deploy to GitHub + Vercel automatically

## Configuration

Before first use, create a blog config in your project root:

```json
{
  "company_name": "Your Company",
  "industry": "your-industry",
  "site_url": "https://yourcompany.com",
  "blog_path": "/blog",
  "competitors": ["competitor1.com", "competitor2.com"],
  "target_keywords": ["keyword1", "keyword2"],
  "language": "en",
  "cta_url": "https://yourcompany.com/signup",
  "author_bio": "Written by the Your Company team.",
  "brand_voice": "Professional but approachable. Evidence-based. Honest about limitations.",
  "trusted_reference_domains": [
    "wikipedia.org", "reuters.com", "bloomberg.com",
    "techcrunch.com", "wired.com", "hbr.org"
  ]
}
```

Save as `seo-forge.config.json` in your project root. The skill auto-detects it.

## Autonomous Pipeline: 10 Phases

```
CONFIG → TREND → KEYWORD → OUTLINE → DRAFT
                                        │
                             score < 100│
                                        ▼
        GAP_FILL ← RESCORE ← EDIT ← SCORE ← OPTIMIZE
            │
            │ score = 100 + all checks pass
            ▼
         PUBLISH (GitHub commit + Vercel deploy)
```

### Phase 1: CONFIG

**Goal**: Parse user input, load or create blog configuration.

**Steps**:
1. Parse the argument: `<company-or-industry>`
2. Look for existing `seo-forge.config.json` in the current directory
3. If not found, generate one interactively:
   - Use web search to identify the company's industry, competitors, and positioning
   - Infer target keywords from industry analysis
   - Write the config file
4. Validate all required fields are present

**Output**: `seo-forge.config.json` with complete company/industry profile

**Transition**: → TREND

### Phase 2: TREND

**Goal**: Auto-discover trending keywords and hot topics in the industry.

**Steps**:
1. Use `mcp__web-search-prime__web_search_prime` to search for:
   - `"[industry] trends [current_year]"`
   - `"[industry] blog topics trending"`
   - `"[industry] keywords high volume"`
   - `"what is trending in [industry] this month"`
2. Read top results with `mcp__web_reader__webReader`
3. Extract keyword candidates:
   - Search volume indicators (mention frequency, Google Trends hints)
   - Intent classification (informational, commercial, transactional, navigational)
   - Competition level (SERP analysis signals)
4. Cross-reference with company's target keywords from config
5. Score and rank keyword candidates:
   ```
   Score = (0.30 × TrendSignal) + (0.25 × Relevance) + (0.25 × LowCompetition) + (0.20 × IntentMatch)
   ```

**Agent**: Use `keyword-hunter` agent profile for structured discovery

**Output**: Ranked keyword list with scores, intent, and suggested angles

**Transition**: → KEYWORD

### Phase 3: KEYWORD

**Goal**: Deep-evaluate top keyword candidates with SERP analysis.

**Steps**:
1. For top 10-15 candidates from Phase 2:
   - Search for each keyword on Google via web search tools
   - Analyze top 10 results: domain authority, content type, freshness
   - Identify content gaps (missing perspectives, outdated content)
   - Calculate opportunity score with circuit breaker logic
2. Grade each keyword:
   - **S-tier**: Final Score ≥ 20, WinProbability ≥ 50, ROIPotential ≥ 55
   - **A-tier**: Final Score ≥ 10, WinProbability ≥ 40
   - **B-tier**: Final Score ≥ 5
   - **C-tier**: Final Score < 5 (deprioritize)
3. Select top N keywords (default: 5) based on `--count` flag

**Scoring Formula**:
```
Final Score = (0.30 × Potential) + (0.20 × Validation) - (0.50 × RealDifficulty) + OpportunityWindow
```

**Agent**: Use `keyword-hunter` agent for SERP analysis

**Output**: Final keyword selection with opportunity analysis

**Transition**: → OUTLINE

### Phase 4: OUTLINE

**Goal**: Generate article outlines for each selected keyword.

**Steps**:
1. Select blog template (see `references/blog-templates.md`):
   - Smart selection based on keyword intent and content type
   - Rotate templates to avoid similarity across articles
   - 8 templates available: Reviewer, Tutorial, Analyst, Problem-Solver, Beginner's Guide, Storyteller, Comparison, Case Study
2. Generate outline following template structure:
   - H2 section order per template
   - Writing voice and opening style per template
   - Comparison targets (company vs competitors from config)
3. Plan keyword distribution:
   - Main keyword in title (H1), 2+ H2 headings, 1+ H3 heading, meta description (first 60 chars)
   - Secondary keywords woven into body text
   - Long-tail keywords in FAQ questions and subheadings

**Agent**: Use `content-architect` agent for outline generation

**Output**: Article outline with template assignment and keyword placement map

**Transition**: → DRAFT

### Phase 5: DRAFT

**Goal**: Generate the full blog article from the outline.

**Steps**:
1. Generate article following the outline and template:
   - Follow E-E-A-T framework (see `references/eeat-framework.md`)
   - Use first-person perspective (15-20+ occurrences of I/my/we/our)
   - Include specific testing/experience timeline
   - Provide balanced pros (3-5) and cons (2-3)
   - Include technical specifications relevant to the industry
   - Add comparison section vs named competitors from config
2. Generate supporting elements:
   - SEO-optimized title (contains main keyword)
   - Meta description (120-160 characters, keyword in first 60 chars)
   - URL slug (≤6 words, keyword-rich)
   - Image alt text for cover image
3. Structure requirements:
   - NO H1 in body (title is separate)
   - Paragraph length: 150-300 words each
   - At least 6 FAQ questions with natural phrasing
   - References section with 4-6 authoritative sources (real URLs, `<a href>` format)
   - Maximum 3 CTA buttons total
4. Readability requirements (see "Blog Readability Standards" section):
   - Every H2 and H3 gets a slugified `id` attribute for TOC linking
   - Tables use proper `<thead>`/`<tbody>` structure with header styling
   - For CJK languages (`--lang zh|ja|ko`), paragraphs are wrapped in `<p>` tags suitable for CSS `text-indent`
   - Articles > 2000 words include a TOC data structure (array of heading items with id, text, level)

**Agent**: Use `content-architect` agent for content generation

**Output**: Complete HTML blog article with title, meta, slug, and content

**Transition**: → SCORE

### Phase 6: SCORE

**Goal**: Score the article on 4 quality axes (0-25 each, total 0-100).

**Axes**:
| Axis | Measures | Target |
|------|----------|--------|
| SEO Quality (0-25) | Keyword density, heading optimization, meta tags, slug quality | 22+ |
| E-E-A-T Compliance (0-25) | First-person usage, experience evidence, balanced perspective, transparency | 20+ |
| Content Depth (0-25) | Word count, FAQ coverage, technical detail, comparison depth | 20+ |
| Readability & Structure (0-25) | Heading hierarchy with IDs, table visualization, paragraph formatting, TOC presence | 20+ |

**Steps**:
1. Score each axis independently:
   - **SEO Quality**: Check keyword density (1-2% target), heading keyword presence, meta optimization
   - **E-E-A-T Compliance**: Count first-person usage, verify experience claims, check pros/cons balance
   - **Content Depth**: Verify word count increase, FAQ count, technical detail presence
   - **Readability & Structure**: Verify heading IDs present, tables properly styled, paragraph formatting, TOC for long articles
2. Compute total score (sum of 4 axes)
3. Generate detailed scoring report per axis with specific improvement suggestions

**Agent**: Use `quality-scorer` agent for objective scoring

**Output**: `scoring_report.json` with per-axis scores, total, and improvement suggestions

**Transition**:
- Total = 100 → PUBLISH
- Total < 100 → OPTIMIZE

### Phase 7: OPTIMIZE

**Goal**: Fix specific quality issues identified by scoring.

**Steps**:
1. Read the scoring report
2. For each axis below target:
   - **SEO Quality**: Adjust keyword density, add keywords to headings, fix meta
   - **E-E-A-T**: Add more first-person language, include experience evidence, balance pros/cons
   - **Content Depth**: Expand thin sections, add FAQ questions, include technical details
   - **Readability & Structure**: Add heading IDs, improve table styling, add TOC, fix paragraph formatting
3. Apply targeted fixes (not full rewrite — surgical edits only)
4. Validate URL references:
   - HEAD request verification for all reference URLs
   - Remove broken URLs, replace with alternatives
   - Ensure at least 2 references have verified URLs

**Agent**: Use `seo-optimizer` agent for targeted optimization

**Output**: Optimized article with specific fixes applied

**Transition**: → SCORE (re-score after optimization)

### Phase 8: EDIT

**Goal**: Final polish and quality gate.

**Steps**:
1. Run final checks:
   - Content completeness (not truncated)
   - HTML structure validity
   - No self-referential company links in References
   - CTA buttons preserved and functional
   - Image placeholders resolved (if applicable)
   - No AI-detection red flags (natural language, varied sentence structure)
   - **Readability check**: All H2/H3 headings have `id` attributes, tables have `<thead>`/`<tbody>` structure, paragraphs are properly spaced
   - **TOC check**: Articles > 2000 words have a generated Table of Contents
   - **Table check**: All data tables use proper header styling (not plain unstyled tables)
2. Run post-optimization fixes:
   - Keyword density fine-tuning (target exactly 1-2%)
   - Meta description length enforcement (strictly 120-160 chars)
   - Reference URL normalization
3. Generate final optimization report

**Agent**: Use `quality-scorer` agent for final review

**Output**: Final polished article ready for publication

**Transition**: → RESCORE

### Phase 9: RESCORE

**Goal**: Final scoring pass to confirm quality threshold.

**Steps**:
1. Re-run all 4-axis scoring on the edited article
2. If total ≥ 90 (practical threshold for publication):
   - Generate publication-ready report
   - → PUBLISH
3. If total < 90:
   - Identify remaining gaps
   - → OPTIMIZE (max 3 iterations total)
4. After 3 iterations without convergence:
   - Publish best version with quality report
   - Flag for manual review

**Output**: Final scoring report and publication decision

**Transition**: → PUBLISH (or manual review)

### Phase 10: PUBLISH

**Goal**: Push finished blog to GitHub and deploy via Vercel.

**Steps**:
1. Format the article for the target platform:
   - Markdown format (with frontmatter for static site generators)
   - Or HTML format (for CMS integration)
2. Commit to GitHub:
   ```bash
   git checkout -b seo-forge/<keyword-slug>
   git add <blog_file>
   git commit -m "feat(seo-forge): add blog '<title>'

   SEO Score: <score>/100
   Keyword: <keyword>
   Template: <template_name>
   Word Count: <count>"
   git push -u origin seo-forge/<keyword-slug>
   ```
3. Create Pull Request:
   ```bash
   gh pr create --title "SEO Blog: <title>" --body "<scoring_report>"
   ```
4. If Vercel is configured, the PR auto-triggers a preview deployment
5. Merge the PR to trigger production deployment

**Agent**: Use `publisher` agent for deployment

**Output**: GitHub PR URL + Vercel preview URL

**Transition**: Terminal (pipeline complete)

## Single Article Mode (Quick)

For generating a single article without the full pipeline:

```
Invoke skill with: "write blog about [topic] for [company]"
```

The skill will:
1. Load/create config
2. Generate keyword analysis (quick mode)
3. Select template → Generate outline → Draft
4. Score → Optimize → Publish

## Batch Mode

For generating multiple articles:

```
Invoke skill with: "generate 5 blogs for [company] on [industry]"
```

The skill will:
1. Run Phase 2 (TREND) to discover 15-20 keyword candidates
2. Run Phase 3 (KEYWORD) to evaluate and select top N
3. For each selected keyword, run Phases 4-10
4. Rotate templates across articles to ensure diversity
5. Publish all articles as separate PRs

## Convergence Criteria

The pipeline terminates when ALL conditions are met:

1. Total SEO quality score ≥ 90/100
2. All reference URLs return 200 (verified)
3. Keyword density within target range (1-2%)
4. E-E-A-T compliance score ≥ 20/25
5. No content truncation or HTML structure errors

## Loop Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--count` | 1 | Number of articles to generate |
| `--site` | (from config) | Company website URL |
| `--keywords` | (auto-discovered) | Override keyword list |
| `--auto-push` | false | Auto-commit and push to GitHub |
| `--lang` | en | Output language for articles |
| `--template` | auto | Force specific template ID |
| `--max-iterations` | 3 | Max optimize-rescore cycles |

## State Persistence

Pipeline state stored in `seo-forge-state.json`:
- Current phase, iteration count, score history
- Selected keywords, assigned templates
- Generated articles and their scores
- Build failures and optimization history

Each iteration reads state at start, writes at end.

## Search Tools

Use MCP tools for web research:
- `mcp__web-search-prime__web_search_prime` — keyword discovery and trend analysis
- `mcp__web_reader__webReader` — read competitor articles and reference sources
- `mcp__zread__read_file` — read GitHub repo files for config
- `mcp__zread__get_repo_structure` — explore existing blog structure

## Blog Readability Standards

Content quality is not only about SEO scores and keyword density — visual readability directly impacts bounce rate, time-on-page, and user satisfaction. Every article generated by this pipeline MUST meet the following readability standards before publication.

### Paragraph Formatting

1. **Text Indentation (CJK)**: For Chinese, Japanese, and Korean articles, every `<p>` paragraph MUST have `text-indent: 2em` via CSS. First paragraphs after headings, lists, tables, or blockquotes are exempt (zero indent).
2. **Paragraph Length**: 150-300 words each. No wall-of-text paragraphs.
3. **Spacing**: Adequate margin between paragraphs (1em bottom margin minimum).

### Heading Hierarchy

1. **Structural**: H2 for major sections, H3 for subsections. Never skip levels (no H2 → H4).
2. **ID Anchors**: Every H2 and H3 MUST have an `id` attribute for Table of Contents linking. Use slugified text (lowercase, hyphens, strip HTML tags, handle CJK characters).
3. **Visual Distinction**: H2 and H3 must be visually distinct:
   - H2: Larger font, bottom border, with a short primary-color accent bar
   - H3: Left border in primary color, slightly indented
4. **SEO Requirement**: Main keyword appears in at least 2 H2 headings and 1 H3 heading.

### Table of Contents

1. **Required for articles > 2000 words**: Generate a TOC from all H2/H3 headings.
2. **Desktop**: Sticky sidebar TOC on large screens (hidden on mobile or collapsed accordion).
3. **Mobile**: Inline collapsible TOC below article metadata.
4. **Links**: Each TOC item links to the heading's `id` anchor.

### Table Visualization

Raw HTML tables with plain text are visually unappealing and hurt readability. Every data table MUST follow these standards:

1. **Header Styling**: Table header row uses primary brand color background with white/light text. Uppercase, smaller font, letter-spacing.
2. **Alternating Rows**: Even rows use a subtle muted background for scanability.
3. **Hover Effects**: Row highlights on hover for interactive feel.
4. **Responsive**: Tables wrapped in `overflow-x: auto` container for mobile scroll.
5. **First Column Bold**: Parameter/label column uses font-weight 500+ for emphasis.
6. **Border Radius**: Rounded corners on table container (0.75rem).
7. **Row Borders**: Subtle bottom borders between rows; no heavy grid lines.
8. **For Data-Heavy Tables**: Consider supplementing tables with CSS-based inline bar indicators or summary cards above the table highlighting key comparisons.

### CSS Requirements for Blog Content

Every project using seo-forge MUST include these CSS classes (adapt colors to brand):

```css
/* Paragraph indentation for CJK */
.blog-content p { text-indent: 2em; margin-bottom: 1em; }
.blog-content p:first-child,
.blog-content h2 + p, .blog-content h3 + p,
.blog-content ul + p, .blog-content ol + p,
.blog-content table + p, .blog-content blockquote + p { text-indent: 0; }

/* Heading hierarchy */
.blog-content h2 {
  font-size: 1.625rem; font-weight: 700;
  margin-top: 2.5rem; margin-bottom: 1rem;
  padding-bottom: 0.5rem; border-bottom: 2px solid var(--border);
  position: relative;
}
.blog-content h2::before {
  content: ""; position: absolute; left: 0; bottom: -2px;
  width: 60px; height: 2px; background: var(--primary);
}
.blog-content h3 {
  font-size: 1.25rem; font-weight: 600;
  margin-top: 1.75rem; margin-bottom: 0.75rem;
  padding-left: 0.75rem; border-left: 3px solid var(--primary);
}

/* Table visualization */
.blog-content table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  margin: 1.5rem 0; font-size: 0.875rem;
  border-radius: 0.75rem; overflow: hidden;
  border: 1px solid var(--border);
  display: block; overflow-x: auto;
}
.blog-content table thead { background: var(--primary); }
.blog-content table thead th {
  color: var(--primary-foreground); font-weight: 600;
  padding: 0.75rem 1rem; text-align: left;
  text-transform: uppercase; letter-spacing: 0.025em;
}
.blog-content table tbody tr { border-bottom: 1px solid var(--border); }
.blog-content table tbody tr:hover { background: var(--muted); }
.blog-content table tbody tr:nth-child(even) { background: var(--muted); }
.blog-content table tbody td { padding: 0.625rem 1rem; }
.blog-content table tbody td:first-child { font-weight: 500; }
```

## Safety and Quality

- All reference URLs must be verified before inclusion
- Never fabricate quotes, statistics, or URLs
- All competitor comparisons must be against real named competitors
- Never compare against "traditional methods" or "manual processes" — only against real competing products/services
- Disclose affiliations transparently
- Limit marketing superlatives ("amazing", "perfect", "revolutionary")
- Expert knowledge is an analysis lens, not primary evidence
