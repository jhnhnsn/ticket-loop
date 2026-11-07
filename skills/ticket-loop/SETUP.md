# Setup: the loop config

The **loop config** is `docs/agents/ticket-loop.md` in the repo: how this project's tickets are found, built, tested, shipped and written up. Every step of the loop reads it. Setup writes it once, the first time the loop runs in a repo, by grilling the user.

## 1. Look before asking

Read what the repo already says: CLAUDE.md (or AGENTS.md), `docs/agents/*` (the issue tracker and labels from `/setup-matt-pocock-skills`), the README, the roadmap or milestone docs, `scripts/` or the package manifest, the git remote. Draft an answer to every question below from what you find. Finding facts is your job; only decisions go to the user.

## 2. Grill

Call the Skill tool with `mattpocock-skills:grilling`. The design tree's root questions are these, each asked with your drafted answer as the recommendation, so "yes" accepts it:

1. **Tickets:** where they live; how a parent (milestone, spec, map issue) holds its tickets; how blocking is recorded; the labels for ready-for-agent and ready-for-human; the **read command** for a ticket and its comments (GitHub: `gh issue view <n> --json title,body,labels,comments`).
2. **Order:** which parent to work, and the order inside it (the parent's order, ticket number, priority label).
3. **Checks:** the command that runs the automated checks and tests.
4. **Test queue:** what gets run or playtested by hand (an app, a game, a simulator, a page), with which tools; any temporary settings a test needs and how they're undone; what a test plan must measure.
5. **Reference:** an upstream or spec the work must stay faithful to; who wins when a ticket and the reference disagree; which forks still go to the user.
6. **Ship:** the branch to push; the publish or deploy command, if any; whether every ticket ships on its own or a milestone ships at once.
7. **Changelog:** where each shipped ticket's entry goes (file and section), who reads it (players, users, developers), what an entry says (what someone can now try, or what changed), its order (oldest first or newest first), its links; where a finished milestone's summary goes; whether milestones still to come are listed.
8. **Stops:** besides the built-in stops (see the coordinator's definition, `agents/coordinator.md`), anything else the loop should stop for.
9. **Models:** each role's model and, alongside it, its effort: the coordinator (which runs the loop), the researcher (opt-in: on a ticket carrying the `research` label, it maps the ticket read-only before each implementer, in a note posted on the ticket; tell the user to add that label to a ticket to opt it in, and that unlabelled tickets get no research), the implementer, the Standards reviewer and the Spec reviewer. Written one line per role (`Implementer: Opus, low effort.`); to change one later, edit its line.
   - **Model:** recommend Opus for the implementer and the Spec reviewer, Sonnet for the Standards reviewer, and Haiku for the researcher, since a research note is a map and should cost far less than the implementer's own search; Sonnet implementers are faster, but missed a reference detail in a trial. Recommend the implementer's model for the coordinator, which is what a config without one uses. A config without a researcher line uses Haiku.
   - **Effort** (`low`, `medium`, `high`, `xhigh`, `max`, or `usual`: dispatched without an effort parameter): recommend the defaults, which a config without efforts uses: implementer `low`, coordinator `medium`, Spec reviewer `high`, researcher and Standards reviewer `usual`. The Spec reviewer is where real bugs turn up, so it stays thorough. The trade-off: each ticket's one fix pass isn't reviewed again, so a light implementer's misses land in a light fix pass or a follow-up ticket; raise the implementer's effort if that happens often.
10. **Commits:** the message style, closing keyword and attribution lines; one commit per ticket plus its fix commit.
11. **Concurrency:** which of three modes builds tickets. Recommend one at a time, unless the tickets are independent and nothing they test shares one running resource. Tests run one at a time in every mode. The config's Concurrency text starts with the mode's words:
    - **One at a time** (`One at a time.`): one implementer, one ticket.
    - **Parallel worktrees** (`Parallel worktrees: at most 2 at once.`): the loop builds independent ready tickets side by side, up to the limit, with no prompt. Ask the limit; recommend 2.
    - **Suggest and ask** (`Suggest and ask: at most 2 at once.`): the loop names the independent ready tickets and asks the user to accept or decline each new set. Accept builds them side by side, up to the limit; decline builds the first only. Ask the limit; recommend 2. A headless run can't ask, so it takes decline and its report says so.
12. **Daily cap:** the share of the plan's weekly usage one day may take before the loop stops to ask. Recommend one day's share, 14.3% (100 ÷ 7). Then ask its mode, recommending rolling: **rolling** (the week's use so far against the share × the day of the usage week, so a light day leaves more for the next) or **per day** (today's use against the share; unused allowance is lost at midnight). For rolling, start the config's Daily cap text with `Rolling:` (`Rolling: 14.3% of the plan's weekly usage per day.`); any other text is per day. Not applicable without plan usage to read (an API key rather than a Pro, Max or Ultra plan). The loop reads the use (today's or the week's) with the tokencount plugin (1.1.0 or later); if it isn't installed, say how (`claude plugin marketplace add jhnhnsn/tokencount`, `claude plugin install tokencount@tokencount`, then a restart).
13. **Ticket budget:** the most tickets one coordinator ships before handing back to a fresh one, so no coordinator's context grows too large. Recommend 4.
14. **Writing:** the standard the agents write in: their messages, briefs, reports and ticket comments, not code or commit messages. Recommend plain English, no standard, which writes no `## Writing` section. The option is `ASD-STE100` (Simplified Technical English, [Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)), written as the section's text. If the user picks it, ask for an optional local path to their own copy of the PDF (`ASD-STE100, dictionary at ~/Documents/ASD-STE100_ISSUE9.pdf`): with a path, the Standards reviewer looks up doubtful words in it by reading it; without one, words aren't checked. Tell the user the standard is copyrighted, so the loop never copies or extracts its text, and that project terms go in a root `GLOSSARY.md`.

Done when the grilling's frontier is empty and the user confirms the answers.

## 3. Offer the status line

The plugin has a status line script, `scripts/ticket-loop-statusline`. It shows the ticket, step, Tickets and Usage bars and compact roles under the input box. With no run, it shows only the Usage bar. A plugin can't change user settings by itself. Ask the user first, with AskUserQuestion, and recommend yes.

If the user says yes:

1. Read the `statusLine` setting in `~/.claude/settings.json`.
2. Use this shell text as `<script>`. It finds the newest installed version at each refresh, so it follows plugin updates:
   `"$(ls -d ~/.claude/plugins/cache/ticket-loop/ticket-loop/*/ | sort -V | tail -n 1)scripts/ticket-loop-statusline"`
   Don't use the marketplace clone, because it follows `main`, not the installed version.
3. With no `statusLine`, propose `{"type": "command", "command": "python3 <script>", "refreshInterval": 5}`.
4. With a `statusLine` of type `command`, keep the user's command. Propose `python3 <script> --with '<their command>'`.
5. In their command, write each single quote as `'\''`. Otherwise a single quote ends the `--with` text too early.
6. Keep their `padding`. Set `refreshInterval` to 5 if it is not set or is more than 5.
7. In the JSON value, write each `"` as `\"` and each `\` as `\\`.
8. Show the user the old value and the new value. Their line comes first, then the loop's line.
9. Ask again before you write.
10. Write only the `statusLine` key with the Edit tool. Change nothing else in the file.

If the user says no, or the setting has a type other than `command`, change nothing. Tell the user how to add it later. Step 4 records the answer in the config.

## 4. Write it

Write `docs/agents/ticket-loop.md` with one short section per question above, in that order, each the confirmed answer in a few lines: commands in backticks, files as paths, no rationale beyond a clause. The Tickets section has a line `Read a ticket: <read command>.` In the Test queue section, list the test hooks the app has. Last, add a `## Status line` section with the answer from step 3: `Added.`, `Declined.` or `Not added: the statusLine type is not command.`

Add the line `.ticket-loop-status` to the repo's `.gitignore`, so the status file never goes into a commit. Make the file if it does not exist. Add a pointer line to CLAUDE.md's agent docs (`Ticket loop: see docs/agents/ticket-loop.md`). Commit the three files. To change the config later, edit the file; to redo it, delete it and run the loop again.

## 5. Prove the loop closes

Prove each of the six legs (Check, Run, Drive, Ship, Record, Cap) by doing it, as [`CLOSED-LOOP.md`](CLOSED-LOOP.md) says.

- **Every leg closed or not applicable:** start the loop.
- **Any leg open:** file one ticket per open leg under an **M0 · Closed loop** parent, as `CLOSED-LOOP.md` says. Tell the user which legs are open and which tickets need them, then stop. The user works M0 with you in an ordinary session and runs the loop again once it's closed.

Done when every leg is closed or not applicable, or M0's tickets are filed.
