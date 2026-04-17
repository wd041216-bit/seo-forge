# Performance Analytics for Blog Content

Post-publication measurement framework for SEO blog articles. Covers Google Search Console integration, organic traffic tracking, ranking monitoring, AI citation tracking, content decay detection, conversion attribution, A/B testing, quality score correlation, and alerting thresholds. Ties to the automated monitoring defined in `cicd-quality-gates.md` and the quality scoring in `agents/quality-scorer.md`.

## Google Search Console Integration

Google Search Console (GSC) is the primary data source for organic search performance. Every blog article must be tracked in GSC from the moment of publication.

### Indexing Status Monitoring

GSC provides direct data on whether Google has indexed an article and any indexing issues.

**Key reports**:
- **Page Indexing report**: Shows indexed, not indexed, and reasons for non-indexation
- **URL Inspection tool**: Real-time status for individual URLs
- **Coverage report**: Historical indexation trends

**Indexation status classification**:

| Status | Meaning | Action |
|--------|---------|--------|
| Indexed | Google has crawled and indexed the URL | No action; monitor |
| Discovered but not indexed | Google knows the URL exists but has not indexed it | Check content quality, internal links, and crawl budget |
| Crawled but not indexed | Google crawled the URL but chose not to index it | Content quality issue; review against E-E-A-T and competitor standards |
| Excluded by noindex | A `noindex` directive is preventing indexation | Remove the `noindex` tag if the article should be indexed |
| Duplicate without canonical | Google considers this URL a duplicate | Fix canonical tags (see `technical-seo-checklist.md`) |

### Search Performance Data

GSC's Performance report provides query-level data for blog articles.

**Key metrics**:
- **Impressions**: How many times the article appeared in search results
- **Clicks**: How many times users clicked through to the article
- **CTR (Click-Through Rate)**: Clicks / Impressions
- **Average position**: Mean ranking position across all queries

**Data granularity**:
- Filter by page URL to see article-level data
- Filter by query to see which keywords drive traffic
- Filter by date range to track trends
- Filter by device, country, and search appearance (rich results)

**GSC data limitations**:
- Data is sampled, not exact (especially for low-volume queries)
- Position data is averaged across all queries, devices, and locations
- Data has a 2-3 day lag
- Maximum 16 months of historical data
- API access enables programmatic extraction for automated dashboards

### Coverage Issues

Common coverage issues for blog content:

1. **Crawled but not indexed**: Content quality signal. Review the article against top-ranking competitors. If the article provides less value, improve it.
2. **Soft 404**: The page returns a 200 status but Google considers it low-value enough to treat as a 404. Usually indicates thin content.
3. **Redirect error**: Redirect chains or loops preventing crawling. Fix redirect chains to a maximum of 2 hops.
4. **Canonicalization issues**: Google selected a different canonical than the one specified. Investigate why Google disagrees.

## Organic Traffic Tracking

Google Analytics (GA4) provides behavioral data that complements GSC's search data.

### Key Metrics for Blog Content

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| **Organic sessions** | Total visits from organic search | Growth trend month-over-month |
| **Engagement rate** | Percentage of engaged sessions ( > 10s active, conversion, or 2+ pageviews) | > 50% |
| **Average engagement time** | Mean time users actively engage with content | > 2 minutes for long-form |
| **Scroll depth** | How far users scroll down the article | > 75% for 2000+ word articles |
| **Bounce rate (UA-style)** | Single-page sessions with no interaction | < 60% (use engagement rate in GA4) |
| **Pages per session** | Average pages viewed per session | > 1.5 (indicates internal linking works) |
| **Return visitor rate** | Percentage of users who visit more than once | > 15% |

### Traffic Segmentation

Analyze blog traffic by segment to identify patterns:

- **By channel**: Organic search, social, referral, direct, email
- **By landing page**: Which articles drive the most traffic
- **By geography**: Which regions the content serves
- **By device**: Desktop vs mobile engagement differences
- **By content cluster**: Hub vs spoke articles (see `link-building.md`)

### Attribution Model for Blog Content

Blog content operates at multiple funnel stages. The attribution model must account for this:

| Content Type | Funnel Stage | Primary Metric | Attribution Window |
|-------------|-------------|----------------|-------------------|
| Definitional / educational | Top of funnel | Organic impressions, brand awareness | 30-90 days |
| Comparison / review | Middle of funnel | Engagement time, return visits, internal navigation to commercial pages | 14-30 days |
| Decision-focused / pricing | Bottom of funnel | Conversion rate, demo requests, signups | 7-14 days |

Blog content rarely converts directly. Its value is in building the authority and trust that enable conversions on commercial pages. Use multi-touch attribution (not last-click) to capture this value.

## Ranking Monitoring

Track keyword rankings over time to measure content performance and detect issues early.

### Tracking Methodology

**Frequency**:
- **Daily tracking**: Primary keyword for newly published articles (first 30 days)
- **Weekly tracking**: Primary and secondary keywords for all articles
- **Monthly tracking**: Long-tail keyword variations and secondary terms

**Data sources**:
- GSC Performance report (impressions, position) — free, but limited granularity
- Third-party rank trackers (Ahrefs, SEMrush, AccuRanker) — more precise, location-specific

**What to track per article**:
- Primary keyword ranking position
- Top 5 secondary keyword positions
- Position delta (week-over-week change)
- SERP feature occupancy (featured snippet, People Also Ask, AI Overview)

### Volatility Detection

Ranking volatility indicates algorithmic changes or competitor activity.

**Normal volatility**: 1-3 position movement per week is normal for positions 5-15.
**Abnormal volatility**: > 5 position movement in a single week, or consistent downward movement over 3+ consecutive weeks.

**Volatility response protocol**:
1. Check if the volatility affects a single article or multiple articles
2. If single article: check competitor changes, content freshness, link profile changes
3. If multiple articles: check for algorithm update correlation (see below)
4. Cross-reference with GSC data: are impressions and clicks also affected?
5. If ranking drops but traffic is stable: the drop may be due to SERP layout changes, not content quality

### Algorithm Update Correlation

When rankings shift across multiple articles simultaneously, correlate with known algorithm updates.

**Detection process**:
1. Monitor Google Algorithm Update tracking resources: SEMrush Sensor, MozCast, Algoroo
2. When volatility exceeds normal thresholds across multiple articles, check for confirmed updates
3. Classify the update type: core update, helpful content, link spam, reviews, spam
4. Cross-reference affected articles: do they share characteristics that the update targets?
5. Determine response: no action (if the content is strong), content improvement (if quality gaps exist), or technical fix (if the issue is structural)

**Common update impacts on blog content**:
- **Helpful Content updates**: Reward content demonstrating genuine expertise and experience; penalize AI-generated content lacking depth (ties to E-E-A-T framework in `eeat-framework.md`)
- **Core updates**: Broad ranking recalibration; content that was previously over-ranked may drop
- **Link spam updates**: Devalue artificial link patterns; check link velocity (see `link-building.md`)

## AI Citation Tracking

Lily Ray's concept: as AI search (Google AI Overviews, Bing Copilot, Perplexity, ChatGPT with browsing) becomes a significant traffic source, tracking when and how content appears in AI-generated answers is a new measurement domain.

### What to Track

- **AI Overview appearances**: Does the article appear as a citation in Google AI Overviews for relevant queries?
- **AI search citations**: Is the content referenced in Bing Copilot, Perplexity, or ChatGPT answers?
- **AI-driven traffic**: Traffic from AI search platforms (referral data in GA4)
- **Citation context**: How is the content summarized or cited? Is the citation accurate?

### Tracking Methods

1. **Manual queries**: Search for target keywords in AI Overviews and AI search platforms; check if your content is cited
2. **Referral tracking in GA4**: Monitor traffic from AI platforms:
   - Perplexity.ai
   - ChatGPT (chat.openai.com)
   - Bing Copilot (bing.com/chat)
   - Google AI Overview click-throughs (labeled in GSC)
3. **Brand mention monitoring**: Track mentions of your company or article titles in AI search outputs
4. **Third-party tools**: Emerging tools (e.g., Profound, HubSpot AI Search Grader) that track AI citation rates

### AI Citation Optimization

If content is not appearing in AI Overviews or AI search results:

1. **Check passage-level optimization**: Each H2 section must be a self-contained semantic unit (see `content-engineering.md`)
2. **Improve extractability**: Use declarative factual tone with specific, verifiable claims
3. **Increase evidence density**: Each section should contain 2-3 specific claims with data points
4. **Improve citation-worthiness**: Does the passage contain information not in competing sources? (Information gain)
5. **Check schema markup**: Article, FAQ, and HowTo schema enable AI search systems to understand content structure

### AI Citation Metrics

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| AI Overview citation rate | Percentage of target queries where the article appears in AI Overviews | > 10% for established content |
| AI search referral traffic | Sessions from AI search platforms | Growth trend month-over-month |
| Citation accuracy | How accurately AI systems represent the content | 100% (no misrepresentation) |
| AI Overview CTR | Click-through rate from AI Overview citations | Track and compare to organic CTR |

## Content Decay Detection

Blog content does not maintain its peak traffic forever. Content decay — the gradual decline in organic traffic — is normal but detectable and addressable.

### Traffic Decline Patterns

| Pattern | Typical Cause | Detection Timeframe |
|---------|---------------|---------------------|
| Gradual decline (5-10% per month) | Content aging, competitor improvements, algorithm drift | 3-6 months |
| Sudden drop (30%+ in a week) | Algorithm update, technical issue, de-indexation | 1-2 weeks |
| Seasonal decline | Topic seasonality (e.g., tax content drops in summer) | Compare to same period last year |
| Plateau then decline | Content freshness signal loss, competitor content surpasses | 6-12 months |

### Decay Detection Method

1. **Baseline establishment**: Record the article's 90-day average organic traffic after publication (post-initial-growth phase)
2. **Monthly comparison**: Compare each month's organic traffic to the baseline
3. **Trend analysis**: Calculate the 3-month moving average to smooth weekly noise
4. **Threshold trigger**: If the 3-month moving average drops below 70% of baseline, the article has entered decay

### Refresh Triggers

| Signal | Threshold | Action |
|--------|-----------|--------|
| Traffic decline | > 30% below 90-day baseline | Content refresh (update statistics, add new sections) |
| Ranking decline | Primary keyword drops > 5 positions | Competitive analysis and content enhancement |
| CTR decline | CTR drops > 25% below peak | Title and meta description optimization |
| Engagement decline | Average engagement time drops > 30% | Content restructuring for readability |
| AI citation loss | Article no longer appears in AI Overviews | Passage-level optimization review |
| Competitor content surpasses | New competitor content ranks above | Content improvement and link acquisition |

### Content Refresh Strategy

When decay is detected, apply targeted refreshes rather than full rewrites:

1. **Update statistics and data**: Replace outdated numbers with current data
2. **Add new sections**: Cover emerging subtopics that competitors now address
3. **Update references**: Replace broken or outdated reference URLs
4. **Refresh publication date**: Update `dateModified` in Article schema
5. **Re-optimize for current intent**: Search intent may have shifted; update content to match
6. **Re-promote**: Distribute the refreshed content through social and email channels
7. **Resubmit to GSC**: Request re-crawling via URL Inspection after refresh

## Conversion Tracking

Blog content drives conversions indirectly. Tracking this attribution requires deliberate measurement setup.

### Blog-to-Conversion Attribution

| Conversion Type | Tracking Method | Attribution Window |
|----------------|-----------------|-------------------|
| Newsletter signup | UTM parameters + GA4 conversion events | 30 days |
| Demo request | UTM parameters + CRM lead source | 60 days |
| Free trial signup | UTM parameters + product analytics | 30 days |
| Purchase | UTM parameters + GA4 e-commerce | 90 days |
| Internal navigation to commercial pages | GA4 event tracking on internal links | 7 days |

### Funnel Stage Tracking

**Top of funnel (educational content)**:
- Track: newsletter signups, return visits, brand search volume
- Attribution: assisted conversions (blog appears in the conversion path but is not the last touch)

**Middle of funnel (comparison content)**:
- Track: internal link clicks to commercial pages, time on page, pages per session
- Attribution: first-touch and linear models capture blog influence

**Bottom of funnel (decision content)**:
- Track: direct conversions from blog CTA clicks
- Attribution: last-click captures some of this, but multi-touch reveals the full picture

### Blog CTA Tracking

Every CTA in blog articles must be trackable:
- Use UTM parameters on CTA links: `?utm_source=blog&utm_medium=cta&utm_campaign=<article-slug>`
- Track CTA clicks as GA4 events: `cta_click` with parameters for article, CTA position, and destination
- Measure CTA conversion rate: clicks / pageviews
- Benchmark: 1-3% CTA click-through rate is typical for blog content

## A/B Testing Framework for Blog Content

Systematic testing improves content performance over time. Blog content offers several testable elements.

### Headline Testing

**What to test**: Article title (H1 / title tag)
**How**: Serve different titles to different user segments; measure CTR and engagement

**Process**:
1. Identify articles with high impressions but low CTR (< 2%)
2. Generate 2-3 alternative titles that maintain keyword inclusion
3. Use Google's title testing (if available in Search Console experiments) or a CMS-based A/B test
4. Run for 2-4 weeks or until statistical significance (95% confidence, minimum 500 impressions per variant)
5. Promote the winning title

**Title test variables**:
- Keyword position: leading vs. trailing
- Number inclusion: "7 Ways to..." vs. "How to..."
- Question format: "What Is X?" vs. "X: Complete Guide"
- Emotional modifiers: "Essential", "Comprehensive", "Practical"

### CTA Placement Testing

**What to test**: CTA position, design, and copy
**How**: Vary CTA placement across articles in the same cluster

**Test configurations**:
- **Inline CTA** (mid-article) vs. **end-of-article CTA**
- **Sidebar CTA** (desktop) vs. **sticky bottom CTA** (mobile)
- **Text CTA** vs. **button CTA**
- **Single CTA** vs. **dual CTA** (primary + secondary)

**Measurement**: CTA click rate, conversion rate per placement, impact on engagement time (inline CTAs may reduce engagement if disruptive)

### Content Structure Variations

**What to test**: Content format and structure
**How**: Publish similar topics with different structural approaches

**Testable structures**:
- **List format** (numbered steps) vs. **narrative format** (paragraph-based)
- **FAQ-first** (FAQ section at the top) vs. **FAQ-last** (FAQ section at the bottom)
- **Comparison table** vs. **side-by-side prose**
- **Video-embedded** vs. **text-only**

**Measurement**: Engagement time, scroll depth, return visit rate, conversion rate

### Testing Rules

1. **One variable at a time**: Changing title + CTA + structure simultaneously makes results uninterpretable
2. **Statistical significance**: Do not call a test before reaching 95% confidence
3. **Minimum sample size**: At least 500 impressions or 100 pageviews per variant
4. **Duration**: Run tests for at least 2 weeks to capture day-of-week variation
5. **Document everything**: Record hypothesis, test design, results, and decision for each test

## Quality Score Correlation

The pipeline's quality scores (from `agents/quality-scorer.md`) must correlate with actual search performance for the scoring model to be trustworthy. This section defines how to validate and improve the scoring model over time.

### Correlation Metrics

Track the relationship between pre-publication quality scores and post-publication performance:

| Quality Axis | Expected Correlation | Performance Metric |
|-------------|---------------------|-------------------|
| SEO Quality (0-25) | Strong positive | Organic traffic at 90 days, primary keyword ranking |
| E-E-A-T Compliance (0-25) | Moderate positive | Engagement rate, return visit rate, AI citation rate |
| Content Depth (0-25) | Moderate positive | Scroll depth, time on page, secondary keyword rankings |
| Reference Authority (0-25) | Weak-moderate positive | Link acquisition rate, domain authority growth |

### Validation Process

1. **Collect data**: For each published article, record quality scores and 90-day performance metrics
2. **Calculate correlation**: Use Pearson or Spearman correlation between each quality axis and its corresponding performance metric
3. **Identify misalignment**: Articles with high quality scores but poor performance, or low scores but strong performance, indicate scoring model gaps
4. **Adjust weights**: If an axis consistently shows weak or negative correlation with performance, review and adjust the scoring methodology
5. **Retrospective review**: Quarterly, review all published articles and re-evaluate scoring model accuracy

### Scoring Model Improvement

When correlation data reveals scoring weaknesses:

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| High SEO score, low ranking | SEO scoring overweights on-page factors vs. off-page | Add link acquisition potential to SEO scoring |
| High E-E-A-T score, low engagement | E-E-A-T checklist compliance without genuine depth | Increase weight of deep signals over surface signals (see `eeat-framework.md`) |
| Low content depth score, high performance | Depth metrics miss value in concise content | Review word count weighting; some topics benefit from conciseness |
| High reference score, low link acquisition | References don't predict external linking | Add "link-worthiness" assessment to content scoring |

### Feedback Loop

```
Quality Score → Publish → 90-Day Performance Data → Correlation Analysis
     ↑                                                        │
     └─────────────── Adjust Scoring Model ←───────────────────┘
```

This loop ensures the scoring model improves over time as real-world performance data accumulates.

## Alerting Thresholds

Automated alerting ensures that content issues are detected and addressed before they compound. This section extends the alerting thresholds in `cicd-quality-gates.md` with blog-specific triggers.

### Critical Alerts (Immediate Investigation)

| Alert | Trigger | Response Time |
|-------|---------|---------------|
| De-indexation | Article removed from Google index | < 24 hours |
| Manual action | Google Search Console notification | < 24 hours |
| Traffic collapse | > 50% traffic drop in 7 days | < 48 hours |
| Canonical change | Canonical differs from expected | < 24 hours |
| Rendering failure | Article returns 5xx or redirects to error page | < 4 hours |

### Warning Alerts (Investigate Within 48 Hours)

| Alert | Trigger | Response Time |
|-------|---------|---------------|
| Ranking drop | > 10 position drop for primary keyword | < 48 hours |
| Traffic decline | > 30% decline in 14 days | < 48 hours |
| CTR decline | > 25% CTR drop from peak | < 1 week |
| Broken links | New broken internal or external links detected | < 1 week |
| Schema errors | Rich Results Test fails on live URL | < 1 week |
| Content decay | 3-month moving average below 70% of baseline | < 2 weeks |

### Informational Alerts (Weekly Review)

| Alert | Trigger | Review Cadence |
|-------|---------|----------------|
| Ranking movement | 1-5 position change | Weekly |
| Traffic fluctuation | < 15% variation | Weekly |
| New impressions | Article appearing for new queries | Weekly |
| Social share milestones | Significant sharing activity | Weekly |
| AI citation detected | Article appears in AI Overview for new query | Weekly |

### Re-optimization Triggers

These thresholds determine when an article should re-enter the optimization pipeline:

| Condition | Threshold | Pipeline Entry Point |
|-----------|-----------|---------------------|
| Ranking decline | Primary keyword drops > 10 positions | Phase 7: OPTIMIZE |
| Traffic decline | > 30% below 90-day baseline | Phase 8: EDIT (content refresh) |
| CTR decline | > 25% below peak CTR | Phase 7: OPTIMIZE (title/meta) |
| AI citation loss | Was cited, now not cited | Phase 8: EDIT (passage optimization) |
| Content freshness | Article > 12 months old with declining traffic | Phase 8: EDIT (data update) |

### Content Deletion Consideration

Some content cannot be rescued by re-optimization and should be considered for removal:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Zero organic traffic for 90+ days | No impressions or clicks | Consider 301 redirect to a related article or noindex |
| Quality score < 50 after 3 optimization iterations | Fundamentally weak content | Delete or consolidate with stronger article |
| Topically irrelevant (business pivot) | Content no longer aligns with company direction | 301 redirect or remove |
| Thin content penalty risk | < 500 words with no engagement | Expand substantially or remove |
| Negative brand impact | Content misrepresents current positioning | Update immediately or remove |

**Deletion procedure** (per `cicd-quality-gates.md` rollback mechanism):
1. Do not 404 internal-linked articles (breaks link equity flow)
2. 301 redirect to the most topically relevant remaining article
3. Update all internal links pointing to the deleted article
4. Remove from XML sitemap
5. Document the deletion reason and redirect target