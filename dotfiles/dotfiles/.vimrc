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

Plug 'junegunn/fzf'
Plug 'junegunn/fzf.vim'
Plug 'stsewd/fzf-checkout.vim'

Plug 'tomtom/tcomment_vim'

Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

Plug 'alpertuna/vim-header'

Plug 'SirVer/ultisnips'
Plug 'honza/vim-snippets'

Plug 'Vimjas/vim-python-pep8-indent'

Plug 'dense-analysis/ale'

Plug 'ntpeters/vim-better-whitespace'

Plug 'preservim/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'

" Find and replace plugins
Plug 'kqito/vim-easy-replace'
Plug 'brooth/far.vim'

Plug 'pechorin/any-jump.vim'

Plug 'ervandew/supertab'

Plug 'cespare/vim-toml'

call plug#end()

if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" ----------------------------------------------------------------------------
"  any-jump
function! Preserve(command)
    " preparation: save last search, and cursor position.
    let _s=@/
    let l = line(".")
    let c = col(".")
    " do the business:
    execute a:command
    " clean up: restore previous search history, and cursor position
    let @/=_s
    call cursor(l, c)
endfunction

let g:any_jump_disable_default_keybindings = 1
let g:any_jump_list_numbers = 1

nnoremap <leader>j :call Preserve("AnyJump")<CR>
xnoremap <leader>j :call Preserve("AnyJump")<CR>

nnoremap <leader>b :AnyJumpBack<CR>
xnoremap <leader>b :AnyJumpBack<CR>

" ----------------------------------------------------------------------------
" far.vim
let g:far#enable_undo=1

" ----------------------------------------------------------------------------
" nerdtree
nnoremap <leader>n :NERDTreeFocus<CR>
let NERDTreeMinimalUI = 1
let NERDTreeDirArrows = 1
let NERDTreeMinimalUI = 1
" close nerdtree if last
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() | quit | endif

set wildignore+=*.pyc,*.swp,*.DS_Store,*.egg-info,__pycache__

let NERDTreeRespectWildIgnore=1

" do not exit vim when delete a buffer
" https://stackoverflow.com/a/16505009/9690756
noremap <leader>q :bp<cr>:bd #<cr>

" ----------------------------------------------------------------------------
" ale
let g:ale_python_pylint_change_directory = 1
let g:ale_linters={
\ 'python': ['pylint'],
\}

" ----------------------------------------------------------------------------
" vim-better-whitespace
" clean whitespaces on save
let g:better_whitespace_enabled=1
let g:strip_whitespace_on_save=1
let g:strip_whitespace_confirm=0

"----------------------------------------------------------------------------
" UltiSnip
let g:UltiSnipsExpandTrigger = "<tab>"
let g:UltiSnipsJumpForwardTrigger = "<tab>"
let g:UltiSnipsJumpBackwardTrigger = "<s-tab>"

" If you want :UltiSnipsEdit to split your window.
let g:UltiSnipsEditSplit="vertical"

let g:UltiSnipsSnippetDirectories=["UltiSnips", "my_snippets"]

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
" automatic ctags
let g:autotagStartMethod='fork'
let g:autotagTagsFile="tags"

"----------------------------------------------------------------------------
" Set the working directory to the current file
" set autochdir

" sets the behaviour of backspace to the expected
set backspace=indent,eol,start

filetype plugin on
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

set expandtab tabstop=4 shiftwidth=4 softtabstop=4

set hlsearch

set number

set tags=tags

set ruler

" continue comments on next line. and maybe more...
set formatoptions+=r

set grepprg=rg\ --vimgrep\ --smart-case\ --follow

" Two times Ctrl+N to set numbers On/Off
nmap <C-N><C-N> :set invnumber<CR>

" Set working directory to the current file
nnoremap <leader>cd :cd %:p:h<CR>:pwd<CR>

set wildchar=<Tab> wildmenu wildmode=full

" left and right arrows change line
set whichwrap+=<,>,[,]

set mouse=a

set autowriteall

set colorcolumn=88

" the buffer of a file will only be hidden when you switch to the new file, not closed
" set hidden

"----------------------------------------------------------------------------
" Highlight line and change cursor in insert mode
set cursorline

if exists('$TMUX')
    let &t_SI = "\<Esc>Ptmux;\<Esc>\e[5 q\<Esc>\\"
    let &t_EI = "\<Esc>Ptmux;\<Esc>\e[2 q\<Esc>\\"
else
    let &t_SI = "\<Esc>]50;CursorShape=1\x7"
    let &t_EI = "\<Esc>]50;CursorShape=0\x7"
endif

"----------------------------------------------------------------------------
" Set all tabs from 2 to 4 spaces
command FixTabs set ts=2 sts=2 noet | retab! | set ts=4 sts=4 et | retab!

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
