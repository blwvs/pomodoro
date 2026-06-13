# Pomodoro Timer

A terminal-based Pomodoro timer for Windows with no dependencies beyond the Python standard library.

## Usage

```
python pomodoro.py
```

## Controls

| Key | Action |
|-----|--------|
| `Enter` / `Space` | Start / pause |
| `r` | Reset current session |
| `s` | Skip to next session |
| `q` | Quit |

## Configuration

Edit the constants at the top of `pomodoro.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `WORK_MINUTES` | 25 | Focus session length |
| `SHORT_BREAK` | 5 | Short break length |
| `LONG_BREAK` | 15 | Long break length |
| `SESSIONS_BEFORE_LONG` | 4 | Sessions before a long break |
