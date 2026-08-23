import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject, GLib
import sys

class DataObject(GObject.GObject):
    def __init__(self, text):
        super().__init__()
        self.text = text

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    
    store = Gio.ListStore(item_type=DataObject)
    store.append(DataObject("Hello World 1"))
    store.append(DataObject("Hello World 2"))
    
    sel = Gtk.SingleSelection(model=store)
    
    cv = Gtk.ColumnView(model=sel)
    
    factory = Gtk.SignalListItemFactory()
    
    def setup(fact, item):
        label = Gtk.Label()
        label.set_selectable(True)
        item.set_child(label)
        # item.set_selectable(False) # Uncomment to test
        # item.set_activatable(False)
        
    def bind(fact, item):
        obj = item.get_item()
        label = item.get_child()
        label.set_label(obj.text)
        
    factory.connect("setup", setup)
    factory.connect("bind", bind)
    
    col = Gtk.ColumnViewColumn(title="Text", factory=factory)
    cv.append_column(col)
    
    win.set_child(cv)
    win.present()

app = Gtk.Application(application_id='org.gtk.Example')
app.connect('activate', on_activate)
# Run for a second and exit
GLib.timeout_add_seconds(2, lambda: app.quit())
app.run(sys.argv)
