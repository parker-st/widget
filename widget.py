import streamlit as st
import plotly.graph_objects as go

# 1. 페이지 설정: 여백 완전 제거
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 스타일 정의 (중괄호 충돌 방지를 위해 % 포맷팅 방식 사용)
style_html = """
<style>
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 10px 8px !important; max-width: 100% !important; }

    /* 사진 속 검은색 라운드 박스 구현 */
    .widget-box {
        background-color: #1e2227;
        border-radius: 20px;
        padding: 15px;
        border: 1px solid #2d3139;
        font-family: -apple-system, sans-serif;
    }
    .header-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
    .title { color: white; font-size: 1.1rem; font-weight: 800; }
    .date { color: #888; font-size: 0.75rem; }

    /* 2열 레이아웃 그리드 */
    .data-grid { display: flex; gap: 20px; }
    .col { flex: 1; display: flex; flex-direction: column; gap: 5px; }
    
    /* 데이터 행 디자인 (양끝 정렬) */
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 2px 0; }
    .lbl { color: #b0b8c4; font-size: 0.85rem; font-weight: 500; }
    .val-group { display: flex; align-items: baseline; gap: 6px; }
    .chg { font-size: 0.8rem; font-weight: 600; }
    .val { color: white; font-size: 1.0rem; font-weight: 700; letter-spacing: -0.2px; }

    /* 한국식 등락 색상 */
    .up { color: #ff4b4b; }  /* 상승 빨강 */
    .down { color: #4b88ff; } /* 하락 파랑 */
</style>
"""
st.markdown(style_html, unsafe_allow_html=True)

# 데이터 행 생성 함수 (오류 방지를 위해 % 방식 사용)
def render_row(label, value, change):
    color_class = ""
    if "+" in change: color_class = "up"
    elif "-" in change: color_class = "down"
    
    return '''
    <div class="data-row">
        <span class="lbl">%s</span>
        <div class="val-group">
            <span class="chg %s">%s</span>
            <span class="val">%s</span>
        </div>
    </div>
    ''' % (label, color_class, change, value)

# 3. URL 파라미터 확인 (view=fg, fred, idx)
view = st.query_params.get("view", "fg")

# --- [VIEW 1] Fear & Greed Index ---
if view == "fg":
    st.markdown('<div class="widget-box"><div class="header-row"><span class="title">Fear & Greed Index</span><span class="date">(Last 3 months)</span></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.8, 1])
    with c1:
        y = [50, 48, 42, 35, 30, 25, 20, 25, 30, 40, 45, 50, 55, 60, 65, 62, 58, 55, 52, 50, 49]
        fig = go.Figure(go.Scatter(y=y, mode='lines', line=dict(color='#e0e0e0', width=2.5), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=8, color='gray')), height=120)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    with c2:
        gauge = go.Figure(go.Indicator(mode="gauge", value=49, gauge={'axis':{'range':[0,100],'visible':False},'bar':{'color':'white','thickness':0},'steps':[{'range':[0,25],'color':'#ff6b6b'},{'range':[25,45],'color':'#feca57'},{'range':[45,55],'color':'#fff'},{'range':[55,75],'color':'#48dbfb'},{'range':[75,100],'color':'#1dd1a1'}],'threshold':{'line':{'color':'white','width':3},'thickness':0.8,'value':49}}))
        gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=0), height=110)
        st.plotly_chart(gauge, use_container_width=True, config={'staticPlot': True})
        st.markdown('<div style="text-align:center; color:white; font-size:1.6rem; font-weight:800; margin-top:-35px;">49<br><span style="font-size:0.9rem; color:#e0e0e0; font-weight:600;">Neutral</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- [VIEW 2] FRED ---
elif view == "fred":
    l_items = [("Fear & Greed", "49", "Neutral"), ("VIX", "17.43", "+0.07"), ("DXY (ICE)", "96.78", "-0.04"), ("US 2Y", "3.59%", "-0.00"), ("US 10Y", "4.16%", "-0.04"), ("Stress Index", "-0.68", "+0.03"), ("M2 Supply", "22,411", "+88.90")]
    r_items = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("Repo Ops", "0.01B", "+0.01"), ("SOFR", "3.63%", "-"), ("MMF Total", "7,774", "+292.82"), ("Net Liquidity", "5697.13", "+32.61")]
    l_html = "".join([render_row(d[0], d[1], d[2]) for d in l_items])
    r_html = "".join([render_row(d[0], d[1], d[2]) for d in r_items])
    
    st.markdown('''<div class="widget-box"><div class="header-row"><span class="title">FRED</span><span class="date">2026/2/11 15:00</span></div><div class="data-grid"><div class="col">%s</div><div class="col">%s</div></div></div>''' % (l_html, r_html), unsafe_allow_html=True)

# --- [VIEW 3] INDEXerGO ---
elif view == "idx":
    l_items = [("달러인덱스", "97", "-0.04%"), ("원/달러", "1,457", "-0.40%"), ("금 (Gold)", "5,077", "+0.52%"), ("은 (Silver)", "82", "-0.54%")]
    r_items = [("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%"), ("WTI유", "64", "+0.11%"), ("천연가스", "3.14", "-0.06%")]
    l_html = "".join([render_row(d[0], d[1], d[2]) for d in l_items])
    r_html = "".join([render_row(d[0], d[1], d[2]) for d in r_items])
    
    st.markdown('''<div class="widget-box"><div class="header-row"><span class="title">INDEXerGO</span><span class="date">2026-02-11 15:00</span></div><div class="data-grid"><div class="col">%s</div><div class="col">%s</div></div></div>''' % (l_html, r_html), unsafe_allow_html=True)
