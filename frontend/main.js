const { app, BrowserWindow } = require('electron')


function createWindow () {
  const win = new BrowserWindow({
    width: 1000,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    contextIsolation: false,
    },
    autoHideMenuBar: true,
    icon: __dirname + '/static/Logo_2.ico'
  })

  win.loadFile('index.html')
}

app.whenReady().then(createWindow)
