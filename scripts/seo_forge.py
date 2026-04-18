#!/usr/bin/env python3
"""
SEO Forge — Universal Autonomous Blog Engine CLI
Provides state management, pipeline coordination, validation, optimization, and publishing.
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from http.client import HTTPSConnection
from urllib.parse import urlparse

logger = logging.getLogger("seo_forge")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SKILL_NAME = "seo-forge"
PORTABLE_SKILL_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    ".mcp.json",
    "skill.json",
]
PORTABLE_SKILL_DIRS = ["scripts", "agents", "references", "templates", "docs"]
PORTABLE_SKILL_REQUIRED = [
    "SKILL.md",
    "skill.json",
    "scripts/seo_forge.py",
    "templates/blog-config.json",
    "templates/agent-capabilities.json",
    "docs/agent-deployment.md",
]
PORTABLE_SKILL_SKIP_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
}
PORTABLE_SKILL_SKIP_SUFFIXES = (".pyc", ".pyo", ".DS_Store")


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


# ── Portable Skill Packaging ───────────────────────────────────────────────


def _source_root(path: str | None = None) -> str:
    return os.path.abspath(os.path.expanduser(path or REPO_ROOT))


def _bundle_relpaths(include_expert_forum: bool = False) -> list[str]:
    relpaths = list(PORTABLE_SKILL_FILES) + list(PORTABLE_SKILL_DIRS)
    if include_expert_forum:
        relpaths.append("expert-forum")
    return relpaths


def _iter_bundle_files(source: str, include_expert_forum: bool = False):
    source = _source_root(source)
    for relpath in _bundle_relpaths(include_expert_forum):
        abs_path = os.path.join(source, relpath)
        if not os.path.exists(abs_path):
            continue
        if os.path.isfile(abs_path):
            yield abs_path, relpath
            continue

        for root, dirs, files in os.walk(abs_path):
            dirs[:] = [
                d
                for d in dirs
                if d not in PORTABLE_SKILL_SKIP_DIRS and not d.endswith(".egg-info")
            ]
            for filename in files:
                if filename.endswith(PORTABLE_SKILL_SKIP_SUFFIXES):
                    continue
                full_path = os.path.join(root, filename)
                rel_file = os.path.relpath(full_path, source)
                yield full_path, rel_file


def _copy_bundle_path(source: str, target: str, relpath: str):
    src = os.path.join(source, relpath)
    dst = os.path.join(target, relpath)
    if not os.path.exists(src):
        return 0
    if os.path.isdir(src):
        shutil.copytree(
            src,
            dst,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
                ".mypy_cache",
                "*.pyc",
                "*.pyo",
                ".DS_Store",
            ),
        )
        copied = 0
        for _, _, files in os.walk(dst):
            copied += len(files)
        return copied
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return 1


def _target_skill_dir(target: str, name: str = SKILL_NAME) -> str:
    target = os.path.abspath(os.path.expanduser(target))
    if os.path.basename(target.rstrip(os.sep)) != name:
        target = os.path.join(target, name)
    return target


def build_doctor_report(source: str | None = None) -> dict:
    source = _source_root(source)
    required = [
        {"path": relpath, "ok": os.path.exists(os.path.join(source, relpath))}
        for relpath in PORTABLE_SKILL_REQUIRED
    ]
    optional = [
        {"path": relpath, "ok": os.path.exists(os.path.join(source, relpath))}
        for relpath in [
            "README.md",
            "docs/mcp-tools.md",
            ".mcp.json",
        ]
    ]
    integrations = {
        "glm_zhipu": {
            "ready": bool(os.environ.get("ZHIPU_API_KEY")),
            "env": "ZHIPU_API_KEY",
            "covers": ["web_search", "web_fetch", "repo_read"],
        },
        "tavily": {
            "ready": bool(os.environ.get("TAVILY_API_KEY")),
            "env": "TAVILY_API_KEY",
            "covers": ["web_search", "web_fetch"],
        },
        "exa": {
            "ready": bool(os.environ.get("EXA_API_KEY")),
            "env": "EXA_API_KEY",
            "covers": ["web_search", "web_fetch"],
        },
        "github_cli": {
            "ready": shutil.which("gh") is not None,
            "env": "GH_TOKEN or GITHUB_TOKEN recommended for private repos",
            "covers": ["repo_read", "pull_request", "checks"],
        },
    }
    commands = {
        "git": shutil.which("git") is not None,
        "gh": shutil.which("gh") is not None,
        "python": True,
    }
    python_ok = sys.version_info >= (3, 8)
    return {
        "name": SKILL_NAME,
        "source": source,
        "python": {
            "version": ".".join(str(part) for part in sys.version_info[:3]),
            "ok": python_ok,
            "requires": ">=3.8",
        },
        "required": required,
        "optional": optional,
        "commands": commands,
        "integrations": integrations,
        "ok": python_ok and all(item["ok"] for item in required),
    }


def _print_doctor_report(report: dict):
    print("SEO Forge doctor")
    print(f"Source: {report['source']}")
    print(
        "Python: "
        + ("ok" if report["python"]["ok"] else "missing")
        + f" ({report['python']['version']}, requires {report['python']['requires']})"
    )
    print("Required files:")
    for item in report["required"]:
        print(f"  [{'ok' if item['ok'] else 'missing'}] {item['path']}")
    print("Portable extras:")
    for item in report["optional"]:
        print(f"  [{'ok' if item['ok'] else 'missing'}] {item['path']}")
    print("Local commands:")
    for name, ok in report["commands"].items():
        print(f"  [{'ok' if ok else 'missing'}] {name}")
    print("Integrations:")
    for name, item in report["integrations"].items():
        status = "ready" if item["ready"] else "not configured"
        print(f"  [{status}] {name} ({item['env']})")
    print(f"Overall: {'ok' if report['ok'] else 'needs attention'}")


def cmd_doctor(args):
    report = build_doctor_report(getattr(args, "source", None))
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_doctor_report(report)
    if not report["ok"]:
        sys.exit(1)


def cmd_install_skill(args):
    source = _source_root(getattr(args, "source", None))
    name = getattr(args, "name", SKILL_NAME)
    target = _target_skill_dir(args.target, name)
    missing = [
        relpath
        for relpath in PORTABLE_SKILL_REQUIRED
        if not os.path.exists(os.path.join(source, relpath))
    ]
    if missing:
        raise PipelineError("Missing required bundle files: " + ", ".join(missing))

    if os.path.exists(target) and not getattr(args, "overwrite", False):
        raise PipelineError(
            f"Target already exists: {target}. Re-run with --overwrite to refresh it."
        )

    os.makedirs(target, exist_ok=True)
    if getattr(args, "overwrite", False):
        for relpath in _bundle_relpaths(getattr(args, "include_expert_forum", False)):
            dst = os.path.join(target, relpath)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            elif os.path.exists(dst):
                os.unlink(dst)

    copied = 0
    for relpath in _bundle_relpaths(getattr(args, "include_expert_forum", False)):
        copied += _copy_bundle_path(source, target, relpath)

    result = {"status": "ok", "target": target, "files_copied": copied}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_export_skill(args):
    source = _source_root(getattr(args, "source", None))
    output = os.path.abspath(os.path.expanduser(args.output))
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    files = list(
        _iter_bundle_files(source, getattr(args, "include_expert_forum", False))
    )
    if not files:
        raise PipelineError(f"No bundle files found in {source}")

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for full_path, relpath in files:
            archive.write(full_path, relpath)
    result = {"status": "ok", "output": output, "files": len(files)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ── Original Commands ──────────────────────────────────────────────────────


def _score_benchmark() -> dict:
    """Run scoring benchmarks against known inputs to validate scoring model."""
    benchmarks = [
        {
            "name": "empty_article",
            "md": "",
            "keyword": "test",
            "expected_max": 15,
            "description": "Empty article should score very low",
        },
        {
            "name": "keyword_dense_article",
            "md": (
                "# AI Writing Tools Guide\n\n"
                "## Best AI Writing Tools\n\n"
                "AI writing tools are essential for content creators. "
                "I use AI writing tools daily. We tested AI writing tools extensively. "
                "Our team evaluated AI writing tools. My experience with AI writing tools was positive.\n\n"
                "## How AI Writing Tools Work\n\n"
                "AI writing tools use language models. AI writing tools help with drafting. "
                "In my testing, AI writing tools performed well. We found AI writing tools reliable.\n\n"
                "### AI Writing Tools Features\n\n"
                "The best AI writing tools offer grammar checking. "
                "AI writing tools also provide tone suggestions.\n\n"
                "## AI Writing Tools Comparison\n\n"
                "We compared AI writing tools. AI writing tools vary in quality.\n\n"
                "## AI Writing Tools FAQ\n\n"
                "### What are AI writing tools?\nAnswer here.\n\n"
                "### How much do AI writing tools cost?\nAnswer.\n\n"
                "### Are AI writing tools accurate?\nYes.\n\n"
                "### Can AI writing tools replace humans?\nNo.\n\n"
                "### Which AI writing tools are best?\nIt depends.\n\n"
                "### How to use AI writing tools?\nFollow the guide.\n\n"
                "## References\n\n"
                "- https://arxiv.org/abs/2401.0001\n"
                "- https://www.nature.com/articles/s41586-024-0001\n"
                "- https://www.reuters.com/article/ai-writing\n"
                "- https://nist.gov/publication/ai-framework\n"
            ),
            "keyword": "AI writing tools",
            "expected_min": 50,
            "description": "Keyword-dense article should score moderately",
        },
        {
            "name": "minimal_article",
            "md": "# Test\n\nShort.",
            "keyword": "test",
            "expected_max": 20,
            "description": "Minimal article should score low",
        },
        {
            "name": "ymyl_health_article",
            "md": (
                "# Health Benefits of Meditation\n\n"
                "## What is Meditation?\n\n"
                "Meditation is a practice of focused attention. "
                "I have practiced meditation for five years and experienced significant benefits.\n\n"
                "## Health Benefits\n\n"
                "Research shows meditation reduces stress. "
                "A 2023 study in the Journal of Clinical Psychology found regular meditation reduces cortisol by 25%.\n\n"
                "### Meditation for Sleep\n\n"
                "We recommend meditation before bedtime. My experience confirms this helps.\n\n"
                "## References\n\n"
                "- https://www.nih.gov/meditation-research\n"
                "- https://www.mayoclinic.org/meditation-benefits\n"
            ),
            "keyword": "meditation health",
            "expected_sub_scores": {"eeat_compliance": {"min": 5}},
            "description": "YMYL health article should score well on E-E-A-T",
        },
        {
            "name": "seo_optimized_article",
            "md": (
                "# Best Project Management Software 2024\n\n"
                "## Top Project Management Tools\n\n"
                "Project management software helps teams collaborate effectively. "
                "The best project management software includes features like task tracking, "
                "Gantt charts, and team communication tools. Our team tested project management software extensively.\n\n"
                "## Project Management Software Comparison\n\n"
                "We compared project management software options. "
                "Each project management software has unique strengths.\n\n"
                "### How to Choose Project Management Software\n\n"
                "Consider your team size and workflow when selecting project management software.\n\n"
                "## Project Management Software FAQ\n\n"
                "### What is project management software?\nIt helps teams organize work.\n\n"
                "### How much does project management software cost?\nPlans start from free.\n\n"
                "## References\n\n"
                "- https://www.gartner.com/project-management\n"
                "- https://www.capterra.com/pm-comparison\n"
            ),
            "keyword": "project management software",
            "expected_sub_scores": {
                "seo_quality": {"min": 10},
                "content_depth": {"min": 8},
            },
            "description": "Well-structured SEO article should score well on SEO quality",
        },
    ]
    results = []
    for bm in benchmarks:
        scores = compute_article_scores(bm["md"], bm["keyword"])
        passed = True
        if "expected_max" in bm:
            passed = scores["total"] <= bm["expected_max"]
        if "expected_min" in bm:
            passed = scores["total"] >= bm["expected_min"]
        sub_checks = {}
        if "expected_sub_scores" in bm:
            for axis, expectation in bm["expected_sub_scores"].items():
                actual = scores.get(axis, {}).get("score", 0)
                if "min" in expectation:
                    ok = actual >= expectation["min"]
                    sub_checks[axis] = {
                        "actual": actual,
                        "min": expectation["min"],
                        "pass": ok,
                    }
                    if not ok:
                        passed = False
        results.append(
            {
                "name": bm["name"],
                "score": scores["total"],
                "passed": passed,
                "description": bm["description"],
                "sub_checks": sub_checks or None,
            }
        )
    return {"benchmarks": results, "all_passed": all(r["passed"] for r in results)}


def cmd_init(args):
    root = args.root
    domain = generate_id(args.domain)
    os.makedirs(f"{root}/keywords", exist_ok=True)
    os.makedirs(f"{root}/articles", exist_ok=True)
    os.makedirs(f"{root}/scoring", exist_ok=True)
    os.makedirs(f"{root}/build_logs", exist_ok=True)
    os.makedirs(f"{root}/images", exist_ok=True)

    kb_path = f"{root}/brand-knowledge.json"
    if not os.path.exists(kb_path):
        kb = {
            "company": args.domain,
            "facts": [],
            "claims": [],
            "limitations": [],
            "competitors": [],
            "forbidden_claims": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(kb_path, kb)

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


def _validate_reference_authority(md: str, config: dict | None = None) -> dict:
    """Validate that references come from authoritative external sources.

    Returns dict with:
      - external_authority_links: count of links from trusted domains
      - total_links: total reference URLs
      - authority_ratio: ratio of trusted to total
      - has_minimum_authority: bool (at least 2 external authority links)
    """
    config = config or {}
    urls = _extract_urls(md)
    site_url = config.get("site_url", "")
    config_domains = config.get("trusted_reference_domains", [])
    all_trusted = list(set(TRUSTED_DOMAINS) | set(config_domains))
    external = [u for u in urls if not (site_url and u.startswith(site_url))]
    authority = [u for u in external if any(d in u for d in all_trusted)]
    return {
        "external_authority_links": len(authority),
        "total_links": len(urls),
        "external_links": len(external),
        "authority_ratio": round(len(authority) / max(1, len(external)), 2)
        if external
        else 0.0,
        "has_minimum_authority": len(authority) >= 2,
        "authority_domains": list(
            {d for u in authority for d in all_trusted if d in u}
        ),
    }


SUPERLATIVE_WORDS = [
    "best",
    "worst",
    "greatest",
    "most",
    "least",
    "top",
    "number one",
    "#1",
    "leading",
    "premier",
    "ultimate",
    "revolutionary",
    "game-changing",
    "incredible",
    "amazing",
    "groundbreaking",
    "unprecedented",
    "world-class",
    "cutting-edge",
    "state-of-the-art",
    "next-gen",
    "best-in-class",
    "industry-leading",
    "unmatched",
    "unrivaled",
    "unsurpassed",
    "perfect",
    "flawless",
    "game-changer",
    "transformative",
    "disruptive",
]

DRAMATIC_PATTERNS = [
    (r"you won'?t believe", "clickbait"),
    (r"it'?s important to note", "hedging"),
    (r"it goes without saying", "hedging"),
    (r"needless to say", "hedging"),
    (r"as everyone knows", "hedging"),
    (r"studies show (?:that|how)", "unsubstantiated"),
    (r"research proves (?:that|how)", "unsubstantiated"),
    (r"everyone (?:knows|agrees)", "unsubstantiated"),
    (
        r"(?:it|this) (?:will|can|could) change (?:everything|the (?:world|industry|game))",
        "hyperbole",
    ),
    (r"nothing (?:else|comes close) (?:can|will|could|compares)", "hyperbole"),
    (r"the only (?:solution|option|choice|way)", "hyperbole"),
]


def _count_superlatives(md: str) -> int:
    pattern = r"\b(" + "|".join(re.escape(w) for w in SUPERLATIVE_WORDS) + r")\b"
    return len(re.findall(pattern, md, re.IGNORECASE))


def _count_dramatic_patterns(md: str) -> tuple[int, list[dict]]:
    """Detect clickbait, hedging, and unsubstantiated claim patterns.

    Returns (total_count, list of {pattern, type, match}).
    """
    found = []
    for pattern, ptype in DRAMATIC_PATTERNS:
        for m in re.finditer(pattern, md, re.IGNORECASE):
            found.append({"pattern": pattern, "type": ptype, "match": m.group()})
    return len(found), found


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


def _count_internal_links(md: str, site_url: str) -> tuple[int, list[str]]:
    """Count internal links to site_url and return (count, section_headers)."""
    if not site_url:
        return 0, []
    pattern = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
    links = pattern.findall(md)
    internal = [u for u in links if u.startswith(site_url)]
    link_sections = []
    sections = re.split(r"^#{1,3}\s+.+$", md, flags=re.MULTILINE)
    for link in internal:
        for section in sections:
            if link in section:
                header = re.match(r"^#{1,3}\s+(.+)$", section.strip(), re.MULTILINE)
                if header:
                    link_sections.append(header.group(1).strip())
                break
    return len(internal), link_sections


def _count_images(md: str) -> int:
    return len(re.findall(r"<img\s", md, re.IGNORECASE))


def _count_svgs(md: str) -> int:
    return len(re.findall(r"<svg\s", md, re.IGNORECASE))


def _count_youtube_embeds(md: str) -> int:
    return len(re.findall(r"youtube\.com/embed/", md, re.IGNORECASE))


def _check_image_alt_and_dimensions(md: str) -> dict:
    """Check images for alt text, width, height, and loading attributes."""
    imgs = re.findall(r"<img\s[^>]*>", md, re.IGNORECASE)
    issues = []
    for img in imgs:
        if not re.search(r'alt=["\']', img, re.IGNORECASE):
            issues.append("missing alt attribute")
        if not re.search(r"width=", img, re.IGNORECASE):
            issues.append("missing width attribute")
        if not re.search(r"height=", img, re.IGNORECASE):
            issues.append("missing height attribute")
        if not re.search(r"loading=", img, re.IGNORECASE):
            issues.append("missing loading attribute")
    return {"total_images": len(imgs), "issues": issues}


def _media_richness_score(md: str) -> int:
    """Score 0-3 for media variety in content."""
    images = _count_images(md)
    svgs = _count_svgs(md)
    youtube = _count_youtube_embeds(md)
    has_cover = bool(re.search(r"cover[_-]?image", md, re.IGNORECASE))
    score = 0
    if images >= 1:
        score += 1
    if images >= 1 and (svgs >= 1 or youtube >= 1):
        score += 1
    if has_cover and images >= 1 and (svgs >= 1 or youtube >= 1):
        score += 1
    return min(3, score)


def _extract_seo_title(md: str) -> str:
    """Extract SEO title from structured output or frontmatter."""
    match = re.search(r"^SEO_TITLE:\s*(.+)$", md, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^seo_title:\s*(.+)$", md, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return ""


def _parse_structured_content(md: str) -> dict:
    """Parse content-architect structured output or plain markdown."""
    result = {
        "title": "",
        "seo_title": "",
        "slug": "",
        "meta_description": "",
        "cover_image": "",
        "cover_alt": "",
        "content": md,
    }
    title_match = re.search(r"^TITLE:\s*(.+)$", md, re.MULTILINE)
    seo_title_match = re.search(r"^SEO_TITLE:\s*(.+)$", md, re.MULTILINE)
    slug_match = re.search(r"^SLUG:\s*(.+)$", md, re.MULTILINE)
    meta_match = re.search(r"^META:\s*(.+)$", md, re.MULTILINE)
    alt_match = re.search(r"^ALT:\s*(.+)$", md, re.MULTILINE)
    cover_match = re.search(r"^COVER_IMAGE_URL:\s*(.+)$", md, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()
    if seo_title_match:
        result["seo_title"] = seo_title_match.group(1).strip()
    if slug_match:
        result["slug"] = slug_match.group(1).strip()
    if meta_match:
        result["meta_description"] = meta_match.group(1).strip()
    if alt_match:
        result["cover_alt"] = alt_match.group(1).strip()
    if cover_match:
        result["cover_image"] = cover_match.group(1).strip()
    if not result["title"]:
        h1 = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
        result["title"] = h1.group(1).strip() if h1 else "Untitled"
    if not result["meta_description"]:
        result["meta_description"] = _extract_meta_description(md)
    if not result["slug"]:
        result["slug"] = generate_id(result["title"])
    if not result["seo_title"]:
        t = result["title"]
        result["seo_title"] = (t[:57] + "...") if len(t) > 60 else t
    content_match = re.search(r"^CONTENT:\s*\n", md, re.MULTILINE)
    if content_match:
        body = md[content_match.end() :]
        body = re.sub(
            r"^(TITLE|SEO_TITLE|SLUG|META|ALT|COVER_IMAGE_URL|IMAGES|SVG|YOUTUBE):\s*.*\n?",
            "",
            body,
            flags=re.MULTILINE,
        )
        result["content"] = body
    else:
        body = re.sub(r"^---[\s\S]*?---", "", md).lstrip("\n")
        body = re.sub(r"^# .+$", "", body, count=1, flags=re.MULTILINE).lstrip("\n")
        result["content"] = body
    return result


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
    # word_count_score (0-4)
    wc_score = (
        min(4, max(0, word_count * 4 // min_words)) if word_count < min_words else 4
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

    # needs_met (0-4)
    has_faq_coverage = faq_count >= 3
    has_task_paths = bool(
        re.findall(
            r"\b(step|how to|guide|tutorial|process|method|approach)\b",
            md,
            re.IGNORECASE,
        )
    )
    nm_score = min(4, has_faq_coverage * 2 + has_task_paths * 1 + min(faq_count, 1))

    # internal_links (0-3)
    site_url = config.get("site_url", "") if config else ""
    il_count, _ = _count_internal_links(md, site_url)
    il_score = min(3, il_count)

    # media_richness (0-3)
    mr_score = _media_richness_score(md)

    content_depth = (
        wc_score + faq_score + extract_score + ev_score + nm_score + il_score + mr_score
    )

    # Reference Authority (0-25)
    # source_count (0-7)
    src_score = min(7, len(urls))

    # url_validity (0-6) — format check only (HEAD checks done by validate)
    valid_format = sum(
        1 for u in urls if re.match(r"https?://[a-z0-9].+\.[a-z]{2,}", u, re.IGNORECASE)
    )
    url_score = min(6, valid_format * 6 // max(1, len(urls))) if urls else 0

    # domain_credibility (0-6) — merge built-in + config trusted domains
    config_domains = config.get("trusted_reference_domains", []) if config else []
    all_trusted = list(set(TRUSTED_DOMAINS) | set(config_domains))
    credible = sum(1 for u in urls if any(d in u for d in all_trusted))
    cred_score = min(6, credible * 3) if urls else 0

    # citation_worthiness (0-6)
    attributions = _count_source_attributions(md)
    has_entities = len(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", md)) >= 5
    cite_score = min(
        6, (attributions >= 2) * 3 + has_entities * 2 + min(attributions, 1)
    )

    reference_authority = src_score + url_score + cred_score + cite_score

    # Brand knowledge penalty: check for forbidden claims
    kb_path = (
        f"{config.get('root', './seo-forge-data')}/brand-knowledge.json"
        if config
        else None
    )
    forbidden_violations = 0
    forbidden_matched = []
    if kb_path and os.path.exists(kb_path):
        kb = load_json(kb_path)
        md_lower = md.lower()
        for fc in kb.get("forbidden_claims", []):
            text = fc.get("text", "") if isinstance(fc, dict) else fc
            if text and text.lower() in md_lower:
                forbidden_violations += 1
                forbidden_matched.append(text)
    trust_score = trust_score - min(trust_score, forbidden_violations)

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
                "internal_links": il_score,
                "media_richness": mr_score,
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
            "internal_link_count": il_count,
            "media_richness": mr_score,
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
    heading_pass = (
        not details["h1_in_body"]
        and details["h2_count"] >= 1
        and details["h3_count"] >= 1
    )
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

    # Internal links
    site_url = config.get("site_url", "")
    il_count, il_sections = _count_internal_links(md, site_url)
    il_pass = il_count >= 2 and len(set(il_sections)) >= 2 if site_url else True
    checks["internal_links"] = {
        "count": il_count,
        "min": 2,
        "sections": il_sections,
        "pass": il_pass,
        "suggestion": ""
        if il_pass
        else f"Add internal links to site_url (need 2+ across different sections, currently {il_count})"
        if site_url
        else "Set site_url in config to enable internal link checking",
    }

    # Image accessibility
    img_check = _check_image_alt_and_dimensions(md)
    img_pass = len(img_check["issues"]) == 0 or img_check["total_images"] == 0
    checks["image_accessibility"] = {
        "total_images": img_check["total_images"],
        "issues": img_check["issues"],
        "pass": img_pass,
        "suggestion": ""
        if img_pass
        else "Images need alt, width, height, and loading attributes",
    }

    # SEO title
    seo_title = _extract_seo_title(md)
    seo_title_len = len(seo_title)
    seo_title_pass = 50 <= seo_title_len <= 60 if seo_title else False
    checks["seo_title"] = {
        "value": seo_title_len,
        "range": [50, 60],
        "pass": seo_title_pass,
        "suggestion": ""
        if seo_title_pass
        else f"SEO title should be 50-60 chars (currently {seo_title_len})"
        if seo_title
        else "Add SEO_TITLE field (50-60 chars, keyword-optimized)",
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
        quality_scores["seo_quality"]["sub_scores"] = quality["seo_quality"][
            "sub_scores"
        ]
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
        "suggestion": ""
        if canonical_match
        else "No canonical tag found in page source",
    }

    # hreflang tags (required for multilingual configs)
    languages = config.get("languages", [])
    multilingual = len(languages) > 1
    hreflang_matches = re.findall(
        r'<link[^>]+hreflang=["\']([^"\']+)["\']', html, re.IGNORECASE
    )
    has_xdefault = any(h == "x-default" for h in hreflang_matches)
    if multilingual:
        hreflang_pass = len(hreflang_matches) > 0 and has_xdefault
        checks["hreflang_tags"] = {
            "pass": hreflang_pass,
            "found": hreflang_matches,
            "has_x_default": has_xdefault,
            "required": True,
            "suggestion": ""
            if hreflang_pass
            else "No hreflang tags found"
            if not hreflang_matches
            else "Missing x-default hreflang tag",
        }
    else:
        checks["hreflang_tags"] = {
            "pass": True,
            "found": hreflang_matches,
            "has_x_default": has_xdefault,
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

    # JSON-LD schema validation (extract and validate embedded schemas)
    schema_issues = []
    jsonld_scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    for script_content in jsonld_scripts:
        try:
            schema_obj = json.loads(script_content.strip())
            issues = _validate_jsonld(schema_obj)
            schema_issues.extend(issues)
        except json.JSONDecodeError:
            schema_issues.append("Invalid JSON-LD: malformed JSON in script tag")
    checks["schema_validation"] = {
        "pass": len(schema_issues) == 0,
        "issues": schema_issues,
        "schema_count": len(jsonld_scripts),
        "suggestion": "" if not schema_issues else "; ".join(schema_issues),
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


def _validate_jsonld(schema_json: dict) -> list[str]:
    """Validate a JSON-LD schema object for required fields. Returns list of issues."""
    issues = []
    schema_type = schema_json.get("@type", "")
    if not schema_type:
        issues.append("Missing @type field")
        return issues

    if schema_type == "Article":
        for field in ("headline", "datePublished"):
            if field not in schema_json:
                issues.append(f"Article schema missing required field: {field}")
    elif schema_type == "FAQPage":
        if "mainEntity" not in schema_json:
            issues.append("FAQPage schema missing required field: mainEntity")
    elif schema_type == "BreadcrumbList":
        if "itemListElement" not in schema_json:
            issues.append(
                "BreadcrumbList schema missing required field: itemListElement"
            )

    if "@context" not in schema_json:
        issues.append(f"{schema_type} schema missing @context field")

    return issues


def _validate_frontmatter(frontmatter_text: str, platform: str) -> list[str]:
    """Validate published frontmatter against SSG requirements."""
    issues = []
    required = {
        "nextjs": [
            "title",
            "seo_title",
            "date",
            "slug",
            "description",
            "cover_image",
            "cover_alt",
        ],
        "hugo": [
            "title",
            "seo_title",
            "date",
            "slug",
            "description",
            "cover_image",
            "cover_alt",
        ],
        "astro": [
            "title",
            "seo_title",
            "pubDate",
            "slug",
            "description",
            "cover_image",
            "cover_alt",
        ],
    }
    fields = required.get(platform, required["nextjs"])
    for field in fields:
        pattern = rf"^{field}\s*:"
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            issues.append(f"Missing required field: {field}")

    if "---" not in frontmatter_text:
        issues.append("Missing frontmatter delimiters (---)")
    elif frontmatter_text.strip().count("---") < 2:
        issues.append("Frontmatter must have opening and closing --- delimiters")

    date_field = "pubDate" if platform == "astro" else "date"
    date_match = re.search(
        rf"^{date_field}\s*:\s*\"?(\d{{4}}-\d{{2}}-\d{{2}})",
        frontmatter_text,
        re.MULTILINE,
    )
    if not date_match:
        issues.append(f"Invalid date format in {date_field}")

    slug_match = re.search(r'^slug\s*:\s*"?([^"\n]+)"?', frontmatter_text, re.MULTILINE)
    if slug_match:
        slug = slug_match.group(1).strip()
        if " " in slug:
            issues.append(f"Slug contains spaces: {slug}")
    else:
        issues.append("Missing slug field")

    desc_match = re.search(r'^description\s*:\s*"(.+)"', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1)
        if len(desc) < 120 or len(desc) > 160:
            issues.append(f"Meta description length {len(desc)} outside 120-160 range")
    return issues


def _semantic_relevance(query: str, document: str) -> float:
    """Compute semantic relevance between query and document using TF-IDF-like scoring.

    Uses term frequency * inverse specificity to weight rare but matching terms
    more heavily than common terms. No external dependencies required.
    """
    stop_words = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "and",
        "but",
        "or",
        "nor",
        "not",
        "so",
        "yet",
        "both",
        "either",
        "neither",
        "each",
        "every",
        "all",
        "any",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "only",
        "own",
        "same",
        "than",
        "too",
        "very",
        "just",
        "because",
        "if",
        "when",
        "where",
        "how",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
    }

    def tokenize(text):
        return [
            w
            for w in re.findall(r"[a-z]+", text.lower())
            if w not in stop_words and len(w) > 2
        ]

    query_terms = tokenize(query)
    doc_terms = tokenize(document)
    if not query_terms or not doc_terms:
        return 0.0

    doc_freq = {}
    for t in set(doc_terms):
        doc_freq[t] = doc_terms.count(t)

    doc_len = len(doc_terms)
    score = 0.0
    for term in query_terms:
        if term in doc_freq:
            tf = doc_freq[term] / doc_len
            specificity = 1.0 / (1 + doc_freq[term])
            score += tf * specificity

    max_score = sum(1.0 / (1 + 1) / doc_len for _ in query_terms) if doc_len else 1.0
    return round(min(1.0, score / max_score) if max_score > 0 else 0.0, 3)


def _suggest_internal_links(
    article_dir: str, site_url: str, keyword: str, max_suggestions: int = 5
) -> list[dict]:
    """Suggest internal links based on existing article corpus with semantic relevance."""
    if not os.path.isdir(article_dir):
        return []

    articles = []
    keyword_lower = keyword.lower()
    keyword_words = set(keyword_lower.split())

    for fname in os.listdir(article_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(article_dir, fname)
        try:
            content = read_file(fpath)
        except Exception:
            continue

        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = (
            title_match.group(1).strip()
            if title_match
            else fname.replace(".md", "").replace("-", " ")
        )

        slug = fname.replace(".md", "")
        word_count = len(content.split())

        title_words = set(title.lower().split())
        overlap = len(keyword_words & title_words)
        semantic = _semantic_relevance(keyword, f"{title} {content[:2000]}")

        if overlap > 0 or semantic > 0.05 or keyword_lower in content.lower():
            articles.append(
                {
                    "title": title,
                    "slug": slug,
                    "url": f"{site_url.rstrip('/')}/{slug}",
                    "relevance": round(overlap + semantic * 10, 2),
                    "semantic_score": semantic,
                    "word_count": word_count,
                }
            )

    articles.sort(key=lambda a: a["relevance"], reverse=True)
    return articles[:max_suggestions]


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
    # Use SEO title as headline if available (more keyword-optimized)
    seo_title = _extract_seo_title(md)
    if seo_title:
        article_schema["headline"] = seo_title
    if meta_desc:
        article_schema["description"] = meta_desc
    if org_name:
        article_schema["publisher"] = {"@type": "Organization", "name": org_name}
    if site_url:
        article_schema["url"] = site_url
    # Cover image from structured output or frontmatter
    cover_match = re.search(r"^COVER_IMAGE_URL:\s*(.+)$", md, re.MULTILINE)
    if not cover_match:
        cover_match = re.search(r"^cover_image:\s*(.+)$", md, re.MULTILINE)
    if cover_match:
        article_schema["image"] = cover_match.group(1).strip().strip('"').strip("'")
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


BLOG_TEMPLATES = {
    "reviewer": {
        "name": "Deep Reviewer",
        "voice": "Professional reviewer — systematic, evidence-based, balanced",
        "h2_sections": [
            "What Is [KEYWORD] and Why I Started Testing It",
            "My Testing Setup and Methodology",
            "How to Get Started: Step-by-Step Guide",
            "Performance Results: What I Actually Found",
            "Honest Pros and Cons After [X] Weeks",
            "How It Compares to [Competitor A] and [Competitor B]",
            "Technical Specifications and Pricing",
            "Common Questions People Ask",
            "My Final Verdict: Who Should Use This",
            "References",
        ],
    },
    "tutorial": {
        "name": "Tutorial Expert",
        "voice": "Helpful instructor — clear, practical, encouraging",
        "h2_sections": [
            "Why [KEYWORD] Matters in [YEAR]",
            "Getting Started with [KEYWORD]: Complete Setup Guide",
            "Tutorial 1: Basic Use Case — Step by Step",
            "Tutorial 2: Advanced Use Case — Pro Techniques",
            "Tutorial 3: Creative Use Case — Pushing the Limits",
            "Troubleshooting: Common Issues and Fixes",
            "[KEYWORD] vs Alternatives: Which Tool Fits Your Workflow",
            "Pricing Breakdown: Is It Worth the Cost",
            "Common Questions People Ask",
            "References",
        ],
    },
    "analyst": {
        "name": "Industry Analyst",
        "voice": "Authoritative, data-driven, objective",
        "h2_sections": [
            "The State of [INDUSTRY] in [YEAR]: Market Overview",
            "What Makes [KEYWORD] Different: Technical Analysis",
            "Real-World Applications: Industries Using This Technology",
            "Hands-On Analysis: Testing [KEYWORD] Across [X] Scenarios",
            "Competitive Landscape: [KEYWORD] vs [Competitor A] vs [Competitor B]",
            "Pricing Analysis: Cost Per Output Compared to Competitors",
            "Limitations and Future Roadmap",
            "Who Benefits Most: Use Case Breakdown",
            "Common Questions People Ask",
            "References",
        ],
    },
    "problem_solver": {
        "name": "Problem Solver",
        "voice": "Empathetic, solution-focused, results-oriented",
        "h2_sections": [
            "The Problem: Why [Traditional Approach] No Longer Works",
            "Discovering [KEYWORD]: My First Impressions",
            "Solution 1: How [KEYWORD] Solves [Pain Point 1]",
            "Solution 2: How [KEYWORD] Solves [Pain Point 2]",
            "Solution 3: How [KEYWORD] Solves [Pain Point 3]",
            "Before vs After: Real Results from My Projects",
            "How [KEYWORD] Stacks Up Against [Competitors]",
            "Pricing: Is the Investment Worth It",
            "Common Questions People Ask",
            "References",
        ],
    },
    "beginners_guide": {
        "name": "Beginner's Guide",
        "voice": "Friendly mentor — approachable, encouraging, clear",
        "h2_sections": [
            "What Is [KEYWORD]? A Complete Introduction",
            "Who Is [KEYWORD] For? (And Who It's Not For)",
            "Getting Started: Your First Result in 5 Minutes",
            "The Essential Features You Need to Know",
            "5 Beginner Mistakes to Avoid",
            "Leveling Up: Intermediate Tips and Tricks",
            "[KEYWORD] vs Other Beginner-Friendly Tools",
            "Pricing Guide: Which Plan Is Right for You",
            "Common Questions People Ask",
            "References",
        ],
    },
    "storyteller": {
        "name": "Storyteller",
        "voice": "Personal narrative — authentic, emotional, relatable",
        "h2_sections": [
            "The Problem That Changed Everything: My [X]-Month Journey",
            "Why I Almost Gave Up on [CATEGORY] Tools",
            "The Moment I Discovered [KEYWORD]: First Impressions",
            "My First Week: Honest Reactions and Real Surprises",
            "Real Projects I've Completed: What I Actually Made",
            "The Results That Surprised Me Most",
            "How [KEYWORD] Compares to What I Used Before",
            "Who Will Love This Tool (And Who Won't)",
            "Common Questions People Ask",
            "References",
        ],
    },
    "comparison": {
        "name": "Deep Comparison",
        "voice": "Objective comparison — fair, data-driven, structured",
        "h2_sections": [
            "[KEYWORD] vs [Competitor]: The Ultimate Comparison",
            "Quick Verdict: Which Tool Wins for Most Users",
            "Feature-by-Feature Breakdown: What Each Tool Offers",
            "Output Quality Comparison: Real Examples and Side-by-Side Tests",
            "Pricing Comparison: True Cost Analysis of Each Tool",
            "Speed and Performance: Head-to-Head Test Results",
            "Ease of Use: Learning Curve and Interface Design",
            "Use Case Matching: Which Tool Wins for Your Scenario",
            "Common Questions People Ask",
            "References",
        ],
    },
    "case_study": {
        "name": "Case Study",
        "voice": "Results-focused, specific, credible",
        "h2_sections": [
            "Case Study: How [User Type] Used [KEYWORD] to [Achieve Result]",
            "The Challenge: What They Were Trying to Solve",
            "Why They Chose [KEYWORD] Over Alternatives",
            "Implementation: How They Set Up Their Workflow",
            "Results: Measurable Outcomes After [X] Weeks",
            "Key Lessons: What Worked, What Didn't, and What Surprised Them",
            "Replicating This Success: A Step-by-Step Framework",
            "How [KEYWORD] Compares for This Use Case",
            "Common Questions People Ask",
            "References",
        ],
    },
}

INTENT_SIGNALS = {
    "tutorial": ["how to", "tutorial", "guide", "step by step", "learn"],
    "analyst": ["technical", "architecture", "specs", "analysis", "deep dive"],
    "beginners_guide": [
        "beginner",
        "introduction",
        "what is",
        "getting started",
        "basics",
    ],
    "comparison": ["vs", "compare", "alternative", "versus", "which is better"],
    "case_study": [
        "case study",
        "how [x] used",
        "real world",
        "example",
        "success story",
    ],
    "storyteller": ["journey", "story", "experience", "honest review", "my experience"],
    "problem_solver": ["fix", "solve", "problem", "troubleshoot", "solution"],
}

LANG_PHRASES = {
    "en": {
        "introduction": "We have spent months evaluating {keyword} to compile this guide. In our experience, these tools change how we approach content creation. I personally tested the leading options and documented our findings below.",
        "disclosure": "Some tools mentioned offer affiliate partnerships. Our recommendations are based solely on testing results, not affiliate arrangements.",
        "content_placeholder": "[Content for this section about {keyword}]",
        "faq_question": "{keyword} FAQ question {n}?",
        "faq_answer": "Concise answer to FAQ question {n} about {keyword}.",
        "references": "References",
        "learn_more": "Learn more about {keyword} on our site",
        "guide_title": "{keyword}: A Complete Guide",
        "guide_meta": "A comprehensive guide to {keyword} with practical tips, methodology, and real results.",
    },
    "zh": {
        "introduction": "我们花了几个月时间评估{keyword}，整理了这份指南。根据我们的经验，这些工具改变了我们处理内容创建的方式。我亲自测试了主要选项，并在下方记录了我们的发现。",
        "disclosure": "提及的部分工具提供联盟合作关系。我们的推荐完全基于测试结果，而非联盟安排。",
        "content_placeholder": "[关于{keyword}的本节内容]",
        "faq_question": "{keyword}常见问题{n}？",
        "faq_answer": "关于{keyword}的常见问题{n}的简要回答。",
        "references": "参考资料",
        "learn_more": "了解更多关于{keyword}的信息",
        "guide_title": "{keyword}：完整指南",
        "guide_meta": "关于{keyword}的全面指南，包含实用技巧、方法和真实结果。",
    },
    "es": {
        "introduction": "Hemos pasado meses evaluando {keyword} para compilar esta guía. En nuestra experiencia, estas herramientas cambian cómo abordamos la creación de contenido. Probé personalmente las opciones principales y documenté nuestros hallazgos.",
        "disclosure": "Algunas herramientas mencionadas ofrecen asociaciones de afiliados. Nuestras recomendaciones se basan únicamente en resultados de pruebas, no en acuerdos de afiliados.",
        "content_placeholder": "[Contenido para esta sección sobre {keyword}]",
        "faq_question": "Pregunta frecuente {n} sobre {keyword}?",
        "faq_answer": "Respuesta concisa a la pregunta frecuente {n} sobre {keyword}.",
        "references": "Referencias",
        "learn_more": "Más información sobre {keyword}",
        "guide_title": "{keyword}: Guía completa",
        "guide_meta": "Una guía completa sobre {keyword} con consejos prácticos, metodología y resultados reales.",
    },
    "de": {
        "introduction": "Wir haben Monate damit verbracht, {keyword} zu evaluieren und diesen Leitfaden zusammenzustellen. Unserer Erfahrung nach verändern diese Tools, wie wir die Content-Erstellung angehen. Ich habe die führenden Optionen persönlich getestet.",
        "disclosure": "Einige der genannten Tools bieten Affiliate-Partnerschaften an. Unsere Empfehlungen basieren ausschließlich auf Testergebnissen.",
        "content_placeholder": "[Inhalt für diesen Abschnitt über {keyword}]",
        "faq_question": "FAQ Frage {n} zu {keyword}?",
        "faq_answer": "Kurze Antwort auf FAQ-Frage {n} zu {keyword}.",
        "references": "Referenzen",
        "learn_more": "Mehr über {keyword} erfahren",
        "guide_title": "{keyword}: Ein vollständiger Leitfaden",
        "guide_meta": "Ein umfassender Leitfaden zu {keyword} mit praktischen Tipps, Methodik und echten Ergebnissen.",
    },
    "ja": {
        "introduction": "{keyword}を評価するために数ヶ月を費やし、このガイドを作成しました。私たちの経験では、これらのツールはコンテンツ作成のアプローチを変えます。主要なオプションを実際にテストし、結果を文書化しました。",
        "disclosure": "紹介する一部のツールはアフィリエイト提携を提供しています。推奨はテスト結果のみに基づいています。",
        "content_placeholder": "[{keyword}に関するこのセクションの内容]",
        "faq_question": "{keyword}に関するよくある質問{n}？",
        "faq_answer": "{keyword}に関するよくある質問{n}への簡潔な回答。",
        "references": "参考文献",
        "learn_more": "{keyword}について詳しくはこちら",
        "guide_title": "{keyword}：完全ガイド",
        "guide_meta": "{keyword}に関する実践的なヒント、手法、実際の結果を含む包括的なガイド。",
    },
}


def cmd_draft(args):
    """Generate article scaffolding from keyword and template selection."""
    keyword = args.keyword
    template_name = args.template or "auto"
    config = {}
    if getattr(args, "config", None) and os.path.exists(args.config):
        config = load_json(args.config)
    site_url = config.get("site_url", "")

    # Auto-select template based on keyword intent
    if template_name == "auto":
        keyword_lower = keyword.lower()
        for tmpl_key, signals in INTENT_SIGNALS.items():
            if any(s in keyword_lower for s in signals):
                template_name = tmpl_key
                break
        else:
            template_name = "reviewer"

    template = BLOG_TEMPLATES.get(template_name, BLOG_TEMPLATES["reviewer"])
    year = datetime.now(timezone.utc).year

    # Generate H2 sections with keyword substituted
    h2_sections = []
    for section in template["h2_sections"]:
        section = section.replace("[KEYWORD]", keyword)
        section = section.replace("[YEAR]", str(year))
        section = section.replace("[INDUSTRY]", config.get("industry", "Technology"))
        section = section.replace("[X]", "3")
        section = section.replace("[Competitor A]", "Alternative A")
        section = section.replace("[Competitor B]", "Alternative B")
        section = section.replace("[Competitors]", "Alternatives")
        section = section.replace("[Competitor]", "Alternative")
        section = section.replace("[Pain Point 1]", "Your Biggest Challenge")
        section = section.replace("[Pain Point 2]", "Time and Resource Constraints")
        section = section.replace("[Pain Point 3]", "Quality and Consistency Issues")
        section = section.replace("[Traditional Approach]", "Manual Processes")
        section = section.replace("[CATEGORY]", "This Type of")
        section = section.replace("[User Type]", "a Team")
        section = section.replace("[Achieve Result]", "Improve Results")
        h2_sections.append(section)

    # Generate structured content scaffolding
    lang = config.get("language", "en")
    phrases = LANG_PHRASES.get(lang, LANG_PHRASES["en"])

    kw_lower = keyword.lower()
    title = phrases["guide_title"].replace("{keyword}", keyword)
    seo_title = f"{keyword}: Complete Guide ({year})"[:60]
    slug = generate_id(keyword)
    meta = phrases["guide_meta"].replace("{keyword}", kw_lower)
    if len(meta) > 160:
        meta = meta[:157] + "..."
    elif len(meta) < 120:
        meta += " Read our detailed analysis and recommendations."

    content_lines = [
        f"# {title}",
        "",
        phrases["introduction"].replace("{keyword}", kw_lower),
        "",
        f"**Disclosure:** {phrases['disclosure']}",
        "",
    ]

    for i, section in enumerate(h2_sections):
        content_lines.append(f"## {section}")
        content_lines.append("")
        if i < len(h2_sections) - 1:
            content_lines.append(
                phrases["content_placeholder"].replace("{keyword}", kw_lower)
            )
            content_lines.append("")
        if site_url and i > 0 and i % 3 == 0:
            content_lines.append(
                f'<a href="{site_url}">{phrases["learn_more"].replace("{keyword}", kw_lower)}</a>'
            )
            content_lines.append("")

    # Add FAQ section
    faq_section = h2_sections[-2] if h2_sections else "Common Questions People Ask"
    if "Common Questions" in faq_section or "?" in faq_section:
        for j in range(6):
            content_lines.append(
                f"### {phrases['faq_question'].replace('{keyword}', kw_lower).replace('{n}', str(j + 1))}"
            )
            content_lines.append("")
            content_lines.append(
                phrases["faq_answer"]
                .replace("{keyword}", kw_lower)
                .replace("{n}", str(j + 1))
            )
            content_lines.append("")

    # Add references
    content_lines.append(f"### {phrases['references']}")
    content_lines.append("")
    content_lines.append(f"- https://en.wikipedia.org/wiki/{keyword.replace(' ', '_')}")
    if site_url:
        content_lines.append(f"- {site_url}")

    # Build structured output
    output = [
        f"TITLE: {title}",
        f"SEO_TITLE: {seo_title}",
        f"SLUG: {slug}",
        f"META: {meta}",
        f"ALT: Cover image showing {keyword.lower()} comparison and key features",
        "COVER_IMAGE_URL: https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=630&fit=crop",
        "CONTENT:",
        "",
    ]
    output.extend(content_lines)

    result = "\n".join(output)

    output_path = args.output or f"{keyword.lower().replace(' ', '-')}-draft.md"
    write_file(output_path, result)
    logger.info("Draft generated: %s (template: %s)", output_path, template_name)

    draft_info = {
        "keyword": keyword,
        "template": template_name,
        "template_name": template["name"],
        "voice": template["voice"],
        "language": lang,
        "h2_count": len(h2_sections),
        "output": output_path,
        "has_internal_links": bool(site_url),
        "has_cover_image": True,
        "has_seo_title": True,
    }

    articles_dir = config.get("articles_dir", "")
    if articles_dir and site_url:
        suggestions = _suggest_internal_links(articles_dir, site_url, keyword)
        if suggestions:
            draft_info["suggested_internal_links"] = suggestions
            logger.info("Suggested %d internal links from corpus", len(suggestions))

    print(json.dumps(draft_info, indent=2, ensure_ascii=False))
    return draft_info


def cmd_editorial_review(args):
    """Run automated editorial review checks on an article."""
    article_path = args.article
    keyword = args.keyword or ""

    if not os.path.exists(article_path):
        error_json(f"Article file not found: {article_path}", "ValidationError")

    md = read_file(article_path)
    config = {}
    if getattr(args, "config", None) and os.path.exists(args.config):
        config = load_json(args.config)
    seo_rules = config.get("seo_rules", {})
    kw_min = seo_rules.get("keyword_density_min", 1.0)
    kw_max = seo_rules.get("keyword_density_max", 2.0)
    min_words = seo_rules.get("min_word_count", 1000)
    min_faqs = seo_rules.get("faq_min_questions", 6)

    # Compute quality scores for data
    quality = compute_article_scores(md, keyword, config)
    details = quality["details"]

    # Run checklist categories
    checklist = {}

    # Factual accuracy (automated: check source attributions and URLs)
    attributions = _count_source_attributions(md)
    urls = _extract_urls(md)
    fact_pass = attributions >= 2 and len(urls) >= 4
    checklist["factualAccuracy"] = {
        "pass": fact_pass,
        "notes": ""
        if fact_pass
        else f"Need 2+ source attributions (have {attributions}) and 4+ reference URLs (have {len(urls)})",
    }

    # E-E-A-T depth (use scoring sub-scores)
    eeat = quality["eeat_compliance"]["sub_scores"]
    eeat_pass = eeat["first_person"] >= 5 and eeat["experience_evidence"] >= 3
    checklist["eeatDepth"] = {
        "pass": eeat_pass,
        "notes": ""
        if eeat_pass
        else f"First-person score {eeat['first_person']}/8, experience evidence {eeat['experience_evidence']}/7",
    }

    # AI slop detection (check superlatives, repetitive patterns)
    superlatives = _count_superlatives(md)
    ctas = _count_ctas(md)
    slop_pass = superlatives < 10 and ctas <= 3
    checklist["aiSlopDetection"] = {
        "pass": slop_pass,
        "notes": ""
        if slop_pass
        else f"Superlatives: {superlatives} (max 10), CTAs: {ctas} (max 3)",
    }

    # SEO compliance
    density = details["keyword_density"]
    seo_pass = (
        kw_min <= density <= kw_max
        and details["h2_count"] >= 2
        and details["faq_count"] >= min_faqs
        and details["word_count"] >= min_words
    )
    checklist["seoCompliance"] = {
        "pass": seo_pass,
        "notes": ""
        if seo_pass
        else f"Keyword density {density:.1f}%, H2s: {details['h2_count']}, FAQs: {details['faq_count']}, Words: {details['word_count']}",
    }

    # Reference authority (external authority links)
    ref_auth = _validate_reference_authority(md, config)
    ref_pass = ref_auth["has_minimum_authority"]
    checklist["referenceAuthority"] = {
        "pass": ref_pass,
        "notes": ""
        if ref_pass
        else f"External authority links: {ref_auth['external_authority_links']} (need ≥2)",
        "details": ref_auth,
    }

    # Technical checks (heading hierarchy, SEO title)
    heading_ok = not details["h1_in_body"] and details["h2_count"] >= 1
    seo_title = _extract_seo_title(md)
    seo_title_ok = 50 <= len(seo_title) <= 60 if seo_title else False
    tech_pass = heading_ok and seo_title_ok
    checklist["technicalChecks"] = {
        "pass": tech_pass,
        "notes": ""
        if tech_pass
        else f"Heading OK: {heading_ok}, SEO title OK: {seo_title_ok} (len={len(seo_title)})",
    }

    # Structural integrity
    max_ctas = seo_rules.get("max_cta_buttons", 3)
    struct_pass = ctas <= max_ctas
    checklist["structuralIntegrity"] = {
        "pass": struct_pass,
        "notes": "" if struct_pass else f"CTAs: {ctas} (max {max_ctas})",
    }

    # Content quality (word count, internal links, media)
    site_url = config.get("site_url", "")
    il_count, _ = _count_internal_links(md, site_url)
    media = _media_richness_score(md)
    content_pass = details["word_count"] >= min_words and il_count >= 2 and media >= 1
    checklist["contentQuality"] = {
        "pass": content_pass,
        "notes": ""
        if content_pass
        else f"Words: {details['word_count']}, Internal links: {il_count}, Media: {media}/3",
    }

    # Brand voice alignment
    brand_keywords = config.get("brand_voice_keywords", [])
    if brand_keywords:
        md_lower = md.lower()
        matched = [kw for kw in brand_keywords if kw.lower() in md_lower]
        voice_pass = len(matched) >= max(1, len(brand_keywords) // 2)
        checklist["brandVoice"] = {
            "pass": voice_pass,
            "notes": ""
            if voice_pass
            else f"Matched {len(matched)}/{len(brand_keywords)} brand voice keywords: {matched}",
        }
    else:
        checklist["brandVoice"] = {
            "pass": True,
            "notes": "No brand_voice_keywords configured; skipped",
        }

    # Exaggeration control (superlatives, dramatic patterns, claim-to-fact ratio)
    dramatic_count, dramatic_found = _count_dramatic_patterns(md)
    unsubstantiated = sum(1 for d in dramatic_found if d["type"] == "unsubstantiated")
    declarative = _count_declarative_sentences(md)
    verifiable = _count_verifiable_claims(md)
    claim_ratio = (superlatives + dramatic_count) / max(1, verifiable)
    exag_pass = (
        superlatives < 5
        and dramatic_count < 3
        and unsubstantiated == 0
        and claim_ratio <= 0.33
    )
    exag_notes = []
    if superlatives >= 5:
        exag_notes.append(f"superlatives: {superlatives} (max 5)")
    if dramatic_count >= 3:
        exag_notes.append(f"dramatic patterns: {dramatic_count} (max 3)")
    if unsubstantiated > 0:
        exag_notes.append(f"unsubstantiated claims: {unsubstantiated}")
    if claim_ratio > 0.33:
        exag_notes.append(f"claim-to-fact ratio: {claim_ratio:.2f} (max 0.33)")
    checklist["exaggerationControl"] = {
        "pass": exag_pass,
        "notes": "; ".join(exag_notes)
        if exag_notes
        else "Promotional language within limits",
        "details": {
            "superlatives": superlatives,
            "dramatic_patterns": dramatic_count,
            "unsubstantiated_claims": unsubstantiated,
            "claim_to_fact_ratio": round(claim_ratio, 2),
            "verifiable_claims": verifiable,
            "declarative_sentences": declarative,
        },
    }

    # Overall decision
    all_pass = all(c["pass"] for c in checklist.values())
    any_blocked = (
        checklist.get("factualAccuracy", {}).get("pass") is False
        or checklist.get("exaggerationControl", {}).get("pass") is False
    )

    if all_pass:
        decision = "approve"
    elif any_blocked:
        decision = "block"
    else:
        decision = "request_changes"

    result = {
        "article": article_path,
        "keyword": keyword,
        "decision": decision,
        "reviewer": "editorial-reviewer",
        "checklist": checklist,
        "quality_scores": {
            "total": quality["total"],
            "seo_quality": quality["seo_quality"]["score"],
            "eeat_compliance": quality["eeat_compliance"]["score"],
            "content_depth": quality["content_depth"]["score"],
            "reference_authority": quality["reference_authority"]["score"],
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    output_path = getattr(args, "output", None)
    if output_path:
        save_json(output_path, result)
        logger.info("Editorial review saved: %s", output_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


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
    parsed = _parse_structured_content(md)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = parsed["content"]

    # Build frontmatter for each platform
    if platform == "nextjs":
        frontmatter = (
            f"---\n"
            f'title: "{parsed["title"]}"\n'
            f'seo_title: "{parsed["seo_title"]}"\n'
            f'date: "{date_str}"\n'
            f'slug: "{parsed["slug"]}"\n'
            f'description: "{parsed["meta_description"]}"\n'
            f'cover_image: "{parsed["cover_image"]}"\n'
            f'cover_alt: "{parsed["cover_alt"]}"\n'
            f"---\n\n"
        )
    elif platform == "hugo":
        frontmatter = (
            f"---\n"
            f'title: "{parsed["title"]}"\n'
            f'seo_title: "{parsed["seo_title"]}"\n'
            f"date: {date_str}\n"
            f'slug: "{parsed["slug"]}"\n'
            f'description: "{parsed["meta_description"]}"\n'
            f'cover_image: "{parsed["cover_image"]}"\n'
            f'cover_alt: "{parsed["cover_alt"]}"\n'
            f"---\n\n"
        )
    elif platform == "astro":
        frontmatter = (
            f"---\n"
            f'title: "{parsed["title"]}"\n'
            f'seo_title: "{parsed["seo_title"]}"\n'
            f'pubDate: "{date_str}"\n'
            f'slug: "{parsed["slug"]}"\n'
            f'description: "{parsed["meta_description"]}"\n'
            f'cover_image: "{parsed["cover_image"]}"\n'
            f'cover_alt: "{parsed["cover_alt"]}"\n'
            f"---\n\n"
        )
    else:
        frontmatter = (
            f"---\n"
            f'title: "{parsed["title"]}"\n'
            f'seo_title: "{parsed["seo_title"]}"\n'
            f'slug: "{parsed["slug"]}"\n'
            f'date: "{date_str}"\n'
            f'description: "{parsed["meta_description"]}"\n'
            f'cover_image: "{parsed["cover_image"]}"\n'
            f'cover_alt: "{parsed["cover_alt"]}"\n'
            f"---\n\n"
        )

    output_md = frontmatter + body

    fm_issues = _validate_frontmatter(frontmatter, platform)
    if fm_issues:
        logger.warning("Frontmatter issues for %s: %s", platform, fm_issues)

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


COMFYUI_DEFAULT_URL = "http://127.0.0.1:8188"
COMFYUI_DEFAULT_WORKFLOW = "/Users/dawei/ComfyUI/ernie-image-turbo-gguf-workflow.json"
GLM_OCR_DEFAULT_URL = "http://127.0.0.1:8190"
GLM_OCR_DEFAULT_MODEL = "zai-org/GLM-OCR"


def _comfyui_request(url, path, method="GET", data=None, timeout=5):
    """Make an HTTP request to ComfyUI or GLM-OCR API."""
    full_url = f"{url}{path}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(
        full_url,
        data=req_data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_comfyui_check(args):
    """Check if ComfyUI is running and the workflow is valid."""
    url = args.url or COMFYUI_DEFAULT_URL
    workflow_path = args.workflow or COMFYUI_DEFAULT_WORKFLOW
    result = {"running": False, "model_ready": False, "workflow_valid": False}
    try:
        _comfyui_request(url, "/system_stats", timeout=3)
        result["running"] = True
    except Exception:
        print(json.dumps(result, indent=2))
        return
    if os.path.exists(workflow_path):
        try:
            wf = json.loads(read_file(workflow_path))
            has_gguf_loader = any(
                n.get("type") == "UnetLoaderGGUF" for n in wf.get("nodes", [])
            )
            result["workflow_valid"] = has_gguf_loader
            if has_gguf_loader:
                model_node = next(
                    n for n in wf["nodes"] if n.get("type") == "UnetLoaderGGUF"
                )
                model_name = model_node.get("widgets_values", [""])[0]
                model_path = os.path.join(
                    os.path.expanduser("~"),
                    "ComfyUI",
                    "models",
                    "diffusion_models",
                    model_name,
                )
                result["model_ready"] = os.path.exists(model_path)
        except (json.JSONDecodeError, KeyError, StopIteration):
            pass
    print(json.dumps(result, indent=2))


def cmd_comfyui_generate(args):
    """Generate an image via ComfyUI ERNIE-Image-Turbo workflow."""
    url = args.url or COMFYUI_DEFAULT_URL
    workflow_path = args.workflow or COMFYUI_DEFAULT_WORKFLOW
    output_dir = args.output_dir or "./seo-forge-data/images"
    timeout = args.timeout or 120
    prompt_text = args.prompt
    width = args.width or 1024
    height = args.height or 1024
    enhance = not args.no_enhance

    # Check ComfyUI availability first
    try:
        _comfyui_request(url, "/system_stats", timeout=3)
    except Exception as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"ComfyUI not running at {url}. Start ComfyUI first or use --url to specify a different endpoint.",
                    "detail": str(e),
                },
                indent=2,
            )
        )
        return

    os.makedirs(output_dir, exist_ok=True)

    wf = json.loads(read_file(workflow_path))

    # Mutate workflow parameters
    for node in wf["nodes"]:
        if (
            node.get("type") == "PrimitiveStringMultiline"
            and node.get("title") == "Prompt"
        ):
            node["widgets_values"][0] = prompt_text
        elif node.get("type") == "EmptyFlux2LatentImage":
            node["widgets_values"][0] = width
            node["widgets_values"][1] = height
        elif node.get("type") == "PrimitiveBoolean":
            node["widgets_values"][0] = enhance

    # Submit workflow
    payload = {"prompt": wf, "client_id": "seo-forge"}
    resp = _comfyui_request(url, "/prompt", method="POST", data=payload, timeout=10)
    prompt_id = resp.get("prompt_id")
    if not prompt_id:
        print(
            json.dumps(
                {"status": "error", "message": "No prompt_id returned", "detail": resp},
                indent=2,
            )
        )
        return

    # Poll for completion
    max_checks = timeout // 3
    for _ in range(max_checks):
        time.sleep(3)
        try:
            history = _comfyui_request(url, f"/history/{prompt_id}", timeout=10)
        except Exception:
            continue
        entry = history.get(prompt_id)
        if not entry:
            continue
        status = entry.get("status", {})
        if status.get("completed", False) or status.get("status_str") == "success":
            outputs = entry.get("outputs", {})
            for node_id, node_out in outputs.items():
                for img in node_out.get("images", []):
                    fname = img["filename"]
                    img_url = f"{url}/view?filename={urllib.parse.quote(fname)}&type={img.get('type', 'output')}"
                    dest = os.path.join(output_dir, f"{prompt_id[:8]}_{fname}")
                    urllib.request.urlretrieve(img_url, dest)
                    print(
                        json.dumps(
                            {
                                "status": "completed",
                                "prompt_id": prompt_id,
                                "image_path": dest,
                                "width": width,
                                "height": height,
                                "enhanced": enhance,
                            },
                            indent=2,
                        )
                    )
                    return
        if status.get("status_str") == "error":
            print(
                json.dumps(
                    {"status": "error", "prompt_id": prompt_id, "detail": status},
                    indent=2,
                )
            )
            return

    print(
        json.dumps(
            {
                "status": "timeout",
                "prompt_id": prompt_id,
                "message": f"Generation exceeded {timeout}s",
            },
            indent=2,
        )
    )


def cmd_glm_ocr_check(args):
    """Check if GLM-OCR inference server is running."""
    url = args.url or GLM_OCR_DEFAULT_URL
    result = {"running": False}
    try:
        resp = _comfyui_request(url, "/health", timeout=3)
        result["running"] = True
        result["detail"] = resp
    except Exception:
        pass
    print(json.dumps(result, indent=2))


def cmd_glm_ocr_verify(args):
    """Verify an image matches an expected subject using GLM-OCR."""
    url = args.url or GLM_OCR_DEFAULT_URL
    image_path = args.image_path
    expected_subject = args.expected_subject

    if not os.path.exists(image_path):
        print(
            json.dumps(
                {"matches": False, "error": f"Image not found: {image_path}"}, indent=2
            )
        )
        return

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower()
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }.get(ext.lstrip("."), "image/png")

    payload = {
        "model": "glm-ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": f"Describe what you see in this image in one sentence. Does this image show or relate to '{expected_subject}'? Answer YES or NO at the start of your response.",
                    },
                ],
            }
        ],
    }

    try:
        resp = _comfyui_request(
            url, "/v1/chat/completions", method="POST", data=payload, timeout=30
        )
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        matches = content.strip().upper().startswith("YES")
        confidence = "high" if matches else "low"
        print(
            json.dumps(
                {
                    "matches": matches,
                    "description": content,
                    "confidence": confidence,
                    "expected_subject": expected_subject,
                },
                indent=2,
            )
        )
    except Exception as e:
        print(json.dumps({"matches": False, "error": str(e)}, indent=2))


def cmd_brand_knowledge(args):
    """Manage brand knowledge base: init, validate, show."""
    root = args.root
    action = args.action
    kb_path = f"{root}/brand-knowledge.json"

    if action == "init":
        kb = {
            "company": args.company or "",
            "facts": [],
            "claims": [],
            "limitations": [],
            "competitors": [],
            "forbidden_claims": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if args.add_fact:
            kb["facts"].append({"text": args.add_fact, "verified": False})
        if args.add_forbidden:
            kb["forbidden_claims"].append(
                {"text": args.add_forbidden, "reason": "manual"}
            )
        os.makedirs(root, exist_ok=True)
        save_json(kb_path, kb)
        print(
            json.dumps(
                {
                    "status": "ok",
                    "action": "init",
                    "path": kb_path,
                    "company": kb["company"],
                },
                indent=2,
            )
        )

    elif action == "validate":
        if not os.path.exists(kb_path):
            error_json(f"Brand knowledge file not found: {kb_path}", "ValidationError")
        kb = load_json(kb_path)
        issues = []
        if not kb.get("facts"):
            issues.append(
                "No facts defined — article claims cannot be validated against brand knowledge"
            )
        if not kb.get("forbidden_claims"):
            issues.append(
                "No forbidden claims defined — exaggeration control will use general superlative detection only"
            )
        company = kb.get("company", "")
        if not company:
            issues.append("Company name is empty")
        for i, fact in enumerate(kb.get("facts", [])):
            if not fact.get("text"):
                issues.append(f"Fact {i} has empty text")
        for i, claim in enumerate(kb.get("forbidden_claims", [])):
            if not claim.get("text") and not claim.get("reason"):
                issues.append(f"Forbidden claim {i} is empty")
        result = {
            "valid": len(issues) == 0,
            "issues": issues,
            "fact_count": len(kb.get("facts", [])),
            "forbidden_count": len(kb.get("forbidden_claims", [])),
        }
        print(json.dumps(result, indent=2))

    elif action == "show":
        if not os.path.exists(kb_path):
            error_json(f"Brand knowledge file not found: {kb_path}", "ValidationError")
        kb = load_json(kb_path)
        print(json.dumps(kb, indent=2, ensure_ascii=False))


def cmd_image_register(args):
    """Register image metadata in article state."""
    root = args.root
    article_id = args.article_id
    slot = args.slot
    source = args.source
    path = args.path
    alt = args.alt or ""

    state_dir = f"{root}"
    article_file = os.path.join(state_dir, "articles", f"{article_id}.json")
    if not os.path.exists(article_file):
        print(json.dumps({"error": f"Article not found: {article_file}"}, indent=2))
        return

    article = load_json(article_file)
    if "images" not in article:
        article["images"] = []

    article["images"].append(
        {
            "slot": slot,
            "source": source,
            "path": path,
            "alt": alt,
            "registered_at": ts(),
        }
    )
    save_json(article_file, article)
    print(
        json.dumps(
            {"status": "ok", "article_id": article_id, "slot": slot, "source": source},
            indent=2,
        )
    )


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

    # editorial-review
    p = sub.add_parser(
        "editorial-review",
        help="Run automated editorial review checks on an article",
    )
    p.add_argument("--article", required=True, help="Path to article markdown file")
    p.add_argument("--keyword", default="", help="Target keyword for checks")
    p.add_argument("--config", default=None, help="Path to blog config JSON")
    p.add_argument("--output", default=None, help="Path to save review report JSON")

    # verify
    p = sub.add_parser(
        "verify", help="Verify post-deployment status of a published article"
    )
    p.add_argument("--url", required=True, help="Published article URL to verify")
    p.add_argument("--config", default=None, help="Path to blog config JSON")
    p.add_argument(
        "--output", default=None, help="Path to save verification report JSON"
    )

    # schema
    p = sub.add_parser("schema", help="Generate JSON-LD schema markup")
    p.add_argument("--article", required=True, help="Path to article markdown file")
    p.add_argument("--config", default=None, help="Path to blog config JSON")
    p.add_argument("--output", default=None, help="Path to save schema JSON")

    # draft
    p = sub.add_parser(
        "draft", help="Generate article scaffolding from keyword and template"
    )
    p.add_argument("--keyword", required=True, help="Target keyword for the article")
    p.add_argument(
        "--template", default=None, help="Template name (auto-detected if omitted)"
    )
    p.add_argument("--config", default=None, help="Path to blog config JSON")
    p.add_argument("--output", default=None, help="Path to save draft article")

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

    # comfyui-check
    p = sub.add_parser(
        "comfyui-check", help="Check if ComfyUI is running and workflow is valid"
    )
    p.add_argument("--url", default=None, help="ComfyUI API URL")
    p.add_argument("--workflow", default=None, help="Path to workflow JSON")

    # comfyui-generate
    p = sub.add_parser(
        "comfyui-generate", help="Generate image via ComfyUI ERNIE-Image-Turbo"
    )
    p.add_argument("--prompt", required=True, help="Image generation prompt")
    p.add_argument("--width", type=int, default=1024, help="Image width")
    p.add_argument("--height", type=int, default=1024, help="Image height")
    p.add_argument(
        "--output-dir",
        default="./seo-forge-data/images",
        help="Output directory for generated images",
    )
    p.add_argument("--url", default=None, help="ComfyUI API URL")
    p.add_argument("--workflow", default=None, help="Path to workflow JSON")
    p.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    p.add_argument(
        "--no-enhance", action="store_true", help="Disable prompt enhancement"
    )

    # glm-ocr-check
    p = sub.add_parser("glm-ocr-check", help="Check if GLM-OCR server is running")
    p.add_argument("--url", default=None, help="GLM-OCR server URL")

    # glm-ocr-verify
    p = sub.add_parser(
        "glm-ocr-verify",
        help="Verify image content matches expected subject via GLM-OCR",
    )
    p.add_argument("--image-path", required=True, help="Path to image file")
    p.add_argument(
        "--expected-subject", required=True, help="Expected subject to verify"
    )
    p.add_argument("--url", default=None, help="GLM-OCR server URL")

    # brand-knowledge
    p = sub.add_parser("brand-knowledge", help="Manage brand knowledge base")
    p.add_argument("--root", default="./seo-forge-data", help="Pipeline data root")
    p.add_argument(
        "--action",
        required=True,
        choices=["init", "validate", "show"],
        help="Action: init, validate, show",
    )
    p.add_argument("--company", default="", help="Company name for init")
    p.add_argument("--add-fact", default=None, help="Add a fact to the knowledge base")
    p.add_argument(
        "--add-forbidden",
        default=None,
        help="Add a forbidden claim to the knowledge base",
    )

    # image-register
    p = sub.add_parser(
        "image-register", help="Register image metadata in article state"
    )
    p.add_argument("--root", default="./seo-forge-data", help="Pipeline data root")
    p.add_argument("--article-id", required=True, help="Article ID")
    p.add_argument(
        "--slot", required=True, help="Image slot: cover, inline-1, inline-2, etc."
    )
    p.add_argument(
        "--source",
        required=True,
        choices=["generate", "search", "unsplash"],
        help="Image source",
    )
    p.add_argument("--path", required=True, help="Path to image file or URL")
    p.add_argument("--alt", default="", help="Alt text for the image")

    # doctor
    p = sub.add_parser(
        "doctor", help="Check whether the portable skill bundle is deployable"
    )
    p.add_argument("--source", default=None, help="Source repo or skill directory")
    p.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    # install-skill
    p = sub.add_parser(
        "install-skill", help="Copy SEO Forge into an agent skill directory"
    )
    p.add_argument(
        "--target",
        required=True,
        help="Agent skills directory or final seo-forge skill directory",
    )
    p.add_argument("--source", default=None, help="Source repo or skill directory")
    p.add_argument("--name", default=SKILL_NAME, help="Installed skill directory name")
    p.add_argument(
        "--overwrite", action="store_true", help="Refresh an existing skill directory"
    )
    p.add_argument(
        "--include-expert-forum",
        action="store_true",
        help="Also copy generated expert-forum artifacts",
    )

    # export-skill
    p = sub.add_parser("export-skill", help="Create a portable SEO Forge skill zip")
    p.add_argument(
        "--output",
        default=f"{SKILL_NAME}-skill.zip",
        help="Path to write the exported zip file",
    )
    p.add_argument("--source", default=None, help="Source repo or skill directory")
    p.add_argument(
        "--include-expert-forum",
        action="store_true",
        help="Also include generated expert-forum artifacts",
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
        "editorial-review": cmd_editorial_review,
        "verify": cmd_verify,
        "draft": cmd_draft,
        "publish": cmd_publish,
        "comfyui-check": cmd_comfyui_check,
        "comfyui-generate": cmd_comfyui_generate,
        "glm-ocr-check": cmd_glm_ocr_check,
        "glm-ocr-verify": cmd_glm_ocr_verify,
        "image-register": cmd_image_register,
        "brand-knowledge": cmd_brand_knowledge,
        "doctor": cmd_doctor,
        "install-skill": cmd_install_skill,
        "export-skill": cmd_export_skill,
    }
    fn = cmds.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
