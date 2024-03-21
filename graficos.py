import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Grafico():
    
    # region GRAFICO HISTOGRAMA
    def histograma(self,df,nombre,etiqueta_x, titulo):
        df=df
        nombre=nombre
        # Crear histograma
        fig, ax = plt.subplots()
        ax.hist(df[nombre], bins=5, color='blue', edgecolor='black')

        # Agregar etiquetas y título
        ax.set_xlabel(etiqueta_x)
        ax.set_ylabel('Frecuencia')
        ax.set_title(titulo)
        ax.tick_params(axis='x', labelsize=6)
        plt.xticks(rotation=45)

        # Guardar la figura en una variable
        figura = plt.gcf()
        return figura
    # endregion
    
    # region GRAFICO DE LINEA
    def grafico_de_linea(self, x, y, etiqueta_x, etiqueta_y, titulo):
            # Crear gráfico de línea
        fig, ax = plt.subplots()
        ax.plot(x, y, color='red', marker='o', linestyle='-')

        # Agregar etiquetas y título
        ax.set_xlabel(etiqueta_x)
        ax.set_ylabel(etiqueta_y)
        ax.set_title(titulo)
        ax.tick_params(axis='x', labelsize=6)
        plt.xticks(rotation=45)

        # Guardar la figura en una variable
        figura = plt.gcf()
        return figura
    
    # endregion
    
    # region GRAFICO DE DISPERCION 
    def grafico_de_dispersion(self, x, y, etiqueta_x, etiqueta_y, titulo):
            # Crear gráfico de dispersión
        fig, ax = plt.subplots()
        ax.scatter(x, y, color='green', marker='o')

        # Agregar etiquetas y título
        ax.set_xlabel(etiqueta_x)
        ax.set_ylabel(etiqueta_y)
        ax.set_title(titulo)

        # Guardar la figura en una variable
        figura = plt.gcf()
        return figura
    
    # endregion
    
    # region GRAFICO DE DISPERCION CON COLOR DE 
    
    def grafico_dispersion_color(self, x, y,color, etiqueta_x, etiqueta_y, titulo):
            # Crear gráfico de dispersión
        fig, ax = plt.subplots()
        ax.scatter(x, y, c=color, marker='o')

        # Agregar etiquetas y título
        ax.set_xlabel(etiqueta_x)
        ax.set_ylabel(etiqueta_y)
        ax.set_title(titulo)

        # Guardar la figura en una variable
        figura = plt.gcf()
        return figura
    
    # endregion
    
    # region MAPA DE CALOR DE COORRELACIONES
    # esta funcion recive un dataframe y devuelve la ruta de imagen temporal
    # de una mapa de calor de coorrelaciones
    def heatmap(self, df):
        # Calcular la matriz de correlación
        correlacion_matrix = df.corr()

        # Crear el mapa de calor
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlacion_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Mapa de Calor de Correlación')
    
        # Guardar el mapa de calor en un archivo temporal
        img_path = "heatmap_correlacion.png"
        plt.savefig(img_path, bbox_inches='tight', format='png')
        plt.close()  # Cerrar la figura para liberar memoria

        return img_path
    # endregion
    
    # region DATAFRAME DE ESTADISTICAS
    # esta funcion recibe un dataframe y devuelte una dataframe
    # con estadisticas basicas como la moda y la varianza
    def descripcion(self, df):
        nuevo_df = df.describe().transpose()
        # Calcular las métricas estadísticas


        # Agregar la moda como una nueva fila
        moda = df.mode()
        nuevo_df['Moda'] = moda.iloc[0]
        return nuevo_df
    
       