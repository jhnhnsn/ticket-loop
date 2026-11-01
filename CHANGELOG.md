# Changelog

What changes for you, the person running the loop, newest first.

## Unreleased

- A decision that's yours no longer ends the run. The coordinator hands it to the main thread, which asks you, records your answer on the ticket, and resumes the same coordinator to carry on. A headless run still stops at a decision: answer on the ticket and run again. ([#4](https://github.com/jhnhnsn/ticket-loop/issues/4))
- Runs go through a coordinator. `/ticket-loop:ticket-loop` now hands each run to a background `ticket-loop: <run> coordinator 1` agent that builds, tests, reviews and ships the tickets, so your main thread stays free. Any question about running tickets in parallel is asked up front. Watch the test queue in the coordinator's transcript in the agent view. A decision or the daily cap still ends the run for now: answer or raise the cap, then run the command again. ([#3](https://github.com/jhnhnsn/ticket-loop/issues/3))
- Coordinators will dispatch by session: in the background when they can be woken (interactive and `claude --bg`), in the foreground in headless `claude -p` runs, where ending a turn ends the run. Settled by trying it; the evidence is in ADR-0001. ([#2](https://github.com/jhnhnsn/ticket-loop/issues/2))
