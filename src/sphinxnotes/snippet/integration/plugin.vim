" Vim integration for sphinxnotes-snippet
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-01
" :Version: 20211114
"
" NOTE: junegunn/fzf.vim is required

let s:snippet = 'snippet'
let s:width = 0.9
let s:height = 0.6

" TODO: remove
function! s:SplitID(row)
  return split(a:row, ' ')[0]
endfunction

" Use fzf to list all snippets, callback with arguments (selection).
function! g:SphinxNotesSnippetList(callback, tags)
  let cmd = [s:snippet, 'list',
        \ '--tags', a:tags,
        \ '--width', float2nr(&columns * s:width) - 2,
        \ ]
  " https://github.com/junegunn/fzf/blob/master/README-VIM.md#fzfrun
  call fzf#run({
        \ 'source': join(cmd, ' '),
        \ 'sink': a:callback,
        \ 'options': ['--with-nth', '2..', '--no-hscroll', '--header-lines', '1'],
        \ 'window': {'width': s:width, 'height': s:height},
        \ })
endfunction

" Return the attribute value of specific snippet.
function! g:SphinxNotesSnippetGet(id, attr)
    let cmd = [s:snippet, 'get', a:id, '--' . a:attr]
    return systemlist(join(cmd, ' '))
endfunction

" Use fzf to list all attr of specific snippet,
" callback with arguments (attr_name, attr_value).
function! g:SphinxNotesSnippetListSnippetAttrs(id, callback)
    " Display attr -> Identify attr (also used as CLI option)
    let attrs = {
                \ 'Source':             'src',
                \ 'URL':                'url',
                \ 'Docname':            'docname',
                \ 'Dependent files':    'deps',
                \ 'Text':               'text',
                \ 'Title':              'title',
                \ }
    let delim = '  '
    let table = ['OPTION' . delim . 'ATTRIBUTE']
    for name in keys(attrs)
        call add(table, attrs[name] . delim . name)
    endfor

    " Local scope -> script scope, so vars can be access from inner function.
    let s:id_for_list_snippet_attrs  = a:id
    let s:cb_for_list_snippet_attrs = a:callback
    function! s:SphinxNotesSnippetListSnippetAttrs_CB(selection)
        let opt = split(a:selection, ' ')[0]
        let val = g:SphinxNotesSnippetGet(s:id_for_list_snippet_attrs, opt)
        call s:cb_for_list_snippet_attrs(opt, val) " finally call user's cb
    endfunction

    let preview_cmd = [s:snippet, 'get', a:id, '--$(echo {} | cut -d " " -f1)']
    let info_cmd = ['echo', 'Index ID:', a:id]
    call fzf#run({
                \ 'source': table,
                \ 'sink': function('s:SphinxNotesSnippetListSnippetAttrs_CB'),
                \ 'options': [
                \               '--header-lines', '1',
                \               '--with-nth', '2..',
                \               '--preview', join(preview_cmd, ' '),
                \               '--preview-window', ',wrap',
                \               '--info-command', join(info_cmd, ' '),
                \            ],
                \ 'window': {'width': s:width, 'height': s:height},
                \ })
endfunction

function! g:SphinxNotesSnippetInput(id)
  function! s:SphinxNotesSnippetInput_CB(attr, val)
    if a:attr == 'docname' 
      " Create doc reference.
      let content = ':doc:`/' . a:val[0] . '`'
    elseif a:attr == 'title'
      " Create local section reference.
      let content = '`' . a:val[0] . '`_'
    else
      let content = join(a:val, '<CR>')
    endif

    execute 'normal! i' . content
  endfunction

  call g:SphinxNotesSnippetListSnippetAttrs(a:id, function('s:SphinxNotesSnippetInput_CB'))
endfunction

function! g:SphinxNotesSnippetListAndInput()
  function! s:SphinxNotesSnippetListAndInput_CB(selection)
    let id = s:SplitID(a:selection)
    call g:SphinxNotesSnippetInput(id)
  endfunction

  call g:SphinxNotesSnippetList(function('s:SphinxNotesSnippetListAndInput_CB'), '"*"')
endfunction

  " vim: set shiftwidth=2:
