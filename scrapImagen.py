import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict

class ScrapImagen:
    def __init__(self, base_url):
        self.base_url = base_url

    def obtener_imagenes(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.content, "html.parser")
        imagenes = defaultdict(list)
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                imagen_url = urljoin(self.base_url, src)
                # Extraer la fecha y la hora del nombre del archivo
                partes = src.split("_")
                if len(partes) > 1:
                    fecha = partes[0].split("/")[-1]  # Obtener la fecha del nombre del archivo
                    hora = partes[1]  # Obtener la hora del nombre del archivo
                    imagenes[fecha].append((hora, imagen_url))
        return imagenes
