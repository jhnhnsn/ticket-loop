# ticket-loop

A Claude Code plugin that ships a milestone's tickets one at a time, without check-ins. Your
main thread hands the run to a background **coordinator** subagent and stays free for you. The
coordinator works the tickets: each is built by a fresh implementer subagent (so every ticket
starts with a clear context), tested by the coordinator, reviewed by two fresh reviewer
subagents, then pushed, published and written up. It asks you only for decisions that are
yours, and stops only when it needs you and at the end of each milestone.

## Getting started

1. **Install Matt Pocock's skills**, which the loop builds on (`mattpocock-skills:grilling`,
   `mattpocock-skills:tdd`, `mattpocock-skills:code-review`, called by their full names so
   Claude Code's built-in `code-review` isn't loaded in their place):

   ```sh
   claude plugin install mattpocock-skills@claude-plugins-official
   ```

2. **Install ticket-loop:**

   ```sh
   claude plugin marketplace add jhnhnsn/ticket-loop
   claude plugin install ticket-loop@ticket-loop
   ```

   Restart Claude Code so the new skill is listed.

   For the [daily cap](#when-it-stops), also install
   [tokencount](https://github.com/jhnhnsn/tokencount) (1.1.0 or later, on a Pro or Max plan),
   which reports how much of your plan's week today has used:

   ```sh
   claude plugin marketplace add jhnhnsn/tokencount
   claude plugin install tokencount@tokencount
   ```

3. **Optional: run `/setup-matt-pocock-skills`** in your project. It records where tickets
   live and what the triage labels are (`docs/agents/`), which answers the loop's first
   questions before they're asked.

4. **Have tickets under a parent:** a milestone or spec issue whose sub-issues are the
   tickets, or a tracker milestone holding them, labelled `ready-for-agent`, each saying what it blocks on. `/to-spec` and
   `/to-tickets` (Matt Pocock's) make them from a plan.

5. **Run it** with the parent, or with the tickets you want shipped:

   ```
   /ticket-loop:ticket-loop 120        # every ticket under parent issue #120
   /ticket-loop:ticket-loop v1         # every ticket in milestone v1
   /ticket-loop:ticket-loop 82         # just ticket #82
   /ticket-loop:ticket-loop 82 84 85   # just these three
   ```

   The first run in a repo grills you before it starts (see [First run](#first-run)); after
   that it goes straight to the first ticket.

6. **Let it work.** The coordinator runs in the background, labelled with what it runs
   (`ticket-loop: #82 coordinator 1`), and your main thread is free for other work meanwhile.
   As it starts, the main thread previews the run: how big it is, how far through its
   tickets it is, how much of your [daily cap](#when-it-stops) today has used, and how each
   role runs, model and effort (see [Models](#models)):

   ```
   M1: 7 ready, about 2 coordinators.
   Tickets  [███░░░░░░░] 3 of 10 shipped
   Usage    [████░░░░░░] 6.1% of the week today, cap 14.3%
   Coordinator: Opus, medium · Researcher: Haiku, usual (opt-in) · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high
   ```

   **Tickets** counts the parent's tickets that are closed, out of all of them, open or
   closed; run with tickets, the named ones that are closed, out of those named. **Usage** is
   how much of your plan's week today has used (tokencount's `today.percent_of_week`) against
   the config's daily cap. With a rolling cap it's the week's use so far (`week.percent_used`)
   against the allowance, the daily share × the day of the usage week, counted in 24-hour days
   from the week's start. Either way the bar fills as a share of the limit: full at or over it,
   when the coordinator's next cap check hands back to ask you. A rolling cap's line reads:

   ```
   Usage    [█████░░░░░] 15.0% of the week so far, allowance 28.6% (day 2 of 7)
   ```

   Without plan usage to read (the config marks the cap not applicable) it says
   `not applicable (no plan usage to read)`, and if tokencount can't tell,
   `can't read today's usage`, which hands back the same way.

   Each coordinator ships the config's **ticket budget**, or fewer if a ticket ran heavy, or
   more if a parallel build in hand must finish. It then hands back, and the main thread starts
   a fresh one (`ticket-loop: M1 coordinator 2`) without asking, so no coordinator's context
   grows too large. At each hand-back (a decision for you, a parallel offer, a handover, or a
   stop) the main thread shows the report for each ticket shipped since the last, in a few
   lines: what shipped, the decisions you answered and any taken on your behalf, tickets filed,
   what's next. Under the
   reports come the Tickets and Usage bars again, read fresh from the tracker and tokencount,
   so you see the run's progress partway through. For a decision they come after you answer,
   in the message saying your answer is recorded on the ticket and the coordinator resumed
   (a headless run, where the decision is a stop, shows them with the question). For a
   handover they come in the message saying which coordinator took over, once the fresh one
   has started, which doesn't repeat the rest of the preview. Ask "how's the agent doing?" in
   the main thread at any time. Push and publish commands ask permission in your main session,
   naming the agent, unless your settings allow them; allow them to keep the loop unattended.

   **While a run goes on**, the coordinator writes its state to `.ticket-loop-status` at the
   root of the main checkout, one line at each step change. Setup adds the file to your
   `.gitignore`, so it never goes into a commit. When Claude Code says that a coordinator
   "is waiting on its own background work", the main thread reads the file and writes one line:

   ```
   #121 is in the test queue, running the browser suite (4 min). Tickets [░░░░░░░░░░] 0 of 1 shipped.
   ```

   With no change since its last line, it writes `Still running the browser suite on #121 (6 min).`
   With no status file, it says that it has no status yet.

   **The status line.** The plugin has a status line script, `scripts/ticket-loop-statusline`,
   for Claude Code's `statusLine` setting. Setup offers to add it and shows you the change
   first. Your own status line stays in front of it. The line stays under the input box, and
   it refreshes every 5 seconds. If your config is older, the loop offers it once:

   ```
   #121 test queue · Tickets [░░░░░░░░░░] 0/1 · Usage [████████░░] 43.0%/57.2% d4 · Opus/med · Haiku/usual opt-in · Opus/low · Sonnet · Opus/high
   ```

   With no run, it shows only the Usage progress bar, or nothing if tokencount can't tell. A
   run is over when the file's last step is `hand-back`. The main thread writes that step when
   a run stops, also when you stop the coordinator. A file 12 hours old also counts as over.
   The script makes no GitHub call: the ticket counts come from the file. The Usage progress
   bar shows the last tokencount report, which the script refreshes in the background each
   minute. To add it by hand, set `statusLine` to this (it finds the newest installed version):

   ```json
   {"type": "command", "command": "python3 \"$(ls -d ~/.claude/plugins/cache/ticket-loop/ticket-loop/*/ | sort -V | tail -n 1)scripts/ticket-loop-statusline\"", "refreshInterval": 5}
   ```

   To keep a status line you have, add `--with '<your command>'` after the script. In your
   command, write each single quote as `'\''`.

## First run

With no loop config in the repo, the loop runs setup first. It reads what the repo already says
(CLAUDE.md, `docs/agents/`, the README, the roadmap, scripts, the git remote) and drafts an
answer to every question, then grills you in rounds with Matt Pocock's `grilling` skill, each
question carrying its drafted answer so "yes" accepts it:

| Topic | What it settles |
| --- | --- |
| Tickets | where they live, how a parent holds them, how blocking is recorded, the labels, the command that reads a ticket and its comments |
| Order | which parent next, and the order inside it |
| Checks | the command for the automated checks and tests |
| Test queue | what gets run or playtested by hand, with which tools, temporary settings and how they're undone, what a test plan measures |
| Reference | an upstream or spec to stay faithful to, who wins when a ticket disagrees with it, which forks still go to you |
| Ship | the branch to push, the publish or deploy command, per ticket or per milestone |
| Changelog | where each shipped ticket's entry goes, who reads it, what it says, its order and links, where milestone summaries go, whether upcoming milestones are listed |
| Stops | anything beyond the built-in stops |
| Models | the model and effort for the coordinator, the researcher (opt-in per ticket with the `research` label; Haiku, usual effort drafted), the implementer, the Standards reviewer and the Spec reviewer |
| Commits | message style, closing keyword, attribution lines |
| Concurrency | one of three modes: one at a time, parallel worktrees (up to a limit, no prompt), or suggest and ask (asks you once for each new set, up to a limit); the limit defaults to 2 |
| Daily cap | the share of your plan's weekly usage one day may take (one day's share, 14.3%, by default), and whether it's rolling or per day (rolling if its text starts with `Rolling:`, otherwise per day) |
| Ticket budget | the tickets one coordinator ships before a fresh one takes over (4 by default); a parallel build in hand finishes first |
| Writing | the standard the agents write in: plain English, no standard, by default, or `ASD-STE100` (see [Writing](#writing)), with an optional path to your own copy of its dictionary |

The answers go to **`docs/agents/ticket-loop.md`**, the loop config, with a pointer line in
CLAUDE.md; both are committed. Every later run reads it. Edit it to change an answer, or delete
it to be grilled again.

Then setup **proves the loop closes** by doing each leg of one ticket's cycle itself:

- **Check:** the checks command passes.
- **Run:** the app starts without a click.
- **Drive:** a tool operates the app and reads its state, and a test hook takes effect.
- **Ship:** pushing and publishing need no prompt.
- **Record:** the changelog is in place.
- **Cap:** tokencount reports how much of the week today has used.

Each leg that can't be proven becomes a ticket under an **M0 · Closed loop** parent. The loop
then stops, and you close M0 with Claude in an ordinary session before running it again: the
loop can't test anything until its own legs close. Later tickets keep the cycle closed by
building any test hook their test plan needs. See
[`CLOSED-LOOP.md`](skills/ticket-loop/CLOSED-LOOP.md).

## How each ticket goes

The loop has two roles. The **launcher** is the skill in your main thread: it runs setup when
there's no config, works out the argument (a bad one fails there, in front of you), starts the
coordinator, and shows you what it hands back. The **coordinator** is a subagent shipped with
the plugin (`ticket-loop:coordinator`, on the config's coordinator model): it takes each ticket
through these steps, dispatching the researcher, implementer and reviewers as subagents of its
own, each labelled with its ticket first (`#82 research: greet option`, `#82 implement: greet
option`, `#82 spec review`). That's two levels of subagents, within Claude Code's default
nesting limit.

1. **Frontier:** the next open `ready-for-agent` ticket under the parent whose blockers are all
   closed, in the config's order. Run with tickets instead, it's the next one named, in the order
   given; a named ticket that isn't `ready-for-agent`, or waits on an open ticket you didn't name,
   is skipped and you're told why.
2. **Research (opt-in), then implement:** research runs only on a ticket carrying the
   `research` label; add it to tickets in unfamiliar code, ones that lean on a reference, or
   fixes across several files. An unlabelled ticket gets no research and no note, and its report
   says `research: not requested`. On a labelled ticket, first a cheap, read-only
   **researcher** subagent (Haiku by default) maps the ticket in a **research note** of about
   200 words, 300 at most, in order of value: the files and functions it touches as `path:line`,
   any open question or ticket–reference conflict, flagged but not decided, the patterns and
   earlier commits to follow, and the existing seams, tests and checks command. The coordinator
   posts it on the ticket as a `Research note (#82 research)` comment; a note over 300 words it
   trims to fit first, keeping every part, pointer and flagged question, and marks it
   `(trimmed from <n> words)`; the pass still counts, and the report says
   `1 research pass (trimmed)`. It edits, commits and files nothing; if it fails or gives no
   `path:line` pointers, the implementer goes ahead without it and
   the ticket's report says "research skipped". Then a fresh implementer subagent, starting from
   the ticket's research notes, builds it test-first at the seams the ticket names, runs the
   checks, commits locally (staging only its own files), and reports "ready to test" with a
   step-by-step **test plan** and the expected results.
3. **Decide:** where the ticket and the reference disagree, the config's rule settles it.
   Anything still yours comes to you in the main thread as a question with the options and a
   recommendation, while the coordinator waits. Your answer is recorded on the ticket as a
   comment and goes back to the same coordinator, which passes it to the implementer and
   carries on with the ticket; its report says which way you decided. (A headless `claude -p`
   run can't ask, so there the question ends the run: answer on the ticket and run the same
   command again.)
4. **Test and review:** the coordinator runs the test plan itself from the **test queue**, one
   ticket at a time, saying what it's about to run. To watch, open the coordinator's
   transcript in the agent view. Meanwhile two fresh reviewer subagents check the commit:
   **Standards** (the repo's conventions) and **Spec** (the ticket and the reference, where
   real bugs turn up), once per ticket. Failures and findings go to a fresh implementer, who
   fixes them all in one follow-up commit carrying the playtest record. Every later implementer
   on a `research`-labelled ticket (for the review fixes, after a test failure, or fresh after
   a decision) gets its own research pass first, scoped to what it's fixing and posted as a new note naming its
   purpose (`Research note (#82 research) for the review fixes`). The follow-up fixes aren't
   reviewed again: the coordinator re-runs the checks and the affected test steps, and anything
   found later becomes a new ticket, not another round.
5. **Ship:** the coordinator adds the ticket's changelog entry, commits it, pushes, and
   publishes as the config says.
6. **Report:** a few lines for its hand-back, including how many research passes ran, trimmed
   ones marked (or "research skipped", or `research: not requested`), then the next ticket.

## When it stops

The coordinator hands back to the main thread, which shows you why it stopped and its report
for each ticket it worked.

- Setup found the loop open: M0's tickets are filed for you to close with Claude.
- **The tickets you named have shipped** (or the rest were skipped, and it says why). It never
  goes on to their siblings.
- **The milestone is done:** it writes the milestone's summary, tells you what shipped and
  what's left for you (`ready-for-human` tickets, tickets filed for triage), and waits. It never
  starts the next milestone on its own.
- The remaining tickets are all blocked or `ready-for-human`.
- It can't read a named ticket's blockers: it dispatches nothing, and names the ticket and why the
  read failed.
- Something needs you in person: a click in a running app, a device check, credentials, a stuck
  tool.
- A push, publish or check fails in a way a fix can't safely cover.
- **The daily cap is reached.** Before each dispatch and each ship, the loop checks how much of
  your plan's weekly usage today has taken (a **per day** cap, where unused allowance is lost at
  midnight), or, with a **rolling** cap, how much the week has taken against the daily share ×
  the day of the usage week (a light day leaves more for the next). A Daily cap that doesn't
  start with `Rolling:` is per day. At the limit, or if it can't tell, it dispatches and ships
  nothing and asks you, with the use, the limit (and, rolling, the day) and where the ticket in
  hand stands:
  **stop here** (the ticket stays as it is, and it says what's committed locally), **finish this
  ticket or one more** (then it asks again), or **keep going today** (not asked again today,
  even by the next coordinator). In a headless run it can't ask, so it stops there. What you
  do next depends on the cause:
  - **The cap is reached:** raise the cap in the loop config, or run the loop interactively, to
    go on today. Otherwise run it once the limit grows: tomorrow for a per day cap, or for a
    rolling one at the week's reset time each day, when the allowance grows by a day's share.
  - **The cap can't be read:** the stop says why. Install or enable tokencount, if the stop says
    that tokencount is missing, disabled or not available. Or mark the cap not applicable in the
    loop config's Daily cap section, so the loop skips the cap. Or run the loop interactively and
    answer the question. A higher cap or a wait doesn't help here.
- Anything else your config lists.

## Models

Each role's model comes from the config: the coordinator, the researcher, the implementer and
the two reviewers. A config without a coordinator model runs it on the implementer's; one
without a researcher line runs it on Haiku at `usual` effort (`- Researcher: Haiku, usual
effort.`), since a research note is a map and should cost far less than the implementer's own
search. Either way the researcher is opt-in: it runs only on tickets labelled `research`.
The default suggestion, from a trial where Opus and Sonnet implemented the same ticket
side by side: **Opus for the implementer and the Spec reviewer, Sonnet for the Standards
reviewer.** Sonnet's implementer was about 40% faster but
missed a detail in the reference source that Opus got right; the Spec reviewer caught it, which
is why that review stays on the stronger model.

Each role's **effort** comes from the config too, next to its model, and is passed to the
subagent's dispatch (`low`, `medium`, `high`, `xhigh`, `max`). The defaults, which a config
without efforts uses without asking: **implementer `low`, coordinator `medium`, Spec reviewer
`high`**, and the researcher and Standards reviewer at `usual` (dispatched without an effort parameter). The
Spec reviewer is where real bugs turn up, so it stays thorough while the implementer runs light.
The trade-off: each ticket gets one fix pass that isn't reviewed again, so what a low-effort
implementer misses either lands in a low-effort fix pass or becomes a follow-up ticket. Raise
the implementer's effort if that happens often. To change a role's effort, edit its line in the
config's Models section:

```
- Implementer: Opus, medium effort.
- Standards reviewer: Sonnet, low effort.
```

When a run starts, the main thread's preview (see [Let it work](#getting-started)) ends with
every role as the run uses them, defaults applied:

```
Coordinator: Opus, medium · Researcher: Haiku, usual (opt-in) · Implementer: Opus, low · Standards reviewer: Sonnet, usual · Spec reviewer: Opus, high
```

Per-role effort needs Claude Code 2.1.292 or later. A model runs the highest level it supports
at or below the one asked for, and some older models don't support effort at all (see Claude
Code's model configuration docs). `CLAUDE_CODE_EFFORT_LEVEL`, if set, overrides every role's.

## Writing

Off by default. Add a `## Writing` section to the loop config with the text `ASD-STE100`, and
the agents write in [ASD-STE100 Simplified Technical English, Issue
9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf): the main thread's messages
and questions (the bars and roles line stay as they are), the coordinator's briefs, hand-backs
and reports, the implementer and reviewer reports, research notes, and ticket comments and
tickets filed in a run. Code, test names, quoted text and commit messages aren't covered. The
coordinator's definition states the rules that can be checked without the dictionary, in our
own words: short sentences (20 words for an instruction, 25 for a description), one
instruction per sentence, active voice, short paragraphs, simple tenses, short noun clusters,
one word for one meaning.

The standard is copyrighted by ASD, and its PDF forbids copying text, so the plugin only names
and links it, and never copies, extracts or converts its rules or dictionary. Words are checked
only against a local copy you download yourself: write
`ASD-STE100, dictionary at ~/Documents/ASD-STE100_ISSUE9.pdf`, and the Standards reviewer reads
the dictionary pages for the words it doubts, as a person would, and lists unapproved words
with their approved alternatives. Without a path, words aren't checked. Your project's own
terms (ticket, coordinator, commit) are technical words the check allows: list them, one line
each, in a root `GLOSSARY.md`, as [this repo's](GLOSSARY.md) does.

## Tips

- **Shared tree:** the coordinator commits its own edits (changelog, milestone summary) at
  once, so they never end up in an implementer's commit.
- **Side work during a run:** the main thread is yours, but it shares the working tree with the
  coordinator. Code edits you make there while a run is going are visible to its test runs, and
  can break a test. For code investigations during a run, use a worktree (`claude --worktree`,
  or `git worktree add`).
- **Stopping:** stop the coordinator in the agent list to stop the loop.
- **Concurrency modes:** the config's Concurrency text is one of these three forms.
  - `One at a time.` builds one ticket, then the next.
  - `Parallel worktrees: at most 2 at once.` builds independent ready tickets side by side, with
    no prompt.
  - `Suggest and ask: at most 2 at once.` names the independent ready tickets and asks you. Accept
    builds them side by side in worktrees. Decline covers that set and builds its first ticket
    only. A new set, such as the tickets left after that build, asks once; the same set never
    asks twice in a run. One ready ticket, or tickets blocked on each other, asks nothing. A
    headless run can't ask, so it takes decline, and its report says so.

  Tests run one at a time in every mode. An older config keeps working: other text that offers
  parallel worktrees is suggest and ask, and anything else is one at a time.
- **One running app:** tickets that share one app session, simulator or game engine go one at a
  time; parallel worktrees only pay off when nothing they test is shared. In a parallel build,
  the coordinator brings each worktree's commits to main and removes the worktree; tests,
  reviews, fixes and decisions then run on main, one ticket at a time. Wider concurrency is
  `/implement-spec`'s job.
- **After a restart,** run the same command again; the config and the tickets carry the state.

## Install for a team

Commit this to the project's `.claude/settings.json`, so everyone working in it gets the
plugin:

```json
{
  "extraKnownMarketplaces": {
    "ticket-loop": { "source": { "source": "github", "repo": "jhnhnsn/ticket-loop" } }
  },
  "enabledPlugins": { "ticket-loop@ticket-loop": true }
}
```

## Updating

```sh
claude plugin marketplace update ticket-loop
claude plugin update ticket-loop
```
