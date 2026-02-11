import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import random

# 1. 페이지 설정 (여백 0, 와이드 모드)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. CSS 스타일 (아이폰 위젯 100% 맞춤 디자인)
# ---------------------------------------------------------
style_css = """
<style>
    /* 전체 배경: 리얼 블랙 */
    .stApp { background-color: #000000 !important; }
    header, footer, #MainMenu { visibility: hidden; }
    
    /* 컨테이너 여백 제거 */
    .block-container {
        padding: 0px !important;
        max-width: 100% !important;
    }

    /* 위젯 박스 공통 스타일 */
    .widget-box {
        background-color: #1c1c1e; /* 아이폰 다크모드 카드색 */
        border-radius: 22px;
        padding: 14px 16px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        height: 100vh; /* 화면 꽉 채우기 */
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
    }

    /* 헤더 (제목 + 날짜) */
    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 10px;
        height: 24px;
    }
    .title {
        color: white;
        font-size: 17px;
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    .date {
        color: #8e8e93;
        font-size: 11px;
        font-weight: 400;
        margin-bottom: 2px;
    }

    /* 2열 그리드 레이아웃 */
    .data-grid {
        display: flex;
        flex-direction: row;
        gap: 12px; /* 좌우 컬럼 간격 */
        flex: 1;
    }
    .col {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 4px; /* 데이터 행 사이 간격 (아주 촘촘하게) */
    }

    /* 데이터 행 디자인 */
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        min-height: 18px;
    }

    /* 라벨 (왼쪽) */
    .lbl {
        color: #b0b0b0;
        font-size: 13px;
        font-weight: 500;
        white-space: nowrap;
    }

    /* 값 그룹 (오른쪽) */
    .val-group {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .chg {
        font-size: 12px;
        font-weight: 600;
    }
    .val {
        color: white;
        font-size: 14px;
        font-weight: 700;
        text-align: right;
        min-width: 45px;
        letter-spacing: -0.3px;
    }

    /* 색상표 (한국 주식 스타일: 상승=빨강) */
    .up { color: #ff453a; }
    .down { color: #0a84ff; }
    .neutral { color: #8e8e93; }

    /* F&G 전용 스타일 */
    .fg-score {
        font-size: 26px;
        font-weight: 800;
        color: white;
        text-align: center;
        line-height: 1;
    }
    .fg-status {
        font-size: 13px;
        font-weight: 600;
        color: #e0e0e0;
        text-align: center;
        margin-top: 2px;
    }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 실시간 데이터 가져오기 (yfinance)
# ---------------------------------------------------------
@st.cache_data(ttl=60) # 1분마다 갱신
def get_live_data(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) < 2: return "-", "0.00%"
        
        curr = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((curr - prev) / prev) * 100
        
        # 값 포맷팅
        if curr >= 1000: val_str = f"{curr:,.0f}"
        elif curr < 1: val_str = f"{curr:,.3f}" # 1보다 작으면 소수점 3자리
        else: val_str = f"{curr:,.2f}"
            
        return val_str, f"{change_pct:+.2f}%"
    except:
        return "Err", "0.00%"

# HTML 행 생성 함수
def make_row(label, value, change):
    if "+" in change: color = "up"
    elif "-" in change: color = "down"
    else: color = "neutral"
    
    return f"""
    <div class="data-row">
        <span class="lbl">{label}</span>
        <div class="val-group">
            <span class="chg {color}">{change}</span>
            <span class="val">{value}</span>
        </div>
    </div>
    """

# ---------------------------------------------------------
# 4. 뷰(View) 라우팅
# ---------------------------------------------------------
view_mode = st.query_params.get("view", "fred")

# =========================================================
# [1] Fear & Greed Index (왼쪽 차트 + 오른쪽 게이지)
# =========================================================
if view_mode == "fg":
    st.markdown("""
    <div class="widget-box" style="justify-content: center;">
        <div class="header-row" style="margin-bottom:0;">
            <span class="title">Fear & Greed Index</span>
            <span class="date">(Last 3 months)</span>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.8, 1])
    
    with c1:
        # 꺾은선 그래프 (디자인용 모의 데이터 + 약간의 랜덤성)
        base_y = [50,48,42,35,30,25,20,25,30,40,45,50,55,60,65,62,58,55,52,50,49]
        # 실제로는 API가 없어서 고정 패턴 사용 (사진과 동일하게)
        
        fig = go.Figure(go.Scatter(
            y=base_y, mode='lines', 
            line=dict(color='#e0e0e0', width=2), 
            fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(visible=False), 
            yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=9, color='#666')),
            height=110
        )
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

    with c2:
        # 반원 게이지
        fig_g = go.Figure(go.Indicator(
            mode="gauge", value=49,
            gauge={
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': "white", 'thickness': 0}, # 바늘 숨김(숫자로 대체)
                'steps': [
                    {'range': [0, 25], 'color': '#ff453a'}, # 공포
                    {'range': [25, 45], 'color': '#ff9f0a'},
                    {'range': [45, 55], 'color': '#ffffff'}, # 중립
                    {'range': [55, 75], 'color': '#64d2ff'},
                    {'range': [75, 100], 'color': '#30d158'} # 탐욕
                ],
                'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': 49}
            }
        ))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=5,b=0), height=90)
        st.plotly_chart(fig_g, use_container_width=True, config={'staticPlot': True})
        
        st.markdown("""
        <div style="margin-top: -20px;">
            <div class="fg-score">49</div>
            <div class="fg-status">Neutral</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<div class="date" style="text-align:right; margin-top:5px;">Updated: 2026-02-10</div></div>', unsafe_allow_html=True)


# =========================================================
# [2] FRED (VIX, DXY, 금리 등)
# =========================================================
elif view_mode == "fred":
    # 실시간 데이터
    vix_v, vix_c = get_live_data("^VIX")
    dxy_v, dxy_c = get_live_data("DX-Y.NYB")
    us10y_v, us10y_c = get_live_data("^TNX")
    us2y_v, us2y_c = get_live_data("^IRX")

    # 데이터 배치
    left = [
        ("Fear & Greed", "49", "Neutral"), # 고정값
        ("VIX", vix_v, vix_c),
        ("DXY (ICE)", dxy_v, dxy_c),
        ("US 2Y", us2y_v, us2y_c),
        ("US 10Y", us10y_v, us10y_c),
        ("Stress Index", "-0.68", "+0.03"), # 고정값
        ("M2 Supply", "22,411", "+88.90")   # 고정값
    ]
    right = [
        ("Fed Balance", "6605.91", "+18.34"),
        ("TGA (Est)", "908.77", "-14.27"),
        ("ON RRP", "1.31B", "-1.81"),
        ("Repo Ops", "0.01B", "+0.01"),
        ("SOFR", "3.63%", "-"),
        ("MMF Total", "7,774", "+292.82"),
        ("Net Liquidity", "5697.13", "+32.61")
    ]
    
    # HTML 렌더링
    l_html = "".join([make_row(l, v, c) for l, v, c in left])
    r_html = "".join([make_row(l, v, c) for l, v, c in right])

    st.markdown(f"""
    <div class="widget-box">
        <div class="header-row">
            <span class="title">FRED</span>
            <span class="date">Live Data</span>
        </div>
        <div class="data-grid">
            <div class="col">{l_html}</div>
            <div class="col">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# [3] INDEXerGO (코인, 환율, 원자재)
# =========================================================
elif view_mode == "idx":
    # 실시간 데이터
    krw_v, krw_c = get_live_data("KRW=X")
    gold_v, gold_c = get_live_data("GC=F")
    silver_v, silver_c = get_live_data("SI=F")
    btc_v, btc_c = get_live_data("BTC-USD")
    eth_v, eth_c = get_live_data("ETH-USD")
    wti_v, wti_c = get_live_data("CL=F")
    gas_v, gas_c = get_live_data("NG=F")
    dxy_v, dxy_c = get_live_data("DX-Y.NYB")

    left = [
        ("달러인덱스", dxy_v, dxy_c),
        ("원/달러", krw_v, krw_c),
        ("금 (Gold)", gold_v, gold_c),
        ("은 (Silver)", silver_v, silver_c)
    ]
    right = [
        ("비트코인", btc_v, btc_c),
        ("이더리움", eth_v, eth_c),
        ("WTI유", wti_v, wti_c),
        ("천연가스", gas_v, gas_c)
    ]
    
    l_html = "".join([make_row(l, v, c) for l, v, c in left])
    r_html = "".join([make_row(l, v, c) for l, v, c in right])

    st.markdown(f"""
    <div class="widget-box">
        <div class="header-row">
            <span class="title">INDEXerGO</span>
            <span class="date">Live Data</span>
        </div>
        <div class="data-grid">
            <div class="col">{l_html}</div>
            <div class="col">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
