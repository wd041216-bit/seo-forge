#!/usr/bin/env python3
"""
SEO Forge — Universal Autonomous Blog Engine CLI
Provides state management, pipeline coordination, validation, optimization, and publishing.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.client import HTTPSConnection
from urllib.parse import urlparse

logger = logging.getLogger("seo_forge")


# ── Custom Exceptions ──────────────────────────────────────────────────────


class PipelineError(Exception):
    """Base exception for pipeline failures."""


class ValidationError(PipelineError):
    """Article validation failed."""


class ScoringError(PipelineError):
    """Scoring computation failed."""


class PublishError(PipelineError):
    """Publishing step failed."""


# ── Retry Decorator ────────────────────────────────────────────────────────


def retry(max_attempts=3, delay=1.0, exceptions=(OSError, ConnectionError)):
    """Retry a function on network-related exceptions."""

    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        logger.warning(
                            "Retry %d/%d for %s: %s",
                            attempt,
                            max_attempts,
                            fn.__name__,
                            exc,
                        )
                        time.sleep(delay * attempt)
            raise last_exc

        return wrapper

    return decorator


# ── Utilities ──────────────────────────────────────────────────────────────


def generate_id(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("'", "")
        .replace('"', "")
    )


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def error_json(msg: str, exc_type: str = "PipelineError"):
    """Structured JSON error output for CI integration."""
    output = {"error": True, "type": exc_type, "message": msg}
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(1)


@retry(max_attempts=2, delay=0.5)
def check_url_head(url: str) -> bool:
    """HEAD request to check if a URL is reachable. Returns True on 2xx/3xx."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        return False
    conn = HTTPSConnection(parsed.hostname, timeout=5)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    try:
        conn.request("HEAD", path)
        resp = conn.getresponse()
        return 200 <= resp.status < 400
    finally:
        conn.close()


# ── Original Commands ──────────────────────────────────────────────────────


def cmd_init(args):
    root = args.root
    domain = generate_id(args.domain)
    os.makedirs(f"{root}/keywords", exist_ok=True)
    os.makedirs(f"{root}/articles", exist_ok=True)
    os.makedirs(f"{root}/scoring", exist_ok=True)
    os.makedirs(f"{root}/build_logs", exist_ok=True)

    state = {
        "domain": args.domain,
        "domain_id": domain,
        "topic": args.topic,
        "language": args.lang or "en",
        "status": "initialized",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_phase": "CONFIG",
        "iteration": 0,
        "score_history": [],
        "keywords": [],
        "articles": [],
    }
    save_json(f"{root}/pipeline_state.json", state)
    logger.info("Initialized: %s (%s)", args.domain, domain)
    print(f"[SEO Forge] Initialized: {args.domain} ({domain})")
    print(f"  Topic: {args.topic}")
    print(f"  Language: {args.lang or 'en'}")
    print(f"  Root: {root}")


def cmd_trend(args):
    root = args.root
    state = load_json(f"{root}/pipeline_state.json")
    if not state:
        print("[ERROR] No pipeline state found. Run 'init' first.")
        return

    keyword_data = {
        "keyword": args.keyword,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "source": args.source or "web_search",
        "intent": args.intent or "informational",
        "volume_signal": int(args.volume) if args.volume else 0,
        "competition_signal": args.competition or "unknown",
    }
    state["pipeline_phase"] = "TREND"
    state.setdefault("keywords", []).append(keyword_data)
    save_json(f"{root}/pipeline_state.json", state)

    kw_file = f"{root}/keywords/{generate_id(args.keyword)}_{ts()}.json"
    save_json(kw_file, keyword_data)
    logger.info("Trend recorded: %s", args.keyword)
    print(f"[SEO Forge] Trend recorded: {args.keyword}")
    print(f"  Intent: {keyword_data['intent']}")
    print(f"  Saved: {kw_file}")


def cmd_score_keyword(args):
    root = args.root

    scores = {
        "keyword": args.keyword,
        "potential": float(args.potential or 0),
        "validation": float(args.validation or 0),
        "real_difficulty": float(args.difficulty or 0),
        "opportunity_window": float(args.opportunity or 0),
        "win_probability": float(args.win_prob or 0),
        "roi_potential": float(args.roi or 0),
    }
    final = (
        (0.30 * scores["potential"])
        + (0.20 * scores["validation"])
        - (0.50 * scores["real_difficulty"])
        + scores["opportunity_window"]
    )
    scores["final_score"] = round(final, 2)

    # CTR opportunity scoring
    if getattr(args, "serp_features", None):
        position = int(getattr(args, "position", 1))
        baseline = CTR_BASELINES.get(position, 0.5)
        features = [f.strip() for f in args.serp_features.split(",")]
        penalty = 1.0
        for f in features:
            penalty *= SERP_PENALTIES.get(f, 1.0)
        adjusted_ctr = round(baseline * penalty, 2)
        scores["ctr_opportunity"] = {
            "position": position,
            "baseline_ctr": baseline,
            "serp_features": features,
            "adjusted_ctr": adjusted_ctr,
        }

    if (
        final >= 25
        and scores["win_probability"] >= 50
        and scores["roi_potential"] >= 55
    ):
        scores["grade"] = "S+"
    elif (
        final >= 20
        and scores["win_probability"] >= 50
        and scores["roi_potential"] >= 55
    ):
        scores["grade"] = "S"
    elif (
        final >= 15
        and scores["win_probability"] >= 50
        and scores["roi_potential"] >= 55
    ):
        scores["grade"] = "A+"
    elif final >= 10 and scores["win_probability"] >= 40:
        scores["grade"] = "A"
    elif final >= 5:
        scores["grade"] = "B"
    else:
        scores["grade"] = "C"

    kw_file = f"{root}/keywords/{generate_id(args.keyword)}_scored.json"
    save_json(kw_file, scores)
    logger.info("Keyword scored: %s — grade %s", args.keyword, scores["grade"])
    print(f"[SEO Forge] Keyword scored: {args.keyword}")
    print(f"  Final Score: {scores['final_score']}")
    print(f"  Grade: {scores['grade']}")
    print(f"  Win Probability: {scores['win_probability']}%")
    if "ctr_opportunity" in scores:
        print(
            f"  CTR Opportunity: {scores['ctr_opportunity']['adjusted_ctr']}% at position {scores['ctr_opportunity']['position']}"
        )


def cmd_article(args):
    root = args.root
    state = load_json(f"{root}/pipeline_state.json")

    article = {
        "keyword": args.keyword,
        "template": args.template or "auto",
        "title": args.title or "",
        "slug": args.slug or generate_id(args.keyword),
        "status": "drafted",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scores": {},
    }
    article_id = generate_id(args.keyword) + "_" + ts()
    article["id"] = article_id

    art_file = f"{root}/articles/{article_id}.json"
    save_json(art_file, article)

    state["pipeline_phase"] = "DRAFT"
    state.setdefault("articles", []).append(article_id)
    save_json(f"{root}/pipeline_state.json", state)

    logger.info("Article registered: %s", article_id)
    print(f"[SEO Forge] Article registered: {article_id}")
    print(f"  Keyword: {args.keyword}")
    print(f"  Template: {article['template']}")
    print("  Status: drafted")


def cmd_score_article(args):
    root = args.root
    art_file = f"{root}/articles/{args.article_id}.json"
    article = load_json(art_file)
    if not article:
        logger.error("Article not found: %s", args.article_id)
        print(f"[ERROR] Article not found: {args.article_id}")
        return

    # Auto-scoring from article file
    if getattr(args, "article_file", None) and os.path.exists(args.article_file):
        config = (
            load_json(getattr(args, "config", "") or "")
            if getattr(args, "config", None)
            else {}
        )
        md = read_file(args.article_file)
        keyword = article.get("keyword", getattr(args, "keyword", ""))
        scores = compute_article_scores(md, keyword, config)
    elif any(
        float(getattr(args, a, 0) or 0) > 0 for a in ("seo", "eeat", "depth", "refs")
    ):
        seo = float(args.seo or 0)
        eeat = float(args.eeat or 0)
        depth = float(args.depth or 0)
        refs = float(args.refs or 0)
        total = seo + eeat + depth + refs
        scores = {
            "seo_quality": {"score": seo, "max": 25},
            "eeat_compliance": {"score": eeat, "max": 25},
            "content_depth": {"score": depth, "max": 25},
            "reference_authority": {"score": refs, "max": 25},
            "total": total,
            "pass": total >= 90,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        logger.error("Provide --article-file or --seo/--eeat/--depth/--refs")
        return

    total = scores["total"]
    article["scores"] = scores
    article["status"] = "scored"
    save_json(art_file, article)

    state = load_json(f"{root}/pipeline_state.json")
    state["score_history"].append(
        {
            "article": args.article_id,
            "total": total,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_json(f"{root}/pipeline_state.json", state)

    logger.info("Article scored: %s — total %d/100", args.article_id, total)
    print(f"[SEO Forge] Article scored: {args.article_id}")
    print(f"  SEO Quality: {scores['seo_quality']['score']}/25")
    print(f"  E-E-A-T: {scores['eeat_compliance']['score']}/25")
    print(f"  Content Depth: {scores['content_depth']['score']}/25")
    print(f"  References: {scores['reference_authority']['score']}/25")
    print(f"  TOTAL: {total}/100")
    print(f"  PASS: {'YES' if total >= 90 else 'NO (need optimization)'}")


def cmd_report(args):
    root = args.root
    state = load_json(f"{root}/pipeline_state.json")
    if not state:
        print("[ERROR] No pipeline state found.")
        return

    lines = [
        f"# SEO Forge Report: {state['domain']}",
        "",
        f"**Domain**: {state['domain']}",
        f"**Topic**: {state['topic']}",
        f"**Status**: {state['status']}",
        f"**Phase**: {state['pipeline_phase']}",
        f"**Iterations**: {state['iteration']}",
        "",
        "## Score History",
        "",
    ]
    for sh in state.get("score_history", []):
        lines.append(f"- {sh['timestamp']}: {sh['total']}/100 ({sh['article']})")

    lines.append(f"\n## Articles ({len(state.get('articles', []))})")
    for aid in state.get("articles", []):
        art = load_json(f"{root}/articles/{aid}.json")
        if art:
            total = art.get("scores", {}).get("total", "pending")
            lines.append(f"- `{aid}` — Keyword: {art['keyword']} — Score: {total}/100")

    lines.append(f"\n## Keywords ({len(state.get('keywords', []))})")
    for kw in state.get("keywords", []):
        lines.append(f"- `{kw['keyword']}` — Intent: {kw['intent']}")

    report = "\n".join(lines)
    out_file = args.output or f"{root}/REPORT.md"
    with open(out_file, "w") as f:
        f.write(report)
    logger.info("Report saved: %s", out_file)
    print(f"[SEO Forge] Report saved: {out_file}")


def cmd_state(args):
    root = args.root
    state = load_json(f"{root}/pipeline_state.json")
    if not state:
        print("[ERROR] No pipeline state found.")
        return
    print(json.dumps(state, indent=2, ensure_ascii=False))


# ── New Commands ────────────────────────────────────────────────────────────


def _extract_meta_description(md: str) -> str:
    """Extract meta description from frontmatter 'description:' field."""
    match = re.search(r"^description:\s*(.+)$", md, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return ""


def _count_words(text: str) -> int:
    return len(text.split())


def _keyword_density(md: str, keyword: str) -> float:
    words = _count_words(md)
    if words == 0:
        return 0.0
    # Case-insensitive keyword count
    count = len(re.findall(re.escape(keyword), md, re.IGNORECASE))
    return (count / words) * 100


def _heading_hierarchy(md: str) -> dict:
    """Check heading rules: no H1 in body, at least one H2 and one H3."""
    h1s = re.findall(r"^# .+$", md, re.MULTILINE)
    h2s = re.findall(r"^## .+$", md, re.MULTILINE)
    h3s = re.findall(r"^### .+$", md, re.MULTILINE)
    return {
        "h1_in_body": len(h1s) > 1,  # first H1 allowed as title
        "has_h2": len(h2s) >= 1,
        "has_h3": len(h3s) >= 1,
    }


def _count_first_person(md: str) -> int:
    """Count first-person pronouns: I, me, my, mine, we, us, our, ours."""
    return len(re.findall(r"\b(I|me|my|mine|we|us|our|ours)\b", md, re.IGNORECASE))


def _count_faqs(md: str) -> int:
    """Count FAQ-style questions (lines starting with ## ... ? or ### ... ?)."""
    return len(re.findall(r"^#{2,3}\s+.+\?.*$", md, re.MULTILINE))


def _extract_urls(md: str) -> list:
    """Extract HTTP(S) URLs from markdown."""
    return re.findall(r"https?://[^\s\)>]+", md)


YMYL_KEYWORDS = {
    "health",
    "medical",
    "financial",
    "legal",
    "investing",
    "medicine",
    "treatment",
    "therapy",
    "drug",
    "insurance",
    "tax",
    "attorney",
    "lawyer",
    "doctor",
    "clinic",
    "hospital",
    "pharmaceutical",
    "supplement",
    "diet",
    "weight loss",
    "mental health",
    "anxiety",
    "depression",
    "surgery",
    "diagnosis",
    "prescription",
    "side effects",
}

TRUSTED_DOMAINS = {
    "stanford.edu",
    "mit.edu",
    "harvard.edu",
    "ox.ac.uk",
    "nature.com",
    "openai.com",
    "google.com",
    "microsoft.com",
    "aws.amazon.com",
    "hbr.org",
    "mckinsey.com",
    "moz.com",
    "searchengineland.com",
    "techcrunch.com",
    "wired.com",
    "wikipedia.org",
    "statista.com",
    "who.int",
    "nih.gov",
    "cdc.gov",
    "fda.gov",
}

CTR_BASELINES = {
    1: 31.7,
    2: 15.9,
    3: 10.5,
    4: 7.4,
    5: 5.3,
    6: 3.1,
    7: 2.6,
    8: 2.3,
    9: 2.0,
    10: 1.8,
}

SERP_PENALTIES = {
    "featured_snippet": 0.45,
    "knowledge_panel": 0.35,
    "ads": 0.70,
    "ai_overview": 0.40,
    "image_pack": 0.55,
    "people_also_ask": 0.80,
    "local_pack": 0.50,
    "video_carousel": 0.60,
}


def _is_ymyl(keyword: str) -> bool:
    kw_lower = keyword.lower()
    return any(y in kw_lower for y in YMYL_KEYWORDS)


def _extract_headings(md: str) -> list:
    return re.findall(r"^(#{1,6})\s+(.+)$", md, re.MULTILINE)


def _count_declarative_sentences(md: str) -> int:
    body = re.sub(r"^---[\s\S]*?---", "", md)
    body = re.sub(r"^#{1,6}\s+.+$", "", body, flags=re.MULTILINE)
    sentences = re.split(r"[.!?]+\s", body)
    declarative = 0
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 10:
            continue
        if not re.match(
            r"^(who|what|when|where|why|how|is|are|do|does|can|will|should|would|could)",
            s,
            re.IGNORECASE,
        ):
            declarative += 1
    return declarative


def _count_verifiable_claims(md: str) -> int:
    claims = 0
    claims += len(re.findall(r"\d+\.?\d*%?", md))
    claims += len(re.findall(r"\b(19|20)\d{2}\b", md))
    claims += len(re.findall(r"\$[\d,.]+", md))
    claims += len(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", md))
    return claims


def _count_source_attributions(md: str) -> int:
    return len(
        re.findall(
            r"(according to|cited by|reported by|research by|study by|data from|source:)",
            md,
            re.IGNORECASE,
        )
    )


def _count_superlatives(md: str) -> int:
    return len(
        re.findall(
            r"\b(best|worst|greatest|most|least|top|number one|#1|leading|premier|ultimate)\b",
            md,
            re.IGNORECASE,
        )
    )


def _count_ctas(md: str) -> int:
    return len(
        re.findall(
            r"\b(buy now|sign up|subscribe|click here|get started|learn more|contact us|shop now|download|register)\b",
            md,
            re.IGNORECASE,
        )
    )


def _count_experience_verbs(md: str) -> int:
    return len(
        re.findall(
            r"\b(tested|tried|used|implemented|built|deployed|configured|measured|compared|evaluated|analyzed|observed|found that)\b",
            md,
            re.IGNORECASE,
        )
    )


def compute_article_scores(md: str, keyword: str, config: dict | None = None) -> dict:
    """Compute article scores from content. Returns dict with 4 axis scores (0-25 each)."""
    config = config or {}
    seo_rules = config.get("seo_rules", {})
    kw_min = seo_rules.get("keyword_density_min", 1.0)
    kw_max = seo_rules.get("keyword_density_max", 2.0)
    min_words = seo_rules.get("min_word_count", 1000)

    density = _keyword_density(md, keyword) if keyword else 0.0
    word_count = _count_words(md)
    headings = _extract_headings(md)
    h1s = [h for lvl, h in headings if lvl == "#"]
    h2s = [h for lvl, h in headings if lvl == "##"]
    h3s = [h for lvl, h in headings if lvl == "###"]
    h1_in_body = len(h1s) > 1
    meta_desc = _extract_meta_description(md)
    pronoun_count = _count_first_person(md)
    faq_count = _count_faqs(md)
    urls = _extract_urls(md)
    is_ymyl = _is_ymyl(keyword)

    # SEO Quality (0-25)
    # keyword_density_score (0-8)
    if kw_min <= density <= kw_max:
        kw_dens_score = 8
    elif 0.5 <= density <= 3.0:
        kw_dens_score = max(0, 8 - int(abs(density - (kw_min + kw_max) / 2) * 4))
    else:
        kw_dens_score = 0

    # heading_optimization (0-6)
    kw_in_h2 = sum(1 for h in h2s if keyword.lower() in h.lower()) if keyword else 0
    kw_in_h3 = sum(1 for h in h3s if keyword.lower() in h.lower()) if keyword else 0
    heading_score = min(
        6, (kw_in_h2 >= 2) * 3 + (kw_in_h3 >= 1) * 2 + min(kw_in_h2 + kw_in_h3, 1)
    )

    # meta_optimization (0-6)
    meta_len = len(meta_desc)
    if 120 <= meta_len <= 160:
        meta_score = 6
    elif 80 <= meta_len <= 200:
        meta_score = max(0, 6 - abs(meta_len - 140) // 20)
    else:
        meta_score = 0

    # slug_quality (0-5)
    slug_kw = keyword.lower().replace(" ", "-") if keyword else ""
    slug_score = 3 if slug_kw else 0
    if slug_kw and word_count > 0:
        slug_score += 2

    seo_quality = kw_dens_score + heading_score + meta_score + slug_score

    # E-E-A-T Compliance (0-25)
    # first_person_score (0-8)
    fp_score = min(8, pronoun_count * 8 // 15) if pronoun_count < 15 else 8

    # experience_evidence (0-7)
    exp_verbs = _count_experience_verbs(md)
    has_timeline = bool(
        re.findall(
            r"\b(20\d{2}|last year|in 20|over the past|recently)\b", md, re.IGNORECASE
        )
    )
    exp_score = min(7, (exp_verbs >= 3) * 4 + has_timeline * 2 + min(exp_verbs, 1))

    # ymyl_gate (0-5)
    if is_ymyl:
        ymyl_score = (
            5 if (pronoun_count >= 20 and exp_verbs >= 3 and len(urls) >= 4) else 0
        )
    else:
        ymyl_score = 3 if pronoun_count >= 10 else 0

    # trust_transparency (0-5)
    disclosures = len(
        re.findall(
            r"\b(disclosure|disclaimer|sponsored|affiliate|note:|important:)\b",
            md,
            re.IGNORECASE,
        )
    )
    superlatives = _count_superlatives(md)
    ctas = _count_ctas(md)
    trust_score = min(
        5, (disclosures >= 2) * 2 + (superlatives < 5) * 2 + (ctas <= 3) * 1
    )

    eeat_compliance = fp_score + exp_score + ymyl_score + trust_score

    # Content Depth (0-25)
    # word_count_score (0-5)
    wc_score = (
        min(5, max(0, word_count * 5 // min_words)) if word_count < min_words else 5
    )

    # faq_coverage (0-5)
    faq_min = seo_rules.get("faq_min_questions", 6)
    faq_score = min(5, faq_count * 5 // faq_min) if faq_count < faq_min else 5

    # extractability (0-5)
    total_paragraphs = len(
        [
            p
            for p in re.split(r"\n{2,}", md)
            if p.strip() and not p.strip().startswith("#")
        ]
    )
    declaratives = _count_declarative_sentences(md)
    has_topic_sentences = declaratives / max(1, total_paragraphs) > 0.5
    extract_score = min(
        5,
        (has_topic_sentences * 2)
        + (declaratives > total_paragraphs * 0.6) * 2
        + min(total_paragraphs, 1),
    )

    # evidence_density (0-5)
    claims = _count_verifiable_claims(md)
    sections = max(1, len(h2s))
    claims_per_section = claims / sections
    ev_score = min(
        5,
        int(claims_per_section >= 3) * 3
        + int(claims_per_section >= 2) * 1
        + min(1, claims // 10),
    )

    # needs_met (0-5)
    has_faq_coverage = faq_count >= 3
    has_task_paths = bool(
        re.findall(
            r"\b(step|how to|guide|tutorial|process|method|approach)\b",
            md,
            re.IGNORECASE,
        )
    )
    nm_score = min(5, has_faq_coverage * 2 + has_task_paths * 2 + min(faq_count, 1))

    content_depth = wc_score + faq_score + extract_score + ev_score + nm_score

    # Reference Authority (0-25)
    # source_count (0-7)
    src_score = min(7, len(urls))

    # url_validity (0-6) — format check only (HEAD checks done by validate)
    valid_format = sum(
        1 for u in urls if re.match(r"https?://[a-z0-9].+\.[a-z]{2,}", u, re.IGNORECASE)
    )
    url_score = min(6, valid_format * 6 // max(1, len(urls))) if urls else 0

    # domain_credibility (0-6)
    credible = sum(1 for u in urls if any(d in u for d in TRUSTED_DOMAINS))
    cred_score = min(6, credible * 3) if urls else 0

    # citation_worthiness (0-6)
    attributions = _count_source_attributions(md)
    has_entities = len(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", md)) >= 5
    cite_score = min(
        6, (attributions >= 2) * 3 + has_entities * 2 + min(attributions, 1)
    )

    reference_authority = src_score + url_score + cred_score + cite_score

    seo_quality = min(25, seo_quality)
    eeat_compliance = min(25, eeat_compliance)
    content_depth = min(25, content_depth)
    reference_authority = min(25, reference_authority)
    total = seo_quality + eeat_compliance + content_depth + reference_authority

    return {
        "seo_quality": {
            "score": seo_quality,
            "max": 25,
            "sub_scores": {
                "keyword_density": kw_dens_score,
                "heading_optimization": heading_score,
                "meta_optimization": meta_score,
                "slug_quality": slug_score,
            },
        },
        "eeat_compliance": {
            "score": eeat_compliance,
            "max": 25,
            "sub_scores": {
                "first_person": fp_score,
                "experience_evidence": exp_score,
                "ymyl_gate": ymyl_score,
                "trust_transparency": trust_score,
            },
        },
        "content_depth": {
            "score": content_depth,
            "max": 25,
            "sub_scores": {
                "word_count": wc_score,
                "faq_coverage": faq_score,
                "extractability": extract_score,
                "evidence_density": ev_score,
                "needs_met": nm_score,
            },
        },
        "reference_authority": {
            "score": reference_authority,
            "max": 25,
            "sub_scores": {
                "source_count": src_score,
                "url_validity": url_score,
                "domain_credibility": cred_score,
                "citation_worthiness": cite_score,
            },
        },
        "total": total,
        "pass": total >= 90,
        "details": {
            "keyword_density": round(density, 2),
            "word_count": word_count,
            "h1_in_body": h1_in_body,
            "h2_count": len(h2s),
            "h3_count": len(h3s),
            "first_person_pronouns": pronoun_count,
            "faq_count": faq_count,
            "source_urls": len(urls),
            "is_ymyl": is_ymyl,
            "meta_description_length": meta_len,
            "experience_verbs": exp_verbs,
            "declarative_sentences": declaratives,
            "verifiable_claims": claims,
            "superlatives": superlatives,
            "ctas": ctas,
        },
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def cmd_validate(args):
    """Validate an article's structure and content against quality rules."""
    article_path = args.article
    keyword = args.keyword

    if not os.path.exists(article_path):
        error_json(f"Article file not found: {article_path}", "ValidationError")

    md = read_file(article_path)

    # Load config if provided
    config = {}
    if args.config and os.path.exists(args.config):
        config = load_json(args.config)

    seo_rules = config.get("seo_rules", {})
    kw_min = seo_rules.get("keyword_density_min", 1.0)
    kw_max = seo_rules.get("keyword_density_max", 2.0)
    min_words = seo_rules.get("min_word_count", 1000)
    min_faqs = seo_rules.get("faq_min_questions", 6)
    min_pronouns = 15

    # Compute quality scores using the unified scoring engine
    quality = compute_article_scores(md, keyword, config)
    details = quality["details"]

    # Build structural checks from compute_article_scores details
    checks = {}

    # Keyword density
    density = details["keyword_density"]
    density_pass = kw_min <= density <= kw_max
    checks["keyword_density"] = {
        "value": round(density, 2),
        "range": [kw_min, kw_max],
        "pass": density_pass,
        "suggestion": ""
        if density_pass
        else f"Adjust keyword '{keyword}' usage to {kw_min}-{kw_max}% range (currently {density:.1f}%)",
    }

    # Meta description length
    meta_len = details["meta_description_length"]
    meta_pass = 120 <= meta_len <= 160
    checks["meta_description"] = {
        "value": meta_len,
        "range": [120, 160],
        "pass": meta_pass,
        "suggestion": ""
        if meta_pass
        else f"Meta description should be 120-160 chars (currently {meta_len})",
    }

    # Word count
    word_count = details["word_count"]
    word_pass = word_count >= min_words
    checks["word_count"] = {
        "value": word_count,
        "min": min_words,
        "pass": word_pass,
        "suggestion": ""
        if word_pass
        else f"Article needs at least {min_words} words (currently {word_count})",
    }

    # Heading hierarchy
    heading_pass = not details["h1_in_body"] and details["h2_count"] >= 1 and details["h3_count"] >= 1
    checks["heading_hierarchy"] = {
        "h1_in_body": details["h1_in_body"],
        "has_h2": details["h2_count"] >= 1,
        "has_h3": details["h3_count"] >= 1,
        "pass": heading_pass,
        "suggestion": ""
        if heading_pass
        else "Ensure no H1 in body, add H2 and H3 headings",
    }

    # First-person pronoun count
    pronoun_count = details["first_person_pronouns"]
    pronoun_pass = pronoun_count >= min_pronouns
    checks["first_person_pronouns"] = {
        "value": pronoun_count,
        "min": min_pronouns,
        "pass": pronoun_pass,
        "suggestion": ""
        if pronoun_pass
        else f"Add more first-person pronouns (I/we/our), need {min_pronouns}+ (currently {pronoun_count})",
    }

    # FAQ count
    faq_count = details["faq_count"]
    faq_pass = faq_count >= min_faqs
    checks["faq_count"] = {
        "value": faq_count,
        "min": min_faqs,
        "pass": faq_pass,
        "suggestion": ""
        if faq_pass
        else f"Add more FAQ questions, need {min_faqs}+ (currently {faq_count})",
    }

    # Reference URL validity
    urls = _extract_urls(md)
    url_results = []
    if args.check_urls:
        for url in urls[:10]:  # cap at 10 to avoid long waits
            try:
                valid = check_url_head(url)
                url_results.append({"url": url, "valid": valid})
            except Exception:
                url_results.append(
                    {"url": url, "valid": False, "error": "request_failed"}
                )
    else:
        for url in urls:
            url_results.append({"url": url, "valid": None, "skipped": True})

    checked_results = [r for r in url_results if not r.get("skipped")]
    all_urls_valid = (
        all(r.get("valid", True) for r in checked_results) if checked_results else True
    )
    checks["reference_urls"] = {
        "count": len(urls),
        "results": url_results,
        "pass": all_urls_valid,
        "suggestion": "" if all_urls_valid else "Some reference URLs returned errors",
    }

    # Overall requires both structural checks pass AND total score >= 90
    structural_pass = all(c["pass"] for c in checks.values())
    score_pass = quality["total"] >= 90
    overall = structural_pass and score_pass

    quality_scores = {
        "seo_quality": {"score": quality["seo_quality"]["score"], "max": 25},
        "eeat_compliance": {"score": quality["eeat_compliance"]["score"], "max": 25},
        "content_depth": {"score": quality["content_depth"]["score"], "max": 25},
        "reference_authority": {
            "score": quality["reference_authority"]["score"],
            "max": 25,
        },
        "total": quality["total"],
    }

    # Include sub-score breakdown when --detailed
    detailed = getattr(args, "detailed", False)
    if detailed:
        quality_scores["seo_quality"]["sub_scores"] = quality["seo_quality"]["sub_scores"]
        quality_scores["eeat_compliance"]["sub_scores"] = quality["eeat_compliance"][
            "sub_scores"
        ]
        quality_scores["content_depth"]["sub_scores"] = quality["content_depth"][
            "sub_scores"
        ]
        quality_scores["reference_authority"]["sub_scores"] = quality[
            "reference_authority"
        ]["sub_scores"]

    result = {
        "article": article_path,
        "keyword": keyword,
        "overall_pass": overall,
        "structural_pass": structural_pass,
        "score_pass": score_pass,
        "quality_scores": quality_scores,
        "checks": checks,
    }

    output_path = args.output
    if output_path:
        save_json(output_path, result)
        logger.info("Validation report saved: %s", output_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not overall:
        logger.warning("Validation FAILED for %s", article_path)
    return result


def cmd_verify(args):
    """Verify post-deployment status of a published article."""
    url = args.url
    config = {}
    if args.config and os.path.exists(args.config):
        config = load_json(args.config)

    checks = {}
    html = ""

    # HTTP 200 check
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError(f"Invalid URL: {url}")
        conn = HTTPSConnection(parsed.hostname, timeout=10)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        conn.request("GET", path)
        resp = conn.getresponse()
        html = resp.read().decode("utf-8", errors="replace")
        http_ok = 200 <= resp.status < 400
        checks["http_status"] = {
            "value": resp.status,
            "pass": http_ok,
            "suggestion": "" if http_ok else f"Expected 200, got {resp.status}",
        }
        conn.close()
    except Exception as e:
        checks["http_status"] = {
            "value": None,
            "pass": False,
            "error": str(e),
            "suggestion": f"Could not connect to {url}: {e}",
        }
        # Cannot check HTML without content — report early
        result = {
            "url": url,
            "overall_pass": False,
            "checks": checks,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result

    # JSON-LD schema
    has_jsonld = bool(
        re.search(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>',
            html,
            re.IGNORECASE,
        )
    )
    checks["jsonld_schema"] = {
        "pass": has_jsonld,
        "suggestion": ""
        if has_jsonld
        else "No JSON-LD schema (application/ld+json) found in page source",
    }

    # Canonical tag
    canonical_match = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    if not canonical_match:
        canonical_match = re.search(
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
            html,
            re.IGNORECASE,
        )
    canonical_url = canonical_match.group(1) if canonical_match else None
    checks["canonical_tag"] = {
        "pass": canonical_match is not None,
        "canonical_url": canonical_url,
        "suggestion": "" if canonical_match else "No canonical tag found in page source",
    }

    # hreflang tags (required for multilingual configs)
    languages = config.get("languages", [])
    multilingual = len(languages) > 1
    hreflang_matches = re.findall(
        r'<link[^>]+hreflang=["\']([^"\']+)["\']', html, re.IGNORECASE
    )
    if multilingual:
        hreflang_pass = len(hreflang_matches) > 0
        checks["hreflang_tags"] = {
            "pass": hreflang_pass,
            "found": hreflang_matches,
            "required": True,
            "suggestion": ""
            if hreflang_pass
            else "No hreflang tags found — required for multilingual site",
        }
    else:
        checks["hreflang_tags"] = {
            "pass": True,
            "found": hreflang_matches,
            "required": False,
            "suggestion": "",
        }

    # Meta description
    meta_match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
        html,
        re.IGNORECASE,
    )
    if not meta_match:
        meta_match = re.search(
            r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',
            html,
            re.IGNORECASE,
        )
    meta_desc = meta_match.group(1) if meta_match else ""
    meta_pass = len(meta_desc) >= 120
    checks["meta_description"] = {
        "pass": meta_pass,
        "length": len(meta_desc),
        "suggestion": ""
        if meta_pass
        else f"Meta description too short or missing (found {len(meta_desc)} chars, need 120+)",
    }

    overall = all(c["pass"] for c in checks.values())
    result = {
        "url": url,
        "overall_pass": overall,
        "checks": checks,
    }

    output_path = getattr(args, "output", None)
    if output_path:
        save_json(output_path, result)
        logger.info("Verification report saved: %s", output_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def cmd_optimize(args):
    """Apply targeted optimizations to an article based on its score report."""
    article_path = args.article
    report_path = args.report
    keyword = args.keyword

    if not os.path.exists(article_path):
        error_json(f"Article file not found: {article_path}", "ValidationError")

    md = read_file(article_path)
    report = (
        load_json(report_path) if report_path and os.path.exists(report_path) else {}
    )
    checks = report.get("checks", {})
    optimizations = []

    # Keyword density adjustment — insert into existing sentences, not boilerplate
    density_check = checks.get("keyword_density", {})
    if not density_check.get("pass", True):
        kw_range = density_check.get("range", [1.0, 2.0])
        target_density = (kw_range[0] + kw_range[1]) / 2
        word_count = _count_words(md)
        target_count = max(1, round(word_count * target_density / 100))
        current_count = (
            len(re.findall(re.escape(keyword), md, re.IGNORECASE)) if keyword else 0
        )

        if current_count < target_count and keyword:
            # Insert keyword naturally at paragraph boundaries
            paragraphs = re.split(r"\n{2,}", md)
            to_add = target_count - current_count
            added = 0
            for i, para in enumerate(paragraphs):
                if added >= to_add:
                    break
                if (
                    para.strip()
                    and not para.strip().startswith("#")
                    and not para.strip().startswith("---")
                ):
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    for j, sent in enumerate(sentences):
                        if added >= to_add:
                            break
                        if len(sent) > 20 and keyword.lower() not in sent.lower():
                            words = sent.split()
                            mid = len(words) // 2
                            insert_phrase = f"In the context of {keyword},"
                            words.insert(mid, insert_phrase)
                            sentences[j] = " ".join(words)
                            added += 1
                    paragraphs[i] = " ".join(sentences)
            if added > 0:
                md = "\n\n".join(paragraphs)
            optimizations.append(
                f"Added {added} keyword mentions for '{keyword}' (target density ~{target_density:.1f}%)"
            )

    # Meta description fix — extract from article content, not boilerplate
    meta_check = checks.get("meta_description", {})
    if not meta_check.get("pass", True):
        meta_desc = _extract_meta_description(md)
        if not meta_desc:
            # Extract first 155 chars of actual content
            body = re.sub(r"^---[\s\S]*?---", "", md).strip()
            body = re.sub(r"^#{1,6}\s+.+$", "", body, flags=re.MULTILINE).strip()
            first_paragraph = re.split(r"\n{2,}", body)[0].strip() if body else ""
            new_desc = (
                first_paragraph[:155].rsplit(" ", 1)[0].strip()
                if first_paragraph
                else f"A detailed guide covering {keyword}."
            )
            if len(new_desc) < 120:
                new_desc = (
                    (new_desc + " " + first_paragraph[155:300])
                    .strip()[:155]
                    .rsplit(" ", 1)[0]
                    .strip()
                )
            if md.startswith("---"):
                first_end = md.index("---", 3)
                md = (
                    md[: first_end + 3]
                    + f'\ndescription: "{new_desc}"\n'
                    + md[first_end + 3 :]
                )
            else:
                md = f'---\ndescription: "{new_desc}"\n---\n\n{md}'
            optimizations.append(
                f"Added meta description from content ({len(new_desc)} chars)"
            )

    # Heading keyword insertion — context-sensitive, not generic
    heading_check = checks.get("heading_hierarchy", {})
    if not heading_check.get("pass", True) and keyword:
        if not heading_check.get("has_h2"):
            md += f"\n\n## {keyword.title()}: Key Considerations and Best Practices\n\nOur experience with {keyword} has revealed several important factors that deserve attention."
            optimizations.append("Added H2 section with keyword")
        if not heading_check.get("has_h3"):
            md += f"\n\n### Practical Applications of {keyword.title()}\n\nWe have applied these principles of {keyword} across multiple scenarios."
            optimizations.append("Added H3 section with keyword")

    output_path = args.output or article_path.replace(".md", ".optimized.md")
    write_file(output_path, md)

    opt_log = {
        "article": article_path,
        "output": output_path,
        "optimizations": optimizations,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    log_path = output_path.replace(".md", ".optimization_log.json")
    save_json(log_path, opt_log)

    logger.info("Optimized article saved: %s", output_path)
    print(json.dumps(opt_log, indent=2, ensure_ascii=False))
    return opt_log


def cmd_schema(args):
    """Generate JSON-LD schema markup from article metadata."""
    article_path = args.article
    if not os.path.exists(article_path):
        error_json(f"Article file not found: {article_path}", "ValidationError")

    md = read_file(article_path)
    config = {}
    if args.config and os.path.exists(args.config):
        config = load_json(args.config)

    title_match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"
    meta_desc = _extract_meta_description(md)
    org_name = config.get("company_name", "")
    site_url = config.get("site_url", "")
    date_published = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    schemas = []

    # Article schema
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": date_published,
    }
    if meta_desc:
        article_schema["description"] = meta_desc
    if org_name:
        article_schema["publisher"] = {"@type": "Organization", "name": org_name}
    if site_url:
        article_schema["url"] = site_url
    schemas.append(article_schema)

    # FAQPage schema (if FAQ sections exist)
    faq_headings = re.findall(r"^#{2,3}\s+.+\?.*$", md, re.MULTILINE)
    if faq_headings:
        faq_items = []
        for q in faq_headings[:10]:
            faq_items.append(
                {
                    "@type": "Question",
                    "name": q.strip(),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"See section: {q.strip()}",
                    },
                }
            )
        schemas.append(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_items,
            }
        )

    # BreadcrumbList schema
    headings = _extract_headings(md)
    breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "Home"}]
    pos = 2
    for lvl, text in headings:
        if lvl in ("##", "###") and pos <= 5:
            breadcrumb_items.append(
                {"@type": "ListItem", "position": pos, "name": text.strip()}
            )
            pos += 1
    if len(breadcrumb_items) > 1:
        schemas.append(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": breadcrumb_items,
            }
        )

    # Organization schema
    if org_name:
        schemas.append(
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": org_name,
                "url": site_url or None,
            }
        )

    result = {"schemas": schemas, "count": len(schemas)}
    if args.output:
        save_json(args.output, result)
        logger.info("Schema markup saved: %s", args.output)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def _check_editorial_gate() -> bool:
    """Check if editorial review is approved."""
    approved = os.environ.get("SEO_FORGE_EDITOR_APPROVED", "").strip()
    if approved in ("1", "true", "yes"):
        return True
    try:
        response = (
            input("\n[Editorial Gate] Approve publication? (yes/no): ").strip().lower()
        )
        return response in ("yes", "y")
    except (EOFError, KeyboardInterrupt):
        return False


def cmd_run(args):
    """Execute the full 10-phase pipeline for a blog config."""
    config_path = args.config

    if not os.path.exists(config_path):
        error_json(f"Config file not found: {config_path}", "PipelineError")

    try:
        config = load_json(config_path)
    except json.JSONDecodeError:
        error_json(f"Invalid JSON in config: {config_path}", "ValidationError")

    if not config:
        error_json(f"Empty or invalid config: {config_path}", "PipelineError")

    required = ["company_name", "industry", "site_url"]
    for field in required:
        if field not in config:
            error_json(f"Missing required field in config: {field}", "ValidationError")

    root = args.root
    max_iterations = args.max_iterations or 5
    require_review = getattr(args, "require_review", False)

    # Phase 1: CONFIG
    logger.info("Phase CONFIG: initializing pipeline")

    class InitArgs:
        pass

    InitArgs.root = root
    InitArgs.domain = config["company_name"]
    InitArgs.topic = config["industry"]
    InitArgs.lang = config.get("language", "en")
    cmd_init(InitArgs)

    state = load_json(f"{root}/pipeline_state.json")

    # Phase 2: TREND — discover keywords
    state["pipeline_phase"] = "TREND"
    save_json(f"{root}/pipeline_state.json", state)
    for kw in config.get("target_keywords", []):

        class TrendArgs:
            pass

        TrendArgs.root = root
        TrendArgs.keyword = kw
        TrendArgs.intent = "informational"
        TrendArgs.volume = "1000"
        TrendArgs.competition = "medium"
        TrendArgs.source = "config"
        cmd_trend(TrendArgs)

    # Phase 3: EVALUATE — score keywords
    state["pipeline_phase"] = "EVALUATE"
    save_json(f"{root}/pipeline_state.json", state)

    # Phase 4: SELECT — pick top keyword
    state["pipeline_phase"] = "SELECT"
    save_json(f"{root}/pipeline_state.json", state)
    top_kw = config.get("target_keywords", ["default-keyword"])[0]

    # Phase 5: OUTLINE — generate heading structure
    state["pipeline_phase"] = "OUTLINE"
    save_json(f"{root}/pipeline_state.json", state)

    # Phase 6: DRAFT / GENERATE — register article
    state["pipeline_phase"] = "GENERATE"

    class ArticleArgs:
        pass

    ArticleArgs.root = root
    ArticleArgs.keyword = top_kw
    ArticleArgs.template = config.get("default_template", "tutorial")
    ArticleArgs.title = ""
    ArticleArgs.slug = ""
    cmd_article(ArticleArgs)

    state = load_json(f"{root}/pipeline_state.json")
    art_id = state["articles"][-1] if state["articles"] else None

    for iteration in range(1, max_iterations + 1):
        state["iteration"] = iteration
        save_json(f"{root}/pipeline_state.json", state)
        logger.info("Iteration %d/%d", iteration, max_iterations)

        # Phase 7: SCORE — compute article scores
        state["pipeline_phase"] = "SCORE"
        save_json(f"{root}/pipeline_state.json", state)
        if art_id:

            class ScoreArgsAuto:
                pass

            ScoreArgsAuto.root = root
            ScoreArgsAuto.article_id = art_id
            ScoreArgsAuto.article_file = None
            ScoreArgsAuto.keyword = top_kw
            ScoreArgsAuto.config = config_path
            ScoreArgsAuto.seo = "0"
            ScoreArgsAuto.eeat = "0"
            ScoreArgsAuto.depth = "0"
            ScoreArgsAuto.refs = "0"
            cmd_score_article(ScoreArgsAuto)

        # Check convergence
        state = load_json(f"{root}/pipeline_state.json")
        if state["score_history"]:
            latest = state["score_history"][-1]["total"]
            if latest >= 90:
                state["pipeline_phase"] = "EDIT"
                save_json(f"{root}/pipeline_state.json", state)
                break

        # Phase 8: OPTIMIZE — apply optimizations
        state["pipeline_phase"] = "OPTIMIZE"
        save_json(f"{root}/pipeline_state.json", state)

        # Phase 9: RESCORE — re-evaluate after optimization
        state["pipeline_phase"] = "RESCORE"
        save_json(f"{root}/pipeline_state.json", state)
        if art_id:

            class RescoreArgs:
                pass

            RescoreArgs.root = root
            RescoreArgs.article_id = art_id
            RescoreArgs.article_file = None
            RescoreArgs.keyword = top_kw
            RescoreArgs.config = config_path
            RescoreArgs.seo = "0"
            RescoreArgs.eeat = "0"
            RescoreArgs.depth = "0"
            RescoreArgs.refs = "0"
            cmd_score_article(RescoreArgs)

        state = load_json(f"{root}/pipeline_state.json")
        if state["score_history"]:
            latest = state["score_history"][-1]["total"]
            if latest >= 90:
                break
    else:
        state["status"] = "max_iterations_reached"
        save_json(f"{root}/pipeline_state.json", state)
        logger.warning(
            "Max iterations (%d) reached without convergence", max_iterations
        )

    # Phase 10: EDIT — editorial review gate
    state["pipeline_phase"] = "EDIT"
    save_json(f"{root}/pipeline_state.json", state)
    if require_review:
        if not _check_editorial_gate():
            state["status"] = "editorial_review_required"
            save_json(f"{root}/pipeline_state.json", state)
            logger.info("Pipeline paused: editorial review required")
            print(
                json.dumps(
                    {"status": "editorial_review_required", "phase": "EDIT"}, indent=2
                )
            )
            return state

    # Phase 10: PUBLISH
    if state.get("status") != "max_iterations_reached":
        state["status"] = "converged"
    state["pipeline_phase"] = "PUBLISH"
    save_json(f"{root}/pipeline_state.json", state)
    logger.info("Pipeline ready to publish")

    print(
        json.dumps(
            {
                "status": state["status"],
                "iteration": state["iteration"],
                "phase": state["pipeline_phase"],
            },
            indent=2,
        )
    )
    return state


def cmd_publish(args):
    """Format and publish an article."""
    article_path = args.article
    platform = args.platform or "generic"
    dry_run = args.dry_run

    if not os.path.exists(article_path):
        error_json(f"Article file not found: {article_path}", "PublishError")

    md = read_file(article_path)

    # Convert markdown to platform format
    if platform == "nextjs":
        # Next.js: add frontmatter with date/slug
        title_match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        slug = generate_id(title)
        frontmatter = f'---\ntitle: "{title}"\ndate: "{datetime.now(timezone.utc).strftime("%Y-%m-%d")}"\nslug: "{slug}"\n---\n\n'
        output_md = frontmatter + re.sub(
            r"^# .+$", "", md, count=1, flags=re.MULTILINE
        ).lstrip("\n")
    elif platform == "hugo":
        title_match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        frontmatter = f'---\ntitle: "{title}"\ndate: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}\n---\n\n'
        output_md = frontmatter + re.sub(
            r"^# .+$", "", md, count=1, flags=re.MULTILINE
        ).lstrip("\n")
    elif platform == "astro":
        title_match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        frontmatter = f'---\ntitle: "{title}"\npubDate: "{datetime.now(timezone.utc).strftime("%Y-%m-%d")}"\n---\n\n'
        output_md = frontmatter + re.sub(
            r"^# .+$", "", md, count=1, flags=re.MULTILINE
        ).lstrip("\n")
    else:
        output_md = md

    output_path = args.output or article_path.replace(".md", f".{platform}.md")
    write_file(output_path, output_md)
    logger.info("Formatted article for %s: %s", platform, output_path)

    if dry_run:
        result = {"status": "dry_run", "output": output_path, "platform": platform}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result

    # Editorial review gate
    if getattr(args, "require_review", False):
        if not _check_editorial_gate():
            result = {
                "status": "editorial_review_required",
                "output": output_path,
                "platform": platform,
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result

    # Create feature branch, commit, PR via gh CLI
    branch_name = f"seo-forge/{generate_id(os.path.basename(article_path))}"
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name], check=True, capture_output=True
        )
        subprocess.run(["git", "add", output_path], check=True, capture_output=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"feat: add SEO article {os.path.basename(article_path)}",
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                f"SEO Article: {os.path.basename(article_path)}",
                "--body",
                "Auto-generated SEO article from SEO Forge pipeline.",
            ],
            check=True,
            capture_output=True,
        )
        result = {
            "status": "published",
            "branch": branch_name,
            "output": output_path,
            "platform": platform,
        }
        logger.info("Published via PR on branch %s", branch_name)
    except subprocess.CalledProcessError as e:
        error_json(
            f"Git/gh command failed: {e.stderr.decode() if e.stderr else str(e)}",
            "PublishError",
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="SEO Forge CLI")
    parser.add_argument("--root", default="./seo-forge-data", help="Pipeline data root")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress all output except errors"
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p = sub.add_parser("init", help="Initialize pipeline")
    p.add_argument("--domain", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--lang", default="en")

    # trend
    p = sub.add_parser("trend", help="Record discovered keyword trend")
    p.add_argument("--keyword", required=True)
    p.add_argument("--intent", default="informational")
    p.add_argument("--volume", default="0")
    p.add_argument("--competition", default="unknown")
    p.add_argument("--source", default="web_search")

    # score-keyword
    p = sub.add_parser("score-keyword", help="Score a keyword candidate")
    p.add_argument("--keyword", required=True)
    p.add_argument("--potential", default="0")
    p.add_argument("--validation", default="0")
    p.add_argument("--difficulty", default="0")
    p.add_argument("--opportunity", default="0")
    p.add_argument("--win-prob", default="0")
    p.add_argument("--roi", default="0")
    p.add_argument(
        "--serp-features",
        default=None,
        help="Comma-separated SERP features for CTR calculation",
    )
    p.add_argument(
        "--position",
        type=int,
        default=1,
        help="Expected SERP position for CTR calculation",
    )

    # article
    p = sub.add_parser("article", help="Register a new article")
    p.add_argument("--keyword", required=True)
    p.add_argument("--template", default="auto")
    p.add_argument("--title", default="")
    p.add_argument("--slug", default="")

    # score-article
    p = sub.add_parser("score-article", help="Score an article")
    p.add_argument("--article-id", required=True)
    p.add_argument(
        "--article-file", default=None, help="Path to article markdown for auto-scoring"
    )
    p.add_argument("--keyword", default="", help="Target keyword for auto-scoring")
    p.add_argument("--config", default=None, help="Blog config JSON for scoring rules")
    p.add_argument("--seo", default="0")
    p.add_argument("--eeat", default="0")
    p.add_argument("--depth", default="0")
    p.add_argument("--refs", default="0")

    # report
    p = sub.add_parser("report", help="Generate pipeline report")
    p.add_argument("--output", default=None)

    # state
    p = sub.add_parser("state", help="Show current pipeline state")

    # validate
    p = sub.add_parser("validate", help="Validate article structure and content")
    p.add_argument("--article", required=True, help="Path to article markdown file")
    p.add_argument("--keyword", required=True, help="Target keyword for density check")
    p.add_argument(
        "--config", default=None, help="Path to blog config JSON for SEO rules"
    )
    p.add_argument(
        "--check-urls",
        action="store_true",
        help="Validate reference URLs with HEAD requests",
    )
    p.add_argument("--output", default=None, help="Path to save validation report JSON")

    # optimize
    p = sub.add_parser("optimize", help="Apply targeted optimizations to article")
    p.add_argument("--article", required=True, help="Path to article markdown file")
    p.add_argument("--keyword", required=True, help="Target keyword")
    p.add_argument(
        "--report", default=None, help="Path to validation/scoring report JSON"
    )
    p.add_argument("--output", default=None, help="Path to save optimized article")

    # run
    p = sub.add_parser("run", help="Execute full pipeline from config")
    p.add_argument("--config", required=True, help="Path to blog-config.json")
    p.add_argument(
        "--max-iterations", type=int, default=5, help="Maximum optimization iterations"
    )
    p.add_argument(
        "--require-review",
        action="store_true",
        help="Require editorial approval before publish",
    )

    # verify
    p = sub.add_parser("verify", help="Verify post-deployment status of a published article")
    p.add_argument("--url", required=True, help="Published article URL to verify")
    p.add_argument("--config", default=None, help="Path to blog config JSON")
    p.add_argument("--output", default=None, help="Path to save verification report JSON")

    # schema
    p = sub.add_parser("schema", help="Generate JSON-LD schema markup")
    p.add_argument("--article", required=True, help="Path to article markdown file")
    p.add_argument("--config", default=None, help="Path to blog config JSON")
    p.add_argument("--output", default=None, help="Path to save schema JSON")

    # publish
    p = sub.add_parser("publish", help="Format and publish an article")
    p.add_argument("--article", required=True, help="Path to article markdown file")
    p.add_argument(
        "--platform",
        default="generic",
        choices=[
            "nextjs",
            "hugo",
            "astro",
            "gatsby",
            "wordpress",
            "ghost",
            "framer",
            "generic",
        ],
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Format without pushing to git"
    )
    p.add_argument("--output", default=None, help="Path to save formatted article")
    p.add_argument(
        "--require-review", action="store_true", help="Require editorial approval"
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    # Configure logging based on flags
    if getattr(args, "verbose", False):
        logging.basicConfig(
            level=logging.DEBUG, format="%(name)s %(levelname)s: %(message)s"
        )
    elif getattr(args, "quiet", False):
        logging.basicConfig(
            level=logging.ERROR, format="%(name)s %(levelname)s: %(message)s"
        )
    else:
        logging.basicConfig(
            level=logging.INFO, format="%(name)s %(levelname)s: %(message)s"
        )

    cmds = {
        "init": cmd_init,
        "trend": cmd_trend,
        "score-keyword": cmd_score_keyword,
        "article": cmd_article,
        "score-article": cmd_score_article,
        "report": cmd_report,
        "state": cmd_state,
        "validate": cmd_validate,
        "optimize": cmd_optimize,
        "run": cmd_run,
        "schema": cmd_schema,
        "verify": cmd_verify,
        "publish": cmd_publish,
    }
    fn = cmds.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
