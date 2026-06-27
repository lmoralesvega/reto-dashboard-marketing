import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# CONFIGURACIÓN AVANZADA DE LA PÁGINA
st.set_page_config(
    page_title="HR Analytics | Socialize Your Knowledge", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual para todas las gráficas
sns.set_theme(style="whitegrid", palette="muted")

# Título, descripción y logotipo
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        import os
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio_actual, "logo.png")
        st.image(ruta_logo, width=150)
    except Exception as e: # 👈 Atrapa TODOS los errores, incluyendo el de Streamlit
        st.warning("Logo pendiente")
        st.warning("Logo no disponible")

with col_title:
    st.title("HR Analytics Panel - Marketing")
    st.markdown("*Plataforma de inteligencia de talento para la toma de decisiones estratégicas.*")

# MOTOR DE DATOS (Carga y Limpieza)
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("employee_data.csv")
    df = df.drop_duplicates()
    cols_categoricas = ['gender', 'marital_status', 'position']
    for col in cols_categoricas:
        if col in df.columns: df[col] = df[col].astype(str).str.strip()
    cols_numericas = ['age', 'salary', 'performance_score', 'average_work_hours']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median())
    if 'name_employee' in df.columns:
        df = df.dropna(subset=['name_employee'])
    return df

df = load_and_clean_data()

# BARRA LATERAL
st.sidebar.markdown("### ⚙️ Panel de Control")
st.sidebar.markdown("Filtra la información para actualizar el dashboard.")

# Género
genero = st.sidebar.selectbox("👤 Género:", options=["Todos"] + list(df['gender'].unique()))

# Estado Civil
estado_civil = st.sidebar.selectbox("💍 Estado Civil:", options=["Todos"] + list(df['marital_status'].unique()))

# Rango de Desempeño
min_score, max_score = float(df['performance_score'].min()), float(df['performance_score'].max())
rango_desempeno = st.sidebar.slider("⭐ Rango de Desempeño:", min_score, max_score, (min_score, max_score))

# Aplicación de filtros
df_filtrado = df.copy()
if genero != "Todos": df_filtrado = df_filtrado[df_filtrado['gender'] == genero]
if estado_civil != "Todos": df_filtrado = df_filtrado[df_filtrado['marital_status'] == estado_civil]
df_filtrado = df_filtrado[(df_filtrado['performance_score'] >= rango_desempeno[0]) & 
                          (df_filtrado['performance_score'] <= rango_desempeno[1])]

# SECCIÓN DE KPIS 
st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="👥 Total Colaboradores", value=len(df_filtrado))
kpi2.metric(label="⭐ Desempeño Promedio", value=f"{df_filtrado['performance_score'].mean():.1f} / 5.0")
kpi3.metric(label="⏱️ Horas Promedio/Mes", value=f"{df_filtrado['average_work_hours'].mean():.0f} hrs")
kpi4.metric(label="💵 Salario Promedio", value=f"${df_filtrado['salary'].mean():,.2f}")
st.markdown("---")

# INTERFAZ POR PESTAÑAS 
tab1, tab2, tab3 = st.tabs(["📊 Visión General del Desempeño", "💵 Análisis de Compensación", "📂 Base de Datos y Descarga"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        # Rúbrica 6: Distribución de puntajes
        st.markdown("#### Distribución del Talento (Desempeño)")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.histplot(df_filtrado['performance_score'], bins=5, kde=True, ax=ax1, color='#4A90E2', edgecolor="white")
        ax1.set(xlabel="Puntaje", ylabel="Número de Empleados")
        st.pyplot(fig1)
        
    with col_b:
        # Horas por género
        st.markdown("#### Carga Laboral Promedio por Género")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        horas_gen = df_filtrado.groupby('gender')['average_work_hours'].mean().reset_index()
        sns.barplot(data=horas_gen, x='gender', y='average_work_hours', ax=ax2, palette='Set2')
        ax2.set(xlabel="", ylabel="Horas Mensuales")
        st.pyplot(fig2)

    # Horas vs Desempeño (Gráfico ancho)
    st.markdown("#### Relación: Horas Trabajadas vs Puntaje de Desempeño")
    fig4, ax4 = plt.subplots(figsize=(10, 3))
    sns.regplot(data=df_filtrado, x='average_work_hours', y='performance_score', ax=ax4, color='#F39C12', scatter_kws={'alpha':0.6}, line_kws={'color':'red'})
    ax4.set(xlabel="Horas Trabajadas al Mes", ylabel="Puntaje de Desempeño")
    st.pyplot(fig4)

with tab2:
    # Edad vs Salario
    st.markdown("#### Curva de Compensación: Edad vs Salario")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_filtrado, x='age', y='salary', hue='gender', size='performance_score', sizes=(40, 200), alpha=0.8, palette='viridis', ax=ax3)
    ax3.set(xlabel="Edad del Colaborador", ylabel="Salario (MXN)")
    # Mover la leyenda afuera para mayor limpieza
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig3)

with tab3:
    st.markdown("#### Auditoría de Datos Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)
    # Extra: Botón para descargar CSV de los datos filtrados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar reporte actual (CSV)", data=csv, file_name="reporte_marketing_filtrado.csv", mime="text/csv")

# CONCLUSIONES CORREGIDAS
st.markdown("### Conclusiones")

st.markdown("<br>", unsafe_allow_html=True)
st.info("""
**Conclusión**
El análisis multivariable del departamento de Marketing revela puntos de acción inmediatos. La distribución del talento nos muestra dónde se concentra el núcleo operativo de la agencia. Notablemente, la relación entre *Horas Trabajadas* y *Desempeño* (con su línea de tendencia) nos permite identificar si el sobreesfuerzo está generando resultados o simplemente causando *burnout*. Finalmente, el mapa de compensación por edad cruzado con género y desempeño otorga una radiografía clara para auditar la equidad salarial interna en los próximos ciclos de revisión.
""")
