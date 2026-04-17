# E-E-A-T Compliance Framework

Google's E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is the cornerstone of high-quality SEO content. Every article must score well on all four dimensions.

This framework goes beyond checklist compliance. It distinguishes surface E-E-A-T signals (easy to fake) from deep E-E-A-T signals (what actually correlates with Google's quality decisions), separates Page Quality from Needs Met evaluation, and gates content by YMYL harm potential before generation begins.

## YMYL Harm-Potential Assessment

Before content generation begins, assess whether the topic falls under YMYL (Your Money or Your Life) and the degree of harm potential. This assessment determines the E-E-A-T threshold the content must meet.

### Three-Tier YMYL Classification

| Tier | Harm Potential | Examples | E-E-A-T Threshold |
|------|---------------|----------|-------------------|
| **High** | Content that could directly cause financial loss, health harm, or safety risk | Medical advice, financial planning, legal guidance, safety procedures | Maximum: credentialed authors, cited sources, editorial oversight, independent corroboration |
| **Medium** | Content that could indirectly affect important decisions | Business software reviews, investment context, health-adjacent lifestyle | Elevated: verified expertise, specific evidence, balanced perspective |
| **Low** | Content where harm potential is negligible | Entertainment, hobbies, personal productivity, non-YMYL tech reviews | Standard: basic transparency, honest claims, functional author attribution |

### YMYL Overapplication Anti-Pattern

Do not apply maximum E-E-A-T requirements to content that lacks harm potential. A review of project management software does not need a board-certified physician author. Lily Ray's analysis of post-Medic updates shows that Google scales E-E-A-T scrutiny to YMYL impact — the system does not treat all content as if it were medical advice.

**Decision rule**: If the content cannot plausibly cause harm to a user's health, finances, or safety, it is not Tier 1 YMYL. Apply proportional requirements.

### YMYL Gate Checklist

- [ ] Is this topic YMYL? (health, finance, safety, legal)
- [ ] If yes, what is the harm potential tier?
- [ ] Does the author have credentials appropriate to the harm tier?
- [ ] Are claims supported by sources appropriate to the harm tier?
- [ ] Is editorial oversight required before publication?

## Scoring Rubric (1-10 per dimension)

### Experience (Target: 8/10)

**What it measures**: Does the content demonstrate first-hand experience with the product/service/topic?

**Requirements**:
- Write from first-person perspective using "I", "my", "we", "our" at least 15-20 times
- Share REAL testing/experience timeline: "I tested [product] for [X weeks/months]..."
- Describe SPECIFIC usage scenarios: "When I first tried...", "During my testing..."
- Include PERSONAL observations: "I noticed that...", "In my experience..."
- Mention CHALLENGES faced: "I initially struggled with...", "One issue I encountered..."
- Provide CONCRETE examples: "For instance, when I created...", "One time, I tried to..."

**Example opening**:
> "I've been testing [product] for the past 3 months to [use case], and I want to share my honest, hands-on experience with you..."

### Expertise (Target: 7+/10)

**What it measures**: Does the content demonstrate deep knowledge of the topic?

**Requirements**:
- Provide TECHNICAL specifications relevant to the industry
- Include DETAILED steps with clear explanations
- Use industry-specific TERMINOLOGY correctly and consistently
- Explain PARAMETERS clearly: costs, metrics, configurations, settings
- Offer ADVANCED tips: optimization techniques, best practices, pro-level workflows
- Include TROUBLESHOOTING: common issues and solutions

### Authoritativeness (Target: 8/10)

**What it measures**: Does the content establish credibility through comparison and evidence?

**Requirements**:
- Provide COMPARATIVE analysis against named real competitors
- Express PROFESSIONAL opinions with evidence backing
- Include BALANCED view with honest pros AND cons:
  - Pros: 3-5 genuine advantages with specific examples
  - Cons: 2-3 honest limitations or drawbacks
- Specify USE CASES clearly: who should use this, who shouldn't
- Offer ACTIONABLE recommendations
- Mention ALTERNATIVES: real competing products/services

**Critical rule**: NEVER compare against "custom development", "traditional methods", or "manual processes". Only compare against real, named competing products/services.

### Trustworthiness (Target: 8/10)

**What it measures**: Is the content transparent and honest?

**Requirements**:
- DISCLOSE relationships clearly
- LIMIT marketing language: avoid "amazing", "stunning", "perfect", "revolutionary"
- USE factual descriptions: replace "stunning results" with specific metrics
- PROVIDE specific evidence: concrete numbers, test results, measurements
- CITE independent sources: at least 2-3 external references per article
- ACKNOWLEDGE limitations honestly
- AVOID absolute claims: replace "always works" with "works reliably in most cases"
- MAXIMUM 3 CTA buttons total (not per section)

## Deep vs Surface E-E-A-T Signals

Surface signals are easy to add and commonly faked. Deep signals require genuine investment and are what actually correlate with Google's quality decisions. Cyrus Shepard's 400-site analysis showed that surface signals (author boxes, About pages) do not predict core update winners.

### Signal Classification

| Signal Type | Surface (Easy to Add) | Deep (Hard to Fake) |
|-------------|----------------------|---------------------|
| **Experience** | First-person pronouns ("I tested this") | Specific methodology, reproducible observations, named challenges with context |
| **Expertise** | Industry jargon, credential badges | Technical depth, nuanced analysis, original insights not found in competing content |
| **Authoritativeness** | Author bio box, About page | Independent corroboration (cited by others, referenced in industry), verified credentials |
| **Trustworthiness** | Disclosure statement, privacy policy | Transparent methodology, balanced perspective, independently verifiable claims |

### Deep Signal Requirements

**Genuine reputation**: The author or organization is recognized by independent third parties — cited in other publications, referenced in industry discussions, or known in the field beyond self-promotion.

**Verified credentials**: Claims of expertise are backed by verifiable facts — degrees, certifications, years of experience, published work, or public recognition. An author bio that says "expert" is surface. A bio that links to a LinkedIn profile with 10 years of relevant experience and published work is deep.

**Independent corroboration**: Claims in the content can be verified through sources other than the publishing site. If the only source for a claim is the article itself, it lacks corroboration.

**Testing methodology**: For content that makes performance or quality claims, the methodology should be explicit enough that a reader could reproduce the test. "I tested it" is surface. "I tested it over 6 weeks using dataset X with the following configuration" is deep.

## Needs Met as Separate Evaluation

A high-quality page can still fail user intent. Page Quality (PQ) and Needs Met are independent axes — this is the core distinction from Google's Quality Rater Guidelines that Cyrus Shepard's rater experience emphasizes.

### The Two-Axis Model

**Page Quality (PQ)**: How well-made is the content? Is it accurate, comprehensive, well-written, and trustworthy? This is what the E-E-A-T rubric above measures.

**Needs Met (NM)**: Does the content satisfy the user's actual intent? Would the user need to see additional results, or can they complete their task here? This is a separate question.

### Why They Diverge

- A high-quality medical article that doesn't let users book an appointment has high PQ but may fail NM for transactional intent.
- A mediocre comparison table that exactly answers the user's comparison query may fully meet needs despite lower PQ.
- A beautifully written review that doesn't include pricing fails NM for users who need cost information to make decisions.

### Needs Met Assessment

| Rating | Label | Criteria |
|--------|-------|----------|
| 5 | Fully Meets | User can complete their task with this single result; no additional results needed |
| 4 | Highly Meets | User can mostly complete their task; minor supplementary information may be helpful |
| 3 | Moderately Meets | User gets useful information but needs additional results to fully address their query |
| 2 | Slightly Meets | Minimal useful information; user must consult other results |
| 1 | Fails to Meet | Content does not address the user's intent at all |

### Needs Met Checklist for Blog Articles

- [ ] Does the article address the specific intent behind the target keyword?
- [ ] Can a reader make a decision or take an action after reading this article?
- [ ] Are the key questions a user would have answered within the article?
- [ ] Does the article include actionable next steps?
- [ ] Would a non-SEO user consider this the best result for their query?

## The "Regular User" Quality Test

Would a non-SEO user consider this the best result for their query? If not, E-E-A-T compliance is meaningless.

### The SEO Mind Trap

Cyrus Shepard's concept: SEO professionals evaluate pages through an optimization lens — checking keyword placement, heading structure, internal links. Regular users evaluate pages through a satisfaction lens — did this answer my question? Can I do what I came to do? Is this trustworthy?

A page that passes every SEO checklist but fails the regular user test is a page that will eventually lose to a page that passes the regular user test, regardless of SEO optimization.

### How to Apply the Regular User Test

1. **Read the article as if you know nothing about SEO.** Ignore headings, keyword density, and structural compliance.
2. **Ask: "If I searched for this keyword and found this article, would I be satisfied?"** Would you stay? Would you return to search results looking for something better?
3. **Ask: "Does this article help me do something or decide something?"** Or is it just information for information's sake?
4. **Ask: "Is this the best result I could find for this query?"** If the answer is "probably not," the content needs improvement regardless of its E-E-A-T scores.

## Author Entity Strategy

Google recognizes authors as entities. Lily Ray's analysis demonstrates that content attributed to authors Google can recognize in its Knowledge Graph receives a quality signal advantage over content by unrecognizable or pseudonymous authors.

### What This Means

An "author" is not just a name on a page. Google attempts to resolve author entities across the web. If Google can verify that a specific person wrote the content, has a consistent web presence, and is associated with the topic domain, the content receives a corroboration signal.

### Author Entity Requirements

1. **Discoverable profiles.** The author must have profiles that Google can crawl and associate with the content: LinkedIn, Twitter/X, industry publications, or a personal website.
2. **Topical consistency.** The author's body of work across platforms should be topically consistent with the content they are attributed to. A health article by someone whose web presence is entirely about cooking lacks entity corroboration.
3. **Cross-platform corroboration.** The same author entity should be verifiable across multiple independent sources — not just the publishing site.
4. **Schema markup.** Use `Person` schema and `author` property in `Article` schema to explicitly link content to the author entity. Include the author's URL (sameAs) for entity resolution.

### Author Entity Checklist

- [ ] Author has a verifiable web presence (LinkedIn, personal site, or industry publications)
- [ ] Author's published work is topically consistent with the article
- [ ] Author entity is referenced across multiple independent platforms
- [ ] Article schema includes author name, URL, and sameAs links
- [ ] Author page on the publishing site links to external profiles

## AI Slop Loop Awareness

Lily Ray's concept: AI-generated misinformation can self-reinforce via RAG (Retrieval-Augmented Generation) systems. When AI-generated content is published and indexed, it becomes part of the retrieval corpus that other AI systems draw from. If that content contains inaccuracies, those inaccuracies can be cited and amplified by subsequent AI outputs, creating a self-reinforcing loop.

### How the Loop Works

1. AI-generated content with an unverified claim is published
2. The content is indexed and becomes part of the web corpus
3. Another AI system retrieves this content as a source
4. The AI system cites the unverified claim, giving it the appearance of corroboration
5. The original claim now appears in multiple AI-generated outputs
6. Each output further "validates" the claim through apparent consensus

### How to Break the Loop

- **Verify every factual claim before publication.** Do not publish AI-generated statistics, benchmarks, or study results without independent verification.
- **Distinguish content from AI-generated filler.** Include specific, verifiable details that AI-generated content typically lacks: testing methodology, named sources, conditional scope.
- **Do not rely on AI consensus as verification.** Multiple AI outputs agreeing on a claim does not make the claim true. It may indicate the loop is active.
- **Audit existing content.** Review previously published articles for claims that lack independent verification. Update or remove them.

### AI Slop Loop Red Flags

- Statistics that appear in AI outputs but trace back to no primary source
- Claims that are widely repeated but never attributed to a specific study or organization
- Content that reads as authoritative but contains no specific evidence
- Benchmarks or comparisons where the methodology is unspecified

## Before/After Scoring

Every article receives E-E-A-T scores BEFORE and AFTER optimization:

```
Before: Experience=X/10, Expertise=Y/10, Authoritativeness=Z/10, Trustworthiness=W/10
Target: Experience=8/10, Expertise=7+/10, Authoritativeness=8/10, Trustworthiness=8/10
After:  Experience=X'/10, Expertise=Y'/10, Authoritativeness=Z'/10, Trustworthiness=W'/10
Needs Met: X/5 (separate from E-E-A-T scores)
```

## Improvement Strategies

| Low Score On | Fix Strategy |
|-------------|-------------|
| Experience | Add first-person testing narrative, specific timeline, personal observations |
| Expertise | Add technical specs, numbered steps, industry terminology, troubleshooting |
| Authoritativeness | Add competitor comparison, balanced pros/cons, professional recommendations |
| Trustworthiness | Remove superlatives, add disclosures, cite sources, acknowledge limitations |
| Needs Met | Identify user intent, add actionable next steps, ensure key questions are answered |

## Anti-Patterns to Avoid

1. **Checklist E-E-A-T** — Going through the motions: adding author boxes, About pages, and first-person pronouns without genuine substance behind them. Surface signals without deep corroboration. (Cyrus Shepard: his data shows these don't predict update winners.)

2. **Counting first-person pronouns without genuine experience** — Writing "I tested this" 20 times without describing methodology, observations, or results is worse than no first-person usage at all. It signals performance, not experience.

3. **Surface signals without deep corroboration** — An author box with a photo and bio, but the author has no verifiable web presence, no published work elsewhere, and no recognized expertise. Google can detect this disconnect.

4. **YMYL overapplication to non-harmful queries** — Applying medical-grade E-E-A-T requirements to a review of project management tools. This wastes resources and over-engineers content that doesn't need it. (Lily Ray: E-E-A-T scrutiny scales with harm potential.)

5. **PQ/Needs Met conflation** — Assuming a high-quality page automatically satisfies user intent. Quality and relevance are separate evaluations. A well-written article that doesn't answer the user's question is a well-written failure. (Cyrus Shepard: his rater experience showed these are independent axes.)

6. **Marketing Speak** — "Revolutionary", "game-changing", "best ever" — Use specific facts instead.

7. **Vague Claims** — "High quality" → "verified 99.5% accuracy in benchmark tests"

8. **No Alternatives** — Always mention competing options.

9. **Hidden Affiliation** — Always disclose relationship with the company.

10. **Over-CTA** — More than 3 CTA buttons feels spammy.

11. **Fabricated Evidence** — Never invent quotes, statistics, or testimonials. This is both an E-E-A-T violation and an AI Slop Loop accelerant.