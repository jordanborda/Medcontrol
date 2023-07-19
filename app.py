import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import networkx as nx
from pyvis.network import Network
import json
import requests
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import OrdinalEncoder

st.set_page_config(layout="wide")
locations_lima = [
    {'city': 'Lima', 'latitude': -12.0464, 'longitude': -77.0428},
    {'city': 'San Isidro', 'latitude': -12.0989, 'longitude': -77.0365},
    {'city': 'Miraflores', 'latitude': -12.1111, 'longitude': -77.0301},
    {'city': 'Barranco', 'latitude': -12.1409, 'longitude': -77.0208},
    {'city': 'La Molina', 'latitude': -12.0761, 'longitude': -76.9647},
    {'city': 'San Miguel', 'latitude': -12.0775, 'longitude': -77.0802},
    {'city': 'Santiago de Surco', 'latitude': -12.1251, 'longitude': -76.9988},
    {'city': 'San Borja', 'latitude': -12.0892, 'longitude': -76.9976},
    ]

locations_provinces = [
        {'city': 'Arequipa', 'latitude': -16.4090, 'longitude': -71.5375},
        {'city': 'Trujillo', 'latitude': -8.1092, 'longitude': -79.0215},
        {'city': 'Cusco', 'latitude': -13.5319, 'longitude': -71.9673},
        {'city': 'Piura', 'latitude': -5.1945, 'longitude': -80.6328},
        {'city': 'Iquitos', 'latitude': -3.7437, 'longitude': -73.2516},
        {'city': 'Chiclayo', 'latitude': -6.7766, 'longitude': -79.8443},
        {'city': 'Huancayo', 'latitude': -12.0672, 'longitude': -75.2045},
        {'city': 'Tacna', 'latitude': -18.0056, 'longitude': -70.2463},
    ]




def create_marker_map(locations_lima, locations_provinces, data):
    m = folium.Map(location=[-9.189967, -75.015152], zoom_start=6)

    marker_cluster_lima = MarkerCluster().add_to(m)
    marker_cluster_provinces = MarkerCluster().add_to(m)

    for location in locations_lima:
        city_data = data[data['ubicacion_geografica'] == location['city']]
        for _, patient in city_data.iterrows():
            folium.Marker(
                location=[location['latitude'], location['longitude']],
                popup=f"Paciente ID: {patient['id_paciente']}",
                icon=None,
            ).add_to(marker_cluster_lima)

    for location in locations_provinces:
        city_data = data[data['ubicacion_geografica'] == location['city']]
        for _, patient in city_data.iterrows():
            folium.Marker(
                location=[location['latitude'], location['longitude']],
                popup=f"Paciente ID: {patient['id_paciente']}",
                icon=None,
            ).add_to(marker_cluster_provinces)

    # Guardar el mapa en un archivo HTML
    m.save("marker_map.html")

def sankey_chart(data):
    source = data['diagnosticos_previos'].value_counts().index.tolist()
    target = data['tratamientos_ant'].value_counts().index.tolist()
    label = source + target

    source_indices = data['diagnosticos_previos'].apply(lambda x: source.index(x))
    target_indices = data['tratamientos_ant'].apply(lambda x: target.index(x) + len(source))
    value_counts = data.groupby([source_indices, target_indices]).size().reset_index(name='value')

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=label,
            color="blue"
        ),
        link=dict(
            source=value_counts[source_indices.name].values,
            target=value_counts[target_indices.name].values,
            value=value_counts['value'].values
        )
    ))

    fig.update_layout(title_text="Diagnósticos previos a tipos de tratamiento", font_size=10)
    st.plotly_chart(fig)

def load_geojson_data(url):
    response = requests.get(url)
    return json.loads(response.text)

def choropleth_map(data, geojson_data):
    # Contar el número de pacientes por ciudad
    city_counts = data['ubicacion_geografica'].value_counts().reset_index()
    city_counts.columns = ['city', 'count']

    # Crear el mapa coroplético
    fig = px.choropleth(city_counts,
                        geojson=geojson_data,
                        locations='city',
                        featureidkey='properties.name',
                        color='count',
                        color_continuous_scale="Viridis",
                        labels={'count': 'Número de pacientes'},
                        title="Pacientes por ciudad")
    fig.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig)




def main():

    st.sidebar.image('logo.png')
    uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type="csv")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        tophead=data.head(100)
        # Crear paneles
        panel = st.sidebar.radio("Selecciona un panel:", ["Información general", "Análisis financiero", "Análisis de calidad"])

        if panel == "Información general":
            # Código para generar gráficos y mostrar información en el panel "Información general"
            st.header("Información general")
            st.subheader("Registros")
            st.dataframe(tophead)
            col1, col2 = st.columns(2)
            col1.metric("Pacientes esta semana", "426", "-2%")
            col2.metric("Pacientes este mes", "1710", "+8%")
            selected_columns = st.multiselect("Selecciona las columnas que deseas visualizar", data.columns)
            if len(selected_columns) > 0:
                st.dataframe(data[selected_columns])

            st.header("Buscar paciente por ID")
            patient_id = st.text_input("Introduce el ID del paciente", "")
            if patient_id != "":
                try:
                    patient_data = data[data['id_paciente'] == int(patient_id)]
                    if len(patient_data) > 0:
                        st.write("Datos del paciente con ID:", patient_id)
                        st.dataframe(patient_data)
                    else:
                        st.warning("No se encontró un paciente con el ID proporcionado.")
                except ValueError:
                    st.warning("Por favor, introduce un ID de paciente válido (número entero).")


            # Crear el mapa con marcadores
            create_marker_map(locations_lima, locations_provinces, data)

            # Incrustar el archivo HTML en Streamlit
            with open("marker_map.html", "r") as f:
                html_string = f.read()
            components.html(html_string, width=900, height=600)
            
            
            co1, co2 = st.columns(2,gap='small')
            
            with co1:
                # Gráfico de dispersión con ubicación geográfica de pacientes
                scatter_plot = px.scatter(
                    data,
                    x="latitud",
                    y="longitud",
                    color="genero",
                    hover_data=["ubicacion_geografica", "nivel_socioeconomico"],
                    title="Ubicación geográfica de pacientes por género",
                    color_discrete_sequence=["red", "blue"],
                )
                st.plotly_chart(scatter_plot)

                st.header("Pacientes por raza y género en cada centro de salud")
                race_filter = st.multiselect('Selecciona las razas a mostrar:', data['raza'].unique())
                if not race_filter:
                    race_filter = data['raza'].unique()

                stacked_bar = data[data['raza'].isin(race_filter)].groupby(['id_centro_salud', 'raza', 'genero']).size().unstack().reset_index().melt(id_vars=['id_centro_salud', 'raza'])
                stacked_bar_fig = px.bar(stacked_bar, x='id_centro_salud', y='value', color='genero', text='value', facet_col='raza', labels={'id_centro_salud': 'Centro de salud', 'value': 'Cantidad de pacientes'}, title="Cantidad de pacientes por raza y género en cada centro de salud")
                st.plotly_chart(stacked_bar_fig)

                # Gráfico de caja - Comparación de edad de pacientes según tipo de tratamiento y género
                    
                st.header("Comparación de edad de pacientes según tipo de tratamiento y género")
                treatment_filter = st.multiselect('Selecciona los tratamientos a mostrar:', data['procedimientos_realizados'].unique())
                if not treatment_filter:
                    treatment_filter = data['procedimientos_realizados'].unique()

                box_plot = px.box(
                    data[data["procedimientos_realizados"].isin(treatment_filter)],
                    x="procedimientos_realizados",
                    y="edad",
                    color="genero",
                    hover_data=["id_centro_salud"],
                    title="Comparación de edad de pacientes por tipo de tratamiento y género",
                    color_discrete_sequence=["red", "blue"],
                )
                st.plotly_chart(box_plot)


                # ...
                # Gráfico de densidad - Distribución de duración de visitas y facturación según el tipo de tratamiento o el centro de salud
                kde_plot1 = px.histogram(
                    data,
                    x="duracion_visita",
                    color="procedimientos_realizados",
                    marginal="violin",
                    nbins=50,
                    title="Distribución de duración de visitas por tipo de tratamiento",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                st.plotly_chart(kde_plot1)

                bar_chart = px.bar(data, x='id_centro_salud', y=['tasas_mortalidad', 'tasas_morbilidad'], title='Tasas de mortalidad y morbilidad por centro de salud')
                st.plotly_chart(bar_chart)

                bar_chart = px.bar(data, x='tipo_tratamiento', y='seguimiento_enfermedad', color='genero', title='Seguimiento de enfermedades por tipo de tratamiento y género')
                st.plotly_chart(bar_chart)

                stacked_bar = data.groupby(['id_centro_salud', 'nivel_socioeconomico', 'genero']).size().unstack().reset_index().melt(id_vars=['id_centro_salud', 'nivel_socioeconomico'])
                stacked_bar_fig = px.bar(stacked_bar, x='id_centro_salud', y='value', color='genero', text='value', facet_col='nivel_socioeconomico', labels={'id_centro_salud': 'Centro de salud', 'value': 'Cantidad de pacientes'}, title="Cantidad de pacientes por nivel socioeconómico y género en cada centro de salud")
                st.plotly_chart(stacked_bar_fig)

                avg_costs = data.groupby('id_centro_salud').agg({'costo_tratamiento': 'mean', 'costos_operacion': 'mean'}).reset_index()
                bar_chart = px.bar(avg_costs, x='id_centro_salud', y=['costo_tratamiento', 'costos_operacion'], title='Promedio de costos de tratamiento y costos de operación por centro de salud')
                st.plotly_chart(bar_chart)

                bar_chart = px.bar(data.groupby(['raza', 'genero']).agg({'eventos_adversos': 'sum', 'reclamaciones_responsabilidad_medica': 'sum'}).reset_index(), x='raza', y=['eventos_adversos', 'reclamaciones_responsabilidad_medica'], color='genero', facet_col='genero', title='Eventos adversos y reclamaciones de responsabilidad médica por raza y género')
                st.plotly_chart(bar_chart)

                treatment_cost_comparison_chart = px.box(
                    data,
                    x="id_centro_salud",
                    y="costo_tratamiento",
                    title="Comparación de los costos de tratamiento por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "costo_tratamiento": "Costo del tratamiento"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(treatment_cost_comparison_chart)


                operation_cost_comparison_chart = px.bar(
                    data,
                    x="id_centro_salud",
                    y="costos_operacion",
                    title="Comparación de costos de operación por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "costos_operacion": "Costos de operación"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(operation_cost_comparison_chart)

            with co2:



                #Análisis de costos

                cost_analysis_chart = px.box(
                data,
                x="id_centro_salud",
                y="costo_tratamiento",
                points="all",
                title="Análisis de costos por centro de salud",
                color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(cost_analysis_chart)


                #Análisis de tiempo
                data["fecha_visita"] = pd.to_datetime(data["fecha_visita"]) # Convierte la columna a tipo de fecha
                time_analysis_chart = px.line(
                data,
                x="fecha_visita",
                y="duracion_visita",
                title="Tendencias temporales en visitas de seguimiento",
                color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(time_analysis_chart)


                chronic_disease_counts = data['enfermedades_cronicas'].value_counts()
                bar_chart = px.bar(chronic_disease_counts, x=chronic_disease_counts.index, y='enfermedades_cronicas', title='Enfermedades crónicas más comunes')
                st.plotly_chart(bar_chart)


                box_plot = px.box(data, x='tipo_tratamiento', y='duracion_visita', color='genero', title='Duración de visitas por tipo de tratamiento y género')
                st.plotly_chart(box_plot)


                medications_by_treatment = data.groupby(['tipo_tratamiento', 'medicamentos_recetados']).size().unstack().reset_index().melt(id_vars=['tipo_tratamiento'])
                stacked_bar_chart = px.bar(medications_by_treatment, x='tipo_tratamiento', y='value', color='medicamentos_recetados', title='Medicamentos recetados por tipo de tratamiento')
                st.plotly_chart(stacked_bar_chart)


                violin_plot = px.violin(data, x='tipo_tratamiento', y='duracion_visita', color='genero', box=True, points="all", title='Distribución de duración de visitas por tipo de tratamiento y género')
                st.plotly_chart(violin_plot)

                # Gráfico de violín - Distribución de la satisfacción del paciente según el tipo de tratamiento, género y nivel socioeconómico
                violin_plot1 = px.violin(
                    data,
                    x="tipo_tratamiento",
                    y="satisfaccion_paciente",
                    box=True,
                    points="all",
                    color="genero",
                    title="Distribución de la satisfacción del paciente por tipo de tratamiento y género",
                    color_discrete_sequence=["red", "blue"],
                )
                st.plotly_chart(violin_plot1)

                violin_plot2 = px.violin(
                    data,
                    x="nivel_socioeconomico",
                    y="satisfaccion_paciente",
                    box=True,
                    points="all",
                    color="genero",
                    title="Distribución de la satisfacción del paciente por nivel socioeconómico y género",
                    color_discrete_sequence=["red", "blue"],
                )
                st.plotly_chart(violin_plot2)

                socioeconomic_counts = data['nivel_socioeconomico'].value_counts()
                pie_chart = px.pie(socioeconomic_counts, values='nivel_socioeconomico', names=socioeconomic_counts.index, title='Distribución de pacientes por nivel socioeconómico')
                st.plotly_chart(pie_chart)

                language_counts = data['idioma'].value_counts()
                pie_chart = px.pie(language_counts, values='idioma', names=language_counts.index, title='Distribución de pacientes por idioma')
                st.plotly_chart(pie_chart)

                #Gráfico de pastel - Distribución de pacientes por tipo de tratamiento
                treatment_counts = data['tipo_tratamiento'].value_counts()
                pie_chart = px.pie(
                treatment_counts,
                values='tipo_tratamiento',
                names=treatment_counts.index,
                title='Distribución de pacientes por tipo de tratamiento',
                color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(pie_chart)
                
                density_map = px.density_mapbox(data, lat='latitud', lon='longitud', z='id_paciente', radius=10, zoom=5, mapbox_style='carto-positron', title='Densidad de pacientes por ubicación geográfica')
                st.plotly_chart(density_map)
        elif panel == "Análisis financiero":
            # Código para generar gráficos y mostrar información en el panel "Análisis financiero"
            st.header("Análisis financiero")

            fin1,fin2=st.columns(2)
            with fin1:

                kde_plot2 = px.histogram(
                data,
                x="facturacion",
                color="id_centro_salud",
                marginal="violin",
                nbins=50,
                title="Distribución de facturación por centro de salud",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                st.plotly_chart(kde_plot2)

                scatter_plot = px.scatter(data, x='facturacion', y='costo_tratamiento', title='Relación entre facturación y costo del tratamiento')
                st.plotly_chart(scatter_plot)

                avg_cost_chart = px.bar(
                data.groupby("id_centro_salud")["costo_tratamiento"].mean().reset_index(),
                x="id_centro_salud",
                y="costo_tratamiento",
                title="Costo promedio del tratamiento por centro de salud",
                labels={"id_centro_salud": "Centro de salud", "costo_tratamiento": "Costo promedio"}
                )
                st.plotly_chart(avg_cost_chart)


                scatter_cost_success = px.scatter(
                    data,
                    x="costo_tratamiento",
                    y="tasa_exito_tratamiento",
                    color="id_centro_salud",
                    title="Relación entre costo del tratamiento y tasa de éxito",
                    labels={"costo_tratamiento": "Costo del tratamiento", "tasa_exito_tratamiento": "Tasa de éxito"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(scatter_cost_success)

                data['porcentaje_cubierto'] = (data['pago_seguros'] / data['facturacion']) * 100
                insurance_coverage_chart = px.histogram(
                    data,
                    x="id_centro_salud",
                    y="porcentaje_cubierto",
                    histfunc="avg",
                    title="Porcentaje promedio de facturación cubierta por seguros por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "porcentaje_cubierto": "Porcentaje cubierto"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(insurance_coverage_chart)

                operation_cost_chart = px.bar(
                    data.groupby("id_centro_salud")["costos_operacion"].mean().reset_index(),
                    x="id_centro_salud",
                    y="costos_operacion",
                    title="Comparación de costos de operación por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "costos_operacion": "Costo de operación"}
                )
                st.plotly_chart(operation_cost_chart)

            with fin2:
                billing_revenue_chart = px.bar(
                    data.groupby("procedimientos_realizados")["facturacion"].sum().reset_index(),
                    x="procedimientos_realizados",
                    y="facturacion",
                    title="Ingresos por facturación según el tipo de tratamiento",
                    labels={"procedimiento realizado": "Tipo de tratamiento", "facturacion": "Ingresos por facturación"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(billing_revenue_chart)

                insurance_payments_chart = px.bar(
                    data.groupby("procedimientos_realizados")["pago_seguros"].sum().reset_index(),
                    x="procedimientos_realizados",
                    y="pago_seguros",
                    title="Pagos de seguros según el tipo de tratamiento",
                    labels={"procedimiento realizado": "Tipo de tratamiento", "pago_seguros": "Pagos de seguros"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(insurance_payments_chart)




        elif panel == "Análisis de calidad":
            # Código para generar gráficos y mostrar información en el panel "Análisis de calidad"
            st.header("Análisis de calidad")
            cal1,cal2 =st.columns(2)
            with cal1:
                #Gráfico de radar - Comparación de indicadores de desempeño por tipo de tratamiento
                categories = ['satisfaccion_paciente', 'tasas_mortalidad', 'tasas_morbilidad', 'tasa_exito_tratamiento']
                treatment_types = data['tipo_tratamiento'].unique()

                fig = go.Figure()

                for treatment in treatment_types:
                    treatment_data = data[data['tipo_tratamiento'] == treatment]
                    values = [treatment_data[col].mean() for col in categories]
                    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=treatment))

                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, title="Comparación de indicadores de desempeño por tipo de tratamiento")
                    st.plotly_chart(fig)       

                #Comparación de centros de salud
                
                center_comparison_chart = px.bar(
                data,
                x="id_centro_salud",
                y="tasa_exito_tratamiento",
                text="tasa_exito_tratamiento",
                title="Comparación de centros de salud por tasa de éxito en tratamientos",
                color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(center_comparison_chart)


                scatter_3d = px.scatter_3d(data, x='costo_tratamiento', y='tasa_exito_tratamiento', z='satisfaccion_paciente', color='id_centro_salud', symbol='genero', title='Relación entre costos de tratamiento, tasas de éxito y satisfacción del paciente')
                st.plotly_chart(scatter_3d)

                data['fecha_visita'] = pd.to_datetime(data['fecha_visita'])
                trend_data = data.groupby('fecha_visita').agg({'ensayos_clinicos': 'sum', 'publicaciones_cientificas': 'sum', 'descubrimientos_medicos': 'sum'}).reset_index()
                trend_plot = px.line(trend_data, x='fecha_visita', y=['ensayos_clinicos', 'publicaciones_cientificas', 'descubrimientos_medicos'], title='Tendencias en ensayos clínicos, publicaciones científicas y descubrimientos médicos')
                st.plotly_chart(trend_plot)

                trend_data = data.groupby('fecha_visita').agg({'eventos_adversos': 'sum', 'reclamaciones_responsabilidad_medica': 'sum'}).reset_index()
                trend_plot = px.line(trend_data, x='fecha_visita', y=['eventos_adversos', 'reclamaciones_responsabilidad_medica'], title='Tendencias en eventos adversos y reclamaciones de responsabilidad médica')
                st.plotly_chart(trend_plot)

            with cal2:
                scatter_plot = px.scatter(data, x='satisfaccion_paciente', y='seguridad_paciente', title='Relación entre satisfacción del paciente y seguridad del paciente')
                st.plotly_chart(scatter_plot)

                treatment_success_rate_chart = px.bar(
                    data.groupby("tipo_tratamiento")["tasa_exito_tratamiento"].mean().reset_index(),
                    x="tipo_tratamiento",
                    y="tasa_exito_tratamiento",
                    title="Tasa de éxito del tratamiento por tipo de tratamiento",
                    labels={"tipo_tratamiento": "Tipo de tratamiento", "tasa_exito_tratamiento": "Tasa de éxito"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(treatment_success_rate_chart)

                patient_satisfaction_chart = px.bar(
                    data,
                    x="id_centro_salud",
                    y="satisfaccion_paciente",
                    title="Índice de satisfacción del paciente por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "satisfaccion_paciente": "Satisfacción del paciente"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(patient_satisfaction_chart)

                morbidity_rate_chart = px.bar(
                    data,
                    x="id_centro_salud",
                    y="tasas_morbilidad",
                    title="Tasas de morbilidad por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "tasas_morbilidad": "Tasa de morbilidad"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(morbidity_rate_chart)

                mortality_rate_chart = px.bar(
                    data,
                    x="id_centro_salud",
                    y="tasas_mortalidad",
                    title="Tasas de mortalidad por centro de salud",
                    labels={"id_centro_salud": "Centro de salud", "tasas_mortalidad": "Tasa de mortalidad"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(mortality_rate_chart)


if __name__ == "__main__":
    main()