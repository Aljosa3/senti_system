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
        try:
            curses.curs_set(0)
        except:
            pass  # Some terminals don't support cursor visibility
        self.mode = "system"  # system | stacks | logs | events | help
        stdscr.nodelay(True)  # Non-blocking input

    def draw_box(self, y, x, w, title):
        self.stdscr.addstr(y, x, "+" + "-"*(w-2) + "+")
        self.stdscr.addstr(y, x+2, f"[ {title} ]")
        self.stdscr.addstr(y+1, x, "|")
        self.stdscr.addstr(y+1, x+w-1, "|")

    def render(self):
        while True:
            try:
                self.stdscr.clear()
                max_y, max_x = self.stdscr.getmaxyx()

                status = self.boot_manager.get_status()
                system = status["system"]
                health = status["health"]
                stacks = status["stacks"]
                events = status["events"]["recent"]
                logs = self.logs_manager.get_logs(limit=20)

                # Header
                header = "SENTI OS – FAZA 23 Dashboard   (q=quit, r=refresh, s=stacks, l=logs, e=events, h=help)"
                self.safe_addstr(0, 0, header[:max_x-1])
                self.safe_addstr(1, 0, "-" * min(max_x - 1, 120))

                # Render current mode
                if self.mode == "system":
                    self.render_system(system, health, max_y, max_x)
                elif self.mode == "stacks":
                    self.render_stacks(stacks, max_y, max_x)
                elif self.mode == "logs":
                    self.render_logs(logs, max_y, max_x)
                elif self.mode == "events":
                    self.render_events(events, max_y, max_x)
                elif self.mode == "help":
                    self.render_help(max_y, max_x)

                # Footer with current mode
                footer = f" Mode: {self.mode.upper()} "
                self.safe_addstr(max_y - 1, 0, footer)

                self.stdscr.refresh()
            except Exception as e:
                # If rendering fails, try to display error
                try:
                    self.stdscr.clear()
                    self.safe_addstr(0, 0, f"Error: {str(e)}")
                    self.stdscr.refresh()
                except:
                    pass

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
            elif key == ord('1'):
                self.mode = "system"

    def safe_addstr(self, y, x, text):
        """Safely add string to screen, handling out of bounds."""
        try:
            max_y, max_x = self.stdscr.getmaxyx()
            if y < max_y and x < max_x:
                # Truncate text if too long
                available_width = max_x - x - 1
                if len(text) > available_width:
                    text = text[:available_width]
                self.stdscr.addstr(y, x, text)
        except:
            pass

    def render_system(self, system, health, max_y, max_x):
        uptime = system.get('uptime_seconds') or 0
        self.safe_addstr(3, 2, f"System State: {system['state'].upper()}")
        self.safe_addstr(4, 2, f"Uptime: {uptime:.0f} seconds")
        self.safe_addstr(5, 2, f"Boot Completed: {system.get('boot_completed_at', 'N/A')}")

        self.safe_addstr(7, 2, f"Enabled Stacks: {health['enabled_stacks']}/{health['total_stacks']}")
        self.safe_addstr(8, 2, f"Running Stacks: {health['running_stacks']}")
        self.safe_addstr(9, 2, f"Error Stacks: {health['error_stacks']}")

        # Health indicator
        if health['error_stacks'] == 0 and system['state'] == 'running':
            self.safe_addstr(11, 2, "Health: ✓ HEALTHY")
        else:
            self.safe_addstr(11, 2, f"Health: ⚠ DEGRADED")

    def render_stacks(self, stacks, max_y, max_x):
        self.safe_addstr(3, 2, "Stack Status:")
        y = 5
        for name, info in stacks.items():
            if y >= max_y - 2:
                break
            status_icon = "✓" if info['status'] == 'running' else "○"
            self.safe_addstr(y, 2, f"{status_icon} {name:<10} : {info['status']}")
            if info.get('error'):
                y += 1
                self.safe_addstr(y, 4, f"  Error: {info['error'][:max_x-10]}")
            y += 1

    def render_logs(self, logs, max_y, max_x):
        self.safe_addstr(3, 2, "Recent Logs:")
        y = 5
        for log in logs:
            if y >= max_y - 2:
                break
            ts = log["timestamp"][:19]
            lvl = log["level"].upper()
            msg = log["message"]
            log_line = f"[{ts}] {lvl:<7} {msg}"
            self.safe_addstr(y, 2, log_line[:max_x-4])
            y += 1

    def render_events(self, events, max_y, max_x):
        self.safe_addstr(3, 2, "Recent Events:")
        y = 5
        for e in events:
            if y >= max_y - 2:
                break
            ts = e.get('timestamp', '')[:19]
            evt_type = e.get('type', 'unknown')
            msg = e.get('message', '')
            event_line = f"{ts}  {evt_type}  {msg}"
            self.safe_addstr(y, 2, event_line[:max_x-4])
            y += 1

    def render_help(self, max_y, max_x):
        self.safe_addstr(3, 2, "FAZA 23 TUI Dashboard - Help")
        self.safe_addstr(4, 2, "=" * 40)
        self.safe_addstr(6, 2, "Navigation:")
        self.safe_addstr(7, 4, "q or Q      - Quit dashboard")
        self.safe_addstr(8, 4, "1 or Enter  - System View (default)")
        self.safe_addstr(9, 4, "s           - Stacks View")
        self.safe_addstr(10, 4, "l           - Logs View")
        self.safe_addstr(11, 4, "e           - Events View")
        self.safe_addstr(12, 4, "h           - Help (this screen)")
        self.safe_addstr(13, 4, "r           - Force Refresh")
        self.safe_addstr(15, 2, "The dashboard auto-refreshes every 0.5 seconds.")
