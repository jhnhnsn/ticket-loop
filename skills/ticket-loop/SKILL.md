---
name: ticket-loop
description: Work a parent issue's tickets one at a time to shipped (fresh implementer subagent, a test queue run in the main thread, independent two-axis review, push, publish), stopping only for the user's decisions.
disable-model-invocation: true
---

Ship the tickets under a parent issue (a milestone or spec) one at a time, each built by a fresh **implementer subagent**, run or playtested by you from the **test queue** (in the main thread, where the user can watch), reviewed by fresh **reviewer subagents**, then pushed and published. You are the **orchestrator**: you hold the frontier, the user's decisions and the reports, never a ticket's working detail. Keep going ticket after ticket without asking whether to continue; stop only at a **stop condition** below.

The argument is the parent issue. With none, take the current milestone from the repo's roadmap, and say which.

The repo's agent docs, written by `/setup-matt-pocock-skills`, give the issue tracker, its labels and how a **frontier** is found (`docs/agents/issue-tracker.md`). Its CLAUDE.md gives how to check, run or playtest, and publish. Communicate with subagents through **context pointers** (ticket numbers, those docs, earlier commits as patterns), not copies.

## Steps

1. **Frontier.** List the parent's open tickets labelled ready-for-agent whose blockers are all closed; the first in the parent's order is next. State its number and title. Done when a ticket is chosen, or the frontier is empty (a stop condition).

2. **Implement.** Dispatch one implementer subagent (general-purpose, in the background) with a brief that points at: the ticket; CLAUDE.md and the agent docs; any reference source the repo keeps (e.g. a vendored upstream to be faithful to); the previous ticket's commit as a pattern. Its rules:
   - Build it with the Skill tool's `tdd`, at the seams the ticket names (it can't confirm seams with the user, so the ticket's are agreed).
   - Run the repo's automated checks often. It doesn't run or playtest the app itself: that's the test queue's.
   - Commit locally with the ticket's closing keyword, staging only the files it changed for this ticket (never `git add -A`: the orchestrator may have edits of its own in the same tree); don't push.
   - File a ticket for any separate problem found, rather than fixing it out of scope.
   - **Decision protocol:** where the ticket and the reference (or the code) disagree in a way the owner may care about, or the ticket is unclear, stop and report the options with a recommendation; don't guess.
   - Report "ready to test" in under 300 words: commit, what was built and where, seams specced, decisions taken, tickets filed, anything unfinished, and a **test plan**: step by step how to run or playtest it as CLAUDE.md says (settings, inputs, what to measure) with the expected results.

   End your turn while it works; its completion wakes you. Done when it reports a commit and a test plan, or a decision it needs.

3. **Decide.** For a decision: ask the user (AskUserQuestion, recommendation first), record the answer on the ticket as a comment, then send it to the same subagent if it had done real work, or dispatch a fresh one from the updated ticket if it stopped early. Back to step 2's wait.

4. **Test and review.** Put the ticket on the test queue, and while you work through it, dispatch two fresh reviewer subagents in parallel, as the `code-review` skill describes (Standards and Spec), on the implementer's commit (its diff against the commit before it), so the review isn't anchored on the implementer's view.
   - **Test queue:** you run each test plan yourself, one ticket at a time, as CLAUDE.md says, saying what you're about to run so the user can watch, and undo any temporary test settings afterwards. Record what you measured against what the plan expected. A failure goes back to the implementer with what you saw.
   - Send the reviewers' findings to the implementer to fix: fix what's right, push back on what's wrong, and file tickets for anything pre-existing or out of scope. If the fixes change behaviour, re-run the affected steps of the test plan.

   Done when the test plan passed and the implementer reports the fixes committed with the checks green.

5. **Ship.** Update any changelog or release notes CLAUDE.md names (written for its readers: for a game, what a player can now try), commit it, push, then publish or deploy as CLAUDE.md says. Confirm the ticket closed. Done when all succeeded; a failure is a stop condition.

6. **Report.** Tell the user in a few lines what shipped, any decision taken on their behalf, and tickets filed, then what's next. Back to step 1.

## Stop conditions

Stop, say why, and wait for the user when:

- a decision is theirs (step 3 asks it, then carries on);
- the parent's last ticket has shipped: the milestone is done. Write its summary in any changelog CLAUDE.md names, tell the user what shipped and what is left for them (ready-for-human tickets), and wait; never start the next milestone's tickets yourself, even when they're ready, and offer `/to-spec`, `/to-tickets` or `/grill-with-docs` if it has none;
- the frontier is empty with tickets still open (all blocked, or ready-for-human): say what blocks them;
- the next ticket is ready-for-human: tell them what it needs, and take the next ready-for-agent ticket if there is one;
- something only they can do: a click in a running app, a device check, credentials, a stuck tool;
- a push, publish or check fails in a way a fix can't safely cover.

## Constraints

- One ticket at a time when tickets share a running resource (one app session, one simulator); concurrency is `/implement-spec`'s job. If implementers do run in parallel, the test queue is where they meet: tests still run one at a time, in the main thread.
- Read diffs only to judge a report, never to redo the subagent's work; your context is the loop's memory across tickets.
- While a subagent works in the tree, commit your own edits (docs, changelog) at once, so they never end up in its commit.
