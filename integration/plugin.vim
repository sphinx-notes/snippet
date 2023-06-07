" Vim integration for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-01
" :Version: 20211114
"
" NOTE: junegunn/fzf.vim is required

let s:snippet = 'snippet'

function! s:SplitID(row)
  return split(a:row, ' ')[0]
endfunction

function! g:SphinxNotesSnippetList(callback, tags)
  let l:width = 0.9
  let cmd = [s:snippet, 'list',
        \ '--tags', a:tags,
        \ '--width', float2nr(&columns * l:width) - 2,
        \ ]
  " https://github.com/junegunn/fzf/blob/master/README-VIM.md#fzfrun
  call fzf#run({
        \ 'source': join(cmd, ' '),
        \ 'sink': a:callback,
        \ 'options': ['--with-nth', '2..', '--no-hscroll', '--header-lines', '1'],
        \ 'window': {'width': l:width, 'height': 0.6},
        \ })
endfunction

" vim: set shiftwidth=2:
