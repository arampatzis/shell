" File              : .vimrc
" Author            : George Arampatzis <garampat@ethz.ch>
" Date              : 08.03.2021
" Last Modified Date: 24.11.2021
" Last Modified By  : George Arampatzis <garampat@ethz.ch>

let mapleader = " "

"----------------------------------------------------------------------------
" vim-plug plugin manager
" run :PlugInstall after adding a new plugin
"----------------------------------------------------------------------------
if empty(glob('~/.vim/autoload/plug.vim'))
  silent execute '!curl -fLo .vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')

Plug 'morhetz/gruvbox'

Plug 'junegunn/fzf.vim'
Plug 'junegunn/fzf'

Plug 'tomtom/tcomment_vim'

Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

Plug 'alpertuna/vim-header'

" Enhanced C and C++ syntax highlighting
Plug 'bfrg/vim-cpp-modern'

Plug 'craigemery/vim-autotag'

Plug 'SirVer/ultisnips'
Plug 'honza/vim-snippets'

Plug 'tpope/vim-fugitive'
Plug 'stsewd/fzf-checkout.vim'

Plug 'ycm-core/YouCompleteMe'

Plug 'vim-scripts/indentpython.vim'

call plug#end()

"----------------------------------------------------------------------------
" YouCompleteMe
let g:ycm_autoclose_preview_window_after_completion = 1

"----------------------------------------------------------------------------
" UltiSnip
" Trigger configuration. You need to change this to something other than <tab> if you use one of the following:
" - https://github.com/Valloric/YouCompleteMe
" - https://github.com/nvim-lua/completion-nvim
let g:UltiSnipsExpandTrigger="<C-l>"
let g:UltiSnipsJumpForwardTrigger="<C-j>"
let g:UltiSnipsJumpBackwardTrigger="<C-k>"

" If you want :UltiSnipsEdit to split your window.
let g:UltiSnipsEditSplit="vertical"

" let g:UltiSnipsSnippetDirectories=["UltiSnips", "my.snippets"]

"----------------------------------------------------------------------------
" gruvbox
set bg=dark 
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
nnoremap <silent> ;; :Buffers<CR>
let $FZF_DEFAULT_OPTS='--reverse'

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

" sets the behaviour of backspace to the expected
set backspace=indent,eol,start

filetype plugin indent on
syntax on
autocmd BufNewFile,BufRead *._cpp set filetype=cpp
autocmd BufNewFile,BufRead *.cpp.base set filetype=cpp
autocmd BufNewFile,BufRead *._hpp set filetype=cpp
autocmd BufNewFile,BufRead *.hpp.base set filetype=cpp
autocmd BufNewFile,BufRead *.config set filetype=json
autocmd BufRead,BufNewFile vifmrc set filetype=vim

augroup python
    autocmd!
    " Add shiftwidth and/or softtabstop if you want to override those too.
    autocmd FileType python setlocal expandtab tabstop=4 shiftwidth=4 softtabstop=4
augroup end

" Vim jumps to the last position when reopening a file
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

" continue comments on next line. and maybe more...
set formatoptions+=r

set grepprg=rg\ --vimgrep\ --smart-case\ --follow

" Two times Ctrl+N to set numbers On/Off
nmap <C-N><C-N> :set invnumber<CR>

nnoremap <leader>cd :cd %:p:h<CR>:pwd<CR>

set wildchar=<Tab> wildmenu wildmode=full

" left and right arrows change line
set whichwrap+=<,>,[,]

set mouse=a

set autowriteall

"----------------------------------------------------------------------------
" Highlight line and change cursor in insert mode
let &t_SI = "\<Esc>]50;CursorShape=1\x7"
let &t_EI = "\<Esc>]50;CursorShape=0\x7"
autocmd InsertEnter * set cul
autocmd InsertLeave * set nocul

"----------------------------------------------------------------------------
" Functions

function! CommentStart()
    let [L, R] = split(substitute(substitute(get(b:, 'commentary_format', &commentstring),'\S\zs%s',' %s','') ,'%s\ze\S', '%s ', ''), '%s', 1)
    return L
endfunction

function! CommentEnd()
    let [L, R] = split(substitute(substitute(get(b:, 'commentary_format', &commentstring),'\S\zs%s',' %s','') ,'%s\ze\S', '%s ', ''), '%s', 1)
    return R
endfunction
