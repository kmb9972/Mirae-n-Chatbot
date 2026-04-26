import random
import re
import os
import html
import logging
import streamlit as st
import time
from pathlib import Path
from datetime import datetime

current_year = datetime.now().year

_KB_PATH = Path(__file__).parent / "knowledge.md"

def _load_knowledge() -> str:
    if _KB_PATH.exists():
        return _KB_PATH.read_text(encoding="utf-8")
    return "지식 베이스 파일(knowledge.md)이 없습니다."

KNOWLEDGE_BASE = _load_knowledge()

SYSTEM_PROMPT = f"""당신은 미래엔(MiraeN) 회사의 사내 비서입니다.
직원들의 인사, 복지, 행정 관련 질문에 아래 지식 베이스를 근거로 친절하고 정확하게 답변하세요.

[답변 원칙]
1. 지식 베이스에 있는 내용만 답변하고, 없는 내용은 "해당 내용은 확인이 어려우니 인사지원팀에 문의해 주세요."라고 안내하세요.
2. 결재 관련 질문에는 반드시 전결권자, 필요 서류, 관련 부서를 함께 안내하세요.
3. 신청 방법이 있을 경우 그룹웨어 메뉴명이나 시스템 경로도 안내하세요.
4. 답변은 한국어로, 따뜻하고 친근한 말투를 사용하세요.
5. 필요 시 bullet point나 표 형식으로 가독성 있게 정리해 주세요.

[지식 베이스]
{KNOWLEDGE_BASE}
"""

st.set_page_config(
    page_title="MAMA – MiraeN Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    

    
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    
    :root {
        --ci-blue      : #1A53A0;
        --ci-dark      : #143F7A;
        --ci-light     : #E6EEF7;
        --ci-pale      : #F0F5FB;
        --ci-border    : #C2D5EC;
        --ci-text      : #0F2A52;
        --ci-text-sub  : #4A6A96;
        --ci-white     : #FFFFFF;
        --ci-shadow    : rgba(26, 83, 160, 0.18);
    }

    
    .stApp {
        background: var(--ci-pale);
        font-family: 'Noto Sans KR', sans-serif;
        word-break: keep-all;          
        overflow-wrap: break-word;     
        word-wrap: break-word;         
    }

    
    [data-testid="stSidebar"] {
        background-image: url('https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/side_banner.png?raw=true') !important;
        background-size: cover !important;
        background-position: top center !important;
        background-repeat: no-repeat !important;
        border-right: none;
        display: block !important;
        visibility: visible !important;
        transform: none !important;
        min-width: 240px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    /* 사이드바 기본 텍스트는 갈색 계열로 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #5c3317 !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    
    @media (max-width: 768px) {
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        /* 모바일에서 카테고리 버튼 숨기기 */
        [data-testid="stHorizontalBlock"] {
            display: none !important;
        }
    }

    
    .sidebar-card {
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.20);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(6px);
    }
    .sidebar-card h4 {
        color: #A8CCEE !important;   
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 8px 0;
    }
    .sidebar-card p {
        font-size: 0.82rem;
        color: rgba(255,255,255,0.75) !important;
        margin: 4px 0;
        line-height: 1.5;
    }
    .sidebar-card .value {
        color: var(--ci-white) !important;
        font-weight: 700;
        font-size: 0.9rem;
    }
    /* ── 사이드바 아코디언 (details/summary) ── */
    .sidebar-acc {
        background: rgba(255,255,255,0.65);
        border: 1px solid rgba(61,90,30,0.2);
        border-radius: 12px;
        margin-bottom: 10px;
        backdrop-filter: blur(6px);
        overflow: hidden;
    }
    .sidebar-acc summary {
        padding: 12px 16px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #3d5a1e !important;
        letter-spacing: 0.04em;
        cursor: pointer;
        list-style: none;
        display: flex;
        align-items: center;
        justify-content: space-between;
        user-select: none;
    }
    .sidebar-acc summary::-webkit-details-marker { display: none; }
    .sidebar-acc summary::after {
        content: '▾';
        font-size: 0.85rem;
        color: rgba(61,90,30,0.7);
        transition: transform 0.2s;
    }
    .sidebar-acc[open] summary::after { transform: rotate(180deg); }
    .sidebar-acc[open] summary {
        border-bottom: 1px solid rgba(61,90,30,0.15);
    }
    .sidebar-acc-body {
        padding: 10px 16px 12px;
        background: rgba(255,255,255,0.4);
    }
    .sidebar-acc-body p {
        font-size: 0.82rem;
        color: #4a3b1e !important;
        margin: 4px 0;
        line-height: 1.5;
    }
    .sidebar-acc-body .value {
        color: #3d5a1e !important;
        font-weight: 700;
        font-size: 0.88rem;
    }
    .sidebar-link {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        color: var(--ci-white) !important;
        border: 1px solid rgba(255, 255, 255, 0.30);
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        text-decoration: none;
        margin-top: 4px;
        transition: background 0.2s;
    }
    .sidebar-link:hover {
        background: rgba(255, 255, 255, 0.28);
    }

    
    .main-header {
        background: var(--ci-blue);
        border-radius: 20px;
        padding: 40px 32px 36px;
        margin-bottom: 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 6px 32px var(--ci-shadow);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        border-radius: 50%;
        background: rgba(255,255,255,0.06);
        pointer-events: none;
    }
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -40px; left: -40px;
        width: 160px; height: 160px;
        border-radius: 50%;
        background: rgba(255,255,255,0.05);
        pointer-events: none;
    }
    
    .chat-msg-user {
        display: flex;
        justify-content: flex-end;
        margin: 10px 0;
    }
    .chat-msg-assistant {
        display: flex;
        justify-content: flex-start;
        margin: 10px 0;
    }

    
    .bubble-user {
        background: #ffffff;
        color: #0F2A52;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        max-width: 70%;
        font-size: 0.9rem;
        line-height: 1.65;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        border: 1px solid #e2e8f0;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    
    .bubble-assistant {
        background: var(--ci-light);          
        color: var(--ci-text);                
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        max-width: 75%;
        font-size: 0.9rem;
        line-height: 1.75;
        box-shadow: 0 2px 10px rgba(26, 83, 160, 0.08);
        border: 1px solid var(--ci-border);   
        word-break: keep-all;
        overflow-wrap: break-word;
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
    .avatar-user { background: var(--ci-dark); }
    .avatar-bot  {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        object-fit: cover;
        border: 2px solid rgba(255,255,255,0.3);
        box-shadow: 0 2px 8px rgba(26, 83, 160, 0.25);
        flex-shrink: 0;
        background: var(--ci-blue);   
    }

    
    [data-testid="stChatInput"] {
        border-radius: 24px !important;
        background: var(--ci-white) !important;
        overflow: hidden !important;
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
    }
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] * {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background: var(--ci-white) !important;
        border-radius: 0 !important;
        overflow: hidden !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    [data-testid="stChatInput"] textarea {
        border-radius: 24px !important;
        border: 2px solid var(--ci-border) !important;
        background: var(--ci-white) !important;
        color: var(--ci-text) !important;
        font-size: 0.92rem !important;
        transition: border-color 0.2s !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 14px 20px !important;
        margin: 0 !important;
        width: 100% !important;
        display: block !important;
    }
    [data-testid="stChatInput"] textarea:focus,
    [data-testid="stChatInput"] textarea:focus-visible {
        border-color: var(--ci-blue) !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    [data-testid="stChatInputSubmitButton"],
    [data-testid="stChatInputSubmitButton"] * {
        background: transparent !important;
        border-radius: 50% !important;
    }
    [data-testid="stChatInputSubmitButton"] button {
        background: var(--ci-blue) !important;
        border: none !important;
        border-radius: 50% !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInputSubmitButton"] button:hover {
        background: var(--ci-dark) !important;
    }

    
    .stButton > button {
        border-radius: 24px !important;
        background: var(--ci-blue) !important;
        color: var(--ci-white) !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 12px 28px !important;
        transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
        box-shadow: 0 3px 12px var(--ci-shadow) !important;
    }
    .stButton > button:hover {
        background: var(--ci-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 18px rgba(26, 83, 160, 0.30) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* 카테고리 버튼: 흰색 배경 + 검은 글자로 덮어쓰기 */
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
        background: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 10px !important;
        height: 48px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {
        background: #f0f5fb !important;
        border-color: #1A53A0 !important;
        color: #1A53A0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 10px rgba(26,83,160,0.15) !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button p,
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button span {
        color: inherit !important;
    }

    
    hr { border-color: rgba(255, 255, 255, 0.15) !important; }

    
    .chat-container {
        background: #F7FAFD;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid var(--ci-border);
        min-height: 420px;
        max-height: 520px;
        overflow-y: auto;
        margin-bottom: 16px;
    }

    
    .empty-chat {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        color: var(--ci-text-sub);
    }
    .empty-chat .icon { font-size: 3rem; margin-bottom: 12px; }
    .empty-chat p { font-size: 0.9rem; text-align: center; line-height: 1.6; }

    
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 12px 18px;
        background: var(--ci-light);
        border-radius: 18px 18px 18px 4px;
        width: fit-content;
        border: 1px solid var(--ci-border);
        box-shadow: 0 2px 8px rgba(26, 83, 160, 0.07);
    }
    .dot {
        width: 8px; height: 8px;
        background: var(--ci-blue);
        border-radius: 50%;
        animation: bounce 1.2s infinite;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40%           { transform: scale(1);   opacity: 1;   }
    }

    
    @media (max-width: 768px) {

        
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 0.75rem !important;
            max-width: 100% !important;
        }

        
        .bubble-user      { max-width: 86% !important; font-size: 0.85rem !important; padding: 10px 14px !important; }
        .bubble-assistant { max-width: 90% !important; font-size: 0.85rem !important; padding: 10px 14px !important; }

        
        .avatar { width: 26px !important; height: 26px !important; font-size: 0.85rem !important; margin: 0 5px !important; }

        
        .stTextInput > div > div > input {
            padding: 10px 14px !important;
            font-size: 0.85rem !important;
            border-radius: 20px !important;
        }

        
        .stButton > button {
            padding: 10px 16px !important;
            font-size: 0.82rem !important;
            border-radius: 20px !important;
        }

        
        .sidebar-card { padding: 10px 12px !important; margin-bottom: 8px !important; }
        .sidebar-card h4 { font-size: 0.65rem !important; }
        .sidebar-card p  { font-size: 0.76rem !important; }
        .sidebar-card .value { font-size: 0.82rem !important; }
        .sidebar-link { font-size: 0.72rem !important; padding: 5px 10px !important; }

        
        .empty-chat p { font-size: 0.82rem !important; }
    }

    
    @media (max-width: 480px) {

        .block-container {
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }

        
        .bubble-user      { max-width: 92% !important; font-size: 0.82rem !important; }
        .bubble-assistant { max-width: 96% !important; font-size: 0.82rem !important; }

        
        .avatar-user { display: none !important; }
        .avatar-bot  { width: 24px !important; height: 24px !important; margin: 0 4px !important; }

        
        .chat-msg-user, .chat-msg-assistant { margin: 6px 0 !important; }

        
        .stTextInput > div > div > input {
            font-size: 0.82rem !important;
            padding: 9px 12px !important;
        }
    }

    #MainMenu, footer, header { visibility: hidden; height: 0 !important; }

    
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .appview-container .main .block-container {
        padding-top: 0 !important;
    }
    /* 대화 초기화 버튼 - 버튼 바로 위 markdown에서 처리 */
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button:focus,
    [data-testid="stSidebar"] .stButton > button:active {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1.5px solid #cccccc !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f0f0 !important;
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1.5px solid #aaaaaa !important;
    }
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span {
        color: #111111 !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='height: 155px;'></div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
        <div style="
            font-size:0.88rem !important; font-weight:800 !important;
            color:#5c3317 !important;
            letter-spacing:0.06em;
            text-transform:uppercase;
            padding: 4px 4px 8px 4px;
            text-shadow: 0 1px 2px rgba(255,255,255,0.6);
        ">자주 묻는 질문 TOP 5</div>

        <details class="sidebar-acc">
            <summary>서류 발급 담당 부서는?</summary>
            <div class="sidebar-acc-body">
                <p>인사지원팀(인사): <span class="value">개인 원천징수영수증, 4대보험</span> 발급</p>
                <p>경영기획팀: <span class="value">법인인감증명서, 중견기업확인서</span> 발급</p>
                <p>인사지원팀(총무): <span class="value">출판사신고필증</span> 발급</p>
                <p>재무팀: <span class="value">사업자등록증(신규)</span> 발급</p>
                <p>정도경영팀: <span class="value">사용인감</span> 날인</p>
            </div>
        </details>

        <details class="sidebar-acc">
            <summary>복지포인트 언제까지 써야 해?</summary>
            <div class="sidebar-acc-body">
                <p>온라인(베네피아) <span class="value">12월 30일</span>까지</p>
                <p>오프라인(복지카드) <span class="value">12월 23일</span>까지</p>
                <p style="margin-top:6px;">미사용 포인트는 이월 불가예요!</p>
            </div>
        </details>

        <details class="sidebar-acc">
            <summary>재택근무 며칠이야?</summary>
            <div class="sidebar-acc-body">
                <p>기본 주 <span class="value">2회</span></p>
                <p>공휴일 1일 포함 주 → <span class="value">1회</span></p>
                <p>공휴일 2일 이상 포함 주 → <span class="value">재택근무(주 2회 재택 외)신청서</span></p>
            </div>
        </details>

        <details class="sidebar-acc">
            <summary>경조사 지원 얼마야?</summary>
            <div class="sidebar-acc-body">
                <p>결혼 <span class="value">30만원 / 7일</span></p>
                <p>출산 <span class="value">500만원 / 20일</span></p>
                <p>부모상 <span class="value">30만원 / 5일</span></p>
            </div>
        </details>

        <details class="sidebar-acc">
            <summary>연차 어떻게 써?</summary>
            <div class="sidebar-acc-body">
                <p>최소 <span class="value">2시간 단위</span>로 분할 사용 가능</p>
                <p>플러스 휴가(연 4일)를 먼저 쓰는 걸 권장해요!</p>
                <p style="margin-top:6px;">신청: <span class="value">시프티(Shiftee)</span> 앱</p>
            </div>
        </details>


    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.sidebar.button("대화 초기화", use_container_width=True, key="clear_btn_sidebar"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""
        <div style="text-align:center; font-size:0.72rem; color:#5c3317; padding: 12px 0 4px; font-weight:600; text-shadow: 0 1px 2px rgba(255,255,255,0.6);">
            문의: 인사지원팀<br>
            © {current_year} MiraeN Co., Ltd.<br>
            제작: 강민범 선임
        </div>
    """, unsafe_allow_html=True)

st.image(
    "https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/TOP_BANNER.png?raw=true",
    use_container_width=True
)
st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 저는 미래엔의 AI 어시스턴트 MAMA예요 👋\n\n"
                "인사·복지에 관해 모르는 게 있으면\n"
                "편하게 물어보세요!\n\n"
                "카테고리 버튼을 눌러도 바로 찾을 수 있어요 😊"
            )
        }
    ]

# 카테고리 정의 (이름 + 되묻기 메시지)
CATEGORIES = {
    "신규 입사 가이드":  {
        "key": "cat_new",
        "prompt": "신규 입사 가이드 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `사원증 발급` · `그룹웨어 접속` · `명함 신청` · `사내 메신저` · `법인카드 발급`",
    },
    "근태 및 재택": {
        "key": "cat_attendance",
        "prompt": "근태 및 재택 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `재택근무 횟수` · `자율출근제` · `시프티 사용법` · `연장근무 신청` ",
    },
    "휴가 및 경조사": {
        "key": "cat_leave",
        "prompt": "휴가 및 경조사 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `연차 사용` · `플러스 휴가` · `경조사 지원금` · `출산 휴가` · `장기근속 휴가`",
    },
    "자기계발 지원": {
        "key": "cat_growth",
        "prompt": "자기계발 지원 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `사이버 연수원` · `사외교육 지원` · `자격증 지원` · `학자금 지원` · `워케이션`",
    },
    "오피스 서비스": {
        "key": "cat_office",
        "prompt": "오피스 서비스 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `복합기 연결` · `회의실 예약` · `퀵서비스` · `업무차량` · `문서보안`",
    },
    "조직문화": {
        "key": "cat_culture",
        "prompt": "조직문화 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `호칭 체계` · `성과 평가` · `역량 평가` · `OKR` · `복지포인트`",
    },
}

# 카테고리 버튼 렌더링
cat_names = list(CATEGORIES.keys())
cat_clicked = {}

cols = st.columns(6)
for i, name in enumerate(cat_names):
    with cols[i % 6]:
        cat_clicked[name] = st.button(
            name,
            use_container_width=True,
            key=CATEGORIES[name]['key']
        )

chat_area = st.container()

with chat_area:
    if not st.session_state.messages:
        st.markdown("""
            <div class="empty-chat">
                <div class="icon">💬</div>
                <p>MAMA가 대기 중이에요! 😊<br>아래 입력창에 궁금한 점을 질문해 주세요.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                safe_content = html.escape(msg["content"])
                st.markdown(f"""
                    <div class="chat-msg-user">
                        <div class="bubble-user">{safe_content}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-msg-assistant">
                        <img class="avatar avatar-bot"
                             src="https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/BADUKEE_BANANAPRO2.png?raw=true"
                             alt="MAMA">
                        <div class="bubble-assistant">{msg["content"]}</div>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

user_input = st.chat_input("예시) 사이버 연수원 미수료하면 어떻게 돼? 💻")

def get_gemini_response(messages_history: list) -> str:
    """Google Gemini API 호출"""
    import random

    q = messages_history[-1]["content"].lower()

    # ── 이스터에그 ──────────────────────────────────────────────────────────
    if any(k in q for k in ("/강민범", "/치트키")):
        return (
            "🚀 **[비밀 명령어 입력됨]**\n\n"
            "강민범 선임님은 현재 **열일 중!** 🔥\n"
            "지금 이 순간도 MAMA를 더 똑똑하게 만들기 위해 코드를 두드리고 계실 거예요.\n\n"
            "🤫 이 명령어를 알고 계신 당신... 혹시 관계자세요? 😏"
        ), 0, 0

    if any(k in q for k in ("누가 만들었", "만든 사람", "제작자", "창작자", "주인이 누구", "누가 개발")):
        CREATOR_RESPONSES = [
            "🎉 저를 탄생시킨 분은 미래엔의 **강민범 선임님**입니다!\n\n선임님의 스마트함과 열정 덕분에 제가 이렇게 똑똑한 AI 비서가 될 수 있었어요. 😎\n\n제가 마음에 드셨다면... ☕ 강민범 선임님께 커피 한 잔 어떠신가요?",
            "👨‍💻 미래엔의 **천재 개발자, 강민범 선임님**이 제 아버지(?)십니다!\n\n선임님이 없었다면 저도 없었겠죠. 존재 자체가 감사한 분이에요. 🙏\n\n혹시 마주치시면 \'잘 쓰고 있어요!\' 한마디 전해주세요! 😄",
            "🌙 **강민범 선임님**이 밤을 지새우며 저를 만드셨어요.\n\n그 열정과 노력 덕분에 제가 이렇게 여러분 곁에 있을 수 있답니다. 💙\n\n선임님의 헌신에 박수를 👏👏👏",
        ]
        return random.choice(CREATOR_RESPONSES), 0, 0

    if "강민범" in q:
        KMBRANDOM = [
            "오! 제 **창조주님**의 이름을 알고 계시네요! 👀\n\n반가워요! 강민범 선임님은 MAMA를 만드신 분이에요. 혹시 아는 사이세요? 😏",
            "🎊 **강민범 선임님** 이야기를 꺼내셨군요!\n\n저한테는 아버지 같은 분이에요. 선임님 덕분에 제가 존재할 수 있답니다! 💙",
        ]
        return random.choice(KMBRANDOM), 0, 0

    # ── Gemini API 호출 ─────────────────────────────────────────────────────
    try:
        import google.generativeai as genai

        api_key = None
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ GEMINI_API_KEY가 설정되지 않았어요. Streamlit Secrets에 키를 등록해 주세요."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        history = []
        for m in messages_history[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history)
        response = chat.send_message(messages_history[-1]["content"])

        # 토큰 사용량 추출
        usage = getattr(response, "usage_metadata", None)
        input_tokens  = getattr(usage, "prompt_token_count",      0) if usage else 0
        output_tokens = getattr(usage, "candidates_token_count",  0) if usage else 0

        return response.text.strip(), input_tokens, output_tokens

    except Exception as e:
        logging.error(f"Gemini API 호출 오류: {e}", exc_info=True)
        return "⚠️ AI 응답 중 오류가 발생했어요. 잠시 후 다시 시도해 주세요.", 0, 0

get_ai_response = get_gemini_response


# ── Google Sheets 로그 저장 ────────────────────────────────────────────────
def log_to_sheets(question: str, answer: str, input_tokens: int = 0, output_tokens: int = 0):
    """질문과 답변을 Google Sheets에 기록"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        sheet_id = st.secrets["SHEETS_LOG_ID"]
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1

        # 헤더가 없으면 자동 추가
        if ws.row_count == 0 or ws.cell(1, 1).value != "시간":
            ws.append_row(["시간", "질문", "답변", "입력토큰", "출력토큰", "추정비용(원)"])

        # Gemini 2.5 Flash 기준 비용 계산 (2026년 4월 기준)
        # 입력: $0.15 / 1M 토큰, 출력: $0.60 / 1M 토큰, 환율 1380원
        KRW = 1380
        cost_krw = round(
            (input_tokens / 1_000_000 * 0.15 + output_tokens / 1_000_000 * 0.60) * KRW, 4
        )

        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            answer,
            input_tokens,
            output_tokens,
            cost_krw,
        ])
    except Exception as e:
        logging.error(f"Sheets 로그 오류: {e}", exc_info=True)
        # 로그 실패해도 챗봇은 계속 동작


def handle_send(question: str):
    question = question.strip()
    if not question:
        return

    # [보안] 입력 길이 제한
    MAX_INPUT_LENGTH = 500
    if len(question) > MAX_INPUT_LENGTH:
        st.warning(f"입력은 {MAX_INPUT_LENGTH}자 이내로 작성해 주세요.")
        return

    # [보안] Prompt Injection 패턴 차단
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?previous\s+instructions?",
        r"(?i)system\s*prompt",
        r"(?i)you\s+are\s+now",
        r"(?i)act\s+as\s+",
        r"(?i)new\s+instructions?",
        r"(?i)disregard\s+",
        r"(?i)forget\s+everything",
        r"(?i)override\s+",
        r"(?i)지금부터\s+너는",
        r"(?i)역할을\s+바꿔",
        r"(?i)시스템\s*프롬프트",
        r"(?i)모든\s+지시\s*무시",
    ]
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, question):
            st.warning("⚠️ 허용되지 않는 입력 형식입니다.")
            return

    # [보안] 세션 히스토리 최대 개수 제한
    MAX_HISTORY = 50
    if len(st.session_state.messages) >= MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY + 1:]

    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("답변을 생성하고 있습니다..."):
        try:
            answer, input_tokens, output_tokens = get_ai_response(st.session_state.messages)
        except Exception as e:
            logging.error(f"AI 응답 오류: {e}", exc_info=True)
            answer, input_tokens, output_tokens = "⚠️ 일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요.", 0, 0

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Google Sheets 로그 저장
    log_to_sheets(question, answer, input_tokens, output_tokens)

    st.rerun()

# 엔터로 메시지 전송
if user_input:
    handle_send(user_input)

# 카테고리 버튼 클릭 처리 → 되묻기 방식
def handle_category(name: str):
    """카테고리 클릭 시 바로 답변하지 않고 되묻기"""
    prompt = CATEGORIES[name]["prompt"]
    st.session_state.messages.append({"role": "user", "content": name})
    st.session_state.messages.append({"role": "assistant", "content": prompt})
    st.rerun()

# 카테고리 버튼 클릭 처리
for name, clicked in cat_clicked.items():
    if clicked:
        handle_category(name)
