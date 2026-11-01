---
name: ticket-loop
description: Work a parent issue's tickets, or just the tickets named, one at a time to shipped (fresh implementer subagent, a test queue run in the main thread, independent two-axis review, push, publish), stopping only for the user's decisions.
disable-model-invocation: true
---

Ship the tickets under a parent (a milestone, or a spec or map issue), or just the tickets named, one at a time, each built by a fresh **implementer subagent**, run or playtested by you from the **test queue** (in the main thread, where the user can watch), reviewed by fresh **reviewer subagents**, then pushed and published. You are the **orchestrator**: you hold the frontier, the user's decisions and the reports, never a ticket's working detail. Keep going ticket after ticket without asking whether to continue; stop only at a **stop condition** below.

The argument is either a parent or one or more tickets (`/ticket-loop 120`, `/ticket-loop v1`, `/ticket-loop 82`, `/ticket-loop 82 84 85`). A parent is whatever holds tickets in the loop config's tracker: an issue with sub-issues, or a milestone by name; any other issue is a ticket. Named tickets are all that run: the loop works those and stops, never their siblings. With no argument, take the parent the loop config says to work next, and say which.

Matt Pocock's skills are named in full (`mattpocock-skills:tdd`), since a bare name can load another skill of the same name.

The **loop config**, `docs/agents/ticket-loop.md`, says how this project's tickets are found, built, tested, shipped and written up: the tracker, the checks command, the test queue, the reference to stay faithful to, the ship and changelog steps, the models per role. Every step below reads it. Communicate with subagents through **context pointers** (ticket numbers, the loop config, CLAUDE.md, earlier commits as patterns), not copies.

## Steps

0. **Setup.** With no loop config in the repo, run setup first, as [`SETUP.md`](SETUP.md) says. It grills the user, writes the config, and proves the loop closes ([`CLOSED-LOOP.md`](CLOSED-LOOP.md)). Done when `docs/agents/ticket-loop.md` is committed and every leg is closed, or M0's tickets are filed (a stop condition).

1. **Frontier.** For a parent, list its open ready-for-agent tickets whose blockers are all closed, as the loop config's tracker says; the first in its order is next. For named tickets, the frontier is the ones not yet shipped, in the order given, except that a named ticket blocked by another named ticket waits for it; a named ticket that isn't ready-for-agent, or is blocked by an open ticket that wasn't named, is skipped with a word on why. State its number and title. Done when a ticket is chosen, or the frontier is empty (a stop condition).

**Labels.** Every subagent you dispatch gets a label (the Agent tool's `description`) that starts with its ticket number, then its role: `#85 implement: wall grind`, `#85 standards review`, `#85 spec review`. That's so the agent list shows which ticket each one is on. No exceptions: a fresh implementer after a decision or a failure gets the same label as the first. Shorten the ticket's title to two or three words to fit; never drop the number to make room. Check the label before every dispatch.

2. **Implement.** Dispatch one implementer subagent labelled `#<ticket> implement: <short title>` (general-purpose, in the background, on the loop config's implementer model) with a brief that points at: the ticket; the loop config, CLAUDE.md and the agent docs; the reference the config names; the previous ticket's commit as a pattern. Its rules:
   - Build it with the Skill tool's `mattpocock-skills:tdd`, at the seams the ticket names (it can't confirm seams with the user, so the ticket's are agreed).
   - Run the config's checks often. It doesn't run or playtest the app itself: that's the test queue's.
   - If the test plan needs a test hook the app lacks (a way to reach a state, or to read a value), build the hook as part of the ticket, and add it to the config's Test queue list.
   - Commit locally with the ticket's closing keyword, staging only the files it changed for this ticket (never `git add -A`: the orchestrator may have edits of its own in the same tree); don't push.
   - File a ticket for any separate problem found, rather than fixing it out of scope.
   - **Decision protocol:** where the ticket and the reference disagree, follow the config's rule for who wins; where that leaves the owner a choice, or the ticket is unclear, stop and report the options with a recommendation; don't guess.
   - Report "ready to test" in under 300 words: commit, what was built and where, seams specced, decisions taken, tickets filed, anything unfinished, and a **test plan**: step by step how to run or playtest it as the config's test queue says (settings, inputs, what to measure) with the expected results.

   End your turn while it works; its completion wakes you. Done when it reports a commit and a test plan, or a decision it needs.

3. **Decide.** For a decision: ask the user (AskUserQuestion, recommendation first), record the answer on the ticket as a comment, then send it to the same subagent if it had done real work, or dispatch a fresh one from the updated ticket if it stopped early, labelled as the first was. Back to step 2's wait.

4. **Test and review.** Put the ticket on the test queue, and while you work through it, dispatch two fresh reviewer subagents in parallel, labelled `#<ticket> standards review` and `#<ticket> spec review`, once per ticket, as the `mattpocock-skills:code-review` skill describes (Standards and Spec, each on the config's model for it; not Claude Code's built-in `code-review`, which is a different review), on the implementer's commit (its diff against the commit before it), so the review isn't anchored on the implementer's view.
   - **Test queue:** you run each test plan yourself, one ticket at a time, as the config says, saying what you're about to run so the user can watch, and undo any temporary test settings afterwards. Record what you measured against what the plan expected. A failure goes back to the implementer with what you saw.
   - Send all the reviewers' findings to the implementer in one go, to fix in a single pass: fix what's right, push back on what's wrong, and file tickets for anything pre-existing or out of scope. Don't review the fixes again: check them yourself by re-running the checks and the affected steps of the test plan, and reading the fix diff to judge the report. Anything that turns up after that becomes a new ticket, not another round.

   Done when the test plan passed and the implementer reports the fixes committed with the checks green.

5. **Ship.** Add the ticket's entry to the changelog the config names, written as it says for its readers, commit it, push, then publish or deploy as the config says. Confirm the ticket closed. Done when all succeeded; a failure is a stop condition.

6. **Report.** Tell the user in a few lines what shipped, any decision taken on their behalf, and tickets filed, then what's next. Back to step 1, unless that was the last ticket named.

## Daily cap

The loop never goes past the user's **daily cap** (the share of their plan's weekly usage one day may take, from the loop config) unless the user says to, at the cap. Check the cap before every subagent dispatch and before every ship, with the Skill tool's `tokencount:tokencount` (the tokencount plugin): its `--json` report's `today.percent_of_week` is how much of the plan's weekly usage today has taken so far. Don't set tokencount's guard for this: it blocks every session on the account, where the cap only pauses the loop to ask.

- **Under the cap:** carry on.
- **At or over the cap, or unreadable** (tokencount isn't installed, its `usage_source` is `unavailable`, or `today.percent_of_week` is null): dispatch nothing and ship nothing. Ask the user (AskUserQuestion) with today's use and the cap, which ticket is in hand, and where it stands:
  - **Stop here** (recommended): stop with the ticket in hand as it is. Say what's committed locally; a later run picks it up.
  - **Finish this ticket**, or **One more ticket** at a ticket boundary: carry on to ship it, then ask again.
  - **Keep going today:** no more cap questions until the date changes.

The answer at the cap is the only override; nothing else lifts it, and a restart asks again. A loop config written before the cap existed has no Daily cap section: before the first ticket, ask setup's Daily cap question alone, prove the Cap leg, and add the answer to the config. If the config marks the cap not applicable (no plan usage to read, as with an API key), skip the check.

## Stop conditions

Stop, say why, and wait for the user when:

- a decision is theirs (step 3 asks it, then carries on);
- the parent's last ticket has shipped (worked as a parent or ticket by ticket): the milestone is done. Write its summary where the config says, tell the user what shipped and what is left for them (ready-for-human tickets), and wait; never start the next milestone's tickets yourself, even when they're ready, and offer `/to-spec`, `/to-tickets` or `/grill-with-docs` if it has none;
- the last named ticket has shipped, or the rest were skipped: say what shipped and what was skipped and why. If that finished the tickets' parent, the milestone stop above applies too;
- setup found the loop open: M0's tickets are filed, and the user works them with you outside the loop;
- the frontier is empty with tickets still open (all blocked, or ready-for-human): say what blocks them;
- the next ticket is ready-for-human: tell them what it needs, and take the next ready-for-agent ticket if there is one;
- something only they can do: a click in a running app, a device check, credentials, a stuck tool;
- a push, publish or check fails in a way a fix can't safely cover;
- the daily cap is reached, or can't be read, and the user says to stop (see Daily cap);
- anything else the config lists as a stop.

## Constraints

- One ticket at a time unless the config allows parallel worktrees (it shouldn't when tickets share a running resource: one app session, one simulator); wider concurrency is `/implement-spec`'s job. If implementers do run in parallel, the test queue is where they meet: tests still run one at a time, in the main thread.
- Read diffs only to judge a report, never to redo the subagent's work; your context is the loop's memory across tickets.
- While a subagent works in the tree, commit your own edits (docs, changelog) at once, so they never end up in its commit.

## Dispatch mode (coordinators)

This is how the **coordinator** (a subagent that runs the loop in place of the main thread, coming in #3) dispatches its implementer and reviewers. It doesn't change the steps above for the main thread. A background subagent is woken when its own background subagent finishes only if its session gives it an explicit hand-back (the SubagentHandback tool), so the coordinator picks its mode by session:

- **Interactive** (`claude`, including `claude --bg`), where the coordinator has an explicit hand-back: dispatch the implementer and reviewers in the background and end your turn while they work, as step 2 says. Run the test queue alongside the reviews.
- **Headless** (`claude -p`), where ending a turn counts as finishing: dispatch the implementer in the foreground and the two reviewers as parallel foreground calls in one message. Run the test queue before or after the reviews, not alongside them.

Hand back explicitly only once, at your real hand-back. While you wait for a subagent, end your turn with plain text. An early SubagentHandback is delivered as your only report, and a later one is refused.

Settled by a trial on Claude Code 2.1.316 (#2), three levels deep (main → background coordinator → background child that sleeps, then reports a word). Headless: not woken. The coordinator finished with its waiting text, and the child's word went to the main thread. Interactive and `--bg`: woken, and the coordinator reported the child's word. Foreground fallback: works, and two foreground children in one message ran in parallel. Re-check when Claude Code changes how subagents hand back.
