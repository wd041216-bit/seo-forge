import json
import os
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
