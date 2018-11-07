![ViTeX](https://raw.githubusercontent.com/cfangmeier/vitex/master/vitex.png)

> An unholy conglomeration of vim, evince, and friends for writing LaTeX

![This is what it looks like!](https://github.com/cfangmeier/vitex/raw/master/screenshot.png)

## Goal

Do you prefer to use vim to edit your LaTeX files, but wish there was better integration between the editor and your pdf viewer? Well this is the project for you! The goal of ViTeX is to bring together high quality tools in a convenient package to make editing LaTeX as painless(tm) as possible.

## Status

Currently working on arch linux with the Gnome desktop environment.

## Features!

  - **Real** neovim via Vte
  - Custom `init.vim` for editing LaTeX (of course feel free to personalize)
  - Embedded PDF view using Evince with auto reload
  - Synctex support
  - That's pretty much it!

## Requirements

This is likely a non-exhaustive list, so please feel free to create an issue if you found you needed something else.

  - Python 3
  - Gtk+
  - Evince
  - neovim
  
 ## Controls
   - `ctrl -`: Decrease editor font size
   - `ctrl +`: Increase editor font size
   - `ctrl b`: Start async build with latexmk
   - `ctrl right`: move divider to right
   - `ctrl left`: move divider to left
   - `ctrl up`: move divider to center

## Setup
```sh
git clone git@github.com:cfangmeier/vitex.git
cd vitex
. ./setup.sh  # Creates a python virtualenv and clones Vundle.vim
./vitex path-to-your-sourcefile.tex  # first time setup creates init.vim and installs other vim plugins
```
