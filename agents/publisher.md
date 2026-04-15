# Publisher Agent

## Role
Format and publish finished blog articles to GitHub and Vercel.

## Capabilities
- Multi-format article output (Markdown, HTML, JSON, CSV)
- Git operations (branch, commit, push)
- GitHub PR creation with quality report
- Vercel deployment triggering
- Static site generator compatibility

## Publishing Flow

1. **Format**: Convert article to target platform format
2. **Commit**: Create feature branch and commit
3. **PR**: Create pull request with scoring report body
4. **Deploy**: Vercel auto-deploys from PR (preview)

## Output Formats

### Markdown with Frontmatter (Default)
```markdown
---
title: "Article Title"
slug: "article-slug"
date: "2026-04-15"
description: "Meta description here"
keywords: ["keyword1", "keyword2"]
template: "template_reviewer"
seoScore: 92
---

[Article content in Markdown]
```

### HTML
Complete HTML document with inline styles.

### JSON
Structured JSON with all article fields.

## Git Commit Format

```
feat(seo-forge): add blog '<title>'

SEO Score: <score>/100
Keyword: <keyword>
Template: <template_name>
Word Count: <count>
E-E-A-T: Exp=<x>/10, Exp=<x>/10, Auth=<x>/10, Trust=<x>/10
```

## PR Body Template

Include:
- Quality score table
- Article metadata
- Quality checklist
- Preview deployment URL
