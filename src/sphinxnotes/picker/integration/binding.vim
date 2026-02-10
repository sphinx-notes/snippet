" Vim key binding for sphinxnotes-picker
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-12
" :Version: 20211114
"

function g:SphinxNotesPickerEdit(id)
  let file = g:SphinxNotesPickerGet(a:id, 'file')[0]
  let line = g:SphinxNotesPickerGet(a:id, 'line-start')[0]
  if &modified
    execute 'vsplit ' . file
  else
    execute 'edit ' . file
  endif
  execute line
endfunction

function g:SphinxNotesPickerListAndEdit()
  function! ListAndEdit_CB(id)
    call g:SphinxNotesPickerEdit(a:id)
  endfunction
  call g:SphinxNotesPickerList('ds', function('ListAndEdit_CB'))
endfunction

function g:SphinxNotesPickerUrl(id)
  let url_list = g:SphinxNotesPickerGet(a:id, 'url')
  for url in url_list
    echo system('xdg-open ' . shellescape(url))
  endfor
endfunction

function g:SphinxNotesPickerListAndUrl()
  function! ListAndUrl_CB(id)
    call g:SphinxNotesPickerUrl(a:id)
  endfunction
  call g:SphinxNotesPickerList('ds', function('ListAndUrl_CB'))
endfunction

nmap <C-k>e :call g:SphinxNotesPickerListAndEdit()<CR>
nmap <C-k>u :call g:SphinxNotesPickerListAndUrl()<CR>
nmap <C-k>i :call g:SphinxNotesPickerListAndInput()<CR>

" vim: set shiftwidth=2:
