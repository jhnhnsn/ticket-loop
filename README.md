# ticket-loop

A Claude Code plugin that ships a milestone's tickets one at a time, without check-ins. Claude
orchestrates: each ticket is built by a fresh implementer subagent (so every ticket starts with
a clear context), tested by Claude in the main thread where you can watch, reviewed by two fresh
reviewer subagents, then pushed, published and written up. It stops only when it needs you,
and at the end of each milestone.

## Getting started

1. **Install Matt Pocock's skills**, which the loop builds on (`grilling`, `tdd`,
   `code-review`):

   ```sh
   claude plugin install mattpocock-skills@claude-plugins-official
   ```

2. **Install ticket-loop:**

   ```sh
   claude plugin marketplace add jhnhnsn/ticket-loop
   claude plugin install ticket-loop@ticket-loop
   ```

   Restart Claude Code so the new skill is listed.

3. **Optional: run `/setup-matt-pocock-skills`** in your project. It records where tickets
   live and what the triage labels are (`docs/agents/`), which answers the loop's first
   questions before they're asked.

4. **Have tickets under a parent issue.** A milestone or spec issue whose sub-issues are the
   tickets, labelled `ready-for-agent`, each saying what it blocks on. `/to-spec` and
   `/to-tickets` (Matt Pocock's) make them from a plan.

5. **Run it** with the parent issue, or with the tickets you want shipped:

   ```
   /ticket-loop:ticket-loop 120        # every ticket under parent #120
   /ticket-loop:ticket-loop 82         # just ticket #82
   /ticket-loop:ticket-loop 82 84 85   # just these three
   ```

   The first run in a repo grills you before it starts (see [First run](#first-run)); after
   that it goes straight to the first ticket.

6. **Let it work.** It reports after each ticket in a few lines: what shipped, any decision
   taken on your behalf, tickets filed, what's next. Ask "how's the agent doing?" at any time.
   Push and publish commands ask permission unless your settings allow them; allow them to
   keep the loop unattended.

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
| Models | the model for the implementer, the Standards reviewer and the Spec reviewer |
| Commits | message style, closing keyword, attribution lines |
| Concurrency | one ticket at a time, or parallel worktrees |

The answers go to **`docs/agents/ticket-loop.md`**, the loop config, with a pointer line in
CLAUDE.md; both are committed. Every later run reads it. Edit it to change an answer, or delete
it to be grilled again.

Then setup **proves the loop closes** by doing each leg of one ticket's cycle itself:

- **Check:** the checks command passes.
- **Run:** the app starts without a click.
- **Drive:** a tool operates the app and reads its state, and a test hook takes effect.
- **Ship:** pushing and publishing need no prompt.
- **Record:** the changelog is in place.

Each leg that can't be proven becomes a ticket under an **M0 · Closed loop** parent. The loop
then stops, and you close M0 with Claude in an ordinary session before running it again: the
loop can't test anything until its own legs close. Later tickets keep the cycle closed by
building any test hook their test plan needs. See
[`CLOSED-LOOP.md`](skills/ticket-loop/CLOSED-LOOP.md).

## How each ticket goes

1. **Frontier:** the next open `ready-for-agent` ticket under the parent whose blockers are all
   closed, in the config's order. Run with tickets instead, it's the next one named, in the order
   given; a named ticket that isn't `ready-for-agent`, or waits on an open ticket you didn't name,
   is skipped and you're told why.
2. **Implement:** a fresh implementer subagent builds it test-first at the seams the ticket
   names, runs the checks, commits locally (staging only its own files), and reports "ready to
   test" with a step-by-step **test plan** and the expected results.
3. **Decide:** where the ticket and the reference disagree, the config's rule settles it.
   Anything still yours comes to you as a question with a recommendation; your answer is
   recorded on the ticket as a comment and goes back to the same subagent.
4. **Test and review:** Claude runs the test plan itself from the **test queue**, one ticket
   at a time in the main thread, saying what it's about to run so you can watch. Meanwhile two
   fresh reviewer subagents check the commit: **Standards** (the repo's conventions) and
   **Spec** (the ticket and the reference, where real bugs turn up). Failures and findings go
   back to the implementer, who fixes them in a follow-up commit carrying the playtest record.
5. **Ship:** Claude adds the ticket's changelog entry, commits it, pushes, and publishes as the
   config says.
6. **Report:** a few lines to you, then the next ticket.

## When it stops

- A decision is yours (it asks, then carries on).
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
- Anything else your config lists.

## Models

Each role's model comes from the config. The default suggestion, from a trial where Opus and
Sonnet implemented the same ticket side by side: **Opus for the implementer and the Spec
reviewer, Sonnet for the Standards reviewer.** Sonnet's implementer was about 40% faster but
missed a detail in the reference source that Opus got right; the Spec reviewer caught it, which
is why that review stays on the stronger model.

## Tips

- **Shared tree:** Claude commits its own edits (changelog, docs) at once, so they never end up
  in an implementer's commit.
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
