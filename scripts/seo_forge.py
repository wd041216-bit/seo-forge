#!/usr/bin/env python3
"""
SEO Forge — Universal Autonomous Blog Engine CLI
Provides state management and pipeline coordination for the SEO Forge skill.
"""

import argparse
import json
import os
from datetime import datetime, timezone


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


# ── Commands ──────────────────────────────────────────────────────────────


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
    print(f"[SEO Forge] Keyword scored: {args.keyword}")
    print(f"  Final Score: {scores['final_score']}")
    print(f"  Grade: {scores['grade']}")
    print(f"  Win Probability: {scores['win_probability']}%")


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

    print(f"[SEO Forge] Article registered: {article_id}")
    print(f"  Keyword: {args.keyword}")
    print(f"  Template: {article['template']}")
    print("  Status: drafted")


def cmd_score_article(args):
    root = args.root
    art_file = f"{root}/articles/{args.article_id}.json"
    article = load_json(art_file)
    if not article:
        print(f"[ERROR] Article not found: {args.article_id}")
        return

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

    print(f"[SEO Forge] Article scored: {args.article_id}")
    print(f"  SEO Quality: {seo}/25")
    print(f"  E-E-A-T: {eeat}/25")
    print(f"  Content Depth: {depth}/25")
    print(f"  References: {refs}/25")
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
    print(f"[SEO Forge] Report saved: {out_file}")


def cmd_state(args):
    root = args.root
    state = load_json(f"{root}/pipeline_state.json")
    if not state:
        print("[ERROR] No pipeline state found.")
        return
    print(json.dumps(state, indent=2, ensure_ascii=False))


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="SEO Forge CLI")
    parser.add_argument("--root", default="./seo-forge-data", help="Pipeline data root")
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

    # article
    p = sub.add_parser("article", help="Register a new article")
    p.add_argument("--keyword", required=True)
    p.add_argument("--template", default="auto")
    p.add_argument("--title", default="")
    p.add_argument("--slug", default="")

    # score-article
    p = sub.add_parser("score-article", help="Score an article")
    p.add_argument("--article-id", required=True)
    p.add_argument("--seo", default="0")
    p.add_argument("--eeat", default="0")
    p.add_argument("--depth", default="0")
    p.add_argument("--refs", default="0")

    # report
    p = sub.add_parser("report", help="Generate pipeline report")
    p.add_argument("--output", default=None)

    # state
    p = sub.add_parser("state", help="Show current pipeline state")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "init": cmd_init,
        "trend": cmd_trend,
        "score-keyword": cmd_score_keyword,
        "article": cmd_article,
        "score-article": cmd_score_article,
        "report": cmd_report,
        "state": cmd_state,
    }
    fn = cmds.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
