#!/usr/bin/env python3
"""Test window for CircularGauge widget"""

import sys
import os
import gi
import time

# Set up path and environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

gi.require_version('Gtk', '4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Gtk, GLib, Adw
from Common import CircularGauge

class GaugeTestWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Gauge Test Window")
        self.set_size_request(800, 600)
        self.set_default_size(800, 600)
        
        # Create main vertical box
        main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        
        # Title
        title = Gtk.Label.new("GPU Stats Gauges Test")
        title.add_css_class("title-1")
        main_box.append(title)
        
        # Create a horizontal scroll view for gauges
        scroll = Gtk.ScrolledWindow.new()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        
        # Container for gauges
        gauge_container = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 20)
        gauge_container.set_homogeneous(True)
        gauge_container.set_margin_start(10)
        gauge_container.set_margin_end(10)
        
        # Create gauges
        gauges = []
        labels = ["VRAM", "Usage", "Temp", "Clock", "Fan", "Power"]
        
        for label_text in labels:
            # Gauge box
            gauge_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            gauge_box.set_valign(Gtk.Align.CENTER)
            gauge_box.set_halign(Gtk.Align.CENTER)
            gauge_box.set_margin_start(10)
            gauge_box.set_margin_end(10)
            gauge_box.set_margin_top(10)
            gauge_box.set_margin_bottom(10)
            
            # Label
            label = Gtk.Label.new(label_text)
            label.add_css_class("title-3")
            label.set_margin_bottom(5)
            
            # Gauge
            gauge = CircularGauge(size=100)
            gauge.set_max_value(100.0)
            gauges.append(gauge)
            
            # Value label
            value_label = Gtk.Label.new("0%")
            value_label.add_css_class("body")
            value_label.set_margin_top(5)
            gauge.value_label = value_label  # Store reference for updates
            
            gauge_box.append(label)
            gauge_box.append(gauge)
            gauge_box.append(value_label)
            
            gauge_container.append(gauge_box)
        
        scroll.set_child(gauge_container)
        main_box.append(scroll)
        
        # Control buttons
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        
        # Auto update button
        auto_btn = Gtk.Button.new_with_label("Auto Increment")
        auto_btn.connect("clicked", self.on_auto_increment, gauges)
        button_box.append(auto_btn)
        
        # Reset button
        reset_btn = Gtk.Button.new_with_label("Reset")
        reset_btn.connect("clicked", self.on_reset, gauges)
        button_box.append(reset_btn)
        
        main_box.append(button_box)
        
        self.set_content(main_box)
        self.gauges = gauges
        self.auto_update_id = None
        
    def on_auto_increment(self, button, gauges):
        """Auto increment all gauges"""
        if self.auto_update_id:
            GLib.source_remove(self.auto_update_id)
            self.auto_update_id = None
            button.set_label("Auto Increment")
            return
        
        def update():
            for gauge in gauges:
                new_val = gauge.value + 5
                if new_val > gauge.max_value:
                    new_val = 0
                gauge.set_value(new_val)
                gauge.value_label.set_label(f"{int((gauge.value/gauge.max_value)*100)}%")
            return True
        
        self.auto_update_id = GLib.timeout_add(500, update)
        button.set_label("Stop Auto Increment")
    
    def on_reset(self, button, gauges):
        """Reset all gauges to 0"""
        for gauge in gauges:
            gauge.set_value(0)
            gauge.value_label.set_label("0%")
        if self.auto_update_id:
            GLib.source_remove(self.auto_update_id)
            self.auto_update_id = None


class TestApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="test.gauge.app")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app):
        window = GaugeTestWindow(self)
        window.present()


if __name__ == "__main__":
    app = TestApp()
    sys.exit(app.run(None))
