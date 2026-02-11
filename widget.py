import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ---------------------------------------------------------
# 1. 페이지 설정: 여백 없이 꽉 채우기
# ---------------------------------------------------------
st.set_page_config(page_title="Macro Widget", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 전체 배경색 강제 적용 (검정) */
    .stApp {
        background-color: #0e1117 !important;
    }
    
    /* [핵심] 위젯처럼 보이게 불필요한 여백/메뉴 싹 제거 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 본문 여백 제거 (화면 꽉 채우기) */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* 카드 디자인: 그림자 없애고 경계선 강조 */
    div[data-testid="stMetric"] {
        background-color: #1e2227;
        padding: 8px 10px; /* 패딩을 조금 줄여서 오밀조밀하게 */
        border-radius: 8px;
        border: 1px solid #2d3139;
        margin-bottom: 5px;
    }
    
    /* 텍스트 크기 미세 조정 (모바일 가독성) */
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #b0b8c4 !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; color: white !important; font-weight: 700 !important;}
    
    /* 상승(빨강)/하락(파랑) 색상 강제 */
    [data-testid="stMetricDelta"][aria-label^="Up"] svg { fill: #ff4b4b !important; }
    [data-testid="stMetricDelta"][aria-label^="Up"] > div { color: #ff4b4b !important; }
    [data-testid="stMetricDelta"][aria-label^="Down"] svg { fill: #4b88ff !important; }
    [data-testid="stMetricDelta"][aria-label^="Down"] > div { color: #4b88ff !important; }

    /* Fear & Greed 텍스트 */
    .fg-value { font-size: 1.8rem; font-weight: 800; color: white; line-height: 1.0; text-align: center; margin-top: -30px; }
    .fg-label { font-size: 0.9rem; font-weight: 600; color: #e0e0e0; text-align: center; }
    .fg-date { font-size: 0.6rem; color: #888; text-align: center; margin-bottom: 10px; }
    
    /* 구분선 간격 줄이기 */
    hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 한국식 색상 카드 함수
# ---------------------------------------------------------
def create_card(label, value, change_str, unit=""):
    if "+" in change_str:
        color, arrow = "#ff4b4b", "▲"
    elif "-" in change_str:
        color, arrow = "#4b88ff", "▼"
    else:
        color, arrow = "#888888", "-"
        change_str = "0.00%"

    st.markdown(f"""
    <div style="background-color: #1e2227; padding: 10px; border-radius: 8px; border: 1px solid #2d3139; margin-bottom: 8px;">
        <div style="color: #9da5b1; font-size: 0.7rem; margin-bottom: 2px;">{label}</div>
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div style="color: white; font-size: 1.2rem; font-weight: 700;">{value}<span style="font-size:0.8rem; color:#ccc;">{unit}</span></div>
            <div style="color: {color}; font-size: 0.8rem; font-weight: 600;">{change_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 차트 생성 (여백 최소화)
# ---------------------------------------------------------
def make_fg_charts():
    # 데이터는 고정 (사진과 동일)
    y = [50, 45, 30, 25, 20, 25, 30, 40, 45, 50, 55, 60, 58, 55, 60, 65, 60, 55, 50, 48, 49]
    line = go.Figure(go.Scatter(y=y, mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
    line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=5, b=5), 
        xaxis=dict(visible=False), yaxis=dict(visible=False), height=80
    )

    gauge = go.Figure(go.Indicator(
        mode = "gauge", value = 49,
        gauge = {
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "rgba(0,0,0,0)"}, # 투명 바늘
            'steps': [
                {'range': [0, 25], 'color': '#ff6b6b'}, {'range': [25, 45], 'color': '#feca57'},
                {'range': [45, 55], 'color': '#ffffff'}, {'range': [55, 75], 'color': '#48dbfb'},
                {'range': [75, 100], 'color': '#1dd1a1'}
            ],
            'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': 49}
        }
    ))
    gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=0), height=80)
    return line, gauge

# ---------------------------------------------------------
# 4. 화면 배치
# ---------------------------------------------------------

# Fear & Greed
st.markdown("<h5 style='color:white; margin:0; padding:0;'>Fear & Greed Index</h5>", unsafe_allow_html=True)
c1, c2 = st.columns([1.5, 1])
l_chart, g_chart = make_fg_charts()
with c1:
    st.plotly_chart(l_chart, use_container_width=True, config={'staticPlot': True})
with c2:
    st.plotly_chart(g_chart, use_container_width=True, config={'staticPlot': True})
    st.markdown("""<div class="fg-value">49</div><div class="fg-label">Neutral</div>""", unsafe_allow_html=True)
st.markdown("<div class='fg-date'>Last updated: 2026-02-10 23:18</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# FRED
st.markdown("<h5 style='color:white; margin:0; padding:0;'>FRED</h5>", unsafe_allow_html=True)
f1, f2 = st.columns(2)
with f1:
    create_card("Fear & Greed", "49", "Neutral")
    create_card("VIX", "17.43", "+0.07")
    create_card("DXY (ICE)", "96.78", "-0.04%")
    create_card("US 2Y", "3.59", "-0.00", unit="%")
with f2:
    create_card("Fed Balance", "6605.91", "+18.34")
    create_card("TGA (Est)", "908.77", "-14.27")
    create_card("ON RRP", "1.31B", "-1.81")
    create_card("Repo Ops", "0.01B", "+0.01")

st.markdown("<hr>", unsafe_allow_html=True)

# INDEXerGO
st.markdown("<h5 style='color:white; margin:0; padding:0;'>INDEXerGO</h5>", unsafe_allow_html=True)
i1, i2 = st.columns(2)
with i1:
    create_card("달러인덱스", "97", "-0.04%")
    create_card("원/달러", "1,457", "-0.40%")
    create_card("금 (Gold)", "5,077", "+0.52%")
with i2:
    create_card("비트코인", "69,150", "-1.38%")
    create_card("이더리움", "2,023", "-3.83%")
    create_card("WTI유", "64", "+0.11%")
