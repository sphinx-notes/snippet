" Vim integration for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-01
" :Version: 20210814
"
" NOTE: junegunn/fzf.vim is required

let s:snippet = 'snippet'

function! s:SplitID(row)
  return split(a:row, ' ')[0]
endfunction

function! g:SphinxNotesSnippetList(callback, tags)
  let cmd = [s:snippet, 'list',
        \ '--tags', a:tags,
        \ '--width', &columns - 2,
        \ ]
  call fzf#run({
        \ 'source': join(cmd, ' '),
        \ 'sink': a:callback,
        \ 'options': ['--with-nth', '2..', '--no-hscroll', '--header-lines', '1'],
        \ })
endfunction

" vim: set shiftwidth=2:
