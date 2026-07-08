import streamlit as st
import time
from datetime import timedelta
import pdfplumber
import google.generativeai as genai
import json
import pandas as pd
import plotly.express as px
import sqlite3
from reportlab.pdfgen import canvas

def gerar_carta_anuencia(produtor, fazenda):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "CARTA DE ANUÊNCIA DE ARRENDATÁRIO")
    c.drawString(100, 700, f"Eu, {produtor}, na qualidade de arrendatário da {fazenda},")
    c.drawString(100, 680, "declaro estar ciente e autorizar a constituição de penhor da safra.")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

import io# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="App Barter", page_icon="🌱", layout="wide")

# --- 1. CRIAÇÃO DO BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect('banco_barter.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produtor TEXT,
            cultura TEXT,
            volume INTEGER,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

iniciar_banco()

# --- MENU LATERAL (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2933/2933004.png", width=80)
st.sidebar.title("Navegação")
pagina_selecionada = st.sidebar.radio("Ir para:", ["📝 Nova Operação", "📊 Dashboard Gerencial"])

st.sidebar.divider()
st.sidebar.header("⚙️ Configurações da IA")
api_key_input = st.sidebar.text_input("API Key (Gemini)", type="password")

if api_key_input:
    genai.configure(api_key=api_key_input)


# ==========================================
# PÁGINA 1: NOVA OPERAÇÃO
# ==========================================
if pagina_selecionada == "📝 Nova Operação":
    st.title("🚜 Análise de Risco - Barter")

    # MÓDULO 1
    st.header("1. Compliance Socioambiental")
    numero_car = st.text_input("Número do CAR (Ex: SP-3538006...)")
    if st.button("Consultar IBAMA"):
        if numero_car:
            with st.spinner("Consultando bases..."):
                time.sleep(1)
                st.success("✅ NADA CONSTA (REGULAR)")
        else:
            st.warning("⚠️ Digite um CAR válido.")
    st.divider() 

    # MÓDULO 2
    st.header("2. Trava Lógica de Prazos")
    col1, col2 = st.columns(2)
    with col1:
        data_fim_arrendamento = st.date_input("Data Final do Arrendamento")
    with col2:
        data_vencimento_cpr = st.date_input("Data de Vencimento da CPR")

    dias_carencia = st.number_input("Dias de Carência", min_value=0, value=30, step=15)

    if st.button("Validar Risco da Operação"):
        data_limite_segura = data_vencimento_cpr + timedelta(days=dias_carencia)
        if data_limite_segura > data_fim_arrendamento:
            st.error(f"🔴 BLOQUEADO: Arrendamento vence antes da liquidação.")
        else:
            st.success("🟢 APROVADO: Prazos validados.")
    st.divider() 

    # MÓDULO 3
 # --- 3. GESTÃO DE DOCUMENTOS E FORMALIZAÇÃO ---
    st.header("3. Gestão de Documentos e Formalização")
    aba_contrato, aba_matricula, aba_pessoais, aba_formalizacao = st.tabs(["📑 Contrato", "📜 Matrícula", "🪪 Pessoais", "✍️ Formalização"])

    with aba_contrato:
        arquivo_contrato = st.file_uploader("Upload do Contrato", type=["pdf"], key="up_contrato")
        if arquivo_contrato and st.button("Analisar Contrato com IA"):
             st.info("IA rodando...") # Lógica que você já tinha

    with aba_matricula:
        st.file_uploader("Upload da Matrícula", type=["pdf"], key="up_mat")
        
    with aba_pessoais:
        st.file_uploader("Upload de Documentos Pessoais", type=["pdf", "jpg"], key="up_pes")

    with aba_formalizacao:
        st.subheader("Assinatura e Anuências")
        st.markdown("Gerador de documentos para formalização da operação.")
        
        # Botão para gerar a carta
        if st.button("Gerar Carta de Anuência PDF"):
            # Aqui chamamos a função que criamos (lembre-se de tê-la definido no topo)
            pdf_buffer = gerar_carta_anuencia(nome_produtor, "Fazenda Alvorada")
            st.download_button(label="📥 Baixar Anuência", data=pdf_buffer, file_name="anuencia.pdf")
        
        st.divider()
        st.markdown("Enviar para Assinatura (ZapSign):")
        email_ass = st.text_input("E-mail do Produtor")
        if st.button("📤 Disparar Assinatura Digital"):
            st.success(f"Link enviado para {email_ass}!")

    # --- NOVO MÓDULO 4: DILIGÊNCIA B3/CARTÓRIO ---
    st.header("4. Diligência de Garantias (Cartório/B3)")
    st.markdown("Consulta automatizada de ônus, hipotecas e CPRs registradas na matrícula ou CNPJ.")
    
    col_garantia1, col_garantia2 = st.columns(2)
    with col_garantia1:
        tipo_consulta = st.selectbox("Tipo de Consulta", ["Matrícula do Imóvel", "CNPJ do Produtor"])
    with col_garantia2:
        dado_consulta = st.text_input("Número do Documento")

    if st.button("Consultar Central de Registradores / B3"):
        if dado_consulta:
            with st.spinner(f"Conectando à API ({tipo_consulta})..."):
                time.sleep(2) # Simula o tempo da API real
                st.success("✅ NADA CONSTA: Área livre de ônus e penhor prévio.")
                st.json({"Documento": dado_consulta, "Status B3": "Livre", "Penhor_Agricola": "Negativo"})
        else:
            st.warning("⚠️ Preencha o número do documento para consultar.")
    st.divider()

    # --- NOVO MÓDULO 5: ASSINATURA DIGITAL ---
    st.header("5. Formalização (Assinatura Digital)")
    st.markdown("Integração com API de Assinaturas (Ex: ZapSign, DocuSign).")
    
    col_ass1, col_ass2 = st.columns(2)
    with col_ass1:
        email_assinante = st.text_input("E-mail do Produtor")
    with col_ass2:
        telefone_assinante = st.text_input("WhatsApp (DDD + Número)")

    if st.button("📤 Enviar Contrato para Assinatura"):
        if email_assinante and telefone_assinante:
            with st.spinner("Gerando envelope digital e disparando links via WhatsApp..."):
                time.sleep(2) # Simula a requisição HTTP para a ZapSign
                st.success(f"📩 Envelope enviado com sucesso para o e-mail e WhatsApp do cliente!")
                st.info("🔗 Link de rastreamento gerado: https://zapsign.com.br/verificar/mock-8a7b6c")
        else:
            st.warning("⚠️ Preencha e-mail e WhatsApp para disparar a assinatura.")
    st.divider()
if st.button("Gerar Carta de Anuência PDF"):
    pdf_buffer = gerar_carta_anuencia(nome_produtor, "Fazenda Alvorada")
    st.download_button(label="📥 Baixar Anuência", data=pdf_buffer, file_name="anuencia.pdf")

    # --- MÓDULO 6: SALVAR NO BANCO ---
    st.header("6. Efetivar Operação")
    
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        nome_produtor = st.text_input("Nome do Produtor / Fazenda")
    with col_b:
        cultura = st.selectbox("Cultura", ["Soja", "Milho Safrinha", "Algodão", "Café"])
    with col_c:
        volume_sacas = st.number_input("Volume (Sacas)", min_value=0, step=1000)
        
    # Adicionei o status "Aguardando Assinatura"
    status_operacao = st.selectbox("Status Final", ["Análise de Risco", "Aguardando Assinatura", "Aprovada (Emissão)", "Bloqueio Ambiental", "Pendência Documental"])

    if st.button("💾 Salvar no Banco de Dados"):
        if nome_produtor and volume_sacas > 0:
            conn = sqlite3.connect('banco_barter.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO operacoes (produtor, cultura, volume, status) VALUES (?, ?, ?, ?)", 
                           (nome_produtor, cultura, volume_sacas, status_operacao))
            conn.commit()
            conn.close()
            st.success(f"🎉 Operação de {nome_produtor} salva com sucesso! Vá ao Dashboard para ver os gráficos atualizados.")
        else:
            st.warning("⚠️ Preencha o nome do produtor e o volume maior que zero para salvar.")


# ==========================================
# PÁGINA 2: DASHBOARD GERENCIAL
# ==========================================
elif pagina_selecionada == "📊 Dashboard Gerencial":
    st.title("📊 Painel Gerencial - Tempo Real")
    
    conn = sqlite3.connect('banco_barter.db')
    df = pd.read_sql_query("SELECT * FROM operacoes", conn)
    conn.close()

    if df.empty:
        st.info("Nenhuma operação registrada no banco de dados.")
    else:
        total_ops = len(df)
        volume_total = df['volume'].sum()
        aprovadas = len(df[df['status'].isin(['Aprovada (Emissão)', 'Aguardando Assinatura'])])
        
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric(label="Operações Ativas", value=f"{total_ops}")
        col_kpi2.metric(label="Volume Total Originado (Sacas)", value=f"{volume_total:,.0f}".replace(',', '.'))
        col_kpi3.metric(label="Taxa de Progresso (Aprov/Assinatura)", value=f"{(aprovadas/total_ops)*100:.1f}%")

        st.divider()

        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            st.subheader("Volume por Cultura")
            df_cultura = df.groupby('cultura')['volume'].sum().reset_index()
            fig_bar = px.bar(df_cultura, x='cultura', y='volume', color='cultura', 
                             color_discrete_sequence=['#2E8B57', '#F4A460', '#8B4513', '#A0522D'])
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_grafico2:
            st.subheader("Status do Portfólio")
            df_status = df.groupby('status').size().reset_index(name='Quantidade')
            fig_pie = px.pie(df_status, values='Quantidade', names='status', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Banco de Dados Bruto")
        st.dataframe(df, use_container_width=True, hide_index=True)