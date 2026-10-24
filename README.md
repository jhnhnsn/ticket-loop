# ticket-loop

A Claude Code plugin that ships a milestone's tickets one at a time, without check-ins.
Claude orchestrates; each ticket is built by a fresh subagent, so every ticket starts with a
clear context:

1. **Frontier:** the next open, ready-for-agent ticket under the parent issue whose blockers
   are all closed.
2. **Implement:** a fresh implementer subagent builds it test-first, runs the automated checks,
   commits locally, and hands over a test plan.
3. **Decide:** where the ticket and the code disagree in a way you might care about, it stops
   and reports options. Claude asks you, records your answer on the ticket, and carries on.
4. **Test and review:** Claude runs the test plan itself from a test queue, one ticket at a
   time in the main thread (where you can watch), as your `CLAUDE.md` says; meanwhile two fresh
   reviewer subagents (standards and spec) check the commit. The implementer fixes what they
   find.
5. **Ship:** push, then publish or deploy as your `CLAUDE.md` says.
6. **Report:** a few lines on what shipped, then the next ticket.

It stops only when a decision is yours, the milestone is done, the next ticket needs a human,
something needs you in person (a click, a device, credentials), or a push or publish fails.

## First run

The first time it runs in a repo, it grills you (Matt Pocock's `grilling` skill) about the project: where tickets live and how milestones hold them, the checks command, what gets playtested and how, a reference to stay faithful to, how to ship, where the changelog and milestone summaries go and who reads them, extra stops, the model for each role, commit style, and concurrency. It looks up what the repo already says first, so most questions arrive with an answer to confirm. The answers go to `docs/agents/ticket-loop.md` (with a pointer in `CLAUDE.md`), which every later run reads; edit it to change them, or delete it to be grilled again.

## Use

```
/ticket-loop:ticket-loop 120
```

with the parent issue (milestone or spec) whose tickets to ship. With none, it takes the
current milestone from the repo's roadmap.

## Install

For yourself (all projects):

```sh
claude plugin marketplace add jhnhnsn/ticket-loop
claude plugin install ticket-loop@ticket-loop
```

For everyone working in a project, commit this to the project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ticket-loop": { "source": { "source": "github", "repo": "jhnhnsn/ticket-loop" } }
  },
  "enabledPlugins": { "ticket-loop@ticket-loop": true }
}
```

## Requires

- [Matt Pocock's skills](https://github.com/mattpocock/skills) (`mattpocock-skills` in the
  official marketplace): the loop uses its `grilling`, `tdd` and `code-review` skills.
- Helpful, not required: `/setup-matt-pocock-skills` run in the project first. Its
  `docs/agents/issue-tracker.md` answers the setup's ticket questions before they're asked.
