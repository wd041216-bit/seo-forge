# Content Engineering for AI Search

Passage-level content optimization framework for AI search retrieval and citation. Based on Mike King's Relevance Engineering methodology and Aleyda Solis's AI search optimization guidance.

## Passage-Level Optimization

Each H2 section must be a **semantic unit** — independently understandable, independently citable, and independently retrievable by AI search systems.

### What This Means in Practice

AI search systems do not evaluate pages. They evaluate **chunks** (passages). A page can rank well in traditional search while having zero passages that survive the AI selection funnel. Every key piece of information must be a self-contained unit that can be extracted and synthesized without requiring surrounding context.

### Guidelines for Self-Contained Passages

1. **One idea per section.** Each H2 section addresses a single topic. If you find yourself writing "and also" or "moving on to," you need a new section.
2. **Topic sentence first.** The first sentence of each paragraph should state the key claim. Supporting detail follows. This mirrors how LLMs extract — they weight opening sentences more heavily.
3. **No forward references.** A passage must not require the reader (or the LLM) to have read a previous section to understand it. Define terms inline.
4. **No dangling context.** A passage must not end with a transition that depends on the next section. Each section closes its own thought.
5. **Entity mentions are explicit.** If a passage is about "schema markup," the phrase "schema markup" must appear in the passage — not just "it" or "this approach."

### Anti-Patterns

- Burying the key fact in the third paragraph of a section
- Opening with an anecdote or hook before the factual claim
- Writing sections that only make sense after reading the previous section
- Using pronoun references that cross section boundaries

## Extractability Requirements

Content must be structured so that LLMs can extract key facts directly. This means writing in a **declarative factual tone** rather than promotional copywriting.

### Declarative vs Promotional Tone

| Promotional (Low Extractability) | Declarative (High Extractability) |
|----------------------------------|-----------------------------------|
| "Our revolutionary platform delivers stunning results" | "The platform processes 10,000 requests per second with 99.95% uptime" |
| "You'll love how easy it is to get started" | "Setup requires three steps: account creation, API key generation, and endpoint configuration" |
| "Industry-leading performance" | "Benchmark tests show 2.3x faster response times than the closest competitor" |
| "This game-changing feature will transform your workflow" | "The feature reduces manual data entry by 67% according to internal testing across 50 organizations" |

### Why This Matters

LLMs preferentially cite passages with:
- Specific numbers and data points
- Clear definitions and technical specifications
- Attribution to named sources
- Conditional statements with scope ("For datasets under 1GB, batch processing is 40% faster")

Promotional language is noise in the extraction pipeline. It adds token count without adding information. LLMs trained on factual corpora learn to discount superlatives and vague claims.

## Evidence Density Targets

Each section should contain at least **2-3 specific, verifiable claims** with data points. Evidence density is a primary selection signal in AI search.

### What Counts as a Verifiable Claim

- A specific number with units: "reduces load time by 1.2 seconds"
- A named comparison: "3x faster than [Competitor X]"
- A citation-backed statistic: "According to [Source], 67% of users..."
- A specific configuration: "Set the `max_tokens` parameter to 4096"
- A temporal benchmark: "After 6 weeks of testing..."

### What Does Not Count

- Vague superlatives: "significantly faster"
- Unattributed generalizations: "studies show that..."
- Promotional claims: "the best in the industry"
- Truisms: "it's important to optimize performance"

### Evidence Density Checklist

For each H2 section, verify:
- [ ] At least 2 specific, verifiable claims
- [ ] At least 1 claim includes a number, percentage, or named comparison
- [ ] Claims are attributed to a source when possible
- [ ] Claims are scoped (not absolute statements)

## Chunk-Level Retrieval Design

Content must be structured for vector database indexing — the mechanism AI search systems use to retrieve candidate passages before synthesis.

### Structure Rules for Chunking

1. **Short paragraphs (100-200 words).** Long paragraphs get split during chunking, breaking semantic coherence. Keep paragraphs focused on one claim.
2. **Clear topic sentences.** The first sentence of each paragraph should contain the primary entity and claim. This sentence becomes the densest vector in the chunk.
3. **Entity mentions at the start.** Mention the key entity (product, technology, concept) in the first sentence of each paragraph. Don't bury it mid-paragraph.
4. **Avoid orphaned pronouns.** Every pronoun reference should be resolvable within the same paragraph. Cross-paragraph pronoun references break when chunks are split.
5. **Use heading hierarchy as chunk boundaries.** H2 sections are natural chunk boundaries. H3 subsections within an H2 can be sub-chunks. Don't create chunks that span H2 boundaries.

### Vector-Optimized Writing Pattern

```
[Entity + claim]. [Supporting evidence with data]. [Scope or condition].
[Secondary claim about same entity]. [Comparison or alternative].
```

Example:
> Schema markup increases rich result eligibility by 36% for qualifying content types (Google, 2025). For Article schema, pages with correctly implemented JSON-LD appear in rich results 2.7x more often than those without. This applies to content that meets Google's structured data quality guidelines.

## Citation-Worthiness Criteria

What makes a passage likely to be cited by AI search (Aleyda Solis's concept). AI search systems select passages for synthesis based on citation-worthiness signals.

### The Four Signals of Citation-Worthiness

1. **Factual precision.** The passage states a specific, verifiable fact rather than an opinion or generalization. LLMs preferentially select passages where they can extract a single clear claim.
2. **Unique data.** The passage contains information not commonly found in competing sources. Original research, proprietary benchmarks, and primary data are the highest-value citation targets.
3. **Authoritative sources.** The passage attributes its claims to a recognized authority — a named study, a specific organization, a cited paper. Attribution signals verification to the LLM.
4. **Clear definitions.** The passage defines a term or concept in a way that is concise and unambiguous. LLMs frequently cite definitional passages because they serve as authoritative references.

### Citation-Worthiness Checklist

For each passage, ask:
- [ ] Does this passage contain a fact that no other top-10 result states this precisely?
- [ ] Does this passage attribute its claims to a named source?
- [ ] Does this passage define a term or concept that a user might query?
- [ ] Could an LLM extract a single sentence from this passage and use it as a citation?

If the answer to all four is "no," the passage is unlikely to be cited. Rewrite it.

## Information Gain

Content should add something not already available in the top 10 search results for the target query. Mike King's principle: **"Publish only what you can uniquely publish."**

### The Information Gain Test

Before publishing, compare the article against the current top 10 results. Ask:

1. **Novel data**: Does the article contain data points, benchmarks, or case studies not in the existing results?
2. **Novel perspective**: Does it offer an analysis framework, taxonomy, or mental model not in the existing results?
3. **Novel experience**: Does it include first-hand testing results, specific observations, or personal findings not in the existing results?
4. **Novel connections**: Does it connect concepts across domains in a way that existing results do not?

If the article does not add at least one of these four, it is redundant content. AI search systems have no reason to cite it over the existing results it duplicates.

### Redundancy Detection

Common patterns that indicate zero information gain:
- Paraphrasing the same documentation everyone else paraphrases
- Summarizing features that every review already summarizes
- Regurgitating the same "best practices" list
- Writing the 11th article with the same structure as the first 10

### Information Gain Strategies

- **Original testing**: Run your own benchmarks and publish the results
- **Composite analysis**: Synthesize multiple sources into a unified framework
- **Gap filling**: Identify what the top 10 results miss and write specifically about that
- **Temporal advantage**: Update numbers, features, and pricing that existing results have outdated
- **Structural innovation**: Present information in a format (checklist, decision tree, comparison matrix) that existing results do not use

## Query Fan-Out Coverage

Mike King's methodology for ensuring content is represented across all branches of an AI search query.

### What Is Query Fan-Out?

When a user submits a query to an AI search system, the system decomposes it into a tree of subqueries. For example, "best running shoes 2026" might fan out into:

```
best running shoes 2026
├── running shoe reviews 2026
├── running shoe comparison by price
├── running shoe injury prevention features
├── running shoe durability data
├── running shoe sizing guide
└── running shoe brand reputation
```

Each branch is routed to different sources. If your content only addresses the trunk query, you compete for one retrieval slot. If your content addresses multiple branches, you can be represented in multiple retrieval slots within the same AI answer.

### How to Implement Fan-Out Coverage

1. **Decompose the target query.** List the 5-8 most likely subqueries an AI system would generate from the target keyword.
2. **Audit existing content.** Check which subquery branches are already covered by your article.
3. **Add passages for uncovered branches.** Each subquery that lacks coverage needs a dedicated passage (not just a mention).
4. **Verify passage independence.** Each subquery-targeted passage must be self-contained — it may be the only passage of yours that the AI system retrieves for that branch.

### Fan-Out Coverage Template

| Subquery Branch | Covered? | Passage Location | Passage Self-Contained? |
|-----------------|----------|-------------------|------------------------|
| [Subquery 1] | Yes/No | [H2 Section] | Yes/No |
| [Subquery 2] | Yes/No | [H2 Section] | Yes/No |
| [Subquery 3] | Yes/No | [H2 Section] | Yes/No |
| [Subquery 4] | Yes/No | [H2 Section] | Yes/No |
| [Subquery 5] | Yes/No | [H2 Section] | Yes/No |

Target: 70%+ branch coverage for the primary keyword's fan-out tree.

## Definition-Layer to Commercial-Layer Connection

Aleyda Solis's strategy for AI search visibility: dominate informational/definitional content first (which LLMs are more likely to cite), then connect those pages to commercial pages via schema markup and internal links.

### How It Works

1. **Definition layer**: Create passages that define, explain, and contextualize key terms. These are the passages LLMs cite most frequently.
2. **Connection layer**: Use schema markup (especially `Article`, `Organization`, and `BreadcrumbList`) and internal links to connect definitional content to commercial pages.
3. **Commercial layer**: Transactional and product pages benefit from the authority and citation flow established by the definition layer.

### Implementation for Blog Articles

- Each article should include at least 1-2 definitional passages that clearly explain a key concept
- These passages should link to relevant product or service pages
- Schema markup should explicitly connect the article to the organization entity
- Breadcrumbs should show the topical hierarchy from definition to commercial content