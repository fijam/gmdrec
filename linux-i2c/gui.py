import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gmdrec import GMDRec_Rev2, find_i2c_dev

i2c_dev = find_i2c_dev()
assert i2c_dev is not None

gmdrec = GMDRec_Rev2(i2c_dev)

def on_button_pressed(button):
    gmdrec.button_down(button.props.label)

def on_button_released(button):
    gmdrec.button_up(button.props.label)

window = Gtk.Window(title='GMDRec Linux I2C Remote Button Tester')
window.set_default_size(200, -1)
vbox = Gtk.VBox()
vbox.props.spacing = 6
vbox.props.border_width = 12
for label in sorted(gmdrec.wiper_values.keys()):
    button = Gtk.Button(label=label)
    button.connect('pressed', on_button_pressed)
    button.connect('released', on_button_released)
    vbox.add(button)
window.add(vbox)
window.show_all()
window.connect('destroy', Gtk.main_quit)
Gtk.main()
