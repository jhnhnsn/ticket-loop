# Changelog

What changes for you, the person running the loop, newest first.

## Unreleased

- At a handover, the launcher now starts the fresh coordinator before it reads any ticket, and it doesn't judge the next ticket. A decision on that ticket comes from the fresh coordinator, as a decision needed hand-back. ([#21](https://github.com/jhnhnsn/ticket-loop/issues/21))

## 1.18.0

Concurrency has three modes, and suggest and ask can offer a parallel build mid-run. A named run no longer ships a ticket ahead of its blocker, and the plugin has an MIT licence. Published on its own, between milestones.

- The config's Concurrency section now has three modes, each with a limit where it builds in parallel: `One at a time.`, `Suggest and ask: at most 2 at once.` and `Parallel worktrees: at most 2 at once.` In suggest and ask, the run asks you once about each set of independent ready tickets, before the build or through a new parallel offer hand-back, and doesn't ask again about a set you answered. A headless run can't ask, so it takes decline and says so in its report. A parallel build's whole set finishes before the ticket budget check. Older configs keep working: `Parallel worktrees when independent.` and `One at a time, or parallel worktrees when offered.` read as suggest and ask, and `One ticket per run.` or no section reads as one at a time. Headless runs of the modes passed. The question, the parallel offer hand-back and the answered sets haven't run in an interactive session yet, so tell us if they misbehave. ([#7](https://github.com/jhnhnsn/ticket-loop/issues/7))
- The plugin now has an MIT licence: a `LICENSE` file at the root and a `license` field in `plugin.json`. The plugin directory no longer refuses a submission for a missing licence. ([#8](https://github.com/jhnhnsn/ticket-loop/issues/8))
- A named run no longer ships a ticket ahead of its blocker. The coordinator now reads the blockers of each named ticket from the tracker before it chooses the next one, also after a handover. If it can't read them, it stops, dispatches nothing, and tells you which ticket and why. ([#11](https://github.com/jhnhnsn/ticket-loop/issues/11))

## 1.17.0

You can see what a running coordinator does, in the chat and in a status line that doesn't scroll. Published on its own, between milestones.

- You can now see what a running coordinator does. The coordinator writes its ticket, step, what runs now and the start time to `.ticket-loop-status` at the repo root, and git ignores the file. When Claude Code says that the coordinator "is waiting on its own background work", the launcher reads the file and tells you the ticket, its step, what runs and for how long, with the Tickets bar. It writes a short "Still …" line if nothing changed, and it doesn't guess. A new status line script shows the ticket, step, Tickets and Usage bars and compact roles under the input box. It makes no GitHub call. With no run, it shows only the Usage bar. Setup asks before it adds the script to your settings, and it keeps your own status line. Older configs get the offer one time. ([#37](https://github.com/jhnhnsn/ticket-loop/issues/37))

## 1.16.0

Agents can write in ASD-STE100 Simplified Technical English, parallel builds no longer strand the coordinator in a worktree, and long research notes are trimmed instead of dropped. Published on its own, between milestones.

- Your loop config can ask the agents to write in ASD-STE100 Simplified Technical English, with a new `## Writing` section. Then the launcher, coordinator, researchers, implementers and reviewers keep their messages, briefs, reports and ticket comments short and plain: short sentences, one instruction each, active voice. Code, quoted text and commit messages stay as they are. Setup asks for it, with plain English as the default. A new `GLOSSARY.md` lists the project's own terms. If you give a path to your own copy of the standard, the Standards reviewer looks up doubtful words in its dictionary. The plugin links to the standard and never copies its text. ([#36](https://github.com/jhnhnsn/ticket-loop/issues/36))
- Parallel builds no longer get the coordinator stuck in a worktree. It never messages a worktree implementer, not even with a decision's answer. Once one reports, the coordinator cherry-picks its commits onto main, checks they all arrived, and removes the worktree and its branch. Review fixes, test failures and decisions then go to a fresh implementer on main, and each push carries only the shipping ticket's commits, so no ticket closes before it ships. ([#34](https://github.com/jhnhnsn/ticket-loop/issues/34))
- A research note that runs over 300 words is now trimmed and posted, not thrown away. The researcher aims for about 200 words, with its `path:line` pointers first. The coordinator cuts a long note to fit, keeping every pointer and flagged question, and marks it `(trimmed from <n> words)`. The ticket's report counts the pass as `1 research pass (trimmed)`. A note with no pointers is still skipped. ([#33](https://github.com/jhnhnsn/ticket-loop/issues/33))

## 1.15.0

The researcher is opt-in: only tickets labelled `research` get research passes. Published on its own, between milestones.

- Research no longer runs by default. A ticket gets research passes only when it carries a `research` label, and then it gets everything 1.14.0 gave: a pass before its first implementer and one before each later implementer, with notes on the ticket. A ticket without the label goes straight to its implementer, and its report says `research: not requested`. The preview's roles line marks the researcher `(opt-in)`, and setup's Models question tells you how to opt a ticket in. ([#35](https://github.com/jhnhnsn/ticket-loop/issues/35))

## 1.14.0

The researcher milestone (#29) is done. A cheap, read-only researcher maps each ticket before every implementer, its first and each fix pass, so a low-effort implementer starts from a note on the ticket instead of searching on its own.

- A researcher maps each ticket before its first implementer. It's a cheap, read-only fifth role (Haiku at usual effort unless your config's Models section names a `Researcher:`), shown in the preview's roles line. Its note of at most 300 words, with `path:line` pointers, is posted on the ticket as `Research note (#<ticket> research)`, and the implementer starts from it. If research fails or the note runs long, the ticket goes ahead without it, and each ticket's report says how many research passes ran. ([#30](https://github.com/jhnhnsn/ticket-loop/issues/30))
- Setup's Models question asks for the researcher's model and effort alongside the other roles, recommending Haiku at usual effort, and writes a `Researcher:` line into your config. A config written before the researcher existed still gets those defaults without being asked. ([#32](https://github.com/jhnhnsn/ticket-loop/issues/32))
- Every later implementer on a ticket gets its own research pass first, scoped to what it's fixing: the review fixes, a test failure, or a decision. Each note is posted as a new comment naming its purpose (`Research note (#<ticket> research) for the review fixes`). Review findings and test failures now go to a fresh implementer in interactive runs too, so this pass always runs before a fix. ([#31](https://github.com/jhnhnsn/ticket-loop/issues/31))

## 1.13.0

The daily cap can roll over unused days in the usage week, and commits follow your config's attribution rule over the session's default. Published on its own, between milestones.

- The daily cap can be rolling: the week's use so far is held to your daily share × the day of the usage week (24-hour days from the week's start), so a light day leaves more for the next. The Usage bar then reads `15.0% of the week so far, allowance 28.6% (day 2 of 7)`. Setup asks rolling or per day, recommending rolling, and writes a rolling cap as `Rolling: …`; a config without that label keeps today's per-day cap unchanged. ([#24](https://github.com/jhnhnsn/ticket-loop/issues/24))
- Commits in a run follow your loop config's Commits section, even when the session's own default asks for a `Co-Authored-By` line. Where the config says no attribution, no commit carries one, whether the launcher, a coordinator or an implementer made it. ([#27](https://github.com/jhnhnsn/ticket-loop/issues/27))

## 1.12.0

Headless and unattended runs survive refused Bash commands: every agent makes one plain call at a time and reads tickets with `--json`. Published on its own, between milestones.

- Headless runs no longer stop on refused Bash commands. Every agent in the run, the launcher included, changes files with Edit or Write and makes one plain Bash call at a time, with no chains, loops or pipes. When a command is refused, it retries a simpler one instead of telling you Bash is unavailable. Tickets are read with the command the config's Tickets section names, which setup now writes (for GitHub, `gh issue view <n> --json …`, since `--comments` prints nothing headless). A headless decision or cap stop now ends with one message: every ticket shipped this run, then the bars, then the decision. ([#26](https://github.com/jhnhnsn/ticket-loop/issues/26))

## 1.11.0

The coordinator milestone (#1) is done. Every run goes through a background coordinator, so your main thread stays free, and long runs hand over to fresh coordinators at a ticket budget.
Decisions and the daily cap now come to you as questions instead of ending the run, and a Keep going today answer holds across handovers.

- At the daily cap, or when it can't be read, the run no longer just stops. The coordinator hands back before it dispatches anything, and you're asked: Stop here, Finish this ticket or one more, or Keep going today. The same coordinator then carries on. Keep going today holds for the rest of that day, including after a handover, so you aren't asked again. A headless run still stops at the cap. ([#6](https://github.com/jhnhnsn/ticket-loop/issues/6))

## 1.10.0

Long runs hand over to a fresh coordinator at a ticket budget, each role runs at an effort you set in the loop config (implementer `low` by default), and the preview and every hand-back show the run's progress and today's usage against your cap. Published partway through the coordinator milestone (#1): the daily cap across coordinators (#6) is still to come.

- At a decision, the question comes first, with nothing printed before it. Once you answer, one message shows the reports, then the Tickets and Usage bars, then a line saying your answer is on the ticket and the coordinator has resumed. A headless run still shows them with the decision, since there it's a stop. ([#23](https://github.com/jhnhnsn/ticket-loop/issues/23))
- The run's preview shows two bars under the ready count: the tickets shipped out of the run's total, and today's usage against your daily cap. If there's no plan usage, or it can't be read, a line says so instead of a bar. The bars show again, read fresh, at every hand-back. At a handover they come in the message saying which coordinator took over. ([#19](https://github.com/jhnhnsn/ticket-loop/issues/19))
- Each role runs at an effort you can set in the loop config, next to its model: by default the implementer at `low`, the coordinator at `medium`, the Spec reviewer at `high` and the Standards reviewer at its usual effort. Configs without efforts use these without asking, and setup asks for them. The run's preview, now shown as the first coordinator starts, gives each role's model and effort on a line under the ready count. ([#18](https://github.com/jhnhnsn/ticket-loop/issues/18))
- Long runs are split across coordinators, so none of them fills its context. Each ships at most the config's ticket budget (4 unless you set one), then a fresh `… coordinator 2` takes over from the tracker without asking you. As the first one starts, the run is previewed: `M1: 7 ready, about 2 coordinators.` Setup asks for the budget. ([#5](https://github.com/jhnhnsn/ticket-loop/issues/5))

## 1.9.0

Runs go through a coordinator subagent, so your main thread stays free, and a decision that's yours no longer ends the run. Published partway through the coordinator milestone (#1): the ticket budget, handover and the daily cap across coordinators are still to come.

- A decision that's yours no longer ends the run. The coordinator hands it to the main thread, which asks you, records your answer on the ticket, and resumes the same coordinator to carry on. A headless run still stops at a decision: answer on the ticket and run again. ([#4](https://github.com/jhnhnsn/ticket-loop/issues/4))
- Runs go through a coordinator. `/ticket-loop:ticket-loop` now hands each run to a background `ticket-loop: <run> coordinator 1` agent that builds, tests, reviews and ships the tickets, so your main thread stays free. Any question about running tickets in parallel is asked up front. Watch the test queue in the coordinator's transcript in the agent view. A decision or the daily cap still ends the run for now: answer or raise the cap, then run the command again. ([#3](https://github.com/jhnhnsn/ticket-loop/issues/3))
- Coordinators will dispatch by session: in the background when they can be woken (interactive and `claude --bg`), in the foreground in headless `claude -p` runs, where ending a turn ends the run. Settled by trying it; the evidence is in ADR-0001. ([#2](https://github.com/jhnhnsn/ticket-loop/issues/2))
