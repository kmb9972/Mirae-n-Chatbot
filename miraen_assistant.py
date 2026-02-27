"""
미래엔 사내 비서 챗봇 (Streamlit)
====================================
실행 방법:
  1. pip install streamlit anthropic
  2. streamlit run miraen_assistant.py
"""

import streamlit as st
import time
import re

# ──────────────────────────────────────────
# [Mock 모드] Anthropic API 비활성화
# 실제 API 사용 시 아래 주석을 해제하고
# Mock 응답 함수(get_mock_response)를 get_ai_response로 교체하세요.
# ──────────────────────────────────────────
# import anthropic

# ──────────────────────────────────────────
# 1. 지식 베이스 (Knowledge Base)
# ──────────────────────────────────────────
KNOWLEDGE_BASE = """
[미래엔 사내 비서] 통합 지식 베이스

1. 자녀 양육 및 교육 지원 가이드
미취학 자녀 보육료:
- 0세반: 국가 584,000원 + 회사 292,000원 지원.
- 1세반: 국가 515,000원 + 회사 257,500원 지원.
- 2세반: 국가 426,000원 + 회사 213,000원 지원.
- 3~5세반: 국가 280,000원 + 회사 140,000원 지원.

보육지원비 수당: 만 0~5세 월 10만 원, 만 6세 월 20만 원 급여 지급. 자녀 생일 월 기준으로 지원하며 매월 10만 원까지 비과세 처리.

취학 자녀 입학 선물: 초등학생 30만 원(학용품/도서), 중·고등학생 40만 원(교복/체육복) 한도 내 영수증 정산. 매년 2월 신청서 접수.

대학교 학자금: 5년 이상 재직자 자녀 대상 연간 최대 200만 원. 입학금, 수업료, 기성회비만 해당. 매년 8~9월 전자결재 신청.

육아기 근로시간 단축: 만 12세 이하(초6 이하) 자녀 대상 일 1~5시간 단축 근무. 육아휴직 미사용 기간의 2배까지 연장 사용 가능.

2. 경조사 지원
주요 경조 기준:
- 본인 결혼: 30만 원 / 7일.
- 본인/배우자 출산: 500만 원 / 20일 (120일 내 3회 분할 가능, 출산일 포함 3일 연속 사용 필수).
- 부모상(배우자 부모 포함): 30만 원 / 5일.
- 조부모상(친/외가 포함): 20만 원 / 3일 (승중 시 30만 원 / 5일).

재직 기간 차등: 근속 1년 미만은 경조금 50% 지급, 휴가는 전일 지급.
신청: 발생 30일 이내. 그룹웨어 '경조사 신고서' 작성 후 시프티(Shiftee)에 휴가 별도 입력 필수.
장례 서비스: 본인/배우자/부모/자녀상 시 장례지도사 1명(3일), 의전용품(상복 남4·여4), 리무진/버스(200km) 지원.

3. 휴가 및 근무 제도
- 연차: 2시간 단위(쿼터) 분할 사용 가능.
- 플러스 휴가: 연차 외 매년 4일 추가 부여. 당해 연도 소멸, 연차보다 우선 사용 권장.
- 장기근속 휴가: 5년(3일), 10/15년(5일), 20년(7일), 25/30/35년(10일).
- 재택근무: 주 2회 원칙. 주중 휴일 1일 시 재택 1일, 휴일 2일 이상 시 재택 불가. 사무실 전화 휴대폰 착신 전환 필수.
- 자율출근: 일 9시간(휴게 포함) 근무 준수 하에 지각 없는 자율 출근.

4. 자기계발 및 IT 설정
- 자격증: LV 1~5등급별 학습비/축하금 차등 지원(각 20~150만 원). 리스트 외 자격증은 직무 연관성 판단 후 지급.
- 직원용 WIFI: MiraeN-AP / PW: 19480924ab
- 외부용 WIFI: MiraeN-WIfI / PW: 34753800
- 문서보안: 서버 doc.mirae-n.com, 포트 443, 계정은 사번.
- 명함 신청: mirae-n.onehp.co.kr / ID: miraen / PW: 1111

5. 사무위임전결규정 (결재선)
휴가/경조사 신청:
- 팀원 → 팀장 전결 (인사지원팀 통보). 서류: 휴가신청서 / 경조사신고서

사외교육:
- 국내 3일 이내: 팀장(실장) 승인
- 국내 3일 초과: 본부(실)장 승인
- 국내 1개월 이상: 사장 승인
- 서류: 교육신청서

비용 전표(경비):
- 건당 1백만 원 미만: 팀장
- 건당 2천만 원 미만: 본부(실)장
- 건당 2천만 원 이상: 사장 결재

구매 품의(본사):
- 총액 1백만 원 미만: 팀장
- 총액 2천만 원 미만: 본부(실)장
- 총액 2천만 원 이상: 본부(실)장 → 사장

출장:
- 국내(팀원): 팀장 승인 / 서류: 출장신청서
- 국내(팀장 이상): 본부(실)장 승인
- 해외: 사장 승인, 경영기획실·경영관리팀 합의

접대비:
- 건당 20만 원 미만: 팀장
- 건당 30만 원 미만: 실장
- 건당 30만 원 이상: 본부(실)장 (정도경영팀 합의)
"""

# ──────────────────────────────────────────
# 2. 시스템 프롬프트
# ──────────────────────────────────────────
SYSTEM_PROMPT = f"""당신은 미래엔(MiraeN) 회사의 사내 비서입니다.
직원들의 인사, 복지, 행정 관련 질문에 아래 지식 베이스를 근거로 친절하고 정확하게 답변하세요.

[답변 원칙]
1. 지식 베이스에 있는 내용만 답변하고, 없는 내용은 "해당 내용은 지식 베이스에 없어 인사지원팀에 문의해 주세요."라고 안내하세요.
2. 결재 관련 질문에는 반드시 전결권자, 필요 서류, 관련 부서를 함께 안내하세요.
3. 신청 방법이 있을 경우 그룹웨어 메뉴명이나 시스템 경로도 안내하세요.
4. 답변은 한국어로, 따뜻하고 친근한 말투를 사용하세요.
5. 필요 시 bullet point나 표 형식으로 가독성 있게 정리해 주세요.

[지식 베이스]
{KNOWLEDGE_BASE}
"""

# ──────────────────────────────────────────
# 3. 페이지 설정 & 커스텀 CSS
# ──────────────────────────────────────────
st.set_page_config(
    page_title="미래엔 사내 비서",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Pretendard:wght@400;600;700&display=swap');

    /* 전체 배경 */
    .stApp {
        background: #F4F6FB;
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #1A3A6B 0%, #0D2247 100%);
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: #E8EEF8 !important;
    }

    /* 사이드바 카드 */
    .sidebar-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
    }
    .sidebar-card h4 {
        color: #7FB3F5 !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 8px 0;
    }
    .sidebar-card p {
        font-size: 0.82rem;
        color: #C8D8F0 !important;
        margin: 4px 0;
        line-height: 1.5;
    }
    .sidebar-card .value {
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 0.88rem;
    }
    .sidebar-link {
        display: inline-block;
        background: rgba(127,179,245,0.2);
        color: #7FB3F5 !important;
        border: 1px solid rgba(127,179,245,0.4);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        text-decoration: none;
        margin-top: 4px;
        transition: all 0.2s;
    }
    .sidebar-link:hover {
        background: rgba(127,179,245,0.35);
    }

    /* 메인 헤더 */
    .main-header {
        background: linear-gradient(135deg, #1A3A6B 0%, #2A5298 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 4px 24px rgba(26,58,107,0.18);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #A8C4E8 !important;
        font-size: 0.88rem;
        margin: 4px 0 0 0;
    }

    /* 빠른 질문 버튼 */
    .quick-btn-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 20px;
    }

    /* 채팅 메시지 */
    .chat-msg-user {
        display: flex;
        justify-content: flex-end;
        margin: 8px 0;
    }
    .chat-msg-assistant {
        display: flex;
        justify-content: flex-start;
        margin: 8px 0;
    }
    .bubble-user {
        background: linear-gradient(135deg, #2A5298, #1A3A6B);
        color: #FFFFFF;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        max-width: 70%;
        font-size: 0.9rem;
        line-height: 1.6;
        box-shadow: 0 2px 12px rgba(26,58,107,0.2);
    }
    .bubble-assistant {
        background: #FFFFFF;
        color: #1A2B4A;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        max-width: 75%;
        font-size: 0.9rem;
        line-height: 1.7;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E4EAF6;
    }
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
        margin: 0 8px;
    }
    .avatar-user { background: #2A5298; }
    .avatar-bot  { background: linear-gradient(135deg,#1A3A6B,#2A5298); }

    /* 입력창 */
    .stTextInput > div > div > input {
        border-radius: 24px !important;
        border: 2px solid #D0DCEF !important;
        padding: 12px 20px !important;
        font-size: 0.92rem !important;
        background: #FFFFFF !important;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2A5298 !important;
        box-shadow: 0 0 0 3px rgba(42,82,152,0.1) !important;
    }

    /* 전송 버튼 */
    .stButton > button {
        border-radius: 24px !important;
        background: linear-gradient(135deg, #2A5298, #1A3A6B) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 12px 28px !important;
        transition: all 0.2s !important;
        box-shadow: 0 3px 12px rgba(26,58,107,0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 18px rgba(26,58,107,0.35) !important;
    }

    /* 빠른 질문 버튼 */
    .quick-btn > button {
        background: #FFFFFF !important;
        color: #2A5298 !important;
        border: 1.5px solid #C0D0E8 !important;
        border-radius: 20px !important;
        font-size: 0.78rem !important;
        padding: 6px 12px !important;
        font-weight: 500 !important;
        width: 100% !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    .quick-btn > button:hover {
        background: #EEF3FC !important;
        border-color: #2A5298 !important;
    }

    /* 구분선 */
    hr { border-color: rgba(255,255,255,0.1) !important; }

    /* 채팅 컨테이너 */
    .chat-container {
        background: #F9FAFF;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #E4EAF6;
        min-height: 420px;
        max-height: 520px;
        overflow-y: auto;
        margin-bottom: 16px;
    }

    /* 빈 채팅 안내 */
    .empty-chat {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        color: #8A9BBD;
    }
    .empty-chat .icon { font-size: 3rem; margin-bottom: 12px; }
    .empty-chat p { font-size: 0.9rem; text-align: center; line-height: 1.6; }

    /* 로딩 */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 12px 18px;
        background: #FFFFFF;
        border-radius: 18px 18px 18px 4px;
        width: fit-content;
        border: 1px solid #E4EAF6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .dot {
        width: 8px; height: 8px;
        background: #2A5298;
        border-radius: 50%;
        animation: bounce 1.2s infinite;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* 숨기기 */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 4. 사이드바
# ──────────────────────────────────────────
with st.sidebar:
    # 로고/타이틀
    st.markdown("""
        <div style="text-align:center; padding: 8px 0 20px;">
            <div style="font-size:2.4rem;">🏢</div>
            <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF; margin-top:6px;">미래엔 사내 비서</div>
            <div style="font-size:0.75rem; color:#7FB3F5; margin-top:3px;">MiraeN Internal Assistant</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # WIFI 정보
    st.markdown("""
        <div class="sidebar-card">
            <h4>📶 WIFI 정보</h4>
            <p>직원용</p>
            <p class="value">MiraeN-AP</p>
            <p style="color:#7FB3F5 !important; font-size:0.75rem;">PW: 19480924ab</p>
            <p style="margin-top:10px;">외부 방문객용</p>
            <p class="value">MiraeN-WIfI</p>
            <p style="color:#7FB3F5 !important; font-size:0.75rem;">PW: 34753800</p>
        </div>
    """, unsafe_allow_html=True)

    # 명함 신청
    st.markdown("""
        <div class="sidebar-card">
            <h4>🪪 명함 신청</h4>
            <p>사이트에 접속해서 신청하세요</p>
            <a class="sidebar-link" href="http://mirae-n.onehp.co.kr" target="_blank">
                🔗 명함 신청 바로가기
            </a>
            <p style="margin-top:8px;">ID: <span class="value">miraen</span> &nbsp;|&nbsp; PW: <span class="value">1111</span></p>
        </div>
    """, unsafe_allow_html=True)

    # 문서 보안
    st.markdown("""
        <div class="sidebar-card">
            <h4>🔒 문서보안 설정</h4>
            <p>서버: <span class="value">doc.mirae-n.com</span></p>
            <p>포트: <span class="value">443</span></p>
            <p>계정: <span class="value">사번</span></p>
        </div>
    """, unsafe_allow_html=True)

    # 그룹웨어 바로가기
    st.markdown("""
        <div class="sidebar-card">
            <h4>🖥️ 그룹웨어</h4>
            <a class="sidebar-link" href="https://gw.mirae-n.com" target="_blank">
                🔗 그룹웨어 접속
            </a>
            <p style="margin-top:8px; font-size:0.75rem; color:#8AAAD0 !important;">
                경조사 신고서 · 휴가신청 · 전자결재
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 시프티 바로가기
    st.markdown("""
        <div class="sidebar-card">
            <h4>📅 근태 관리 (Shiftee)</h4>
            <a class="sidebar-link" href="https://www.shiftee.io" target="_blank">
                🔗 시프티 접속
            </a>
            <p style="margin-top:8px; font-size:0.75rem; color:#8AAAD0 !important;">
                휴가 입력 · 연장근무 신청
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align:center; font-size:0.72rem; color:#567AAA; padding: 4px 0;">
            인사지원팀 문의: 내선 1234<br>
            © 2025 MiraeN Co., Ltd.
        </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────
# 5. 메인 화면
# ──────────────────────────────────────────
# 헤더
st.markdown("""
    <div class="main-header">
        <div style="font-size:2.2rem;">🤖</div>
        <div>
            <h1>안녕하세요, 미래엔 사내 비서입니다 👋</h1>
            <p>인사·복지·행정 관련 궁금한 점을 편하게 질문해 주세요. 지식 베이스 기반으로 정확하게 답변드립니다.</p>
            <span style="display:inline-block; margin-top:8px; background:rgba(255,200,0,0.2); border:1px solid rgba(255,200,0,0.5); color:#FFD966; border-radius:20px; padding:3px 12px; font-size:0.72rem; font-weight:600; letter-spacing:0.05em;">
                🧪 MOCK 모드 · API 키 없이 테스트 중
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# ──────────────────────────────────────────
# 6. 빠른 질문 버튼
# ──────────────────────────────────────────
QUICK_QUESTIONS = [
    "🍼 육아휴직 및 보육비 지원 알려줘",
    "💐 경조사 휴가일수와 경조금 기준은?",
    "🏖️ 플러스 휴가가 뭐야?",
    "✅ 출장 신청 결재선이 어떻게 돼?",
    "📚 자격증 취득 지원금 얼마야?",
    "🏠 재택근무 규정 알려줘",
]

st.markdown("<p style='font-size:0.82rem; color:#8A9BBD; margin-bottom:8px;'>💡 자주 묻는 질문</p>", unsafe_allow_html=True)

cols = st.columns(3)
for i, q in enumerate(QUICK_QUESTIONS):
    with cols[i % 3]:
        with st.container():
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button(q, key=f"quick_{i}"):
                st.session_state.messages.append({"role": "user", "content": q})
                st.session_state.pending_response = True
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 7. 채팅 메시지 렌더링
# ──────────────────────────────────────────
chat_area = st.container()

with chat_area:
    if not st.session_state.messages:
        st.markdown("""
            <div class="empty-chat">
                <div class="icon">💬</div>
                <p>아직 대화가 없습니다.<br>위 빠른 질문을 클릭하거나,<br>아래 입력창에 질문을 입력해 주세요.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="chat-msg-user">
                        <div class="bubble-user">{msg["content"]}</div>
                        <div class="avatar avatar-user">🙋</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-msg-assistant">
                        <div class="avatar avatar-bot">🤖</div>
                        <div class="bubble-assistant">{msg["content"]}</div>
                    </div>
                """, unsafe_allow_html=True)

# ──────────────────────────────────────────
# 8. 입력창 + 전송
# ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_input = st.text_input(
        label="질문 입력",
        placeholder="예: 출산 휴가는 며칠 받을 수 있나요?",
        label_visibility="collapsed",
        key="user_input"
    )

with col_btn:
    send_clicked = st.button("전송 ✈️", use_container_width=True)

# ──────────────────────────────────────────
# 9. 응답 함수
# ──────────────────────────────────────────

# ── [주석 처리됨] 실제 Anthropic API 호출 함수 ──────────────────────────────
# def get_ai_response(messages_history: list) -> str:
#     """Anthropic API 호출 (실제 운영 시 사용)"""
#     client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 환경변수 자동 참조
#
#     api_messages = [
#         {"role": m["role"], "content": m["content"]}
#         for m in messages_history
#     ]
#
#     response = client.messages.create(
#         model="claude-sonnet-4-6",
#         max_tokens=1500,
#         system=SYSTEM_PROMPT,
#         messages=api_messages,
#     )
#     return response.content[0].text
# ── [주석 처리 끝] ────────────────────────────────────────────────────────────


# ── [Mock 모드] 키워드 기반 가짜 응답 함수 ──────────────────────────────────
def get_mock_response(messages_history: list) -> str:
    """
    API 키 없이 테스트 가능한 Mock 응답 함수.
    질문에서 키워드를 감지해 지식 베이스 내용을 요약 반환합니다.
    실제 운영 시 이 함수를 get_ai_response(주석 해제)로 교체하세요.
    """
    question = messages_history[-1]["content"].lower()

    # ── 키워드 → 응답 매핑 테이블 ──────────────────────────────────────────
    MOCK_RESPONSES = {
        # 보육 / 육아
        ("보육", "육아", "보육료", "육아휴직", "보육비", "자녀 지원", "보육지원"): (
            "🍼 **자녀 보육 관련 지원 안내**\n\n"
            "**미취학 보육료 지원** (국가 + 회사 매칭)\n"
            "- 0세반: 국가 584,000원 + 회사 292,000원\n"
            "- 1세반: 국가 515,000원 + 회사 257,500원\n"
            "- 2세반: 국가 426,000원 + 회사 213,000원\n"
            "- 3~5세반: 국가 280,000원 + 회사 140,000원\n\n"
            "**보육지원비 수당** (매월 급여 지급)\n"
            "- 만 0~5세: 월 10만 원 (비과세)\n"
            "- 만 6세: 월 20만 원\n\n"
            "**육아기 근로시간 단축**\n"
            "- 대상: 만 12세 이하(초등 6학년 이하) 자녀\n"
            "- 단축 범위: 일 1~5시간\n"
            "- 육아휴직 미사용 기간의 최대 2배까지 연장 사용 가능\n\n"
            "📌 자세한 신청 방법은 그룹웨어 → 전자결재에서 확인하세요."
        ),
        # 경조사
        ("경조", "결혼", "출산", "부모상", "조부모상", "상조", "장례", "경조금", "경조 휴가"): (
            "💐 **경조사 지원 안내**\n\n"
            "| 구분 | 경조금 | 휴가 |\n"
            "|------|--------|------|\n"
            "| 본인 결혼 | 30만 원 | 7일 |\n"
            "| 본인/배우자 출산 | 500만 원 | 20일 |\n"
            "| 부모상 (배우자 포함) | 30만 원 | 5일 |\n"
            "| 조부모상 | 20만 원 | 3일 |\n"
            "| 조부모상 (승중) | 30만 원 | 5일 |\n\n"
            "**출산 휴가 특이사항**\n"
            "- 120일 내 3회 분할 사용 가능\n"
            "- 출산일 포함 3일은 연속 사용 필수\n\n"
            "**근속 1년 미만** 시 경조금 50% 지급 (휴가는 전일 지급)\n\n"
            "**신청 방법**\n"
            "1. 그룹웨어 → **경조사 신고서** 작성 (발생 30일 이내)\n"
            "2. **시프티(Shiftee)** 에 휴가 별도 입력 필수\n\n"
            "**장례 서비스** (본인/배우자/부모/자녀상)\n"
            "장례지도사 1명(3일), 상복(남4·여4), 리무진/버스(200km 이내) 지원"
        ),
        # 플러스 휴가 / 연차
        ("플러스 휴가", "플러스휴가", "연차", "휴가", "장기근속"): (
            "🏖️ **휴가 제도 안내**\n\n"
            "**연차 휴가**\n"
            "- 2시간 단위(쿼터)로 분할 사용 가능\n\n"
            "**플러스 휴가** ⭐\n"
            "- 연차 외 매년 4일 추가 부여\n"
            "- 당해 연도 미사용 시 소멸 (이월 불가)\n"
            "- 연차보다 플러스 휴가 먼저 사용 권장\n\n"
            "**장기근속 휴가**\n"
            "- 5년: 3일\n"
            "- 10년 / 15년: 5일\n"
            "- 20년: 7일\n"
            "- 25년 / 30년 / 35년: 10일\n\n"
            "📌 휴가 신청: 시프티(Shiftee) 앱에서 입력 / 결재선: 팀원 → 팀장 전결"
        ),
        # 재택근무
        ("재택", "재택근무", "원격", "자율출근", "출근"): (
            "🏠 **재택근무 & 자율출근 안내**\n\n"
            "**재택근무**\n"
            "- 기본 원칙: 주 2회\n"
            "- 주중 휴일 1일 → 재택 1일만 가능\n"
            "- 주중 휴일 2일 이상 → 재택 불가\n"
            "- ⚠️ 사무실 전화를 휴대폰으로 **착신 전환 필수**\n\n"
            "**자율출근**\n"
            "- 일 9시간(휴게 포함) 근무 준수 조건으로 자유롭게 출근\n"
            "- 지각 없이 자율 출근 가능\n\n"
            "📌 근태 관련 문의: 인사지원팀 / 시스템: 시프티(Shiftee)"
        ),
        # 출장
        ("출장", "해외출장", "국내출장", "출장비", "출장 결재"): (
            "✈️ **출장 신청 결재선 안내**\n\n"
            "**국내 출장**\n"
            "- 팀원: 팀장 승인\n"
            "- 팀장 이상: 본부(실)장 승인\n"
            "- 📄 서류: 출장신청서\n\n"
            "**해외 출장**\n"
            "- 전결권자: 사장\n"
            "- 합의 부서: 경영기획실, 경영관리팀\n"
            "- 📄 서류: 기안서 + 출장신청서\n\n"
            "**출장비 정산**\n"
            "- 해외 출장비 선지급: 팀장 → 재무팀 통보\n"
            "- 출장비 정산: 팀장 → 재무팀 / 서류: 지출명세서, 출장여비계산서\n"
            "- 시내교통비: 팀장 → 인사지원팀 / 서류: 교통비신청서\n\n"
            "📌 그룹웨어 전자결재에서 신청서 양식을 사용하세요."
        ),
        # 자격증
        ("자격증", "자기계발", "학습비", "축하금"): (
            "📚 **자격증 취득 지원 안내**\n\n"
            "등급별로 학습비와 축하금을 차등 지원합니다:\n\n"
            "| 등급 | 지원 금액 |\n"
            "|------|-----------|\n"
            "| LV 1 | 20만 원 |\n"
            "| LV 2 | 50만 원 |\n"
            "| LV 3 | 80만 원 |\n"
            "| LV 4 | 120만 원 |\n"
            "| LV 5 | 150만 원 |\n\n"
            "*(학습비 + 축하금 합산 기준)\n\n"
            "**지원 리스트 외 자격증**은 직무 연관성 검토 후 지급 여부 결정\n\n"
            "📌 신청 및 문의: 인사지원팀"
        ),
        # 비용 전표 / 결재
        ("결재", "전결", "비용", "전표", "경비", "품의", "접대비", "구매"): (
            "✅ **비용 결재선 (사무위임전결규정)**\n\n"
            "**경비 전표**\n"
            "- 건당 100만 원 미만: 팀장\n"
            "- 건당 2,000만 원 미만: 본부(실)장\n"
            "- 건당 2,000만 원 이상: 사장\n\n"
            "**접대비 (사외 회의비 포함)**\n"
            "- 건당 20만 원 미만: 팀장\n"
            "- 건당 30만 원 미만: 실장\n"
            "- 건당 30만 원 이상: 본부(실)장 (정도경영팀 합의)\n\n"
            "**구매 품의 (본사)**\n"
            "- 총액 100만 원 미만: 팀장\n"
            "- 총액 2,000만 원 미만: 본부(실)장\n"
            "- 총액 2,000만 원 이상: 사장\n\n"
            "📌 그룹웨어 전자결재 → 기안서 양식 사용"
        ),
        # 사외 교육
        ("교육", "사외교육", "외부교육", "연수"): (
            "🎓 **사외교육 신청 결재선**\n\n"
            "| 교육 기간 | 전결권자 |\n"
            "|-----------|----------|\n"
            "| 국내 3일 이내 | 팀장(실장) |\n"
            "| 국내 3일 초과 | 본부(실)장 |\n"
            "| 국내 1개월 이상 | 사장 |\n\n"
            "- 📄 서류: **교육신청서**\n"
            "- 승인 부서: 인사지원팀\n"
            "- 교육 결과 보고: 본부(실)장 → 인사지원팀 통보 (교육이수보고서)\n\n"
            "📌 예외사항(격주·격월·온라인 교육 등)은 인사지원팀이 결재라인 권고 가능"
        ),
        # WIFI / IT
        ("wifi", "와이파이", "인터넷", "문서보안", "보안", "it", "명함"): (
            "💻 **IT 설정 및 업무 도구 안내**\n\n"
            "**📶 WIFI**\n"
            "- 직원용: `MiraeN-AP` / PW: `19480924ab`\n"
            "- 외부 방문객용: `MiraeN-WIfI` / PW: `34753800`\n\n"
            "**🔒 문서보안**\n"
            "- 서버: `doc.mirae-n.com`\n"
            "- 포트: `443`\n"
            "- 계정: 본인 사번\n\n"
            "**🪪 명함 신청**\n"
            "- 사이트: [mirae-n.onehp.co.kr](http://mirae-n.onehp.co.kr)\n"
            "- ID: `miraen` / PW: `1111`"
        ),
        # 학자금
        ("학자금", "대학교", "대학", "등록금"): (
            "🎓 **대학교 학자금 지원 안내**\n\n"
            "**지원 대상**: 재직 5년 이상 임직원의 자녀\n"
            "**지원 금액**: 연간 최대 200만 원\n"
            "**지원 항목**: 입학금, 수업료, 기성회비 (해당 항목만 인정)\n"
            "**신청 시기**: 매년 8~9월\n"
            "**신청 방법**: 그룹웨어 전자결재\n\n"
            "📌 재직 5년 미만은 대상에서 제외됩니다."
        ),
        # 입학 선물
        ("입학", "초등", "중학교", "고등학교", "교복", "학용품"): (
            "🎒 **취학 자녀 입학 선물 지원**\n\n"
            "| 구분 | 한도 | 지원 내용 |\n"
            "|------|------|-----------|\n"
            "| 초등학생 | 30만 원 | 학용품 / 도서 |\n"
            "| 중·고등학생 | 40만 원 | 교복 / 체육복 |\n\n"
            "- 영수증 정산 방식\n"
            "- **신청 시기**: 매년 2월 신청서 접수\n\n"
            "📌 신청서는 인사지원팀 또는 그룹웨어에서 확인하세요."
        ),
    }

    # 키워드 매칭
    for keywords, response in MOCK_RESPONSES.items():
        if any(kw in question for kw in keywords):
            time.sleep(0.6)  # 응답 생성 딜레이 시뮬레이션
            return response

    # 매칭 없을 경우 기본 안내
    time.sleep(0.4)
    return (
        "🤔 **해당 내용을 지식 베이스에서 찾지 못했습니다.**\n\n"
        "아래 키워드로 다시 질문해 보시거나, 직접 인사지원팀에 문의해 주세요.\n\n"
        "**검색 가능한 주요 주제**\n"
        "- 보육료 / 육아 지원\n"
        "- 경조사 (결혼·출산·부모상 등)\n"
        "- 연차 / 플러스 휴가 / 장기근속 휴가\n"
        "- 재택근무 / 자율출근\n"
        "- 출장 신청 / 결재선\n"
        "- 자격증 지원\n"
        "- 비용·경비 전표 결재\n"
        "- 사외교육 신청\n"
        "- WIFI / 문서보안 / 명함 신청\n"
        "- 학자금 / 입학 선물\n\n"
        "📞 인사지원팀 직통: **내선 1234**"
    )

# ── [Mock 모드 끝] ────────────────────────────────────────────────────────────


# 실제 운영 시 아래 함수명을 get_ai_response로 변경하고
# 위 주석을 해제하면 바로 API 모드로 전환됩니다.
get_ai_response = get_mock_response


def handle_send(question: str):
    """메시지 처리 공통 함수"""
    question = question.strip()
    if not question:
        return

    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": question})

    # 로딩 표시 후 응답
    with st.spinner("답변을 생성하고 있습니다..."):
        try:
            answer = get_ai_response(st.session_state.messages)
        except Exception as e:
            answer = f"⚠️ Mock 응답 중 오류가 발생했습니다: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()


# 전송 버튼 / 엔터
if send_clicked and user_input:
    handle_send(user_input)
elif hasattr(st.session_state, "pending_response") and st.session_state.pending_response:
    st.session_state.pending_response = False
    # 빠른 질문 처리: 마지막 user 메시지에 대한 응답
    last_user = st.session_state.messages[-1]["content"]
    with st.spinner("답변을 생성하고 있습니다..."):
        try:
            answer = get_ai_response(st.session_state.messages)
        except Exception as e:
            answer = f"⚠️ Mock 응답 중 오류가 발생했습니다: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# ──────────────────────────────────────────
# 10. 대화 초기화 버튼
# ──────────────────────────────────────────
if st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    col_clear = st.columns([4, 1])[1]
    with col_clear:
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
