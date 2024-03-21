# archivo con clase para scrap_web
import requests
from bs4 import BeautifulSoup
import pandas as pd

class Scrapero:
    def scrapear(self, url):
        # Realizar una solicitud GET a la página web
        response = requests.get(url)

        # Comprobar si la solicitud fue exitosa (código de estado 200)
        if response.status_code == 200:
            # Parsear el contenido de la página web utilizando BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Encontrar la tabla en la página web (puedes inspeccionar la página web para encontrar el selector adecuado)
            table = soup.find('table')

            # Extraer los datos de la tabla y cargarlos en un DataFrame de Pandas
            if table:
                # Inicializar listas para almacenar los datos
                rows = []
                headers = []

                # Iterar sobre las filas de la tabla
                for row in table.find_all('tr'):
                    # Obtener los datos de cada celda en la fila
                    row_data = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]

                    # Verificar si es una fila de encabezado o de datos
                    if len(row_data) > 0:
                        # Si la lista de encabezados está vacía, asumimos que esta fila es un encabezado
                        if not headers:
                            headers = row_data
                        else:
                            rows.append(row_data)

                # Convertir la lista de datos en un DataFrame de Pandas
                df = pd.DataFrame(rows, columns=headers)
                return df
            else:
                print("No se encontró ninguna tabla en la página.")
        else:
            print("No se pudo acceder a la página web.")
