import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. 페이지 설정: 여백 최소화
# ---------------------------------------------------------
st.set_page_config(page_title="Macro Widget", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 전체 배경 검정색 */
    .stApp { background-color: #0e1117 !important; }
    
    /* 상단 헤더, 푸터 숨김 */
    header, footer, #MainMenu {visibility: hidden;}
    
    /* 본문 여백 제거 */
    .block-container {
        padding: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* [핵심] 통합 위젯 박스 디자인 (사진과 동일하게) */
    .widget-box {
        background-color: #1e2227;
        border-radius: 16px;       /* 둥근 모서리 */
        padding: 15px 15px;        /* 내부 여백 */
        margin-bottom: 15px;       /* 박스 간 간격 */
    }
    
    /* 헤더 영역 (제목 + 날짜) */
    .widget-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 10px;
    }
    .widget-title {
        color: white;
        font-size: 1.1rem;
        font-weight: 800;
    }
    .widget-date {
        color: #888;
        font-size: 0.75rem;
    }
    
    /* 데이터 그리드 (2열 배치) */
    .data-grid {
        display: grid;
        grid-template-columns: 1fr 1fr; /* 1:1 비율로 2열 */
        column-gap: 20px;               /* 열 사이 간격 */
        row-gap: 4px;                   /* 행 사이 간격 (촘촘하게) */
    }
    
    /* 개별 데이터 행 (라벨 ... 등락률 값) */
    .data-row {
        display: flex;
        justify-content: space-between; /* 양끝 정렬 */
        align-items: center;
        padding: 4px 0;                 /* 행 높이 조절 */
    }
    
    /* 텍스트 스타일 */
    .lbl { color: #b0b8c4; font-size: 0.85rem; font-weight: 500; }
    .val-group { display: flex; align-items: baseline; gap: 8px; } /* 등락률과 값 사이 간격 */
    .chg { font-size: 0.8rem; font-weight: 600; }
    .val { color: white; font-size: 1.0rem; font-weight: 700; letter-spacing: 0.5px; }
    
    /* 구분선 (박스 안에서 사용 안 함, 박스 자체가 구분) */
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 데이터 행 생성 함수 (HTML 리턴)
# ---------------------------------------------------------
def get_row_html(label, value, change_str):
    # 색상 결정
    if "+" in change_str:
        color = "#ff4b4b" # Red
    elif "-" in change_str:
        color = "#4b88ff" # Blue
    else:
        color = "#888888" # Gray
        change_str = "0.00%"
        
    # 단위 분리 (값 뒤에 %가 붙어있는 경우 등 처리)
    # 단순히 문자열로 처리
    
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
# 3. 통합 박스 생성 함수 (핵심)
# ---------------------------------------------------------
def render_section_block(title, left_data, right_data):
    """
    title: 섹션 제목 (예: FRED)
    left_data: 왼쪽 열에 들어갈 데이터 리스트 [(라벨, 값, 등락), ...]
    right_data: 오른쪽 열에 들어갈 데이터 리스트
    """
    
    # 왼쪽 열 HTML 생성
    left_html = ""
    for item in left_data:
        left_html += get_row_html(item[0], item[1], item[2])
        
    # 오른쪽 열 HTML 생성
    right_html = ""
    for item in right_data:
        right_html += get_row_html(item[0], item[1], item[2])
        
    # 전체 HTML 조립
    st.markdown(f"""
    <div class="widget-box">
        <div class="widget-header">
            <span class="widget-title">{title}</span>
            <span class="widget-date">2026/02/10 23:18</span>
        </div>
        <div class="data-grid">
            <div class="col-left">
                {left_html}
            </div>
            <div class="col-right">
                {right_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 차트 생성 (Fear & Greed) - 이 부분도 박스 안에 넣음
# ---------------------------------------------------------
def make_fg_charts():
    y = [50, 45, 30, 25, 20, 25, 30, 40, 45, 50, 55, 60, 58, 55, 60, 65, 60, 55, 50, 48, 49]
    line = go.Figure(go.Scatter(y=y, mode='lines', line=dict(color='#e0e0e0', width=2), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
    line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=10, t=5, b=5), 
        xaxis=dict(visible=False), yaxis=dict(visible=True, range=[0, 100], showgrid=True, gridcolor='#333', tickfont=dict(size=8)),
        height=80
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
    gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=0), height=80)
    return line, gauge

# ---------------------------------------------------------
# 5. 화면 배치 (메인)
# ---------------------------------------------------------

# [1] Fear & Greed (박스 스타일 적용)
st.markdown("""<div class="widget-box">
<div class="widget-header"><span class="widget-title">Fear & Greed Index</span><span class="widget-date">(Last 3 months)</span></div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1.8, 1])
l_chart, g_chart = make_fg_charts()
with c1:
    st.plotly_chart(l_chart, use_container_width=True, config={'staticPlot': True})
with c2:
    st.plotly_chart(g_chart, use_container_width=True, config={'staticPlot': True})
    st.markdown("""<div style="text-align:center; margin-top:-25px; color:white; font-weight:800; font-size:1.5rem;">49<br><span style="font-size:0.9rem; font-weight:600; color:#e0e0e0;">Neutral</span></div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True) # 박스 닫기


# [2] FRED 데이터 준비 (하나의 박스로 합치기)
fred_left = [
    ("Fear & Greed", "49", "0.00%"), # 첫줄 왼쪽
    ("VIX", "17.43", "+0.07"),
    ("DXY (ICE)", "96.78", "-0.04"),
    ("US 2Y", "3.59%", "-0.00"),
    ("US 10Y", "4.16%", "-0.04"),
    ("Stress Index", "-0.68", "+0.03"),
    ("M2 Supply", "22,411", "+88.90")
]
fred_right = [
    ("Fed Balance", "6605.91", "+18.34"), # 첫줄 오른쪽
    ("TGA (Est)", "908.77", "-14.27"),
    ("ON RRP", "1.31B", "-1.81"),
    ("Repo Ops", "0.01B", "+0.01"),
    ("SOFR", "3.63%", "-"),
    ("MMF Total", "7,774", "+292.82"),
    ("Net Liquidity", "5697.13", "+32.61")
]

# FRED 박스 렌더링
render_section_block("FRED", fred_left, fred_right)


# [3] INDEXerGO 데이터 준비
idx_left = [
    ("달러인덱스", "97", "-0.04%"),
    ("원/달러", "1,457", "-0.40%"),
    ("금 (Gold)", "5,077", "+0.52%"),
    ("은 (Silver)", "82", "-0.54%")
]
idx_right = [
    ("비트코인", "69,150", "-1.38%"),
    ("이더리움", "2,023", "-3.83%"),
    ("WTI유", "64", "+0.11%"),
    ("천연가스", "3.14", "-0.06%")
]

# INDEXerGO 박스 렌더링
render_section_block("INDEXerGO", idx_left, idx_right)
