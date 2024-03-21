import streamlit as st 
import pandas as pd
from consulta_db import Database
import mysql.connector
import matplotlib.pyplot as plt
from graficos import Grafico
from modelos import *
from scrap_web import Scrapero
import plotly.graph_objects as go
# region conexion a la base de datos (DESCONECTADA POR AHORA)
########### conectar con la base de datos########################


#database = Database(
#    host="sql10.freesqldatabase.com",
#    usuario="sql10690757",
#    contraseña="PfEevLLg59",
#    base_datos="sql10690757",
#)

#database.conectar()

# Ejemplo de ejecución de una consulta
#resultado = database.ejecutar_consulta("SELECT * FROM SensorData")
#data = pd.DataFrame(resultado)
#data = data.rename(columns={0:'id',1:'sensor',2:'ambiente',3:'temp_ext',4:'temp_int',
#                    5:'hum_ext', 6:'hum_int', 7:'temp_s_ext', 8:'temp_s_int',
#                    9:'ventana', 10:'Aire_AC', 11:'fecha'})
#print(data.columns)
#database.desconectar()
#df=data
#################################################################

# endregion


# region SCRAP de datos (POR AHORA ACTIVO)
##########################################################################
scrap = Scrapero()
path = 'https://www.proyectociudad.com.ar/esp-data.php'
# columnas de la tabla 
# ['ID', 'Sensor', 'Location', 'TEMP_INT', 'TEMP_EXT', 'HUM_INT',
#       'TEMP_INTERIORDHT11', 'HUMEDAD_EXT', 'TEMP_EXT_DHT11', 'BOTON_INT',
#      'BOTON_EXT', 'Timestamp']
data = scrap.scrapear(url=path)
df = data
df['Timestamp']=pd.to_datetime(df['Timestamp'])
# Convertir las columnas a tipo float
columnas = ['TEMP_INT', 'TEMP_EXT', 'HUM_INT', 'HUMEDAD_EXT','TEMP_INTERIORDHT11','TEMP_EXT_DHT11']
df[columnas] = df[columnas].apply(pd.to_numeric, errors='coerce')

print(df.columns)
##########################################################################
# endregion

# region caracteristicas de menu
caracteristicas= ['Temperatura externa', 'Temperatura interna', 'Temperatura muro externa',
                'Temperatura muro interna', 'Humedad externa', 'Humedad interna',
                'Ventana abierta', 'Aire acondicionado encendido']

columna= {'Temperatura externa':'TEMP_EXT_DHT11', 'Temperatura interna':'TEMP_INTERIORDHT11', 
            'Temperatura muro externa':'TEMP_EXT',
                'Temperatura muro interna':'TEMP_INT', 'Humedad externa':'HUMEDAD_EXT',
                'Humedad interna':'HUM_INT', 'Ventana abierta':'BOTON_EXT', 
                'Aire acondicionado encendido':'BOTON_EXT'}
# endregion
with st.sidebar:
    # region de seleccion de periodo de estudio
    with st.expander("Periodo de estudio"):
        selec=['Historico','Ultimas 24 horas', 'Ultimas 12 horas', 'Ultima hora']
        
        radioButton = st.radio(label='Periodo', options=selec, on_change=None)    
        if radioButton =='Historico':
            df=data
        elif radioButton == 'Ultimas 24 horas':
            df=data.head(97)
        elif radioButton == 'Ultimas 12 horas':
            df=data.head(48)
        elif radioButton == 'Ultima hora':
            df=data.head(4)    
    # endregion
    # region grafico histograma y seleccion de variable comparativa
    with st.expander("Seccion 'A' variables independientes"):
        st.subheader("seleccion tipo de grafico")
        opcion = st.selectbox(label='',options=['Histograma','Linea'], label_visibility='hidden')
        st.subheader("Variables a comparar")
        subCol_1, subCol_2 = st.columns(2)
        with subCol_1:
                var_1 = st.selectbox(label="Variable uno", options=caracteristicas)
        with subCol_2:
                var_2 = st.selectbox(label="Variable dos", options=caracteristicas)
    # endregion
    
    # grafico de dispercion
    with st.expander("Grafico 2 Dispercion"):
        st.markdown('Grafico de dispercion')
        
        elec = st.multiselect(label='Variables', options=caracteristicas, label_visibility='collapsed')
        
        
    # sidebar grafico PCA y DBSCAN    
    
    with st.expander("Grafico 3 PCA y DBSCAN"):
        st.markdown('Analisis PCA')
        
        elec_PCA = st.multiselect(label='Variable', options=caracteristicas, label_visibility='collapsed')
        
        st.text("Valor Epsilon para DBSCAN")
        clusters=st.slider(label='Epsilon',min_value=0.1, max_value=4.0,value=0.5)
    
    
#creacion del objeto grafico para futuras llamadas a sus metodos
grafico = Grafico()
# visualizacion del diagrama del sensor
with st.expander('Diagrama de la disposicion de los sensores '):
    ruta="imagenes\diagrama.png"
    st.image(ruta, caption='Diagrama')

# region MAPA DE CALOR DE COORELACIONES

with st.expander("Mapa de calor coorrelaciones"):
    ruta_imagen = grafico.heatmap(df)
    st.image(ruta_imagen, caption='Mapa de calor coorrelaciones')  
    
# endregion    

# region DATAFRAME DE ESTADISTICAS BASICAS
with st.expander("Estadisticas basicas"):
    # referenciamos el dataframe a una nueva variable para poder
    # cambiar el nombre de las columnas y que sean mas legibles
    # por el usuario
    ndf= df 
    cabecera= {
        'TEMP_INT':'Temp. muro interior', 'TEMP_EXT':'Temp. muro exterior',
        'HUM_INT':'Humedad interior', 'TEMP_INTERIORDHT11':'Temp. interior',
        'HUMEDAD_EXT':'Humedad exterior', 'TEMP_EXT_DHT11':'Temp. exterior'
    }
    ndf = ndf.rename(columns=cabecera)
    ndf = grafico.descripcion(ndf)
    
    st.dataframe(ndf)
# endregion
  
#graficos Histograma y de linea dentro de expansor
with st.expander('Visualice el grafico 1 seleccionado en el menú de la izquierda'):            
    
    col1,col2 =st.columns(2)
    if opcion == 'Histograma':
        with col1:
                st.subheader(f"Grafica {opcion}")
                st.pyplot(grafico.histograma(df, columna[var_1],var_1,var_1))
            
        with col2:
                st.subheader(f"Grafica {opcion}")
                st.pyplot(grafico.histograma(df, columna[var_2],var_2,var_2))
    elif opcion == 'Linea':
        with col1:
                st.subheader(f"Grafica {opcion}")
                st.text(f'ha elegido la variable {var_1}')
                st.pyplot(grafico.grafico_de_linea(df['Timestamp'],df[columna[var_1]],'Fecha',var_1,var_1))
                
            
        with col2:
                st.subheader(f"Grafica {opcion}")
                st.text(f'ha elegido la variable {var_2}')
                st.pyplot(grafico.grafico_de_linea(df['Timestamp'],df[columna[var_2]],'Fecha',var_2,var_2))

# region GRAFICO DE LINEAS SUPERPUESTAS

with st.expander(" Grafico de lineas superpuestas"):
    col_a, col_b = st.columns(2)
    with col_a:
        df_l = df[['TEMP_INT','TEMP_EXT','TEMP_INTERIORDHT11','TEMP_EXT_DHT11','Timestamp']]

        # Crear figura de Plotly
        fig = go.Figure()

        # Añadir líneas al gráfico
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['TEMP_INT'], mode='lines', name='Temp Muro Int'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['TEMP_INTERIORDHT11'], mode='lines', name='Temp Int'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['TEMP_EXT'], mode='lines', name='Temp Muro Ext'))
        
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['TEMP_EXT_DHT11'], mode='lines', name='Temp Ext'))
        
        
        # Configuración del diseño del gráfico
        fig.update_layout(
        title='Gráfico de Temperaturas',
        xaxis_title='Fecha',
        yaxis_title='Grados centigrados',
        template='plotly_white'
        )
    
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)

        with col_b:
            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir líneas al gráfico
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['HUM_INT'], mode='lines', name='Humedad Int'))
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['HUMEDAD_EXT'], mode='lines', name='Humedad Ext'))
            
            
            
            # Configuración del diseño del gráfico
            fig.update_layout(
            title='Gráfico de Humedad relativa',
            xaxis_title='Fecha',
            yaxis_title='Porcentaje',
            template='plotly_white'
            )
        
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)

# endregion



# region grafico de dispersion            
with st.expander("Grafico 2 Dispersion"):
    if elec.__len__() >= 2:
            st.pyplot(grafico.grafico_de_dispersion(df[columna[elec[0]]],df[columna[elec[1]]],elec[0],elec[1],'Dispersion'))
    else:
        st.text("Elija dos variable")
# endregion

# region PCA y DBSCAN

listado=[]
for item in elec_PCA:
    listado.append(columna[item])
datosPCA = df[listado]

with st.expander(label='Grafico 3 Analisis de PCA y Cluster DBSCAN'):
    col_pca_1,col_pca_2 = st.columns(2)
    if elec_PCA:
        with col_pca_1:
            pca = Modelo()
            df_pca = pca.modeloPCA(dataframe=datosPCA)
            st.pyplot(grafico.grafico_de_dispersion(df_pca.iloc[:,0],df_pca.iloc[:,1],'componente 1','compoente 2', 'analisis de componentes principales'))
        with col_pca_2:
            df_dbscan = pca.modelo_DBSCAN(datosPCA, clusters)
            st.pyplot(grafico.grafico_dispersion_color(df_pca.iloc[:,0],df_pca.iloc[:,1],df_dbscan['Clase'],'componente 1','compoente 2', 'DBSCAN'))
            




# endregion

#region REGRESION LINEAL
with st.expander("Prediccion por regresion lineal"):
    df_ultimo = df.iloc[0]
    st.markdown("Parametros actuales (ultima medicion) {}".format(df_ultimo['Timestamp']))
    
    colA,colB,colC = st.columns(3)
    with colA:
        st.text("Temperatura \nExterior : {} °C".format(df_ultimo['TEMP_EXT_DHT11']))
        st.text("Temperatura \nInterior : {} °C".format(df_ultimo['TEMP_INTERIORDHT11']))
    with colB:
        st.text("Humedad \nExterior : {} °C".format(df_ultimo['HUMEDAD_EXT']))
        st.text("Humedad \nInterior : {} °C".format(df_ultimo['HUM_INT']))
    with colC:
        st.text("Temp. Muro \nExterior : {} °C".format(df_ultimo['TEMP_EXT']))
        st.text("Temp. Muro \nInterior : {} °C".format(df_ultimo['TEMP_INT']))

    # conformacion del dataset para el entrenamiento
    lista= ['TEMP_INT','TEMP_EXT','HUM_INT','TEMP_INTERIORDHT11','HUMEDAD_EXT','TEMP_EXT_DHT11']
    reg_df = df[lista]
    df_ultimo = df_ultimo[lista] # del ultimo registro solo guardamos las columnas de interes
    # conformacion de la columna con los valores target
    reg_df['Prediccion'] = 0
    
    regresion = R_lineal() #creamos un objeto de regrasion lineal
    ruta_modelo = 'C:/Users/Javier/Desktop/Streamlit_TUTORIAL/modelo_regresion_lineal.pkl'
    prediccion = regresion.predecir(df_ultimo,ruta_modelo)
    colE,colF=st.columns(2)
    
 
    
    #colE.text("Prediccion de la Temperatura \nInterior en una hora")
    opcion_pred = ['---------------------','Temperatura externa', 'Temperatura interna', 'Temperatura muro externa',
                'Temperatura muro interna', 'Humedad externa', 'Humedad interna']
    with colE:
        predice= st.selectbox(label='seleccione prediccion \na 60 minutos', options=opcion_pred)
        
    with colF:
        if predice:
            if predice == 'Temperatura externa':
                ruta_modelo='./reg_lineal_temp_EXT.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
        
            elif predice == 'Temperatura interna':
                ruta_modelo='./reg_lineal_temp_int.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
                
            elif predice == 'Temperatura muro externa':
                ruta_modelo='./reg_lineal_Temp_Muro_EXT.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
                
            elif predice == 'Temperatura muro interna':
                ruta_modelo='./reg_lineal_Temp_Muro_INT.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
                
            elif predice == 'Humedad externa':
                ruta_modelo='./reg_lineal_Hum_EXT.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} %".format(prediccion))
                
            elif predice == 'Humedad interna':
                ruta_modelo='./reg_lineal_Hum_INT.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} %".format(prediccion))
        
        
    # entrenamiento de modelos
with st.expander(label="Reentrenar modelo de regresion con datos actualizados"):
    eleccion = st.selectbox("Seleccione el objetivo del modelo predictor", options=opcion_pred)
    if eleccion:
        if eleccion == 'Temperatura externa':
            inicio = 4
            ruta_modelo = './reg_lineal_temp_EXT.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) # borramos los ultimos 4 registros ya que valen 0 por no tener prediccion
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)# entrenamos y guardamos el modelo
            st.info("Modelo actualizado correctamente")
            
        elif eleccion == 'Temperatura interna':
            inicio = 4
            ruta_modelo = './reg_lineal_temp_int.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Temperatura muro externa':
            inicio = 4
            ruta_modelo = './reg_lineal_Temp_Muro_EXT.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Temperatura muro interna':
            inicio = 4
            ruta_modelo = './reg_lineal_Temp_Muro_INT.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Humedad externa':
            inicio = 4
            ruta_modelo = './reg_lineal_Hum_EXT.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Humedad interna':
            inicio = 4
            ruta_modelo = './reg_lineal_Hum_INT.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.success("Modelo actualizado correctamente")
    
#endregion


st.subheader("Dataset original")
st.dataframe(df)
