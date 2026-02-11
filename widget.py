import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. 페이지 설정: 휴대폰 화면에 맞춰 여백 완전 제거
# ---------------------------------------------------------
st.set_page_config(page_title="Macro Mobile Widget", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 배경색 및 기본 폰트 설정 */
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    
    /* 모바일 화면을 위해 좌우 여백을 최소화 (0.3rem) */
    .block-container {
        padding: 0.5rem 0.3rem !important;
        max-width: 100% !important;
    }
    
    /* [핵심] 통합 위젯 박스 (사진과 동일한 라운드 및 배경) */
    .widget-box {
        background-color: #1e2227;
        border-radius: 20px;
        padding: 12px 12px;
        margin-bottom: 12px;
        border: 1px solid #2d3139;
    }
    
    /* 헤더 스타일 (제목 + 날짜) */
    .widget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding: 0 4px;
    }
    .widget-title { color: white; font-size: 1.1rem; font-weight: 800; }
    .widget-date { color: #888; font-size: 0.7rem; }
    
    /* [중요] 2열 그리드 설정: 여백(gap)을 최소로 조절 */
    .data-grid {
        display: grid;
        grid-template-columns: 1fr 1fr; /* 1:1 비율 2열 */
        column-gap: 12px;               /* 열 사이 간격 좁게 */
        row-gap: 2px;                  /* 행 사이 간격 아주 촘촘하게 */
    }
    
    /* 개별 데이터 행 디자인 (양끝 정렬) */
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 3px 0;
    }
    
    /* 텍스트 스타일링 */
    .lbl { color: #b0b8c4; font-size: 0.8rem; font-weight: 500; white-space: nowrap; }
    .val-group { display: flex; align-items: baseline; gap: 4px; }
    .chg { font-size: 0.75rem; font-weight: 600; }
    .val { color: white; font-size: 0.95rem; font-weight: 700; letter-spacing: -0.2px; }
    
    /* Fear & Greed 전용 스타일 */
    .fg-val { font-size: 1.4rem; font-weight: 800; color: white; margin-top: -15px; }
    .fg-lbl { font-size: 0.85rem; font-weight: 600; color: #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. HTML 데이터 로우 생성 함수
# ---------------------------------------------------------
def get_row_html(label, value, change_str):
    # 한국식 색상: 상승(+) 빨강, 하락(-) 파랑
    if "+" in change_str:
        color = "#ff4b4b"
    elif "-" in change_str:
        color = "#4b88ff"
    else:
        color = "#888888"
        
    return f"""
    <div class="data-row">
        <span class="lbl">{label}</span>
        <div class="val-group">
            <span class="chg" style="color: {color};">{change_str}</span>
            <span class="val">{value}</span>
        </div>
    </div>
    """

# ---------------------------------------------------------
# 3. 섹션 블록 렌더링 함수 (2열 통합형)
# ---------------------------------------------------------
def render_mobile_section(title, date_str, left_data, right_data):
    left_html = "".join([get_row_html(i[0], i[1], i[2]) for i in left_data])
    right_html = "".join([get_row_html(i[0], i[1], i[2]) for i in right_data])
    
    st.markdown(f"""
    <div class="widget-box">
        <div class="widget-header">
            <span class="widget-title">{title}</span>
            <span class="widget-date">{date_str}</span>
        </div>
        <div class="data-grid">
            <div class="col-left">{left_html}</div>
            <div class="col-right">{right_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 차트 생성 (Fear & Greed)
# ---------------------------------------------------------
def make_fg_charts():
    y = [50, 48, 30, 25, 20, 25, 30, 40, 45, 50, 55, 60, 58, 55, 60, 65, 60, 55, 50, 48, 49]
    line = go.Figure(go.Scatter(y=y, mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
    line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=5, t=5, b=5), 
        xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=7, color='gray')),
        height=90
    )

    gauge = go.Figure(go.Indicator(
        mode = "gauge", value = 49,
        gauge = {
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps': [
                {'range': [0, 25], 'color': '#ff6b6b'}, {'range': [25, 45], 'color': '#feca57'},
                {'range': [45, 55], 'color': '#ffffff'}, {'range': [55, 75], 'color': '#48dbfb'},
                {'range': [75, 100], 'color': '#1dd1a1'}
            ],
            'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': 49}
        }
    ))
    gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=0), height=85)
    return line, gauge

# ---------------------------------------------------------
# 5. 메인 화면 구성
# ---------------------------------------------------------

# [섹션 1] Fear & Greed Index
st.markdown("""<div class="widget-box">
<div class="widget-header"><span class="widget-title">Fear & Greed Index</span><span class="widget-date">(Last 3 months)</span></div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1.6, 1])
l_chart, g_chart = make_fg_charts()
with c1:
    st.plotly_chart(l_chart, use_container_width=True, config={'staticPlot': True})
with c2:
    st.plotly_chart(g_chart, use_container_width=True, config={'staticPlot': True})
    st.markdown("""<div style="text-align:center; margin-top:-25px;"><div class="fg-val">49</div><div class="fg-lbl">Neutral</div><div style="font-size:0.6rem; color:#888;">2026-02-10 23:18</div></div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# [섹션 2] FRED (2열 통합)
fred_l = [("Fear & Greed", "49", "Neutral"), ("VIX", "17.43", "+0.07"), ("DXY (ICE)", "96.78", "-0.04"), ("US 2Y", "3.59%", "-0.00"), ("US 10Y", "4.16%", "-0.04"), ("Stress Index", "-0.68", "+0.03"), ("M2 Supply", "22,411", "+88.90")]
fred_r = [("Fed Balance", "6605.91", "+18.34"), ("TGA (Est)", "908.77", "-14.27"), ("ON RRP", "1.31B", "-1.81"), ("Repo Ops", "0.01B", "+0.01"), ("SOFR", "3.63%", "-"), ("MMF Total", "7,774", "+292.82"), ("Net Liquidity", "5697.13", "+32.61")]

render_mobile_section("FRED", "2026/2/10 23:18", fred_l, fred_r)

# [섹션 3] INDEXerGO (2열 통합)
idx_l = [("달러인덱스", "97", "-0.04%"), ("원/달러", "1,457", "-0.40%"), ("금 (Gold)", "5,077", "+0.52%"), ("은 (Silver)", "82", "-0.54%")]
idx_r = [("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%"), ("WTI유", "64", "+0.11%"), ("천연가스", "3.14", "-0.06%")]

render_mobile_section("INDEXerGO", "2026-02-10 23:18", idx_l, idx_r)
