import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

# 1. 페이지 설정
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 스타일 (디자인 유지)
css_style = """
<style>
    .stApp { background-color: #000000 !important; }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 0px !important; max-width: 100% !important; }

    .widget-container {
        background-color: #1c1c1e;
        border-radius: 22px;
        padding: 16px;
        font-family: -apple-system, sans-serif;
        height: 100vh;
    }
    .header-box { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
    .widget-title { color: white; font-size: 18px; font-weight: 700; }
    .widget-date { color: #8e8e93; font-size: 12px; }

    .grid-container { display: flex; gap: 20px; }
    .grid-column { flex: 1; display: flex; flex-direction: column; gap: 6px; }

    .data-row { display: flex; justify-content: space-between; align-items: center; line-height: 1.4; }
    .label { color: #b0b0b0; font-size: 13px; font-weight: 500; }
    .value-group { display: flex; align-items: center; gap: 6px; }
    .change-text { font-size: 12px; font-weight: 600; }
    .main-value { color: white; font-size: 15px; font-weight: 700; text-align: right; min-width: 40px; }

    .up { color: #ff453a; }
    .down { color: #0a84ff; }
    .neutral { color: #8e8e93; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 실시간 데이터 가져오기 함수 (yfinance)
# ---------------------------------------------------------
@st.cache_data(ttl=60) # 60초마다 갱신 (서버 부하 방지)
def get_market_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # 2일치 데이터를 가져와서 전일 대비 변동률 계산
        hist = ticker.history(period="2d")
        
        if len(hist) < 2:
            return "Loading..", "0.00%"
            
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        
        # 등락률 계산
        change_pct = ((current - prev) / prev) * 100
        change_str = f"{change_pct:+.2f}%"
        
        # 값 포맷팅 (천 단위 콤마)
        if current >= 1000:
            value_str = f"{current:,.0f}"
        else:
            value_str = f"{current:,.2f}"
            
        return value_str, change_str
    except:
        return "Error", "0.00%"

# HTML 행 생성 함수
def make_row_html(label, value, change):
    if "+" in change: color = "up"
    elif "-" in change: color = "down"
    else: color = "neutral"
    
    return f"""
    <div class="data-row">
        <span class="label">{label}</span>
        <div class="value-group">
            <span class="change-text {color}">{change}</span>
            <span class="main-value">{value}</span>
        </div>
    </div>
    """

# ---------------------------------------------------------
# 4. 화면 구성 로직
# ---------------------------------------------------------
view_mode = st.query_params.get("view", "fred")

# [1] FRED 위젯
if view_mode == "fred":
    # (A) 실시간 데이터 호출
    vix_v, vix_c = get_market_data("^VIX")
    dxy_v, dxy_c = get_market_data("DX-Y.NYB")
    us10y_v, us10y_c = get_market_data("^TNX")
    us2y_v, us2y_c = get_market_data("^IRX") # 13주(단기)로 대체하거나 ^TNX 사용. 야후에 2년물(^2YY)이 잘 없음.
    
    # (B) 고정 데이터 (API 필요함) - 디자인 유지를 위해 고정값 사용
    # * Fed Balance, M2 등은 FRED API 키가 있어야 실시간 가능
    
    left_data = [
        ("Fear & Greed", "49", "Neutral"), # 별도 크롤링 필요
        ("VIX", vix_v, vix_c),             # 실시간
        ("DXY (ICE)", dxy_v, dxy_c),       # 실시간
        ("US 2Y (Yield)", us2y_v, us2y_c), # 실시간
        ("US 10Y", us10y_v, us10y_c),      # 실시간
        ("Stress Index", "-0.68", "+0.03"),
        ("M2 Supply", "22,411", "+88.90"),
    ]
    right_data = [
        ("Fed Balance", "6605.91", "+18.34"),
        ("TGA (Est)", "908.77", "-14.27"),
        ("ON RRP", "1.31B", "-1.81"),
        ("Repo Ops", "0.01B", "+0.01"),
        ("SOFR", "3.63%", "-"),
        ("MMF Total", "7,774", "+292.82"),
        ("Net Liquidity", "5697.13", "+32.61"),
    ]

    l_html = "".join([make_row_html(l,v,c) for l,v,c in left_data])
    r_html = "".join([make_row_html(l,v,c) for l,v,c in right_data])

    st.markdown(f"""
    <div class="widget-container">
        <div class="header-box"><span class="widget-title">FRED</span><span class="widget-date">Live Data</span></div>
        <div class="grid-container">
            <div class="grid-column">{l_html}</div>
            <div class="grid-column">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# [2] INDEXerGO 위젯
elif view_mode == "idx":
    # 실시간 데이터 호출
    krw_v, krw_c = get_market_data("KRW=X")   # 원달러
    gold_v, gold_c = get_market_data("GC=F")  # 금
    silver_v, silver_c = get_market_data("SI=F") # 은
    btc_v, btc_c = get_market_data("BTC-USD") # 비트코인
    eth_v, eth_c = get_market_data("ETH-USD") # 이더리움
    wti_v, wti_c = get_market_data("CL=F")    # WTI유
    gas_v, gas_c = get_market_data("NG=F")    # 천연가스
    
    left_data = [
        ("달러인덱스", dxy_v if 'dxy_v' in locals() else get_market_data("DX-Y.NYB")[0], get_market_data("DX-Y.NYB")[1]),
        ("원/달러", krw_v, krw_c),
        ("금 (Gold)", gold_v, gold_c),
        ("은 (Silver)", silver_v, silver_c),
    ]
    right_data = [
        ("비트코인", btc_v, btc_c),
        ("이더리움", eth_v, eth_c),
        ("WTI유", wti_v, wti_c),
        ("천연가스", gas_v, gas_c),
    ]

    l_html = "".join([make_row_html(l,v,c) for l,v,c in left_data])
    r_html = "".join([make_row_html(l,v,c) for l,v,c in right_data])

    st.markdown(f"""
    <div class="widget-container">
        <div class="header-box"><span class="widget-title">INDEXerGO</span><span class="widget-date">Live Data</span></div>
        <div class="grid-container">
            <div class="grid-column">{l_html}</div>
            <div class="grid-column">{r_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# [3] Fear & Greed (디자인용 고정값)
elif view_mode == "fg":
    # F&G는 CNN에서 크롤링해야 하는데 차단이 심해서 고정값 유지 권장
    st.markdown("""
    <div class="widget-container">
        <div class="header-box"><span class="widget-title">Fear & Greed Index</span><span class="widget-date">(Last 3 months)</span></div>
    """, unsafe_allow_html=True)
    
    # 그래프는 고정값 사용 (레이아웃 유지)
    c1, c2 = st.columns([1.8, 1])
    with c1:
        fig = go.Figure(go.Scatter(y=[50,48,40,35,30,25,20,30,40,50,60,55,50,49], mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0,100], showgrid=True, gridcolor='#333'), height=120)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    with c2:
        fig_g = go.Figure(go.Indicator(mode="gauge", value=49, gauge={'axis':{'range':[0,100],'visible':False},'bar':{'color':'white','thickness':0},'steps':[{'range':[0,25],'color':'#ff453a'},{'range':[25,45],'color':'#ff9f0a'},{'range':[45,55],'color':'#ffffff'},{'range':[55,75],'color':'#64d2ff'},{'range':[75,100],'color':'#30d158'}]}))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=10,b=0), height=100)
        st.plotly_chart(fig_g, use_container_width=True, config={'staticPlot': True})
        st.markdown('<div style="text-align:center; margin-top:-25px; color:white; font-size:22px; font-weight:800;">49<br><span style="font-size:13px; color:#ccc;">Neutral</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
