# Coordinators pick their dispatch mode by session

A coordinator (the loop run as a background subagent, spec #1) has to wait for its implementer and reviewers. A trial (#2, Claude Code 2.1.316) found that whether a background subagent is woken when its own background subagent finishes depends on the session. So the owner chose to have coordinators decide by session: background dispatch where they're woken, foreground dispatch where they aren't. The rule is in the coordinator's definition, `agents/coordinator.md`, under "Dispatch".

## What the trial observed

Each run was main thread → background coordinator → trivial child that slept 15–20s, then reported a word. Sonnet was used throughout.

- **Headless `claude -p` (coordinator at depth 1): not woken.** The coordinator had no SubagentHandback tool. It ended its turn with its waiting text, was marked completed with that text as its result, and the child's word went to the main thread instead. The headless main thread did stay alive until every background task ended.
- **Interactive session (coordinator at depth 2): woken.** The coordinator had SubagentHandback and ended its turn with plain text. Twenty seconds later the child's completion woke it, and it reported the child's word.
- **`claude --bg` (coordinator at depth 1): woken, but only one report delivered.** The coordinator called SubagentHandback while still waiting, which delivered its waiting text as its report. The child still woke it, but its second SubagentHandback was refused ("already delivered"). The main thread's completion notice for it came only once its child had finished.
- **Interactive resume:** after a finished coordinator was resumed with SendMessage, a fresh SubagentHandback was accepted. So spec #1's relay (resume after "decision needed" or "cap reached", then hand back again) works.
- **Headless foreground fallback:** a foreground child's report came back inline. Two foreground children dispatched in one message ran in parallel (both 11:01:02–11:01:17).
- **Headless resume:** a coordinator's SendMessage to its finished foreground child resumed that child in the background. The coordinator then ended its run, and the child's reply went to the main thread. So headless coordinators send follow-up work to a fresh foreground implementer.

We observed that being woken goes with having SubagentHandback. We didn't prove that one causes the other, which is why the skill's test is "is SubagentHandback among your tools".

## Consequences

- The coordinator's agent definition (#3) must not hide SubagentHandback in interactive sessions. Whether a `tools` list in the agent frontmatter can remove it is untested, so the definition sets no `tools` or `disallowedTools` and inherits every tool a subagent gets.
- Headless test-queue runs in the sandbox exercise only the foreground path. The background path needs an interactive or `claude --bg` run.
- Re-run the trial when Claude Code changes how subagents hand back. Ask the main thread to dispatch a background coordinator. The coordinator dispatches a background child (`date +%T; sleep 20; date +%T`, then a word), ends its turn with "COORDINATOR WAITING", and reports "COORDINATOR WOKEN: <word>" if woken. Run it headless from the sandbox with `--allowedTools "Agent Bash(sleep:*) Bash(date:*) SendMessage"`, prompt first and stdin closed.

## Open

- **Interactive SendMessage to a finished implementer (#4, untested).** After a decision, a resumed coordinator sends the user's answer to its finished background implementer with SendMessage. The trial proved a wake for a freshly dispatched background child, and a fresh SubagentHandback after a resume, but not this. Its only SendMessage data point (headless) went the wrong way: the child's reply reached the main thread. On the first real decision in an interactive run, watch whether the implementer's reply wakes the coordinator or lands in the main thread. The known-good fallback, which the coordinator's step 3 already takes when SendMessage fails: dispatch a fresh background implementer, labelled as the first, pointed at the ticket's comments and the work so far. A reply that lands in the main thread can't be seen by the coordinator, so if that happens, make the fallback step 3's only path.
