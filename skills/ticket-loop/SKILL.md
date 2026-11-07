---
name: ticket-loop
description: Work a parent issue's tickets, or just the tickets named, one at a time to shipped, in a background coordinator subagent so the main thread stays free (fresh implementer subagent, a test queue run by the coordinator, independent two-axis review, push, publish), asking the user only for their decisions, from the main thread.
disable-model-invocation: true
---

Ship the tickets under a parent (a milestone, or a spec or map issue), or just the tickets named, one at a time, each built by a fresh implementer subagent, tested from the test queue, reviewed by fresh reviewer subagents, then pushed and published. The loop runs in two roles:

- You are the **launcher**, in the main thread: setup, resolving the argument, dispatching the coordinator, asking the user its decisions, and showing the user what it hands back. You keep no ticket's working detail, and the main thread stays free for the user while the loop runs.
- The **coordinator** is this plugin's `ticket-loop:coordinator` agent, a subagent that runs the loop: frontier, research (opt-in), implement, test queue, review, ship, report, ticket after ticket, dispatching researcher, implementer and reviewer subagents of its own. It ships the config's **ticket budget** of tickets, so its context stays small; a parallel build in hand finishes first, and can go past the budget. It hands back **decision needed** (a decision that's the user's: you ask it, then resume the coordinator with the answer), **cap reached** (the daily cap is reached or can't be read: you ask the cap question, then resume it), **parallel offer** (independent ready tickets to build side by side: you ask the user, then resume it), **budget reached** (you start a fresh coordinator, which carries on from the tracker), or a **stop condition**, which ends the run; each carries its per-ticket reports. Its steps are in its definition, [`agents/coordinator.md`](../../agents/coordinator.md).

The argument is either a parent or one or more tickets (`/ticket-loop 120`, `/ticket-loop v1`, `/ticket-loop 82`, `/ticket-loop 82 84 85`). A parent is whatever holds tickets in the loop config's tracker: an issue with sub-issues, or a milestone by name; any other issue is a ticket.

The **loop config**, `docs/agents/ticket-loop.md`, says how this project's tickets are found, built, tested, shipped and written up, and which model and effort run each role. Both roles read it.

**Bash rules.** You follow the coordinator's Bash rules ([`agents/coordinator.md`](../../agents/coordinator.md), Bash rules), in setup too: change files with Edit or Write, one plain command per Bash call with no chains, loops, variables or pipes of any kind, tickets read with the config's read command, tokencount run as its skill says. A refused command means rewrite it simpler and try again.

**Commit messages.** Your commits, such as the loop config's in setup, follow the coordinator's commit message rule ([`agents/coordinator.md`](../../agents/coordinator.md), Commit messages).

**Writing.** When the config's `## Writing` section names `ASD-STE100`, your messages to the user, your questions and the preview's prose follow the coordinator's writing rule ([`agents/coordinator.md`](../../agents/coordinator.md), Writing rule); the bars and the roles line stay as they are. So do the comments you post on tickets. Without the section, write as usual.

## Roles

The run has five roles: the coordinator, the researcher, the implementer, the Standards reviewer and the Spec reviewer. Each takes its model and its **effort** from the config's Models section (`Implementer: Opus, low effort.`). Whoever dispatches a role passes its effort as the Agent tool's `effort` parameter (`low`, `medium`, `high`, `xhigh`, `max`): you for the coordinator, the coordinator for the researchers, implementers and reviewers. The config is the user's explicit choice of effort, so pass it. `usual` means the role is dispatched without an `effort` parameter, at its usual effort.

What the config leaves out, the defaults fill, without asking (a config written before effort existed has none):

- **Coordinator:** the implementer's model; `medium` effort.
- **Researcher:** Haiku; `usual` effort (a config written before the researcher existed has no line for it). Either way it runs only on tickets labelled `research`.
- **Implementer:** `low` effort.
- **Standards reviewer:** `usual` effort.
- **Spec reviewer:** `high` effort.

The **roles line** is each role's model and effort with the defaults applied, in that order, the model's name capitalized, and the researcher followed by `(opt-in)`, since it runs only on tickets carrying the `research` label: `Coordinator: Opus, medium · Researcher: Haiku, usual (opt-in) · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high`. Step 2 previews it, and the coordinator's brief carries it, so the run dispatches each role as the preview said.

## Concurrency

The config's Concurrency section gives the **concurrency mode** and the **concurrency limit**, the most tickets built at once. Read the mode by matching the section's full text against these forms:

- `One at a time.`: one implementer, one ticket.
- `Parallel worktrees: at most <N> at once.`: independent ready tickets build side by side, up to the limit, with no prompt.
- `Suggest and ask: at most <N> at once.`: the user accepts or declines each new set of independent ready tickets.

A config with any other text keeps working, and setup doesn't ask again. Other text that offers parallel worktrees is suggest and ask, as such a config always asked. All remaining text, or no section, is one at a time. The limit is the number the text gives, or 2 without one.

The **parallel set** is the first tickets up to the limit, in the run's order, that are open and ready-for-agent with no open blockers. Tickets with open blockers never count, so tickets blocked on each other make no set. Fewer than two tickets is no set, and nobody asks anything. A set is the same set whatever its order.

The **answered sets** are the sets the user accepted or declined in this run. You keep them for the whole run and give them in every coordinator's brief, so the loop asks no set twice.

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
- at a **parallel offer** hand-back, under its reports in step 9's "answer given" message, after the coordinator is resumed. Read them before any question, but print nothing of them before it;
- at a **budget reached** hand-back, under its reports in step 7's "took over" message, after the fresh coordinator's dispatch. A handover shows nothing else of the preview.

## Steps

0. **Setup.** With no loop config in the repo, run setup first, as [`SETUP.md`](SETUP.md) says. It grills the user, writes the config, and proves the loop closes ([`CLOSED-LOOP.md`](CLOSED-LOOP.md)). Done when `docs/agents/ticket-loop.md` is committed and every leg is closed, or M0's tickets are filed (a stop: tell the user, and dispatch nothing). A loop config written before the daily cap existed has no Daily cap section: ask setup's Daily cap question alone, prove the Cap leg, and add the answer to the config, committed, before dispatching. In the same way, a loop config with no Status line section gets a one-time offer:
   - Ask setup's status line offer alone (SETUP.md step 3).
   - Add the `## Status line` section with the answer, as SETUP.md step 4 says.
   - If the repo's `.gitignore` does not list `.ticket-loop-status`, add it.
   - Commit the changed files before you dispatch.

   With the section in the config, don't ask again.

1. **Resolve the argument.** Work out from the config's tracker what the run is: a parent, or the tickets named, in the order given. With no argument, take the parent the config says to work next, and say which. Check each issue or milestone exists; if one doesn't, say so and stop, dispatching nothing.

   In suggest and ask mode (see Concurrency above), ask the **offer question** now, since the coordinator can't ask:
   - Read the blockers of the run's ready tickets, as the config's tracker says, and work out the parallel set. With no set, ask nothing.
   - With a set, ask the user with one AskUserQuestion that names its tickets, with two options: **Accept** (recommended; build them side by side in worktrees) and **Decline** (for this set only: build its first ticket; a new set asks once).
   - Add the answer to the answered sets.
   - Without AskUserQuestion (a headless run), or if a blockers read fails, ask nothing and answer nothing: the coordinator reads the blockers itself, and step 1 of its definition covers a headless run.

   Then count the run for step 2's preview:
   - **Ready count:** its ready tickets (the open ready-for-agent tickets under the parent, blocked or not, since blockers ship as the run goes; or the named tickets that are open and ready-for-agent; this is the run's size, not the parallel set), then the coordinators they take: the count divided by the ticket budget, rounded up, at least 1. The line opens with the run name exactly as this step gives it: `M1: 7 ready, about 2 coordinators.` for a milestone named `M1`, `#120: 7 ready, about 2 coordinators.` for issue parent #120, `#82: 1 ready, about 1 coordinator.` for a named ticket. The ticket budget is the config's Ticket budget; a config without one uses 4, without asking.
   - **Progress:** the two progress bars (see Progress above).
   - **Roles:** the roles line (see Roles above).

   The run name is the milestone's own name, or the issue numbers: `M1` for a milestone named `M1`, `#120` for an issue parent, `#82 #84` for named tickets. `M1` is the name of a milestone, not a prefix, so never write `M120` for issue #120.

   Done when you can name the run (`M1`, `#120`, `#82 #84`), any offer question is answered and you have the preview's lines: the ready count, the two bars and the roles line.

2. **Dispatch the coordinator.** Use the Agent tool with `subagent_type` `ticket-loop:coordinator`, in the background, on the coordinator's model, passed as an alias (`opus`, `sonnet`, `haiku`, `fable`), and with the coordinator's effort as the Agent tool's `effort` parameter, both as the roles line gives them (an effort of `usual`: leave `effort` out). Label it (the Agent tool's `description`) `ticket-loop: <what it runs> coordinator <n>`: the run as step 1 named it, and `<n>` counting this run's coordinators from 1 (`ticket-loop: M1 coordinator 1`, `ticket-loop: #82 #84 coordinator 1`). The `ticket-loop:` prefix sets it apart from the per-ticket subagents it dispatches. Its brief names the run (the parent, or the tickets in order), gives the ticket budget, the roles line, the concurrency mode and limit (`Concurrency: suggest and ask, at most 2.`) and the answered sets (`Answered sets: #82 #84 accepted; #85 #86 declined.`, or `none`), and points at the loop config. If the user answered **keep going today** to the cap question earlier in this run, and today's local date (`date +%F`) is the date recorded with it, the brief says so, with that date, so the coordinator skips the cap check that day and doesn't ask again (step 6).

   Once the call returns, tell the user the coordinator is running, in a message that opens with the run's **preview**, these lines in this order:
   - step 1's ready count, with the run name exactly as step 1 gives it;
   - step 1's two progress bars, Tickets then Usage;
   - the roles line.

   ```
   M1: 7 ready, about 2 coordinators.
   Tickets  [███░░░░░░░] 3 of 10 shipped
   Usage    [████░░░░░░] 6.1% of the week today, cap 14.3%
   Coordinator: Opus, medium · Researcher: Haiku, usual (opt-in) · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high
   ```

   This example runs a milestone named `M1`. For issue parent #120, the first line is `#120: 7 ready, about 2 coordinators.`, with no `M`.

   Then, in a line, say that the coordinator is running, that the user can watch it (and its test queue) in the agent view, and that the main thread is theirs meanwhile. The user, in a headless run too, sees only what you write as text, so write the preview out every time: lines worked out in your thinking aren't shown. End your turn: its hand-back wakes you.

3. **While it runs**, the main thread is the user's: answer what they ask as usual. The coordinator's tests and commits see the working tree, so code edits during a run belong in a worktree: make none yourself for the loop, and if the user asks for some, suggest a worktree. Asked "how's the agent doing?", answer from the coordinator's latest state without disturbing it. Don't send it a message for this. Read these, in this order:
   - the status file (see Status file below);
   - the tail of its transcript (the output file its dispatch named);
   - the tracker;
   - `git log`.

   **Status file.** The coordinator writes its state to `.ticket-loop-status` at the root of the main checkout, as one line: `#121 · test queue · running the browser suite · since 14:02 · 0/1 shipped · <compact roles>` ([`agents/coordinator.md`](../../agents/coordinator.md), Status file). To find the root, take the parent folder of `git rev-parse --path-format=absolute --git-common-dir`. Read the file with the Read tool. To get its age, run `date -r <path> +%s` and compare it with `date +%s`.

   **No run.** The launcher and the status line script use the same rule. There is no run when one of these is true:
   - there is no status file;
   - its line does not have the six fields;
   - its step is `hand-back`;
   - the file is older than 12 hours (a backstop only).

   **End the status.** When the run ends, write the `hand-back` step to the status file. Do this at each stop (steps 5, 6 and 8), and when the coordinator stops or fails without a hand-back. The user can stop it in the agent list, for example. Read the file first, then Write the same line with the step changed to `hand-back`.

   **Background notices.** Claude Code can tell you that a coordinator "is waiting on its own background work". For each notice, read the status file and write one line. Give the ticket, its step, what runs now, and the minutes since the `since` time. Add the Tickets progress bar from the file's counts:
   `#121 is in the test queue, running the browser suite (4 min). Tickets [░░░░░░░░░░] 0 of 1 shipped.`
   If the step and what runs now are the same as in your last line, write a short line: `Still running the browser suite on #121 (6 min).` If the No run rule is true, write that you have no status yet. Don't guess.

   **Status line.** The plugin has a status line script, `scripts/ticket-loop-statusline`, for Claude Code's `statusLine` setting. Setup offers to add it ([`SETUP.md`](SETUP.md)). It shows the status file and the Usage progress bar under the input box, and does not scroll. It makes no GitHub call.

4. **Show the hand-back.** Each ticket's report it carries (what shipped, how many research passes ran, trimmed ones marked (or research skipped, or research: not requested), decisions they answered and any taken on their behalf, tickets filed), any `took decline` line, with the two progress bars under the reports, read fresh at the moment Progress above gives. Write them out as text now, or hold them for a later message, as Progress says for this kind of hand-back. Keep none of the coordinator's working detail.

5. **Relay a decision.** When the hand-back is **decision needed**, ask the user with AskUserQuestion: the ticket in the question, the options with the recommendation first (marked as recommended). Write nothing to the user before the question. Record their answer on the ticket as a comment, as the config's tracker says. Then resume the same coordinator with SendMessage, to the agent ID its dispatch returned, with the answer and a pointer to the comment. Don't dispatch a new coordinator for this. Once SendMessage returns, tell the user, in one message, in this order:
   - the hand-back's reports (step 4), if it carried any;
   - the two progress bars step 4 read;
   - one line saying their answer is recorded on the ticket, as a comment, and the coordinator is resumed.

   As with step 2's preview, write it all out as text every time: lines worked out in your thinking aren't shown. End your turn: its next hand-back wakes you, and you go back to step 4.

   Without AskUserQuestion (a headless run), treat it as a stop instead, in one final message: the report of every ticket shipped this run and every `took decline` line, from every coordinator's hand-backs (not only this one's, since the last message may be all the user reads), then step 4's bars, then the ticket, the options and the recommendation, recommendation first; the user records their answer on the ticket, and running the same command again carries on from it.

6. **Relay the cap.** When the hand-back is **cap reached**, ask the user the cap question with AskUserQuestion: the use and the limit as the hand-back gives them, or that the cap can't be read and why, and the ticket in hand and where it stands, in the question, with three options: **Stop here**, **Finish this ticket or one more**, **Keep going today**. Recommend none. Write nothing to the user before the question. Then resume the same coordinator with SendMessage, to the agent ID its dispatch returned, with the answer, and, for keep going today, today's local date (`date +%F`). Don't dispatch a new coordinator for this. Remember a keep going today answer and its date for the rest of the run: every later coordinator's brief that day carries it (steps 2 and 7). Once SendMessage returns, tell the user, in one message, in this order:
   - the hand-back's reports (step 4), if it carried any;
   - the two progress bars step 4 read;
   - one line saying their answer and that the coordinator is resumed.

   Write it all out as text every time. End your turn: its next hand-back wakes you, and you go back to step 4. Stop here comes back as a stop condition (step 8). Finish this ticket or one more comes back as cap reached again once that ticket ships, and you ask again.

   Without AskUserQuestion (a headless run), treat it as a stop instead, in one final message: the report of every ticket shipped this run and every `took decline` line, from every coordinator's hand-backs, then step 4's bars, then the ticket in hand, where it stands and what's committed locally. To go on today, the user raises the cap in the loop config, or runs the loop interactively and answers the question; otherwise the run waits until the limit grows: tomorrow for a per day cap, or, for a rolling one, the next day of the usage week, when the allowance grows by the daily share at the week's reset time.

7. **Hand over.** When the hand-back is **budget reached**, its next ticket shows the frontier still has a ready one: without asking, dispatch a fresh coordinator with step 2's Agent call, numbered one up (`ticket-loop: M1 coordinator 2`), with the same budget, roles line, concurrency mode and limit, all the answered sets so far, and the keep going today line exactly as step 2 gives it, and without the preview, which the first coordinator's message already gave. It rebuilds the frontier from the tracker. For named tickets, its brief names only those not yet shipped, in the original order, as the hand-backs' reports show them.

   Before the dispatch, read no ticket, and don't judge what the next ticket asks. A decision on it belongs to the fresh coordinator, which hands it back as **decision needed** (step 5). Write nothing to the user before the dispatch. Once the call returns, read the progress bars, then tell the user, in place of step 2's message, in one message, in this order:
   - the hand-back's reports (step 4);
   - the two progress bars;
   - one line saying which coordinator took over, with any skipped tickets or ready-for-human notes the hand-back carried.

   As with step 2's preview, write it all out as text every time, in a headless run too: lines worked out in your thinking aren't shown. End your turn: its hand-back wakes you.

8. **Show the stop.** When the hand-back is a **stop condition**, show it, with what the user needs to know or do, then what's next. The run ends here:
   - **The daily cap**, at stop here (step 6) or in a headless run (step 6's last paragraph): step 4's Usage bar gives the use and the limit, so don't repeat the coordinator's figures; give the ticket in hand, left as it is, and what's committed locally and not pushed. A later run picks it up.
   - Anything else: as the coordinator said it.

9. **Relay a parallel offer.** When the hand-back is **parallel offer**, ask the user the offer question with one AskUserQuestion that names its tickets, with step 1's two options, Accept first and recommended. Write nothing to the user before the question. Without AskUserQuestion, ask nothing: the answer is decline, and your message says the run took decline because it couldn't ask. Add the answer to the answered sets, and post no comment on a ticket. Then resume the same coordinator with SendMessage, to the agent ID its dispatch returned, with the answer. Don't dispatch a new coordinator for this. Never message the coordinator's own subagents. Once SendMessage returns, tell the user, in one message, in this order:
   - the hand-back's reports (step 4), if it carried any;
   - the two progress bars step 4 read;
   - one line saying their answer and that the coordinator is resumed.

   Write it all out as text every time. End your turn: its next hand-back wakes you, and you go back to step 4.

Stopping the coordinator in the agent list stops the loop. Then write the `hand-back` step to the status file (step 3, End the status). To carry on after any stop or restart, run the same command again; the config and the tickets carry the state.
