# Blog Templates

8 universal blog templates with different structures, voices, and focuses. Templates are selected based on keyword intent and rotated across articles to prevent similarity.

## Template Selection Logic

1. Analyze the keyword/topic for content type signals
2. Match to the most appropriate template
3. If the same template was used last time, rotate to the next one
4. Override available via `--template` flag

### Signal Detection

| Signal | Template |
|--------|----------|
| "how to", "tutorial", "guide", "step by step" | Problem-Solver |
| "technical", "architecture", "specs" | Analyst |
| "beginner", "introduction", "what is", "getting started" | Beginner's Guide |
| "vs", "compare", "alternative", "versus" | Comparison |
| "case study", "how [x] used" | Case Study |
| "journey", "story", "experience", "honest review" | Storyteller |
| Default | Reviewer |

---

## Template 1: Deep Reviewer (`template_reviewer`)

**Voice**: Professional reviewer — systematic, evidence-based, balanced
**Opening**: Start with a specific testing scenario
**Focus**: Comprehensive evaluation across all dimensions

### H2 Structure
1. What Is [Product/Service] and Why I Started Testing It
2. My Testing Setup and Methodology
3. How to Get Started: Step-by-Step Guide
4. Performance Results: What I Actually Found
5. Honest Pros and Cons After [X] Weeks
6. How It Compares to [Competitor A] and [Competitor B]
7. Technical Specifications and Pricing
8. Common Questions People Ask
9. My Final Verdict: Who Should Use This
10. References

### Unique Elements
- Comparison table with at least 4 competitors
- Testing methodology explanation
- Specific metrics and measurements
- Clear verdict with recommendation

---

## Template 2: Tutorial Expert (`template_tutorial`)

**Voice**: Helpful instructor — clear, practical, encouraging
**Opening**: Start with a relatable problem
**Focus**: Practical how-to with multiple tutorials

### H2 Structure
1. Why [Use Case] Matters in [Year]
2. Getting Started with [Product]: Complete Setup Guide
3. Tutorial 1: [Basic Use Case] — Step by Step
4. Tutorial 2: [Advanced Use Case] — Pro Techniques
5. Tutorial 3: [Creative Use Case] — Pushing the Limits
6. Troubleshooting: Common Issues and Fixes
7. [Product] vs Alternatives: Which Tool Fits Your Workflow
8. Pricing Breakdown: Is It Worth the Cost
9. Common Questions People Ask
10. References

### Unique Elements
- At least 3 numbered tutorials with clear steps
- "Pro Tip" callouts throughout
- "Common Mistakes" or "Troubleshooting" section
- Workflow descriptions

---

## Template 3: Industry Analyst (`template_analyst`)

**Voice**: Industry analyst — authoritative, data-driven, objective
**Opening**: Start with market context
**Focus**: Market positioning and technical depth

### H2 Structure
1. The State of [Industry Category] in [Year]: Market Overview
2. What Makes [Product/Service] Different: Technical Analysis
3. Real-World Applications: Industries Using This Technology
4. Hands-On Analysis: Testing [Product] Across [X] Scenarios
5. Competitive Landscape: [Product] vs [Competitor A] vs [Competitor B]
6. Pricing Analysis: Cost Per Output Compared to Competitors
7. Limitations and Future Roadmap
8. Who Benefits Most: Use Case Breakdown
9. Common Questions People Ask
10. References

### Unique Elements
- Market statistics and industry data
- Competitive positioning analysis
- Pricing comparison table
- Technical architecture explanation

---

## Template 4: Problem Solver (`template_problem_solver`)

**Voice**: Problem-solver — empathetic, solution-focused, results-oriented
**Opening**: Start with a specific pain point
**Focus**: Concrete solutions to real problems

### H2 Structure
1. The Problem: Why [Traditional Approach] No Longer Works
2. Discovering [Product]: My First Impressions
3. Solution 1: How [Product] Solves [Pain Point 1]
4. Solution 2: How [Product] Solves [Pain Point 2]
5. Solution 3: How [Product] Solves [Pain Point 3]
6. Before vs After: Real Results from My Projects
7. How [Product] Stacks Up Against [Competitors]
8. Pricing: Is the Investment Worth It
9. Common Questions People Ask
10. References

### Unique Elements
- Before vs After section with examples
- 3 specific pain points and solutions
- Time/cost savings calculations
- Real project examples or case studies

---

## Template 5: Beginner's Guide (`template_beginners_guide`)

**Voice**: Friendly mentor — approachable, encouraging, clear
**Opening**: Start with reassurance
**Focus**: Progressive learning path

### H2 Structure
1. What Is [Product]? A Beginner's Complete Introduction
2. Who Is [Product] For? (And Who It's Not For)
3. Getting Started: Your First [Output] in 5 Minutes
4. The Essential Features You Need to Know
5. 5 Beginner Mistakes to Avoid
6. Leveling Up: Intermediate Tips and Tricks
7. [Product] vs Other Beginner-Friendly Tools
8. Pricing Guide: Which Plan Is Right for You
9. Common Questions People Ask
10. References

### Unique Elements
- "Who Is This For" with clear audience definition
- "5 Beginner Mistakes to Avoid" section
- Quick-start guide (first result in 5 minutes)
- Leveling up section for intermediate users

---

## Template 6: Storyteller (`template_storyteller`)

**Voice**: Personal narrative — authentic, emotional, relatable
**Opening**: Start with a personal struggle
**Focus**: Journey narrative with real experiences

### H2 Structure
1. The Problem That Changed Everything: My [X]-Month Journey
2. Why I Almost Gave Up on [Category] Tools
3. The Moment I Discovered [Product]: First Impressions
4. My First Week: Honest Reactions and Real Surprises
5. Real Projects I've Completed: What I Actually Made
6. The Results That Surprised Me Most
7. How [Product] Compares to What I Used Before
8. Who Will Love This Tool (And Who Won't)
9. Common Questions People Ask
10. References

### Unique Elements
- Personal journey narrative with specific timeline
- Specific dates, numbers, and personal anecdotes
- "What I Wish I Knew Earlier" section
- Personal recommendation based on audience types

---

## Template 7: Deep Comparison (`template_comparison`)

**Voice**: Objective comparison — fair, data-driven, structured
**Opening**: Start with the core decision
**Focus**: Head-to-head comparison with clear winners

### H2 Structure
1. [Product A] vs [Product B]: The Ultimate [Year] Comparison
2. Quick Verdict: Which Tool Wins for Most Users
3. Feature-by-Feature Breakdown: What Each Tool Offers
4. Output Quality Comparison: Real Examples and Side-by-Side Tests
5. Pricing Comparison: True Cost Analysis of Each Tool
6. Speed and Performance: Head-to-Head Test Results
7. Ease of Use: Learning Curve and Interface Design
8. Use Case Matching: Which Tool Wins for Your Specific Scenario
9. Common Questions People Ask
10. References

### Unique Elements
- Comparison table with 6+ criteria and per-category winners
- Quick Verdict section at the top for skimmers
- Real output examples from both tools
- "Best For" summary boxes for each tool

---

## Template 8: Case Study (`template_case_study`)

**Voice**: Case study — specific, results-focused, credible
**Opening**: Start with the outcome
**Focus**: Concrete results and replication framework

### H2 Structure
1. Case Study: How [User Type] Used [Product] to [Achieve Result]
2. The Challenge: What They Were Trying to Solve
3. Why They Chose [Product] Over Alternatives
4. Implementation: How They Set Up Their Workflow Step by Step
5. Results: Measurable Outcomes After [X] Weeks of Use
6. Key Lessons: What Worked, What Didn't, and What Surprised Them
7. Replicating This Success: A Step-by-Step Framework for You
8. How [Product] Compares for This Use Case
9. Common Questions People Ask
10. References

### Unique Elements
- Specific metrics: time saved, cost reduced, quality improved
- Replication framework with step-by-step instructions
- Before/after workflow comparison
- Key takeaways summary

---

## Reference Format (ALL Templates)

Every reference MUST follow this exact format:

```html
<p>[1] Source Name - "Title" - <a href="URL" target="_blank">URL</a> - Description</p>
```

**Rules**:
- URL must appear TWICE: in `href` attribute AND as visible text
- Only use homepage or well-known stable paths
- Never fabricate article paths
- At least 2-3 references required per article
- Place after FAQ, before final CTA

## FAQ Requirements (ALL Templates)

- At least 6 questions
- Natural conversational format
- Section title: "Common Questions People Ask"
- 50-80 words per answer
- At least 2 questions contain the main keyword
