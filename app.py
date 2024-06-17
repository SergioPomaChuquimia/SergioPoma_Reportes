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


# Función para crear un gráfico de barras de las medallas
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


# Función para crear un heatmap de correlación de atributos de los atletas
def create_heatmap(data):
    numeric_cols = data[['Age', 'Height', 'Weight']].dropna()
    correlation_matrix = numeric_cols.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
    ax.set_title('Heatmap de Correlación de Atributos de Atletas')
    st.pyplot(fig)

# Función para crear un mapa de las medallas por país
def create_map(data):
    country_medals = data[data['Medal'] != 'No Medal'].groupby('NOC').size().reset_index(name='Total Medals')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world.rename(columns={'iso_a3': 'NOC'})
    world_map = world.merge(country_medals, on='NOC', how='left')

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world_map.boundary.plot(ax=ax, linewidth=1)
    world_map.dropna().plot(ax=ax, column='Total Medals', cmap='OrRd', legend=True,
                         legend_kwds={'label': "Total de Medallas por País"},
                         missing_kwds={'color': 'lightgrey'})
    plt.title('Distribución de Medallas por País')
    st.pyplot(fig)

# Función para crear un gráfico de barras apiladas de medallas
def create_stacked_bar_chart(data):
    top_countries = data[data['Medal'] != 'No Medal'].groupby(['NOC', 'Medal']).size().unstack(fill_value=0).sort_values('Gold', ascending=False).head(5)
    top_countries[['Gold', 'Silver', 'Bronze']].plot(kind='bar', stacked=True, color=['gold', 'silver', '#cd7f32'])
    plt.title('Distribución de Medallas para los Top 5 Países')
    plt.xlabel('Países')
    plt.ylabel('Número de Medallas')
    plt.xticks(rotation=45)
    plt.legend(title='Tipo de Medalla')
    st.pyplot(plt)

# Cargar datos para la generación de visualizaciones
if 'data' in locals():
    st.subheader('Gráfico de Barras de Medallas')
    create_medal_chart(data)

    st.subheader('Heatmap de Correlación de Atributos de Atletas')
    create_heatmap(data)

    st.subheader('Mapa de Medallas por País')
    create_map(data)

    st.subheader('Gráfico de Barras Apiladas de Medallas')
    create_stacked_bar_chart(data)

else:
    st.error("No se ha cargado el dataset de los Juegos Olímpicos para la generación de las visualizaciones.")


# Verificación si el archivo existe y carga de datos
if os.path.exists(data_path):
    data = pd.read_csv(data_path)
    st.write("Aquí se muestra el dataset cargado:")
    st.dataframe(data.head())

    # Limpieza de datos
    data['Medal'] = data['Medal'].fillna('No Medal')

    # Crear y mostrar el gráfico de serie temporal de medallas por año
    st.subheader('Número de Medallas Ganadas por Año')
    medal_data = data.dropna(subset=['Medal'])
    medals_per_year = medal_data.groupby('Year')['Medal'].count()
    plt.figure(figsize=(10, 5))
    plt.plot(medals_per_year.index, medals_per_year.values, marker='o', linestyle='-', color='b')
    plt.title('Número de Medallas Ganadas por Año')
    plt.xlabel('Año')
    plt.ylabel('Cantidad de Medallas')
    plt.grid(True)
    st.pyplot(plt)  # Usar st.pyplot para mostrar el gráfico en Streamlit
else:
    st.error(f"El archivo {data_path} no se encontró. Asegúrate de que esté en la ubicación correcta.")


if os.path.exists(data_path):
    data = pd.read_csv(data_path)
    st.write("Aquí se muestra el dataset cargado:")
    st.dataframe(data.head())

    # Opción para seleccionar deportes
    all_sports = data['Sport'].unique()
    selected_sports = st.multiselect('Seleccione hasta 10 deportes:', all_sports, help="Puedes seleccionar hasta 10 deportes.")

    # Limitar a 10 deportes máximo
    if len(selected_sports) > 10:
        st.error('Por favor selecciona un máximo de 10 deportes.')
    else:
        # Filtrar los datos por los deportes seleccionados
        data_filtered = data[data['Sport'].isin(selected_sports) & data['Medal'].notna()]

        # Agrupar datos por Año y Deporte, contar las medallas
        grouped = data_filtered.groupby(['Year', 'Sport']).size().reset_index(name='Medals')
        grouped['Sport_Code'] = pd.factorize(grouped['Sport'])[0]  # Codificar los deportes para el eje y

        # Crear el gráfico de burbujas
        fig, ax = plt.subplots(figsize=(14, 8))
        bubble = ax.scatter(grouped['Year'], grouped['Sport_Code'], s=grouped['Medals']*10, alpha=0.5)
        
        ax.set_xlabel('Año')
        ax.set_ylabel('Deporte')
        ax.set_title('Distribución de Medallas por Deporte y Año')
        ax.grid(True)

        # Crear etiquetas para los deportes en el eje y
        plt.yticks(range(len(grouped['Sport'].unique())), grouped['Sport'].unique())

        plt.colorbar(bubble, label='Cantidad de Medallas')
        
        st.pyplot(fig)  # Mostrar el gráfico en Streamlit
else:
    st.error(f"El archivo {data_path} no se encontró. Asegúrate de que esté en la ubicación correcta.")


if os.path.exists(data_path):
    data = pd.read_csv(data_path)
    st.write("Aquí se muestra el dataset cargado:")
    st.dataframe(data.head())

    # Agrupar los datos por deporte y contar las entradas
    sport_counts = data['Sport'].value_counts().head(10)  # Top 10 deportes más frecuentes

    # Crear un gráfico de barras horizontal
    plt.figure(figsize=(10, 8))
    plt.barh(sport_counts.index, sport_counts.values, color='skyblue')
    plt.xlabel('Número de Eventos')
    plt.title('Top 10 Deportes Más Frecuentes en los Juegos Olímpicos')
    plt.gca().invert_yaxis()  # Invertir el eje y para que el deporte con más eventos esté arriba
    st.pyplot(plt)  # Mostrar el gráfico en Streamlit
else:
    st.error(f"El archivo {data_path} no se encontró. Asegúrate de que esté en la ubicación correcta.")  

data = pd.read_csv(data_path)

# Preprocesamiento de los datos
data = data.dropna(subset=['Team', 'NOC', 'Year', 'Sex'])  # Asegurarse de que los datos necesarios estén completos

# Selector de año
year = st.slider('Seleccione el año', int(data['Year'].min()), int(data['Year'].max()), step=4)  # Juegos Olímpicos cada 4 años
data = data[data['Year'] == year]

# Supongamos que tenemos coordenadas para cada NOC (esto es un ejemplo)
noc_coords = pd.DataFrame({
    'NOC': ['USA', 'CHN', 'DEN', 'NED'],
    'latitude': [37.0902, 35.8617, 56.2639, 52.1326],
    'longitude': [-95.7129, 104.1954, 9.5018, 5.2913]
})

data = data.merge(noc_coords, on='NOC', how='left')

# Contar participantes por país, año y género
count_data = data.groupby(['Team', 'latitude', 'longitude', 'Sex']).size().reset_index(name='Participants')

# Crear el mapa
m = folium.Map(location=[20, 0], zoom_start=2)

# Agregar marcadores con gráficos de torta
for location, group in count_data.groupby(['latitude', 'longitude']):
    fig, ax = plt.subplots(figsize=(1, 1))
    # Asegúrate de que ambos géneros estén presentes en el grupo
    group_pivot = group.pivot(index='Team', columns='Sex', values='Participants').fillna(0)
    ax.pie(group_pivot.sum(), labels=group_pivot.columns, colors=['blue', 'red'])
    # Guardar el gráfico como un objeto de bytes en memoria
    pie_io = BytesIO()
    plt.savefig(pie_io, format='png', bbox_inches='tight', pad_inches=0)
    pie_io.seek(0)
    base64_png = base64.b64encode(pie_io.read()).decode('utf-8')
    iframe = folium.IFrame(f'<img src="data:image/png;base64,{base64_png}">', width=100, height=100)
    popup = folium.Popup(iframe, max_width=300)
    folium.Marker(location, popup=popup).add_to(m)

# Mostrar el mapa en Streamlit
folium_static(m)