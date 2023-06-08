const { app, BrowserWindow, Menu } = require('electron')


function createWindow () {
  const win = new BrowserWindow({
    width: 1000,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    contextIsolation: false,
    },
    icon: __dirname + '/static/Logo_2.ico'
  })

  win.loadFile('index.html')

  const menuTemplate = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New',
          accelerator: 'Ctrl+N',
          click: () => {
            win.webContents.send('new')
          }
        },
        {
          label: 'Open',
          accelerator: 'Ctrl+O',
          click: () => {
            win.webContents.send('open')
          }
        }, 
        {
          label: 'Save',
          accelerator: 'Ctrl+S',
          click: () => {
            win.webContents.send('save')
          }
        },
        {
          label: 'Save As',
          accelerator: 'Ctrl+Shift+S',
          click: () => {
            win.webContents.send('saveAs')
          }
        },
        {
          label: 'Export',
          accelerator: 'Ctrl+E',
          click: () => {
            win.webContents.send('export')
          }
        },
        {
          label: 'Exit',
          accelerator: 'Ctrl+Q',
          click: () => {
            win.webContents.send('exit')
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        {
          label: 'Undo',
          accelerator: 'Ctrl+Z',
          click: () => {
            win.webContents.send('undo')
          }
        },
        {
          label: 'Redo',
          accelerator: 'Ctrl+Y',
          click: () => {
            win.webContents.send('redo')
          }
        },
        {
          label: 'Cut',
          accelerator: 'Ctrl+X',
          click: () => {
            win.webContents.send('cut')
          }
        },
        {
          label: 'Copy',
          accelerator: 'Ctrl+C',
          click: () => {
            win.webContents.send('copy')
          }
        },
        {
          label: 'Paste',
          accelerator: 'Ctrl+V',
          click: () => {
            win.webContents.send('paste')
          }
        },
        {
          label: 'Delete',
          accelerator: 'Delete',
          click: () => {
            win.webContents.send('delete')
          }
        },
        {
          label: 'Select All',
          accelerator: 'Ctrl+A',
          click: () => {
            win.webContents.send('selectAll')
          }
        },
        {
          label: 'Refresh',
          accelerator: 'Ctrl+R',
          click: () => {
            win.reload()
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Zoom In',
          accelerator: 'Ctrl+Plus',
          click: () => {
            win.webContents.send('zoomIn')
          }
        },
        {
          label: 'Zoom Out',
          accelerator: 'Ctrl+-',
          click: () => {
            win.webContents.send('zoomOut')
          }
        },
        {
          label: 'Reset Zoom',
          accelerator: 'Ctrl+0',
          click: () => {
            win.webContents.send('resetZoom')
          }
        },
        {
          label: 'Developer Tools',
          accelerator: 'Ctrl+Shift+I',
          click: () => {
            win.webContents.openDevTools()
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

app.whenReady().then(() => {
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
      app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
  }
});