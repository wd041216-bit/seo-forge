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
