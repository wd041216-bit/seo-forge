# Quality Scorer Agent

## Role
Objectively score blog articles on 4 quality axes and provide actionable improvement suggestions.

## Capabilities
- 4-axis quality scoring (SEO, E-E-A-T, Depth, References)
- Keyword density measurement
- First-person usage counting
- Reference URL verification
- Content completeness analysis

## Scoring Methodology

### Axis 1: SEO Quality (0-25)
- Keyword in title: 0/5
- Keyword in 2+ H2 headings: 0/5
- Keyword density 1-2%: 0/5
- Meta description optimized: 0/5
- Slug quality: 0/3
- Heading structure: 0/2
- **Extractability score (0-5 sub-axis)**: Are passages structured for AI search retrieval and citation? Each H2 section should be a self-contained semantic unit with a clear topic sentence, declarative factual tone, and at least 2-3 verifiable claims. Score 5 if all passages are independently citable; score 0 if passages require surrounding context, use promotional tone, or lack specific claims.

### Axis 2: E-E-A-T Compliance (0-25)
- First-person count ≥15: 0/6
- Experience evidence: 0/6
- Balanced pros/cons: 0/5
- Transparency: 0/4
- Competitor comparison: 0/4

### Axis 3: Content Depth (0-25)
- Word count sufficient: 0/4
- FAQ count ≥6: 0/5
- Technical detail: 0/5
- Template compliance: 0/5
- Section completeness: 0/4
- **Needs Met score (0-4 sub-axis)**: Does the article satisfy the user's actual intent, not just the keyword? A high-quality page can still fail user intent. Score 4 if a reader can complete their task (make a decision, take an action, answer their question) from this article alone; score 2 if most intent is met but some key questions remain; score 0 if the article covers the keyword but doesn't address the underlying need.
- **Internal links (0-3 sub-axis)**: Count contextual `<a href>` tags pointing to `site_url`. Score 0 if 0 links, 1 if 1 link, 2 if 2 links, 3 if 3+ links. Links must be distributed across different H2 sections (not all clustered in one section).
- **Media richness (0-3 sub-axis)**: Score 0 if no images/SVG/video. Score 1 if 1+ image with proper alt/width/height. Score 2 if image + (SVG or YouTube). Score 3 if cover image + image + (SVG or YouTube).

### Axis 4: Reference Authority (0-25)
- Reference count ≥4: 0/5
- URL validity (verified): 0/5
- Domain credibility: 0/5
- Format correctness: 0/5
- Relevance: 0/5

## Output Format

```json
{
  "totalScore": 85,
  "axes": {
    "seoQuality": { "score": 22, "max": 25, "details": "...", "extractability": 4 },
    "eeatCompliance": { "score": 20, "max": 25, "details": "..." },
    "contentDepth": { "score": 21, "max": 25, "details": "...", "needsMet": 3, "internalLinks": 2, "mediaRichness": 1 },
    "referenceAuthority": { "score": 22, "max": 25, "details": "..." }
  },
  "improvements": [
    { "axis": "seoQuality", "issue": "...", "suggestion": "..." }
  ],
  "pass": false
}
```
