import streamlit as st
import plotly.graph_objects as go

# 1. 페이지 기본 설정 (여백 제거)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. 통합 CSS (모바일 위젯 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding: 0px !important; }
    
    /* 위젯 통합 박스 디자인 */
    .widget-box {
        background-color: #1e2227;
        border-radius: 20px;
        padding: 15px;
        margin: 0;
        height: 100vh;
        border: 1px solid #2d3139;
    }
    .widget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .widget-title { color: white; font-size: 1.1rem; font-weight: 800; }
    .widget-date { color: #888; font-size: 0.75rem; }
    
    /* 2열 데이터 그리드 */
    .data-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        column-gap: 15px;
        row-gap: 5px;
    }
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
    }
    .lbl { color: #b0b8c4; font-size: 0.85rem; font-weight: 500; }
    .val-group { display: flex; align-items: baseline; gap: 5px; }
    .chg { font-size: 0.8rem; font-weight: 600; }
    .val { color: white; font-size: 1.0rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로우 HTML 생성 함수
def get_row_html(label, value, change):
    color = "#ff4b4b" if "+" in change else "#4b88ff" if "-" in change else "#888"
    return f"""
    <div class="data-row">
        <span class="lbl">{label}</span>
        <div class="val-group">
            <span class="chg" style="color: {color};">{change}</span>
            <span class="val">{value}</span>
        </div>
    </div>
    """

# URL 파라미터 확인
view = st.query_params.get("view", "fg")

# --- [VIEW 1] Fear & Greed Index ---
if view == "fg":
    st.markdown("""
    <div class="widget-box">
        <div class="widget-header">
            <span class="widget-title">Fear & Greed Index</span>
            <span class="widget-date">(Last 3 months)</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 게이지 차트 구현
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = 49,
        number = {'font': {'color': 'white', 'size': 30}},
        gauge = {
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "white", 'thickness': 0.8},
            'steps': [
                {'range': [0, 25], 'color': '#ff6b6b'},
                {'range': [25, 45], 'color': '#feca57'},
                {'range': [45, 55], 'color': '#ffffff'},
                {'range': [55, 75], 'color': '#48dbfb'},
                {'range': [75, 100], 'color': '#1dd1a1'}
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.8, 'value': 49}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20,r=20,t=20,b=20), height=180)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    
    st.markdown("""
        <div style="text-align:center; margin-top:-20px;">
            <div style="color:white; font-size:1.4rem; font-weight:800;">Neutral</div>
            <div style="color:#888; font-size:0.75rem;">Last updated: 2026-02-10 23:18</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- [VIEW 2] FRED ---
elif view == "fred":
    l_data = [("Fear & Greed", "49", "0.00%"), ("VIX", "17.43", "+0.07"), ("DXY", "96.78", "-0.04"), ("US 2Y", "3.59%", "-0.00"), ("US 10Y", "4.16%", "-0.04"), ("Stress Index", "-0.68", "+0.03"), ("M2 Supply", "22,411", "+88.90")]
    r_data = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("Repo Ops", "0.01B", "+0.01"), ("SOFR", "3.63%", "-"), ("MMF Total", "7,774", "+292.82"), ("Net Liquidity", "5697.13", "+32.61")]
    
    l_html = "".join([get_row_html(d[0], d[1], d[2]) for d in l_data])
    r_html = "".join([get_row_html(d[0], d[1], d[2]) for d in r_data])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="widget-header">
            <span class="widget-title">FRED</span>
            <span class="widget-date">2026/02/10 23:18</span>
        </div>
        <div class="data-grid">
            <div class="col-left">{l_html}</div>
            <div class="col-right">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- [VIEW 3] INDEXerGO ---
elif view == "idx":
    l_data = [("달러인덱스", "97", "-0.04%"), ("원/달러", "1,457", "-0.40%"), ("금 (Gold)", "5,077", "+0.52%"), ("은 (Silver)", "82", "-0.54%")]
    r_data = [("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%"), ("WTI유", "64", "+0.11%"), ("천연가스", "3.14", "-0.06%")]
    
    l_html = "".join([get_row_html(d[0], d[1], d[2]) for d in l_data])
    r_html = "".join([get_row_html(d[0], d[1], d[2]) for d in r_data])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="widget-header">
            <span class="widget-title">INDEXerGO</span>
            <span class="widget-date">2026-02-10 23:18</span>
        </div>
        <div class="data-grid">
            <div class="col-left">{l_html}</div>
            <div class="col-right">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
