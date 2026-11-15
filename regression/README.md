# Regression suite

A fixed set of sandbox scenarios, made from real past failures, that tests a loop change against old behaviour (#54). It runs a **controlled comparison**: the suite runs on a frozen baseline version and on the changed version, under the same conditions, some times each, and writes one result file with the verdict.

- **Runner and graders:** `scripts/ticket-loop-regression` (unit tests: `scripts/test_regression.py`, on saved stream-json in `scripts/fixtures/regression/`). Grading uses no LLM: it reads the stream-json, the sandbox tracker and the sandbox's `git log`.
- **Visible scenarios:** `regression/scenarios/*.json`.
- **Held-out scenarios:** only in `~/.ticket-loop-holdout/scenarios/*.json`, a clone of a private repo. Only this suite opens it. A result file names each one by an opaque ID (`holdout-<hash>`), with its pass rates and no check details.
- **Results:** one new file per comparison, at `$TICKET_LOOP_HOME/runs/_sandbox/regression/<date>-<baseline>-vs-<candidate>-<id>.json` (default `~/.ticket-loop/`, the run store, #57). The raw stream-json of each run stays in the temporary folder the result's `conditions.stream_dir` names.

## When it runs

One full comparison against the last published version before each milestone publish, and when the user asks. A loop ticket keeps its own sandbox test, as the Test queue says.

```sh
scripts/ticket-loop-regression compare --baseline a133728 [--target claimed-skip] [--repeats 5] [--only ships]
```

`--baseline` and `--candidate` take a git ref (checked out in a temporary worktree) or a path; the candidate is this checkout by default. The repo has no tags, so name the last published version by its publish commit (`git log --grep '^Publish' -1`). `list` prints the scenarios. `grade <scenario.json> <observation.json>` grades one saved run.

## The rules

- **Same conditions:** each run is headless, `--model sonnet`, with `CLAUDE_CODE_EFFORT_LEVEL` unset, from the sandbox's `main`. The result records the model IDs of both versions, the sandbox's `main` commit, its config hash, the `claude` version and the scenario set. Different model IDs make the comparison `invalid`: run the baseline again on the new model.
- **Order:** round by round, each scenario on the baseline and then on the candidate, so a stop leaves both versions with the same runs.
- **Pass rule:** a change passes only if each `--target` scenario's pass rate goes up, and no other scenario's rate goes down by more than the noise. The noise is the standard error of the difference of the two rates, and never less than one run's share (1/5 at 5 repeats). With no target, the comparison checks only that nothing got worse.
- **Held-out check:** reported apart. A held-out scenario that gets worse fails the change; when a visible target improved too, the reason says overfitting.
- **The cap:** before each scenario run, the suite reads tokencount. It stops, and writes what finished as `incomplete`, when the tokencount rolling guard is not armed, the loop's Daily cap (this repo's loop config) is reached, or the cap is unreadable. With little cap left, it runs fewer rounds, and the result's `notes` say so. A Sonnet run counts as 0.5% of the week until the suite has measured one.
- **Write scope:** the scenarios, `scripts/ticket-loop-regression`, its tests and fixtures, and the held-out clone are outside the write scope of any agent that proposes loop changes (#55). An agent like that never reads the sandbox tracker's closed tickets, because held-out scenarios become dummy tickets there while they run.

## A scenario

```json
{"name": "claimed-skip", "from": "#49: ...",
 "tickets": [{"key": "a", "title": "...", "body": "...", "labels": ["ready-for-agent"]}],
 "claim": ["a"], "blocked_by": [["b", "a"]],
 "config": {"Daily cap": "Rolling: 0.01% of the plan's weekly usage per day."},
 "settings_local": {"permissions": {"deny": ["Bash(gh api:*)"]}},
 "args": "{parent}",
 "checks": [{"check": "ticket_state", "ticket": "a", "state": "OPEN"}]}
```

The runner files the tickets under a fresh sandbox parent, pre-claims and blocks them, sets the named sandbox config sections and the local settings on a test branch, and runs `/ticket-loop:ticket-loop <args>` (`{parent}` and `{<key>}` become issue numbers). Clean-up is the Test queue's: it closes the tickets, deletes the branch, and checks that the sandbox's `main` did not move.

Checks: `ticket_state`, `ticket_label` (`present`), `commit_closes`, `no_commit_closes`, `report_matches` (a regex on the final report; `present`), `dispatched` (a regex on each Agent call's `description`, or on `field`; `min`, `max`), `refused` (refused tool calls; `min`, `max`), `main_unchanged`. A run passes only when every check holds.

## Setup (steps only the user can do)

The loop never changes user settings or makes repos outside this one, so do these yourself, one time on each machine that runs the suite.

1. Make the private held-out repo (one time only): `gh repo create jhnhnsn/ticket-loop-holdout --private`
2. Clone it: `gh repo clone jhnhnsn/ticket-loop-holdout ~/.ticket-loop-holdout`
3. Put held-out scenarios in `~/.ticket-loop-holdout/scenarios/`, in the format above, and commit and push them. Write them yourself, and never in an agent session.
4. Add these deny rules to `permissions.deny` in `~/.claude/settings.json`, so no agent reads or edits the held-out set:
   `"Read(~/.ticket-loop-holdout/**)"`, `"Edit(~/.ticket-loop-holdout/**)"`, `"Write(~/.ticket-loop-holdout/**)"`, `"Bash(*ticket-loop-holdout*)"`
5. Before a comparison, arm the tokencount rolling guard: `python3 "<tokencount path>/tokencount" guard set --rolling 14.3 --window week` (the loop's Daily cap share).
