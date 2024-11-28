const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    selectFolder: () => ipcRenderer.invoke('select-folder'),
    processImages: (dirs) => ipcRenderer.invoke('process-images', dirs),
});
