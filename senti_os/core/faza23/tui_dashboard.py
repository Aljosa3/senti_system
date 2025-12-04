import curses
import time
from datetime import datetime
from senti_os.core.faza22.boot_manager import BootManager
from senti_os.core.faza22.logs_manager import LogsManager

class SentiTUIDashboard:
    """
    FAZA 23 – Terminal UI Dashboard for Senti OS.
    Displays:
      - System status
      - Boot state
      - Stack health
      - Recent logs
      - Recent events
    """

    REFRESH_INTERVAL = 0.5

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.boot_manager = BootManager()
        self.logs_manager = LogsManager()
        curses.curs_set(0)
        self.mode = "system"  # system | stacks | logs | events | help

    def draw_box(self, y, x, w, title):
        self.stdscr.addstr(y, x, "+" + "-"*(w-2) + "+")
        self.stdscr.addstr(y, x+2, f"[ {title} ]")
        self.stdscr.addstr(y+1, x, "|")
        self.stdscr.addstr(y+1, x+w-1, "|")

    def render(self):
        while True:
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()

            status = self.boot_manager.get_status()
            system = status["system"]
            health = status["health"]
            stacks = status["stacks"]
            events = status["events"]["recent"]
            logs = self.logs_manager.get_logs(limit=20)

            self.stdscr.addstr(0, 0, "SENTI OS – FAZA 23 Dashboard   (q=quit, r=refresh, s=stacks, l=logs, e=events, h=help)")
            self.stdscr.addstr(1, 0, "-" * (max_x - 1))

            if self.mode == "system":
                self.render_system(system, health)
            elif self.mode == "stacks":
                self.render_stacks(stacks)
            elif self.mode == "logs":
                self.render_logs(logs)
            elif self.mode == "events":
                self.render_events(events)
            elif self.mode == "help":
                self.render_help()

            self.stdscr.refresh()
            time.sleep(self.REFRESH_INTERVAL)

            key = self.stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('r'):
                continue
            elif key == ord('s'):
                self.mode = "stacks"
            elif key == ord('l'):
                self.mode = "logs"
            elif key == ord('e'):
                self.mode = "events"
            elif key == ord('h'):
                self.mode = "help"
            else:
                self.mode = "system"

    def render_system(self, system, health):
        self.stdscr.addstr(3, 2, f"System State: {system['state']}")
        self.stdscr.addstr(4, 2, f"Uptime: {system.get('uptime_seconds', 0)} seconds")
        self.stdscr.addstr(5, 2, f"Boot Completed: {system.get('boot_completed_at', 'N/A')}")

        self.stdscr.addstr(7, 2, f"Enabled Stacks: {health['enabled_stacks']}/{health['total_stacks']}")
        self.stdscr.addstr(8, 2, f"Running Stacks: {health['running_stacks']}")
        self.stdscr.addstr(9, 2, f"Error Stacks: {health['error_stacks']}")

    def render_stacks(self, stacks):
        y = 3
        for name, info in stacks.items():
            self.stdscr.addstr(y, 2, f"{name:<10} : {info['status']}")
            y += 1

    def render_logs(self, logs):
        y = 3
        for log in logs:
            ts = log["timestamp"][:19]
            lvl = log["level"].upper()
            msg = log["message"]
            self.stdscr.addstr(y, 2, f"[{ts}] {lvl:<7} {msg}")
            y += 1

    def render_events(self, events):
        y = 3
        for e in events:
            self.stdscr.addstr(y, 2, f"{e['timestamp'][:19]}  {e['type']}  {e['message']}")
            y += 1

    def render_help(self):
        self.stdscr.addstr(3, 2, "HELP:")
        self.stdscr.addstr(4, 2, "q = Quit dashboard")
        self.stdscr.addstr(5, 2, "s = Stacks View")
        self.stdscr.addstr(6, 2, "l = Logs View")
        self.stdscr.addstr(7, 2, "e = Events View")
        self.stdscr.addstr(8, 2, "h = Help")
        self.stdscr.addstr(9, 2, "r = Refresh")
