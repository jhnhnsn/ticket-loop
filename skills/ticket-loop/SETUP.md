# Setup: the loop config

The **loop config** is `docs/agents/ticket-loop.md` in the repo: how this project's tickets are found, built, tested, shipped and written up. Every step of the loop reads it. Setup writes it once, the first time the loop runs in a repo, by grilling the user.

## 1. Look before asking

Read what the repo already says: CLAUDE.md (or AGENTS.md), `docs/agents/*` (the issue tracker and labels from `/setup-matt-pocock-skills`), the README, the roadmap or milestone docs, `scripts/` or the package manifest, the git remote. Draft an answer to every question below from what you find. Finding facts is your job; only decisions go to the user.

## 2. Grill

Call the Skill tool with `grilling`. The design tree's root questions are these, each asked with your drafted answer as the recommendation, so "yes" accepts it:

1. **Tickets:** where they live; how a parent (milestone, spec, map issue) holds its tickets; how blocking is recorded; the labels for ready-for-agent and ready-for-human.
2. **Order:** which parent to work, and the order inside it (the parent's order, ticket number, priority label).
3. **Checks:** the command that runs the automated checks and tests.
4. **Test queue:** what gets run or playtested by hand (an app, a game, a simulator, a page), with which tools; any temporary settings a test needs and how they're undone; what a test plan must measure.
5. **Reference:** an upstream or spec the work must stay faithful to; who wins when a ticket and the reference disagree; which forks still go to the user.
6. **Ship:** the branch to push; the publish or deploy command, if any; whether every ticket ships on its own or a milestone ships at once.
7. **Changelog:** where each shipped ticket's entry goes (file and section), who reads it (players, users, developers), what an entry says (what someone can now try, or what changed), its order (oldest first or newest first), its links; where a finished milestone's summary goes; whether milestones still to come are listed.
8. **Stops:** besides the built-in ones (a user decision, the end of each milestone, a failed ship), anything else the loop should stop for.
9. **Models:** the model per role. Recommend Opus for the implementer and the Spec reviewer and Sonnet for the Standards reviewer; Sonnet implementers are faster, but missed a reference detail in a trial.
10. **Commits:** the message style, closing keyword and attribution lines; one commit per ticket plus its fix commit.
11. **Concurrency:** one ticket at a time, or implementers in parallel worktrees (only when nothing they test shares one running resource).

Done when the grilling's frontier is empty and the user confirms the answers.

## 3. Write it

Write `docs/agents/ticket-loop.md` with one short section per question above, in that order, each the confirmed answer in a few lines: commands in backticks, files as paths, no rationale beyond a clause. Add a pointer line to CLAUDE.md's agent docs (`Ticket loop: see docs/agents/ticket-loop.md`). Commit both, then start the loop. To change the config later, edit the file; to redo it, delete it and run the loop again.
