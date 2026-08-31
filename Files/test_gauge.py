#!/usr/bin/env python3
"""
test_gauge.py — Live visual test for the CircularGauge speedometer widget.

Shows all 7 GPU-stat gauges (VRAM, VRAM Clock, GPU Usage, Temp, GPU Clock,
Power, Fan Speed) populated with animated demo values, plus optional live
readings from the first detected GPU.
"""

import sys
import os
import gi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, GLib, Adw
from Common import CircularGauge, get_gpu_stats_for_index

# Gauge definitions: (key, title, unit, gauge_type, max_value)
GAUGE_DEFS = [
    ("VRAM",       "VRAM",       "%",  "vram",      100.0),
    ("VRAM Clock", "VRAM Clock", "%",  "vram_clock", 100.0),
    ("GPU Usage",  "GPU Usage",  "%",  "usage",     100.0),
    ("Temp",       "Temp",       "°C", "temp",      110.0),
    ("GPU Clock",  "GPU Clock",  "%",  "clock",     100.0),
    ("Power",      "Power",      "W",  "power",     300.0),
    ("Fan Speed",  "Fan Speed",  "%",  "fan",       100.0),
]

GAUGE_SIZE = 140


class GaugeTestWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("GPU Stats Gauge — Test Window")
        self.set_default_size(920, 520)
        self.set_size_request(720, 400)

        self.gauges: dict[str, CircularGauge] = {}
        self._demo_step = 0
        self._demo_id = None
        self._live_id = None

        # ── Outer layout ────────────────────────────────────────────────
        toolbar_view = Adw.ToolbarView()
        headerbar = Adw.HeaderBar()
        headerbar.set_title_widget(Gtk.Label(label="GPU Stats Speedometers — Test"))
        toolbar_view.add_top_bar(headerbar)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        root.set_margin_start(20)
        root.set_margin_end(20)
        root.set_margin_top(16)
        root.set_margin_bottom(16)

        # ── Gauge grid ──────────────────────────────────────────────────
        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(8)
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_hexpand(True)

        cols = 4
        for idx, (key, title, unit, gtype, max_v) in enumerate(GAUGE_DEFS):
            col = idx % cols
            row = idx // cols

            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            cell.set_halign(Gtk.Align.CENTER)
            cell.set_valign(Gtk.Align.CENTER)

            g = CircularGauge(
                size=GAUGE_SIZE,
                title=title,
                unit=unit,
                gauge_type=gtype,
                min_value=0.0,
                max_value=max_v,
            )
            g.set_value(0.0, subtitle="—")
            g.set_hexpand(False)
            g.set_vexpand(False)

            self.gauges[key] = g
            cell.append(g)
            grid.attach(cell, col, row, 1, 1)

        root.append(grid)

        # ── Buttons ─────────────────────────────────────────────────────
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)

        self._demo_btn = Gtk.Button(label="▶  Start Demo")
        self._demo_btn.add_css_class("suggested-action")
        self._demo_btn.connect("clicked", self._toggle_demo)
        btn_box.append(self._demo_btn)

        live_btn = Gtk.Button(label="⚡  Live GPU Readings")
        live_btn.connect("clicked", self._start_live)
        btn_box.append(live_btn)

        reset_btn = Gtk.Button(label="↺  Reset")
        reset_btn.connect("clicked", self._reset)
        btn_box.append(reset_btn)

        root.append(btn_box)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_child(root)

        toolbar_view.set_content(scroll)
        self.set_content(toolbar_view)

    # ── Demo animation ───────────────────────────────────────────────────
    def _toggle_demo(self, _btn):
        if self._demo_id:
            GLib.source_remove(self._demo_id)
            self._demo_id = None
            self._demo_btn.set_label("▶  Start Demo")
        else:
            self._demo_btn.set_label("⏸  Pause Demo")
            self._demo_id = GLib.timeout_add(80, self._demo_tick)

    def _demo_tick(self):
        self._demo_step = (self._demo_step + 1) % 200
        t = self._demo_step / 200.0  # 0 → 1 → 0 cycle

        import math
        # Sine wave at different frequencies for each gauge
        vals = {
            "VRAM":       55 + 40 * math.sin(t * 2 * math.pi),
            "VRAM Clock": 70 + 28 * math.sin(t * 2 * math.pi + 0.5),
            "GPU Usage":  50 + 48 * math.sin(t * 2 * math.pi + 1.0),
            "Temp":       45 + 55 * abs(math.sin(t * math.pi)),
            "GPU Clock":  65 + 33 * math.sin(t * 2 * math.pi + 1.5),
            "Power":      80 + 180 * abs(math.sin(t * math.pi + 0.3)),
            "Fan Speed":  30 + 65 * abs(math.sin(t * math.pi + 0.8)),
        }
        subtitles = {
            "VRAM":       f"{int(vals['VRAM'] * 81.92)}/{8192}MB",
            "VRAM Clock": f"{int(vals['VRAM Clock'] * 20)}/2000MHz",
            "GPU Usage":  "",
            "Temp":       "",
            "GPU Clock":  f"{int(vals['GPU Clock'] * 24)}/2400MHz",
            "Power":      "",
            "Fan Speed":  "",
        }
        for key, g in self.gauges.items():
            g.set_value(vals.get(key, 0.0), subtitle=subtitles.get(key, ""))
        return True

    # ── Live GPU readings ────────────────────────────────────────────────
    def _start_live(self, _btn):
        if self._demo_id:
            GLib.source_remove(self._demo_id)
            self._demo_id = None
            self._demo_btn.set_label("▶  Start Demo")
        if self._live_id:
            return
        self._live_id = GLib.timeout_add(1000, self._live_tick)
        self._live_tick()

    def _live_tick(self):
        import threading
        def fetch():
            s = get_gpu_stats_for_index(0)
            GLib.idle_add(self._apply_live, s)
        threading.Thread(target=fetch, daemon=True).start()
        return True

    def _apply_live(self, s):
        if not s:
            return
        mem_used  = s.get("mem_used") or 0
        mem_total = s.get("mem_total") or 0
        vram_pct  = (mem_used / mem_total * 100) if mem_total > 0 else 0
        self.gauges["VRAM"].set_value(vram_pct, subtitle=f"{mem_used}/{mem_total}MB")

        vc_cur = s.get("vram_clock") or 0
        vc_max = s.get("vram_clock_max") or 0
        vc_pct = (vc_cur / vc_max * 100) if vc_max > 0 else 0
        self.gauges["VRAM Clock"].set_value(vc_pct, subtitle=f"{vc_cur}/{vc_max}MHz" if vc_max > 0 else f"{vc_cur}MHz")

        usage = s.get("usage")
        if usage is not None and usage >= 0:
            self.gauges["GPU Usage"].set_value(usage)

        temp = s.get("temp") or 0
        if temp > 0:
            self.gauges["Temp"].set_value(temp)

        clk_cur = s.get("clock_current") or 0
        clk_max = s.get("clock_max") or 0
        clk_pct = (clk_cur / clk_max * 100) if clk_max > 0 else 0
        self.gauges["GPU Clock"].set_value(clk_pct, subtitle=f"{clk_cur}/{clk_max}MHz" if clk_max > 0 else f"{clk_cur}MHz")

        power = s.get("power_usage") or 0
        if power > 0:
            self.gauges["Power"].set_value(power)

        fan = s.get("fan_speed")
        if fan is not None and fan >= 0:
            self.gauges["Fan Speed"].set_value(fan)

    def _reset(self, _btn):
        if self._demo_id:
            GLib.source_remove(self._demo_id)
            self._demo_id = None
            self._demo_btn.set_label("▶  Start Demo")
        if self._live_id:
            GLib.source_remove(self._live_id)
            self._live_id = None
        for g in self.gauges.values():
            g.set_value(0.0, subtitle="—")


class TestApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.gpuviewer.gauge_test")
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        win = GaugeTestWindow(app)
        win.present()


if __name__ == "__main__":
    app = TestApp()
    sys.exit(app.run(None))
