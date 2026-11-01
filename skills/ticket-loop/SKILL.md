---
name: ticket-loop
description: Work a parent issue's tickets, or just the tickets named, one at a time to shipped, in a background coordinator subagent so the main thread stays free (fresh implementer subagent, a test queue run by the coordinator, independent two-axis review, push, publish), stopping only for the user's decisions.
disable-model-invocation: true
---

Ship the tickets under a parent (a milestone, or a spec or map issue), or just the tickets named, one at a time, each built by a fresh implementer subagent, tested from the test queue, reviewed by fresh reviewer subagents, then pushed and published. The loop runs in two roles:

- You are the **launcher**, in the main thread: setup, resolving the argument, dispatching the coordinator, and showing the user what it hands back. You keep no ticket's working detail, and the main thread stays free for the user while the loop runs.
- The **coordinator** is this plugin's `ticket-loop:coordinator` agent, a subagent that runs the loop: frontier, implement, test queue, review, ship, report, ticket after ticket, dispatching implementer and reviewer subagents of its own. It ends by handing back a **stop condition** with its per-ticket reports. Its steps are in its definition, [`agents/coordinator.md`](../../agents/coordinator.md).

The argument is either a parent or one or more tickets (`/ticket-loop 120`, `/ticket-loop v1`, `/ticket-loop 82`, `/ticket-loop 82 84 85`). A parent is whatever holds tickets in the loop config's tracker: an issue with sub-issues, or a milestone by name; any other issue is a ticket.

The **loop config**, `docs/agents/ticket-loop.md`, says how this project's tickets are found, built, tested, shipped and written up, and which model runs each role. Both roles read it.

## Steps

0. **Setup.** With no loop config in the repo, run setup first, as [`SETUP.md`](SETUP.md) says. It grills the user, writes the config, and proves the loop closes ([`CLOSED-LOOP.md`](CLOSED-LOOP.md)). Done when `docs/agents/ticket-loop.md` is committed and every leg is closed, or M0's tickets are filed (a stop: tell the user, and dispatch nothing). A loop config written before the daily cap existed has no Daily cap section: ask setup's Daily cap question alone, prove the Cap leg, and add the answer to the config, committed, before dispatching.

1. **Resolve the argument.** Work out from the config's tracker what the run is: a parent, or the tickets named, in the order given. With no argument, take the parent the config says to work next, and say which. Check each issue or milestone exists; if one doesn't, say so and stop, dispatching nothing. Then ask the config's offers, since the coordinator can't ask: where the config offers parallel worktrees and the run has two or more ready tickets that don't block each other, ask the user to accept or decline. Done when you can name the run (`M1`, `#120`, `#82 #84`) and the offers are answered.

2. **Dispatch the coordinator.** Use the Agent tool with `subagent_type` `ticket-loop:coordinator`, in the background, on the config's coordinator model (a config without one uses its implementer model), passed as an alias (`opus`, `sonnet`, `haiku`, `fable`). Label it (the Agent tool's `description`) `ticket-loop: <what it runs> coordinator <n>`: the run as step 1 named it, and `<n>` counting this run's coordinators from 1 (`ticket-loop: M1 coordinator 1`, `ticket-loop: #82 #84 coordinator 1`). The `ticket-loop:` prefix sets it apart from the per-ticket subagents it dispatches. Its brief names the run (the parent, or the tickets in order), gives the user's answers to the offers, and points at the loop config. Then tell the user in a line that the coordinator is running, that they can watch it (and its test queue) in the agent view, and that the main thread is theirs meanwhile. End your turn: its hand-back wakes you.

3. **While it runs**, the main thread is the user's: answer what they ask as usual. The coordinator's tests and commits see the working tree, so code edits during a run belong in a worktree: make none yourself for the loop, and if the user asks for some, suggest a worktree. Asked "how's the agent doing?", answer from the coordinator's latest state without disturbing it: the tail of its transcript (the output file its dispatch named), the tracker and `git log`. Don't send it a message for this.

4. **Show the hand-back.** Show the user each ticket's report (what shipped, any decision taken on their behalf, tickets filed) and the stop condition, with what they need to know or do, then what's next. Keep none of the coordinator's working detail. The run ends here:
   - **A decision that's theirs:** give the ticket, the options and the recommendation, recommendation first. When they answer, record it on the ticket as a comment; running the same command again carries on from the ticket.
   - **The daily cap:** give today's use, the cap, and the ticket in hand and where it stands. To go on today, the user raises the cap in the loop config; otherwise the run waits for tomorrow.
   - Anything else: as the coordinator said it.

Stopping the coordinator in the agent list stops the loop. To carry on after any stop or restart, run the same command again; the config and the tickets carry the state.
