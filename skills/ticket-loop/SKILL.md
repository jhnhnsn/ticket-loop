---
name: ticket-loop
description: Work a parent issue's tickets, or just the tickets named, one at a time to shipped (fresh implementer subagent, a test queue run in the main thread, independent two-axis review, push, publish), stopping only for the user's decisions.
disable-model-invocation: true
---

Ship the tickets under a parent issue (a milestone or spec), or just the tickets named, one at a time, each built by a fresh **implementer subagent**, run or playtested by you from the **test queue** (in the main thread, where the user can watch), reviewed by fresh **reviewer subagents**, then pushed and published. You are the **orchestrator**: you hold the frontier, the user's decisions and the reports, never a ticket's working detail. Keep going ticket after ticket without asking whether to continue; stop only at a **stop condition** below.

The argument is either a parent issue or one or more tickets (`/ticket-loop 120`, `/ticket-loop 82`, `/ticket-loop 82 84 85`). A single issue that holds tickets, as the loop config's tracker says a parent does, is a parent; any other issue is a ticket. Named tickets are all that run: the loop works those and stops, never their siblings. With no argument, take the parent the loop config says to work next, and say which.

The **loop config**, `docs/agents/ticket-loop.md`, says how this project's tickets are found, built, tested, shipped and written up: the tracker, the checks command, the test queue, the reference to stay faithful to, the ship and changelog steps, the models per role. Every step below reads it. Communicate with subagents through **context pointers** (ticket numbers, the loop config, CLAUDE.md, earlier commits as patterns), not copies.

## Steps

0. **Setup.** With no loop config in the repo, run setup first, as [`SETUP.md`](SETUP.md) says. It grills the user, writes the config, and proves the loop closes ([`CLOSED-LOOP.md`](CLOSED-LOOP.md)). Done when `docs/agents/ticket-loop.md` is committed and every leg is closed, or M0's tickets are filed (a stop condition).

1. **Frontier.** For a parent, list its open ready-for-agent tickets whose blockers are all closed, as the loop config's tracker says; the first in its order is next. For named tickets, the frontier is the ones not yet shipped, in the order given, except that a named ticket blocked by another named ticket waits for it; a named ticket that isn't ready-for-agent, or is blocked by an open ticket that wasn't named, is skipped with a word on why. State its number and title. Done when a ticket is chosen, or the frontier is empty (a stop condition).

Label every subagent you dispatch with its ticket first, then its role: `#85 implement: wall grind`, `#85 standards review`, `#85 spec review`, so the agent list shows which ticket each one is on.

2. **Implement.** Dispatch one implementer subagent (general-purpose, in the background, on the loop config's implementer model) with a brief that points at: the ticket; the loop config, CLAUDE.md and the agent docs; the reference the config names; the previous ticket's commit as a pattern. Its rules:
   - Build it with the Skill tool's `tdd`, at the seams the ticket names (it can't confirm seams with the user, so the ticket's are agreed).
   - Run the config's checks often. It doesn't run or playtest the app itself: that's the test queue's.
   - If the test plan needs a test hook the app lacks (a way to reach a state, or to read a value), build the hook as part of the ticket, and add it to the config's Test queue list.
   - Commit locally with the ticket's closing keyword, staging only the files it changed for this ticket (never `git add -A`: the orchestrator may have edits of its own in the same tree); don't push.
   - File a ticket for any separate problem found, rather than fixing it out of scope.
   - **Decision protocol:** where the ticket and the reference disagree, follow the config's rule for who wins; where that leaves the owner a choice, or the ticket is unclear, stop and report the options with a recommendation; don't guess.
   - Report "ready to test" in under 300 words: commit, what was built and where, seams specced, decisions taken, tickets filed, anything unfinished, and a **test plan**: step by step how to run or playtest it as the config's test queue says (settings, inputs, what to measure) with the expected results.

   End your turn while it works; its completion wakes you. Done when it reports a commit and a test plan, or a decision it needs.

3. **Decide.** For a decision: ask the user (AskUserQuestion, recommendation first), record the answer on the ticket as a comment, then send it to the same subagent if it had done real work, or dispatch a fresh one from the updated ticket if it stopped early. Back to step 2's wait.

4. **Test and review.** Put the ticket on the test queue, and while you work through it, dispatch two fresh reviewer subagents in parallel, as the `code-review` skill describes (Standards and Spec, each on the config's model for it), on the implementer's commit (its diff against the commit before it), so the review isn't anchored on the implementer's view.
   - **Test queue:** you run each test plan yourself, one ticket at a time, as the config says, saying what you're about to run so the user can watch, and undo any temporary test settings afterwards. Record what you measured against what the plan expected. A failure goes back to the implementer with what you saw.
   - Send the reviewers' findings to the implementer to fix: fix what's right, push back on what's wrong, and file tickets for anything pre-existing or out of scope. If the fixes change behaviour, re-run the affected steps of the test plan.

   Done when the test plan passed and the implementer reports the fixes committed with the checks green.

5. **Ship.** Add the ticket's entry to the changelog the config names, written as it says for its readers, commit it, push, then publish or deploy as the config says. Confirm the ticket closed. Done when all succeeded; a failure is a stop condition.

6. **Report.** Tell the user in a few lines what shipped, any decision taken on their behalf, and tickets filed, then what's next. Back to step 1, unless that was the last ticket named.

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
- anything else the config lists as a stop.

## Constraints

- One ticket at a time unless the config allows parallel worktrees (it shouldn't when tickets share a running resource: one app session, one simulator); wider concurrency is `/implement-spec`'s job. If implementers do run in parallel, the test queue is where they meet: tests still run one at a time, in the main thread.
- Read diffs only to judge a report, never to redo the subagent's work; your context is the loop's memory across tickets.
- While a subagent works in the tree, commit your own edits (docs, changelog) at once, so they never end up in its commit.
