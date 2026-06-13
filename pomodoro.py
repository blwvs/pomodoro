"""
Pomodoro Timer — terminal TUI, no dependencies beyond stdlib.

Controls:
  ENTER  start / pause
  r      reset current session
  s      skip to next session
  q      quit
"""

import sys
import time
import threading
import msvcrt  # Windows keyboard input
import os

# ── Config ────────────────────────────────────────────────────────────────────
WORK_MINUTES    = 25
SHORT_BREAK     = 5
LONG_BREAK      = 15
SESSIONS_BEFORE_LONG = 4

# ── ANSI helpers ──────────────────────────────────────────────────────────────
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_LINE  = "\r\033[K"
RESET       = "\033[0m"

def color(text, code): return f"\033[{code}m{text}{RESET}"

RED    = lambda t: color(t, "91")
GREEN  = lambda t: color(t, "92")
YELLOW = lambda t: color(t, "93")
CYAN   = lambda t: color(t, "96")
BOLD   = lambda t: color(t, "1")
DIM    = lambda t: color(t, "2")

# ── State ─────────────────────────────────────────────────────────────────────
class State:
    def __init__(self):
        self.session_count  = 0   # completed work sessions
        self.phase          = "work"  # "work" | "short" | "long"
        self.running        = False
        self.seconds_left   = WORK_MINUTES * 60
        self.lock           = threading.Lock()
        self.skip_requested = False
        self.reset_requested = False

    @property
    def total_seconds(self):
        if self.phase == "work":  return WORK_MINUTES * 60
        if self.phase == "short": return SHORT_BREAK * 60
        return LONG_BREAK * 60

    def advance_phase(self):
        if self.phase == "work":
            self.session_count += 1
            if self.session_count % SESSIONS_BEFORE_LONG == 0:
                self.phase = "long"
            else:
                self.phase = "short"
        else:
            self.phase = "work"
        self.seconds_left = self.total_seconds

    def reset(self):
        self.seconds_left = self.total_seconds
        self.running = False

# ── Rendering ─────────────────────────────────────────────────────────────────
BAR_WIDTH = 30

def phase_label(phase):
    if phase == "work":  return GREEN("● FOCUS")
    if phase == "short": return CYAN("◎ SHORT BREAK")
    return YELLOW("◎ LONG BREAK")

def render(state):
    with state.lock:
        mins, secs  = divmod(int(state.seconds_left), 60)
        total       = state.total_seconds
        elapsed     = total - state.seconds_left
        filled      = int(BAR_WIDTH * elapsed / total)
        bar         = "█" * filled + "░" * (BAR_WIDTH - filled)
        bar_colored = (GREEN if state.phase == "work" else CYAN)(bar)
        status      = BOLD("▶ RUNNING") if state.running else DIM("⏸ PAUSED ")
        phase_str   = phase_label(state.phase)
        sessions    = f"Sessions: {BOLD(str(state.session_count))}"
        next_break  = SESSIONS_BEFORE_LONG - (state.session_count % SESSIONS_BEFORE_LONG)
        next_str    = DIM(f"(long break in {next_break} session{'s' if next_break != 1 else ''})")

    lines = [
        "",
        f"  {BOLD('🍅  POMODORO TIMER')}",
        "",
        f"  {phase_str}",
        f"  {BOLD(f'{mins:02d}:{secs:02d}')}",
        "",
        f"  [{bar_colored}]",
        "",
        f"  {status}    {sessions}  {next_str}",
        "",
        DIM("  ENTER start/pause  ·  r reset  ·  s skip  ·  q quit"),
        "",
    ]
    return "\n".join(lines)

# ── Timer thread ──────────────────────────────────────────────────────────────
def tick(state, stop_event):
    while not stop_event.is_set():
        time.sleep(0.25)
        with state.lock:
            if state.reset_requested:
                state.reset_requested = False
                state.seconds_left = state.total_seconds
                state.running = False
                continue
            if state.skip_requested:
                state.skip_requested = False
                state.advance_phase()
                state.running = False
                continue
            if not state.running:
                continue
            state.seconds_left -= 0.25
            if state.seconds_left <= 0:
                state.advance_phase()
                state.running = False
                # beep
                print("\a", end="", flush=True)

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    os.system("cls")
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    state = State()
    stop_event = threading.Event()
    t = threading.Thread(target=tick, args=(state, stop_event), daemon=True)
    t.start()

    last_render = ""
    try:
        while True:
            # render
            frame = render(state)
            if frame != last_render:
                os.system("cls")
                print(frame, flush=True)
                last_render = frame

            # non-blocking key check (Windows)
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\r", "\n", " "):       # ENTER / space → toggle
                    with state.lock:
                        state.running = not state.running
                elif ch in ("r", "R"):
                    with state.lock:
                        state.reset_requested = True
                elif ch in ("s", "S"):
                    with state.lock:
                        state.skip_requested = True
                elif ch in ("q", "Q"):
                    break

            time.sleep(0.1)
    finally:
        stop_event.set()
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()
        os.system("cls")
        print(f"\n  Thanks for focusing! Completed sessions: {BOLD(str(state.session_count))}\n")

if __name__ == "__main__":
    main()
