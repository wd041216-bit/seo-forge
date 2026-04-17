# CI/CD Quality Gates for Blog Publishing

Automated quality gates for blog content publishing, from pre-deployment validation through post-deployment monitoring and rollback. Based on Mike King's Three Laws of Generative AI Content (human oversight required) and Aleyda Solis's continuous validation loop (pre/post-release SEO checks integrated into development workflows).

## Editorial Checkpoint Specification

### Mike King's Three Laws of Generative AI Content

1. **AI is a force multiplier for workflow, not a replacement for strategy.** Automate repetitive tasks (metadata generation, internal linking, briefs). Do not automate strategic decisions.
2. **Subject matter expert input is non-negotiable for lower-funnel content.** AI-generated content that influences purchasing decisions, health decisions, or financial decisions requires human expert review.
3. **Human oversight must occur before publication.** No article should be auto-published without passing through a human review gate.

### Editorial Gate Design

The editorial gate is a mandatory checkpoint between content generation and publication. It cannot be bypassed by automated processes.

**Gate trigger**: Content generation is complete and has passed automated quality scoring.

**Gate requirement**: A human reviewer must explicitly approve the article for publication.

**What the human reviewer checks**:

- [ ] Factual accuracy of specific claims (are the numbers, names, and dates correct?)
- [ ] Appropriateness for the target audience (is the tone and depth right?)
- [ ] Absence of AI hallucinations (no fabricated statistics, quotes, or study references)
- [ ] Competitive differentiation (does this add something not in the top 10 results?)
- [ ] YMYL compliance (if applicable, is the author qualified and are claims supported?)
- [ ] Brand alignment (does the content represent the company appropriately?)

**Gate outcomes**:

| Outcome | Action |
|---------|--------|
| Approved | Article enters pre-deployment validation pipeline |
| Approved with revisions | Reviewer notes required changes; article returns to content architect for revision |
| Rejected | Article does not proceed. Reviewer documents reason. Content may be regenerated with different parameters. |

### Automation Boundary

| Automated (Before Gate) | Human (At Gate) | Automated (After Gate) |
|------------------------|-----------------|----------------------|
| Quality scoring | Factual accuracy review | Schema validation |
| SEO compliance checks | Audience appropriateness | Broken link check |
| E-E-A-T scoring | AI hallucination detection | Deployment execution |
| Schema generation | Competitive differentiation | Post-deployment verification |
| Reference URL verification | Brand alignment | Indexation monitoring |
| Keyword density measurement | YMYL author qualification | Performance tracking |

## Pre-Deployment Validation Checklist

Automated checks that run between editorial approval and deployment.

### Schema Validation

- [ ] All JSON-LD passes syntax validation (valid JSON)
- [ ] Article schema includes required fields: `headline`, `author`, `datePublished`, `publisher`
- [ ] FAQ schema (if present) has valid Question/Answer pairs
- [ ] BreadcrumbList schema has correct position numbering
- [ ] Schema does not conflict with other on-page structured data

### Broken Link Check

- [ ] All reference URLs return 200 status
- [ ] All internal links resolve to existing pages
- [ ] No links to 404 pages or redirect chains (>2 hops)
- [ ] Image URLs return valid responses

### Content Quality Score Threshold

- [ ] Total quality score >= 90/100
- [ ] No individual axis below 20/25
- [ ] Needs Met score >= 3/5
- [ ] Extractability score >= 3/5

### SEO Compliance

- [ ] Title tag length: 50-60 characters
- [ ] Meta description length: 120-160 characters
- [ ] URL slug: <= 6 words, keyword-rich
- [ ] Keyword density: 1-2%
- [ ] H2 headings contain main keyword: >= 2
- [ ] FAQ questions: >= 6
- [ ] References: >= 4 with verified URLs
- [ ] First-person pronouns: >= 15

### Technical Checks

- [ ] HTML validates without errors
- [ ] Open Graph tags present and complete
- [ ] Canonical tag present and correct
- [ ] hreflang tags present if translated versions exist
- [ ] Image dimensions specified (width/height attributes)
- [ ] No inline styles that override critical CSS

## Post-Deployment Verification

Automated checks that run after deployment to verify the article is live, indexed, and rendering correctly.

### Immediate Verification (< 5 minutes post-deploy)

- [ ] **Page returns 200 status** at the canonical URL
- [ ] **Page renders correctly**: Title, content, images, and formatting load without errors
- [ ] **Schema renders in page source**: JSON-LD present in `<head>` or `<body>` as configured
- [ ] **Canonical tag present**: `<link rel="canonical">` matches expected URL
- [ ] **No JavaScript errors**: Page loads without console errors

### Short-Term Verification (< 24 hours post-deploy)

- [ ] **Google Search Console submission**: URL submitted via URL Inspection API
- [ ] **Structured data test**: Live URL passes Google Rich Results Test
- [ ] **Mobile-friendliness**: Page passes Google Mobile-Friendly Test
- [ ] **PageSpeed Insights**: LCP < 2.5s, INP < 200ms, CLS < 0.1
- [ ] **Sitemap updated**: Article appears in the XML sitemap

### Indexation Verification (< 7 days post-deploy)

- [ ] **Indexation confirmed**: URL appears in `site:example.com` search
- [ ] **Cached version available**: Google has cached the page
- [ ] **Rich results appearing**: FAQ, Article, or other rich results visible in SERP
- [ ] **Initial impressions**: Article shows impressions in Search Console

## Rollback Mechanism

### When to Rollback

An article should be rolled back (removed from production) if:

- Post-deployment verification fails at the immediate or short-term stage
- Factual errors are discovered after publication
- The article is de-indexed or receives a manual action from Google
- Technical issues (broken rendering, schema errors) cannot be fixed within 24 hours

### Rollback Procedure

1. **Remove the article from production.** Delete or unpublish the article from the live site.
2. **Return 410 Gone or 404 Not Found.** Do not redirect to the homepage. Let search engines know the content no longer exists.
3. **Remove from sitemap.** Delete the article URL from the XML sitemap.
4. **Update internal links.** Remove or update any internal links pointing to the rolled-back article.
5. **Document the rollback.** Record the article, the reason for rollback, and any corrective actions.
6. **Re-enter the pipeline.** The article can be revised and re-published through the full pipeline (content generation, quality scoring, editorial review, deployment).

### Rollback for Indexation Issues

If the article is live but not indexing correctly:

1. **Check canonical.** Is Google recognizing the correct canonical URL?
2. **Check for noindex.** Is a `noindex` meta tag present in error?
3. **Check for crawl errors.** Are there server errors or redirect chains?
4. **Fix and resubmit.** Correct the issue and resubmit via URL Inspection.

If the article is indexed but showing errors in structured data:

1. **Fix the schema errors.** Correct the JSON-LD.
2. **Resubmit.** Request re-crawl via URL Inspection.
3. **Monitor.** Verify the fix in Rich Results Test within 48 hours.

## Automated Monitoring

### Monitoring Schedule

| Check | Frequency | Tool | Alert Threshold |
|-------|-----------|------|-----------------|
| Indexation status | Weekly | Google Search Console API | De-indexed article |
| Ranking position | Weekly | Rank tracking API | Drop > 10 positions |
| Organic traffic | Weekly | Analytics API | Drop > 30% week-over-week |
| Structured data errors | Weekly | Rich Results API | Any new errors |
| Broken links | Weekly | Crawler | Any broken links |
| Core Web Vitals | Monthly | CrUX API | LCP > 4s or CLS > 0.25 |
| Canonical changes | Daily | Crawler | Canonical differs from expected |
| Manual actions | On-demand | Search Console | Any manual action |

### Alerting Thresholds

**Critical alerts** (require immediate investigation):
- De-indexed article
- Manual action notification
- Canonical tag changed
- Structured data errors on > 3 articles

**Warning alerts** (require investigation within 48 hours):
- Ranking drop > 10 positions
- Organic traffic drop > 30%
- New broken links detected
- Core Web Vitals regression

**Informational alerts** (review in weekly check):
- Ranking movement of 1-5 positions
- Minor traffic fluctuations
- New impression data

## CI/CD Pipeline Definition

GitHub Actions workflow for blog content publishing.

### Pipeline Stages

```
Content Generation → Quality Scoring → Editorial Review Gate →
Pre-Deployment Validation → Deployment → Post-Deployment Verification →
Monitoring
```

### GitHub Actions Workflow

```yaml
name: Blog Content Pipeline

on:
  workflow_dispatch:
    inputs:
      article_path:
        description: 'Path to article file'
        required: true

jobs:
  quality-score:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Quality Scorer
        run: |
          # Score the article on 4 axes
          # Total must be >= 90, no axis < 20
          python scripts/quality_score.py ${{ inputs.article_path }}

      - name: Check Quality Threshold
        run: |
          # Fail if quality score < 90
          python scripts/check_threshold.py ${{ inputs.article_path }}

  pre-deploy-validation:
    needs: quality-score
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Schema Validation
        run: python scripts/validate_schema.py ${{ inputs.article_path }}

      - name: Broken Link Check
        run: python scripts/check_links.py ${{ inputs.article_path }}

      - name: SEO Compliance Check
        run: python scripts/seo_compliance.py ${{ inputs.article_path }}

  # Editorial review gate: this job requires manual approval
  editorial-review:
    needs: pre-deploy-validation
    runs-on: ubuntu-latest
    environment: editorial-review
    steps:
      - name: Awaiting Editorial Approval
        run: echo "Article approved for publication"

  deploy:
    needs: editorial-review
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy Article
        run: |
          # Commit article to main branch
          # Trigger Vercel deployment
          git add ${{ inputs.article_path }}
          git commit -m "feat(seo-forge): publish blog article"
          git push

  post-deploy-verification:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify Page Live
        run: |
          # Check that the article URL returns 200
          # Verify schema in page source
          # Submit to Google Search Console
          python scripts/post_deploy_verify.py ${{ inputs.article_path }}

      - name: Structured Data Test
        run: |
          # Test live URL against Rich Results API
          python scripts/test_schema_live.py ${{ inputs.article_path }}
```

### Environment Configuration

The `editorial-review` environment in GitHub requires a required reviewer. This enforces the human oversight gate:

1. Go to Settings > Environments > editorial-review
2. Add required reviewers (content editors)
3. Set a deployment protection rule requiring approval
4. The pipeline will pause at the editorial-review job until a reviewer approves

### Branch Strategy

- Content is generated on feature branches: `seo-forge/<keyword-slug>`
- Pre-deployment validation runs on the feature branch
- Editorial review gates the merge to main
- Deployment is triggered by merge to main
- Post-deployment verification runs against the production URL