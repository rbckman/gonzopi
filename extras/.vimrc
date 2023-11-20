" File ~/.vim/ftplugin/html.vim

set cursorline
set encoding=utf-8
set fileencoding=utf-8
set mouse=a
set showcmd
syntax enable
filetype indent on
set nobackup
set number	
set ruler
set undolevels=1000	
set backspace=indent,eol,start 
set tabstop=8
set expandtab
set softtabstop=4
set shiftwidth=4
set nobackup
set nowb
set noswapfile
set linebreak
colorscheme desert
set background=dark
nnoremap j gj
nnoremap k gk
vnoremap j gj
vnoremap k gk
nnoremap <Down> gj
nnoremap <Up> gk
vnoremap <Down> gj
vnoremap <Up> gk
inoremap <Down> <C-o>gj
inoremap <Up> <C-o>gk
