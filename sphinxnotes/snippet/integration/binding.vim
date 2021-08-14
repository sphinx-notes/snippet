" NeoVim key binding for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-12
" :Version: 20210814
"
function! g:SphinxNotesSnippetEdit(id)
  let file = system(join([s:snippet, 'get', '--file', a:id], ' '))
  let line = system(join([s:snippet, 'get', '--line-start', a:id], ' '))
  execute 'tabedit ' . file
  execute line
endfunction

function! g:SphinxNotesSnippetListAndEdit()
  function! s:CallEdit(selection)
    call g:SphinxNotesSnippetEdit(s:SplitID(a:selection))
  endfunction
  call g:SphinxNotesSnippetList(function('s:CallEdit'), 'ds')
endfunction

function! g:SphinxNotesSnippetUrl(id)
  let url_list = systemlist(join([s:snippet, 'get', '--url', a:id], ' '))
  for url in url_list
    echo system('xdg-open ' . shellescape(url))
  endfor
endfunction

function! g:SphinxNotesSnippetListAndUrl()
  function! s:CallUrl(selection)
    call g:SphinxNotesSnippetUrl(s:SplitID(a:selection))
  endfunction
  call g:SphinxNotesSnippetList(function('s:CallUrl'), 'ds')
endfunction

nmap <C-k>e :call g:SphinxNotesSnippetListAndEdit()<CR>
nmap <C-k>u :call g:SphinxNotesSnippetListAndUrl()<CR>

" vim: set shiftwidth=2:
