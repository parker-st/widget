import streamlit as st
import plotly.graph_objects as go

# 1. 페이지 설정 (여백 0)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. 공통 CSS (휴대폰 위젯 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding: 0px !important; }
    
    /* 위젯 박스 디자인 */
    .widget-box {
        background-color: #1e2227;
        border-radius: 24px;
        padding: 15px;
        height: 100vh; /* 화면 전체 채움 */
    }
    .widget-title { color: white; font-size: 1.2rem; font-weight: 800; margin-bottom: 5px; }
    .widget-date { color: #888; font-size: 0.8rem; margin-bottom: 15px; }
    
    /* 데이터 표 스타일 */
    .data-table { width: 100%; border-collapse: collapse; }
    .data-row td { padding: 6px 0; border-bottom: 1px solid #2d3139; }
    .lbl { color: #b0b8c4; font-size: 0.9rem; }
    .val-group { text-align: right; }
    .chg { font-size: 0.85rem; font-weight: 600; margin-right: 5px; }
    .val { color: white; font-size: 1.05rem; font-weight: 700; }
    .up { color: #ff4b4b; }
    .down { color: #4b88ff; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로우 생성 함수
def get_row(label, value, change):
    color_class = "up" if "+" in change else "down" if "-" in change else ""
    return f"""
    <tr class="data-row">
        <td class="lbl">{label}</td>
        <td class="val-group">
            <span class="chg {color_class}">{change}</span>
            <span class="val">{value}</span>
        </td>
    </tr>
    """

# URL 파라미터 읽기 (어떤 위젯을 보여줄지 결정)
query_params = st.query_params
view = query_params.get("view", "fg") # 기본값은 fg

# --- 1. Fear & Greed Index 위젯 ---
if view == "fg":
    st.markdown('<div class="widget-box"><div class="widget-title">Fear & Greed Index</div>', unsafe_allow_html=True)
    y = [50, 45, 30, 25, 20, 25, 30, 40, 45, 50, 55, 60, 58, 55, 60, 65, 60, 55, 50, 48, 49]
    
    # 게이지 차트
    gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = 49,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 25], 'color': '#ff6b6b'}, {'range': [25, 45], 'color': '#feca57'},
                {'range': [45, 55], 'color': '#eeeeee'}, {'range': [55, 75], 'color': '#48dbfb'},
                {'range': [75, 100], 'color': '#1dd1a1'}
            ]
        }
    ))
    gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"}, height=200, margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(gauge, use_container_width=True, config={'staticPlot': True})
    st.markdown('<div style="text-align:center; color:#e0e0e0; font-size:1.2rem; font-weight:700;">Neutral</div></div>', unsafe_allow_html=True)

# --- 2. FRED 위젯 ---
elif view == "fred":
    st.markdown('<div class="widget-box"><div class="widget-title">FRED Metrics</div><div class="widget-date">2026/02/11 15:00</div>', unsafe_allow_html=True)
    rows = [
        ("VIX", "17.43", "+0.07"), ("DXY", "96.78", "-0.04%"),
        ("US 2Y", "3.59%", "-0.00"), ("US 10Y", "4.16%", "-0.04"),
        ("Fed Balance", "6605.9", "+18.3"), ("ON RRP", "1.31B", "-1.81")
    ]
    html = '<table class="data-table">' + "".join([get_row(r[0], r[1], r[2]) for r in rows]) + '</table></div>'
    st.markdown(html, unsafe_allow_html=True)

# --- 3. INDEXerGO 위젯 ---
elif view == "idx":
    st.markdown('<div class="widget-box"><div class="widget-title">INDEXerGO</div><div class="widget-date">2026/02/11 15:00</div>', unsafe_allow_html=True)
    rows = [
        ("원/달러", "1,457", "-0.40%"), ("금 (Gold)", "5,077", "+0.52%"),
        ("비트코인", "69,150", "-1.38%"), ("이더리움", "2,023", "-3.83%"),
        ("WTI유", "64", "+0.11%"), ("천연가스", "3.14", "-0.06%")
    ]
    html = '<table class="data-table">' + "".join([get_row(r[0], r[1], r[2]) for r in rows]) + '</table></div>'
    st.markdown(html, unsafe_allow_html=True)
