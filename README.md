# ticket-loop

A Claude Code plugin that ships a milestone's tickets one at a time, without check-ins. Your
main thread hands the run to a background **coordinator** subagent and stays free for you. The
coordinator works the tickets: each is built by a fresh implementer subagent (so every ticket
starts with a clear context), tested by the coordinator, reviewed by two fresh reviewer
subagents, then pushed, published and written up. It asks you only for decisions that are
yours, and stops only when it needs you and at the end of each milestone.

## Getting started

1. **Install Matt Pocock's skills**, which the loop builds on (`mattpocock-skills:grilling`,
   `mattpocock-skills:tdd`, `mattpocock-skills:code-review`, called by their full names so
   Claude Code's built-in `code-review` isn't loaded in their place):

   ```sh
   claude plugin install mattpocock-skills@claude-plugins-official
   ```

2. **Install ticket-loop:**

   ```sh
   claude plugin marketplace add jhnhnsn/ticket-loop
   claude plugin install ticket-loop@ticket-loop
   ```

   Restart Claude Code so the new skill is listed.

   For the [daily cap](#when-it-stops), also install
   [tokencount](https://github.com/jhnhnsn/tokencount) (1.1.0 or later, on a Pro or Max plan),
   which reports how much of your plan's week today has used:

   ```sh
   claude plugin marketplace add jhnhnsn/tokencount
   claude plugin install tokencount@tokencount
   ```

3. **Optional: run `/setup-matt-pocock-skills`** in your project. It records where tickets
   live and what the triage labels are (`docs/agents/`), which answers the loop's first
   questions before they're asked.

4. **Have tickets under a parent:** a milestone or spec issue whose sub-issues are the
   tickets, or a tracker milestone holding them, labelled `ready-for-agent`, each saying what it blocks on. `/to-spec` and
   `/to-tickets` (Matt Pocock's) make them from a plan.

5. **Run it** with the parent, or with the tickets you want shipped:

   ```
   /ticket-loop:ticket-loop 120        # every ticket under parent issue #120
   /ticket-loop:ticket-loop v1         # every ticket in milestone v1
   /ticket-loop:ticket-loop 82         # just ticket #82
   /ticket-loop:ticket-loop 82 84 85   # just these three
   ```

   The first run in a repo grills you before it starts (see [First run](#first-run)); after
   that it goes straight to the first ticket.

6. **Let it work.** The coordinator runs in the background, labelled with what it runs
   (`ticket-loop: #82 coordinator 1`), and your main thread is free for other work meanwhile.
   As it starts, the main thread says how big the run is (`M1: 7 ready, about 2
   coordinators.`) and how each role runs, model and effort (see [Models](#models)).
   Each coordinator ships at most the config's **ticket budget**, or fewer if a ticket ran
   heavy, then hands back, and the main thread starts a fresh one
   (`ticket-loop: M1 coordinator 2`) without asking, so no coordinator's context grows too
   large. At each hand-back, handovers included, the main thread shows the report for each
   ticket shipped since the last, in a few lines: what shipped, the decisions you answered
   and any taken on your behalf, tickets filed, what's next. Ask "how's the agent doing?" in
   the main thread at any time. Push and publish commands ask permission in your main session,
   naming the agent, unless your settings allow them; allow them to keep the loop unattended.

## First run

With no loop config in the repo, the loop runs setup first. It reads what the repo already says
(CLAUDE.md, `docs/agents/`, the README, the roadmap, scripts, the git remote) and drafts an
answer to every question, then grills you in rounds with Matt Pocock's `grilling` skill, each
question carrying its drafted answer so "yes" accepts it:

| Topic | What it settles |
| --- | --- |
| Tickets | where they live, how a parent holds them, how blocking is recorded, the labels |
| Order | which parent next, and the order inside it |
| Checks | the command for the automated checks and tests |
| Test queue | what gets run or playtested by hand, with which tools, temporary settings and how they're undone, what a test plan measures |
| Reference | an upstream or spec to stay faithful to, who wins when a ticket disagrees with it, which forks still go to you |
| Ship | the branch to push, the publish or deploy command, per ticket or per milestone |
| Changelog | where each shipped ticket's entry goes, who reads it, what it says, its order and links, where milestone summaries go, whether upcoming milestones are listed |
| Stops | anything beyond the built-in stops |
| Models | the model and effort for the coordinator, the implementer, the Standards reviewer and the Spec reviewer |
| Commits | message style, closing keyword, attribution lines |
| Concurrency | one ticket at a time, or parallel worktrees |
| Daily cap | the share of your plan's weekly usage one day may take (one day's share, 14.3%, by default) |
| Ticket budget | the most tickets one coordinator ships before a fresh one takes over (4 by default) |

The answers go to **`docs/agents/ticket-loop.md`**, the loop config, with a pointer line in
CLAUDE.md; both are committed. Every later run reads it. Edit it to change an answer, or delete
it to be grilled again.

Then setup **proves the loop closes** by doing each leg of one ticket's cycle itself:

- **Check:** the checks command passes.
- **Run:** the app starts without a click.
- **Drive:** a tool operates the app and reads its state, and a test hook takes effect.
- **Ship:** pushing and publishing need no prompt.
- **Record:** the changelog is in place.
- **Cap:** tokencount reports how much of the week today has used.

Each leg that can't be proven becomes a ticket under an **M0 · Closed loop** parent. The loop
then stops, and you close M0 with Claude in an ordinary session before running it again: the
loop can't test anything until its own legs close. Later tickets keep the cycle closed by
building any test hook their test plan needs. See
[`CLOSED-LOOP.md`](skills/ticket-loop/CLOSED-LOOP.md).

## How each ticket goes

The loop has two roles. The **launcher** is the skill in your main thread: it runs setup when
there's no config, works out the argument (a bad one fails there, in front of you), starts the
coordinator, and shows you what it hands back. The **coordinator** is a subagent shipped with
the plugin (`ticket-loop:coordinator`, on the config's coordinator model): it takes each ticket
through these steps, dispatching the implementer and reviewers as subagents of its own, each
labelled with its ticket first (`#82 implement: greet option`, `#82 spec review`). That's two
levels of subagents, within Claude Code's default nesting limit.

1. **Frontier:** the next open `ready-for-agent` ticket under the parent whose blockers are all
   closed, in the config's order. Run with tickets instead, it's the next one named, in the order
   given; a named ticket that isn't `ready-for-agent`, or waits on an open ticket you didn't name,
   is skipped and you're told why.
2. **Implement:** a fresh implementer subagent builds it test-first at the seams the ticket
   names, runs the checks, commits locally (staging only its own files), and reports "ready to
   test" with a step-by-step **test plan** and the expected results.
3. **Decide:** where the ticket and the reference disagree, the config's rule settles it.
   Anything still yours comes to you in the main thread as a question with the options and a
   recommendation, while the coordinator waits. Your answer is recorded on the ticket as a
   comment and goes back to the same coordinator, which passes it to the implementer and
   carries on with the ticket; its report says which way you decided. (A headless `claude -p`
   run can't ask, so there the question ends the run: answer on the ticket and run the same
   command again.)
4. **Test and review:** the coordinator runs the test plan itself from the **test queue**, one
   ticket at a time, saying what it's about to run. To watch, open the coordinator's
   transcript in the agent view. Meanwhile two fresh reviewer subagents check the commit:
   **Standards** (the repo's conventions) and **Spec** (the ticket and the reference, where
   real bugs turn up), once per ticket. Failures and findings go back to the implementer, who
   fixes them all in one follow-up commit carrying the playtest record. The fixes aren't
   reviewed again: the coordinator re-runs the checks and the affected test steps, and anything
   found later becomes a new ticket, not another round.
5. **Ship:** the coordinator adds the ticket's changelog entry, commits it, pushes, and
   publishes as the config says.
6. **Report:** a few lines for its hand-back, then the next ticket.

## When it stops

The coordinator hands back to the main thread, which shows you why it stopped and its report
for each ticket it worked.

- Setup found the loop open: M0's tickets are filed for you to close with Claude.
- **The tickets you named have shipped** (or the rest were skipped, and it says why). It never
  goes on to their siblings.
- **The milestone is done:** it writes the milestone's summary, tells you what shipped and
  what's left for you (`ready-for-human` tickets, tickets filed for triage), and waits. It never
  starts the next milestone on its own.
- The remaining tickets are all blocked or `ready-for-human`.
- Something needs you in person: a click in a running app, a device check, credentials, a stuck
  tool.
- A push, publish or check fails in a way a fix can't safely cover.
- **The daily cap is reached.** Before each dispatch and each ship, the loop checks how much of
  your plan's weekly usage today has taken. At the cap, or if it can't tell, it stops before
  dispatching or shipping anything, and tells you today's use and where the ticket in hand
  stands. To go on today, raise the cap in the loop config; otherwise run it again tomorrow.
- Anything else your config lists.

## Models

Each role's model comes from the config: the coordinator, the implementer and the two
reviewers. A config without a coordinator model runs it on the implementer's. The default
suggestion, from a trial where Opus and Sonnet implemented the same ticket side by side: **Opus
for the implementer and the Spec reviewer, Sonnet for the Standards reviewer.** Sonnet's implementer was about 40% faster but
missed a detail in the reference source that Opus got right; the Spec reviewer caught it, which
is why that review stays on the stronger model.

Each role's **effort** comes from the config too, next to its model, and is passed to the
subagent's dispatch (`low`, `medium`, `high`, `xhigh`, `max`). The defaults, which a config
without efforts uses without asking: **implementer `low`, coordinator `medium`, Spec reviewer
`high`**, and the Standards reviewer at `usual` (dispatched without an effort parameter). The
Spec reviewer is where real bugs turn up, so it stays thorough while the implementer runs light.
The trade-off: each ticket gets one fix pass that isn't reviewed again, so what a low-effort
implementer misses either lands in a low-effort fix pass or becomes a follow-up ticket. Raise
the implementer's effort if that happens often. To change a role's effort, edit its line in the
config's Models section:

```
- Implementer: Opus, medium effort.
- Standards reviewer: Sonnet, low effort.
```

When a run starts, the main thread previews every role as the run uses them, defaults
applied, under the ready count:

```
M1: 7 ready, about 2 coordinators.
Coordinator: Opus, medium · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high
```

Per-role effort needs Claude Code 2.1.292 or later. A model runs the highest level it supports
at or below the one asked for, and some older models don't support effort at all (see Claude
Code's model configuration docs). `CLAUDE_CODE_EFFORT_LEVEL`, if set, overrides every role's.

## Tips

- **Shared tree:** the coordinator commits its own edits (changelog, milestone summary) at
  once, so they never end up in an implementer's commit.
- **Side work during a run:** the main thread is yours, but it shares the working tree with the
  coordinator. Code edits you make there while a run is going are visible to its test runs, and
  can break a test. For code investigations during a run, use a worktree (`claude --worktree`,
  or `git worktree add`).
- **Stopping:** stop the coordinator in the agent list to stop the loop.
- **One running app:** tickets that share one app session, simulator or game engine go one at a
  time; parallel worktrees only pay off when nothing they test is shared. Wider concurrency is
  `/implement-spec`'s job.
- **After a restart,** run the same command again; the config and the tickets carry the state.

## Install for a team

Commit this to the project's `.claude/settings.json`, so everyone working in it gets the
plugin:

```json
{
  "extraKnownMarketplaces": {
    "ticket-loop": { "source": { "source": "github", "repo": "jhnhnsn/ticket-loop" } }
  },
  "enabledPlugins": { "ticket-loop@ticket-loop": true }
}
```

## Updating

```sh
claude plugin marketplace update ticket-loop
claude plugin update ticket-loop
```
