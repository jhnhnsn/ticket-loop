# Changelog

What changes for you, the person running the loop, newest first.

## Unreleased

- The run's preview shows two bars under the ready count: the tickets shipped out of the run's total, and today's usage against your daily cap. If there's no plan usage, or it can't be read, a line says so instead of a bar. The bars show again, read fresh, at every hand-back. At a handover they come in the message saying which coordinator took over. ([#19](https://github.com/jhnhnsn/ticket-loop/issues/19))
- Each role runs at an effort you can set in the loop config, next to its model: by default the implementer at `low`, the coordinator at `medium`, the Spec reviewer at `high` and the Standards reviewer at its usual effort. Configs without efforts use these without asking, and setup asks for them. The run's preview, now shown as the first coordinator starts, gives each role's model and effort on a line under the ready count. ([#18](https://github.com/jhnhnsn/ticket-loop/issues/18))
- Long runs are split across coordinators, so none of them fills its context. Each ships at most the config's ticket budget (4 unless you set one), then a fresh `… coordinator 2` takes over from the tracker without asking you. As the first one starts, the run is previewed: `M1: 7 ready, about 2 coordinators.` Setup asks for the budget. ([#5](https://github.com/jhnhnsn/ticket-loop/issues/5))

## 1.9.0

Runs go through a coordinator subagent, so your main thread stays free, and a decision that's yours no longer ends the run. Published partway through the coordinator milestone (#1): the ticket budget, handover and the daily cap across coordinators are still to come.

- A decision that's yours no longer ends the run. The coordinator hands it to the main thread, which asks you, records your answer on the ticket, and resumes the same coordinator to carry on. A headless run still stops at a decision: answer on the ticket and run again. ([#4](https://github.com/jhnhnsn/ticket-loop/issues/4))
- Runs go through a coordinator. `/ticket-loop:ticket-loop` now hands each run to a background `ticket-loop: <run> coordinator 1` agent that builds, tests, reviews and ships the tickets, so your main thread stays free. Any question about running tickets in parallel is asked up front. Watch the test queue in the coordinator's transcript in the agent view. A decision or the daily cap still ends the run for now: answer or raise the cap, then run the command again. ([#3](https://github.com/jhnhnsn/ticket-loop/issues/3))
- Coordinators will dispatch by session: in the background when they can be woken (interactive and `claude --bg`), in the foreground in headless `claude -p` runs, where ending a turn ends the run. Settled by trying it; the evidence is in ADR-0001. ([#2](https://github.com/jhnhnsn/ticket-loop/issues/2))
