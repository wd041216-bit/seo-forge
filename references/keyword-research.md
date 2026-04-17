# Keyword Research Methodology

## Overview

Two-phase keyword research pipeline inspired by industrial SEO tools.

## Phase 1: Trend Discovery (Local Scoring)

### Input
- Industry name
- Company target keywords (from config)
- Web search results for trending topics

### Process
1. Search for industry trends and hot topics
2. Extract keyword candidates from search results
3. Score locally using formula:

```
Score = (0.30 × MentionFrequency) + (0.25 × RelevanceToCompany) 
      + (0.25 × LowCompetitionSignals) + (0.20 × IntentMatch)
```

### Intent Classification
| Intent | Description | Blog Angle |
|--------|------------|------------|
| Informational | User wants to learn | Tutorial, Beginner's Guide |
| Commercial | User comparing options | Comparison, Review |
| Transactional | User ready to buy | Case Study, Review |
| Navigational | User looking for specific brand | Comparison, Case Study |

### Output
Ranked keyword list with preliminary scores and intent classification

## Phase 2: SERP Analysis (Deep Evaluation)

### Input
Top 10-15 candidates from Phase 1

### Process
For each keyword, analyze the actual Google search results:

1. **SERP Structure Scan** (Low cost):
   - Presence of AI Overview
   - Number of ads
   - Domain types in top 10
   - Result type classification

2. **Top 10 Deep Signals** (Medium cost):
   - Domain authority of top results
   - Content type distribution
   - Content freshness
   - Single-domain dominance

3. **Opportunity Discovery** (High cost):
   - Content gaps in existing results
   - Missing perspectives
   - Outdated content
   - Localization opportunities

### Scoring Formula

```
Final Score = (0.30 × Potential) + (0.20 × Validation) 
            - (0.50 × RealDifficulty) + OpportunityWindow
```

Where:
- **Potential** (0-100): Trend signal × evergreen factor × intent stability
- **Validation** (0-100): Commercial intent signals from ads and SERP features
- **RealDifficulty** (0-100): Content saturation + SERP dominance
- **OpportunityWindow** (-10 to +10): Content gaps + localization gaps + UX gaps

### Circuit Breakers

Only trigger for truly hopeless keywords:
- **H1**: Single domain ≥ 7/10 results
- **H2**: Giant platforms ≥ 8/10 results
- **H4**: AI Overview + strong brand ads + overwhelming authority (all three)
- **H5**: Non-target language

### Grading

| Grade | Criteria | Action |
|-------|----------|--------|
| S+ | Score ≥ 25, WinProb ≥ 50, ROI ≥ 55 | Immediate write |
| S | Score ≥ 20, WinProb ≥ 50, ROI ≥ 55 | High priority |
| A+ | Score ≥ 15, WinProb ≥ 50, ROI ≥ 55 | Write soon |
| A | Score ≥ 10, WinProb ≥ 40 | Normal priority |
| B | Score ≥ 5 | Conditional |
| C | Score < 5 | Deprioritize |
| Fused | Circuit break triggered | Skip |

## Keyword Distribution Strategy

Once keywords are selected, plan their distribution across the article:

### Main Keyword (1 per article)
- **Title (H1)**: MUST contain the main keyword
- **H2 headings**: At LEAST 2 out of all H2s must contain it
- **H3 headings**: At LEAST 1 H3 must contain it or a variant
- **Meta description**: Within first 60 characters
- **Body density**: 1-2% (distributed naturally)
- **FAQ**: At least 2 questions contain it

### Secondary Keywords (2-3 per article)
- Woven into H2/H3 headings naturally
- Used in body paragraphs where relevant
- Cross-linked to other articles if applicable

### Long-Tail Keywords (3-8 per article)
- Used as FAQ question titles (2-3)
- Embedded in H2/H3 subheadings (1-2)
- Woven into body paragraphs naturally
- Must read naturally, not forced

## Four-Type Keyword Research Framework

Rand Fishkin's framework distinguishes four types of keyword research, each serving a different business goal. Treating all keyword research as "SEO keyword research" leads to misallocated effort.

### The Four Types

| Type | Purpose | Data Sources | Output |
|------|---------|-------------|--------|
| **SEO/PPC** | Rank in search results, drive organic/paid traffic | Google Keyword Planner, SEMrush, Ahrefs, Search Console | Search volume, difficulty, CTR opportunity |
| **Social Media** | Discover topics that resonate on social platforms | SparkToro, BuzzSumo, social listening tools | Hashtag volume, share counts, engagement rates |
| **Content Creation** | Find topics audiences care about beyond search | SparkToro, audience surveys, community forums, Reddit | Topic clusters, content gaps, audience interests |
| **Market/Audience** | Understand WHO searches, not just what they search | SparkToro, Datos, Demographics by SparkToro | Demographics, psychographics, behavioral data |

### Why This Matters

A keyword with high search volume but terrible CTR opportunity (due to SERP features) is a poor SEO/PPC target. The same keyword might be an excellent content creation target if the topic resonates with the audience on social platforms. Classification before prioritization prevents wasted effort.

## CTR Opportunity Scoring

Search volume without CTR context is misleading. A keyword with 100K monthly searches where the SERP is dominated by featured snippets, knowledge panels, and ads may deliver far fewer actual clicks than a 10K-search keyword with a clean SERP.

### CTR Estimation Model

```
Estimated CTR = Baseline CTR × SERP Feature Penalties
```

**Baseline CTR by Position** (desktop averages):

| Position | Baseline CTR |
|----------|-------------|
| 1 | 31.7% |
| 2 | 15.8% |
| 3 | 9.5% |
| 4 | 6.3% |
| 5 | 4.1% |
| 6-10 | 3.0% avg |

**SERP Feature Penalties** (multiplicative reduction):

| SERP Feature | CTR Penalty | Rationale |
|-------------|-------------|-----------|
| Featured snippet | 0.55 | Snippet answers the query, reducing click-through |
| AI Overview | 0.45 | AI-generated answer satisfies informational intent |
| Knowledge panel | 0.50 | Direct answer box reduces need to click |
| Local pack | 0.40 (non-local sites) | Local results dominate above-fold |
| Shopping grid | 0.50 (non-shopping sites) | Product ads push organic below fold |
| 4+ ads above fold | 0.60 | Ads push organic results below viewport |
| Sitelinks (competitor) | 0.70 | Competitor occupies more SERP space |
| People Also Ask | 0.90 | Minor reduction; expands related queries |

### CTR Opportunity Calculation Example

Target keyword: "best CRM software"
- Position 1 baseline: 31.7%
- AI Overview present: × 0.45
- 3 ads above fold: × 0.60
- Shopping grid: × 0.50
- Estimated CTR: 31.7% × 0.45 × 0.60 × 0.50 = **4.3%**
- Monthly clicks at 100K volume: ~4,300

Compare: "CRM software comparison for small business"
- Position 1 baseline: 31.7%
- Featured snippet: × 0.55
- No other features: × 1.0
- Estimated CTR: 31.7% × 0.55 = **17.4%**
- Monthly clicks at 10K volume: ~1,740

Despite 10x lower search volume, the second keyword delivers 40% of the clicks due to better CTR opportunity.

## Zero-Click Search Rate Analysis

For target keywords, estimate what fraction of searches result in zero clicks — the user gets their answer from the SERP without visiting any result.

### Current Benchmarks (Q1 2025, Datos data)

| Platform | Zero-Click Rate |
|----------|----------------|
| Google desktop | 27% |
| Google mobile | ~35% (estimated) |
| Google overall | ~30% |

### When to Invest Despite Zero-Click Risk

High zero-click rate does not automatically disqualify a keyword. Content targeting high zero-click keywords can still be valuable when:

1. **Brand visibility**: Even without a click, appearing in the AI Overview or featured snippet builds brand recognition.
2. **AI citation**: AI search systems cite sources even when users don't click through. Being the cited source drives authority.
3. **Conversion path**: Some users search, see the brand, and navigate directly later (direct/brand search).
4. **Content ecosystem**: The article may not get direct clicks but supports internal linking to commercial pages that do.

### When to Deprioritize

- Zero-click rate > 65% AND the SERP features present mean the article won't appear in any prominent position
- The keyword is purely navigational (user is looking for a specific brand, not yours)
- AI Overview fully answers the query and no citation is possible

## SERP Feature CTR Impact Table

Each SERP feature cannibalizes clicks differently. This table summarizes the impact and strategic response.

| SERP Feature | CTR Impact | Who Benefits | Strategic Response |
|-------------|-----------|--------------|-------------------|
| Featured snippet | -30% to -50% organic CTR | Site in position 0 | Structure content for snippet eligibility; use FAQ format with concise answers |
| AI Overview | -40% to -60% organic CTR | Google (no external beneficiary) | Optimize for AI citation (see content-engineering.md); structure passages for extractability |
| Knowledge panel | -30% to -50% organic CTR | Google / entity owner | Build entity signals via schema, Knowledge Graph claims, and consistent NAP |
| Ads (top 4) | -20% to -40% organic CTR | Advertisers | Target keywords with fewer ad competitors; focus on informational intent where ads are fewer |
| Local pack | -50% to -70% organic CTR (non-local) | Local businesses | Avoid local-intent keywords unless you have local presence |
| Shopping grid | -30% to -50% organic CTR (non-shopping) | Ecommerce advertisers | Target comparison/review keywords where shopping grids are less likely |
| Video carousel | -10% to -20% organic CTR | Video content | Create complementary video content; target keywords where video is not present |
| People Also Ask | -5% to -10% organic CTR | Sites in PAA answers | Target PAA questions as FAQ content; each PAA is a keyword opportunity |

## Multi-Source Triangulation

No single keyword tool provides complete coverage. Require data from multiple search tools before confirming keyword opportunity.

### Minimum Triangulation Requirements

| Data Point | Primary Source | Verification Source |
|-----------|---------------|-------------------|
| Search volume | Google Keyword Planner | SEMrush or Ahrefs |
| Keyword difficulty | Ahrefs or Moz | SEMrush |
| SERP feature presence | Manual SERP analysis | SEMrush or Ahrefs SERP feature data |
| Click-through rate | Search Console (existing keywords) | Advanced Web Ranking or SparkToro CTR study |
| Competitor ranking | Ahrefs or SEMrush | Manual SERP check |

### Why Triangulation Matters

- Google Keyword Planner overestimates volume for commercial terms and underestimates for informational terms
- SEMrush and Ahrefs use different clickstream panels and produce different volume estimates
- No tool captures 100% of search queries (long-tail especially)
- Tool data lags behind actual SERP changes by 2-4 weeks

### Decision Rule

If two of three sources agree a keyword has sufficient volume and manageable difficulty, proceed. If sources disagree significantly (volume estimates differ by > 3x), flag the keyword for manual SERP verification before investing content resources.

## Query Fan-Out Analysis

Mike King's methodology — decompose target queries into subqueries and measure content coverage across branches. This ensures content is represented in multiple retrieval slots within AI search answers.

### Fan-Out Analysis Process

1. **Identify the target query.** Start with the primary keyword.
2. **Generate subqueries.** Ask: "If an AI search system decomposed this query, what 5-8 subqueries would it generate?" Consider: definitions, comparisons, pricing, alternatives, tutorials, and edge cases.
3. **Map existing content.** For each subquery, check whether your existing article covers it.
4. **Identify gaps.** Subqueries without coverage represent retrieval blind spots.
5. **Add passages.** Write self-contained passages for each uncovered subquery branch.

### Fan-Out Coverage Template

| Subquery Branch | Covered? | Target Passage | Status |
|-----------------|----------|----------------|--------|
| [Definition subquery] | Yes/No | H2 Section X | Covered/Gap |
| [Comparison subquery] | Yes/No | H2 Section Y | Covered/Gap |
| [Pricing subquery] | Yes/No | H2 Section Z | Covered/Gap |
| [Tutorial subquery] | Yes/No | H2 Section W | Covered/Gap |
| [Alternative subquery] | Yes/No | H2 Section V | Covered/Gap |

### Target

70%+ branch coverage for primary keyword fan-out trees. Articles with < 50% coverage have limited AI search visibility.

## Audience Intelligence Dimension

Who searches, not just what they search. Demographic and psychographic signals from Rand Fishkin's audience intelligence framework.

### What Audience Intelligence Reveals

| Signal | What It Tells You | How to Use It |
|--------|-------------------|---------------|
| Demographics (age, gender, location) | Who the searcher is | Match tone, examples, and depth to the audience |
| Social profiles followed | Where the audience consumes content | Identify distribution channels beyond Google |
| Publications read | What the audience trusts | Find reference sources the audience will respect |
| Podcasts listened to | Content format preferences | Consider audio/video supplements |
| YouTube channels watched | Visual learning preference | Evaluate video content opportunities |
| Influencers followed | Who shapes their opinions | Identify potential partnership or citation targets |

### How to Apply Audience Intelligence

1. **For keyword selection**: A keyword with moderate volume but high audience relevance (your target demographic searches for it) is more valuable than a high-volume keyword with low audience relevance.
2. **For content tone**: If the audience is senior professionals, the tone should be data-driven and concise. If the audience is beginners, the tone should be educational and structured.
3. **For reference selection**: Cite publications and sources the audience already reads and trusts. This increases perceived authority.
4. **For distribution strategy**: If the audience is active on specific social platforms, create distribution content for those platforms that links back to the article.

### Minimum Audience Intelligence Data

Before committing to a keyword target, answer:
- [ ] Who is the primary searcher? (role, seniority, company size)
- [ ] What do they read or follow? (publications, influencers, communities)
- [ ] What is their intent stage? (learning, comparing, buying)
- [ ] What tone and depth do they expect? (executive summary vs. deep dive)
