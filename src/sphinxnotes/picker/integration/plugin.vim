" Vim integration for sphinxnotes-picker
" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"
" :Author: Shengyu Zhang
" :Date: 2021-04-01
" :Version: 20211114
"
" NOTE: junegunn/fzf.vim is required

let s:picker = 'sphinxnotes-picker'
let s:width = 0.9
let s:height = 0.6

" Use fzf to list all snippets, callback with argument id.
function g:SphinxNotesPickerList(tags, callback)
  let cmd = [s:picker, 'list',
        \ '--tags', a:tags,
        \ '--width', float2nr(&columns * s:width) - 2,
        \ ]

  " Use closure keyword so that inner function can access outer one's
  " localvars (l:) and arguments (a:).
  " https://vi.stackexchange.com/a/21807
  function! List_CB(selection) closure
      let id = split(a:selection, ' ')[0]
      call a:callback(id)
  endfunction

  " https://github.com/junegunn/fzf/blob/master/README-VIM.md#fzfrun
  call fzf#run({
        \ 'source': join(cmd, ' '),
        \ 'sink': function('List_CB'),
        \ 'options': ['--with-nth', '2..', '--no-hscroll', '--header-lines', '1'],
        \ 'window': {'width': s:width, 'height': s:height},
        \ })
endfunction

" Return the attribute value of specific snippet.
function g:SphinxNotesPickerGet(id, attr)
    let cmd = [s:picker, 'get', a:id, '--' . a:attr]
    return systemlist(join(cmd, ' '))
endfunction

" Use fzf to list all attr of specific snippet,
" callback with arguments (attr_name, attr_value).
function g:SphinxNotesPickerListPickerAttrs(id, callback)
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

    function! ListPickerAttrs_CB(selection) closure
        let opt = split(a:selection, ' ')[0]
        let val = g:SphinxNotesPickerGet(a:id, opt)
        call a:callback(opt, val) " finally call user's cb
    endfunction

    let preview_cmd = [s:picker, 'get', a:id, '--$(echo {} | cut -d " " -f1)']
    let info_cmd = ['echo', 'Index ID:', a:id]
    call fzf#run({
                \ 'source': table,
                \ 'sink': function('ListPickerAttrs_CB'),
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

function g:SphinxNotesPickerInput(id)
  function! Input_CB(attr, val) " TODO: became g:func.
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

  call g:SphinxNotesPickerListPickerAttrs(a:id, function('Input_CB'))
endfunction

function g:SphinxNotesPickerListAndInput()
  function! ListAndInput_CB(id)
    call g:SphinxNotesPickerInput(a:id)
  endfunction

  call g:SphinxNotesPickerList('"*"', function('ListAndInput_CB'))
endfunction

  " vim: set shiftwidth=2:
