'''
EN ESTE ARCHIVO SE ENCUENTRAN MODELOS DE MACHINE LEANRNIG PARA TRABAJAR CON EL DATASET 
ESPECIFICO DE LA DEL PROYECTO
'''

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import scale
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

class Modelo():
    # region MODELO PCA
    def modeloPCA(self,dataframe): # este metodo recibe un dataframe y devulve un dataframe PCA
        # Reemplazar NaN con ceros
        dataframe.fillna(0, inplace=True)
    
        # Eliminar filas con datos nulos
        dataframe.dropna(inplace=True)
        # Asegurar que todos los datos sean numéricos
        dataframe = dataframe.apply(pd.to_numeric, errors='coerce')
    
        # Eliminar filas con valores no numéricos
        dataframe.dropna(inplace=True)
    
        # Estandarizar los datos
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(dataframe)
    
        # Realizar el análisis de componentes principales
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(data_scaled)
    
        # Crear un nuevo dataframe con solo los dos primeros componentes principales
        pca_df = pd.DataFrame(data = principal_components, columns = ['Componente 1', 'Componente 2'])
    
        return pca_df
    
        # endregion
    
    
    
    # region MODELO DBSCAN
    def modelo_DBSCAN(self,dataframe, min_samples):
        # Reemplazar NaN con ceros
        dataframe.fillna(0, inplace=True)
    
        # Eliminar filas con datos no numéricos
        dataframe = dataframe.apply(pd.to_numeric, errors='coerce')
        dataframe.dropna(inplace=True)
    
        # Escalar los datos
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(dataframe)
    
        # Realizar el análisis con DBSCAN
        dbscan = DBSCAN(eps=min_samples)
        clases_dbscan = dbscan.fit_predict(data_scaled)
    
        # Realizar el análisis de componentes principales
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(data_scaled)
    
        # Crear un nuevo DataFrame con los componentes principales y las clases de DBSCAN
        pca_df = pd.DataFrame(data=principal_components, columns=['Componente 1', 'Componente 2'])
        pca_df['Clase'] = clases_dbscan
    
        return pca_df
    
    # endregion
    

class R_lineal:
        
    #region MODELO REGRESION LINEAL
    def __init__(self):
        self.modelo = LinearRegression()

    def entrenar_y_guardar(self, dataframe, archivo_modelo):
        # Dividir el dataset en características (X) y variable objetivo (y)
        X = dataframe.drop('Prediccion', axis=1)  # Características
        y = dataframe['Prediccion']  # Variable objetivo
        
        # Dividir los datos en conjuntos de entrenamiento y prueba (80% entrenamiento, 20% prueba)
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar el modelo
        self.modelo.fit(X_train, y_train)

        # Guardar el modelo entrenado en un archivo
        joblib.dump(self.modelo, archivo_modelo)

    def predecir(self, datos_entrada, ruta_modelo):
        # Cargar el modelo entrenado
        modelo_cargado = joblib.load(ruta_modelo)
        
        # Convertir la serie de Pandas en una matriz bidimensional
        datos_entrada = datos_entrada.values.reshape(1, -1)
        
        # Realizar la predicción
        prediccion = modelo_cargado.predict(datos_entrada)

        return prediccion
    # endregion    
    