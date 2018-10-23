#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
gi.require_version('EvinceDocument', '3.0')
gi.require_version('EvinceView', '3.0')

from gi.repository import (Gtk, GObject, Gio, GLib, Vte,
                           EvinceDocument, EvinceView)


class VitexApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="apps.vitex", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def add_editor_window(self, pane):
        self.terminal = Vte.Terminal()
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ["/usr/bin/nvim"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        scroller = Gtk.ScrolledWindow()
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        scroller.add(self.terminal)
        box.pack_start(scroller, False, True, 2)
        pane.pack1(box)

    def add_pdf_viewer(self, pane):
        scroll = Gtk.ScrolledWindow()
        pane.pack2(scroll)
        EvinceDocument.init()
        doc = EvinceDocument.Document.factory_get_document('file:///home/caleb/AN-18-062_latest.pdf')
        view = EvinceView.View()
        model = EvinceView.DocumentModel()
        model.set_document(doc)
        view.set_model(model)
        scroll.add(view)

    def on_activate(self, data=None):
        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_title("Vitex")
        window.set_border_width(14)
        # window.set_default_size(600, 300)
        pane = Gtk.Paned()
        self.add_editor_window(pane)
        self.add_pdf_viewer(pane)
        window.add(pane)
        window.show_all()
        self.add_window(window)


if __name__ == "__main__":
    app = VitexApp()
    app.run(None)

