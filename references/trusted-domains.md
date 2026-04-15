# Trusted Reference Domains

## Approved Domains for Reference URLs

When adding authoritative references to blog articles, prioritize these domains:

### Academic & Research
- stanford.edu, mit.edu, harvard.edu, cmu.edu, berkeley.edu, oxford.ac.uk, cambridge.org
- ieee.org, acm.org, nature.com, science.org, arxiv.org, springer.com, elsevier.com
- nih.gov, nist.gov, nsf.gov

### Technology & Industry
- openai.com, research.google, deepmind.com, anthropic.com
- microsoft.com, nvidia.com, aws.amazon.com, cloud.google.com
- github.com, huggingface.co, pytorch.org, tensorflow.org
- developer.mozilla.org, w3.org

### Business & Analysis
- hbr.org, mckinsey.com, bcg.com, deloitte.com, bain.com
- gartner.com, forrester.com, idc.com
- reuters.com, bloomberg.com, wsj.com, ft.com, economist.com

### Tech Media
- techcrunch.com, wired.com, theverge.com, technologyreview.com
- venturebeat.com, thenextweb.com, arstechnica.com, zdnet.com

### General Reference
- wikipedia.org, britannica.com
- statista.com, census.gov, worldbank.org

## URL Rules

1. **Only use homepage or well-known stable paths**
   - ✅ `https://openai.com/research`
   - ✅ `https://en.wikipedia.org/wiki/Topic`
   - ✅ `https://arxiv.org/abs/XXXX.XXXXX`
   - ❌ Never guess article paths like `/2024/01/15/some-article`

2. **Never fabricate URLs** — if you don't know the exact URL, use the domain root

3. **Verify URLs** — HEAD request verification before including

4. **No self-referential links** — never include links to the company's own domain in References

## Reference Format

```html
<p>[1] Source Name - "Title" - <a href="URL" target="_blank">URL</a> - Description</p>
```

The URL MUST appear twice:
1. Inside the `href` attribute
2. As visible clickable text between the `<a>` tags
