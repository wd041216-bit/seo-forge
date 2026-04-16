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
    generate_id,
    ts,
    load_json,
)


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
