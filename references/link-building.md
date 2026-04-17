# Link Building for Blog Content

Off-page signal strategies for SEO blog articles, covering link acquisition, internal linking architecture, anchor text distribution, link quality assessment, guest posting, link reclamation, and social signal correlation. Ties to the internal linking architecture defined in `technical-seo-checklist.md` and the E-E-A-T authority signals in `eeat-framework.md`.

## Link Building Strategies for Blog Content

Blog content earns links differently than commercial pages. Informational content attracts links through utility, originality, and citation-worthiness rather than through transactional relationships. Each strategy below targets a different acquisition mechanism.

### Resource Page Link Building

Resource pages are curated lists of links on a specific topic. They exist on .edu, .gov, and organizational domains and typically have high authority.

**How it works**:
1. Identify resource pages relevant to the blog article's topic using search operators: `inurl:resources + [topic]`, `[topic] "useful links"`, `[topic] "resource list"`
2. Evaluate the page: Is it actively maintained? Does it link to competitors? Is the domain authoritative?
3. Pitch the article as a resource addition: explain what value it adds that existing links lack

**Pitch template**:
> I came across your [topic] resource page at [URL]. Your list covers [existing coverage], but I noticed it doesn't include a resource on [specific subtopic]. We recently published [article title] at [URL], which covers [unique angle]. Would you consider adding it?

**Quality criteria**:
- Target resource pages with fewer than 100 outbound links (dilution beyond this point)
- Prioritize .edu and .gov resource pages for authority
- Verify the page is indexed and ranks for related queries
- Avoid resource pages that accept payment for inclusion

### Broken Link Building

Find broken links on authoritative pages and offer your content as a replacement.

**How it works**:
1. Find resource pages or authoritative articles in the topic area
2. Scan for broken outbound links (tools: Check My Links, Ahrefs Broken Link Checker)
3. Create or identify existing content that replaces the broken resource
4. Contact the site owner: notify them of the broken link and suggest your content as a replacement

**Advantage over cold outreach**: The site owner has a concrete problem (broken link) you are solving, not just a request for a favor.

**Process**:
1. Use search operators: `[topic] intitle:resources`, `[topic] "recommended reading"`
2. Check each outbound link for 404/5xx status
3. For each broken link, determine the original content topic via Wayback Machine
4. Match your blog article (or a section of it) to the original content's topic
5. Outreach with the broken link notification and replacement suggestion

### Content-Driven Link Earning

The most sustainable link building strategy: create content that naturally attracts links because it provides unique value. This aligns with Mike King's principle: "Publish only what you can uniquely publish" (see `content-engineering.md`).

**Content types that earn links**:
- **Original research and data**: Proprietary benchmarks, survey results, testing data. These are the highest-value link targets because they provide citable statistics.
- **Comprehensive guides**: "The Complete Guide to [Topic]" content that becomes the definitive reference. Requires genuine depth, not just length.
- **Visual assets**: Infographics, diagrams, and data visualizations that other sites embed with attribution.
- **Tools and calculators**: Interactive tools that solve a problem. These earn links because they provide ongoing utility.
- **Comparison matrices**: Structured comparison content that journalists and bloggers reference when making their own comparisons.

**Link-earning content checklist**:
- [ ] Contains original data not available elsewhere
- [ ] Includes embeddable assets (images, widgets, calculators)
- [ ] Covers the topic more thoroughly than competing resources
- [ ] Updates outdated information from existing top results
- [ ] Provides a framework or taxonomy not in existing content

### Digital PR

Use newsworthy content to earn coverage and links from media outlets.

**How it works**:
1. Create content with a news angle: original research, industry trends, data analysis, expert commentary
2. Pitch to journalists and editors who cover the topic
3. Coverage includes a link to the original content

**What makes content newsworthy**:
- **Data-driven insights**: "New research reveals [surprising finding about topic]"
- **Trend analysis**: "How [industry] changed in [timeframe]: a data analysis"
- **Expert commentary**: Cited experts providing perspective on current events (ties to E-E-A-T author entity strategy in `eeat-framework.md`)
- **Contrarian findings**: Data that challenges conventional wisdom

**Digital PR process**:
1. Identify journalists covering the topic (Muck Rack, Twitter/X lists, Google News)
2. Build a media list: publication, journalist, recent articles, contact method
3. Craft a pitch that leads with the data or finding, not the company
4. Offer exclusivity for early access to data
5. Follow up once, then stop

### HARO / Source Pitching

Connect Response (formerly HARO) and journalist query platforms match journalists seeking expert sources with subject matter experts.

**How it works**:
1. Monitor journalist queries on platforms: Connect Response, Qwoted, SourceBottle, Twitter/X #journorequest
2. Match queries to your company's expertise area
3. Respond with concise, quotable expert commentary
4. Coverage typically includes a link and expert attribution (supports E-E-A-T author entity)

**Response guidelines**:
- Respond within 1-2 hours (queries close fast)
- Lead with a quotable 1-2 sentence expert statement
- Include credentials and relevance: "I'm [name], [role] at [company], where we [relevant experience]"
- Offer additional data or context the journalist may not have
- Do not pitch your product; pitch your expertise

## Internal Linking Architecture

Internal links establish topical authority, distribute PageRank, and connect informational content to commercial pages. This section extends the internal linking rules in `technical-seo-checklist.md` with strategic architecture guidance.

### Hub-and-Spoke Topical Clusters

Every blog article belongs to a topical cluster anchored by a hub page.

**Structure**:
```
Hub Page (comprehensive category/topic guide)
├── Spoke: Subtopic Article 1 → links back to hub
├── Spoke: Subtopic Article 2 → links back to hub
├── Spoke: Subtopic Article 3 → links back to hub and to Spoke 1
└── Commercial Page → hub links here, spokes link here
```

**Rules**:
- Every spoke links to the hub (at least once, in body content)
- The hub links to every spoke
- Spokes link to related spokes when topically relevant (2-3 cross-links per spoke)
- Every spoke links to at least one relevant commercial page (Aleyda Solis's definition-layer-to-commercial-layer connection; see `content-engineering.md`)

### Contextual Link Rules

1. **Body content links carry more weight than sidebar/footer links.** Google's original PageRank paper and subsequent analyses confirm that in-content links pass more ranking signal than navigational links.
2. **Target 3-5 contextual internal links per article.** Fewer than 3 isolates the article. More than 10 dilutes the signal per link.
3. **Anchor text should describe the target page.** Use the target page's primary keyword or topic as anchor text. Avoid "click here" or "read more."
4. **Link from new articles to existing articles.** New articles should link to older, authoritative articles in the same cluster. This distributes freshness signals.
5. **Link from high-authority pages to new articles.** When a hub page gains external links, its internal links distribute authority to spoke pages.

### Link Depth and Crawl Budget

- **Maximum 3 clicks from the homepage** to any blog article (per `technical-seo-checklist.md`)
- **Every article in the XML sitemap** (required for indexation)
- **Orphan page detection**: Articles with zero internal links must be linked from at least the category page and the sitemap
- **Crawl priority**: Articles closer to the homepage receive more frequent crawling

## Anchor Text Distribution

Google's Penguin update penalized over-optimized anchor text profiles. A natural anchor text distribution is essential for sustainable link building.

### Target Distribution

| Anchor Text Type | Target Proportion | Example (for "project management software") |
|-----------------|-------------------|----------------------------------------------|
| **Exact match** | < 10% | "project management software" |
| **Partial match** | ~30% | "best project management tools", "project management software comparison" |
| **Branded** | ~40% | "Asana", "the Asana blog", "asana.com" |
| **Generic** | ~20% | "click here", "this guide", "learn more" |

### Why This Distribution

- **Branded anchors dominate natural profiles.** When real people link to content, they use the brand name or site name most often. A profile with > 30% exact match anchors is a Penguin risk signal.
- **Exact match anchors are rare in natural linking.** Most people do not link with the exact target keyword. A high proportion of exact match anchors signals manipulation.
- **Partial match anchors are common and safe.** People naturally use descriptive phrases that include part of the target keyword.
- **Generic anchors are natural but carry no topical signal.** They dilute the profile but are expected in small proportions.

### Anchor Text Rules for Internal Links

Internal link anchor text is less risky than external, but still matters:
- Use descriptive, keyword-relevant anchor text for internal links
- Vary anchor text across internal links to the same page
- Do not use the same exact anchor text for every internal link to a page
- Internal anchor text signals topical relevance to Google

### Anchor Text Audit

Quarterly, audit the external anchor text profile pointing to blog articles:

1. Pull anchor text data from Ahrefs, Moz, or SEMrush
2. Categorize each anchor as exact, partial, branded, or generic
3. Calculate percentages and compare to targets
4. If exact match exceeds 10%, prioritize branded and partial match links in future outreach
5. If branded is below 30%, increase brand-focused content and outreach

## Link Quality Assessment

Not all links are equal. A single high-quality link can outweigh dozens of low-quality links. Evaluate every potential link source before investing outreach effort.

### Quality Assessment Framework

| Signal | High Quality | Low Quality |
|--------|-------------|-------------|
| **Relevance** | Topically related to the blog article's subject | Unrelated topic, general directories |
| **Authority** | Domain has established search visibility and external citations | New domain, no search presence, no external links |
| **Traffic** | Site receives organic traffic (verify in SimilarWeb or Ahrefs) | Site has negligible organic traffic |
| **Editorial nature** | Link is given voluntarily based on content merit | Link is paid, traded, or part of a scheme |
| **Context** | Link appears within relevant body content | Link appears in footers, sidebars, or "sponsored" sections |
| **Anchor text** | Natural, descriptive, varied | Over-optimized exact match, or sitewide |

### Red Flags (Avoid These Links)

- **Private blog networks (PBNs)**: Networks of sites created solely to pass link equity. Google deindexes these regularly.
- **Link farms**: Pages or directories that exist only to list links. Zero topical relevance.
- **Sitewide links**: Footer or sidebar links that appear on every page of a site. These create thousands of links with the same anchor text.
- **Paid links without nofollow/ugc/sponsored**: Buying dofollow links violates Google's guidelines. If paying for placement, the link must use `rel="sponsored"` or `rel="nofollow"`.
- **Irrelevant directory links**: Being listed in a general directory (not a topically relevant one) provides no ranking signal.
- **Link exchange schemes**: Reciprocal link arrangements ("I link to you, you link to me") at scale. Google detects and devalues these.

### Link Quality Scoring

Score each potential link source on a 1-5 scale across these dimensions:

| Dimension | 5 (Excellent) | 1 (Poor) |
|-----------|---------------|----------|
| Topical relevance | Same industry/topic area | Completely unrelated |
| Domain authority | DR 70+ / DA 60+ | DR < 20 / DA < 20 |
| Organic traffic | 10K+ monthly visits | < 100 monthly visits |
| Link context | In-content, editorial | Footer/sidebar/sitewide |
| Outbound link count | < 50 on the page | > 200 on the page |

Target: average score >= 3.5 for link building efforts. Links scoring < 2 are unlikely to provide value and may carry risk.

## Link Velocity

Link velocity measures the rate at which a page acquires new backlinks over time. Unnatural velocity patterns are a ranking risk.

### Natural Growth Patterns

- **New content**: 0-5 links in the first month is normal for a blog article. Viral content may spike higher, but sustained rapid growth on a single page is unusual.
- **Established content**: 1-3 new links per month on an ongoing basis. Steady, gradual growth.
- **Evergreen content**: May experience periodic spikes when the topic trends or when the article is rediscovered.

### Red Flags for Google

- **Sudden spike without content trigger**: 50+ new links in a week with no content update, promotion event, or news cycle to explain it.
- **Uniform anchor text in spike**: If a sudden influx of links uses the same anchor text, Google interprets this as a coordinated campaign.
- **Links from unrelated domains**: A spike in links from domains with no topical relevance to the content.
- **Link velocity exceeding competitors by 10x+**: If your article acquires links at a rate far exceeding the top-ranking articles for the same query, the pattern may trigger algorithmic review.

### Sustainable Velocity Targets

| Article Age | Monthly New Links | Risk Level |
|-------------|-------------------|------------|
| 0-1 month | 0-10 | Normal (depends on promotion) |
| 1-3 months | 1-5 | Normal |
| 3-12 months | 1-3 | Healthy steady growth |
| 12+ months | 0-2 | Natural long-tail acquisition |

### Velocity Monitoring

- Track new referring domains weekly via Ahrefs or Moz
- Set alerts for: > 20 new referring domains in a single week on any single article
- Investigate spikes: did a promotion, news event, or social share cause it? If not, investigate whether negative SEO is occurring.

## Guest Posting Guidelines

Guest posting remains a legitimate link building tactic when done for audience exposure, not for link equity manipulation.

### Quality Standards

A legitimate guest post meets ALL of these criteria:
- **Published on a site with genuine audience**: The site has organic traffic, real readers, and editorial standards. Not a site built for guest posts.
- **Topically relevant**: The host site covers the same or adjacent topic area as the blog article.
- **Original, valuable content**: The guest post provides genuine value to the host site's audience. It is not a repurposed or spun version of existing content.
- **Author attribution**: The post is attributed to a real author with a verifiable identity (ties to E-E-A-T author entity strategy in `eeat-framework.md`).
- **Limited self-referential links**: Maximum 1-2 links to your own content within the body, and only when contextually relevant. Not a link-stuffed promotional piece.

### Nofollow Considerations

- **Google's stance**: Google treats `rel="nofollow"` as a hint, not a directive. Nofollow links from high-authority, topically relevant sites can still provide ranking benefit through discovery, traffic, and co-occurrence signals.
- **When to accept nofollow**: A nofollow link from a high-authority site (e.g., Forbes, TechCrunch) provides traffic, brand visibility, and potential follow-on links from other sites that discover the content through the original mention.
- **When to push for dofollow**: Guest posts on niche-relevant sites where the editorial context makes a dofollow link appropriate. If the site marks all guest post links as nofollow by policy, accept it rather than arguing.

### Editorial vs Paid

| Aspect | Editorial Guest Post | Paid/Sponsored Post |
|--------|---------------------|---------------------|
| Link attribute | `rel="nofollow"` or dofollow (editor's choice) | `rel="sponsored"` (required by Google) |
| Content control | Editorial discretion at host site | Advertiser may control content |
| Google compliance | Fully compliant | Compliant only if `rel="sponsored"` is used |
| Value | Higher (editorial trust) | Lower (Google discounts sponsored links) |
| Risk | None if content is genuine | Risk if `rel="sponsored"` is not used |

### Guest Post Quality Checklist

- [ ] Host site has > 1,000 monthly organic visits
- [ ] Host site is topically relevant to your content
- [ ] Host site has real editorial standards (not a content farm)
- [ ] Guest post is original, not repurposed
- [ ] Author is a real person with verifiable identity
- [ ] Maximum 2 self-referential links in the body
- [ ] Link anchor text is natural, not exact match keyword
- [ ] Link context is relevant to the surrounding content
- [ ] No link schemes: no "3 guest posts for 3 links back" arrangements

## Link Reclamation

Links that are lost or mentions that lack links represent untapped authority. Reclaiming these is one of the highest-ROI link building activities because the mention or link already exists — you are simply fixing a gap.

### Monitoring for Lost Links

**Causes of lost links**:
- Site redesigns: pages are moved or deleted without proper redirects
- Content updates: editors remove or change link references during updates
- CMS migrations: URL structures change, breaking old link targets
- Domain changes: the linking site changes domain without redirects

**Monitoring process**:
1. Track referring domains weekly via Ahrefs or Moz
2. Set alerts for lost referring domains or lost backlinks
3. For each lost link, determine the cause:
   - **Page removed (404)**: Request the editor restore the link or redirect to the new location
   - **Link removed from page**: Ask if the removal was intentional or an error
   - **Domain change**: Check if the content still exists at the new domain

**Outreach template for lost links**:
> Hi [Name], I noticed that the link to [your article title] on your page [URL] is no longer working / has been removed. The linked resource has been updated and is now at [new URL]. Would you consider restoring the link?

### Brand Mentions Without Links

When your company, content, or authors are mentioned without a link, you have a reclamation opportunity.

**How to find unlinked mentions**:
1. Set up Google Alerts for brand name, product names, and key author names
2. Search for brand mentions using: `"[company name]" -site:yourdomain.com`
3. Use Ahrefs or Moz "brand mentions" or "unlinked mentions" features

**Outreach template for unlinked mentions**:
> Hi [Name], Thanks for mentioning [company/content] in your article at [URL]. I'm glad you found it valuable! Would you consider adding a link to the original source at [URL] so your readers can access it directly?

**Success rate**: Unlinked mention outreach typically has a 15-30% conversion rate, significantly higher than cold link building outreach (2-5%).

## Social Signals and Rankings

The relationship between social signals (shares, likes, mentions) and search rankings is one of the most debated topics in SEO. The data is clear on correlation; the mechanism is disputed.

### Rand Fishkin's Correlation Data

Rand Fishkin's analysis (based on Searchmetrics and Moz data across thousands of SERPs) consistently shows:

- **Social shares correlate with higher rankings.** Pages with more social shares tend to rank higher in search results.
- **The correlation is real but the causation is debated.** Social shares do not appear to be a direct ranking factor in Google's algorithm. Google representatives have repeatedly stated that social signals are not used as ranking factors.
- **The likely mechanism**: Social sharing increases content visibility, which leads to more organic link acquisition, which is a direct ranking factor. Social signals are a proxy for content that attracts links.

### What This Means for Blog Content

1. **Social sharing is worth investing in, but as a distribution channel, not a ranking factor.** The goal of social promotion is to get content in front of people who might link to it, not to accumulate social signals.
2. **Content that gets shared also gets linked.** The same qualities that make content shareworthy (originality, utility, emotional resonance) also make it link-worthy.
3. **Social proof affects click-through rate.** Articles with visible social proof (share counts, comments) may receive higher CTR in search results, which is an indirect ranking signal.
4. **Social profiles contribute to entity authority.** A company's social presence (follower count, engagement rate, content quality) contributes to Google's entity understanding. This is a brand authority signal, not a link signal.

### Practical Social Distribution Strategy

For each published blog article:
1. **Share across company social channels** within 1 hour of publication
2. **Tailor the message per platform**: professional angle for LinkedIn, data/highlight for Twitter/X, visual for Instagram
3. **Tag cited sources and mentioned individuals**: "Our new analysis cites @expert's work on [topic]" increases share likelihood
4. **Engage with reshares**: Respond to comments, answer questions, provide additional data
5. **Reshare after 30 days**: Content that performed well deserves a second distribution push

### Social Attribution Tracking

Track the path from social share to link acquisition:
- Monitor referral traffic from social platforms in Google Analytics
- Cross-reference with new referring domains in Ahrefs/Moz
- Articles that receive social shares but no new referring domains may need better link-earning content (see content-driven link earning above)
- Articles that receive both social shares and new links validate the social-to-link pipeline