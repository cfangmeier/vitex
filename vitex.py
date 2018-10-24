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
        self.tex_file = realpath(texfile)
        self.pdf_file = splitext(self.tex_file)[0] + '.pdf'
        self.proj_dir = split(self.tex_file)[0]
        self.nvim = None
        self.connect("activate", self.on_activate)

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

        def do_exit(*args, **kwargs):
            self.quit()
        self.terminal.connect("child-exited", do_exit)
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
        doc = EvinceDocument.Document.factory_get_document('file://' + self.pdf_file)
        self.doc_view = EvinceView.View()
        self.doc_model = EvinceView.DocumentModel()
        self.doc_model.set_document(doc)
        self.doc_view.set_model(self.doc_model)
        scroll.add(self.doc_view)

    # def add_header(self, window):
    #     hb = Gtk.HeaderBar()
    #     hb.set_show_close_button(True)
    #     window.set_titlebar(hb)
    #
    #     button = Gtk.Button()
    #     icon = Gio.ThemedIcon(name="media-playback-start-symbolic.symbolic")
    #     image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
    #     button.add(image)
    #     button.connect("clicked", self.build)
    #     hb.pack_end(button)

    def attach_nvim(self):
        self.nvim = attach('socket', path='/tmp/vitex.sock')
        self.nvim.command('cd ' + self.proj_dir)
        self.nvim.command('edit ' + self.tex_file)

    # def build(self, _):
    #     f_dir, f_name = split(self.tex_file)
    #     f_basename = splitext(f_name)[0]
    #     proc = run(['latexmk', '-f', '-pdf', f_name], cwd=f_dir)
    #     pdf_name = join(f_dir, f_basename+'.pdf')
    #     if isfile(pdf_name):
    #         self.doc_model.get_document().load('file://'+pdf_name)
    #         self.doc_view.reload()

    def reload_pdf(self, m, f, o, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            f_dir, f_name = split(self.tex_file)
            f_basename = splitext(f_name)[0]
            pdf_name = join(f_dir, f_basename+'.pdf')
            if isfile(pdf_name):
                self.doc_model.get_document().load('file://'+pdf_name)
                self.doc_view.reload()

    def on_activate(self, data=None):
        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_title("Vitex")
        window.set_border_width(14)
        window.set_default_size(1400, 900)
        pane = Gtk.Paned()
        # self.add_header(window)
        self.add_editor_window(pane)
        self.add_pdf_viewer(pane)
        self.attach_nvim()

        # Setup pdf file monitor
        gfile = Gio.File.new_for_path(self.pdf_file)
        self.monitor = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
        self.monitor.connect("changed", self.reload_pdf)

        window.add(pane)
        window.show_all()
        self.add_window(window)
        pane.set_position(window.get_allocated_width() // 2)  # in pixels




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add = parser.add_argument
    add('texfile')
    args = parser.parse_args()
    app = VitexApp(args.texfile)
    app.run(None)

