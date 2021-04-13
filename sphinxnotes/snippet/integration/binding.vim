" NeoVim key binding for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-12
" :Version: 20210412
"
nmap <C-k>v :call g:SphinxNotesSnippetListAndView()<CR>
nmap <C-k>e :call g:SphinxNotesSnippetListAndEdit()<CR>
nmap <C-k>u :call g:SphinxNotesSnippetListAndUrl()<CR>

" vim: set shiftwidth=2:
