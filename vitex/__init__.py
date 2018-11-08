#!/usr/bin/env python

from os import environ, remove, makedirs
from os.path import splitext, realpath, split, isfile, join, expanduser
from subprocess import run
import argparse
from neovim import attach

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
gi.require_version('EvinceDocument', '3.0')
gi.require_version('EvinceView', '3.0')
from gi.repository import (Gtk, Gdk, GObject, Gio, GLib, Vte,
                           EvinceDocument, EvinceView)

__version__ = '0.2.1'
SOCKET = '/tmp/vitex.sock'
INSTALLDIR = join(expanduser('~'), '.local/vitex/')


class VitexApp(Gtk.Application):
    def __init__(self, texfile):
        Gtk.Application.__init__(self, application_id="apps.vitex", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.tex_file = realpath(expanduser(texfile))
        self.pdf_file = splitext(self.tex_file)[0] + '.pdf'
        self.proj_dir = split(self.tex_file)[0]
        self.doc_loaded = False
        self.connect("activate", self.on_activate)

    def add_editor_window(self):
        self.terminal = Vte.Terminal()
        self.terminal.set_color_background(Gdk.RGBA(0, 43/256, 54/256, 1))
        try:
            remove(SOCKET)
        except FileNotFoundError:
            pass
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            environ['HOME'],
            ["/usr/bin/nvim", "-u", join(INSTALLDIR, "init.vim"), "--listen", SOCKET],
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
        self.pane.pack1(box)

    def add_pdf_viewer(self):
        self.scroll = Gtk.ScrolledWindow()
        self.pane.pack2(self.scroll)
        EvinceDocument.init()
        self.doc_view = EvinceView.View()
        self.doc_view.connect('button-press-event', self.synctex)
        self.doc_model = EvinceView.DocumentModel()
        self.doc_view.set_model(self.doc_model)
        self.load_pdf()
        self.scroll.add(self.doc_view)

        # now for eqn previewer
        self.prev_scroll = Gtk.ScrolledWindow()
        self.prev_view = EvinceView.View()
        self.prev_scroll.add(self.prev_view)
        # self.doc_view.connect('button-press-event', self.synctex)
        self.prev_model = EvinceView.DocumentModel()
        self.prev_view.set_model(self.prev_model)

    def attach_nvim(self):
        self.nvim = attach('socket', path=SOCKET)
        self.nvim.command('cd ' + self.proj_dir)
        self.nvim.command('edit ' + self.tex_file)

    def load_pdf(self):
        if isfile(self.pdf_file):
            if self.doc_loaded:
                self.doc_model.get_document().load('file://'+self.pdf_file)
                self.doc_view.reload()
            else:
                self.doc = EvinceDocument.Document.factory_get_document('file://' + self.pdf_file)
                self.doc_model.set_document(self.doc)
                self.doc_loaded = True

    def reload_pdf(self, m, f, o, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            self.load_pdf()

    def synctex(self, obj, event):
        click_x = event.x + self.scroll.get_hscrollbar().get_value()
        click_y = event.y + self.scroll.get_vscrollbar().get_value()
        for idx in range(self.doc.get_n_pages()):
            page_rect = Gdk.Rectangle()
            page_border = Gtk.Border()
            self.doc_view.get_page_extents(idx, page_rect, page_border)
            if (page_rect.x < click_x < (page_rect.x + page_rect.width) and
                    page_rect.y < click_y < (page_rect.y + page_rect.height)):
                page_size = self.doc.get_page_size(idx)
                page_x = (page_size.width / page_rect.width) * (click_x - page_rect.x)
                page_y = (page_size.height / page_rect.height) * (click_y - page_rect.y)
                page_idx = idx
                break
        else:  # clicked outside page
            return

        # print(f'clicked on page {page_idx} at page coordinates {page_x}, {page_y}')

        result = self.doc.synctex_backward_search(page_idx, page_x, page_y)
        if result is not None:
            filename = realpath(result.filename)
            if not isfile(filename): return
            self.nvim.command(f'edit {filename}')
            self.nvim.command(f'{result.line}')

    def increment_text_size(self, increment):
        current_scale = self.terminal.get_font_scale()
        if increment > 0:
            self.terminal.set_font_scale(current_scale + 0.1)
        else:
            self.terminal.set_font_scale(current_scale - 0.1)

    def preview_equation(self):
        # First send a literal escape to exit visual mode and populate the marks
        self.nvim.feedkeys(bytes([27]))
        vmode = self.nvim.funcs.visualmode()
        if vmode == "V":  # Visual line mode
            start_l, _ = self.nvim.current.buffer.mark('<')
            end_l, _ = self.nvim.current.buffer.mark('>')
            eqn = '\n'.join(self.nvim.current.buffer[start_l-1:end_l])
        else:
            return  # not implemented
        text = '\n'.join([
            r'\documentclass{standalone}',
            r'\begin{document}',
            r'$\displaystyle',
            eqn,
            r'$',
            r'\end{document}'
        ])
        if not self.eqn_ed_pane.get_reveal_child():
            with open('/tmp/vitex_preview.tex', 'w') as f:
                f.write(text)
            run(['pdflatex', '/tmp/vitex_preview.tex'], cwd='/tmp')
            if isfile('/tmp/vitex_preview.pdf'):
                prev = EvinceDocument.Document.factory_get_document('file://' + '/tmp/vitex_preview.pdf')
                self.prev_model.set_document(prev)
            self.eqn_ed_pane.set_reveal_child(True)
        else:
            self.eqn_ed_pane.set_reveal_child(False)

    def on_key_press(self, obj, event):
        is_ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        # is_alt = bool(event.state & Gdk.ModifierType.MOD1_MASK)

        if is_ctrl and event.keyval == 45:  # '-'
            self.increment_text_size(-1)
        elif is_ctrl and event.keyval == 61:  # '+'
            self.increment_text_size(+1)
        elif is_ctrl and event.keyval == 65363:  # right arrow
            self.pane.set_position(self.pane.get_position() + 50)  # in pixels
        elif is_ctrl and event.keyval == 65361:  # left arrow
            self.pane.set_position(self.pane.get_position() - 50)  # in pixels
        elif is_ctrl and event.keyval == 65362:  # up arrow
            self.pane.set_position(self.window.get_allocated_width() // 2)  # in pixels
        elif is_ctrl and event.keyval == 98:  # 'b'
            self.nvim.command('Latexmk', async_=True)  # async_ here to avoid hanging UI
            # self.doc_view.set_loading(True)  # seems to do nothing...
        elif is_ctrl and event.keyval == 101:  # 'e'
            print('display equation editor')
            self.preview_equation()
            # self.launch_equation_editor()
        else:
            return False
        return True

    def on_activate(self, data=None):
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Vitex - (" + self.tex_file + ")")
        self.window.set_border_width(0)
        self.window.set_default_size(1400, 900)
        self.pane = Gtk.Paned()
        self.add_editor_window()
        self.add_pdf_viewer()
        self.attach_nvim()

        # Setup pdf file monitor
        gfile = Gio.File.new_for_path(self.pdf_file)
        self.monitor = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
        self.monitor.connect("changed", self.reload_pdf)

        overlay = Gtk.Overlay()
        # stack.
        self.window.connect('key-press-event', self.on_key_press)

        overlay.add(self.pane)

        self.eqn_ed_pane = Gtk.Revealer()
        self.eqn_ed_pane.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.eqn_ed_pane.transition_duration = 400
        # eqn_prev = Gtk.Image()
        # eqn_prev.set_from_file("/home/caleb/Sources/vitex/vitex.png")
        # self.eqn_ed_pane.add(Gtk.Label("Hello World"))
        self.eqn_ed_pane.add(self.prev_scroll)
        overlay.add_overlay(self.eqn_ed_pane)

        # self.about_dialog = Gtk.AboutDialog()
        # self.about_dialog.add_credit_section('makers', ['me', 'you', 'abu'])
        # self.about_dialog.set_program_name('ViTeX')
        self.window.add(overlay)
        self.add_window(self.window)
        self.window.show_all()
        self.pane.set_position(self.window.get_allocated_width() // 2)  # in pixels


def first_time_setup():

    def make_conf_dir(path):
        makedirs(join(INSTALLDIR, path), exist_ok=True)

    print('performing first time setup')
    pkgdir = split(realpath(__file__))[0]
    with open(join(pkgdir, 'init.vim.template'), 'r') as f:
        text = f.read()
    text = text.replace('___INSTALLDIR___', INSTALLDIR)
    make_conf_dir('')
    with open(join(INSTALLDIR, 'init.vim'), 'w') as f:
        f.write(text)
    make_conf_dir('backup')
    make_conf_dir('swap')
    make_conf_dir('undo')
    print('Installing Vundle')
    make_conf_dir('nvim/bundle')
    run(['git', 'clone', 'https://github.com/VundleVim/Vundle.vim.git', join(INSTALLDIR, 'nvim/bundle/Vundle.vim')])
    print('Installing additional plugins')
    run(['nvim', '-u', join(INSTALLDIR, 'init.vim'), '-Es', '+PluginInstall', '+qall'])
    print('done')
    print('The neovim configuration file for vitex is installed in:')
    print(join(INSTALLDIR, 'init.vim'))
    print('Please feel free to customize it as you see fit')


def vitex(args):
    if not isfile(join(INSTALLDIR, 'init.vim')):
        first_time_setup()
    app = VitexApp(args.texfile)
    print("starting ViTeX")
    app.run(None)
