# Loop config

How `/ticket-loop:ticket-loop` finds, builds, tests, ships and records this repo's tickets.

## Tickets

GitHub issues in `jhnhnsn/ticket-loop` (see `docs/agents/issue-tracker.md`). A parent is an issue whose sub-issues are its tickets, or a milestone by name. Blocking is GitHub's native issue dependencies. Labels: `ready-for-agent`, `ready-for-human`, and `research` (opts a ticket in to research passes).

Read a ticket: `gh issue view <n> --repo jhnhnsn/ticket-loop --json title,body,labels,comments`, never `--comments`.

## Order

Next is the first open sub-issue, in the parent's sub-issue order, whose blockers are all closed. With no argument, work the oldest open parent issue that has sub-issues.

## Checks

`claude plugin validate .` (exit code is the verdict; warnings don't fail it), and `python3 -m unittest discover -s scripts -p 'test_*.py'` (the status line script's tests).

## Test queue

The app is the plugin itself. A ticket that changes what the loop does (dispatch, handover, stops, order, the cap) is tested by a real loop run of the working copy in the **sandbox**: `jhnhnsn/ticket-loop-sandbox` (private), cloned at `~/github/ticket-loop-sandbox`, with a tiny app and its own ready-made loop config (Sonnet on every role, so test runs stay cheap).

A ticket that changes only wording, docs or the changelog gets no sandbox run. Check it by reading, and say in its report: `No sandbox run: wording only, checked by reading.` A ticket that changes only the status line script uses that hook and the unit tests, and its report says so too.

- **Test branch:** each test works on its own branch, from a clean tree on the sandbox's `main`. Do these in order, each in its own Bash call. First, record the remote `main` for Clean up: `git -C ~/github/ticket-loop-sandbox ls-remote origin main`. Second, make the branch: `git -C ~/github/ticket-loop-sandbox switch -c test/<ticket>-<short name>`. Third, commit any config or file change a hook makes to this branch, so it stays off `main`. Git ignores `.claude/settings.local.json` (the user's global ignore file), so the hooks that write it don't commit it, and Clean up removes it. Fourth, push the branch, so it exists on the remote even when a run ships nothing: `git -C ~/github/ticket-loop-sandbox push origin test/<ticket>-<short name>`. The sandbox config's Ship pushes the current branch, closes each ticket with `gh issue close` (a closing keyword acts only on the default branch), and never pushes `main`.
- **Run:** on the test branch, from the sandbox, the headless command in the sandbox's README (`claude -p "/ticket-loop:ticket-loop <args>" --plugin-dir ~/github/ticket-loop …`, prompt first, stdin closed). Ready when the stream's first message arrives. It loads the working copy in place of the installed plugin.
- **Read:** the stream-json output (Agent dispatches and their `description` labels, AskUserQuestion calls, the final report), the sandbox tracker (`gh issue view`, comments, closures) and the sandbox's `git log`.
- **Interactive:** steps that need a question answered (decisions, the daily cap) run in an interactive `claude --plugin-dir ~/github/ticket-loop` session on the test branch in the sandbox, which the user drives from a test plan: AskUserQuestion isn't available headless (proven at setup).
- **Research label hook:** opt a sandbox dummy ticket in to research with `gh issue edit <n> --repo jhnhnsn/ticket-loop-sandbox --add-label research` (create the label in the sandbox first if it's missing: `gh label create research --repo jhnhnsn/ticket-loop-sandbox`); leave it off a ticket to test the default.
- **Test plan measures:** labels in the agent list, what reaches the main thread, tracker state, commits, and that the main session stays free.
- **Clean up after each test:** close its dummy tickets and parent. Remove the run's status file, until #40 settles it: `rm -f ~/github/ticket-loop-sandbox/.ticket-loop-status`. If a hook wrote the local settings file, remove it too: `rm -f ~/github/ticket-loop-sandbox/.claude/settings.local.json`. Then delete the branch with these commands, each in its own Bash call: `git -C ~/github/ticket-loop-sandbox switch main`, `git -C ~/github/ticket-loop-sandbox branch -D test/<ticket>-<short name>`, then `git -C ~/github/ticket-loop-sandbox push origin --delete test/<ticket>-<short name>`. A test's commits and config changes go with the branch. Last, run `git -C ~/github/ticket-loop-sandbox ls-remote origin main` again, and check that it prints the commit that the Test branch step recorded.

Test hooks:

- **Dummy tickets:** each test plan files its own under a fresh sandbox parent issue (one-line tickets; a ticket built to force a decision; several for a handover).
- **Low cap:** set the sandbox config's Daily cap below today's use to make the cap trip at once.
- **Low rolling cap:** set the sandbox config's Daily cap to `Rolling: 0.01% of the plan's weekly usage per day.`, so the allowance (at most 0.07%) is below the week's use and the cap trips at once, even early in a fresh week. The Usage line then shows the allowance to one decimal as 0.0% or 0.1% (`allowance 0.0% (day 2 of 7)`), with a full bar.
- **Cap not applicable:** replace the sandbox config's Daily cap section's text with `Not applicable: no plan usage to read.`, so the loop skips the cap and the preview's Usage line says so.
- **Cap unreadable:** disable tokencount in the sandbox only, with a sandbox `.claude/settings.local.json` of `{"enabledPlugins": {"tokencount@tokencount": false}}`, so the coordinator can't read the cap. Clean-up removes the file. Never change the user settings or the plugin cache for this.
- **Blockers unreadable:** refuse the tracker's dependency reads in the sandbox only, with a sandbox `.claude/settings.local.json` of `{"permissions": {"deny": ["Bash(gh api:*)", "Bash(*blocked*)", "Bash(*blocking*)"]}}`, so no agent can read a ticket's native dependencies, through `gh api`, `gh issue view --json`'s two dependency fields, or a search qualifier (`is:blocked`, `blocked-by:`, `blocking:`). A `Blocked by:` line in a ticket's body stays readable, so keep such lines out of this test's tickets. A deny rule beats the headless command's `--allowedTools`. Clean-up removes the file. Never change the user settings for this.
- **Concurrency modes:** set the sandbox config's Concurrency text to `One at a time.`, `Parallel worktrees: at most 2 at once.` or `Suggest and ask: at most 2 at once.`. For an older config, use `One at a time, or parallel worktrees when offered.` or `Parallel worktrees when independent.` (each reads as suggest and ask, limit 2), or `One ticket per run.` or no section (each reads as one at a time). For a parallel test, the sandbox config's Ship reads Parallel builds for the test branch, so its narrower push targets that branch. No parallel run on a test branch has happened yet, so that reading and the base commit of each worktree are unverified: check in the run that nothing reaches the sandbox's `main`.
- **Low budget:** add a `## Ticket budget` section to the sandbox config with a budget of 1, so a handover comes after the first ticket, or after the whole set of a parallel build.
- **Effort overrides:** give every role in the sandbox config's Models section an effort other than its default (`- Implementer: Sonnet, high effort.`), then read each Agent call's `effort` in the stream-json. Keep `CLAUDE_CODE_EFFORT_LEVEL` unset: it overrides the parameter.
- **Writing standard:** add a `## Writing` section to the sandbox config with the text `ASD-STE100` to test the writing rule; leave it out to test the default. For the dictionary check, write `ASD-STE100, dictionary at <path>` with the path to the user's own local copy of the PDF (the repo never holds one). Copy the sandbox a `GLOSSARY.md` from this repo's root if the test needs the project terms.
- **Status line script:** run `scripts/ticket-loop-statusline` with no stdin, or with `--with '<command>'`. Set `TICKET_LOOP_USAGE_JSON` to a saved tokencount `--json` report and `TICKET_LOOP_NOW` to an ISO time to fix its input. Write a sample `.ticket-loop-status` at the repo root to show a run (the repo's `.gitignore` lists it). Unit tests: `python3 -m unittest discover -s scripts -p 'test_*.py'`.
- **Milestone summary:** the sandbox config writes none; to test the milestone stop, set its Changelog to put a finished parent's summary under `## Unreleased`, above its entries.

## Reference

Spec #1 for the coordinator work, and the Claude Code docs (code.claude.com) for platform facts: nesting, SendMessage, AskUserQuestion, plugin agents. Where a ticket and its spec disagree, the ticket wins within its own scope. Anything that changes what the user sees, or contradicts a platform fact, goes to the user.

## Ship

Push `main` after every ticket. Publish once per milestone, when the parent closes: bump the minor `version` in `.claude-plugin/plugin.json` (#1 → 1.9.0), commit and push, so `claude plugin update` picks it up.

## Changelog

`CHANGELOG.md` at the root, for plugin users, newest first. Each shipped ticket adds an entry under `## Unreleased`: what the loop now does differently, in a sentence or two, linking its ticket (`(#3)`). At a milestone's publish, `## Unreleased` becomes `## <version>`, with a two-line summary of the milestone above its entries. Upcoming milestones aren't listed.

## Stops

Besides the built-in ones: stop before any change outside this repo and the sandbox (the plugin cache, user settings, other repos).

## Models

- Implementer: Opus.
- Standards reviewer: Sonnet.
- Spec reviewer: Opus.

## Commits

Plain sentence-case summaries with no type prefix, as in the history. Body ends with `Closes #<ticket>`. No `Co-Authored-By` or other attribution lines. One commit per ticket, plus its fix commit.

## Concurrency

Suggest and ask: at most 2 at once.

## Writing

ASD-STE100

## Daily cap

Rolling: 14.3% of the plan's weekly usage per day (one day's share), so the week's use so far (tokencount's `week.percent_used`) may reach 14.3% × the day of the usage week (24-hour days counted from the week's start).

## Status line

Added.
