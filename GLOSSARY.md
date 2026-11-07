# Glossary

This project's own terms. With a `## Writing` section of `ASD-STE100`, they are technical nouns and technical verbs: each has one meaning only, and the Standards reviewer doesn't flag them. The definitions are ours.

## Technical nouns

### Loop roles

- **launcher:** the `/ticket-loop:ticket-loop` skill in the user's main thread; it starts coordinators and relays their hand-backs.
- **coordinator:** the subagent that takes a run's tickets to shipped, one at a time.
- **implementer:** the subagent that builds one ticket and commits it locally.
- **Standards reviewer:** the reviewer subagent that checks a commit against the repo's own standards.
- **Spec reviewer:** the reviewer subagent that checks a commit against its ticket and the reference.
- **researcher:** the read-only subagent that maps a `research`-labelled ticket for the implementer.
- **subagent:** an agent that another agent starts with the Agent tool.

### Run parts

- **run:** one launch of the loop, from the argument to the last hand-back.
- **ticket:** one unit of work in the tracker, built and shipped on its own.
- **parent:** an issue or milestone that holds tickets.
- **milestone:** a named group of tickets in the tracker, published together.
- **spec:** an issue that describes a larger piece of work its tickets come from.
- **sub-issue:** a ticket attached to a parent issue.
- **blocker:** an open ticket that another ticket waits on.
- **frontier:** the open, ready tickets whose blockers are all closed.
- **label:** a tag on a ticket.
- **agent label:** the name the Agent tool shows for a subagent, such as `#85 spec review`.
- **decision:** a choice that belongs to the user, asked as a question.
- **hand-back:** the message a coordinator gives the launcher when it stops its turn of work.
- **parallel set:** the independent ready tickets, up to the concurrency limit, that the loop can build side by side.
- **parallel offer:** the hand-back that gives the launcher a new parallel set to ask about.
- **offer question:** the launcher's question to the user to accept or decline a parallel set.
- **answered set:** a parallel set that the user accepted or declined in a run; each brief lists them.
- **state read:** the launcher's read of only a ticket's state and labels, to count a run and draw the Tickets bar.
- **brief:** the prompt an agent gives a subagent it starts.
- **report:** what a subagent returns.
- **ticket report:** the few lines a coordinator writes per shipped ticket.
- **research note:** the researcher's short map of a ticket, posted as a ticket comment.
- **test plan:** the implementer's step-by-step instructions to test its ticket, with expected results.
- **test queue:** the tests the coordinator runs itself, one ticket at a time.
- **sandbox:** the separate repository where test runs of the loop happen.
- **preview:** the launcher's first lines of a run: the ready count, the progress bars and the roles line.
- **roles line:** the line that gives each role's model and effort.
- **progress bar:** one of the two ten-cell bars for tickets shipped and usage.
- **status line:** the line under Claude Code's input box that the plugin's `scripts/ticket-loop-statusline` script prints.
- **compact roles:** the short roles line form in the status file, such as `Opus/med`, one field per role.

### Limits

- **ticket budget:** the tickets one coordinator ships before a fresh one takes over; a parallel build in hand finishes first.
- **concurrency mode:** how the loop builds ready tickets: one at a time, parallel worktrees, or suggest and ask.
- **concurrency limit:** the most tickets the loop builds at once.
- **daily cap:** the share of the plan's weekly usage that one day can use.
- **allowance:** a rolling cap's limit: the daily share times the day of the usage week.
- **cap question:** the launcher's question to the user when the daily cap is reached.
- **effort:** how hard a model thinks, set per role.

### Files and records

- **loop config:** `docs/agents/ticket-loop.md`, the project's settings for the loop.
- **status file:** `.ticket-loop-status` at the main checkout's root, the coordinator's one-line state; git ignores it.
- **changelog:** `CHANGELOG.md`, the record of what each shipped ticket changed.
- **ADR:** an architecture decision record, in `docs/adr/`.
- **glossary:** this file.
- **plugin:** a package of skills and agents that Claude Code installs.
- **skill:** a set of instructions that Claude Code loads by name.
- **agent definition:** a Markdown file that defines a subagent type, such as `agents/coordinator.md`.

### Git and GitHub

- **repository:** a git project and its history.
- **branch:** a named line of commits.
- **commit:** one recorded change in the history.
- **worktree:** a second working directory of the same repository, on its own branch.
- **main checkout:** the repository's first working directory, on `main`.
- **pull request:** a GitHub request to merge one branch into another.
- **issue:** a GitHub tracker item; a ticket or a parent.
- **comment:** a note on an issue.
- **origin:** the remote repository that pushes go to.

### Tools and models

- **tokencount:** the plugin that reports plan usage.
- **gh:** the GitHub command-line tool.
- **Claude Code:** the CLI that runs the loop.
- **Opus:** a Claude model a role can run on.
- **Sonnet:** a Claude model a role can run on.
- **Haiku:** a Claude model a role can run on.
- **Agent tool:** the tool that starts a subagent.
- **SendMessage:** the tool that sends a message to a running or finished subagent.
- **AskUserQuestion:** the tool that asks the user a question with options.

## Technical verbs

### Git

- **commit:** record staged changes in the history.
- **push:** send commits to origin.
- **pull:** fetch from origin and merge into the current branch.
- **fetch:** get new commits from origin without a merge.
- **merge:** join one branch's commits into another.
- **rebase:** move commits onto a new base commit.
- **cherry-pick:** copy one commit onto the current branch.
- **reset:** move a branch to a given commit.
- **stage:** mark changes for the next commit.
- **clone:** make a local copy of a repository.

### The loop

- **dispatch:** start a subagent with a brief.
- **hand back:** stop a turn of work and give the launcher a hand-back.
- **resume:** continue a stopped agent with a new message.
- **ship:** push a ticket's commits and close the ticket.
- **publish:** release a new plugin version.
- **triage:** sort a new ticket and give it a label.
- **label:** put a label on a ticket, or an agent label on a subagent.
- **close:** mark an issue as done.
- **file:** create a ticket in the tracker.
- **review:** check a commit against standards or the spec.
- **test:** run a test plan and compare the results with the expected results.
- **build:** make the change that a ticket asks for.
