import streamlit as st 
import pandas as pd
from consulta_db import Database
import mysql.connector
import matplotlib.pyplot as plt
from graficos import Grafico
from modelos import *
from scrap_web import Scrapero
import plotly.graph_objects as go
from scrapImagen import ScrapImagen
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
#resultado = database.ejecutar_consulta("SELECT * FROM sonda_brown")
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
path = 'https://www.delsuranalitica.online/esp-data.php'
# columnas de la tabla 
# ['ID', 'Sonda', 'fecha', 'Conductividad', 'TEMP_agua', 'TEMP_aire',
#       'HUM_AIRE', 'ALTURA', 'OBS_1', 'OBS_2']
data = scrap.scrapear(url=path)
df = data
df['fecha']=pd.to_datetime(df['fecha'])
# Convertir las columnas a tipo float
columnas = ['Conductividad', 'TEMP_agua', 'TEMP_aire','HUM_AIRE','ALTURA']
df[columnas] = df[columnas].apply(pd.to_numeric, errors='coerce')

print(df.columns)
##########################################################################
# endregion

# region caracteristicas de menu
caracteristicas= ['Conductividad', 'Temperatura agua', 'Temperatura aire',
                'Humedad aire', 'Altura']

columna= {'Conductividad':'Conductividad', 'Temperatura agua':'TEMP_agua', 
            'Temperatura aire':'TEMP_aire', 'Humedad aire':'HUM_AIRE','Altura':'ALTURA'}
# endregion
with st.sidebar:
    # region de seleccion de periodo de estudio
    with st.expander("Periodo de estudio"):
        selec=['Historico','Ultimas 24 horas', 'Ultimas 12 horas', 'Ultima hora']
        
        radioButton = st.radio(label='Periodo', options=selec, on_change=None)    
        if radioButton =='Historico':
            df=data
        elif radioButton == 'Ultimas 24 horas':
            df=data.head(1440)
        elif radioButton == 'Ultimas 12 horas':
            df=data.head(720)
        elif radioButton == 'Ultima hora':
            df=data.head(60)    
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


# region IMAGENES
with st.expander('Aqui puede seleccionar una imagen con dia y horario del arroyo'):  
# URL de la galería

    url = "https://cnclientes.online/gallery.php"

    # Crear una instancia de ScrapImagen
    scraper = ScrapImagen(url)

    # Obtener la lista de imágenes
    imagenes = scraper.obtener_imagenes()

    # Crear el menú desplegable para los días
    dias = list(imagenes.keys())
    dia_seleccionado = st.selectbox("Selecciona un día", dias)

    # Crear el menú desplegable para las horas según el día seleccionado
    if dia_seleccionado:
        horas = [hora for hora, _ in imagenes[dia_seleccionado]]
        hora_seleccionada = st.selectbox("Selecciona una hora", horas)

        # Mostrar la imagen seleccionada
        if hora_seleccionada:
            url_imagen = next(url for hora, url in imagenes[dia_seleccionado] if hora == hora_seleccionada)
            st.image(url_imagen, caption="Imagen seleccionada")
# endregion






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
        'Conductividad':'Conductividad %', 'TEMP_agua':'Tempetatura agua',
        'TEMP_aire':'Temperatura aire', 'HUM_AIRE':'Humedad aire',
        'ALTURA':'Altura'}
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
                st.pyplot(grafico.grafico_de_linea(df['fecha'],df[columna[var_1]],'Fecha',var_1,var_1))
                
            
        with col2:
                st.subheader(f"Grafica {opcion}")
                st.text(f'ha elegido la variable {var_2}')
                st.pyplot(grafico.grafico_de_linea(df['fecha'],df[columna[var_2]],'Fecha',var_2,var_2))

# region GRAFICO DE LINEAS 

with st.expander(" Grafico de lineas "):
    
    df_l = df[['fecha','Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']]

    # Crear figura de Plotly
    fig = go.Figure()
    # Añadir líneas al gráfico
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['Conductividad'], mode='lines', name='Conductividad'))
    # Configuración del diseño del gráfico
    fig.update_layout(
    title='Conductividad',
    xaxis_title='Fecha',
    yaxis_title='Porcentaje de conduccion',
    template='plotly_white'
    )
    
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)
        
    #-------------temperatura del agua---------------------
    # Crear figura de Plotly
    fig = go.Figure()
    # Añadir líneas al gráfico
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['TEMP_agua'], mode='lines', name='Temp. agua'))
    # Configuración del diseño del gráfico
    fig.update_layout(
    title='Temperatura del agua',
    xaxis_title='Fecha',
    yaxis_title='Grados centigrados',
    template='plotly_white'
    )
    
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    #-------------altura del arroyo---------------------
    # Crear figura de Plotly
    fig = go.Figure()
    # Añadir líneas al gráfico
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['ALTURA'], mode='lines', name='Altura'))
    # Configuración del diseño del gráfico
    fig.update_layout(
    title='Altura del arroyo',
    xaxis_title='Fecha',
    yaxis_title='Centimetros',
    template='plotly_white'
    )
    
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    #-------------temperatura del aire sobre el arroyo---------------------
    # Crear figura de Plotly
    fig = go.Figure()
    # Añadir líneas al gráfico
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['TEMP_aire'], mode='lines', name='Temp. aire'))
    # Configuración del diseño del gráfico
    fig.update_layout(
    title='Temperatura del aire',
    xaxis_title='Fecha',
    yaxis_title='Grados centigrados',
    template='plotly_white'
    )
    
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    #-------------humedad relativa del aire---------------------
    # Crear figura de Plotly
    fig = go.Figure()
    # Añadir líneas al gráfico
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['HUM_AIRE'], mode='lines', name='Humedad aire'))
    # Configuración del diseño del gráfico
    fig.update_layout(
    title='Humedad relativa del aire',
    xaxis_title='Fecha',
    yaxis_title='Porcentaje de humedad',
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
    st.markdown("Parametros actuales (ultima medicion) {}".format(df_ultimo['fecha']))
    
    colA,colB,colC = st.columns(3)
    with colA:
        st.text("Temperatura \nAgua : {} °C".format(df_ultimo['TEMP_agua']))
        st.text("Conductividad \nAgua : {} °C".format(df_ultimo['Conductividad']))
    with colB:
        st.text("Altura \nArroyo : {} °C".format(df_ultimo['ALTURA']))
        
    with colC:
        st.text("Temperatura \nAire : {} °C".format(df_ultimo['TEMP_aire']))
        st.text("Humedad \nAire : {} °C".format(df_ultimo['HUM_AIRE']))

    # conformacion del dataset para el entrenamiento
    lista= ['Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']
    reg_df = df[lista]
    df_ultimo = df_ultimo[lista] # del ultimo registro solo guardamos las columnas de interes
    # conformacion de la columna con los valores target
    reg_df['Prediccion'] = 0
    
    regresion = R_lineal() #creamos un objeto de regrasion lineal
    
    colE,colF=st.columns(2)
    
 
    
    #colE.text("Prediccion de la Temperatura \nInterior en una hora")
    opcion_pred = ['---------------------','Conductividad', 'Temperatura agua', 'Temperatura aire',
                'Humedad aire', 'Altura']
    with colE:
        predice= st.selectbox(label='seleccione prediccion \na 60 minutos', options=opcion_pred)
        
    with colF:
        if predice:
            if predice == 'Conductividad':
                ruta_modelo='./reg_lineal_Conductividad.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
        
            elif predice == 'Temperatura agua':
                ruta_modelo='./reg_lineal_temp_agua.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
                
            elif predice == 'Temperatura aire':
                ruta_modelo='./reg_lineal_Temp_aire.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
                
            elif predice == 'Humedad aire':
                ruta_modelo='./reg_lineal_Hum_aire.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} °C".format(prediccion))
                
            elif predice == 'Altura':
                ruta_modelo='./reg_lineal_Altura.pkl'
                prediccion= regresion.predecir(df_ultimo, ruta_modelo)
                colF.text('PREDICCION')
                colF.text("{} %".format(prediccion))
                

        
        
    # entrenamiento de modelos
    #opcion_pred = ['---------------------','Conductividad', 'Temperatura agua', 'Temperatura aire',
    #            'Humedad aire', 'Altura']
with st.expander(label="Reentrenar modelo de regresion con datos actualizados"):
    eleccion = st.selectbox("Seleccione el objetivo del modelo predictor", options=opcion_pred)
    if eleccion:
        if eleccion == 'Conductividad':
            inicio = 4
            ruta_modelo = './reg_lineal_Conductividad.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) # borramos los ultimos 4 registros ya que valen 0 por no tener prediccion
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)# entrenamos y guardamos el modelo
            st.info("Modelo actualizado correctamente")
            
        elif eleccion == 'Temperatura agua':
            inicio = 4
            ruta_modelo = './reg_lineal_temp_agua.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Temperatura aire':
            inicio = 4
            ruta_modelo = './reg_lineal_Temp_aire.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Humedad aire':
            inicio = 4
            ruta_modelo = './reg_lineal_Hum_aire.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        elif eleccion == 'Altura':
            inicio = 4
            ruta_modelo = './reg_lineal_Altura.pkl'
            n_reg_df = reg_df
            for index, row in n_reg_df.iloc[inicio:].iterrows():
                n_reg_df.at[index, 'Prediccion']= n_reg_df.at[index - 4, columna[eleccion]]
            n_reg_df = n_reg_df.drop(reg_df.index[:4]) 
            regresion.entrenar_y_guardar(n_reg_df,ruta_modelo)
            st.info("Modelo actualizado correctamente")
        
        
    
#endregion

# region EVALUACION DEL MODELO POR CADA VARIABLE
with st.expander(label="Evaluacion del modelo, comparativa del valor real y su prediccion"):
    compara = st.selectbox(label="Elija la el parametro que desea evaluar", options=opcion_pred)
    #opcion_pred = ['---------------------','Conductividad', 'Temperatura agua', 'Temperatura aire',
    #            'Humedad aire', 'Altura']
    
    if compara:
        if compara == 'Conductividad':
            ponderar = pd.DataFrame(columns=['fecha','real','prediccion'])
            lista= ['Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']
            reg_df = df[lista]
            rango = len(df)-4
            ruta = './reg_lineal_Conductividad.pkl'
            for i in range(rango):
                a=regresion.predecir(reg_df.iloc[i+4],ruta_modelo=ruta)
                a = float(a[0])
                
                ponderar = ponderar.append({'fecha':df.iloc[i]['fecha'],'real':df.iloc[i]['Conductividad'],'prediccion':a}, ignore_index=True)
            #--------------GRAFICAR EL DATAFRAME-------------------------
            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir líneas al gráfico
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['real'], mode='lines', name='real'))
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['prediccion'], mode='lines', name='prediccion'))
                                    
            # Configuración del diseño del gráfico
            fig.update_layout(
            title='Gráfico de conductividad',
            xaxis_title='Fecha',
            yaxis_title='Porcentaje de conductividad',
            template='plotly_white'
            )
        
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)
            
            
                
        elif compara == 'Temperatura agua':
            ponderar = pd.DataFrame(columns=['fecha','real','prediccion'])
            lista= ['Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']
            reg_df = df[lista]
            rango = len(df)-4
            ruta = './reg_lineal_temp_agua.pkl'
            for i in range(rango):
                a=regresion.predecir(reg_df.iloc[i+4],ruta_modelo=ruta)
                a = float(a[0])
                
                ponderar = ponderar.append({'fecha':df.iloc[i]['fecha'],'real':df.iloc[i]['TEMP_agua'],'prediccion':a}, ignore_index=True)
            #--------------GRAFICAR EL DATAFRAME-------------------------
            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir líneas al gráfico
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['real'], mode='lines', name='real'))
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['prediccion'], mode='lines', name='prediccion'))
                                    
            # Configuración del diseño del gráfico
            fig.update_layout(
            title='Gráfico de temperatura de agua',
            xaxis_title='Fecha',
            yaxis_title='Grados centigrados',
            template='plotly_white'
            )
        
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)
        elif compara == 'Temperatura aire':
            ponderar = pd.DataFrame(columns=['fecha','real','prediccion'])
            lista= ['Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']
            reg_df = df[lista]
            rango = len(df)-4
            ruta = './reg_lineal_Temp_aire.pkl'
            for i in range(rango):
                a=regresion.predecir(reg_df.iloc[i+4],ruta_modelo=ruta)
                a = float(a[0])
                
                ponderar = ponderar.append({'fecha':df.iloc[i]['fecha'],'real':df.iloc[i]['TEMP_aire'],'prediccion':a}, ignore_index=True)
            #--------------GRAFICAR EL DATAFRAME-------------------------
            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir líneas al gráfico
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['real'], mode='lines', name='real'))
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['prediccion'], mode='lines', name='prediccion'))
                                    
            # Configuración del diseño del gráfico
            fig.update_layout(
            title='Gráfico de Temperatura de aire',
            xaxis_title='Fecha',
            yaxis_title='Grados centigrados',
            template='plotly_white'
            )
        
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)     
            
        elif compara == 'Humedad aire':
            ponderar = pd.DataFrame(columns=['fecha','real','prediccion'])
            lista= ['Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']
            reg_df = df[lista]
            rango = len(df)-4
            ruta = './reg_lineal_Hum_aire.pkl'
            for i in range(rango):
                a=regresion.predecir(reg_df.iloc[i+4],ruta_modelo=ruta)
                a = float(a[0])
                
                ponderar = ponderar.append({'fecha':df.iloc[i]['fecha'],'real':df.iloc[i]['HUM_AIRE'],'prediccion':a}, ignore_index=True)
            #--------------GRAFICAR EL DATAFRAME-------------------------
            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir líneas al gráfico
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['real'], mode='lines', name='real'))
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['prediccion'], mode='lines', name='prediccion'))
                                    
            # Configuración del diseño del gráfico
            fig.update_layout(
            title='Gráfico de Humedad de aire',
            xaxis_title='Fecha',
            yaxis_title='Porcentaje de humedad',
            template='plotly_white'
            )
        
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)    
            
        elif compara == 'Altura':
            ponderar = pd.DataFrame(columns=['fecha','real','prediccion'])
            lista= ['Conductividad','TEMP_agua','TEMP_aire','HUM_AIRE','ALTURA']
            reg_df = df[lista]
            rango = len(df)-4
            ruta = './reg_lineal_Altura.pkl'
            for i in range(rango):
                a=regresion.predecir(reg_df.iloc[i+4],ruta_modelo=ruta)
                a = float(a[0])
                
                ponderar = ponderar.append({'fecha':df.iloc[i]['fecha'],'real':df.iloc[i]['ALTURA'],'prediccion':a}, ignore_index=True)
            #--------------GRAFICAR EL DATAFRAME-------------------------
            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir líneas al gráfico
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['real'], mode='lines', name='real'))
            fig.add_trace(go.Scatter(x=ponderar['fecha'], y=ponderar['prediccion'], mode='lines', name='prediccion'))
                                    
            # Configuración del diseño del gráfico
            fig.update_layout(
            title='Gráfico de Altura',
            xaxis_title='Fecha',
            yaxis_title='Centimetros',
            template='plotly_white'
            )
        
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)
            
        
    
    
    
    
    
    
# endregion   
    
st.subheader("Dataset original")
st.dataframe(df)
