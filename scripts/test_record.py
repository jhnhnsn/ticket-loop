"""Tests for the ticket-loop run store script, through its command-line seam.

Run from the repo root: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "ticket-loop-record")
RECORD = {"project": "demo", "date": "2026-11-15", "ticket": 57, "run_id": "r1"}
NAME = "runs/demo/2026-11-15-57-r1.json"


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


class Store(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "store")
        self.work = os.path.join(self.tmp.name, "work")
        os.mkdir(self.work)

    def tearDown(self):
        self.tmp.cleanup()

    def bare(self):
        path = os.path.join(self.tmp.name, "remote.git")
        git("init", "--bare", "-q", path)
        return path

    def run_script(self, *args, remote=None, home=None):
        env = dict(os.environ, TICKET_LOOP_HOME=home or self.home)
        env.pop("TICKET_LOOP_STORE_REMOTE", None)
        if remote:
            env["TICKET_LOOP_STORE_REMOTE"] = remote
        return subprocess.run([sys.executable, SCRIPT, *args], cwd=self.work,
                              env=env, capture_output=True, text=True)

    def record_file(self, record=RECORD, name="record.json"):
        path = os.path.join(self.work, name)
        with open(path, "w") as f:
            json.dump(record, f)
        return path

    def committed(self, store):
        return git("log", "main", "--name-only", "--format=", cwd=store).stdout.split()

    def test_first_write_without_remote_makes_a_local_repo(self):
        r = self.run_script("write", self.record_file())
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), f"run record: written ({NAME}, no remote)")
        self.assertIn(NAME, self.committed(self.home))

    def test_write_pushes_to_the_remote(self):
        remote = self.bare()
        r = self.run_script("write", self.record_file(), remote=remote)
        self.assertEqual(r.stdout.strip(), f"run record: written ({NAME}, pushed)")
        self.assertIn(NAME, self.committed(remote))

    def test_new_machine_clones_the_remote(self):
        remote = self.bare()
        self.run_script("write", self.record_file(), remote=remote)
        other = os.path.join(self.tmp.name, "machine2")
        two = dict(RECORD, run_id="r2")
        r = self.run_script("write", self.record_file(two), remote=remote, home=other)
        self.assertEqual(r.returncode, 0)
        files = self.committed(other)
        self.assertIn(NAME, files)
        self.assertIn("runs/demo/2026-11-15-57-r2.json", files)

    def test_two_machines_never_conflict(self):
        remote = self.bare()
        other = os.path.join(self.tmp.name, "machine2")
        self.run_script("write", self.record_file(), remote=remote)
        self.run_script("write", self.record_file(dict(RECORD, run_id="r2")),
                        remote=remote, home=other)
        r = self.run_script("write", self.record_file(dict(RECORD, run_id="r3")),
                            remote=remote)
        self.assertIn("pushed", r.stdout)
        self.assertEqual(len(self.committed(remote)), 3)

    def test_push_failure_keeps_the_commit_and_the_next_write_pushes_it(self):
        remote = self.bare()
        self.run_script("write", self.record_file(), remote=remote)
        gone = remote + ".away"
        os.rename(remote, gone)
        r = self.run_script("write", self.record_file(dict(RECORD, run_id="r2")),
                            remote=remote)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "run record: written (runs/demo/"
                         "2026-11-15-57-r2.json), push failed: the commit stays local,"
                         " and the next write pushes it")
        os.rename(gone, remote)
        self.run_script("write", self.record_file(dict(RECORD, run_id="r3")), remote=remote)
        self.assertEqual(len(self.committed(remote)), 3)

    def test_store_not_available(self):
        r = self.run_script("write", self.record_file(),
                            remote=os.path.join(self.tmp.name, "missing.git"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "run record: not written (store not available)")

    def test_records_never_change(self):
        self.run_script("write", self.record_file())
        r = self.run_script("write", self.record_file(dict(RECORD, extra=1)))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(),
                         f"run record: not written (record exists: {NAME})")

    def test_followup_goes_next_to_the_record(self):
        self.run_script("write", self.record_file())
        r = self.run_script("write", "--followup", self.record_file(dict(RECORD, reverted=False)))
        self.assertIn("runs/demo/2026-11-15-57-r1.followup.json", self.committed(self.home))
        self.assertIn("written", r.stdout)

    def test_followup_needs_its_record(self):
        r = self.run_script("write", "--followup", self.record_file())
        self.assertEqual(r.stdout.strip(),
                         f"run record: not written (no record for the followup: {NAME})")

    def test_sandbox_project_writes_apart(self):
        r = self.run_script("write", self.record_file(dict(RECORD, project="_sandbox")))
        self.assertIn("runs/_sandbox/2026-11-15-57-r1.json", r.stdout)

    def test_fields_are_checked(self):
        bad = [({k: v for k, v in RECORD.items() if k != "run_id"}, "run_id is missing"),
               (dict(RECORD, date="15/11/2026"), "date is not YYYY-MM-DD"),
               (dict(RECORD, ticket="x"), "ticket is not a number"),
               (dict(RECORD, project="../up"), "project has characters other than"
                " letters, digits, '.', '_' and '-'")]
        for record, reason in bad:
            r = self.run_script("write", self.record_file(record))
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(),
                             f"run record: not written (record not valid: {reason})")

    def test_multi_repo_record_lists_each_repo_and_its_commits(self):
        multi = dict(RECORD, commits=["aaa111"],
                     repos=[{"repo": "../backend", "commits": ["bbb222", "ccc333"]}])
        r = self.run_script("write", self.record_file(multi))
        self.assertEqual(r.stdout.strip(), f"run record: written ({NAME}, no remote)")
        with open(os.path.join(self.home, NAME)) as f:
            self.assertEqual(json.load(f)["repos"], multi["repos"])

    def test_repos_are_checked(self):
        bad = [{"repo": "../backend"}, {"repo": "", "commits": []},
               {"repo": "../backend", "commits": "bbb222"},
               {"repo": "../backend", "commits": [1]}, "../backend"]
        for entry in bad:
            r = self.run_script("write", self.record_file(dict(RECORD, repos=[entry])))
            self.assertEqual(r.stdout.strip(), "run record: not written (record not valid:"
                             " each repos entry needs a repo and a list of commits)")
        r = self.run_script("write", self.record_file(dict(RECORD, repos={"repo": "x"})))
        self.assertEqual(r.stdout.strip(),
                         "run record: not written (record not valid: repos is not a list)")

    def test_not_json(self):
        path = os.path.join(self.work, "bad.json")
        with open(path, "w") as f:
            f.write("{nope")
        r = self.run_script("write", path)
        self.assertEqual(r.stdout.strip(),
                         "run record: not written (record not valid: not a JSON object)")

    def test_opt_out(self):
        os.makedirs(os.path.join(self.work, "docs", "agents"))
        with open(os.path.join(self.work, "docs", "agents", "ticket-loop.md"), "w") as f:
            f.write("# Loop config\n\n## Run records\n\nOff.\n\n## Ship\n\nPush.\n")
        r = self.run_script("write", self.record_file())
        self.assertEqual(r.stdout.strip(), "run record: not written (off in the loop config)")
        self.assertFalse(os.path.exists(self.home))

    def test_opt_out_needs_off_alone(self):
        os.makedirs(os.path.join(self.work, "docs", "agents"))
        with open(os.path.join(self.work, "docs", "agents", "ticket-loop.md"), "w") as f:
            f.write("# Loop config\n\n## Run records\n\nOff. later, after #60.\n")
        r = self.run_script("write", self.record_file())
        self.assertEqual(r.stdout.strip(), f"run record: written ({NAME}, no remote)")

    def test_empty_store_folder_clones_the_remote(self):
        remote = self.bare()
        self.run_script("write", self.record_file(), remote=remote)
        other = os.path.join(self.tmp.name, "machine2")
        os.mkdir(other)
        r = self.run_script("write", self.record_file(dict(RECORD, run_id="r2")),
                            remote=remote, home=other)
        self.assertIn("pushed", r.stdout)
        self.assertIn(NAME, self.committed(other))

    def test_pull(self):
        remote = self.bare()
        other = os.path.join(self.tmp.name, "machine2")
        self.run_script("write", self.record_file(), remote=remote)
        self.run_script("write", self.record_file(dict(RECORD, run_id="r2")),
                        remote=remote, home=other)
        r = self.run_script("pull", remote=remote)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "run store: pulled")
        self.assertTrue(os.path.exists(
            os.path.join(self.home, "runs/demo/2026-11-15-57-r2.json")))

    def test_pull_reports_and_never_fails(self):
        self.assertEqual(self.run_script("pull").stdout.strip(),
                         "run store: not pulled (no store yet)")
        self.run_script("write", self.record_file())
        self.assertEqual(self.run_script("pull").stdout.strip(),
                         "run store: not pulled (no remote)")
        r = self.run_script("pull", remote=os.path.join(self.tmp.name, "missing.git"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "run store: not pulled (remote not available)")

    def test_due_lists_old_records_with_no_followup(self):
        old = dict(RECORD, date="2020-01-01", commits=["abc123"])
        self.run_script("write", self.record_file(old))
        self.run_script("write", self.record_file(dict(old, run_id="r2")))
        self.run_script("write", "--followup", self.record_file(dict(old, run_id="r2")))
        self.run_script("write", self.record_file(dict(old, project="other")))
        today = datetime.date.today().isoformat()
        self.run_script("write", self.record_file(dict(RECORD, date=today)))
        r = self.run_script("due", "demo")
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0]), old)

    def test_due_skips_a_record_that_is_not_json(self):
        old = dict(RECORD, date="2020-01-01")
        self.run_script("write", self.record_file(old))
        folder = os.path.join(self.home, "runs", "demo")
        with open(os.path.join(folder, "2020-01-02-58-r1.json"), "w") as f:
            f.write("{nope")
        r = self.run_script("due", "demo")
        self.assertEqual(r.returncode, 0)
        self.assertEqual([json.loads(n) for n in r.stdout.strip().splitlines()], [old])

    def test_due_with_only_bad_records_is_none_due(self):
        self.run_script("write", self.record_file(dict(RECORD, date="2020-01-01")))
        folder = os.path.join(self.home, "runs", "demo")
        with open(os.path.join(folder, "2020-01-01-57-r1.json"), "w") as f:
            f.write("[1]")
        self.assertEqual(self.run_script("due", "demo").stdout.strip(),
                         "run store: no records due")

    def test_due_at_exactly_14_days_waits(self):
        day = (datetime.date.today() - datetime.timedelta(days=14)).isoformat()
        self.run_script("write", self.record_file(dict(RECORD, date=day)))
        self.assertEqual(self.run_script("due", "demo").stdout.strip(),
                         "run store: no records due")

    def test_due_reports_and_never_fails(self):
        r = self.run_script("due", "demo")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "run store: no records due (no store yet)")
        self.assertEqual(self.run_script("due", "../up").returncode, 2)

    def test_wrong_usage_exits_2(self):
        r = self.run_script("frob")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
