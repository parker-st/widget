import streamlit as st
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 설정 (중괄호 충돌 방지를 위해 별도 처리)
style_html = """
<style>
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding: 8px !important; }
    .widget-box {
        background-color: #1e2227; border-radius: 20px;
        padding: 15px; border: 1px solid #2d3139; font-family: sans-serif;
    }
    .header-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
    .title { color: white; font-size: 1.1rem; font-weight: 800; }
    .date { color: #888; font-size: 0.75rem; }
    .data-grid { display: flex; gap: 20px; }
    .col { flex: 1; display: flex; flex-direction: column; gap: 4px; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 2px 0; }
    .lbl { color: #b0b8c4; font-size: 0.85rem; }
    .val-group { display: flex; align-items: baseline; gap: 6px; }
    .chg { font-size: 0.8rem; font-weight: 600; }
    .val { color: white; font-size: 1rem; font-weight: 700; }
    .up { color: #ff4b4b; }  /* 상승 빨강 */
    .down { color: #4b88ff; } /* 하락 파랑 */
</style>
"""
st.markdown(style_html, unsafe_allow_html=True)

# 데이터 행 생성 (안전한 % 방식)
def render_row(label, value, change):
    color_class = "up" if "+" in change else "down" if "-" in change else ""
    return '''
    <div class="data-row">
        <span class="lbl">%s</span>
        <div class="val-group">
            <span class="chg %s">%s</span>
            <span class="val">%s</span>
        </div>
    </div>
    ''' % (label, color_class, change, value)

# 3. 뷰(View) 판별
view = st.query_params.get("view", "fg")

# --- Fear & Greed ---
if view == "fg":
    st.markdown('<div class="widget-box"><div class="header-row"><span class="title">Fear & Greed Index</span></div>', unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=49, number={'font': {'color': 'white', 'size': 35}},
        gauge={'axis':{'range':[0,100],'visible':False},'bar':{'color':'white','thickness':1},
        'steps':[{'range':[0,25],'color':'#ff6b6b'},{'range':[25,45],'color':'#feca57'},{'range':[45,55],'color':'#fff'},{'range':[55,75],'color':'#48dbfb'},{'range':[75,100],'color':'#1dd1a1'}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20,r=20,t=10,b=10), height=150)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    st.markdown('<div style="text-align:center; color:white; font-size:1.2rem; font-weight:800; margin-top:-20px;">Neutral</div></div>', unsafe_allow_html=True)

# --- FRED / INDEXerGO ---
else:
    if view == "fred":
        title, date = "FRED", "2026/02/11 15:00"
        left = [("Fear & Greed", "49", "Neutral"), ("VIX", "17.43", "+0.07"), ("DXY", "96.78", "-0.04"), ("US 2Y", "3.59%", "-0.00")]
        right = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("SOFR", "3.63%", "-")]
    else:
        title, date = "INDEXerGO", "2026-02-11 15:00"
        left = [("달러인덱스", "97", "-0.04%"), ("원/달러", "1,457", "-0.40%")]
        right = [("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%")]

    l_html = "".join([render_row(d[0], d[1], d[2]) for d in left])
    r_html = "".join([render_row(d[0], d[1], d[2]) for d in right])
    
    st.markdown('''<div class="widget-box"><div class="header-row"><span class="title">%s</span><span class="date">%s</span></div>
        <div class="data-grid"><div class="col">%s</div><div class="col">%s</div></div></div>''' % (title, date, l_html, r_html), unsafe_allow_html=True)
