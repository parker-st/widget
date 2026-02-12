import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import requests
import re
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. CSS 스타일
# ---------------------------------------------------------
style_css = """
<style>
    .stApp { background-color: #000000 !important; }
    header, footer { visibility: hidden; }
    .block-container { padding: 10px !important; max-width: 100% !important; }
    
    .widget-box {
        background-color: #1c1c1e;
        border-radius: 22px;
        padding: 14px 16px;
        font-family: -apple-system, sans-serif;
        height: auto;
        min-height: 320px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }
    
    .header-row { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 10px; height: 24px; }
    .title { color: white; font-size: 17px; font-weight: 700; }
    .date { color: #8e8e93; font-size: 11px; font-weight: 400; margin-bottom: 2px; }
    
    .data-grid { display: flex; flex-direction: row; gap: 12px; flex: 1; }
    .col { flex: 1; display: flex; flex-direction: column; gap: 4px; }
    
    .data-row { display: flex; justify-content: space-between; align-items: center; width: 100%; min-height: 18px; }
    .lbl { color: #b0b0b0; font-size: 13px; font-weight: 500; }
    .val-group { display: flex; align-items: center; gap: 6px; }
    .chg { font-size: 12px; font-weight: 600; }
    .val { color: white; font-size: 14px; font-weight: 700; text-align: right; min-width: 45px; }
    
    .up { color: #ff453a; }
    .down { color: #0a84ff; }
    .neutral { color: #8e8e93; }
    
    .fg-score { font-size: 26px; font-weight: 800; color: white; text-align: center; line-height: 1; }
    .fg-status { font-size: 13px; font-weight: 600; color: #e0e0e0; text-align: center; margin-top: 2px; }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 가져오기 함수들
# ---------------------------------------------------------

# [핵심] CNN Fear & Greed Index 실시간 크롤링
@st.cache_data(ttl=300) # 5분마다 갱신
def get_fear_greed_live():
    # 기본값 (실패 시 사용)
    default_data = {"score": 50, "rating": "Neutral", "history": [50]*7}
    
    try:
        # CNN 데이터 API 엔드포인트
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.cnn.com/"
        }
        
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            fg_data = data['fear_and_greed_historical']['data']
            
            # 최신 데이터 가져오기
            latest = fg_data[-1]
            score = int(latest['y'])
            rating = latest['rating'].capitalize() # e.g., "Greed"
            
            # 그래프용 과거 데이터 (최근 21개)
            history = [int(d['y']) for d in fg_data[-21:]]
            
            return {"score": score, "rating": rating, "history": history}
    except Exception as e:
        print(f"CNN Fetch Error: {e}")
    
    return default_data

# 야후 파이낸스 데이터
@st.cache_data(ttl=60)
def get_live_data(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) < 2: return "-", "0.00%"
        curr = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((curr - prev) / prev) * 100
        
        if curr >= 1000: val_str = f"{curr:,.0f}"
        elif curr < 1: val_str = f"{curr:,.3f}"
        else: val_str = f"{curr:,.2f}"
            
        return val_str, f"{change_pct:+.2f}%"
    except:
        return "Err", "0.00%"

def make_row(label, value, change):
    if "+" in change: color = "up"
    elif "-" in change: color = "down"
    else: color = "neutral"
    return f'<div class="data-row"><span class="lbl">{label}</span><div class="val-group"><span class="chg {color}">{change}</span><span class="val">{value}</span></div></div>'

# 날짜 시간
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# ---------------------------------------------------------
# 4. 화면 구성
# ---------------------------------------------------------
col_fg, col_fred, col_idx = st.columns(3)

# [1] Fear & Greed Index (실시간 데이터 적용)
fg_data = get_fear_greed_live() # 여기서 51을 가져옵니다!
score = fg_data['score']
rating = fg_data['rating']
history = fg_data['history']

with col_fg:
    st.markdown("""
    <div class="widget-box" style="justify-content: center;">
        <div class="header-row" style="margin-bottom:0;">
            <span class="title">Fear & Greed Index</span>
            <span class="date">(Last 3 weeks)</span>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.8, 1])
    with c1:
        # 실시간 히스토리로 그래프 그리기
        fig = go.Figure(go.Scatter(
            y=history, mode='lines', 
            line=dict(color='#e0e0e0', width=2), 
            fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False), 
            yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=9, color='#666')),
            height=110
        )
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

    with c2:
        # 실시간 점수로 게이지 그리기
        fig_g = go.Figure(go.Indicator(
            mode="gauge", value=score, # <--- 여기가 핵심! (51)
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
                'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': score}
            }
        ))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=5,b=0), height=90)
        st.plotly_chart(fig_g, use_container_width=True, config={'staticPlot': True})
        
        st.markdown(f"""
        <div style="margin-top: -20px;">
            <div class="fg-score">{score}</div>
            <div class="fg-status">{rating}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="date" style="text-align:right; margin-top:5px;">Updated: {current_time}</div></div>', unsafe_allow_html=True)

# [2] FRED
with col_fred:
    vix_v, vix_c = get_live_data("^VIX")
    dxy_v, dxy_c = get_live_data("DX-Y.NYB")
    us10y_v, us10y_c = get_live_data("^TNX")
    us2y_v, us2y_c = get_live_data("^IRX")

    left = [("Fear & Greed", str(score), "Live"), ("VIX", vix_v, vix_c), ("DXY (ICE)", dxy_v, dxy_c), ("US 2Y", us2y_v, us2y_c), ("US 10Y", us10y_v, us10y_c), ("Stress Index", "-0.68", "+0.03"), ("M2 Supply", "22,411", "+88.90")]
    right = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("Repo Ops", "0.01B", "+0.01"), ("SOFR", "3.63%", "-"), ("MMF Total", "7,774", "+292.82"), ("Net Liquidity", "5697.13", "+32.61")]
    
    l_html = "".join([make_row(*x) for x in left])
    r_html = "".join([make_row(*x) for x in right])

    st.markdown(f"""<div class="widget-box"><div class="header-row"><span class="title">FRED</span><span class="date">{current_time}</span></div><div class="data-grid"><div class="col">{l_html}</div><div class="col">{r_html}</div></div></div>""", unsafe_allow_html=True)

# [3] INDEXerGO
with col_idx:
    krw_v, krw_c = get_live_data("KRW=X")
    gold_v, gold_c = get_live_data("GC=F")
    silver_v, silver_c = get_live_data("SI=F")
    btc_v, btc_c = get_live_data("BTC-USD")
    eth_v, eth_c = get_live_data("ETH-USD")
    wti_v, wti_c = get_live_data("CL=F")
    gas_v, gas_c = get_live_data("NG=F")
    dxy_v, dxy_c = get_live_data("DX-Y.NYB")

    left = [("달러인덱스", dxy_v, dxy_c), ("원/달러", krw_v, krw_c), ("금 (Gold)", gold_v, gold_c), ("은 (Silver)", silver_v, silver_c)]
    right = [("비트코인", btc_v, btc_c), ("이더리움", eth_v, eth_c), ("WTI유", wti_v, wti_c), ("천연가스", gas_v, gas_c)]
    
    l_html = "".join([make_row(*x) for x in left])
    r_html = "".join([make_row(*x) for x in right])

    st.markdown(f"""<div class="widget-box"><div class="header-row"><span class="title">INDEXerGO</span><span class="date">{current_time}</span></div><div class="data-grid"><div class="col">{l_html}</div><div class="col">{r_html}</div></div></div>""", unsafe_allow_html=True)
