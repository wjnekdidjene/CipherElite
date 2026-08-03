import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
DIM = Style.DIM
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
CYAN = Fore.CYAN
PURPLE = Fore.MAGENTA
GREY = Fore.LIGHTBLACK_EX

BANNER = """
▓▓▓▓▓▓▓▒▓▓▒▓▓▓▓▓▓▓▒▓▓▒  ▓▓▒▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▒
▓▓▒▒▒▓▓▒▓▓▒▒▒▒▓▓▒▒▓▓▒  ▓▓▒▓▓▒▒▒▒▓▓▓▓▒▒▒▒▓▓▒
▓▓▒  ▒▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▒    ▓▓▓▓▓▓▒▒
▓▓▒  ▒▓▓▒▒▒▒▒▓▓▒▓▓▒▒▒▒  ▓▓▒▓▓▒▒▒▒▒▓▓    ▒▒▓▓▒
▒▓▓▓▓▓▓▒  ▒▓▓▒▓▓▒  ▒▓▓▒▒▓▓▒▓▓▒  ▒▒▓▓▓▓▓▓▓▒
  ▒▒▒▒▒    ▒▒▒ ▒▒▒    ▒▒▒▒▒▒ ▒▒▒    ▒▒▒▒▒
"""


def banner(name: str, version: str, author: str, handle: str):
    print()
    for line in BANNER.strip().split('\n'):
        print(f"{PURPLE}{BOLD}{line}{RESET}")
    print()
    print(f"   {GREY}{name}{RESET}  {DIM}·{RESET}  {CYAN}v{version}{RESET}")
    print(f"   {DIM}{author} · {handle}{RESET}")
    print()


def box(title: str, rows, color: str = CYAN):
    pairs = [(str(k), str(v)) for k, v in rows]
    label_w = max((len(k) for k, _ in pairs), default=0)
    body = [f"{GREY}{k.ljust(label_w)}{RESET}  {v}" for k, v in pairs]
    inner = max(len(title), max((len(b) for b in body), default=0)) + 2
    pad = lambda s: s + " " * (inner - len(s) - 1)

    print(f"{color}╭{'─' * inner}╮{RESET}")
    print(f"{color}│{RESET} {pad(f'{BOLD}{title}{RESET}')}{color}│{RESET}")
    print(f"{color}├{'─' * inner}┤{RESET}")
    for b in body:
        print(f"{color}│{RESET} {pad(b)}{color}│{RESET}")
    print(f"{color}╰{'─' * inner}╯{RESET}")


def rule(text: str = "", color: str = GREY):
    w = min(os.get_terminal_size().columns if sys.stdout.isatty() else 60, 60)
    if not text:
        print(f"{color}{'─' * w}{RESET}")
        return
    left = 3
    right = max(0, w - left - len(text) - 2)
    print(f"{color}{'─' * left} {BOLD}{text}{RESET}{color} {'─' * right}{RESET}")


def step(text: str) -> float:
    print(f"  {YELLOW}◌{RESET} {text}{DIM}…{RESET}", flush=True)
    return time.monotonic()


def ok(text: str, start: float = None):
    if start:
        elapsed = f" {DIM}{time.monotonic() - start:.2f}s{RESET}"
    else:
        elapsed = ""
    print(f"  {GREEN}●{RESET} {text}{elapsed}")


def fail(text: str, start: float = None):
    if start:
        elapsed = f" {DIM}{time.monotonic() - start:.2f}s{RESET}"
    else:
        elapsed = ""
    print(f"  {RED}●{RESET} {text}{elapsed}")


def warn(text: str):
    print(f"  {YELLOW}▲{RESET} {text}")


def info(text: str):
    print(f"  {BLUE}·{RESET} {text}")