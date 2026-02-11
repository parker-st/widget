import streamlit as st
import plotly.graph_objects as go
import yfinance as yf # requirements.txt에 yfinance가 있어야 합니다.

# 1. 페이지 설정 (여백 0)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. CSS 스타일 (아이폰 위젯 전용 초밀착 디자인)
# ---------------------------------------------------------
style_html = """
<style>
    /* 전체 배경: 리얼 블랙 */
    .stApp { background-color: #000000 !important; }
    header, footer, #MainMenu { visibility: hidden; }
    
    /* 화면 여백 제거 */
    .block-container {
        padding: 0px !important;
        max-width: 100% !important;
    }

    /* 위젯 박스: 아이폰 위젯 느낌의 다크 그레이 */
    .widget-box {
        background-color: #1c1c1e; 
        border-radius: 20px;
        padding: 14px 16px; /* 내부 여백 최적화 */
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        height: 100vh; /* 화면 꽉 채우기 */
        box-sizing: border-box;
    }

    /* 헤더 영역 */
    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 10px;
    }
    .title {
        color: white;
        font-size: 17px; /* 폰트 크기 조정 */
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    .date {
        color: #8e8e93;
        font-size: 11px;
        font-weight: 400;
    }

    /* 2열 그리드 (가장 중요한 부분) */
    .data-grid {
        display: flex;
        flex-direction: row;
        gap: 12px; /* 좌우 컬럼 간격: 12px (너무 넓지 않게) */
    }
    .col {
        flex: 1; /* 1:1 비율 */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 4px; /* 행 사이 간격: 4px (오밀조밀하게) */
    }

    /* 개별 데이터 행 */
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        height: 20px; /* 행 높이 고정 (정렬 맞춤) */
    }

    /* 왼쪽 라벨 */
    .lbl {
        color: #b0b0b0;
        font-size: 13px;
        font-weight: 500;
        white-space: nowrap;
    }

    /* 오른쪽 값 그룹 (등락률 + 가격) */
    .val-group {
        display: flex;
        align-items: center;
        gap: 6px; /* 숫자 사이 간격 */
    }

    /* 등락률 */
    .chg {
        font-size: 12px;
        font-weight: 600;
    }

    /* 메인 값 */
    .val {
        color: white;
        font-size: 14px;
        font-weight: 700;
        text-align: right;
        min-width: 45px; /* 숫자 위치 정렬을 위한 최소 너비 */
        letter-spacing: -0.2px;
    }

    /* 색상표 (한국 주식 스타일) */
    .up { color: #ff453a; }   /* 빨강 */
    .down { color: #0a84ff; } /* 파랑 */
    .neutral { color: #8e8e93; } /* 회색 */
</style>
"""
st.markdown(style_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 실시간 데이터 함수 (yfinance)
# ---------------------------------------------------------
@st.cache_data(ttl=60) # 1분마다 갱신
def get_data(ticker, fmt="{:,.2f}"):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) < 2: return "Loading", "0.00%"
        
        curr = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        chg = ((curr - prev) / prev) * 100
        
        # 비트코인 등 가격에 따라 포맷 자동 조정
        if curr > 1000: val_str = "{:,.0f}".format(curr)
        else: val_str = "{:,.2f}".format(curr)
            
        return val_str, f"{chg:+.2f}%"
    except:
        return "-", "0.00%"

# HTML 행 생성 함수
def render_row(label, value, change):
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
# 4. 뷰 렌더링
# ---------------------------------------------------------
view = st.query_params.get("view", "fred")

# === [VIEW 1] FRED ===
if view == "fred":
    # (A) 실시간 데이터
    vix_v, vix_c = get_data("^VIX")
    dxy_v, dxy_c = get_data("DX-Y.NYB")
    us10y_v, us10y_c = get_data("^TNX")
    us2y_v, us2y_c = get_data("^IRX")

    # (B) 화면 구성
    left = [
        ("Fear & Greed", "49", "Neutral"), # 고정값 (API 필요)
        ("VIX", vix_v, vix_c),
        ("DXY (ICE)", dxy_v, dxy_c),
        ("US 2Y", us2y_v, us2y_c),
        ("US 10Y", us10y_v, us10y_c),
        ("Stress Index", "-0.68", "+0.03"),
        ("M2 Supply", "22,411", "+88.90")
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
    
    l_html = "".join([render_row(l,v,c) for l,v,c in left])
    r_html = "".join([render_row(l,v,c) for l,v,c in right])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="header-row"><span class="title">FRED</span><span class="date">Live Data</span></div>
        <div class="data-grid"><div class="col">{l_html}</div><div class="col">{r_html}</div></div>
    </div>
    """, unsafe_allow_html=True)

# === [VIEW 2] INDEXerGO ===
elif view == "idx":
    # (A) 실시간 데이터
    krw_v, krw_c = get_data("KRW=X")
    gold_v, gold_c = get_data("GC=F")
    slv_v, slv_c = get_data("SI=F")
    btc_v, btc_c = get_data("BTC-USD")
    eth_v, eth_c = get_data("ETH-USD")
    wti_v, wti_c = get_data("CL=F")
    gas_v, gas_c = get_data("NG=F")
    dxy_v, dxy_c = get_data("DX-Y.NYB")

    left = [
        ("달러인덱스", dxy_v, dxy_c),
        ("원/달러", krw_v, krw_c),
        ("금 (Gold)", gold_v, gold_c),
        ("은 (Silver)", slv_v, slv_c)
    ]
    right = [
        ("비트코인", btc_v, btc_c),
        ("이더리움", eth_v, eth_c),
        ("WTI유", wti_v, wti_c),
        ("천연가스", gas_v, gas_c)
    ]
    
    l_html = "".join([render_row(l,v,c) for l,v,c in left])
    r_html = "".join([render_row(l,v,c) for l,v,c in right])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="header-row"><span class="title">INDEXerGO</span><span class="date">Live Data</span></div>
        <div class="data-grid"><div class="col">{l_html}</div><div class="col">{r_html}</div></div>
    </div>
    """, unsafe_allow_html=True)

# === [VIEW 3] Fear & Greed ===
elif view == "fg":
    # 레이아웃 유지를 위한 고정값 (디자인 전용)
    st.markdown("""
    <div class="widget-box">
        <div class="header-row"><span class="title">Fear & Greed Index</span><span class="date">(Last 3 months)</span></div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.8, 1])
    with c1:
        y = [50,48,42,35,30,25,20,25,30,40,45,50,55,60,65,62,58,55,52,50,49]
        fig = go.Figure(go.Scatter(y=y, mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=5,b=0), xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0,100], showgrid=True, gridcolor='#333', tickfont=dict(size=8, color='gray')), height=110)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    with c2:
        gauge = go.Figure(go.Indicator(mode="gauge", value=49, gauge={'axis':{'range':[0,100],'visible':False},'bar':{'color':'white','thickness':0},'steps':[{'range':[0,25],'color':'#ff453a'},{'range':[25,45],'color':'#ff9f0a'},{'range':[45,55],'color':'#ffffff'},{'range':[55,75],'color':'#64d2ff'},{'range':[75,100],'color':'#30d158'}]}))
        gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=10,b=0), height=100)
        st.plotly_chart(gauge, use_container_width=True, config={'staticPlot': True})
        st.markdown('<div style="text-align:center; color:white; font-size:20px; font-weight:800; margin-top:-30px; line-height:1;">49<br><span style="font-size:12px; color:#ccc;">Neutral</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
