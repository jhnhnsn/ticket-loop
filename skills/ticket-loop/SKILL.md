---
name: ticket-loop
description: Work a parent issue's tickets, or just the tickets named, one at a time to shipped, in a background coordinator subagent so the main thread stays free (fresh implementer subagent, a test queue run by the coordinator, independent two-axis review, push, publish), asking the user only for their decisions, from the main thread.
disable-model-invocation: true
---

Ship the tickets under a parent (a milestone, or a spec or map issue), or just the tickets named, one at a time, each built by a fresh implementer subagent, tested from the test queue, reviewed by fresh reviewer subagents, then pushed and published. The loop runs in two roles:

- You are the **launcher**, in the main thread: setup, resolving the argument, dispatching the coordinator, asking the user its decisions, and showing the user what it hands back. You keep no ticket's working detail, and the main thread stays free for the user while the loop runs.
- The **coordinator** is this plugin's `ticket-loop:coordinator` agent, a subagent that runs the loop: frontier, research, implement, test queue, review, ship, report, ticket after ticket, dispatching researcher, implementer and reviewer subagents of its own. It ships at most the config's **ticket budget** of tickets, so its context stays small. It hands back **decision needed** (a decision that's the user's: you ask it, then resume the coordinator with the answer), **cap reached** (the daily cap is reached or can't be read: you ask the cap question, then resume it), **budget reached** (you start a fresh coordinator, which carries on from the tracker), or a **stop condition**, which ends the run; each carries its per-ticket reports. Its steps are in its definition, [`agents/coordinator.md`](../../agents/coordinator.md).

The argument is either a parent or one or more tickets (`/ticket-loop 120`, `/ticket-loop v1`, `/ticket-loop 82`, `/ticket-loop 82 84 85`). A parent is whatever holds tickets in the loop config's tracker: an issue with sub-issues, or a milestone by name; any other issue is a ticket.

The **loop config**, `docs/agents/ticket-loop.md`, says how this project's tickets are found, built, tested, shipped and written up, and which model and effort run each role. Both roles read it.

**Bash rules.** You follow the coordinator's Bash rules ([`agents/coordinator.md`](../../agents/coordinator.md), Bash rules), in setup too: change files with Edit or Write, one plain command per Bash call with no chains, loops, variables or pipes of any kind, tickets read with the config's read command, tokencount run as its skill says. A refused command means rewrite it simpler and try again.

**Commit messages.** Your commits, such as the loop config's in setup, follow the coordinator's commit message rule ([`agents/coordinator.md`](../../agents/coordinator.md), Commit messages).

## Roles

The run has five roles: the coordinator, the researcher, the implementer, the Standards reviewer and the Spec reviewer. Each takes its model and its **effort** from the config's Models section (`Implementer: Opus, low effort.`). Whoever dispatches a role passes its effort as the Agent tool's `effort` parameter (`low`, `medium`, `high`, `xhigh`, `max`): you for the coordinator, the coordinator for the researchers, implementers and reviewers. The config is the user's explicit choice of effort, so pass it. `usual` means the role is dispatched without an `effort` parameter, at its usual effort.

What the config leaves out, the defaults fill, without asking (a config written before effort existed has none):

- **Coordinator:** the implementer's model; `medium` effort.
- **Researcher:** Haiku; `usual` effort (a config written before the researcher existed has no line for it).
- **Implementer:** `low` effort.
- **Standards reviewer:** `usual` effort.
- **Spec reviewer:** `high` effort.

The **roles line** is each role's model and effort with the defaults applied, in that order, the model's name capitalized, and the researcher followed by `(opt-in)`, since it runs only on tickets carrying the `research` label: `Coordinator: Opus, medium · Researcher: Haiku, usual (opt-in) · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high`. Step 2 previews it, and the coordinator's brief carries it, so the run dispatches each role as the preview said.

## Progress

The **progress bars** are two lines: how far through its tickets the run is, and how much of the daily cap today has used. Read them fresh each time you show them, from the tracker and tokencount, never from the coordinator's numbers.

```
Tickets  [███░░░░░░░] 3 of 10 shipped
Usage    [████░░░░░░] 6.1% of the week today, cap 14.3%
```

With a rolling cap, the Usage line reads `Usage    [█████░░░░░] 15.0% of the week so far, allowance 28.6% (day 2 of 7)`.

- **Tickets:** for a parent, its tickets (an issue's sub-issues, or a milestone's issues), open or closed, are the total; the closed ones are shipped. For named tickets, the total is the tickets the user named for the run, and the shipped are the named ones that are closed; after a handover, the total is still the run's original named set, not the fresh coordinator's shorter list.
- **Usage:** the use against the limit from the Skill tool's `tokencount:tokencount` `--json` report, worked out for the config's mode exactly as the coordinator's Daily cap section says ([`agents/coordinator.md`](../../agents/coordinator.md)), each to one decimal. The bars never stop the run: the coordinator's own cap check does that.
  - **Per day** (the config's Daily cap text doesn't start with `Rolling:`): `Usage    [bar] <today.percent_of_week>% of the week today, cap <share>%`.
  - **Rolling** (the text starts with `Rolling:`): `Usage    [bar] <week.percent_used>% of the week so far, allowance <allowance>% (day <d> of 7)`.
  - **Cap not applicable** (the config's Daily cap says so): `Usage    not applicable (no plan usage to read)`, with no bar and no tokencount read.
  - **Unreadable** (tokencount isn't installed or isn't available, its `usage_source` is `unavailable`, or the mode's fields are null, as the coordinator's Daily cap section lists them): `Usage    can't read today's usage`, with no bar.
- **Bars** are 10 cells wide, the filled cells `█` first, then the empty `░`, so filled + empty = 10. Work out the filled cells from this reading's numbers every time, and draw the bar anew; never copy an earlier bar, even when only the count changed:
  - **Tickets:** filled = round(10 × shipped ÷ total), halves up (0 when the total is 0). 3 of 10 fills 3; 1 of 3 fills 3; 2 of 3 fills 7 (`[███████░░░]`); 3 of 3 fills 10.
  - **Usage:** filled = round(10 × use ÷ limit), halves up, at most 10; the limit is the cap per day, the allowance rolling. 6.1% of a 14.3% cap fills 4; 4.0% fills 3; 16.0% fills 10; 15.0% of a 28.6% allowance fills 5.

  The labels are padded so both lines' second columns line up: `Tickets` then two spaces, `Usage` then four.

Read them before you write anything for the moment they show, and print them:

- at the start of a run, in step 2's preview, after the coordinator's dispatch;
- at a **stop condition** hand-back, under its reports (step 4), and at a **decision needed** or **cap reached** one in a headless run, where it's a stop (steps 5 and 6);
- at a **decision needed** or **cap reached** hand-back with AskUserQuestion, under its reports in step 5's "answer recorded" or step 6's "answer given" message, after the user answers and the coordinator is resumed. Read them before the question, but print nothing of them before it;
- at a **budget reached** hand-back, under its reports in step 7's "took over" message, after the fresh coordinator's dispatch. A handover shows nothing else of the preview.

## Steps

0. **Setup.** With no loop config in the repo, run setup first, as [`SETUP.md`](SETUP.md) says. It grills the user, writes the config, and proves the loop closes ([`CLOSED-LOOP.md`](CLOSED-LOOP.md)). Done when `docs/agents/ticket-loop.md` is committed and every leg is closed, or M0's tickets are filed (a stop: tell the user, and dispatch nothing). A loop config written before the daily cap existed has no Daily cap section: ask setup's Daily cap question alone, prove the Cap leg, and add the answer to the config, committed, before dispatching.

1. **Resolve the argument.** Work out from the config's tracker what the run is: a parent, or the tickets named, in the order given. With no argument, take the parent the config says to work next, and say which. Check each issue or milestone exists; if one doesn't, say so and stop, dispatching nothing. Then ask the config's offers, since the coordinator can't ask: where the config offers parallel worktrees and the run has two or more ready tickets that don't block each other, ask the user to accept or decline. Then count the run for step 2's preview:
   - **Ready count:** its ready tickets (the open ready-for-agent tickets under the parent, blocked or not, since blockers ship as the run goes; or the named tickets that are open and ready-for-agent), then the coordinators they take: the count divided by the ticket budget, rounded up, at least 1 (`M1: 7 ready, about 2 coordinators.`; `#82: 1 ready, about 1 coordinator.`). The ticket budget is the config's Ticket budget; a config without one uses 4, without asking.
   - **Progress:** the two progress bars (see Progress above).
   - **Roles:** the roles line (see Roles above).

   Done when you can name the run (`M1`, `#120`, `#82 #84`), the offers are answered and you have the preview's lines: the ready count, the two bars and the roles line.

2. **Dispatch the coordinator.** Use the Agent tool with `subagent_type` `ticket-loop:coordinator`, in the background, on the coordinator's model, passed as an alias (`opus`, `sonnet`, `haiku`, `fable`), and with the coordinator's effort as the Agent tool's `effort` parameter, both as the roles line gives them (an effort of `usual`: leave `effort` out). Label it (the Agent tool's `description`) `ticket-loop: <what it runs> coordinator <n>`: the run as step 1 named it, and `<n>` counting this run's coordinators from 1 (`ticket-loop: M1 coordinator 1`, `ticket-loop: #82 #84 coordinator 1`). The `ticket-loop:` prefix sets it apart from the per-ticket subagents it dispatches. Its brief names the run (the parent, or the tickets in order), gives the ticket budget, the roles line and the user's answers to the offers, and points at the loop config. If the user answered **keep going today** to the cap question earlier in this run, and today's local date (`date +%F`) is the date recorded with it, the brief says so, with that date, so the coordinator skips the cap check that day and doesn't ask again (step 6).

   Once the call returns, tell the user the coordinator is running, in a message that opens with the run's **preview**, these lines in this order:
   - step 1's ready count;
   - step 1's two progress bars, Tickets then Usage;
   - the roles line.

   ```
   M1: 7 ready, about 2 coordinators.
   Tickets  [███░░░░░░░] 3 of 10 shipped
   Usage    [████░░░░░░] 6.1% of the week today, cap 14.3%
   Coordinator: Opus, medium · Researcher: Haiku, usual (opt-in) · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high
   ```

   Then, in a line, say that the coordinator is running, that the user can watch it (and its test queue) in the agent view, and that the main thread is theirs meanwhile. The user, in a headless run too, sees only what you write as text, so write the preview out every time: lines worked out in your thinking aren't shown. End your turn: its hand-back wakes you.

3. **While it runs**, the main thread is the user's: answer what they ask as usual. The coordinator's tests and commits see the working tree, so code edits during a run belong in a worktree: make none yourself for the loop, and if the user asks for some, suggest a worktree. Asked "how's the agent doing?", answer from the coordinator's latest state without disturbing it: the tail of its transcript (the output file its dispatch named), the tracker and `git log`. Don't send it a message for this.

4. **Show the hand-back.** Each ticket's report it carries (what shipped, how many research passes ran (or research skipped, or research: not requested), decisions they answered and any taken on their behalf, tickets filed), with the two progress bars under the reports, read fresh now (see Progress above). Write them out as text now, or hold them for a later message, as Progress says for this kind of hand-back. Keep none of the coordinator's working detail.

5. **Relay a decision.** When the hand-back is **decision needed**, ask the user with AskUserQuestion: the ticket in the question, the options with the recommendation first (marked as recommended). Write nothing to the user before the question. Record their answer on the ticket as a comment, as the config's tracker says. Then resume the same coordinator with SendMessage, to the agent ID its dispatch returned, with the answer and a pointer to the comment. Don't dispatch a new coordinator for this. Once SendMessage returns, tell the user, in one message, in this order:
   - the hand-back's reports (step 4), if it carried any;
   - the two progress bars step 4 read;
   - one line saying their answer is recorded on the ticket, as a comment, and the coordinator is resumed.

   As with step 2's preview, write it all out as text every time: lines worked out in your thinking aren't shown. End your turn: its next hand-back wakes you, and you go back to step 4.

   Without AskUserQuestion (a headless run), treat it as a stop instead, in one final message: the report of every ticket shipped this run, from every coordinator's hand-backs (not only this one's, since the last message may be all the user reads), then step 4's bars, then the ticket, the options and the recommendation, recommendation first; the user records their answer on the ticket, and running the same command again carries on from it.

6. **Relay the cap.** When the hand-back is **cap reached**, ask the user the cap question with AskUserQuestion: the use and the limit as the hand-back gives them, or that the cap can't be read and why, and the ticket in hand and where it stands, in the question, with three options: **Stop here**, **Finish this ticket or one more**, **Keep going today**. Recommend none. Write nothing to the user before the question. Then resume the same coordinator with SendMessage, to the agent ID its dispatch returned, with the answer, and, for keep going today, today's local date (`date +%F`). Don't dispatch a new coordinator for this. Remember a keep going today answer and its date for the rest of the run: every later coordinator's brief that day carries it (steps 2 and 7). Once SendMessage returns, tell the user, in one message, in this order:
   - the hand-back's reports (step 4), if it carried any;
   - the two progress bars step 4 read;
   - one line saying their answer and that the coordinator is resumed.

   Write it all out as text every time. End your turn: its next hand-back wakes you, and you go back to step 4. Stop here comes back as a stop condition (step 8). Finish this ticket or one more comes back as cap reached again once that ticket ships, and you ask again.

   Without AskUserQuestion (a headless run), treat it as a stop instead, in one final message: the report of every ticket shipped this run, from every coordinator's hand-backs, then step 4's bars, then the ticket in hand, where it stands and what's committed locally. To go on today, the user raises the cap in the loop config, or runs the loop interactively and answers the question; otherwise the run waits until the limit grows: tomorrow for a per day cap, or, for a rolling one, the next day of the usage week, when the allowance grows by the daily share at the week's reset time.

7. **Hand over.** When the hand-back is **budget reached**, its next ticket shows the frontier still has a ready one: without asking, dispatch a fresh coordinator with step 2's Agent call, numbered one up (`ticket-loop: M1 coordinator 2`), with the same budget, roles line and offer answers, and the keep going today line exactly as step 2 gives it, and without the preview, which the first coordinator's message already gave. It rebuilds the frontier from the tracker. For named tickets, its brief names only those not yet shipped, in the original order. Write nothing to the user before the dispatch. Once the call returns, tell the user, in place of step 2's message, in one message, in this order:
   - the hand-back's reports (step 4);
   - the two progress bars step 4 read;
   - one line saying which coordinator took over, with any skipped tickets or ready-for-human notes the hand-back carried.

   As with step 2's preview, write it all out as text every time, in a headless run too: lines worked out in your thinking aren't shown. End your turn: its hand-back wakes you.

8. **Show the stop.** When the hand-back is a **stop condition**, show it, with what the user needs to know or do, then what's next. The run ends here:
   - **The daily cap**, at stop here (step 6) or in a headless run (step 6's last paragraph): step 4's Usage bar gives the use and the limit, so don't repeat the coordinator's figures; give the ticket in hand, left as it is, and what's committed locally and not pushed. A later run picks it up.
   - Anything else: as the coordinator said it.

Stopping the coordinator in the agent list stops the loop. To carry on after any stop or restart, run the same command again; the config and the tickets carry the state.
