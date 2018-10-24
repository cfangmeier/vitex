#!/usr/bin/env python
#-*- coding:utf-8 -*-

from os import environ, getcwd
from os.path import join, splitext, realpath, split, isfile
from subprocess import run
import argparse
from neovim import attach
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
gi.require_version('EvinceDocument', '3.0')
gi.require_version('EvinceView', '3.0')

from gi.repository import (Gtk, GObject, Gio, GLib, Vte,
                           EvinceDocument, EvinceView)


class VitexApp(Gtk.Application):
    def __init__(self, texfile):
        Gtk.Application.__init__(self, application_id="apps.vitex", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.texfile = realpath(texfile)
        self.nvim = None
        self.connect("activate", self.on_activate)
        # self.my_accelerators = Gtk.AccelGroup()

    def add_editor_window(self, pane):
        self.terminal = Vte.Terminal()
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            environ['HOME'],
            ["/usr/bin/nvim", "-u", realpath("init.vim"), "--listen", "/tmp/vitex.sock"],
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
        pdffile = splitext(self.texfile)[0] + '.pdf'
        doc = EvinceDocument.Document.factory_get_document('file://'+pdffile)
        self.doc_view = EvinceView.View()
        self.doc_model = EvinceView.DocumentModel()
        self.doc_model.set_document(doc)
        self.doc_view.set_model(self.doc_model)
        scroll.add(self.doc_view)

    def add_header(self, window):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        # hb.props.title = "HeaderBar example"
        window.set_titlebar(hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="media-playback-start-symbolic.symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.build)
        hb.pack_end(button)


        # box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Gtk.StyleContext.add_class(box.get_style_context(), "linked")
        #
        # button = Gtk.Button()
        # button.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        # box.add(button)
        #
        # button = Gtk.Button()
        # button.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        # box.add(button)
        #
        # hb.pack_start(box)

        # self.add(Gtk.TextView())

    def attach_nvim(self):
        self.nvim = attach('socket', path='/tmp/vitex.sock')
        self.nvim.command('cd ' + getcwd())
        self.nvim.command('edit ' + self.texfile)

    def build(self, _):
        f_dir, f_name = split(self.texfile)
        f_basename = splitext(f_name)[0]
        # proc = run(['rubber', f_basename], cwd=f_dir)
        proc = run(['latexmk', '-f', '-pdf', f_name], cwd=f_dir)
        pdf_name = join(f_dir, f_basename+'.pdf')
        if isfile(pdf_name):
            self.doc_model.get_document().load('file://'+pdf_name)
            self.doc_view.reload()

    # def add_accelerator(self, widget, accelerator, signal="activate"):
    #     """Adds a keyboard shortcut"""
    #     key, mod = Gtk.accelerator_parse(accelerator)
    #     widget.add_accelerator(signal, self.my_accelerators, key, mod, Gtk.AccelFlags.VISIBLE)

    @staticmethod
    def hello():
        print("hello world")

    def on_activate(self, data=None):
        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_title("Vitex")
        window.set_border_width(14)
        window.set_default_size(600, 600)
        pane = Gtk.Paned()
        self.add_header(window)
        self.add_editor_window(pane)
        self.add_pdf_viewer(pane)
        self.attach_nvim()

        # GObject.signal_new('do_build', window,
        #                    GObject.SignalFlags.RUN_LAST,
        #                    GObject.TYPE_NONE,
        #                    (),
        #                    )
        # window.connect('do_build', self.hello)
        # self.add_accelerator(window, "<Control>b", signal='do_build')

        pane.set_position(300)  # in pixels
        window.add(pane)
        window.show_all()
        self.add_window(window)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add = parser.add_argument
    add('texfile')
    args = parser.parse_args()
    app = VitexApp(args.texfile)
    app.run(None)

