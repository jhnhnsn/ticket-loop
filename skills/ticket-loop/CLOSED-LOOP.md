# The closed loop

The loop runs unattended only if every ticket's cycle **closes**: you can take a commit from checked to shipped and recorded with no human in it. A cycle is five **legs**. Each one closes when you can do it alone, from the terminal or an MCP, and read its result as pass or fail.

| Leg | Closes when | The config section |
| --- | --- | --- |
| **Check** | one command runs every automated check and test; its exit code is the verdict | Checks |
| **Run** | one command starts the app (or confirms it's running) and says when it's ready, without a click | Test queue |
| **Drive** | you can operate the running app and read its state through a tool (an MCP, a browser driver, adb, a CLI, an HTTP API), and put it into a test's situation through **test hooks** (debug settings, seeded data, a test-only command) instead of by hand | Test queue |
| **Ship** | one command pushes and publishes or deploys, with no prompt; any secret reaches only that step (envstow's `run --only`, say) | Ship |
| **Record** | the changelog's file, section and entry format are settled, so an entry is a commit you make | Changelog |

A leg can be **not applicable**: a library has no Run or Drive (Check closes its cycle), and an unpublished tool has no Ship. Record that in the config with the reason, so it isn't mistaken for a gap.

## Proving it

Setup proves each leg by doing it, never by reading about it:

- **Check:** run the command. It passes, or fails only on known, ticketed problems.
- **Run and Drive:** start the app, drive one trivial thing through the tool, and read a value back, as a test plan would. Then set one test hook and see it take effect.
- **Ship:** run the ship command's dry run if it has one. Without one, confirm each step it runs can go unattended: the remote push works, the secrets are listed in the store (`envstow list`), and nothing prompts. Never publish just to prove the leg.
- **Record:** the changelog file exists with the settled section.

A leg that can't be proven is **open**.

## Closing the gaps

Each open leg becomes a ticket under one parent, **M0 · Closed loop**, made the tracker's way: what's missing, what closing it means (the row above), and how to prove it (the list above).

- A leg that needs the owner (an account, a key, an install, a setting in a dashboard) is `ready-for-human`.
- Anything else is `ready-for-agent`.

M0 is worked in an ordinary session with the user, never by the loop: the loop can't test work until its own legs close. Run the loop again once M0 is closed.

## Keeping it closed

Every later ticket's test plan goes through the Drive leg. When a plan needs a hook the app doesn't have yet (a way to reach a state, or to read a value), building that hook is part of the ticket. That's how the Drive leg grows with the app.
