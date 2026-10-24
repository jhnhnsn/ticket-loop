# ticket-loop

A Claude Code plugin that ships a milestone's tickets one at a time, without check-ins.
Claude orchestrates; each ticket is built by a fresh subagent, so every ticket starts with a
clear context:

1. **Frontier:** the next open, ready-for-agent ticket under the parent issue whose blockers
   are all closed.
2. **Implement:** a fresh implementer subagent builds it test-first, runs the checks, runs or
   playtests it as your `CLAUDE.md` says, and commits locally.
3. **Decide:** where the ticket and the code disagree in a way you might care about, it stops
   and reports options. Claude asks you, records your answer on the ticket, and carries on.
4. **Review:** two fresh reviewer subagents (standards and spec) check the commit; the
   implementer fixes what they find.
5. **Ship:** push, then publish or deploy as your `CLAUDE.md` says.
6. **Report:** a few lines on what shipped, then the next ticket.

It stops only when a decision is yours, the milestone is done, the next ticket needs a human,
something needs you in person (a click, a device, credentials), or a push or publish fails.

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
  official marketplace): the subagents use its `tdd` and `code-review` skills.
- A project set up with `/setup-matt-pocock-skills`, so `docs/agents/issue-tracker.md` says
  where tickets live, their labels and how to find the frontier.
- A `CLAUDE.md` that says how to run the checks, how to run or playtest the work, and how to
  publish or deploy.
