import streamlit as st
import plotly.graph_objects as go

# 1. 페이지 설정: 여백 제로화
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 스타일 정의 (중괄호 충돌 방지를 위해 별도 변수 처리)
CSS_STYLE = """
<style>
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding: 10px 5px !important; max-width: 100% !important; }
    
    /* 통합 박스 디자인 */
    .widget-box {
        background-color: #1e2227;
        border-radius: 15px;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid #2d3139;
    }
    .widget-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .widget-title { color: white; font-size: 1rem; font-weight: 800; }
    .widget-date { color: #888; font-size: 0.7rem; }
    
    /* 2열 그리드 구현 (가장 중요) */
    .grid-wrapper {
        display: flex;
        gap: 10px;
    }
    .grid-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    
    /* 개별 행 디자인 */
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2px 0;
    }
    .lbl { color: #b0b8c4; font-size: 0.75rem; font-weight: 500; }
    .val-group { display: flex; align-items: baseline; gap: 4px; }
    .chg { font-size: 0.7rem; font-weight: 600; }
    .val { color: white; font-size: 0.85rem; font-weight: 700; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# 3. 데이터 로우 생성 함수
def make_row(label, value, change):
    color = "#ff4b4b" if "+" in change else "#4b88ff" if "-" in change else "#888"
    return f'''
    <div class="data-row">
        <span class="lbl">{label}</span>
        <div class="val-group">
            <span class="chg" style="color: {color};">{change}</span>
            <span class="val">{value}</span>
        </div>
    </div>
    '''

# 4. URL 파라미터 확인
view = st.query_params.get("view", "fg")

# --- [VIEW] FRED / INDEXerGO 통합 렌더링 ---
if view in ["fred", "idx"]:
    if view == "fred":
        title = "FRED"
        left = [("Fear & Greed", "49", "0.00%"), ("VIX", "17.43", "+0.07"), ("DXY", "96.78", "-0.04"), ("US 2Y", "3.59%", "-0.00"), ("US 10Y", "4.16%", "-0.04"), ("Stress Index", "-0.68", "+0.03"), ("M2 Supply", "22,411", "+88.90")]
        right = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("Repo Ops", "0.01B", "+0.01"), ("SOFR", "3.63%", "-"), ("MMF Total", "7,774", "+292.82"), ("Net Liquidity", "5697.13", "+32.61")]
    else:
        title = "INDEXerGO"
        left = [("달러인덱스", "97", "-0.04%"), ("원/달러", "1,457", "-0.40%"), ("금 (Gold)", "5,077", "+0.52%"), ("은 (Silver)", "82", "-0.54%")]
        right = [("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%"), ("WTI유", "64", "+0.11%"), ("천연가스", "3.14", "-0.06%")]

    l_html = "".join([make_row(d[0], d[1], d[2]) for d in left])
    r_html = "".join([make_row(d[0], d[1], d[2]) for d in right])

    st.markdown(f'''
    <div class="widget-box">
        <div class="widget-header">
            <span class="widget-title">{title}</span>
            <span class="widget-date">2026/02/11 15:00</span>
        </div>
        <div class="grid-wrapper">
            <div class="grid-col">{l_html}</div>
            <div class="grid-col">{r_html}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# --- [VIEW] Fear & Greed ---
else:
    st.markdown('<div class="widget-box"><div class="widget-header"><span class="widget-title">Fear & Greed Index</span></div>', unsafe_allow_html=True)
    # 그래프 및 게이지 차트 코드 (기존과 동일하게 유지)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = 49,
        number = {'font': {'color': 'white', 'size': 35}},
        gauge = {'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': "white", 'thickness': 1},
                 'steps': [{'range': [0, 25], 'color': '#ff6b6b'}, {'range': [25, 45], 'color': '#feca57'},
                           {'range': [45, 55], 'color': '#fff'}, {'range': [55, 75], 'color': '#48dbfb'},
                           {'range': [75, 100], 'color': '#1dd1a1'}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20,r=20,t=10,b=10), height=150)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    st.markdown('<div style="text-align:center; color:white; font-size:1.2rem; font-weight:800; margin-top:-20px;">Neutral</div></div>', unsafe_allow_html=True)
