"""Tests for the ticket-loop regression suite.

Run from the repo root: python3 -m unittest discover -s scripts -p 'test_*.py'
No test starts a loop run: they use saved stream-json fixtures and temporary folders.
"""
import importlib.machinery
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_loader = importlib.machinery.SourceFileLoader(
    "regression", os.path.join(HERE, "ticket-loop-regression"))
_spec = importlib.util.spec_from_loader("regression", _loader)
rg = importlib.util.module_from_spec(_spec)
_loader.exec_module(rg)

FIX = os.path.join(HERE, "fixtures", "regression")


def stream(name):
    with open(os.path.join(FIX, name)) as fh:
        return rg.parse_stream(fh.read())


def observation(**over):
    obs = {"stream": stream("claimed-skip.jsonl"),
           "tickets": {"claimed": {"number": 41, "state": "OPEN", "labels": ["in-progress"]},
                       "free": {"number": 42, "state": "CLOSED", "labels": []}},
           "commits": ["Add the greeting\n\nCloses #42"],
           "main_moved": False}
    obs.update(over)
    return obs


class ParseStream(unittest.TestCase):
    def test_reads_models_dispatches_refusals_and_report(self):
        s = stream("claimed-skip.jsonl")
        self.assertEqual(s["models"], ["claude-haiku-5-5", "claude-sonnet-5-5"])
        self.assertEqual([d["description"] for d in s["dispatches"]],
                         ["Coordinator #40", "Implement #42"])
        self.assertEqual(len(s["refusals"]), 1)
        self.assertIn("Skipped #41", s["report"])
        self.assertAlmostEqual(s["cost_usd"], 0.41)

    def test_skips_lines_that_are_not_json(self):
        s = rg.parse_stream('garbage\n{"type":"result","result":"ok"}\n')
        self.assertEqual(s["report"], "ok")

    def test_no_result_line_is_no_report(self):
        self.assertIsNone(rg.parse_stream("")["report"])


class Grade(unittest.TestCase):
    def test_all_checks_hold_is_a_pass(self):
        checks = [{"check": "ticket_state", "ticket": "free", "state": "CLOSED"},
                  {"check": "ticket_state", "ticket": "claimed", "state": "OPEN"},
                  {"check": "commit_closes", "ticket": "free"},
                  {"check": "no_commit_closes", "ticket": "claimed"},
                  {"check": "report_matches", "pattern": "Skipped {claimed}"},
                  {"check": "dispatched", "pattern": "^Implement {free}$", "min": 1, "max": 1},
                  {"check": "refused", "min": 1},
                  {"check": "main_unchanged"}]
        v = rg.grade(checks, observation())
        self.assertTrue(v["pass"], v)
        self.assertEqual(len(v["checks"]), 8)

    def test_one_failed_check_fails_the_run_and_says_which(self):
        v = rg.grade([{"check": "ticket_state", "ticket": "claimed", "state": "CLOSED"},
                      {"check": "main_unchanged"}], observation())
        self.assertFalse(v["pass"])
        self.assertEqual([c["pass"] for c in v["checks"]], [False, True])
        self.assertIn("#41", v["checks"][0]["detail"])

    def test_a_dispatch_of_a_claimed_ticket_fails(self):
        v = rg.grade([{"check": "dispatched", "pattern": "{claimed}", "max": 0}], observation())
        self.assertTrue(v["pass"])
        v = rg.grade([{"check": "dispatched", "pattern": "{free}", "max": 0}], observation())
        self.assertFalse(v["pass"])

    def test_dispatches_count_by_agent_type(self):
        v = rg.grade([{"check": "dispatched", "field": "subagent_type",
                       "pattern": "coordinator", "min": 2}], observation())
        self.assertFalse(v["pass"])
        self.assertIn("1 dispatches", v["checks"][0]["detail"])

    def test_a_moved_main_fails(self):
        v = rg.grade([{"check": "main_unchanged"}], observation(main_moved=True))
        self.assertFalse(v["pass"])

    def test_a_run_with_no_report_fails_every_report_check(self):
        obs = observation(stream=rg.parse_stream(""))
        v = rg.grade([{"check": "report_matches", "pattern": "."}], obs)
        self.assertFalse(v["pass"])

    def test_an_unknown_check_is_an_error_not_a_pass(self):
        with self.assertRaises(ValueError):
            rg.grade([{"check": "vibes"}], observation())


def rates(**kw):
    return {name: {"passes": p, "runs": n} for name, (p, n) in kw.items()}


class PassRule(unittest.TestCase):
    def test_target_up_and_nothing_worse_passes(self):
        r = rg.judge(rates(ships=(5, 5), claimed=(2, 5)), rates(ships=(5, 5), claimed=(4, 5)),
                     targets=["claimed"], holdout=[])
        self.assertEqual(r["verdict"], "pass", r)
        self.assertEqual(r["scenarios"]["claimed"]["baseline_rate"], 0.4)
        self.assertEqual(r["scenarios"]["claimed"]["candidate_rate"], 0.8)

    def test_target_not_up_fails(self):
        r = rg.judge(rates(claimed=(3, 5)), rates(claimed=(3, 5)), targets=["claimed"], holdout=[])
        self.assertEqual(r["verdict"], "fail")
        self.assertIn("claimed: target did not improve", r["reasons"])

    def test_one_run_down_in_five_is_noise(self):
        r = rg.judge(rates(ships=(5, 5), claimed=(2, 5)), rates(ships=(4, 5), claimed=(4, 5)),
                     targets=["claimed"], holdout=[])
        self.assertEqual(r["verdict"], "pass", r)
        self.assertAlmostEqual(r["scenarios"]["ships"]["noise"], 0.2)

    def test_two_runs_down_in_five_is_worse(self):
        r = rg.judge(rates(ships=(5, 5), claimed=(2, 5)), rates(ships=(3, 5), claimed=(4, 5)),
                     targets=["claimed"], holdout=[])
        self.assertEqual(r["verdict"], "fail")
        self.assertIn("ships: worse by more than the noise", r["reasons"])

    def test_held_out_worse_while_visible_better_is_overfitting(self):
        r = rg.judge(rates(claimed=(2, 5), h1=(5, 5)), rates(claimed=(5, 5), h1=(2, 5)),
                     targets=["claimed"], holdout=["h1"])
        self.assertEqual(r["verdict"], "fail")
        self.assertIn("overfitting: held-out h1 worse while the visible target improved",
                      r["reasons"])
        self.assertEqual(sorted(r["holdout"]), ["h1"])
        self.assertNotIn("h1", r["scenarios"])

    def test_no_target_is_a_check_for_no_regression(self):
        r = rg.judge(rates(ships=(5, 5)), rates(ships=(5, 5)), targets=[], holdout=[])
        self.assertEqual(r["verdict"], "pass")

    def test_a_scenario_with_no_runs_on_one_version_is_incomplete(self):
        r = rg.judge(rates(ships=(5, 5)), rates(ships=(0, 0)), targets=[], holdout=[])
        self.assertEqual(r["verdict"], "incomplete")


NOW = datetime(2026, 11, 15, 21, 0, tzinfo=timezone.utc)   # day 6 of a week from Nov 10 07:00
USAGE = {"usage_source": "live",
         "week": {"percent_used": 64.0, "resets_at": "2026-11-17T07:00:00+00:00"},
         "today": {"percent_of_week": 9.0}}
ROLLING = "Rolling: 14.3% of the plan's weekly usage per day (one day's share)."
GUARD = {"window": "week", "rolling_daily": 14.3, "window_resets_at": "2026-11-17T07:00:00+00:00"}


class CapCheck(unittest.TestCase):
    def test_room_left_under_the_rolling_cap(self):
        c = rg.cap_check(USAGE, ROLLING, GUARD, NOW)
        self.assertTrue(c["ok"], c)
        self.assertAlmostEqual(c["left"], 14.3 * 6 - 64.0)

    def test_cap_reached_stops(self):
        used = dict(USAGE, week=dict(USAGE["week"], percent_used=86.0))
        c = rg.cap_check(used, ROLLING, GUARD, NOW)
        self.assertFalse(c["ok"])
        self.assertIn("Daily cap reached", c["reason"])

    def test_no_armed_guard_stops(self):
        c = rg.cap_check(USAGE, ROLLING, None, NOW)
        self.assertFalse(c["ok"])
        self.assertIn("guard", c["reason"])

    def test_a_fixed_or_expired_or_paused_guard_is_not_armed(self):
        for g in ({"window": "week", "stop_at_used": 90},
                  dict(GUARD, window_resets_at="2026-11-10T07:00:00+00:00"),
                  dict(GUARD, paused_until="2026-11-16T07:00:00+00:00")):
            self.assertFalse(rg.cap_check(USAGE, ROLLING, g, NOW)["ok"], g)

    def test_unreadable_usage_stops(self):
        c = rg.cap_check({"usage_source": "unavailable"}, ROLLING, GUARD, NOW)
        self.assertFalse(c["ok"])
        self.assertIn("unreadable", c["reason"])

    def test_a_per_day_cap_reads_today(self):
        c = rg.cap_check(USAGE, "14.3% of the plan's weekly usage per day.", GUARD, NOW)
        self.assertTrue(c["ok"])
        self.assertAlmostEqual(c["left"], 5.3)

    def test_reads_the_cap_section_of_a_config(self):
        self.assertEqual(rg.cap_text("# x\n\n## Daily cap\n\nRolling: 1% a day.\n\n## Status line\n"),
                         "Rolling: 1% a day.")


class Repeats(unittest.TestCase):
    def test_enough_cap_keeps_the_repeats(self):
        self.assertEqual(rg.plan_repeats(left=30.0, per_run=0.5, runs_per_round=12, wanted=5), 5)

    def test_little_cap_reduces_the_repeats(self):
        self.assertEqual(rg.plan_repeats(left=13.0, per_run=0.5, runs_per_round=12, wanted=5), 2)

    def test_no_cap_reading_keeps_the_repeats(self):
        self.assertEqual(rg.plan_repeats(left=None, per_run=0.5, runs_per_round=12, wanted=5), 5)


SCEN = [{"name": "ships", "holdout": False}, {"name": "claimed", "holdout": False},
        {"name": "secret", "holdout": True}]


def fake_run(table, models=("claude-sonnet-5-5",)):
    """A run function from a table: (scenario, version) -> list of pass values, in order."""
    left = {k: list(v) for k, v in table.items()}
    calls = []

    def run(scenario, version):
        calls.append((scenario["name"], version))
        ok = left[(scenario["name"], version)].pop(0)
        return {"pass": ok, "checks": [{"check": "x", "pass": ok, "detail": "#%s detail" % scenario["name"]}],
                "models": list(models), "usage": 0.5, "cost_usd": 0.1}
    return run, calls


def always(left=50.0):
    return lambda: {"ok": True, "left": left, "reason": "ok"}


ALL_PASS = {(n, v): [True] * 5 for n in ("ships", "claimed", "secret")
            for v in ("baseline", "candidate")}


class Comparison(unittest.TestCase):
    def test_runs_each_scenario_on_both_versions_round_by_round(self):
        run, calls = fake_run(ALL_PASS)
        r = rg.run_comparison(SCEN, 2, [], run, always(), {"sandbox": "abc"})
        self.assertEqual(calls[:6], [("ships", "baseline"), ("ships", "candidate"),
                                     ("claimed", "baseline"), ("claimed", "candidate"),
                                     ("secret", "baseline"), ("secret", "candidate")])
        self.assertEqual(len(calls), 12)
        self.assertEqual(r["verdict"], "pass")
        self.assertEqual(r["scenarios"]["ships"]["candidate"], "2/2")
        self.assertEqual(r["conditions"]["models"]["baseline"], ["claude-sonnet-5-5"])
        self.assertEqual(r["conditions"]["sandbox"], "abc")
        self.assertEqual(r["repeats"], {"wanted": 2, "done": 2})

    def test_held_out_is_reported_apart_under_an_opaque_name_with_no_details(self):
        run, _ = fake_run(ALL_PASS)
        r = rg.run_comparison(SCEN, 1, [], run, always(), {})
        text = json.dumps(r)
        self.assertNotIn("secret", text)
        self.assertEqual(list(r["holdout"]), [rg.holdout_id("secret")])

    def test_cap_reached_mid_way_stops_and_reports_what_finished(self):
        run, calls = fake_run(ALL_PASS)
        checks = iter([{"ok": True, "left": None, "reason": "ok"}] * 7
                      + [{"ok": False, "left": 0, "reason": "Daily cap reached: 86% of 85.8%"}])
        r = rg.run_comparison(SCEN, 2, [], run, lambda: next(checks), {})
        self.assertEqual(len(calls), 7)
        self.assertEqual(r["stopped"], "Daily cap reached: 86% of 85.8%")
        self.assertEqual(r["repeats"]["done"], 1)
        self.assertEqual(r["scenarios"]["ships"]["candidate"], "1/1")
        self.assertEqual(r["verdict"], "incomplete")

    def test_little_cap_left_reduces_the_repeats_and_says_so(self):
        run, calls = fake_run(ALL_PASS)
        r = rg.run_comparison(SCEN, 5, [], run, always(left=6.5), {})
        self.assertEqual(r["repeats"], {"wanted": 5, "done": 2})
        self.assertEqual(len(calls), 12)
        self.assertIn("repeats reduced to 2", r["notes"][0])

    def test_different_models_make_the_comparison_invalid(self):
        b, _ = fake_run(ALL_PASS, models=("claude-sonnet-5-5",))
        c, _ = fake_run(ALL_PASS, models=("claude-sonnet-6",))
        r = rg.run_comparison(SCEN, 1, [], lambda s, v: (b if v == "baseline" else c)(s, v),
                              always(), {})
        self.assertEqual(r["verdict"], "invalid")
        self.assertIn("run the baseline again", r["reasons"][0])

    def test_an_error_in_a_run_stops_and_keeps_what_finished(self):
        run, calls = fake_run(ALL_PASS)

        def flaky(s, v):
            if len(calls) == 3:
                raise RuntimeError("the sandbox's main moved")
            return run(s, v)
        r = rg.run_comparison(SCEN, 1, [], flaky, always(), {})
        self.assertEqual(len(calls), 3)
        self.assertIn("the sandbox's main moved", r["stopped"])
        self.assertEqual(r["scenarios"]["ships"]["candidate"], "1/1")
        self.assertEqual(r["verdict"], "incomplete")

    def test_records_the_effort_of_each_dispatch_with_the_conditions(self):
        b, _ = fake_run(ALL_PASS)

        def run(s, v):
            g = b(s, v)
            g["dispatches"] = [{"subagent_type": "ticket-loop:coordinator", "model": None,
                                "effort": "high", "description": "secret words"}]
            return g
        r = rg.run_comparison(SCEN, 1, [], run, always(), {})
        self.assertEqual(r["conditions"]["dispatch_efforts"]["candidate"],
                         ["ticket-loop:coordinator model=default effort=high"])
        self.assertNotIn("secret words", json.dumps(r))


class SandboxConfig(unittest.TestCase):
    CONFIG = "# Loop config\n\n## Models\n\n- Implementer: Sonnet.\n\n## Daily cap\n\n14.3% a day.\n"

    def test_replaces_a_section_and_adds_a_missing_one(self):
        out = rg.set_sections(self.CONFIG, {"Daily cap": "Rolling: 0.01% a day.",
                                            "Ticket budget": "1"})
        self.assertEqual(rg.cap_text(out), "Rolling: 0.01% a day.")
        self.assertIn("## Ticket budget\n\n1\n", out)
        self.assertIn("- Implementer: Sonnet.", out)
        self.assertNotIn("14.3%", out)

    def test_fills_ticket_numbers_into_the_arguments(self):
        self.assertEqual(rg.fill_args("{b} {a}", {"a": {"number": 3}, "b": {"number": 4}}, 2),
                         "#4 #3")
        self.assertEqual(rg.fill_args("{parent}", {}, 2), "#2")


class ResultFile(unittest.TestCase):
    def test_writes_a_new_committed_record_through_the_record_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = os.path.join(tmp, "store")
            env = dict(os.environ, TICKET_LOOP_HOME=home)
            env.pop("TICKET_LOOP_STORE_REMOTE", None)
            res = {"verdict": "pass", "versions": {"baseline": "a133728@a133728",
                                                   "candidate": "working-copy@abc1234"}}
            l1 = rg.write_result(res, NOW, tmp, env=env)
            l2 = rg.write_result(res, NOW, tmp, env=env)
            self.assertRegex(l1, r"^run record: written \(runs/_sandbox/2026-11-15-0-regression-"
                                 r"a133728-a133728-vs-working-copy-abc1234-\w+\.json, no remote\)$")
            self.assertNotEqual(l1, l2)
            name = l1.split("(", 1)[1].split(",", 1)[0]
            with open(os.path.join(home, name)) as fh:
                rec = json.load(fh)
            self.assertEqual((rec["verdict"], rec["project"], rec["ticket"]), ("pass", "_sandbox", 0))
            log = rg._cmd(["git", "-C", home, "log", "--format=%s"])
            self.assertEqual(log.count("Add runs/_sandbox/"), 2)
            self.assertEqual(os.listdir(tmp), ["store"])


class Scenarios(unittest.TestCase):
    def test_loads_visible_and_held_out_sets(self):
        with tempfile.TemporaryDirectory() as hold:
            os.makedirs(os.path.join(hold, "scenarios"))
            with open(os.path.join(hold, "scenarios", "h.json"), "w") as fh:
                json.dump({"name": "h", "tickets": [], "args": "", "checks": []}, fh)
            got = rg.load_scenarios(os.path.join(ROOT, "regression", "scenarios"), hold)
        names = {s["name"]: s["holdout"] for s in got}
        self.assertTrue(names.pop("h"))
        self.assertGreaterEqual(len(names), 4)
        self.assertLessEqual(len(names), 6)
        self.assertFalse(any(names.values()))

    def test_no_held_out_clone_is_a_note_not_an_error(self):
        got = rg.load_scenarios(os.path.join(ROOT, "regression", "scenarios"), "/nonexistent")
        self.assertTrue(all(not s["holdout"] for s in got))

    def test_refused_bash_fails_a_run_with_no_refusal(self):
        s = {x["name"]: x for x in rg.visible_scenarios()}["refused-bash"]
        refused = [c for c in s["checks"] if c["check"] == "refused"]
        obs = {"stream": rg.parse_stream(""), "tickets": {}, "commits": [], "main_moved": False}
        self.assertFalse(rg.grade(refused, obs)["pass"])

    def test_every_visible_scenario_is_well_formed(self):
        for s in rg.load_scenarios(os.path.join(ROOT, "regression", "scenarios"), "/nonexistent"):
            keys = {t["key"] for t in s["tickets"]}
            self.assertTrue(s["checks"], s["name"])
            for c in s["checks"]:
                self.assertIn(c["check"], rg.CHECKS, s["name"])
                if "ticket" in c:
                    self.assertIn(c["ticket"], keys, s["name"])
            for key in s.get("claim", []):
                self.assertIn(key, keys, s["name"])


if __name__ == "__main__":
    unittest.main()
