import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import exifread
import os

def get_gps_data(file_path):
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f)
    
    gps_latitude = tags.get('GPS GPSLatitude')
    gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
    gps_longitude = tags.get('GPS GPSLongitude')
    gps_longitude_ref = tags.get('GPS GPSLongitudeRef')
    
    if not all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
        return None
    
    def convert_to_degrees(value):
        d, m, s = [float(x.num) / x.den for x in value.values]
        return d + (m / 60.0) + (s / 3600.0)

    lat = convert_to_degrees(gps_latitude)
    if gps_latitude_ref.values[0] != 'N':
        lat = -lat

    lon = convert_to_degrees(gps_longitude)
    if gps_longitude_ref.values[0] != 'E':
        lon = -lon
    
    return lat, lon

def draw_text_on_images(input_folder, output_folder, txt_path, font_size):
    # Cria a pasta de saída se não existir
    os.makedirs(output_folder, exist_ok=True)

    # Cria ou abre o arquivo de texto para salvar coordenadas
    with open(txt_path, 'w') as txt_file:
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(input_folder, filename)
                image = Image.open(file_path)

                # Obter dados de GPS
                gps_data = get_gps_data(file_path)
                if gps_data:
                    lat, lon = gps_data
                    text = f"{filename}: Latitude: {lat:.6f}, Longitude: {lon:.6f}"
                else:
                    text = f"{filename}: Localização não disponível"

                # Desenhar o texto na imagem
                draw = ImageDraw.Draw(image)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()

                text_position = (10, image.height - 160)
                text_bbox = draw.textbbox(text_position, text, font=font)
                padding = 5
                rectangle_position = [
                    text_bbox[0] - padding, 
                    text_bbox[1] - padding, 
                    text_bbox[2] + padding, 
                    text_bbox[3] + padding
                ]
                draw.rectangle(rectangle_position, fill="white")
                text_color = (0, 0, 0)
                draw.text(text_position, text, fill=text_color, font=font)

                # Salva a imagem no formato JPEG na pasta de saída
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.jpeg")
                image = image.convert("RGB")
                image.save(output_path, "JPEG")
                
                # Escreve a coordenada da imagem no arquivo txt
                txt_file.write(text + '\n')

    messagebox.showinfo("Processamento Completo", "As imagens foram processadas com sucesso!")

def select_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_var.set(folder_selected)

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_var.set(folder_selected)

def process_images():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    font_size = int(font_size_var.get())
    txt_path = os.path.join(output_folder, 'coordenadas.txt')

    if not input_folder or not output_folder:
        messagebox.showwarning("Atenção", "Por favor, selecione as pastas de entrada e saída.")
        return

    draw_text_on_images(input_folder, output_folder, txt_path, font_size)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Processador de Coordenadas em Imagens")
root.geometry("400x250")

input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
font_size_var = tk.StringVar(value="150")

# Label e botão para seleção da pasta de entrada
tk.Label(root, text="Pasta de Entrada:").pack(pady=5)
tk.Entry(root, textvariable=input_folder_var, width=50).pack(pady=5)
tk.Button(root, text="Selecionar Pasta", command=select_input_folder).pack(pady=5)

# Label e botão para seleção da pasta de saída
tk.Label(root, text="Pasta de Saída:").pack(pady=5)
tk.Entry(root, textvariable=output_folder_var, width=50).pack(pady=5)
tk.Button(root, text="Selecionar Pasta", command=select_output_folder).pack(pady=5)

# Label e entrada para o tamanho da fonte
tk.Label(root, text="Tamanho do Texto:").pack(pady=5)
tk.Entry(root, textvariable=font_size_var, width=10).pack(pady=5)

# Botão de processamento
tk.Button(root, text="Processar Imagens", command=process_images, bg="green", fg="white").pack(pady=20)

root.mainloop()
