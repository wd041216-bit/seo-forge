# Technical SEO Checklist for Blog Content

On-page technical SEO requirements for blog articles, covering structured data, canonicalization, internal linking, Core Web Vitals, crawl efficiency, international SEO, and pre/post-deployment validation. Based on Aleyda Solis's SP2 framework and AI search optimization guidance.

## Structured Data Schemas

Blog articles must include structured data to enable rich results, provide entity-level signals for AI search, and connect informational content to the organization entity.

### Article Schema (Required)

Every blog article must include `Article` schema in JSON-LD format in the page `<head>`.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title Here",
  "description": "Meta description text (120-160 characters)",
  "image": "https://example.com/images/article-cover.jpg",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://example.com/authors/author-name",
    "sameAs": [
      "https://linkedin.com/in/author-name",
      "https://twitter.com/author-name"
    ]
  },
  "publisher": {
    "@type": "Organization",
    "name": "Company Name",
    "url": "https://example.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "datePublished": "2026-04-16",
  "dateModified": "2026-04-16",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/blog/article-slug"
  }
}
```

### FAQ Schema (When Applicable)

Articles with FAQ sections must include `FAQPage` schema. This enables FAQ rich results and increases AI search citation likelihood for Q&A passages.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here (50-80 words, factual tone)"
      }
    }
  ]
}
```

### HowTo Schema (For Tutorial Content)

Articles using the Tutorial Expert template must include `HowTo` schema.

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [accomplish task]",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Step name",
      "text": "Step description with specific details"
    }
  ]
}
```

### BreadcrumbList Schema (Required)

Every blog article must include breadcrumb schema to establish topical hierarchy.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://example.com/blog"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Category Name",
      "item": "https://example.com/blog/category"
    },
    {
      "@type": "ListItem",
      "position": 4,
      "name": "Article Title"
    }
  ]
}
```

### Organization Schema (Site-Wide)

Include on every page to establish the publisher entity for AI search.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Company Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://linkedin.com/company/name",
    "https://twitter.com/name",
    "https://youtube.com/@name"
  ]
}
```

### Schema Validation Rules

- All JSON-LD must pass Google's Rich Results Test without errors
- Do not duplicate schema types on the same page
- Date formats must use ISO 8601 (`YYYY-MM-DD`)
- Image URLs must be absolute and return 200 status
- Author `sameAs` links must point to verifiable external profiles

## Canonicalization Rules

Incorrect canonicalization causes indexation problems, duplicate content penalties, and wasted crawl budget.

### Rules for Blog Content

| Scenario | Canonical Configuration |
|----------|------------------------|
| Standard blog article | `rel=canonical` pointing to the article's canonical URL |
| Blog pagination (page 2, 3...) | `rel=canonical` pointing to each page itself (self-referencing), NOT to page 1 |
| Category page | `rel=canonical` pointing to the category URL |
| Syndicated content | `rel=canonical` pointing to the original source URL |
| AMP version | `rel=canonical` pointing to the non-AMP version |
| Print-friendly version | `rel=canonical` pointing to the standard version |
| Same content, different query params | `rel=canonical` pointing to the parameter-free URL |

### Common Mistakes

- **Paginating canonical to page 1.** This tells Google that page 2, 3, etc. are duplicates of page 1. They are not — they contain different articles. Use self-referencing canonicals on paginated pages.
- **Missing canonical on category pages.** Category pages can be accessed via multiple URL patterns (with/without trailing slash, with/without page parameter). Pick one and canonicalize to it.
- **Cross-domain canonical for original content.** If you syndicate content to another domain, the syndicating site should canonicalize to your original. Never canonicalize your original to the syndicated version.

## Internal Linking Strategy

Internal links establish topical authority, distribute PageRank, and help AI search systems understand the relationship between informational and commercial content.

### Hub-and-Spoke Model

- **Hub page**: A comprehensive category or topic page that serves as the central authority on a topic
- **Spoke pages**: Individual blog articles that cover subtopics in depth
- **Link pattern**: Every spoke page links back to the hub. The hub links to every spoke. Spoke pages link to related spoke pages when topically relevant.

### Contextual Link Rules

1. **Link within body content, not just in sidebars or footers.** Google weights in-content links more heavily than navigational links.
2. **Anchor text should be descriptive.** Use the target page's primary keyword or topic as anchor text. Avoid "click here" or "read more."
3. **Link from the article to relevant commercial pages.** This implements Aleyda Solis's definition-layer-to-commercial-layer connection.
4. **Link between related articles.** Cross-link articles that cover related subtopics to build topical clusters.
5. **Avoid excessive internal links per page.** Target 3-5 contextual internal links within the body content. More than 10 contextual links dilutes the signal.

### Link Depth Limits

- **Maximum 3 clicks from the homepage** to any blog article. Articles deeper than 3 clicks receive less crawl budget and PageRank.
- **Sitemap inclusion.** Every blog article must be in the XML sitemap.
- **Orphan page detection.** Articles with zero internal links pointing to them are orphan pages. They must be linked from at least the category page and the sitemap.

### Anchor Text Guidelines

| Good Anchor Text | Bad Anchor Text |
|-----------------|-----------------|
| "project management software comparison" | "click here" |
| "how to configure API rate limiting" | "this article" |
| "our analysis of CRM pricing" | "read more" |
| "the complete guide to SEO audits" | "link" |

## Core Web Vitals for Blogs

Blog pages with images, tables, and code blocks have specific performance challenges.

### LCP (Largest Contentful Paint)

Target: < 2.5 seconds

- **Hero images**: Use `srcset` with responsive sizes. Serve WebP format with JPEG fallback.
- **Image optimization**: Compress all images to < 100KB where possible. Use lazy loading for below-fold images (`loading="lazy"`).
- **Preload critical resources**: `<link rel="preload">` for the hero image and critical CSS.
- **Server response time**: Target TTFB < 800ms. Use CDN for static assets.

### FID / INP (Interaction to Next Paint)

Target: < 200ms (INP)

- **Third-party scripts**: Defer non-critical scripts. Audit analytics, chat widgets, and ad scripts.
- **Code block rendering**: If using syntax highlighting, defer the highlighter library. Render code blocks as `<pre><code>` with progressive enhancement.
- **Table rendering**: Avoid JavaScript-dependent tables. Use HTML `<table>` elements with CSS for responsive overflow.

### CLS (Cumulative Layout Shift)

Target: < 0.1

- **Image dimensions**: Always specify `width` and `height` attributes on `<img>` tags. This reserves space and prevents layout shift when images load.
- **Ad slots**: If ads are present, reserve their space in CSS even before the ad loads.
- **Dynamic content**: Any content loaded after initial render (CTAs, pop-ups, related articles) must not push existing content down.
- **Font loading**: Use `font-display: swap` or `font-display: optional` to prevent FOIT (Flash of Invisible Text) layout shifts.

## Crawl Efficiency

### robots.txt Directives for Blog Content

```
User-agent: *
Allow: /blog/
Disallow: /blog/drafts/
Disallow: /blog/preview/
Disallow: /blog/*?preview=*

Sitemap: https://example.com/sitemap.xml
```

- Allow crawling of all published blog content
- Block draft and preview URLs
- Block URLs with preview parameters
- Reference the XML sitemap location

### XML Sitemap Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/blog/article-slug</loc>
    <lastmod>2026-04-16</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
```

- Include all published blog articles
- Update `lastmod` when content is significantly revised
- Split sitemaps at 50,000 URLs — use a sitemap index file
- Submit to Google Search Console after updates

### Pagination Handling

- Use `rel="next"` and `rel="prev"` link headers for blog pagination (Note: Google no longer uses these, but Bing still may)
- Self-referencing canonicals on each paginated page
- Include paginated pages in the XML sitemap
- Add a "view all" option if the total paginated content is under 10MB

## International / Multilingual SEO

The blog-config.json supports 8 languages. Correct international SEO configuration is essential to avoid duplicate content across locales and ensure the right content reaches the right audience.

### hreflang Configuration

For each language/locale version of an article, include `hreflang` annotations in the page `<head>`:

```html
<link rel="alternate" hreflang="en" href="https://example.com/blog/article-slug" />
<link rel="alternate" hreflang="es" href="https://example.com/es/blog/article-slug" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/blog/article-slug" />
<link rel="alternate" hreflang="de" href="https://example.com/de/blog/article-slug" />
<link rel="alternate" hreflang="x-default" href="https://example.com/blog/article-slug" />
```

### hreflang Rules

1. **Bi-directional annotations.** If page A links to page B via hreflang, page B must link back to page A. Missing return annotations cause Google to ignore both.
2. **Include `x-default`.** The `x-default` annotation specifies the fallback page for languages not explicitly listed.
3. **Language-region codes.** Use `hreflang="en"` for language-only, or `hreflang="en-US"` for language-region when content differs by region (e.g., en-US vs en-GB).
4. **Self-referencing.** Each page must include its own hreflang annotation in the set.
5. **Absolute URLs.** All hreflang URLs must be absolute.

### Locale-Specific URL Patterns

| Pattern | Example | Recommendation |
|---------|---------|----------------|
| Subdirectory | `/es/blog/article` | Recommended for most cases. Simple to implement, single domain authority |
| Subdomain | `es.example.com/blog/article` | Acceptable for larger operations with separate infrastructure per locale |
| ccTLD | `example.es/blog/article` | Best for truly independent locale operations; expensive and complex |
| Parameter | `?lang=es` | Avoid. Google recommends against parameter-based locale signals |

### Content Localization Requirements

- Articles must be translated, not just machine-translated. Verify translations for accuracy and natural phrasing.
- Meta descriptions must be localized (not translated character-by-character).
- Date formats should match locale conventions (MM/DD/YYYY vs DD/MM/YYYY).
- Currency and units should match the locale.
- Internal links within translated articles should point to the same-language versions of target pages.

## Pre-Deployment SEO Validation

Aleyda Solis's continuous validation loop: check SEO compliance before publishing, not after.

### Validation Checklist

- [ ] **Schema validation**: All JSON-LD passes Google Rich Results Test without errors
- [ ] **Canonical tag**: Present and correct (self-referencing for original content)
- [ ] **Meta robots**: Not set to `noindex` or `nofollow` on published articles
- [ ] **Title tag**: Present, 50-60 characters, contains main keyword
- [ ] **Meta description**: Present, 120-160 characters, contains keyword in first 60 chars
- [ ] **Heading hierarchy**: Single H1 (title), proper H2/H3 nesting, no skipped levels
- [ ] **Image alt text**: All images have descriptive alt text with keyword where relevant
- [ ] **Internal links**: At least 3 contextual internal links within body
- [ ] **External references**: At least 4 references with valid, verified URLs
- [ ] **URL structure**: Clean slug, ≤6 words, keyword-rich, no special characters
- [ ] **Open Graph tags**: `og:title`, `og:description`, `og:image`, `og:url` present
- [ ] **hreflang**: Present if the article has translated versions
- [ ] **Mobile-friendliness**: Article renders correctly on 375px viewport

## Post-Deployment Monitoring

After publication, verify that the article is correctly indexed and performing as expected.

### Day 1 Checks

- [ ] **Indexation**: Submit URL to Google Search Console via URL Inspection tool
- [ ] **Rendering test**: Use Google's URL Inspection tool to verify rendered HTML matches expected content
- [ ] **Structured data test**: Verify rich results eligibility in Google Rich Results Test (live URL mode)
- [ ] **Mobile test**: Verify mobile-friendliness in Google's Mobile-Friendly Test (live URL mode)
- [ ] **Canonical verification**: Confirm Google recognizes the correct canonical URL via URL Inspection

### Week 1 Checks

- [ ] **Indexation confirmed**: Article appears in `site:` search results
- [ ] **Initial ranking**: Check ranking position for the primary keyword
- [ ] **Click data**: Verify impressions and clicks in Search Console
- [ ] **Rich results**: Confirm any eligible rich results (FAQ, HowTo, Article) are appearing

### Month 1 Checks

- [ ] **Ranking trajectory**: Track ranking movement for primary and secondary keywords
- [ ] **Organic traffic**: Measure organic sessions to the article
- [ ] **Engagement metrics**: Check bounce rate, time on page, and scroll depth
- [ ] **Internal link flow**: Verify the article is receiving internal links from new content

### Automated Monitoring

- Schedule weekly crawls (via ContentKing, Lumar, or Screaming Frog) to detect technical regressions
- Set up alerts for: canonical changes, noindex additions, schema errors, broken internal links
- Monitor Core Web Vitals via CrUX data in Search Console
- Track indexation status weekly — any de-indexed articles require immediate investigation