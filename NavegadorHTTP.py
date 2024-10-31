import socket
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from tkhtmlview import HTMLLabel
from urllib.parse import urlparse

def crear_solicitud_http(host, ruta="/"):
    solicitud = f"GET {ruta} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    return solicitud

#---- Conexion al socket y envío de la solicitud
def enviar_solicitud(host, puerto, solicitud):
    # Crear socket 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Conectar al servidor
    s.connect((host, puerto))
    # Enviar la solicitud HTTP
    s.sendall(solicitud.encode())
    
    # Recibir la respuesta
    respuesta = b""
    bits_completos = ""
    while True:
        datos = s.recv(4096)
        if not datos:
            break
        # Conversion a binario
        bits = ''.join(format(byte, '08b') for byte in datos)
        bits_completos += bits
        respuesta += datos
    s.close()
    
    #print("Datos recibidos (bits):", bits_completos)
    return respuesta, bits_completos

#---- Obtención del contenido HTML---------
def obtener_html(url):
    # Parsear la url
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    ruta = parsed_url.path or "/"
    
    if not host:
        return "URL no válida", ""
    # Crear la solicitud HTTP
    solicitud = crear_solicitud_http(host, ruta)
    
    try:
        # Enviar la solicitud y recibir 
        respuesta, bits_completos = enviar_solicitud(host, 80, solicitud)
        # Separar cabeceras del contenido
        contenido_html = respuesta.split(b"\r\n\r\n", 1)[1]
        # Convertir los bytes de HTML a ASCII
        return contenido_html.decode("ascii", errors="replace"), bits_completos
    except Exception as e:
        return f"Error al obtener la página: {e}", ""
    
def binario_a_ascii(codigo_binario):
    # Divide el código binario en grupos de 8 bits y convierte cada uno a ASCII si es imprimible
    ascii_chars = ''.join(
        chr(int(codigo_binario[i:i+8], 2)) 
        for i in range(0, len(codigo_binario), 8) 
        if int(codigo_binario[i:i+8], 2) in range(32, 127)
    )
    return ascii_chars

#----------------------------------------------INTERFAZ GRAFICA--------------------------------

def mostrar_html():
    # Obtener la URL ingresada 
    url = entrada_url.get()
    # Obtener el contenido HTML y los bits
    html, bits = obtener_html(url)
    # Interpretar los bits en ASCII
    ascii = binario_a_ascii(bits)
    
    # Mostrar el HTML renderizado en la pestaña "Página HTML"
    label_html.set_html(html)
    
    # Mostrar el HTML completo en la pestaña "Código HTML"
    area_codigo_html.delete(1.0, tk.END)
    area_codigo_html.insert(tk.END, html)
    
    # Mostrar los bits en la pestaña "Bits"
    area_bits.delete(1.0, tk.END)
    area_bits.insert(tk.END, bits)
    
    # Mostrar los bits en la pestaña "ASCII"
    area_ascii.delete(1.0, tk.END)
    area_ascii.insert(tk.END, ascii)    

# Ventana principal
ventana = tk.Tk()
ventana.title("Navegador")
ventana.geometry("800x600")

# Frame para la URL y el botón
frame_url = tk.Frame(ventana)
frame_url.pack(pady=10)
etiqueta_url = tk.Label(frame_url, text="URL:")
etiqueta_url.pack(side=tk.LEFT)
entrada_url = tk.Entry(frame_url, width=80)
entrada_url.pack(side=tk.LEFT, padx=(0, 5))
boton_cargar = tk.Button(frame_url, text="Cargar Página", command=mostrar_html)
boton_cargar.pack(side=tk.LEFT)

# Configuración de las pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(expand=1, fill='both')

# Pestaña para mostrar el HTML renderizado (Página HTML)
frame_html = ttk.Frame(notebook)
notebook.add(frame_html, text='Página HTML')
label_html = HTMLLabel(frame_html, html="")
label_html.pack(fill="both", expand=True)

# Pestaña para mostrar el código HTML original (Código HTML)
frame_codigo_html = ttk.Frame(notebook)
notebook.add(frame_codigo_html, text='Código HTML')
area_codigo_html = scrolledtext.ScrolledText(frame_codigo_html, wrap=tk.WORD, width=200, height=60)
area_codigo_html.pack(expand=1, fill='both')

# Pestaña para mostrar los bits de la respuesta (Bits)
frame_bits = ttk.Frame(notebook)
notebook.add(frame_bits, text='Bits')
area_bits = scrolledtext.ScrolledText(frame_bits, wrap=tk.WORD, width=200, height=60)
area_bits.pack(expand=1, fill='both')

# Pestaña para mostrar los bits de la respuesta (ASCII)
frame_ascii = ttk.Frame(notebook)
notebook.add(frame_ascii, text='ASCII')
area_ascii = scrolledtext.ScrolledText(frame_ascii, wrap=tk.WORD, width=200, height=60)
area_ascii.pack(expand=1, fill='both')

# ---- Función principal de la solicitud a la IP del host y el puerto de la VM ------

def main():
    # Dirección IP de la VM (o localhost si se usa NAT con puertos redirigidos)
    host = "172.20.10.2" 
    puerto = 80  # Puerto 
    # Solicitud HTTP
    solicitud = crear_solicitud_http(host)
    # Enviar la solicitud y recibir
    respuesta, bits_completos = enviar_solicitud(host, puerto, solicitud) 
    # Imprimir si es necesario para ver la respuesta.
    #print(respuesta.decode())

if __name__ == "__main__":
    main()
    ventana.mainloop()