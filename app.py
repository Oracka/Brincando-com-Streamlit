import streamlit as st 
import pandas as pd
import plotly.express as px

# define page e caracteristicas da aba/site
st.set_page_config(page_title='exemplo', layout='wide', page_icon='radius.svg')


# armazena dados na memoria do pc apos tempo de aplicação 
@st.cache_data
def carregar_arquivo(caminho_xls):
    xls = pd.ExcelFile(caminho_xls)
    
    abas_anos = [sheet for sheet in xls.sheet_names if '(CV)' not in sheet] 
    # cria uma lista vazia que vai ser preenchida por um for 
    dados_totais = []
    
    for ano in abas_anos:
        df_raw = pd.read_excel(xls, sheet_name=ano)
        
        start_idx = df_raw[df_raw.iloc[:, 0] == 'Brasil'].index[0]
        
        df_ano = df_raw.iloc[start_idx:, [0, 1, 2, 3]].copy()
        df_ano.columns = ['Localidade', 'Total', 'Homem', 'Mulher']
        
        df_ano = df_ano.dropna(subset=['Localidade'])
        df_ano = df_ano[df_ano['Localidade'].astype(str).str.strip() != '']
        
        for col in ['Total', 'Homem', 'Mulher']:
            df_ano[col] = pd.to_numeric(df_ano[col], errors='coerce')
            
        df_ano['Ano'] = str(ano)
        dados_totais.append(df_ano)
        
        
    df_completo = pd.concat(dados_totais, ignore_index=True)
    return df_completo

caminho_xls = r'Tabela 1.1.2.xls'
try:
    df = carregar_arquivo(caminho_xls)
    
    st.sidebar.header('filtros')
    
    ano_disponiveis = sorted(df['Ano'].unique(), reverse=True)
    ano_selecionado = st.sidebar.selectbox('Selecione o Ano', ano_disponiveis)
    
    localidade_disponiveis = df['Localidade'].unique().tolist()
    localidade_selecionadas = st.sidebar.multiselect('Selecione as Regiões/UFs:',options=localidade_disponiveis, 
    
    default=['Brasil', 'Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste']
    )

    st.title('horas dedicadas a cuidados e afazeres')
    st.markdown('analise media de horas semanais por pessoa ')

    df_filtrado = df[(df['Ano'] == ano_selecionado) & (df['Localidade']).isin(localidade_selecionadas)]
    
    if not df_filtrado.empty:
        st.subheader(f'Tabela de dados ({ano_selecionado})')
        st.dataframe(df_filtrado[['Localidade', 'Total', 'Homem', 'Mulher']].reset_index(drop=True), use_container_width=True)
        
        st.markdown('--')
        st.subheader('grafico de comparação')
        # define as duas variaveis em colunas do streamlit
        col1, col2 = st.columns(2)
        
        with col1:
            df_melted = df_filtrado.melt(
                id_vars=['Localidade'],
                value_vars=['Homem', 'Mulher'],
                var_name='Genero',
                value_name='Horas Semanais'
            )
            
            fig_bar = px.bar(
                df_melted, 
                x='Localidade',
                y='Horas Semanais',
                color='Genero',
                barmode='group',
                title=f'Média de horas por Genero ({ano_selecionado})',
                color_discrete_sequence=['#003758', '#000080'],
                labels={'Horas Semanais': 'Horas/Semana', 'Localidade': 'Região/ UF'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            df_historico = df[df['Localidade'].isin(localidade_selecionadas)]
            
            fig_line = px.line(
                df_historico,
                x='Ano',
                y='Total',
                color='Localidade',
                markers=True,
                title='Evolucao temporal do total de horas ',
                labels={'Total': 'Horas/Semana', 'Ano':'Ano'}
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
    else:
        st.warning('nennhuma localidade nos filtros de barra lateral')
        
except Exception as e:
    st.error(f'erro ao carregar{e}')
    st.info('ve o arquivo ai')
        
            