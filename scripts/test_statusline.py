"""Tests for the ticket-loop status line script.

Run from the repo root: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import importlib.machinery
import importlib.util
import os
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
_loader = importlib.machinery.SourceFileLoader(
    "statusline", os.path.join(HERE, "ticket-loop-statusline"))
_spec = importlib.util.spec_from_loader("statusline", _loader)
sl = importlib.util.module_from_spec(_spec)
_loader.exec_module(sl)

NOW = datetime(2026, 11, 6, 20, 0, tzinfo=timezone.utc)
STATUS = ("#121 · test queue · running the browser suite · since 14:02 · 0/1 shipped"
          " · Opus/med · Haiku/usual opt-in · Opus/low · Sonnet · Opus/high")
ROLLING = "Rolling: 14.3% of the plan's weekly usage per day."
REPORT = {"usage_source": "live",
          "week": {"percent_used": 43.0, "resets_at": "2026-11-10T07:00:00+00:00"},
          "today": {"percent_of_week": 9.3}}
FRESH = NOW.timestamp() - 60


class StatusFile(unittest.TestCase):
    def test_parses_the_fields(self):
        s = sl.parse_status(STATUS)
        self.assertEqual(s["ticket"], "#121")
        self.assertEqual(s["step"], "test queue")
        self.assertEqual(s["now"], "running the browser suite")
        self.assertEqual(s["since"], "14:02")
        self.assertEqual((s["shipped"], s["total"]), (0, 1))
        self.assertEqual(s["roles"][1], "Haiku/usual opt-in")

    def test_rejects_a_bad_line(self):
        self.assertIsNone(sl.parse_status("garbage"))


class Render(unittest.TestCase):
    def test_run_going_rolling(self):
        self.assertEqual(
            sl.render(STATUS, FRESH, NOW, REPORT, ROLLING),
            "#121 test queue · Tickets [░░░░░░░░░░] 0/1 · Usage [████████░░] 43.0%/57.2% d4"
            " · Opus/med · Haiku/usual opt-in · Opus/low · Sonnet · Opus/high")

    def test_per_day_usage(self):
        line = sl.render(None, None, NOW, REPORT, "14.3% of the plan's weekly usage per day.")
        self.assertEqual(line, "Usage [███████░░░] 9.3%/14.3% today")

    def test_no_status_file_prints_usage_only(self):
        self.assertEqual(sl.render(None, None, NOW, REPORT, ROLLING),
                         "Usage [████████░░] 43.0%/57.2% d4")

    def test_hand_back_is_no_run(self):
        done = STATUS.replace("test queue", "hand-back")
        self.assertEqual(sl.render(done, FRESH, NOW, REPORT, ROLLING),
                         "Usage [████████░░] 43.0%/57.2% d4")

    def test_stale_file_is_no_run(self):
        old = NOW.timestamp() - 13 * 3600
        self.assertEqual(sl.render(STATUS, old, NOW, REPORT, ROLLING),
                         "Usage [████████░░] 43.0%/57.2% d4")

    def test_no_usage_and_no_run_prints_nothing(self):
        self.assertEqual(sl.render(None, None, NOW, None, ROLLING), "")
        self.assertEqual(sl.render(None, None, NOW, {"usage_source": "unavailable"}, ROLLING), "")

    def test_run_going_without_usage_drops_the_usage_bar(self):
        self.assertEqual(
            sl.render(STATUS, FRESH, NOW, None, ROLLING),
            "#121 test queue · Tickets [░░░░░░░░░░] 0/1"
            " · Opus/med · Haiku/usual opt-in · Opus/low · Sonnet · Opus/high")

    def test_cap_not_applicable_drops_the_usage_bar(self):
        self.assertEqual(
            sl.render(None, None, NOW, REPORT, "Not applicable: no plan usage to read."), "")

    def test_ticket_bar_rounds_halves_up(self):
        two_of_three = STATUS.replace("0/1 shipped", "2/3 shipped")
        self.assertIn("Tickets [███████░░░] 2/3", sl.render(two_of_three, FRESH, NOW, None, ROLLING))


class StatusPath(unittest.TestCase):
    def test_main_checkout_root(self):
        self.assertEqual(sl.status_path("/r/app/.git"), "/r/app/.ticket-loop-status")

    def test_linked_worktree_uses_the_main_checkout(self):
        # A linked worktree's --git-common-dir is still the main checkout's .git.
        self.assertEqual(sl.status_path("/r/app/.git/"), "/r/app/.ticket-loop-status")

    def test_no_git_dir(self):
        self.assertIsNone(sl.status_path(None))


class UsageCache(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.dir = tempfile.mkdtemp()
        self.cache = os.path.join(self.dir, "usage.json")
        self.spawned = []

    def write_cache(self, age):
        import json
        with open(self.cache, "w") as f:
            json.dump(REPORT, f)
        t = NOW.timestamp() - age
        os.utime(self.cache, (t, t))

    def test_cache_name_is_per_user(self):
        self.assertIn(str(os.getuid()), os.path.basename(sl.cache_path()))

    def test_old_cache_still_prints_and_refreshes_in_the_background(self):
        self.write_cache(600)
        got = sl.read_usage(self.cache, NOW.timestamp(), lambda: self.spawned.append(1))
        self.assertEqual(got, REPORT)
        self.assertEqual(self.spawned, [1])

    def test_fresh_cache_does_not_refresh(self):
        self.write_cache(10)
        got = sl.read_usage(self.cache, NOW.timestamp(), lambda: self.spawned.append(1))
        self.assertEqual(got, REPORT)
        self.assertEqual(self.spawned, [])

    def test_no_cache_returns_nothing_and_refreshes(self):
        got = sl.read_usage(self.cache, NOW.timestamp(), lambda: self.spawned.append(1))
        self.assertIsNone(got)
        self.assertEqual(self.spawned, [1])

    def test_a_refresh_in_progress_is_not_started_again(self):
        self.write_cache(600)
        lock = self.cache + ".lock"
        open(lock, "w").close()
        t = NOW.timestamp() - 5
        os.utime(lock, (t, t))
        sl.read_usage(self.cache, NOW.timestamp(), lambda: self.spawned.append(1))
        self.assertEqual(self.spawned, [])


class BadTimes(unittest.TestCase):
    def test_bad_resets_at_drops_the_usage_bar(self):
        bad = {"usage_source": "live", "week": {"percent_used": 43.0, "resets_at": "soon"}}
        self.assertEqual(sl.render(None, None, NOW, bad, ROLLING), "")

    def test_naive_resets_at_is_utc(self):
        naive = {"usage_source": "live",
                 "week": {"percent_used": 43.0, "resets_at": "2026-11-10T07:00:00"}}
        self.assertEqual(sl.render(None, None, NOW, naive, ROLLING),
                         "Usage [████████░░] 43.0%/57.2% d4")

    def test_parse_time(self):
        self.assertIsNone(sl.parse_time("nope"))
        self.assertIsNone(sl.parse_time(None))
        self.assertEqual(sl.parse_time("2026-11-06T20:00:00"), NOW)


class Main(unittest.TestCase):
    def run_main(self, argv, env=None):
        import io
        import contextlib
        import sys
        out, err = io.StringIO(), io.StringIO()
        old = dict(os.environ)
        os.environ.update(env or {})
        old_stdin = sys.stdin
        sys.stdin = io.StringIO('{"cwd": "/nonexistent"}')
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                sl.main(argv)
        finally:
            sys.stdin = old_stdin
            os.environ.clear()
            os.environ.update(old)
        return out.getvalue(), err.getvalue()

    def test_bad_now_prints_nothing_and_no_traceback(self):
        out, err = self.run_main([], {"TICKET_LOOP_NOW": "bad", "TICKET_LOOP_USAGE_JSON": "/none"})
        self.assertEqual((out, err), ("", ""))

    def test_with_and_no_command_gives_a_usage_note(self):
        out, err = self.run_main(["--with"], {"TICKET_LOOP_USAGE_JSON": "/none"})
        self.assertIn("usage", err.lower())


class CapSection(unittest.TestCase):
    def test_reads_the_daily_cap_section(self):
        cfg = "# Loop config\n\n## Daily cap\n\nRolling: 14.3% a day.\n\n## Other\n\nx\n"
        self.assertEqual(sl.cap_text(cfg), "Rolling: 14.3% a day.")


if __name__ == "__main__":
    unittest.main()
