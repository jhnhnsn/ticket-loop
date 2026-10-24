---
name: ticket-loop
description: Work a parent issue's tickets one at a time to shipped (fresh implementer subagent, independent two-axis review, push, publish), stopping only for the user's decisions.
disable-model-invocation: true
---

Ship the tickets under a parent issue (a milestone or spec) one at a time, each built by a fresh **implementer subagent**, reviewed by fresh **reviewer subagents**, then pushed and published. You are the **orchestrator**: you hold the frontier, the user's decisions and the reports, never a ticket's working detail. Keep going ticket after ticket without asking whether to continue; stop only at a **stop condition** below.

The argument is the parent issue. With none, take the current milestone from the repo's roadmap, and say which.

The repo's agent docs, written by `/setup-matt-pocock-skills`, give the issue tracker, its labels and how a **frontier** is found (`docs/agents/issue-tracker.md`). Its CLAUDE.md gives how to check, run or playtest, and publish. Communicate with subagents through **context pointers** (ticket numbers, those docs, earlier commits as patterns), not copies.

## Steps

1. **Frontier.** List the parent's open tickets labelled ready-for-agent whose blockers are all closed; the first in the parent's order is next. State its number and title. Done when a ticket is chosen, or the frontier is empty (a stop condition).

2. **Implement.** Dispatch one implementer subagent (general-purpose, in the background) with a brief that points at: the ticket; CLAUDE.md and the agent docs; any reference source the repo keeps (e.g. a vendored upstream to be faithful to); the previous ticket's commit as a pattern. Its rules:
   - Build it with the Skill tool's `tdd`, at the seams the ticket names (it can't confirm seams with the user, so the ticket's are agreed).
   - Run the repo's checks often; run or playtest it as CLAUDE.md says, and undo any temporary test settings afterwards.
   - Commit locally with the ticket's closing keyword; don't push.
   - File a ticket for any separate problem found, rather than fixing it out of scope.
   - **Decision protocol:** where the ticket and the reference (or the code) disagree in a way the owner may care about, or the ticket is unclear, stop and report the options with a recommendation; don't guess.
   - Report in under 300 words: commit, what was built and where, seams specced, run or playtest results with numbers, decisions taken, tickets filed, anything unfinished.

   End your turn while it works; its completion wakes you. Done when it reports a commit, or a decision it needs.

3. **Decide.** For a decision: ask the user (AskUserQuestion, recommendation first), record the answer on the ticket as a comment, then send it to the same subagent if it had done real work, or dispatch a fresh one from the updated ticket if it stopped early. Back to step 2's wait.

4. **Review.** Dispatch two fresh reviewer subagents in parallel, as the `code-review` skill describes (Standards and Spec), on the implementer's commit (its diff against the commit before it), so the review isn't anchored on the implementer's view. Send their findings to the implementer to fix in the same commit's spirit: fix what's right, push back on what's wrong, and file tickets for anything pre-existing or out of scope. Done when the implementer reports the fixes committed and the checks green.

5. **Ship.** Push, then publish or deploy as CLAUDE.md says. Confirm the ticket closed. Done when both succeeded; a failure is a stop condition.

6. **Report.** Tell the user in a few lines what shipped, any decision taken on their behalf, and tickets filed, then what's next. Back to step 1.

## Stop conditions

Stop, say why, and wait for the user when:

- a decision is theirs (step 3 asks it, then carries on);
- the frontier is empty: the milestone is done, and the next needs a spec, tickets or a grilling (offer `/to-spec`, `/to-tickets` or `/grill-with-docs`);
- the next ticket is ready-for-human: tell them what it needs, and take the next ready-for-agent ticket if there is one;
- something only they can do: a click in a running app, a device check, credentials, a stuck tool;
- a push, publish or check fails in a way a fix can't safely cover.

## Constraints

- One ticket at a time when tickets share a running resource (one app session, one simulator); concurrency is `/implement-spec`'s job.
- Read diffs only to judge a report, never to redo the subagent's work; your context is the loop's memory across tickets.
