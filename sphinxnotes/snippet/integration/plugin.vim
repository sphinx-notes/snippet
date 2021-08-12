" NeoVim integration for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-01
" :Version: 20210413
"
" NOTE: junegunn/fzf.vim is required

let s:snippet = 'snippet'

function! s:SplitID(row)
  return split(a:row, ' ')[0]
endfunction

function! g:SphinxNotesSnippetList(callback, kinds)
  let cmd = [s:snippet, 'list',
        \ '--kinds', a:kinds,
        \ '--width', &columns - 2,
        \ ]
  call fzf#run({
        \ 'source': join(cmd, ' '),
        \ 'sink': a:callback,
        \ 'options': ['--with-nth', '2..', '--no-hscroll', '--header-lines', '1'],
        \ })
endfunction

function! g:SphinxNotesSnippetListAndView()
  function! s:CallView(selection)
    call g:SphinxNotesSnippetView(s:SplitID(a:selection))
  endfunction
  call g:SphinxNotesSnippetList(function('s:CallView'), 'ds')
endfunction

" https://github.com/anhmv/vim-float-window/blob/master/plugin/float-window.vim
function! g:SphinxNotesSnippetView(id)
  let height = float2nr((&lines - 2) / 1.5)
  let row = float2nr((&lines - height) / 2)
  let width = float2nr(&columns / 1.5)
  let col = float2nr((&columns - width) / 2)

  " Main Window
  let opts = {
    \ 'relative': 'editor',
    \ 'style': 'minimal',
    \ 'width': width,
    \ 'height': height,
    \ 'col': col,
    \ 'row': row,
    \ }

  let buf = nvim_create_buf(v:false, v:true)
  " Global for :call
  let g:sphinx_notes_snippet_win = nvim_open_win(buf, v:true, opts)

  " The content is always reStructuredText for now
  set filetype=rst
  " Press enter to return
  nmap <buffer> <CR> :call nvim_win_close(g:sphinx_notes_snippet_win, v:true)<CR>

  let cmd = [s:snippet, 'get', '--text', a:id]
  execute '$read !' . join(cmd, ' ')
  execute '$read !' . '..'
  call append(line('$'), [
        \ '.. Inserted By sphinxnotes-snippet:',
        \ '',
        \ '     Press <ENTER> to return'])
endfunction

function! g:SphinxNotesSnippetEdit(id)
  let cmd = [s:snippet, 'get', '--file', a:id]
  execute '$tabedit ' . system(join(cmd, ' '))
endfunction

function! g:SphinxNotesSnippetListAndEdit()
  function! s:CallEdit(selection)
    call g:SphinxNotesSnippetEdit(s:SplitID(a:selection))
  endfunction
  call g:SphinxNotesSnippetList(function('s:CallEdit'), 'ds')
endfunction

function! g:SphinxNotesSnippetUrl(id)
  let cmd = [s:snippet, 'get', '--url', a:id]
  for url in systemlist(join(cmd, ' '))
    echo system('xdg-open ' . shellescape(url))
  endfor
endfunction

function! g:SphinxNotesSnippetListAndUrl()
  function! s:CallUrl(selection)
    call g:SphinxNotesSnippetUrl(s:SplitID(a:selection))
  endfunction
  call g:SphinxNotesSnippetList(function('s:CallUrl'), 'ds')
endfunction

" vim: set shiftwidth=2:
