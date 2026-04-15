# Deployment Guide

## GitHub Integration

### Prerequisites
- GitHub CLI (`gh`) installed and authenticated
- Git configured with user name and email
- Repository exists for the blog

### Article Commit Format

```bash
git checkout -b seo-forge/<keyword-slug>
git add <article-file>
git commit -m "feat(seo-forge): add blog '<title>'

SEO Score: <score>/100
Keyword: <keyword>
Template: <template_name>
Word Count: <count>
E-E-A-T: Exp=<x>/10, Exp=<x>/10, Auth=<x>/10, Trust=<x>/10"
git push -u origin seo-forge/<keyword-slug>
```

### Pull Request

```bash
gh pr create \
  --title "SEO Blog: <title>" \
  --body "$(cat <<'EOF'
## SEO Forge: Auto-Generated Blog Article

### Quality Scores
| Axis | Score | Target |
|------|-------|--------|
| SEO Quality | X/25 | 20+ |
| E-E-A-T Compliance | X/25 | 20+ |
| Content Depth | X/25 | 20+ |
| Reference Authority | X/25 | 20+ |
| **Total** | **X/100** | **90+** |

### Article Details
- **Keyword**: <keyword>
- **Template**: <template_name>
- **Word Count**: <count>
- **References**: <count> verified sources

### Checklist
- [x] E-E-A-T compliant
- [x] Keyword density 1-2%
- [x] All reference URLs verified
- [x] 6+ FAQ questions
- [x] Balanced pros and cons
EOF
)"
```

## Vercel Deployment

### Prerequisites
- Vercel CLI installed (`npm i -g vercel`)
- Project linked to Vercel

### Auto-Deploy Flow
1. PR creation triggers Vercel preview deployment
2. Review the preview URL
3. Merge PR to trigger production deployment

### Manual Deploy (if needed)

```bash
vercel --prod
```

### Vercel Configuration

Ensure `vercel.json` is configured for your blog framework:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "nextjs"
}
```

## Multi-Platform Support

The skill supports these blog platforms:

### Static Site Generators
- **Next.js**: Articles as MDX files in `content/blog/`
- **Astro**: Articles as Markdown in `src/content/blog/`
- **Hugo**: Articles as Markdown in `content/posts/`
- **Gatsby**: Articles as Markdown in `src/content/blog/`

### CMS Platforms
- **WordPress**: Via REST API or XML-RPC
- **Ghost**: Via Admin API
- **Framer CMS**: Via CSV import (35-field format)

### Output Formats
- **Markdown with Frontmatter** (default)
- **HTML** (for direct embedding)
- **JSON** (for API-based publishing)
- **CSV** (for Framer CMS batch import)
