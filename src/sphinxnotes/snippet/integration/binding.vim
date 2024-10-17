" Vim key binding for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-12
" :Version: 20211114
"

function! g:SphinxNotesSnippetEdit(id)
  let file = system(join([s:snippet, 'get', '--file', a:id, '2>/dev/null'], ' '))
  let line = system(join([s:snippet, 'get', '--line-start', a:id, '2>/dev/null'], ' '))
  if &modified
    execute 'vsplit ' . file
  else
    execute 'edit ' . file
  endif
  execute line
endfunction

function! g:SphinxNotesSnippetListAndEdit()
  function! s:CallEdit(selection)
    call g:SphinxNotesSnippetEdit(s:SplitID(a:selection))
  endfunction
  call g:SphinxNotesSnippetList(function('s:CallEdit'), 'ds')
endfunction

function! g:SphinxNotesSnippetUrl(id)
  let url_list = systemlist(join([s:snippet, 'get', '--url', a:id, '2>/dev/null'], ' '))
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

function! g:SphinxNotesSnippetInput(id, item)
  let content = system(join([s:snippet, 'get', '--' . a:item, a:id, '2>/dev/null'], ' '))
  let content = substitute(content, '\n\+$', '', '') " skip trailing \n
  if a:item == 'docname' 
    " Create doc reference.
    let content = ':doc:`/' . content . '`'
  endif
  execute 'normal! i' . content
endfunction

function! g:SphinxNotesSnippetListAndInputDocname()
  function! s:InputDocname(selection)
    call g:SphinxNotesSnippetInput(s:SplitID(a:selection), 'docname')
  endfunction
  call g:SphinxNotesSnippetList(function('s:InputDocname'), 'd')
endfunction

nmap <C-k>e :call g:SphinxNotesSnippetListAndEdit()<CR>
nmap <C-k>u :call g:SphinxNotesSnippetListAndUrl()<CR>
nmap <C-k>d :call g:SphinxNotesSnippetListAndInputDocname()<CR>
" FIXME: can't return to insert mode even use a/startinsert!/C-o
imap <C-k>d <C-o>:call g:SphinxNotesSnippetListAndInputDocname()<CR>

" vim: set shiftwidth=2:
