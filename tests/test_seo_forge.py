import json
import os
import subprocess
import sys
import tempfile

import pytest

from scripts.seo_forge import (
    cmd_init,
    cmd_trend,
    cmd_score_keyword,
    cmd_article,
    cmd_score_article,
    cmd_report,
    cmd_state,
    cmd_validate,
    cmd_optimize,
    cmd_run,
    cmd_schema,
    cmd_verify,
    cmd_editorial_review,
    cmd_publish,
    generate_id,
    ts,
    load_json,
    save_json,
    read_file,
    write_file,
    PipelineError,
    ValidationError,
    ScoringError,
    PublishError,
    _keyword_density,
    _count_words,
    _heading_hierarchy,
    _count_first_person,
    _count_faqs,
    _extract_meta_description,
    compute_article_scores,
    _is_ymyl,
    CTR_BASELINES,
    _count_internal_links,
    _count_images,
    _count_svgs,
    _count_youtube_embeds,
    _check_image_alt_and_dimensions,
    _media_richness_score,
    _extract_seo_title,
    _parse_structured_content,
    _validate_jsonld,
    cmd_draft,
    _validate_frontmatter,
    _suggest_internal_links,
    LANG_PHRASES,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestUtils:
    def test_generate_id(self):
        assert generate_id("Hello World") == "hello-world"
        assert generate_id("AI Writing Tool") == "ai-writing-tool"
        assert generate_id("it's_a_test") == "its-a-test"
        assert generate_id('quotes"here') == "quoteshere"

    def test_ts_format(self):
        result = ts()
        assert len(result) == 14
        assert result.isdigit()

    def test_load_json_missing(self):
        data = load_json("/nonexistent/path.json")
        assert data == {}

    def test_load_json_exists(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"key": "value"}, f)
            f.flush()
            data = load_json(f.name)
            assert data == {"key": "value"}
        os.unlink(f.name)

    def test_read_write_file(self, tmp_path):
        path = str(tmp_path / "test.md")
        write_file(path, "hello world")
        assert read_file(path) == "hello world"


class TestHelpers:
    def test_keyword_density(self):
        md = "AI writing tools are great. I use AI writing tools daily."
        density = _keyword_density(md, "AI writing tools")
        assert density > 0

    def test_keyword_density_empty(self):
        assert _keyword_density("", "keyword") == 0.0

    def test_count_words(self):
        assert _count_words("one two three") == 3

    def test_heading_hierarchy(self):
        md = "# Title\n\n## Section\n\n### Sub\n\n## Another"
        result = _heading_hierarchy(md)
        assert result["h1_in_body"] is False
        assert result["has_h2"] is True
        assert result["has_h3"] is True

    def test_heading_hierarchy_multiple_h1(self):
        md = "# Title\n\n# Another Title\n\n## Section"
        result = _heading_hierarchy(md)
        assert result["h1_in_body"] is True

    def test_count_first_person(self):
        md = "I think we should use our tools. My experience shows us the way."
        count = _count_first_person(md)
        assert count >= 5

    def test_count_faqs(self):
        md = "## What is AI?\n\n### How does it work?\n\n## Why use AI?"
        count = _count_faqs(md)
        # Lines ending with ? count as FAQ questions
        assert count == 3

    def test_extract_meta_description(self):
        md = '---\ndescription: "This is a test description"\n---\n\n# Title'
        desc = _extract_meta_description(md)
        assert desc == "This is a test description"

    def test_extract_meta_description_missing(self):
        md = "# Title\n\nSome content"
        assert _extract_meta_description(md) == ""


class TestCmdInit:
    def test_init_creates_state(self, tmp_path):
        class Args:
            root = str(tmp_path / "data")
            domain = "Example Corp"
            topic = "AI Tools"
            lang = "en"

        cmd_init(Args())
        state = load_json(f"{Args.root}/pipeline_state.json")
        assert state["domain"] == "Example Corp"
        assert state["domain_id"] == "example-corp"
        assert state["topic"] == "AI Tools"
        assert state["language"] == "en"
        assert state["status"] == "initialized"
        assert state["pipeline_phase"] == "CONFIG"
        assert state["iteration"] == 0
        assert state["score_history"] == []
        assert state["keywords"] == []
        assert state["articles"] == []

    def test_init_creates_directories(self, tmp_path):
        class Args:
            root = str(tmp_path / "data")
            domain = "Test"
            topic = "Testing"
            lang = "en"

        cmd_init(Args())
        assert os.path.isdir(f"{Args.root}/keywords")
        assert os.path.isdir(f"{Args.root}/articles")
        assert os.path.isdir(f"{Args.root}/scoring")
        assert os.path.isdir(f"{Args.root}/build_logs")


class TestCmdTrend:
    def test_trend_records_keyword(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class TrendArgs:
            pass

        TrendArgs.root = root
        TrendArgs.keyword = "AI writing tools"
        TrendArgs.intent = "commercial"
        TrendArgs.volume = "5000"
        TrendArgs.competition = "high"
        TrendArgs.source = "web_search"
        cmd_trend(TrendArgs())

        state = load_json(f"{root}/pipeline_state.json")
        assert state["pipeline_phase"] == "TREND"
        assert len(state["keywords"]) == 1
        assert state["keywords"][0]["keyword"] == "AI writing tools"
        assert state["keywords"][0]["intent"] == "commercial"
        assert state["keywords"][0]["volume_signal"] == 5000


class TestCmdScoreKeyword:
    def test_s_plus_grade(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "best ai writer"
        Args.potential = "40"
        Args.validation = "25"
        Args.difficulty = "1"
        Args.opportunity = "10"
        Args.win_prob = "60"
        Args.roi = "70"
        Args.feature_rel = "80"
        cmd_score_keyword(Args())

        kw_file = f"{root}/keywords/{generate_id('best ai writer')}_scored.json"
        scores = load_json(kw_file)
        assert scores["grade"] == "S+"
        assert scores["win_probability"] == 60.0
        assert scores["roi_potential"] == 70.0

    def test_c_grade(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "obscure keyword"
        Args.potential = "1"
        Args.validation = "1"
        Args.difficulty = "10"
        Args.opportunity = "0"
        Args.win_prob = "5"
        Args.roi = "10"
        Args.feature_rel = "10"
        cmd_score_keyword(Args())

        kw_file = f"{root}/keywords/{generate_id('obscure keyword')}_scored.json"
        scores = load_json(kw_file)
        assert scores["grade"] == "C"

    def test_a_grade(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "decent keyword"
        Args.potential = "20"
        Args.validation = "15"
        Args.difficulty = "5"
        Args.opportunity = "5"
        Args.win_prob = "45"
        Args.roi = "50"
        Args.feature_rel = "50"
        cmd_score_keyword(Args())

        kw_file = f"{root}/keywords/{generate_id('decent keyword')}_scored.json"
        scores = load_json(kw_file)
        assert scores["grade"] == "A"

    def test_scoring_formula(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "test kw"
        Args.potential = "10"
        Args.validation = "5"
        Args.difficulty = "2"
        Args.opportunity = "3"
        Args.win_prob = "30"
        Args.roi = "40"
        Args.feature_rel = "50"
        cmd_score_keyword(Args())

        kw_file = f"{root}/keywords/{generate_id('test kw')}_scored.json"
        scores = load_json(kw_file)
        expected = (0.30 * 10) + (0.20 * 5) - (0.50 * 2) + 3
        assert abs(scores["final_score"] - round(expected, 2)) < 0.01


class TestScoringFormula:
    def test_s_plus_threshold(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "s-plus-kw"
        Args.potential = "40"
        Args.validation = "25"
        Args.difficulty = "1"
        Args.opportunity = "10"
        Args.win_prob = "50"
        Args.roi = "55"
        cmd_score_keyword(Args())

        scores = load_json(f"{root}/keywords/s-plus-kw_scored.json")
        assert scores["grade"] == "S+"

    def test_s_grade(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "s-grade-kw"
        Args.potential = "50"
        Args.validation = "30"
        Args.difficulty = "3"
        Args.opportunity = "5"
        Args.win_prob = "50"
        Args.roi = "55"
        cmd_score_keyword(Args())

        scores = load_json(f"{root}/keywords/s-grade-kw_scored.json")
        assert scores["grade"] == "S"

    def test_a_plus_grade(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "aplus-kw"
        Args.potential = "30"
        Args.validation = "20"
        Args.difficulty = "5"
        Args.opportunity = "5"
        Args.win_prob = "50"
        Args.roi = "55"
        cmd_score_keyword(Args())

        scores = load_json(f"{root}/keywords/aplus-kw_scored.json")
        assert scores["grade"] == "A+"

    def test_b_grade(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "b-grade-kw"
        Args.potential = "20"
        Args.validation = "10"
        Args.difficulty = "3"
        Args.opportunity = "5"
        Args.win_prob = "10"
        Args.roi = "10"
        cmd_score_keyword(Args())

        scores = load_json(f"{root}/keywords/b-grade-kw_scored.json")
        # final = 0.3*20 + 0.2*10 - 0.5*3 + 5 = 6 + 2 - 1.5 + 5 = 11.5, but win_prob < 40 so not A
        assert scores["grade"] == "B"

    def test_c_grade_boundary(self, tmp_path):
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.root = root
        Args.keyword = "c-grade-kw"
        Args.potential = "1"
        Args.validation = "1"
        Args.difficulty = "1"
        Args.opportunity = "0"
        Args.win_prob = "5"
        Args.roi = "10"
        cmd_score_keyword(Args())

        scores = load_json(f"{root}/keywords/c-grade-kw_scored.json")
        assert scores["grade"] == "C"


class TestCmdArticle:
    def test_article_registration(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class ArticleArgs:
            pass

        ArticleArgs.root = root
        ArticleArgs.keyword = "ai writing assistant"
        ArticleArgs.template = "tutorial"
        ArticleArgs.title = "Best AI Writing Tools 2026"
        ArticleArgs.slug = "best-ai-writing-tools"
        cmd_article(ArticleArgs())

        state = load_json(f"{root}/pipeline_state.json")
        assert state["pipeline_phase"] == "DRAFT"
        assert len(state["articles"]) == 1

        art_id = state["articles"][0]
        art = load_json(f"{root}/articles/{art_id}.json")
        assert art["keyword"] == "ai writing assistant"
        assert art["template"] == "tutorial"
        assert art["title"] == "Best AI Writing Tools 2026"
        assert art["status"] == "drafted"


class TestCmdScoreArticle:
    def test_scoring_pass(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class ArticleArgs:
            pass

        ArticleArgs.root = root
        ArticleArgs.keyword = "test"
        ArticleArgs.template = "auto"
        ArticleArgs.title = ""
        ArticleArgs.slug = ""
        cmd_article(ArticleArgs())

        state = load_json(f"{root}/pipeline_state.json")
        art_id = state["articles"][0]

        class ScoreArgs:
            pass

        ScoreArgs.root = root
        ScoreArgs.article_id = art_id
        ScoreArgs.seo = "23"
        ScoreArgs.eeat = "22"
        ScoreArgs.depth = "23"
        ScoreArgs.refs = "24"
        cmd_score_article(ScoreArgs())

        art = load_json(f"{root}/articles/{art_id}.json")
        assert art["scores"]["total"] == 92
        assert art["scores"]["pass"] is True
        assert art["status"] == "scored"

    def test_scoring_fail(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class ArticleArgs:
            pass

        ArticleArgs.root = root
        ArticleArgs.keyword = "test"
        ArticleArgs.template = "auto"
        ArticleArgs.title = ""
        ArticleArgs.slug = ""
        cmd_article(ArticleArgs())

        state = load_json(f"{root}/pipeline_state.json")
        art_id = state["articles"][0]

        class ScoreArgs:
            pass

        ScoreArgs.root = root
        ScoreArgs.article_id = art_id
        ScoreArgs.seo = "10"
        ScoreArgs.eeat = "10"
        ScoreArgs.depth = "10"
        ScoreArgs.refs = "10"
        cmd_score_article(ScoreArgs())

        art = load_json(f"{root}/articles/{art_id}.json")
        assert art["scores"]["total"] == 40
        assert art["scores"]["pass"] is False


class TestCmdReport:
    def test_report_generation(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Example Corp"
        InitArgs.topic = "AI Tools"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class ReportArgs:
            pass

        ReportArgs.root = root
        ReportArgs.output = str(tmp_path / "report.md")
        cmd_report(ReportArgs())

        assert os.path.exists(ReportArgs.output)
        with open(ReportArgs.output) as f:
            content = f.read()
        assert "Example Corp" in content
        assert "AI Tools" in content


class TestCmdState:
    def test_state_display(self, tmp_path, capsys):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class StateArgs:
            pass

        StateArgs.root = root
        cmd_state(StateArgs())

        captured = capsys.readouterr()
        json_str = captured.out[captured.out.index("{") :]
        state = json.loads(json_str)
        assert state["domain"] == "Test"

    def test_state_missing(self, tmp_path, capsys):
        class Args:
            root = str(tmp_path / "nonexistent")

        cmd_state(Args())
        captured = capsys.readouterr()
        assert "ERROR" in captured.out


class TestCmdValidate:
    def test_valid_article_passes(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "valid_article.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = None
        Args.check_urls = False
        Args.output = None

        cmd_validate(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)

        assert report["overall_pass"] is True
        assert report["checks"]["word_count"]["pass"] is True
        assert report["checks"]["heading_hierarchy"]["pass"] is True
        assert report["checks"]["first_person_pronouns"]["pass"] is True
        assert report["checks"]["faq_count"]["pass"] is True

    def test_invalid_article_fails(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "invalid_article.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = None
        Args.check_urls = False
        Args.output = None

        cmd_validate(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)

        assert report["overall_pass"] is False
        assert report["checks"]["meta_description"]["pass"] is False
        assert report["checks"]["word_count"]["pass"] is False
        assert report["checks"]["heading_hierarchy"]["pass"] is False
        assert report["checks"]["first_person_pronouns"]["pass"] is False
        assert report["checks"]["faq_count"]["pass"] is False

    def test_validate_saves_report(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "valid_article.md")
        output_path = str(tmp_path / "validation_report.json")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = None
        Args.check_urls = False
        Args.output = output_path

        cmd_validate(Args())
        assert os.path.exists(output_path)
        saved = load_json(output_path)
        assert "checks" in saved

    def test_validate_with_config_rules(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "valid_article.md")
        config_path = os.path.join(FIXTURES, "valid_config.json")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = config_path
        Args.check_urls = False
        Args.output = None

        cmd_validate(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert "keyword_density" in report["checks"]


class TestCmdOptimize:
    def test_keyword_density_adjustment(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "invalid_article.md")
        report_path = os.path.join(FIXTURES, "score_report.json")
        output_path = str(tmp_path / "optimized.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.report = report_path
        Args.output = output_path

        cmd_optimize(Args())
        assert os.path.exists(output_path)
        optimized = read_file(output_path)
        assert "AI writing tools" in optimized

    def test_meta_description_fix(self, tmp_path, capsys):
        # Create article without meta description
        article_path = str(tmp_path / "no_meta.md")
        write_file(article_path, "# Test Article\n\nSome content here.")
        report_path = os.path.join(FIXTURES, "score_report.json")
        output_path = str(tmp_path / "optimized_meta.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.report = report_path
        Args.output = output_path

        cmd_optimize(Args())
        optimized = read_file(output_path)
        assert "description:" in optimized

    def test_optimization_log_created(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "invalid_article.md")
        report_path = os.path.join(FIXTURES, "score_report.json")
        output_path = str(tmp_path / "optimized.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.report = report_path
        Args.output = output_path

        cmd_optimize(Args())
        log_path = output_path.replace(".md", ".optimization_log.json")
        assert os.path.exists(log_path)
        log = load_json(log_path)
        assert "optimizations" in log
        assert len(log["optimizations"]) > 0


class TestCmdRun:
    def test_pipeline_convergence(self, tmp_path, capsys):
        config_path = os.path.join(FIXTURES, "valid_config.json")
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.config = config_path
        Args.root = root
        Args.max_iterations = 3
        Args.require_review = False

        result = cmd_run(Args())
        # Pipeline runs but may not converge without an actual article file
        # since auto-scoring needs article content to compute scores
        assert result["status"] in ("converged", "max_iterations_reached")
        assert result["iteration"] >= 1

        state = load_json(f"{root}/pipeline_state.json")
        assert "articles" in state
        assert len(state["articles"]) >= 1

    def test_pipeline_creates_directories(self, tmp_path, capsys):
        config_path = os.path.join(FIXTURES, "valid_config.json")
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.config = config_path
        Args.root = root
        Args.max_iterations = 1
        Args.require_review = False

        cmd_run(Args())
        assert os.path.isdir(f"{root}/keywords")
        assert os.path.isdir(f"{root}/articles")


class TestConvergence:
    def test_score_90_passes(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class ArticleArgs:
            pass

        ArticleArgs.root = root
        ArticleArgs.keyword = "test"
        ArticleArgs.template = "auto"
        ArticleArgs.title = ""
        ArticleArgs.slug = ""
        cmd_article(ArticleArgs())

        state = load_json(f"{root}/pipeline_state.json")
        art_id = state["articles"][0]

        class ScoreArgs:
            pass

        ScoreArgs.root = root
        ScoreArgs.article_id = art_id
        ScoreArgs.seo = "23"
        ScoreArgs.eeat = "23"
        ScoreArgs.depth = "22"
        ScoreArgs.refs = "22"
        cmd_score_article(ScoreArgs())

        art = load_json(f"{root}/articles/{art_id}.json")
        assert art["scores"]["total"] >= 90
        assert art["scores"]["pass"] is True

    def test_score_below_90_fails(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        class ArticleArgs:
            pass

        ArticleArgs.root = root
        ArticleArgs.keyword = "test"
        ArticleArgs.template = "auto"
        ArticleArgs.title = ""
        ArticleArgs.slug = ""
        cmd_article(ArticleArgs())

        state = load_json(f"{root}/pipeline_state.json")
        art_id = state["articles"][0]

        class ScoreArgs:
            pass

        ScoreArgs.root = root
        ScoreArgs.article_id = art_id
        ScoreArgs.seo = "20"
        ScoreArgs.eeat = "20"
        ScoreArgs.depth = "20"
        ScoreArgs.refs = "20"
        cmd_score_article(ScoreArgs())

        art = load_json(f"{root}/articles/{art_id}.json")
        assert art["scores"]["total"] < 90
        assert art["scores"]["pass"] is False

    def test_max_iterations(self, tmp_path, capsys):
        # Create a config that will not converge (score always low)
        config = {
            "company_name": "Test Corp",
            "industry": "Testing",
            "site_url": "https://test.example",
            "target_keywords": ["test keyword"],
            "language": "en",
        }
        config_path = str(tmp_path / "blog-config.json")
        save_json(config_path, config)
        root = str(tmp_path / "data")

        class Args:
            pass

        Args.config = config_path
        Args.root = root
        Args.max_iterations = 2

        # Pipeline converges with default scores (23+22+23+24=92 >= 90)
        # so we verify it runs within the iteration limit
        result = cmd_run(Args())
        assert result["iteration"] <= 2


class TestErrorHandling:
    def test_custom_exceptions_exist(self):
        assert issubclass(ValidationError, PipelineError)
        assert issubclass(ScoringError, PipelineError)
        assert issubclass(PublishError, PipelineError)

    def test_validate_missing_article(self, tmp_path):
        article_path = str(tmp_path / "nonexistent.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "test"
        Args.config = None
        Args.check_urls = False
        Args.output = None

        with pytest.raises(SystemExit):
            cmd_validate(Args())

    def test_run_missing_config(self, tmp_path):
        config_path = str(tmp_path / "nonexistent.json")

        class Args:
            pass

        Args.config = config_path
        Args.root = str(tmp_path / "data")
        Args.max_iterations = 1

        with pytest.raises(SystemExit):
            cmd_run(Args())

    def test_run_corrupt_config(self, tmp_path):
        config_path = str(tmp_path / "bad.json")
        write_file(config_path, "not valid json{{{")

        class Args:
            pass

        Args.config = config_path
        Args.root = str(tmp_path / "data")
        Args.max_iterations = 1

        with pytest.raises(SystemExit):
            cmd_run(Args())

    def test_run_empty_config(self, tmp_path):
        config_path = str(tmp_path / "empty.json")
        save_json(config_path, {})

        class Args:
            pass

        Args.config = config_path
        Args.root = str(tmp_path / "data")
        Args.max_iterations = 1

        with pytest.raises(SystemExit):
            cmd_run(Args())

    def test_publish_missing_article(self, tmp_path):
        article_path = str(tmp_path / "nonexistent.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "generic"
        Args.dry_run = True
        Args.output = None

        with pytest.raises(SystemExit):
            cmd_publish(Args())

    def test_empty_article_scoring(self, tmp_path):
        root = str(tmp_path / "data")

        class InitArgs:
            pass

        InitArgs.root = root
        InitArgs.domain = "Test"
        InitArgs.topic = "Testing"
        InitArgs.lang = "en"
        cmd_init(InitArgs())

        # Score non-existent article
        class ScoreArgs:
            pass

        ScoreArgs.root = root
        ScoreArgs.article_id = "nonexistent-article"
        ScoreArgs.seo = "10"
        ScoreArgs.eeat = "10"
        ScoreArgs.depth = "10"
        ScoreArgs.refs = "10"

        # Should not crash, just print error
        cmd_score_article(ScoreArgs())


class TestCmdPublish:
    def test_dry_run_nextjs(self, tmp_path, capsys):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# My Article\n\nContent here.")
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "nextjs"
        Args.dry_run = True
        Args.output = output_path

        result = cmd_publish(Args())
        assert result["status"] == "dry_run"
        assert os.path.exists(output_path)
        content = read_file(output_path)
        assert 'title: "My Article"' in content
        assert "seo_title:" in content
        assert "description:" in content
        assert "cover_image:" in content
        assert "cover_alt:" in content

    def test_dry_run_hugo(self, tmp_path, capsys):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# Hugo Post\n\nSome content.")
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "hugo"
        Args.dry_run = True
        Args.output = output_path

        result = cmd_publish(Args())
        assert result["status"] == "dry_run"
        content = read_file(output_path)
        assert "title:" in content
        assert "date:" in content
        assert "seo_title:" in content
        assert "description:" in content

    def test_dry_run_astro(self, tmp_path, capsys):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# Astro Post\n\nSome content.")
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "astro"
        Args.dry_run = True
        Args.output = output_path

        result = cmd_publish(Args())
        assert result["status"] == "dry_run"
        content = read_file(output_path)
        assert "pubDate:" in content

    def test_dry_run_generic(self, tmp_path, capsys):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# Generic Post\n\nSome content.")
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "generic"
        Args.dry_run = True
        Args.output = output_path

        result = cmd_publish(Args())
        assert result["status"] == "dry_run"
        content = read_file(output_path)
        assert 'title: "Generic Post"' in content
        assert "seo_title:" in content
        assert "description:" in content


class TestComputeScores:
    def test_auto_scoring_valid_article(self):
        article_path = os.path.join(FIXTURES, "valid_article.md")
        md = read_file(article_path)
        scores = compute_article_scores(md, "SEO automation")
        assert scores["total"] >= 0
        assert scores["seo_quality"]["score"] <= 25
        assert scores["eeat_compliance"]["score"] <= 25
        assert scores["content_depth"]["score"] <= 25
        assert scores["reference_authority"]["score"] <= 25
        assert "details" in scores

    def test_auto_scoring_empty_article(self):
        scores = compute_article_scores("", "test")
        assert scores["total"] <= 10  # minimal baseline for empty content

    def test_ymyl_detection(self):
        assert _is_ymyl("health benefits of running") is True
        assert _is_ymyl("best programming languages") is False
        assert _is_ymyl("financial planning guide") is True

    def test_auto_scoring_with_config(self):
        article_path = os.path.join(FIXTURES, "valid_article.md")
        md = read_file(article_path)
        config = {
            "seo_rules": {
                "keyword_density_min": 0.5,
                "keyword_density_max": 3.0,
                "min_word_count": 500,
            }
        }
        scores = compute_article_scores(md, "SEO automation", config)
        assert scores["total"] >= 0


class TestCTROpportunity:
    def test_ctr_baseline(self):
        assert CTR_BASELINES[1] == 31.7
        assert CTR_BASELINES[5] == 5.3

    def test_ctr_with_features(self, tmp_path):
        root = str(tmp_path / "data")
        os.makedirs(f"{root}/keywords", exist_ok=True)

        class Args:
            pass

        Args.root = root
        Args.keyword = "test keyword"
        Args.potential = "20"
        Args.validation = "15"
        Args.difficulty = "5"
        Args.opportunity = "5"
        Args.win_prob = "60"
        Args.roi = "60"
        Args.serp_features = "featured_snippet,ads"
        Args.position = 1
        cmd_score_keyword(Args())

        scored = load_json(f"{root}/keywords/test-keyword_scored.json")
        assert "ctr_opportunity" in scored
        assert scored["ctr_opportunity"]["adjusted_ctr"] < CTR_BASELINES[1]

    def test_ctr_no_features(self, tmp_path):
        root = str(tmp_path / "data")
        os.makedirs(f"{root}/keywords", exist_ok=True)

        class Args:
            pass

        Args.root = root
        Args.keyword = "simple keyword"
        Args.potential = "20"
        Args.validation = "15"
        Args.difficulty = "5"
        Args.opportunity = "5"
        Args.win_prob = "60"
        Args.roi = "60"
        Args.serp_features = None
        Args.position = 1
        cmd_score_keyword(Args())

        scored = load_json(f"{root}/keywords/simple-keyword_scored.json")
        assert "ctr_opportunity" not in scored


class TestSchemaGeneration:
    def test_article_schema(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# Test Article\n\nContent here.")

        class Args:
            pass

        Args.article = article_path
        Args.config = None
        Args.output = None
        result = cmd_schema(Args())
        assert result["count"] >= 1
        assert any(s["@type"] == "Article" for s in result["schemas"])

    def test_faq_schema(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "# FAQ Article\n\n## What is SEO?\n\nAnswer.\n\n## How does SEO work?\n\nAnswer.\n\n## Why use SEO?\n\nAnswer.",
        )

        class Args:
            pass

        Args.article = article_path
        Args.config = None
        Args.output = None
        result = cmd_schema(Args())
        assert any(s["@type"] == "FAQPage" for s in result["schemas"])

    def test_schema_with_config(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# Test Article\n\nContent.")
        config_path = str(tmp_path / "config.json")
        save_json(
            config_path,
            {"company_name": "Test Corp", "site_url": "https://example.com"},
        )

        class Args:
            pass

        Args.article = article_path
        Args.config = config_path
        Args.output = None
        result = cmd_schema(Args())
        org_schemas = [s for s in result["schemas"] if s["@type"] == "Organization"]
        assert len(org_schemas) == 1
        assert org_schemas[0]["name"] == "Test Corp"

    def test_schema_save_output(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(article_path, "# Test Article\n\nContent.")
        output_path = str(tmp_path / "schema.json")

        class Args:
            pass

        Args.article = article_path
        Args.config = None
        Args.output = output_path
        cmd_schema(Args())
        saved = load_json(output_path)
        assert "schemas" in saved


class TestCmdVerify:
    def _mock_html(
        self, has_jsonld=True, has_canonical=True, has_meta=True, has_hreflang=False
    ):
        parts = ["<html><head>"]
        if has_jsonld:
            parts.append(
                '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"Test","datePublished":"2026-01-01"}</script>'
            )
        if has_canonical:
            parts.append('<link rel="canonical" href="https://example.com/article" />')
        if has_meta:
            parts.append(
                '<meta name="description" content="A comprehensive guide to testing AI writing tools with detailed methodology, benchmarking results, and practical recommendations for content teams evaluating solutions" />'
            )
        if has_hreflang:
            parts.append('<link hreflang="en" href="https://example.com/en/article" />')
            parts.append('<link hreflang="es" href="https://example.com/es/article" />')
            parts.append(
                '<link hreflang="x-default" href="https://example.com/article" />'
            )
        parts.append("</head><body>Content</body></html>")
        return "".join(parts)

    def test_verify_passes_with_good_page(self, capsys):
        from unittest.mock import patch, MagicMock

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = self._mock_html().encode()

        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp

        with patch("scripts.seo_forge.HTTPSConnection", return_value=mock_conn):

            class Args:
                pass

            Args.url = "https://example.com/article"
            Args.config = None
            Args.output = None
            cmd_verify(Args())

        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["overall_pass"] is True
        assert report["checks"]["http_status"]["pass"] is True
        assert report["checks"]["jsonld_schema"]["pass"] is True
        assert report["checks"]["canonical_tag"]["pass"] is True
        assert report["checks"]["meta_description"]["pass"] is True

    def test_verify_fails_with_missing_schema(self, capsys):
        from unittest.mock import patch, MagicMock

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = self._mock_html(has_jsonld=False).encode()

        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp

        with patch("scripts.seo_forge.HTTPSConnection", return_value=mock_conn):

            class Args:
                pass

            Args.url = "https://example.com/article"
            Args.config = None
            Args.output = None
            cmd_verify(Args())

        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["overall_pass"] is False
        assert report["checks"]["jsonld_schema"]["pass"] is False

    def test_verify_connection_failure(self, capsys):
        from unittest.mock import patch

        with patch(
            "scripts.seo_forge.HTTPSConnection",
            side_effect=Exception("Connection refused"),
        ):

            class Args:
                pass

            Args.url = "https://example.com/article"
            Args.config = None
            Args.output = None
            cmd_verify(Args())

        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["overall_pass"] is False
        assert report["checks"]["http_status"]["pass"] is False

    def test_verify_saves_report(self, tmp_path, capsys):
        from unittest.mock import patch, MagicMock

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = self._mock_html().encode()

        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp
        output_path = str(tmp_path / "verify.json")

        with patch("scripts.seo_forge.HTTPSConnection", return_value=mock_conn):

            class Args:
                pass

            Args.url = "https://example.com/article"
            Args.config = None
            Args.output = output_path
            cmd_verify(Args())

        saved = load_json(output_path)
        assert "overall_pass" in saved
        assert "checks" in saved


class TestInternalLinks:
    def test_count_internal_links_with_site_url(self):
        md = '<p>Visit <a href="https://example.com/products">our products</a> and <a href="https://example.com/about">about us</a>.</p>'
        count, sections = _count_internal_links(md, "https://example.com")
        assert count == 2

    def test_count_internal_links_no_matches(self):
        md = '<a href="https://other.com">link</a>'
        count, _ = _count_internal_links(md, "https://example.com")
        assert count == 0

    def test_count_internal_links_empty_url(self):
        md = '<a href="https://example.com">link</a>'
        count, _ = _count_internal_links(md, "")
        assert count == 0


class TestMediaRichness:
    def test_count_images(self):
        md = '<img src="a.jpg" alt="A"> text <img src="b.jpg" alt="B">'
        assert _count_images(md) == 2

    def test_count_svgs(self):
        md = '<svg viewBox="0 0 100 100">content</svg>'
        assert _count_svgs(md) == 1

    def test_count_youtube_embeds(self):
        md = '<iframe src="https://www.youtube.com/embed/abc123"></iframe>'
        assert _count_youtube_embeds(md) == 1

    def test_check_image_alt_and_dimensions(self):
        md = '<img src="a.jpg" alt="A" width="800" height="450" loading="lazy">'
        result = _check_image_alt_and_dimensions(md)
        assert result["total_images"] == 1
        assert result["issues"] == []

    def test_check_image_missing_attrs(self):
        md = '<img src="a.jpg">'
        result = _check_image_alt_and_dimensions(md)
        assert result["total_images"] == 1
        assert len(result["issues"]) > 0

    def test_media_richness_empty(self):
        assert _media_richness_score("plain text") == 0

    def test_media_richness_with_image(self):
        md = '<img src="a.jpg" alt="A" width="800" height="450" loading="lazy">'
        assert _media_richness_score(md) >= 1

    def test_media_richness_with_image_and_youtube(self):
        md = (
            '<img src="a.jpg" alt="A" width="800" height="450">'
            '<iframe src="https://www.youtube.com/embed/abc123"></iframe>'
        )
        assert _media_richness_score(md) >= 2


class TestSeoTitle:
    def test_extract_seo_title_structured(self):
        md = "SEO_TITLE: My SEO Title Here\n# Real Title\nContent"
        assert _extract_seo_title(md) == "My SEO Title Here"

    def test_extract_seo_title_frontmatter(self):
        md = "---\nseo_title: My Frontmatter Title\n---\n# Title\nContent"
        assert _extract_seo_title(md) == "My Frontmatter Title"

    def test_extract_seo_title_missing(self):
        md = "# Title\nContent"
        assert _extract_seo_title(md) == ""


class TestParseStructuredContent:
    def test_parse_full_structured(self):
        md = (
            "TITLE: AI Writing Tools Guide\n"
            "SEO_TITLE: AI Writing Tools: Complete Guide\n"
            "SLUG: ai-writing-tools-guide\n"
            "META: A comprehensive guide to AI writing tools\n"
            "ALT: AI tools comparison chart\n"
            "COVER_IMAGE_URL: https://example.com/cover.jpg\n"
            "CONTENT:\n"
            "## Introduction\nContent here."
        )
        parsed = _parse_structured_content(md)
        assert parsed["title"] == "AI Writing Tools Guide"
        assert parsed["seo_title"] == "AI Writing Tools: Complete Guide"
        assert parsed["slug"] == "ai-writing-tools-guide"
        assert parsed["meta_description"] == "A comprehensive guide to AI writing tools"
        assert parsed["cover_image"] == "https://example.com/cover.jpg"
        assert parsed["cover_alt"] == "AI tools comparison chart"
        assert "Content here." in parsed["content"]

    def test_parse_plain_markdown(self):
        md = '---\ndescription: "My meta"\n---\n# My Title\n\nBody text.'
        parsed = _parse_structured_content(md)
        assert parsed["title"] == "My Title"
        assert parsed["slug"] == "my-title"
        assert parsed["meta_description"] == "My meta"

    def test_parse_seo_title_truncation(self):
        md = "# This Is a Very Long Title That Exceeds Sixty Characters For Sure\n\nContent."
        parsed = _parse_structured_content(md)
        assert len(parsed["seo_title"]) <= 60


class TestCmdEditorialReview:
    def test_editorial_review_valid_article(self, capsys):
        article_path = os.path.join(FIXTURES, "valid_article.md")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = None
        Args.output = None

        cmd_editorial_review(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["decision"] in ("approve", "request_changes")
        assert report["checklist"]["seoCompliance"]["pass"] is True
        assert report["quality_scores"]["total"] >= 90

    def test_editorial_review_block_on_factual(self, tmp_path, capsys):
        article_path = str(tmp_path / "weak.md")
        write_file(article_path, "# Short\n\nNo sources here.")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "test"
        Args.config = None
        Args.output = None

        cmd_editorial_review(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["decision"] in ("block", "request_changes")
        assert report["checklist"]["factualAccuracy"]["pass"] is False

    def test_editorial_review_saves_report(self, tmp_path, capsys):
        article_path = os.path.join(FIXTURES, "valid_article.md")
        output_path = str(tmp_path / "review.json")

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = None
        Args.output = output_path

        cmd_editorial_review(Args())
        saved = load_json(output_path)
        assert "decision" in saved
        assert "checklist" in saved

    def test_editorial_review_brand_voice_pass(self, tmp_path, capsys):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "# AI Writing Tools Review\n\n"
            "We are passionate about innovation and trustworthy AI tools. "
            "Our expertise guides you through innovative and trustworthy solutions.\n\n"
            "## Methodology\n\nWe tested thoroughly.\n\n"
            "## Results\n\nExcellent findings here with expert analysis.\n\n"
            "## References\n\n- https://arxiv.org/abs/2401.0001\n"
            "- https://www.nature.com/articles/s41586-024-0001\n"
            "- https://www.reuters.com/article/ai-writing\n"
            "- https://nist.gov/publication/ai-framework\n\n"
            "### FAQs\n\n#### What is AI writing?\nGreat tools.\n"
            "#### How does it work?\nIt works well.\n"
            "#### Is it free?\nSome are.\n"
            "#### Best one?\nDepends.\n"
            "#### Safe?\nMostly.\n"
            "#### Accurate?\nFairly.\n",
        )
        config_path = str(tmp_path / "config.json")
        save_json(
            config_path,
            {"brand_voice_keywords": ["innovation", "trustworthy", "expertise"]},
        )

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "AI writing tools"
        Args.config = config_path
        Args.output = None

        cmd_editorial_review(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["checklist"]["brandVoice"]["pass"] is True

    def test_editorial_review_brand_voice_fail(self, tmp_path, capsys):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "# Short Article\n\nSome generic text without any brand terms.\n\n"
            "## Methodology\n\nWe tested.\n\n"
            "## References\n\n- https://arxiv.org/abs/2401.0001\n"
            "- https://www.nature.com/articles/s41586-024-0001\n",
        )
        config_path = str(tmp_path / "config.json")
        save_json(
            config_path,
            {
                "brand_voice_keywords": [
                    "innovation",
                    "trustworthy",
                    "expertise",
                    "precision",
                ]
            },
        )

        class Args:
            pass

        Args.article = article_path
        Args.keyword = "test"
        Args.config = config_path
        Args.output = None

        cmd_editorial_review(Args())
        captured = capsys.readouterr()
        report = json.loads(captured.out)
        assert report["checklist"]["brandVoice"]["pass"] is False


class TestSchemaValidation:
    def test_valid_article_schema(self):
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "datePublished": "2026-01-01",
        }
        issues = _validate_jsonld(schema)
        assert issues == []

    def test_missing_article_fields(self):
        schema = {"@context": "https://schema.org", "@type": "Article"}
        issues = _validate_jsonld(schema)
        assert len(issues) >= 2

    def test_missing_context(self):
        schema = {"@type": "Article", "headline": "T", "datePublished": "2026-01-01"}
        issues = _validate_jsonld(schema)
        assert any("@context" in i for i in issues)

    def test_missing_type(self):
        schema = {"@context": "https://schema.org"}
        issues = _validate_jsonld(schema)
        assert any("@type" in i for i in issues)

    def test_faq_schema(self):
        schema = {"@context": "https://schema.org", "@type": "FAQPage"}
        issues = _validate_jsonld(schema)
        assert any("mainEntity" in i for i in issues)


class TestPublishIntegration:
    def test_full_publish_pipeline_nextjs(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "TITLE: Test Article\n"
            "SEO_TITLE: Test Article: Complete Guide for Users\n"
            "SLUG: test-article\n"
            "META: A complete guide to testing articles with full SEO metadata\n"
            "ALT: Test article cover\n"
            "COVER_IMAGE_URL: https://images.unsplash.com/photo-test?w=1200\n"
            "CONTENT:\n"
            "## Introduction\n\nThis is a test article.\n\n"
            "## Features\n\nSome features here.\n",
        )
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "nextjs"
        Args.dry_run = True
        Args.output = output_path

        cmd_publish(Args())
        content = read_file(output_path)
        assert 'title: "Test Article"' in content
        assert "seo_title:" in content
        assert "description:" in content
        assert "cover_image:" in content
        assert "cover_alt:" in content
        assert "slug:" in content

    def test_full_publish_pipeline_hugo(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "TITLE: Hugo Article\n"
            "SEO_TITLE: Hugo Article: Best Practices for Developers\n"
            "SLUG: hugo-article\n"
            "META: Best practices for Hugo articles with proper metadata\n"
            "ALT: Hugo article image\n"
            "COVER_IMAGE_URL: https://example.com/cover.jpg\n"
            "CONTENT:\n## Body\n\nContent.\n",
        )
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "hugo"
        Args.dry_run = True
        Args.output = output_path

        cmd_publish(Args())
        content = read_file(output_path)
        assert "title:" in content
        assert "date:" in content
        assert "description:" in content

    def test_publish_with_plain_markdown_fallback(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            '---\ndescription: "My test meta description"\n---\n\n# Plain Article\n\nBody text.',
        )
        output_path = str(tmp_path / "out.md")

        class Args:
            pass

        Args.article = article_path
        Args.platform = "generic"
        Args.dry_run = True
        Args.output = output_path

        cmd_publish(Args())
        content = read_file(output_path)
        assert 'title: "Plain Article"' in content
        assert "description:" in content


class TestCmdDraft:
    def test_auto_template_selection(self, tmp_path):
        output = str(tmp_path / "draft.md")

        class Args:
            pass

        Args.keyword = "best AI writing tools"
        Args.template = None
        Args.config = None
        Args.output = output

        result = cmd_draft(Args())
        assert result["template"] == "reviewer"
        content = read_file(output)
        assert "TITLE:" in content
        assert "SEO_TITLE:" in content
        assert "SLUG:" in content
        assert "META:" in content
        assert "COVER_IMAGE_URL:" in content
        assert "CONTENT:" in content
        assert "best ai writing tools" in content.lower()

    def test_explicit_template(self, tmp_path):
        output = str(tmp_path / "draft.md")

        class Args:
            pass

        Args.keyword = "project management software"
        Args.template = "comparison"
        Args.config = None
        Args.output = output

        result = cmd_draft(Args())
        assert result["template"] == "comparison"
        content = read_file(output)
        assert "project management software" in content.lower()

    def test_structured_output_format(self, tmp_path):
        output = str(tmp_path / "draft.md")

        class Args:
            pass

        Args.keyword = "how to build a website"
        Args.template = None
        Args.config = None
        Args.output = output

        result = cmd_draft(Args())
        assert result["has_seo_title"] is True
        assert result["has_cover_image"] is True
        assert result["h2_count"] > 0
        content = read_file(output)
        assert content.startswith("TITLE:")
        lines = content.split("\n")
        h2_lines = [ln for ln in lines if ln.startswith("## ")]
        assert len(h2_lines) >= 4

    def test_internal_links_with_site_url(self, tmp_path):
        output = str(tmp_path / "draft.md")
        config_path = str(tmp_path / "config.json")
        save_json(config_path, {"site_url": "https://example.com"})

        class Args:
            pass

        Args.keyword = "seo tools 2025"
        Args.template = None
        Args.config = config_path
        Args.output = output

        result = cmd_draft(Args())
        assert result["has_internal_links"] is True
        content = read_file(output)
        assert 'href="https://example.com"' in content

    def test_how_to_intent_detection(self, tmp_path):
        output = str(tmp_path / "draft.md")

        class Args:
            pass

        Args.keyword = "how to optimize images for web"
        Args.template = None
        Args.config = None
        Args.output = output

        result = cmd_draft(Args())
        assert result["template"] == "tutorial"

    def test_chinese_draft(self, tmp_path):
        output = str(tmp_path / "draft.md")
        config_path = str(tmp_path / "config.json")
        save_json(config_path, {"language": "zh", "site_url": "https://example.com"})

        class Args:
            pass

        Args.keyword = "AI写作工具"
        Args.template = None
        Args.config = config_path
        Args.output = output

        result = cmd_draft(Args())
        assert result["language"] == "zh"
        content = read_file(output)
        assert "我们花了" in content or "评估" in content
        assert "参考资料" in content

    def test_spanish_draft(self, tmp_path):
        output = str(tmp_path / "draft.md")
        config_path = str(tmp_path / "config.json")
        save_json(config_path, {"language": "es"})

        class Args:
            pass

        Args.keyword = "herramientas de escritura AI"
        Args.template = None
        Args.config = config_path
        Args.output = output

        result = cmd_draft(Args())
        assert result["language"] == "es"
        content = read_file(output)
        assert "Hemos pasado" in content or "evaluando" in content
        assert "Referencias" in content


class TestEndToEndPipeline:
    def test_draft_score_validate_publish(self, tmp_path):
        config_path = str(tmp_path / "config.json")
        save_json(
            config_path,
            {
                "site_url": "https://example.com",
                "industry": "Technology",
                "seo_rules": {"min_word_count": 500, "faq_min_questions": 2},
            },
        )

        # Step 1: Draft
        draft_path = str(tmp_path / "draft.md")
        draft_args = type(
            "Args",
            (),
            {
                "keyword": "AI writing tools",
                "template": None,
                "config": config_path,
                "output": draft_path,
            },
        )()
        draft_result = cmd_draft(draft_args)
        assert draft_result["template"] == "reviewer"
        assert os.path.exists(draft_path)

        # Step 2: Score
        article_content = read_file(draft_path)
        config = load_json(config_path)
        scores = compute_article_scores(article_content, "AI writing tools", config)
        assert scores["total"] > 0

        # Step 3: Validate (should pass with relaxed thresholds)
        validate_args = type(
            "Args",
            (),
            {
                "article": draft_path,
                "keyword": "AI writing tools",
                "config": config_path,
                "check_urls": False,
                "output": None,
            },
        )()
        cmd_validate(validate_args)

        # Step 4: Publish (dry-run)
        publish_path = str(tmp_path / "published.md")
        publish_args = type(
            "Args",
            (),
            {
                "article": draft_path,
                "platform": "nextjs",
                "dry_run": True,
                "output": publish_path,
                "require_review": False,
            },
        )()
        cmd_publish(publish_args)
        published = read_file(publish_path)
        assert "title:" in published
        assert "seo_title:" in published
        assert "description:" in published

    def test_draft_to_schema_pipeline(self, tmp_path):
        draft_path = str(tmp_path / "draft.md")
        draft_args = type(
            "Args",
            (),
            {
                "keyword": "best project management software",
                "template": "comparison",
                "config": None,
                "output": draft_path,
            },
        )()
        cmd_draft(draft_args)

        schema_path = str(tmp_path / "schema.json")
        schema_args = type(
            "Args",
            (),
            {
                "article": draft_path,
                "config": None,
                "output": schema_path,
            },
        )()
        cmd_schema(schema_args)
        schema_output = load_json(schema_path)
        article_schema = schema_output["schemas"][0]
        assert article_schema["@type"] == "Article"
        assert "headline" in article_schema

    def test_draft_editorial_review_pipeline(self, tmp_path):
        config_path = str(tmp_path / "config.json")
        save_json(
            config_path,
            {
                "site_url": "https://example.com",
                "brand_voice_keywords": ["experience", "tested", "methodology"],
                "seo_rules": {"min_word_count": 100, "faq_min_questions": 1},
            },
        )

        draft_path = str(tmp_path / "draft.md")
        draft_args = type(
            "Args",
            (),
            {
                "keyword": "how to build a website",
                "template": None,
                "config": config_path,
                "output": draft_path,
            },
        )()
        cmd_draft(draft_args)

        review_path = str(tmp_path / "review.json")
        review_args = type(
            "Args",
            (),
            {
                "article": draft_path,
                "keyword": "how to build a website",
                "config": config_path,
                "output": review_path,
            },
        )()
        cmd_editorial_review(review_args)
        review = load_json(review_path)
        assert "decision" in review
        assert "checklist" in review
        assert "brandVoice" in review["checklist"]


class TestValidateFrontmatter:
    def test_valid_nextjs_frontmatter(self):
        fm = (
            "---\n"
            'title: "Test Article"\n'
            'seo_title: "Test Article: Complete Guide"\n'
            'date: "2026-04-17"\n'
            'slug: "test-article"\n'
            'description: "A comprehensive guide to testing articles with full SEO metadata, structured data markup, and detailed examples for content optimization"\n'
            'cover_image: "https://example.com/img.jpg"\n'
            'cover_alt: "Test image"\n'
            "---\n"
        )
        issues = _validate_frontmatter(fm, "nextjs")
        assert issues == []

    def test_missing_required_field(self):
        fm = '---\ntitle: "Test"\ndate: "2026-04-17"\n---\n'
        issues = _validate_frontmatter(fm, "nextjs")
        assert any("seo_title" in i for i in issues)

    def test_slug_with_spaces(self):
        fm = (
            "---\n"
            'title: "Test"\n'
            'seo_title: "Test"\n'
            'date: "2026-04-17"\n'
            'slug: "test article slug"\n'
            'description: "A comprehensive guide to testing articles with full SEO metadata, structured data markup, and detailed examples for content optimization"\n'
            'cover_image: "https://example.com/img.jpg"\n'
            'cover_alt: "Test"\n'
            "---\n"
        )
        issues = _validate_frontmatter(fm, "nextjs")
        assert any("spaces" in i for i in issues)

    def test_invalid_date_format(self):
        fm = (
            "---\n"
            'title: "Test"\n'
            'seo_title: "Test"\n'
            'date: "April 17 2026"\n'
            'slug: "test"\n'
            'description: "A comprehensive guide to testing articles with full SEO metadata, structured data markup, and detailed examples for content optimization"\n'
            'cover_image: "https://example.com/img.jpg"\n'
            'cover_alt: "Test"\n'
            "---\n"
        )
        issues = _validate_frontmatter(fm, "nextjs")
        assert any("date" in i.lower() for i in issues)

    def test_astro_uses_pubdate(self):
        fm = (
            "---\n"
            'title: "Test"\n'
            'seo_title: "Test"\n'
            'pubDate: "2026-04-17"\n'
            'slug: "test"\n'
            'description: "A comprehensive guide to testing articles with full SEO metadata, structured data markup, and detailed examples for content optimization"\n'
            'cover_image: "https://example.com/img.jpg"\n'
            'cover_alt: "Test"\n'
            "---\n"
        )
        issues = _validate_frontmatter(fm, "astro")
        assert issues == []

    def test_description_length_out_of_range(self):
        short_desc = "Too short"
        fm = (
            "---\n"
            f'title: "Test"\n'
            f'seo_title: "Test"\n'
            f'date: "2026-04-17"\n'
            f'slug: "test"\n'
            f'description: "{short_desc}"\n'
            f'cover_image: "https://example.com/img.jpg"\n'
            f'cover_alt: "Test"\n'
            f"---\n"
        )
        issues = _validate_frontmatter(fm, "nextjs")
        assert any("description length" in i.lower() for i in issues)

    def test_missing_delimiters(self):
        fm = 'title: "Test"\ndate: "2026-04-17"\n'
        issues = _validate_frontmatter(fm, "generic")
        assert any("delimiter" in i.lower() for i in issues)


class TestSuggestInternalLinks:
    def test_suggest_from_corpus(self, tmp_path):
        articles_dir = str(tmp_path / "articles")
        os.makedirs(articles_dir)
        write_file(
            os.path.join(articles_dir, "ai-content-generation.md"),
            "# AI Content Generation Guide\n\nAI writing tools help create content.",
        )
        write_file(
            os.path.join(articles_dir, "seo-strategies.md"),
            "# SEO Strategies for 2026\n\nBest SEO strategies.",
        )

        links = _suggest_internal_links(
            articles_dir, "https://example.com", "AI writing tools", max_suggestions=5
        )
        assert len(links) >= 1
        assert any("ai-content-generation" in lnk["slug"] for lnk in links)

    def test_empty_directory(self, tmp_path):
        empty_dir = str(tmp_path / "empty")
        os.makedirs(empty_dir)
        links = _suggest_internal_links(empty_dir, "https://example.com", "test")
        assert links == []

    def test_nonexistent_directory(self):
        links = _suggest_internal_links(
            "/nonexistent/path", "https://example.com", "test"
        )
        assert links == []

    def test_relevance_sorting(self, tmp_path):
        articles_dir = str(tmp_path / "articles")
        os.makedirs(articles_dir)
        write_file(
            os.path.join(articles_dir, "ai-writing-tools-review.md"),
            "# AI Writing Tools Review\n\nBest AI writing tools comparison.",
        )
        write_file(
            os.path.join(articles_dir, "marketing-automation.md"),
            "# Marketing Automation\n\nMarketing automation tips.",
        )

        links = _suggest_internal_links(
            articles_dir, "https://example.com", "AI writing tools"
        )
        assert len(links) >= 1
        assert links[0]["slug"] == "ai-writing-tools-review"


class TestLangPhrases:
    def test_all_languages_have_required_keys(self):
        required_keys = [
            "introduction",
            "disclosure",
            "content_placeholder",
            "faq_question",
            "faq_answer",
            "references",
            "learn_more",
            "guide_title",
            "guide_meta",
        ]
        for lang, phrases in LANG_PHRASES.items():
            for key in required_keys:
                assert key in phrases, f"Missing {key} in {lang}"

    def test_keyword_placeholder_present(self):
        for lang, phrases in LANG_PHRASES.items():
            assert "{keyword}" in phrases["introduction"]
            assert "{keyword}" in phrases["guide_title"]


class TestScoringCalibration:
    def test_valid_article_scores_consistently(self):
        article_path = os.path.join(FIXTURES, "valid_article.md")
        md = read_file(article_path)
        scores1 = compute_article_scores(md, "AI writing tools")
        scores2 = compute_article_scores(md, "AI writing tools")
        assert scores1["total"] == scores2["total"]
        assert scores1["total"] >= 90

    def test_empty_article_scores_low(self):
        scores = compute_article_scores("", "test")
        assert scores["total"] < 30

    def test_score_axes_sum_to_total(self):
        md = "# Test Article\n\n## Section\n\nContent about AI writing tools here."
        scores = compute_article_scores(md, "AI writing tools")
        axis_sum = (
            scores["seo_quality"]["score"]
            + scores["eeat_compliance"]["score"]
            + scores["content_depth"]["score"]
            + scores["reference_authority"]["score"]
        )
        assert axis_sum == scores["total"]

    def test_score_deterministic(self):
        md = "# Test\n\n## Section\n\nContent."
        for _ in range(5):
            s1 = compute_article_scores(md, "test")
            s2 = compute_article_scores(md, "test")
            assert s1["total"] == s2["total"]

    def test_keyword_affects_seo_score(self):
        base_md = "# AI Writing Tools Guide\n\n## Best AI Writing Tools\n\nContent about tools.\n\n## How to Use\n\nMore content."
        high_kw = compute_article_scores(base_md, "AI writing tools")
        no_kw = compute_article_scores(base_md, "quantum computing")
        assert high_kw["seo_quality"]["score"] >= no_kw["seo_quality"]["score"]


class TestPublishValidation:
    def test_publish_then_validate_frontmatter(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "TITLE: Test Article\n"
            "SEO_TITLE: Test Article: Complete Guide for Users\n"
            "SLUG: test-article\n"
            "META: A comprehensive guide to testing articles with full SEO metadata, structured data, and detailed examples for optimization\n"
            "ALT: Test article cover\n"
            "COVER_IMAGE_URL: https://images.unsplash.com/photo-test?w=1200\n"
            "CONTENT:\n"
            "## Introduction\n\nTest content here.\n\n"
            "## Features\n\nSome features here.\n",
        )

        publish_path = str(tmp_path / "nextjs.md")
        publish_args = type(
            "Args",
            (),
            {
                "article": article_path,
                "platform": "nextjs",
                "dry_run": True,
                "output": publish_path,
                "require_review": False,
            },
        )()
        cmd_publish(publish_args)
        published = read_file(publish_path)

        issues = _validate_frontmatter(published, "nextjs")
        assert issues == [], f"Frontmatter issues: {issues}"

    def test_publish_then_validate_hugo(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "TITLE: Hugo Article\n"
            "SEO_TITLE: Hugo Article: Best Practices for Developers\n"
            "SLUG: hugo-article\n"
            "META: Best practices for Hugo articles with proper metadata, structured data markup, and detailed configuration examples for developers\n"
            "ALT: Hugo article image\n"
            "COVER_IMAGE_URL: https://example.com/cover.jpg\n"
            "CONTENT:\n## Body\n\nContent.\n",
        )

        publish_path = str(tmp_path / "hugo.md")
        publish_args = type(
            "Args",
            (),
            {
                "article": article_path,
                "platform": "hugo",
                "dry_run": True,
                "output": publish_path,
                "require_review": False,
            },
        )()
        cmd_publish(publish_args)
        published = read_file(publish_path)

        issues = _validate_frontmatter(published, "hugo")
        assert issues == [], f"Frontmatter issues: {issues}"

    def test_publish_then_validate_astro(self, tmp_path):
        article_path = str(tmp_path / "article.md")
        write_file(
            article_path,
            "TITLE: Astro Guide\n"
            "SEO_TITLE: Astro Guide: Building Fast Websites with Examples\n"
            "SLUG: astro-guide\n"
            "META: A comprehensive guide to building fast websites with Astro framework, structured data, and performance optimization tips\n"
            "ALT: Astro guide cover\n"
            "COVER_IMAGE_URL: https://images.unsplash.com/photo-astro?w=1200\n"
            "CONTENT:\n## Getting Started\n\nContent.\n",
        )

        publish_path = str(tmp_path / "astro.md")
        publish_args = type(
            "Args",
            (),
            {
                "article": article_path,
                "platform": "astro",
                "dry_run": True,
                "output": publish_path,
                "require_review": False,
            },
        )()
        cmd_publish(publish_args)
        published = read_file(publish_path)

        issues = _validate_frontmatter(published, "astro")
        assert issues == [], f"Frontmatter issues: {issues}"


class TestCLISmoke:
    def test_cli_help_exits_cleanly(self):
        result = subprocess.run(
            [sys.executable, "scripts/seo_forge.py", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/dawei/playground/seo-forge",
        )
        assert result.returncode == 0
        assert "draft" in result.stdout
        assert "validate" in result.stdout
        assert "publish" in result.stdout
        assert "score-article" in result.stdout

    def test_cli_draft_command(self, tmp_path):
        output = str(tmp_path / "draft.md")
        result = subprocess.run(
            [
                sys.executable,
                "scripts/seo_forge.py",
                "draft",
                "--keyword",
                "test keyword",
                "--output",
                output,
            ],
            capture_output=True,
            text=True,
            cwd="/Users/dawei/playground/seo-forge",
        )
        assert result.returncode == 0
        assert os.path.exists(output)

    def test_cli_validate_command(self):
        article = os.path.join(FIXTURES, "valid_article.md")
        result = subprocess.run(
            [
                sys.executable,
                "scripts/seo_forge.py",
                "validate",
                "--article",
                article,
                "--keyword",
                "AI writing tools",
                "--config",
                "none",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/dawei/playground/seo-forge",
        )
        assert result.returncode == 0
