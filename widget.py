import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 (여백 최소화)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. CSS 스타일 (아이폰 위젯 디자인 복구)
# ---------------------------------------------------------
style_css = """
<style>
    /* 리얼 블랙 배경 */
    .stApp { background-color: #000000 !important; }
    header, footer { visibility: hidden; }
    
    /* 컨테이너 여백 제거 및 모바일 최적화 */
    .block-container {
        padding: 10px 5px !important;
        max-width: 100% !important;
    }

    /* 위젯 박스 (공통 컨테이너) */
    .widget-container {
        background-color: #1c1c1e;
        border-radius: 22px;
        padding: 16px;
        margin-bottom: 16px; /* 위젯 사이 간격 */
        font-family: -apple-system, sans-serif;
    }

    /* 헤더 영역 */
    .header-box {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 8px;
    }
    .w-title {
        color: white;
        font-size: 18px;
        font-weight: 700;
    }
    .w-date {
        color: #8e8e93;
        font-size: 12px;
    }

    /* 데이터 그리드 (좌우 2열) */
    .grid-box {
        display: flex;
        flex-direction: row;
        gap: 10px;
    }
    .col-box {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    /* 데이터 행 (Row) */
    .d-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 20px;
    }
    .lbl {
        color: #b0b0b0;
        font-size: 13px;
        font-weight: 500;
    }
    .val-group {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .val {
        color: white;
        font-size: 14px;
        font-weight: 700;
        text-align: right;
        min-width: 50px;
    }
    .chg {
        font-size: 12px;
        font-weight: 600;
    }

    /* 색상 유틸리티 */
    .up { color: #ff453a; }
    .down { color: #0a84ff; }
    .neutral { color: #8e8e93; }

    /* F&G 점수 스타일 */
    .score-box {
        text-align: center;
        margin-top: -15px;
    }
    .score-num { font-size: 28px; font-weight: 800; color: white; }
    .score-txt { font-size: 13px; font-weight: 600; color: #e0e0e0; }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 로직
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_live_data(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) < 2: return "-", "0.00%"
        curr = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        pct = ((curr - prev) / prev) * 100
        
        if curr >= 1000: val_s = f"{curr:,.0f}"
        elif curr < 1: val_s = f"{curr:,.3f}"
        else: val_s = f"{curr:,.2f}"
        
        return val_s, f"{pct:+.2f}%"
    except:
        return "-", "0.00%"

def make_row_html(label, val, chg):
    c_cls = "neutral"
    if "+" in chg: c_cls = "up"
    elif "-" in chg: c_cls = "down"
    
    return f"""
    <div class="d-row">
        <span class="lbl">{label}</span>
        <div class="val-group">
            <span class="chg {c_cls}">{chg}</span>
            <span class="val">{val}</span>
        </div>
    </div>
    """

# 날짜 시간
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

# =========================================================
# [1] Fear & Greed Index (그래프 쳐짐 해결 버전)
# =========================================================
# 컨테이너 시작 HTML
st.markdown(f"""
<div class="widget-container">
    <div class="header-box">
        <span class="w-title">Fear & Greed Index</span>
        <span class="w-date">(Last 3 months)</span>
    </div>
""", unsafe_allow_html=True)

# 그래프 영역 (Streamlit 컬럼 사용)
c1, c2 = st.columns([1.8, 1])

with c1:
    # 1. 그래프 위아래 공백 제거 (margin=0)
    # 2. 높이 고정 (height=100)
    fig = go.Figure(go.Scatter(
        y=[50,48,42,35,30,25,20,25,30,40,45,50,55,60,65,62,58,55,52,50,49],
        mode='lines',
        line=dict(color='#e0e0e0', width=2),
        fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=5, b=5), # 핵심: 마진 제거
        xaxis=dict(visible=False),
        yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=9, color='#666')),
        height=100
    )
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

with c2:
    fig_g = go.Figure(go.Indicator(
        mode="gauge", value=49,
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "white", 'thickness': 0},
            'steps': [
                {'range': [0, 25], 'color': '#ff453a'},
                {'range': [25, 45], 'color': '#ff9f0a'},
                {'range': [45, 55], 'color': '#ffffff'},
                {'range': [55, 75], 'color': '#64d2ff'},
                {'range': [75, 100], 'color': '#30d158'}
            ],
            'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': 49}
        }
    ))
    fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=0,b=0), height=80)
    st.plotly_chart(fig_g, use_container_width=True, config={'staticPlot': True})
    
    st.markdown("""
    <div class="score-box">
        <div class="score-num">49</div>
        <div class="score-txt">Neutral</div>
    </div>
    """, unsafe_allow_html=True)

# 컨테이너 닫기
st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# [2] FRED (데이터 + 시간 표시)
# =========================================================
# 데이터 준비
vix_v, vix_c = get_live_data("^VIX")
dxy_v, dxy_c = get_live_data("DX-Y.NYB")
us10y_v, us10y_c = get_live_data("^TNX")
us2y_v, us2y_c = get_live_data("^IRX")

# HTML 조립
left_rows = [
    ("Fear & Greed", "49", "Neutral"),
    ("VIX", vix_v, vix_c),
    ("DXY (ICE)", dxy_v, dxy_c),
    ("US 2Y", us2y_v, us2y_c),
    ("US 10Y", us10y_v, us10y_c),
    ("Stress Index", "-0.68", "+0.03"),
    ("M2 Supply", "22,411", "+88.90")
]
right_rows = [
    ("Fed Balance", "6605.91", "+18.34"),
    ("TGA (Est)", "908.77", "-14.27"),
    ("ON RRP", "1.31B", "-1.81"),
    ("Repo Ops", "0.01B", "+0.01"),
    ("SOFR", "3.63%", "-"),
    ("MMF Total", "7,774", "+292.82"),
    ("Net Liquidity", "5697.13", "+32.61")
]

# [중요] f-string 안에서 HTML을 완성해서 한방에 렌더링해야 깨지지 않음
left_html = "".join([make_row_html(l, v, c) for l, v, c in left_rows])
right_html = "".join([make_row_html(l, v, c) for l, v, c in right_rows])

fred_html = f"""
<div class="widget-container">
    <div class="header-box">
        <span class="w-title">FRED</span>
        <span class="w-date">{now_str}</span>
    </div>
    <div class="grid-box">
        <div class="col-box">{left_html}</div>
        <div class="col-box">{right_html}</div>
    </div>
</div>
"""
st.markdown(fred_html, unsafe_allow_html=True)


# =========================================================
# [3] INDEXerGO (데이터 + 시간 표시)
# =========================================================
krw_v, krw_c = get_live_data("KRW=X")
gold_v, gold_c = get_live_data("GC=F")
silver_v, silver_c = get_live_data("SI=F")
btc_v, btc_c = get_live_data("BTC-USD")
eth_v, eth_c = get_live_data("ETH-USD")
wti_v, wti_c = get_live_data("CL=F")
gas_v, gas_c = get_live_data("NG=F")
dxy_v, dxy_c = get_live_data("DX-Y.NYB")

idx_left = [
    ("달러인덱스", dxy_v, dxy_c),
    ("원/달러", krw_v, krw_c),
    ("금 (Gold)", gold_v, gold_c),
    ("은 (Silver)", silver_v, silver_c)
]
idx_right = [
    ("비트코인", btc_v, btc_c),
    ("이더리움", eth_v, eth_c),
    ("WTI유", wti_v, wti_c),
    ("천연가스", gas_v, gas_c)
]

l_idx_html = "".join([make_row_html(l, v, c) for l, v, c in idx_left])
r_idx_html = "".join([make_row_html(l, v, c) for l, v, c in idx_right])

indexergo_html = f"""
<div class="widget-container">
    <div class="header-box">
        <span class="w-title">INDEXerGO</span>
        <span class="w-date">{now_str}</span>
    </div>
    <div class="grid-box">
        <div class="col-box">{l_idx_html}</div>
        <div class="col-box">{r_idx_html}</div>
    </div>
</div>
"""
st.markdown(indexergo_html, unsafe_allow_html=True)
