import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import os
import squarify
import pydeck as pdk
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from io import BytesIO
import base64


# Título de la aplicación
st.title('Análisis Integral de Datos de los Juegos Olímpicos')

# Subtítulo y carga de datos de los Juegos Olímpicos
st.subheader('Visualización de Datos de los Juegos Olímpicos')
data_path = 'athlete_events.csv'

# Verificación si el archivo existe y carga de datos
if os.path.exists(data_path):
    data = pd.read_csv(data_path)
    st.write("Aquí se muestra el dataset cargado:")
    st.dataframe(data)
else:
    st.error(f"El archivo {data_path} no se encontró. Asegúrate de que esté en la ubicación correcta.")

# Limpieza de datos


# Verificación de la carga de datos
if data is None:
    st.error("El archivo 'athlete_events.csv' no se encontró. Asegúrate de que esté en la ubicación correcta.")
else:
    # Sidebar: Selección de opciones
    st.sidebar.title("Opciones de Visualización")
    option = st.sidebar.selectbox(
        '¿Qué datos te gustaría ver?',
        ('Introducción', 'Gráfico de Medallas', 'Heatmap de Correlación', 'Mapa de Medallas', 'Gráfico de Barras Apiladas', 'Número de Medallas por Año', 'Distribución de Medallas por Deporte y Año', 'Top 10 Deportes Más Frecuentes')
    )

    # Mostrar el dataframe cargado como introducción
    if option == 'Introducción':
        st.subheader('Datos Cargados')
        st.write(data.head())

    elif option == 'Gráfico de Medallas':
        st.subheader('Gráfico de Barras de Medallas')
        def create_medal_chart(data):
            # Primero filtramos para quedarnos solo con las filas que tienen medallas
            medal_data = data[data['Medal'] != 'No Medal']
            # Luego contamos las medallas por país (NOC)
            medal_counts = medal_data['NOC'].value_counts().reset_index()
            medal_counts.columns = ['NOC', 'Medal Count']
            # Ordenamos y nos quedamos con los primeros 5
            medal_counts = medal_counts.head(5)
            
            plt.figure(figsize=(10, 5))
            plt.bar(medal_counts['NOC'], medal_counts['Medal Count'], color='blue')
            plt.title('Total de Medallas Ganadas por los Primeros 5 Países')
            plt.xlabel('Comité Olímpico Nacional')
            plt.ylabel('Total de Medallas')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)
        # create_medal_chart(data)


    elif option == 'Heatmap de Correlación':
        st.subheader('Heatmap de Correlación de Atributos de Atletas')
        # create_heatmap(data)
        def create_heatmap(data):
            numeric_cols = data[['Age', 'Height', 'Weight']].dropna()
            correlation_matrix = numeric_cols.corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
            ax.set_title('Heatmap de Correlación de Atributos de Atletas')
            st.pyplot(fig)

    elif option == 'Mapa de Medallas':
        st.subheader('Mapa de Medallas por País')
        # create_map(data)

    elif option == 'Gráfico de Barras Apiladas':
        st.subheader('Gráfico de Barras Apiladas de Medallas')
        # create_stacked_bar_chart(data)

    elif option == 'Número de Medallas por Año':
        st.subheader('Número de Medallas Ganadas por Año')
        # create_medals_per_year_chart(data)

    elif option == 'Distribución de Medallas por Deporte y Año':
        st.subheader('Distribución de Medallas por Deporte y Año')
        # create_medals_by_sport_year_chart(data)

    elif option == 'Top 10 Deportes Más Frecuentes':
        st.subheader('Top 10 Deportes Más Frecuentes en los Juegos Olímpicos')
        # create_top_sports_chart(data)

# Asegúrate de definir las funciones necesarias para realizar las visualizaciones específicas.