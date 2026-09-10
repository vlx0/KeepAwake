"""KeepAwake — dark GUI + tray."""

from __future__ import annotations

import ctypes
import threading
import tkinter as tk
from typing import Callable

from . import __version__
from .awake import AwakeGuard
from .instance import WINDOW_TITLE

BG = "#111111"
FG = "#ffffff"
MUTED = "#999999"
CARD = "#1a1a1a"
OK = "#86efac"
WARN = "#f87171"
ACCENT = "#93c5fd"


def make_tray_image(active: bool):
    from PIL import Image, ImageDraw

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (134, 239, 172, 255) if active else (148, 163, 184, 255)
    draw.rounded_rectangle((6, 6, size - 6, size - 6), radius=12, fill=color)
    draw.ellipse((22, 18, 42, 38), outline=(17, 17, 17, 255), width=3)
    draw.rectangle((30, 36, 34, 48), fill=(17, 17, 17, 255))
    return img


class TrayIcon:
    def __init__(
        self,
        app: "KeepAwakeApp",
        on_show: Callable[[], None],
        on_toggle: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self._app = app
        self._on_show = on_show
        self._on_toggle = on_toggle
        self._on_quit = on_quit
        self._icon = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True, name="KeepAwakeTray")
        self._thread.start()
        self._ready.wait(timeout=5)

    def _run(self) -> None:
        import pystray
        from pystray import MenuItem as item

        menu = pystray.Menu(
            item("Открыть", lambda _i, _it: self._app.after(0, self._on_show)),
            item(
                "Не спать",
                lambda _i, _it: self._app.after(0, self._on_toggle),
                checked=lambda _i: self._app.guard.active,
            ),
            pystray.Menu.SEPARATOR,
            item("Выход", lambda _i, _it: self._app.after(0, self._on_quit)),
        )
        self._icon = pystray.Icon(
            "KeepAwake",
            make_tray_image(True),
            "KeepAwake — не спать",
            menu,
        )
        self._ready.set()
        self._icon.run()

    def refresh(self, active: bool) -> None:
        if self._icon is None:
            return
        try:
            self._icon.icon = make_tray_image(active)
            self._icon.title = "KeepAwake — не спит" if active else "KeepAwake — сон разрешён"
            self._icon.update_menu()
        except Exception:
            pass

    def notify(self, text: str, title: str = "KeepAwake") -> None:
        if self._icon is not None:
            try:
                self._icon.notify(text, title)
            except Exception:
                pass

    def stop(self) -> None:
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None


class KeepAwakeApp(tk.Tk):
    def __init__(self, start_hidden: bool = False) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("420x300")
        self.minsize(360, 260)
        self.configure(bg=BG)
        self.guard = AwakeGuard()
        self._exiting = False
        self._start_hidden = start_hidden
        self._tray: TrayIcon | None = None

        pad = tk.Frame(self, bg=BG)
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(pad, text="KeepAwake", bg=BG, fg=FG, font=("Segoe UI Semibold", 18)).pack(anchor="w")
        tk.Label(
            pad,
            text="Не давать ПК уснуть и погасить экран",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 18))

        card = tk.Frame(pad, bg=CARD, padx=20, pady=18)
        card.pack(fill="x")

        self._hint = tk.Label(
            card,
            text="Система не уйдёт в сон",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
            justify="center",
        )
        self._hint.pack(anchor="center")

        self._btn = tk.Label(
            card,
            text="Включено",
            bg=OK,
            fg=BG,
            font=("Segoe UI", 11),
            padx=22,
            pady=12,
            cursor="hand2",
        )
        self._btn.pack(anchor="center", pady=(16, 0))
        self._btn.bind("<Button-1>", lambda _e: self.toggle())

        self._status = tk.Label(
            pad,
            text=f"закрытие окна → в трей · v{__version__}",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        )
        self._status.pack(fill="x", pady=(16, 0))

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.guard.enable()
        self._refresh()
        self.after(20, self._place)
        self.after(200, self._start_tray)
        if start_hidden:
            self.after(350, self.hide_to_tray)

    def _place(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width() or 420, self.winfo_height() or 300
        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 3}")

    def _start_tray(self) -> None:
        try:
            self._tray = TrayIcon(self, on_show=self.show_window, on_toggle=self.toggle, on_quit=self.quit_app)
            self._tray.start()
            self._tray.refresh(self.guard.active)
            if self._start_hidden:
                self.after(
                    800,
                    lambda: self._tray and self._tray.notify("KeepAwake включён — ПК не заснёт"),
                )
        except Exception as e:
            self._status.configure(text=f"трей: {e}", fg=WARN)

    def _refresh(self) -> None:
        active = self.guard.active
        if active:
            self._hint.configure(text="Система не уйдёт в сон")
            self._btn.configure(text="Включено", bg=OK, fg=BG)
        else:
            self._hint.configure(text="Система может уснуть")
            self._btn.configure(text="Выключено", bg="#333333", fg=FG)
        if self._tray is not None:
            self._tray.refresh(active)

    def toggle(self) -> None:
        self.guard.toggle()
        self._refresh()
        if self._tray is not None:
            self._tray.notify("Включено" if self.guard.active else "Выключено")

    def show_window(self) -> None:
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(80, lambda: self.attributes("-topmost", False))
        self.focus_force()
        self._refresh()

    def hide_to_tray(self) -> None:
        self.withdraw()

    def quit_app(self) -> None:
        if self._exiting:
            return
        self._exiting = True
        self.guard.disable()
        if self._tray is not None:
            try:
                self._tray.stop()
            except Exception:
                pass
        self.destroy()


def run(start_hidden: bool = False) -> None:
    KeepAwakeApp(start_hidden=start_hidden).mainloop()
