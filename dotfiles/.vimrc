" File              : .vimrc
" Author            : George Arampatzis <garampat@ethz.ch>
" Date              : 08.03.2021
" Last Modified Date: 12.03.2021
" Last Modified By  : George Arampatzis <garampat@ethz.ch>
"----------------------------------------------------------------------------
" vim-plug plugin manager
" run :PlugInstall after adding a new plugin
"----------------------------------------------------------------------------

" Plugins will be downloaded under the specified directory.
call plug#begin('~/.vim/plugged')

" Declare the list of plugins.

Plug 'morhetz/gruvbox'

Plug 'junegunn/fzf.vim'
Plug 'junegunn/fzf'

Plug 'tomtom/tcomment_vim'

Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

Plug 'preservim/nerdtree' | Plug 'Xuyuanp/nerdtree-git-plugin'

Plug 'alpertuna/vim-header'

Plug 'bfrg/vim-cpp-modern'

Plug 'craigemery/vim-autotag'

" List ends here. Plugins become visible to Vim after this call.
call plug#end()

if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif


"----------------------------------------------------------------------------
let mapleader = " "

"----------------------------------------------------------------------------
" NERDTree
nnoremap <leader>n :NERDTreeFocus<CR>

"----------------------------------------------------------------------------
" gruvbox
let g:gruvbox_contrast_dark = 'hard'  " hard, medium, soft
autocmd vimenter * colorscheme gruvbox

"----------------------------------------------------------------------------
" airline
" Enable the list of buffers
let g:airline#extensions#tabline#enabled = 1

" Show just the filename
let g:airline#extensions#tabline#fnamemod = ':t'

"----------------------------------------------------------------------------
" fzf
" https://bluz71.github.io/2018/12/04/fuzzy-finding-in-vim-with-fzf.html
nnoremap <silent> <Leader><Space> :Files<CR>
nnoremap <silent> <Leader>. :Files <C-r>=expand("%:h")<CR>/<CR>
nnoremap <silent> bb :Buffers<CR>

"----------------------------------------------------------------------------
" vim header
let g:header_field_author = 'George Arampatzis'
let g:header_field_author_email = 'garampat@ethz.ch'
let g:header_auto_add_header = 0
let g:header_field_timestamp_format = '%d.%m.%Y'
nmap <C-c> :AddHeader<CR>

"----------------------------------------------------------------------------
" automatic ctags
let g:autotagStartMethod='fork'
let g:autotagTagsFile=".tags"

"----------------------------------------------------------------------------
" Set the working directory to the current file
set autochdir
"autocmd BufEnter * silent! lcd %:p:h


filetype plugin indent on
syntax on
autocmd BufNewFile,BufRead *._cpp set syntax=cpp
autocmd BufNewFile,BufRead *._hpp set syntax=cpp
autocmd BufNewFile,BufRead *.config set syntax=json
autocmd BufRead,BufNewFile vifmrc setfiletype vim

augroup python
    autocmd!
    " Add shiftwidth and/or softtabstop if you want to override those too.
    autocmd FileType python setlocal expandtab tabstop=2 shiftwidth=2 softtabstop=2
augroup end

" Uncomment the following to have Vim jump to the last position when                                                       
" reopening a file
if has("autocmd")
  au BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$")
    \| exe "normal! g'\"" | endif
endif

set expandtab tabstop=2 shiftwidth=2 softtabstop=2

set hlsearch

set number

set tags=.tags

if $TERM_PROGRAM =~ "iTerm"
    let &t_SI = "\<Esc>]50;CursorShape=1\x7" " Vertical bar in insert mode
    let &t_EI = "\<Esc>]50;CursorShape=0\x7" " Block in normal mode
endif

set ruler

set grepprg=rg\ --vimgrep\ --smart-case\ --follow

" Two times Ctrl+N to set numbers On/Off
nmap <C-N><C-N> :set invnumber<CR>

nnoremap <leader>cd :cd %:p:h<CR>:pwd<CR>

set wildchar=<Tab> wildmenu wildmode=full

