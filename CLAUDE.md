# CLAUDE.md

Guidance for AI assistants working in this repository.

## Overview

A single-file Pomodoro timer that runs as a terminal TUI. It cycles through
focus sessions and breaks, drawing a live-updating progress bar with ANSI
colors and reacting to keyboard input. There are no dependencies beyond the
Python standard library.

## Project layout

- `pomodoro.py` — the entire application. Run it directly; there is no package,
  build step, or install.
- `README.md` — placeholder content only.

## Running

```
python pomodoro.py
```

There are no tests, linters, build scripts, or CI configured. The repository is
intentionally minimal; "the codebase" is one ~180-line script.

### Controls

- `ENTER` (or space) — start / pause
- `r` — reset the current session
- `s` — skip to the next session
- `q` — quit

## Platform note (important)

**This script is currently Windows-only.** It depends on Windows-specific APIs:

- `import msvcrt` — used for non-blocking keyboard input (`msvcrt.kbhit()`,
  `msvcrt.getwch()`). This module does not exist on macOS or Linux, so the
  script raises `ModuleNotFoundError` on import there.
- `os.system("cls")` — clears the screen using the Windows command; on
  Unix-like systems the equivalent is `clear`.

If asked to make the app cross-platform, both of these need replacing (e.g.
`termios`/`tty`/`select` for input on Unix, and an OS check for the clear
command). The ANSI escape codes themselves work on modern Windows terminals
and Unix terminals alike.

## Architecture

The program has three concurrent concerns coordinated through a shared `State`
object guarded by a `threading.Lock`:

1. **`State`** (`pomodoro.py`) — holds `session_count`, `phase`
   (`"work"` | `"short"` | `"long"`), `running`, `seconds_left`, and the
   `skip_requested` / `reset_requested` flags. `advance_phase()` encodes the
   Pomodoro cycle: after every work session it goes to a short break, except
   every `SESSIONS_BEFORE_LONG`th session which triggers a long break, then back
   to work.
2. **Timer thread (`tick`)** — a daemon thread that wakes every 0.25s. It
   processes the reset/skip flags, decrements `seconds_left` by 0.25 while
   running, and on reaching zero advances the phase, pauses, and emits a beep
   (`\a`).
3. **Main loop (`main`)** — renders the frame, redraws only when it changes
   (diffed against `last_render`), and polls the keyboard non-blockingly,
   sleeping 0.1s per iteration. On exit it restores the cursor and prints a
   summary.

### Key conventions and gotchas

- **The tick interval is load-bearing.** The timer thread sleeps 0.25s and
  subtracts 0.25 from `seconds_left` per tick. These two values must stay in
  sync — if they diverge, the timer runs at the wrong speed. (A prior bug had
  the timer running 4x too fast; see commit history.) If you change the sleep
  duration, change the decrement to match.
- **All access to `State` mutable fields goes through `state.lock`.** The timer
  thread and main loop both touch the same fields. Keep reads and writes inside
  `with state.lock:` blocks, and keep those blocks short (the existing code
  copies values out under the lock, then renders outside it).
- **Config lives in module-level constants** near the top of `pomodoro.py`:
  `WORK_MINUTES`, `SHORT_BREAK`, `LONG_BREAK`, `SESSIONS_BEFORE_LONG`. Adjust
  durations there.
- **Rendering style** uses small lambda color helpers (`RED`, `GREEN`, etc.)
  built on the `color()` function and ANSI codes. Follow that pattern for new
  output rather than embedding raw escape codes.
- **No external dependencies.** Keep it stdlib-only unless there's a strong
  reason to change that.

## Git workflow

- Active development branch for this work: `claude/claude-md-docs-yi7y8t`.
- The default branch is `main`.
- Commit with clear, descriptive messages and push to the designated branch.
- Do not open a pull request unless explicitly asked.
