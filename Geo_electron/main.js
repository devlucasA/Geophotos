const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const sharp = require('sharp');
const exifParser = require('exif-parser');

let mainWindow;

app.on('ready', () => {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        },
    });

    mainWindow.loadFile('index.html');
});

ipcMain.handle('select-folder', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
    });
    return result.filePaths[0];
});

ipcMain.handle('process-images', async (event, { inputDir, outputDir }) => {
    const files = fs.readdirSync(inputDir).filter(file => /\.(jpg|jpeg|png)$/i.test(file));
    const metadataList = [];

    for (const file of files) {
        const filePath = path.join(inputDir, file);
        const buffer = fs.readFileSync(filePath);
        const parser = exifParser.create(buffer);
        const exifData = parser.parse();

        if (exifData.tags.GPSLongitude && exifData.tags.GPSLatitude) {
            const longitude = exifData.tags.GPSLongitude;
            const latitude = exifData.tags.GPSLatitude;

            metadataList.push({ file, longitude, latitude });

            const outputImagePath = path.join(outputDir, file);
            const textOverlay = `Longitude: ${longitude.toFixed(5)}, Latitude: ${latitude.toFixed(5)}`;

            // SVG para texto com retângulo de fundo
            const svgOverlay = `
                <svg width="2000" height="200">
                    <!-- Retângulo branco -->
                    <rect x="0" y="0" width="100%" height="100%" fill="white" opacity="0.8" />
                    <!-- Texto -->
                    <text x="10" y="85" font-size="100" fill="black" font-family="Arial" dominant-baseline="middle">
                        ${textOverlay}
                    </text>
                </svg>
            `;

            // Adiciona o overlay à imagem
            await sharp(filePath)
                .composite([
                    {
                        input: Buffer.from(svgOverlay),
                        gravity: 'southwest', // Posiciona no canto inferior esquerdo
                    },
                ])
                .toFile(outputImagePath);
        }
    }

    // Salva o arquivo de metadados
    const metadataFile = path.join(outputDir, 'metadata.txt');
    fs.writeFileSync(
        metadataFile,
        metadataList
            .map(data => `${data.file}: Longitude ${data.longitude}, Latitude ${data.latitude}`)
            .join('\n')
    );



    return metadataList.length;
});

  