import streamlit as st
import plotly.graph_objects as go
# 실시간 데이터를 원하시면 아래 두 줄 주석을 해제하고 requirements.txt에 추가하세요.
# import yfinance as yf
# import pandas as pd

# 1. 페이지 설정 (여백 완전 제거)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. CSS 스타일 정의 (간격 최소화 버전)
# ---------------------------------------------------------
# f-string 충돌 방지를 위해 일반 문자열로 작성했습니다.
style_html = """
<style>
    /* 기본 배경 및 여백 설정 */
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container {
        padding: 4px !important; /* 전체 컨테이너 패딩 최소화 */
        max-width: 100% !important;
    }

    /* [핵심] 위젯 박스 디자인 */
    .widget-box {
        background-color: #1e2227;
        border-radius: 18px;      /* 모서리 둥글기 */
        padding: 10px 12px;       /* 박스 내부 여백 줄임 */
        border: 1px solid #2d3139;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        margin-bottom: 8px;
    }

    /* 헤더 (제목 + 날짜) */
    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;       /* 헤더와 데이터 사이 간격 좁힘 */
    }
    .title {
        color: white;
        font-size: 1.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .date {
        color: #888;
        font-size: 0.7rem;
        font-weight: 500;
    }

    /* [핵심] 2열 그리드 레이아웃 (간격 조절) */
    .data-grid {
        display: flex;
        gap: 8px; /* ▲ 좌우 컬럼 사이 간격을 20px -> 8px로 대폭 축소 */
    }
    .col {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 1px; /* ▲ 데이터 행 사이 간격을 최소화 (거의 붙어있게) */
    }
    
    /* 데이터 행 디자인 (양끝 정렬) */
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1px 0; /* ▲ 행 위아래 여백 극소화 */
        line-height: 1.3; /* 줄 간격 좁힘 */
    }

    /* 폰트 스타일 */
    .lbl {
        color: #b0b8c4;
        font-size: 0.8rem;
        font-weight: 500;
        white-space: nowrap; /* 줄바꿈 방지 */
    }
    .val-group {
        display: flex;
        align-items: baseline;
        gap: 5px; /* 등락률과 값 사이 간격 */
    }
    .chg {
        font-size: 0.75rem;
        font-weight: 600;
    }
    .val {
        color: white;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: -0.3px;
        text-align: right;
    }

    /* 한국식 등락 색상 */
    .up { color: #ff4b4b; }  /* 상승 빨강 */
    .down { color: #4b88ff; } /* 하락 파랑 */
    .neutral { color: #888; }
</style>
"""
st.markdown(style_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 행 HTML 생성 함수
# ---------------------------------------------------------
def render_row(label, value, change):
    color_class = "neutral"
    if "+" in change: color_class = "up"
    elif "-" in change: color_class = "down"
    
    # 안전한 문자열 결합 방식 사용
    return f"""
    <div class="data-row">
        <span class="lbl">{label}</span>
        <div class="val-group">
            <span class="chg {color_class}">{change}</span>
            <span class="val">{value}</span>
        </div>
    </div>
    """

# ---------------------------------------------------------
# 4. 화면 렌더링 로직 (View 선택)
# ---------------------------------------------------------
view = st.query_params.get("view", "fred") # 기본값

# === [VIEW 1] Fear & Greed Index ===
if view == "fg":
    st.markdown("""
    <div class="widget-box" style="padding-bottom: 5px;">
        <div class="header-row">
            <span class="title">Fear & Greed Index</span>
            <span class="date">(Last 3 months)</span>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.8, 1])
    with c1:
        # 차트 여백도 최소화
        y = [50, 48, 42, 35, 30, 25, 20, 25, 30, 40, 45, 50, 55, 60, 65, 62, 58, 55, 52, 50, 49]
        fig = go.Figure(go.Scatter(y=y, mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=5,b=0), xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=8, color='gray')), height=110)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    with c2:
        gauge = go.Figure(go.Indicator(mode="gauge", value=49, gauge={'axis':{'range':[0,100],'visible':False},'bar':{'color':'white','thickness':0},'steps':[{'range':[0,25],'color':'#ff4b4b'},{'range':[25,45],'color':'#feca57'},{'range':[45,55],'color':'#ffffff'},{'range':[55,75],'color':'#48dbfb'},{'range':[75,100],'color':'#1dd1a1'}],'threshold':{'line':{'color':'white','width':3},'thickness':0.8,'value':49}}))
        gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=10,b=0), height=100)
        st.plotly_chart(gauge, use_container_width=True, config={'staticPlot': True})
        st.markdown('<div style="text-align:center; color:white; font-size:1.4rem; font-weight:800; margin-top:-30px; line-height:1;">49<br><span style="font-size:0.8rem; color:#e0e0e0; font-weight:600;">Neutral</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align:right; color:#666; font-size:0.65rem; margin-top:5px;">Last updated: 2026-02-10 23:18</div>
    </div>
    """, unsafe_allow_html=True)

# === [VIEW 2] FRED (초밀착 레이아웃) ===
elif view == "fred":
    # (디자인 확인을 위한 고정 데이터입니다. 실시간 연동시 교체 필요)
    l_items = [("Fear & Greed", "49", "Neutral"), ("VIX", "17.43", "+0.07"), ("DXY (ICE)", "96.78", "-0.04"), ("US 2Y", "3.59%", "-0.00"), ("US 10Y", "4.16%", "-0.04"), ("Stress Index", "-0.68", "+0.03"), ("M2 Supply", "22,411", "+88.90")]
    r_items = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("Repo Ops", "0.01B", "+0.01"), ("SOFR", "3.63%", "-"), ("MMF Total", "7,774", "+292.82"), ("Net Liquidity", "5697.13", "+32.61")]
    
    l_html = "".join([render_row(d[0], d[1], d[2]) for d in l_items])
    r_html = "".join([render_row(d[0], d[1], d[2]) for d in r_items])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="header-row">
            <span class="title">FRED</span>
            <span class="date">2026/2/11 15:00</span>
        </div>
        <div class="data-grid">
            <div class="col">{l_html}</div>
            <div class="col">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === [VIEW 3] INDEXerGO (초밀착 레이아웃) ===
elif view == "idx":
    # (디자인 확인을 위한 고정 데이터입니다.)
    l_items = [("달러인덱스", "97", "-0.04%"), ("원/달러", "1,457", "-0.40%"), ("금 (Gold)", "5,077", "+0.52%"), ("은 (Silver)", "82", "-0.54%")]
    r_items = [("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%"), ("WTI유", "64", "+0.11%"), ("천연가스", "3.14", "-0.06%")]
    
    l_html = "".join([render_row(d[0], d[1], d[2]) for d in l_items])
    r_html = "".join([render_row(d[0], d[1], d[2]) for d in r_items])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="header-row">
            <span class="title">INDEXerGO</span>
            <span class="date">2026-02-11 15:00</span>
        </div>
        <div class="data-grid">
            <div class="col">{l_html}</div>
            <div class="col">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
