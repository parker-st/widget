import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ---------------------------------------------------------
# 1. 페이지 설정 및 CSS
# ---------------------------------------------------------
st.set_page_config(page_title="Macro Dashboard Final", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경색 - 다크 모드 */
    .main { background-color: #0e1117; }
    
    /* Plotly 차트 여백 및 모드바 제거 */
    .js-plotly-plot .plotly .modebar { display: none; }
    
    /* [Fear & Greed] 텍스트 스타일 */
    .fg-container {
        text-align: center;
        margin-top: -50px; /* 게이지 안쪽으로 텍스트 올리기 */
        position: relative;
        z-index: 999;
    }
    .fg-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        line-height: 1.0;
    }
    .fg-label {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e0e0e0;
        margin-top: 5px;
    }
    .fg-date {
        font-size: 0.7rem;
        color: #888;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. [핵심] 한국식 색상 카드 생성 함수 (HTML 강제 적용)
# ---------------------------------------------------------
def create_card(label, value, change_str, unit="", is_crypto=False):
    """
    HTML로 카드를 직접 그려서 색상(빨강/파랑)을 완벽하게 고정합니다.
    """
    # 1. 등락률에 따른 색상 및 화살표 결정
    if "+" in change_str:
        color = "#ff4b4b" # 빨간색 (상승)
        arrow = "▲"
        change_val = change_str
    elif "-" in change_str:
        color = "#4b88ff" # 파란색 (하락)
        arrow = "▼"
        change_val = change_str
    else:
        color = "#888888" # 변동 없음 (회색)
        arrow = "-"
        change_val = "0.00%"

    # 2. HTML 카드 디자인 (이미지와 동일한 스타일)
    card_html = f"""
    <div style="
        background-color: #1e2227;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #2d3139;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    ">
        <div style="color: #9da5b1; font-size: 0.8rem; margin-bottom: 4px; font-weight: 500;">{label}</div>
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div style="color: white; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                {value}<span style="font-size:0.9rem; font-weight:400; color:#ccc; margin-left:2px;">{unit}</span>
            </div>
            <div style="color: {color}; font-size: 0.95rem; font-weight: 600;">
                {change_val}
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 차트 생성 함수 (Fear & Greed)
# ---------------------------------------------------------
def make_fg_charts():
    # (1) 왼쪽 선 그래프 (사진과 유사한 굴곡 데이터)
    y_data = [50, 45, 30, 25, 28, 20, 25, 20, 15, 12, 18, 25, 30, 35, 38, 42, 45, 48, 52, 55, 60, 58, 55, 60, 65, 62, 55, 50, 45, 48, 49, 48, 49]
    x_data = list(range(len(y_data)))
    
    line = go.Figure(go.Scatter(
        x=x_data, y=y_data, mode='lines', 
        line=dict(color='#e0e0e0', width=2),
        fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'
    ))
    line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(visible=False), 
        yaxis=dict(visible=True, showgrid=True, gridcolor='#333', range=[0, 100]),
        height=140
    )

    # (2) 오른쪽 게이지 차트
    gauge = go.Figure(go.Indicator(
        mode = "gauge", value = 49,
        gauge = {
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "white", 'thickness': 0}, # 바늘은 숨기고 CSS 텍스트로 대체
            'steps': [
                {'range': [0, 25], 'color': '#ff6b6b'},   # Extreme Fear
                {'range': [25, 45], 'color': '#feca57'},  # Fear
                {'range': [45, 55], 'color': '#ffffff'},  # Neutral (흰색 구분선 느낌)
                {'range': [55, 75], 'color': '#48dbfb'},  # Greed
                {'range': [75, 100], 'color': '#1dd1a1'}  # Extreme Greed
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.8, 'value': 49}
        }
    ))
    gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=20, r=20, t=20, b=0), 
        height=130
    )
    
    return line, gauge

# ---------------------------------------------------------
# 4. 화면 레이아웃 구성
# ---------------------------------------------------------

# === [섹션 1] Fear & Greed Index ===
st.markdown("### Fear & Greed Index")
c1, c2 = st.columns([1.8, 1])
line_fig, gauge_fig = make_fg_charts()

with c1:
    st.caption("(Last 3 months)")
    st.plotly_chart(line_fig, use_container_width=True, config={'staticPlot': True})

with c2:
    # 게이지 차트 그리기
    st.plotly_chart(gauge_fig, use_container_width=True, config={'staticPlot': True})
    # [복구 완료] 텍스트 강제 삽입 (게이지 중앙 하단)
    st.markdown("""
        <div class="fg-container">
            <div class="fg-value">49</div>
            <div class="fg-label">Neutral</div>
            <div class="fg-date">Last updated:<br>2026-02-10 23:18</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# === [섹션 2] FRED ===
st.markdown("### FRED <span style='font-size:0.8rem; color:gray;'>2026/2/10 23:18</span>", unsafe_allow_html=True)
f1, f2 = st.columns(2)

with f1:
    create_card("Fear & Greed", "49", "Neutral") # 변동없음
    create_card("VIX", "17.43", "+0.07")
    create_card("DXY (ICE)", "96.78", "-0.04%")
    create_card("US 2Y", "3.59", "-0.00", unit="%")
    create_card("US 10Y", "4.16", "-0.04", unit="%")
    create_card("Stress Index", "-0.68", "+0.03")
    create_card("M2 Supply", "22,411", "+88.90")

with f2:
    create_card("Fed Balance", "6605.91", "+18.34")
    create_card("TGA (Est)", "908.77", "-14.27")
    create_card("ON RRP", "1.31B", "-1.81")
    create_card("Repo Ops", "0.01B", "+0.01")
    create_card("SOFR", "3.63", "-", unit="%") # 변동없음
    create_card("MMF Total", "7,774", "+292.82")
    create_card("Net Liquidity", "5697.13", "+32.61")

st.divider()

# === [섹션 3] INDEXerGO ===
st.markdown("### INDEXerGO <span style='font-size:0.8rem; color:gray;'>2026-02-10 23:18</span>", unsafe_allow_html=True)
i1, i2 = st.columns(2)

with i1:
    create_card("달러인덱스", "97", "-0.04%")
    create_card("원/달러", "1,457", "-0.40%")
    create_card("금 (Gold)", "5,077", "+0.52%")
    create_card("은 (Silver)", "82", "-0.54%")

with i2:
    create_card("비트코인", "69,150", "-1.38%")
    create_card("이더리움", "2,023", "-3.83%")
    create_card("WTI유", "64", "+0.11%")
    create_card("천연가스", "3.14", "-0.06%")