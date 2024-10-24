" Vim key binding for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-12
" :Version: 20211114
"

function g:SphinxNotesSnippetEdit(id)
  let file = g:SphinxNotesSnippetGet(a:id, 'file')[0]
  let line = g:SphinxNotesSnippetGet(a:id, 'line-start')[0]
  if &modified
    execute 'vsplit ' . file
  else
    execute 'edit ' . file
  endif
  execute line
endfunction

function g:SphinxNotesSnippetListAndEdit()
  function! ListAndEdit_CB(id)
    call g:SphinxNotesSnippetEdit(a:id)
  endfunction
  call g:SphinxNotesSnippetList('ds', function('ListAndEdit_CB'))
endfunction

function g:SphinxNotesSnippetUrl(id)
  let url_list = g:SphinxNotesSnippetGet(a:id, 'url')
  for url in url_list
    echo system('xdg-open ' . shellescape(url))
  endfor
endfunction

function g:SphinxNotesSnippetListAndUrl()
  function! ListAndUrl_CB(id)
    call g:SphinxNotesSnippetUrl(a:id)
  endfunction
  call g:SphinxNotesSnippetList('ds', function('ListAndUrl_CB'))
endfunction

nmap <C-k>e :call g:SphinxNotesSnippetListAndEdit()<CR>
nmap <C-k>u :call g:SphinxNotesSnippetListAndUrl()<CR>
nmap <C-k>i :call g:SphinxNotesSnippetListAndInput()<CR>

" vim: set shiftwidth=2:
