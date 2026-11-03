# Loop config

How `/ticket-loop:ticket-loop` finds, builds, tests, ships and records this repo's tickets.

## Tickets

GitHub issues in `jhnhnsn/ticket-loop` (see `docs/agents/issue-tracker.md`). A parent is an issue whose sub-issues are its tickets, or a milestone by name. Blocking is GitHub's native issue dependencies. Labels: `ready-for-agent`, `ready-for-human`.

## Order

Next is the first open sub-issue, in the parent's sub-issue order, whose blockers are all closed. With no argument, work the oldest open parent issue that has sub-issues.

## Checks

`claude plugin validate .` (exit code is the verdict; warnings don't fail it).

## Test queue

The app is the plugin itself. A ticket is tested by a real loop run of the working copy in the **sandbox**: `jhnhnsn/ticket-loop-sandbox` (private), cloned at `~/github/ticket-loop-sandbox`, with a tiny app and its own ready-made loop config (Sonnet on every role, so test runs stay cheap).

- **Run:** from the sandbox, the headless command in the sandbox's README (`claude -p "/ticket-loop:ticket-loop <args>" --plugin-dir ~/github/ticket-loop …`, prompt first, stdin closed). Ready when the stream's first message arrives. It loads the working copy in place of the installed plugin.
- **Read:** the stream-json output (Agent dispatches and their `description` labels, AskUserQuestion calls, the final report), the sandbox tracker (`gh issue view`, comments, closures) and the sandbox's `git log`.
- **Interactive:** steps that need a question answered (decisions, the daily cap) run in an interactive `claude --plugin-dir ~/github/ticket-loop` session in the sandbox, which the user drives from a test plan: AskUserQuestion isn't available headless (proven at setup).
- **Test plan measures:** labels in the agent list, what reaches the main thread, tracker state, commits, and that the main session stays free.
- **Clean up after each test:** close its dummy tickets and parent, reset the sandbox's `main` to its starting commit (`git push --force-with-lease` on the sandbox only), and undo any config change the test made.

Test hooks:

- **Dummy tickets:** each test plan files its own under a fresh sandbox parent issue (one-line tickets; a ticket built to force a decision; several for a handover).
- **Low cap:** set the sandbox config's Daily cap below today's use to make the cap trip at once.
- **Low budget:** add a `## Ticket budget` section to the sandbox config with a budget of 1, so a handover comes after the first ticket.
- **Effort overrides:** give every role an effort in the sandbox config's Models section that differs from the defaults (`- Implementer: Sonnet, high effort.`, and so on for the coordinator, Standards reviewer and Spec reviewer), then read each Agent call's `effort` in the stream-json; leave them out to test the defaults. `CLAUDE_CODE_EFFORT_LEVEL` must be unset, since it overrides the parameter.
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

One ticket at a time by default. When the frontier has two or more ready tickets that don't block each other, suggest building them in parallel worktrees (at most 2 at once) and ask the user to accept or decline; tests still run one at a time in the main thread.

## Daily cap

14.3% of the plan's weekly usage per day (one day's share), read from tokencount's `today.percent_of_week`.
