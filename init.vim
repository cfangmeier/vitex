" nvimrc - Startup script for Neovim Editor
filetype off
set rtp+=/home/caleb/Sources/vitex/nvim_config/bundle/Vundle.vim

call vundle#begin('/home/caleb/Sources/vitex/nvim_config/bundle/')

Plugin 'gmarik/Vundle.vim'

Plugin 'airblade/vim-gitgutter'
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
" Plugin 'ntpeters/vim-airline-colornum'
Plugin 'tpope/vim-commentary'
Plugin 'tpope/vim-fugitive'

Plugin 'jeetsukumaran/vim-buffergator'

Plugin 'LaTeX-Box-Team/LaTeX-Box'

call vundle#end()

set list                                    " show whitespace
set hidden
set autowrite                               " Write automatically when switching buffers
set incsearch ignorecase smartcase hlsearch " Highlight search matches
set showmatch                               " Show matching paren/brace/bracket etc.
set showcmd                                 " Shows command as it is being typed
set wrap                                  " Disables auto-line wrapping
set number relativenumber                   " line numbering is relative to current line
set lazyredraw                              " limit the amount of screen redraws
set re=1                                    " force old regex engine
set inccommand=split                        " Enable live sub preview
set spr                                     " Make new splits open to the right

set shiftwidth=2                            " Default indent is two spaces
set tabstop=2
set softtabstop=2
set expandtab                               " By default replace tabs with spaces
set ts=2                                    " tab spacing is 2 characters

set mouse=a                                 " Enable all mouse features
set foldmethod=indent                       " Enable code folding
set foldlevel=99                            " Bigtime folding for great fun!
filetype plugin indent on                   " Enable file-specific plugins and indents
syntax on                                   " Set syntax highlighting on
set termguicolors                           " Enable true color support in terminal
set guicursor=n-v-c:block,i-ci-ve:ver25,r-cr:hor20,o:hor50
 \,a:blinkwait700-blinkoff400-blinkon250-Cursor/lCursor
 \,sm:block-blinkwait175-blinkoff150-blinkon175

colorscheme darktooth

let g:netrw_liststyle = 3  " start in tree-style listing
let g:netrw_preview   = 1  " open preview in vertical split
let g:netrw_winsize   = 30 " dir listing uses only 30% of screen width

"" Setup persistent undo
set undofile
set undodir=$HOME/.config/nvim/undo
set undolevels=500
set undoreload=500

"" Setup backup. Put backup in specialized directory
set backupdir=$HOME/.config/nvim/backup " for backup files
set directory=$HOME/.config/nvim/backup " for .swp files

let g:python3_host_prog='/usr/bin/python'

"" Airline setup
set laststatus=2
let g:airline_powerline_fonts = 0
let g:airline_theme='distinguished'
let g:airline_inactive_collapse=1
let g:airline_mode_map = {
        \ '__' : '-',
        \ 'n'  : 'N',
        \ 'i'  : 'I',
        \ 'R'  : 'R',
        \ 'c'  : 'C',
        \ 'v'  : 'V',
        \ 'V'  : 'V',
        \ '' : 'V',
        \ 's'  : 'S',
        \ 'S'  : 'S',
        \ '' : 'S',
        \ }

"" LaTeX Box Setup
let g:LatexBox_latexmk_async=1
let g:LatexBox_autojump=1
let g:LatexBox_quickfix=4
let g:LatexBox_latexmk_options="-pdf"

"" alt key view switching
tnoremap <A-h> <C-\><C-n><C-w>h
tnoremap <A-j> <C-\><C-n><C-w>j
tnoremap <A-k> <C-\><C-n><C-w>k
tnoremap <A-l> <C-\><C-n><C-w>l
nnoremap <A-h> <C-w>h
nnoremap <A-j> <C-w>j
nnoremap <A-k> <C-w>k
nnoremap <A-l> <C-w>l
inoremap <A-h> <esc><C-w>h
inoremap <A-j> <esc><C-w>j
inoremap <A-k> <esc><C-w>k
inoremap <A-l> <esc><C-w>l

"" Set a visable cursor line in current buffer
augroup CursorLine
  au!
  au VimEnter,WinEnter,BufWinEnter * setlocal cursorline
  au WinLeave * setlocal nocursorline
augroup END


"" Custom Mappings
nnoremap <silent> Q @q
noremap <silent> <BS> :noh<CR>

nnoremap <silent> <leader>n :bn<CR>
nnoremap <silent> <leader>p :bp<CR>

"" Buffergator
let g:buffergator_viewport_split_policy = "B"

" Following actually maps <C-/> to gcc/gc
nmap <C-_> gcc
vmap <C-_> gc

