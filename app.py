import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database.connection import init_db, engine
from controllers.main_controller import MainController

# Definições de Página e Design Moderno Minimalista
st.set_page_config(page_title="VisionStream Intelligence", layout="wide", page_icon="⚙️")

# Executa de forma resiliente a inicialização do banco de dados
try:
    init_db()
except Exception:
    pass

# Instanciação unificada do Controller da Camada Superior
controller = MainController()

# Customização e Estilização por CSS Embutido
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .status-badge { padding: 6px 12px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ─── NAV / MENU LATERAL DE OPERAÇÕES ───
with st.sidebar:
    st.title("📸 VisionStream")
    st.caption("Painel Unificado de Controle de Produção")
    st.markdown("---")
    
    # Exibição do Status em Tempo Real da Conexão Neon.tech
    try:
        with engine.connect() as conn:
            st.markdown('<div class="status-badge" style="background-color:#d4edda; color:#155724;">🟢 Conexão Neon: Ativa</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="status-badge" style="background-color:#f8d7da; color:#721c24;">🔴 Conexão Neon: Fallback Local</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    opcao_menu = st.radio("Selecione o Módulo Ativo:", ["Câmera & Captura", "Histórico de Análises", "Dashboard Gerencial"])

# ─── MÓDULO 1: CÂMERA & CAPTURA EM TEMPO REAL ───
if opcao_menu == "Câmera & Captura":
    st.title("📸 Captura e Processamento de Imagens")
    st.markdown("Alinhamento nativo de vídeo por hardware direto no navegador do cliente.")
    
    col_cam, col_res = st.columns([1, 1])
    
    with col_cam:
        st.subheader("Webcam Ativa")
        foto_capturada = st.camera_input("Disparar captura automática")
        
    with col_res:
        if foto_capturada:
            st.subheader("✓ Imagem Registrada")
            st.image(foto_capturada, use_column_width=True)
            
            with st.spinner("Executando pipeline analítico no banco Neon..."):
                raw_bytes = foto_capturada.getvalue()
                try:
                    registro_salvo = controller.processar_e_salvar(raw_bytes)
                    st.success("Análise computacional estruturada gravada com sucesso!")
                    
                    st.markdown("### 📊 Dados Obtidos da Imagem")
                    st.write(f"**Descrição:** {registro_salvo.descricao}")
                    st.write(f"**Resolução Nativa:** {registro_salvo.json_resultado.get('resolucao')}")
                    st.write(f"**Rostos Encontrados:** {registro_salvo.rostos}")
                    st.write(f"**Nível de Nitidez:** {registro_salvo.nitidez}")
                    st.write(f"**Luminosidade Encontrada:** {registro_salvo.luminosidade}")
                    st.write(f"**Paleta Média (RGB):** {registro_salvo.cores}")
                except Exception as ex:
                    st.error(f"Erro no processamento técnico dos dados: {str(ex)}")

# ─── MÓDULO 2: HISTÓRICO INTERATIVO DE ANÁLISES ───
elif opcao_menu == "Histórico de Análises":
    st.title("📜 Histórico de Análises")
    st.markdown("Pesquisa avançada, filtros dinâmicos e exportação de dados analíticos persistidos.")
    
    registros = controller.obter_historico()
    
    if not registros:
        st.info("Nenhuma imagem registrada encontrada no banco de dados.")
    else:
        # Barra superior de filtros de pesquisa e data
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            termo_pesquisa = st.text_input("🔍 Pesquisar por Descrição ou Filtro de Nitidez:", "")
        with col_f2:
            data_filtro = st.date_input("Filtrar por Data:", value=None)
            
        # Estruturação e conversão em DataFrame para tratamento de dados
        lista_exportavel = []
        for r in registros:
            data_item = r.created_at.date()
            
            # Lógica dos filtros combinados
            if termo_pesquisa.lower() not in r.descricao.lower() and termo_pesquisa.lower() not in r.nitidez.lower():
                continue
            if data_filtro is not None and data_item != data_filtro:
                continue
                
            lista_exportavel.append({
                "ID": r.id,
                "Data_Hora": r.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                "Descricao": r.descricao,
                "Objetos": r.objetos,
                "Pessoas": r.quantidade_pessoas,
                "Rostos": r.rostos,
                "Nitidez": r.nitidez,
                "Luminosidade": r.luminosidade,
                "Cores": r.cores,
                "image_path": r.image_path
            })
            
        df_historico = pd.DataFrame(lista_exportavel)
        
        if df_historico.empty:
            st.warning("Nenhum resultado corresponde aos critérios de filtragem selecionados.")
        else:
            # Linha de Botões de Exportação
            col_exp_csv, col_exp_json = st.columns(2)
            with col_exp_csv:
                dados_csv = df_historico.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exportar para CSV", dados_csv, "historico_vision.csv", "text/csv")
            with col_exp_json:
                dados_json = json.dumps(lista_exportavel, indent=4, ensure_ascii=False).encode('utf-8')
                st.download_button("📥 Exportar para JSON", dados_json, "historico_vision.json", "application/json")
                
            st.markdown("---")
            
            # Loop de renderização dos cards individuais do histórico
            for item in lista_exportavel:
                with st.container():
                    c_preview, c_info, c_botoes = st.columns([1.2, 2.5, 1.3])
                    
                    with c_preview:
                        if os.path.exists(item["image_path"]):
                            st.image(item["image_path"], use_column_width=True)
                        else:
                            st.error("Arquivo apagado do servidor")
                            
                    with c_info:
                        st.markdown(f"#### Registro #{item['ID']} — {item['Data_Hora']}")
                        st.write(f"**Descrição:** {item['Descricao']}")
                        st.write(f"**Rostos:** {item['Rostos']} | **Nitidez:** {item['Nitidez']} | **Luminosidade:** {item['Luminosidade']}")
                        st.write(f"**Cores Predominantes:** `{item['Cores']}`")
                        
                    with c_botoes:
                        st.write("")
                        if os.path.exists(item["image_path"]):
                            with open(item["image_path"], "rb") as f_img:
                                st.download_button(
                                    label="💾 Download Foto",
                                    data=f_img,
                                    file_name=os.path.basename(item["image_path"]),
                                    mime="image/jpeg",
                                    key=f"down_{item['ID']}"
                                )
                        if st.button("🗑️ Excluir Registro", key=f"btn_del_{item['ID']}"):
                            controller.excluir_registro(item["ID"], item["image_path"])
                            st.rerun()
                st.markdown("<hr style='margin:1em 0; border:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)

# ─── MÓDULO 3: DASHBOARD DE MÉTRICAS OPERACIONAIS ───
elif opcao_menu == "Dashboard Gerencial":
    st.title("📈 Dashboard Gerencial")
    st.markdown("Métricas consolidadas a partir do histórico de dados salvos.")
    
    registros = controller.obter_historico()
    
    if not registros:
        st.info("Insira dados através do módulo de captura para popular os gráficos analíticos.")
    else:
        df_metrics = pd.DataFrame([{
            "Rostos": r.rostos,
            "Nitidez": r.nitidez.split()[0], # Coleta apenas o texto base "Alta" ou "Baixa"
            "Luminosidade": r.luminosidade
        } for r in registros])
        
        # Grid superior de indicadores estatísticos básicos
        ind1, ind2, ind3 = st.columns(3)
        ind1.metric("Volume de Capturas", len(df_metrics))
        ind2.metric("Total de Rostos Processados", int(df_metrics["Rostos"].sum()))
        ind3.metric("Aproveitamento de Imagens Nítidas", len(df_metrics[df_metrics["Nitidez"] == "Alta"]))
        
        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("Métrica de Luminosidade das Capturas")
            st.bar_chart(df_metrics["Luminosidade"].value_counts())
        with col_g2:
            st.subheader("Qualidade de Foco e Nitidez")
            st.bar_chart(df_metrics["Nitidez"].value_counts())