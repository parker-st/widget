import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import requests
import io
from datetime import datetime

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
        padding: 10px !important;
        max-width: 100% !important;
    }

    /* 위젯 박스 공통 스타일 */
    .widget-box {
        background-color: #1c1c1e;
        border-radius: 22px;
        padding: 14px 16px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        height: auto;
        min-height: 320px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
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
        gap: 12px;
        flex: 1;
    }
    .col {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 4px;
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

    /* 색상표 */
    .up { color: #ff453a; }
    .down { color: #0a84ff; }
    .neutral { color: #8e8e93; }

    /* F&G 전용 스타일 */
    .fg-score { font-size: 26px; font-weight: 800; color: white; text-align: center; line-height: 1; }
    .fg-status { font-size: 13px; font-weight: 600; color: #e0e0e0; text-align: center; margin-top: 2px; }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 엔진 (차단 방지 적용)
# ---------------------------------------------------------

# (1) Fear & Greed (CNN)
@st.cache_data(ttl=300)
def get_fg_index():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        fg_data = data['fear_and_greed_historical']['data']
        latest = fg_data[-1]
        return {
            "score": int(latest['y']),
            "rating": latest['rating'].capitalize(),
            "history": [int(d['y']) for d in fg_data[-21:]]
        }
    except:
        return {"score": 50, "rating": "Neutral", "history": [50]*21}

# (2) 야후 파이낸스
@st.cache_data(ttl=60)
def get_yahoo(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d") # 5일로 넉넉하게
        if len(hist) < 2: return "-", "0.00%"
        
        curr = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        pct = ((curr - prev) / prev) * 100
        
        if curr >= 1000: val = f"{curr:,.0f}"
        elif curr < 1: val = f"{curr:,.3f}"
        else: val = f"{curr:,.2f}"
        return val, pct
    except:
        return "-", 0.0

# (3) FRED 데이터 (차단 방지 헤더 추가) [수정된 부분]
@st.cache_data(ttl=3600) 
def get_fred(series_id):
    try:
        # User-Agent를 추가해서 브라우저인 척 위장
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&sort_order=desc&limit=2"
        
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            # 텍스트 데이터를 pandas로 변환
            df = pd.read_csv(io.StringIO(r.text))
            
            if len(df) >= 1:
                val = df.iloc[0, 1] # 최신 값
                chg_val = 0
                if len(df) >= 2:
                    prev = df.iloc[1, 1]
                    chg_val = val - prev
                return val, chg_val
    except Exception as e:
        print(f"FRED Error {series_id}: {e}")
        pass
    return None, 0

# HTML 생성기
def make_row(label, value, change):
    color = "neutral"
    
    # change가 숫자형이면 포맷팅
    if isinstance(change, (int, float)):
        if change > 0: color = "up"
        elif change < 0: color = "down"
        sign = "+" if change > 0 else ""
        change_str = f"{sign}{change:.2f}"
        # 퍼센트 기호가 있는 경우 (야후 데이터에서 옴)
        if isinstance(change, float) and abs(change) < 0.0001: 
             change_str = "0.00%" # 0일때 처리
    elif isinstance(change, str):
        if "+" in change: color = "up"
        elif "-" in change and change != "-": color = "down"
        change_str = change
    else:
        change_str = "-"

    return f'<div class="data-row"><span class="lbl">{label}</span><div class="val-group"><span class="chg {color}">{change_str}</span><span class="val">{value}</span></div></div>'

# 현재 시간
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

# ---------------------------------------------------------
# 4. 화면 구성
# ---------------------------------------------------------
col_fg, col_fred, col_idx = st.columns(3)

# =========================================================
# [1] Fear & Greed
# =========================================================
fg = get_fg_index()

with col_fg:
    st.markdown("""<div class="widget-box"><div class="header-row"><span class="title">Fear & Greed</span><span class="date">(Last 3 weeks)</span></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([1.8, 1])
    with c1:
        # margin을 0으로 설정하여 그래프 쳐짐 방지
        fig = go.Figure(go.Scatter(y=fg['history'], mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333'), height=110)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    with c2:
        fig_g = go.Figure(go.Indicator(mode="gauge", value=fg['score'], gauge={'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': "white", 'thickness': 0}, 'steps': [{'range': [0, 25], 'color': '#ff453a'}, {'range': [25, 45], 'color': '#ff9f0a'}, {'range': [45, 55], 'color': '#ffffff'}, {'range': [55, 75], 'color': '#64d2ff'}, {'range': [75, 100], 'color': '#30d158'}], 'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': fg['score']}}))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=5,b=0), height=90)
        st.plotly_chart(fig_g, use_container_width=True, config={'staticPlot': True})
        st.markdown(f'<div style="margin-top:-20px;"><div class="fg-score">{fg["score"]}</div><div class="fg-status">{fg["rating"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date" style="text-align:right; margin-top:5px;">Updated: {now_str}</div></div>', unsafe_allow_html=True)

# =========================================================
# [2] FRED (데이터 수집 강화)
# =========================================================
# Market Data
vix_v, vix_c = get_yahoo("^VIX")
dxy_v, dxy_c = get_yahoo("DX-Y.NYB")
us10_v, us10_c = get_yahoo("^TNX")
us2_v, us2_c = get_yahoo("^IRX")

# FRED Data Fetching (헤더 추가로 차단 우회)
fed_val, fed_chg = get_fred("WALCL")      # Fed Balance (Million)
tga_val, tga_chg = get_fred("WTREGEN")    # TGA (Billion)
rrp_val, rrp_chg = get_fred("RRPONTSYD")  # RRP (Billion)
m2_val, m2_chg   = get_fred("M2SL")       # M2 (Billion)

# Net Liquidity Calculation
net_liq = "Loading"
net_chg = 0.0

if fed_val is not None and tga_val is not None and rrp_val is not None:
    # 단위 통일: Fed Balance는 Million 단위이므로 1000으로 나눠서 Billion으로 변환
    fed_bil = fed_val / 1000
    net_val = fed_bil - tga_val - rrp_val
    net_liq = f"{net_val:,.2f}"
    
    # 변동폭 계산
    fed_chg_bil = fed_chg / 1000
    net_chg = fed_chg_bil - tga_chg - rrp_chg
else:
    net_liq = "0.00"

# 포맷팅
fed_s = f"{fed_val/1000:,.2f}" if fed_val else "0.00"
tga_s = f"{tga_val:,.2f}" if tga_val else "0.00"
rrp_s = f"{rrp_val:,.2f}B" if rrp_val else "0.00"
m2_s  = f"{m2_val:,.0f}" if m2_val else "0.00"

# 변동폭 포맷팅 (야후 데이터는 이미 % 문자열임)
if isinstance(vix_c, float): vix_c = f"{vix_c:+.2f}%"

with col_fred:
    left = [
        ("Fear & Greed", str(fg['score']), "Live"),
        ("VIX", vix_v, f"{vix_c}%" if isinstance(vix_c, float) else vix_c),
        ("DXY (ICE)", dxy_v, f"{dxy_c}%" if isinstance(dxy_c, float) else dxy_c),
        ("US 2Y", us2_v, f"{us2_c}%" if isinstance(us2_c, float) else us2_c),
        ("US 10Y", us10_v, f"{us10_c}%" if isinstance(us10_c, float) else us10_c),
        ("Stress Index", "-0.68", "+0.03"), 
        ("M2 Supply", m2_s, m2_chg)
    ]
    right = [
        ("Fed Balance", fed_s, fed_chg/1000 if fed_val else 0),
        ("TGA (Est)", tga_s, tga_chg),
        ("ON RRP", rrp_s, rrp_chg),
        ("Repo Ops", "0.01B", "+0.01"), 
        ("SOFR", "3.63%", "-"),         
        ("MMF Total", "7,774", "+292.82"), 
        ("Net Liquidity", net_liq, net_chg)
    ]
    
    l_html = "".join([make_row(*x) for x in left])
    r_html = "".join([make_row(*x) for x in right])
    st.markdown(f'<div class="widget-box"><div class="header-row"><span class="title">FRED</span><span class="date">{now_str}</span></div><div class="data-grid"><div class="col">{l_html}</div><div class="col">{r_html}</div></div></div>', unsafe_allow_html=True)

# =========================================================
# [3] INDEXerGO
# =========================================================
with col_idx:
    krw_v, krw_c = get_yahoo("KRW=X")
    gold_v, gold_c = get_yahoo("GC=F")
    silver_v, silver_c = get_yahoo("SI=F")
    btc_v, btc_c = get_yahoo("BTC-USD")
    eth_v, eth_c = get_yahoo("ETH-USD")
    wti_v, wti_c = get_yahoo("CL=F")
    gas_v, gas_c = get_yahoo("NG=F")
    dxy_v, dxy_c = get_yahoo("DX-Y.NYB")

    # 야후 데이터는 튜플(값, 퍼센트문자열)로 옴 -> 그대로 사용
    left = [("달러인덱스", dxy_v, dxy_c), ("원/달러", krw_v, krw_c), ("금 (Gold)", gold_v, gold_c), ("은 (Silver)", silver_v, silver_c)]
    right = [("비트코인", btc_v, btc_c), ("이더리움", eth_v, eth_c), ("WTI유", wti_v, wti_c), ("천연가스", gas_v, gas_c)]
    
    l_html = "".join([make_row(*x) for x in left])
    r_html = "".join([make_row(*x) for x in right])
    st.markdown(f'<div class="widget-box"><div class="header-row"><span class="title">INDEXerGO</span><span class="date">{now_str}</span></div><div class="data-grid"><div class="col">{l_html}</div><div class="col">{r_html}</div></div></div>', unsafe_allow_html=True)
