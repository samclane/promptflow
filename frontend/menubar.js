const { ipcRenderer } = require('electron');
const { fromEvent } = require('rxjs');

const new$ = fromEvent(ipcRenderer, 'new');

new$.subscribe(() => {
    console.log('new');
});

const open$ = fromEvent(ipcRenderer, 'open');

open$.subscribe(() => {
    window.location.href = 'index.html';
});

const save$ = fromEvent(ipcRenderer, 'save');

save$.subscribe(() => {
    console.log('save');
});

const saveAs$ = fromEvent(ipcRenderer, 'saveAs');

saveAs$.subscribe(() => {
    console.log('saveAs');
});

const export$ = fromEvent(ipcRenderer, 'export');

export$.subscribe(() => {
    console.log('export');
});

const exit$ = fromEvent(ipcRenderer, 'exit');

exit$.subscribe(() => {
    // close window
    window.close();
});

const undo$ = fromEvent(ipcRenderer, 'undo');

undo$.subscribe(() => {
    console.log('undo');
});

const redo$ = fromEvent(ipcRenderer, 'redo');

redo$.subscribe(() => {
    console.log('redo');
});

const cut$ = fromEvent(ipcRenderer, 'cut');

cut$.subscribe(() => {
    console.log('cut');
});

const copy$ = fromEvent(ipcRenderer, 'copy');

copy$.subscribe(() => {
    console.log('copy');
});

const paste$ = fromEvent(ipcRenderer, 'paste');

paste$.subscribe(() => {
    console.log('paste');
});

const selectAll$ = fromEvent(ipcRenderer, 'selectAll');

selectAll$.subscribe(() => {
    console.log('selectAll');
});

const delete$ = fromEvent(ipcRenderer, 'delete');

delete$.subscribe(() => {
    console.log('delete');
});

const zoomIn$ = fromEvent(ipcRenderer, 'zoomIn');

zoomIn$.subscribe(() => {
    console.log('zoomIn');
});

const zoomOut$ = fromEvent(ipcRenderer, 'zoomOut');

zoomOut$.subscribe(() => {
    console.log('zoomOut');
});

const zoomReset$ = fromEvent(ipcRenderer, 'resetZoom');

zoomReset$.subscribe(() => {
    console.log('resetZoom');
});
