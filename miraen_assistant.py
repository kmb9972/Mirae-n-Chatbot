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
    [data-testid="stSidebar"] * {
        color: var(--ci-white) !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    
    @media (max-width: 768px) {
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
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
        background: rgba(255,255,255,0.55);
        border: 1px solid rgba(0,0,0,0.12);
        border-radius: 12px;
        margin-bottom: 10px;
        backdrop-filter: blur(6px);
        overflow: hidden;
    }
    .sidebar-acc summary {
        padding: 12px 16px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #1A53A0 !important;
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
        color: rgba(26,83,160,0.6);
        transition: transform 0.2s;
    }
    .sidebar-acc[open] summary::after { transform: rotate(180deg); }
    .sidebar-acc[open] summary {
        border-bottom: 1px solid rgba(0,0,0,0.08);
    }
    .sidebar-acc-body {
        padding: 10px 16px 12px;
        background: rgba(255,255,255,0.4);
    }
    .sidebar-acc-body p {
        font-size: 0.82rem;
        color: #2d4a6e !important;
        margin: 4px 0;
        line-height: 1.5;
    }
    .sidebar-acc-body .value {
        color: #1A53A0 !important;
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
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='height: 155px;'></div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
        <div style="
            font-size:0.72rem; font-weight:700;
            color:#1A53A0;
            letter-spacing:0.08em;
            text-transform:uppercase;
            padding: 4px 4px 8px 4px;
        ">자주 묻는 질문 TOP 5</div>

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
                <p>공휴일 2일 이상 포함 주 → <span class="value">불가</span></p>
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

        <details class="sidebar-acc">
            <summary>사이버 연수원 미수료하면?</summary>
            <div class="sidebar-acc-body">
                <p>향후 <span class="value">6개월간</span> 수강 신청 제한!</p>
                <p style="margin-top:6px;">매월 중순 전사게시판에서 신청, 익월 수강이에요.</p>
            </div>
        </details>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
        <style>
        button[data-testid="baseButton-secondary"][key="clear_btn_sidebar"],
        [data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button {
            background-image: url('data:image/png;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAC5A0IDASIAAhEBAxEB/8QAHQABAQADAAMBAQAAAAAAAAAAAAgGBwkDBAUCAf/EAFoQAAEDAwICBgQFCw8LAwUAAAABAgMEBQYHERIhCBYxQVaUE1Fh0hQiNnWzCRUXMjdCV3GBlbQYIzg5Q1JicnR2g5Gh0dMzVGNzgoWSk7G1wSRT8CY0VaLU/8QAFwEBAQEBAAAAAAAAAAAAAAAAAAIBA//EACMRAQEBAQACAgEEAwAAAAAAAAABEQISIQMxUSIycfATQWH/2gAMAwEAAhEDEQA/ALLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEm538t7985VH0rgM7+W9++cqj6VwArIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASbnfy3v3zlUfSuAzv5b375yqPpXACsgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABJud/Le/fOVR9K4DO/lvfvnKo+lcAKyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaZ0s1068635Vpp1W+t/V/4Z/6/wCuHpfhHwepZB/k/Rt4eLj4vtl22259puYACY+h/q9nWoueZXacrucFXSW6BH0zI6WOJWr6VW81aiKvL1lOAAAABMfSn1ezrA9ZMRxvGrnBS225wQPqo30scivV1Q5i7OciqnxURORTgAA+JqBcaq0YHkF2oXpHV0VrqaiBytRyNeyJzmrsvJeaJyA+2Cf+hVqbmGpuL5BXZhcIayeirY4oHR0zIuFqs3VNmIm/MoAAAAAAAAAADH9SMk6nYFfMq+BfDvrVQy1fwf0vo/S8DVXh4tl4d9u3ZfxGJ9HHVf7MOD1mTfWH6yfBrk+h+D/DPhHFwxRP4+LgZtv6Xbbbu7efINmAAAAAAAAAAAAAAJssOrGb1fTRr9NJ7lC7GofScFMlLGjk2pEkT4+3F9tz7SkwAAAAxHWe+XHGtJ8pyC0TNhuFvtc9RTSOYj0a9rFVFVF5Lz7lNf8AQy1CynUrS+5X3Lq2KsroL1LSRvjgZEiRNggeibNRE7Xu5+0DdwAAAmPWzV3OsY6VGH4HZ7nBDYbnPbWVUDqWN7npNUrHJs9U4k3by5LyKcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAk3O/lvfvnKo+lcBnfy3v3zlUfSuAFZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABiesV9uGL6V5PkVqdG2vt1smqadZGcTUe1qqm6d6bmWGv+kf8AcEzj5kqfo1Al7AdYulTntnlvGI2a3XWhhqHU0k0dJA1Gyo1rlbs56L2Pav5TIutnTS8H0Xl6b/FMm+pxfcQvP85J/wBGpimQJGocq6Zbq2BtTiFG2BZGpIvoKbk3fn+6eorkACM+ix+ze1V/3x/3KEswjPosfs3tVf8AfH/coSzAIm+p6fdTzz+TJ9OpbJE31PT7qeefyZPp1LZAl7UPP+lFb85vdDi+AUlbY4K2SOgqHUCuWWFHLwOVfSpvunsQ+D9kvpgfg0ovza7/ABivyctZ+lVj+J36TFcLtEuW35kvoJFieraaOXfbgRWorpXovJWtRE7uLdFQDQWqGP8ASQ1EzC05Tf8ATmobX2pjGU6U1LwRqjJFkTiRXrvzVe9ORsv7JfTA/BpRfm13+MeeHUvpfXONa2j0uttLA7m2KWidE9E/iyzo/f8AIfm29KvOMPvcFq1k00ntTZV2+E0cMkDuFO1zY5VVsqetWvT/AMAeL7JfTA/BpRfm13+MbvbcMquvRnu1wze3st2QzY/XrW0zI+BI3IyVETh3Xb4qNXtXtM7xHI7JluO0eQY9cIbhbaxnHDNGvJfWiovNrkXdFRdlRUVFPnas/cry35krfoHgTn9TX+RGW/OUP0RWRJv1Nf5EZb85Q/RFZAAAAAAGiLl0sdIbfcamgqay8JPTTPhkRtvcqcTVVF2Xf1oev+q90b/z29fm5395sOp0a0pqamWpqNPcblmler5HuoGKrnKu6qq7dqqeP7Cmkf4OMZ/N8f8AcBpTWLpP6VZRpXk+O2qruzq+42yamp0koXNar3NVE3Xfkm5gPQ712wDTDTO42DKqi4R1tReZayNKekWRvo3QwsTmi9u8buRubpJab6UYnodld7psGx6hq4qFY6WeKiYx7JpHJGxWqib78TkNY9AjEdPcywXIaXJcWst4utBc2yelq6ZskjYJImoxu6/e8Uci/jVQNpfqvdG/89vX5ud/eP1Xujf+e3r83O/vM/8AsKaR/g4xn83x/wBw+wppH+DjGfzfH/cBlmJX235RjNtyK1OkdQXGmZU06yM4XKxybpuncux9Q9W026htFsprZbKSGjoqWNIoIIWI1kbETZGtROxEPaA0p0i8V1syG9WqbSvKoLLRQ0z21kclUsXpJFdui7Ix2/I1X9jTpgfhLovzk7/BK/AEgfY06YH4S6L85O/wTG9TLP0qNPsKr8uv+pUbrfQrGkraevV8i8cjY28KLEm/N6d/ZuXGTP8AVEsijtujtusDX7VF4ujN2b9sMLVe5fyPWL+sDOOh7fshyfQu2X7J7tU3Svq6mpX086fG4GyuYib96JwqbgNd9GqwvxrQbDrTKxY5UtrKiRipsrXzKszkX2osiobEAjPFf2yO6/036AhZhGeK/tkd1/pv0BCzANV9IvIdVMestqm0rx6G9Vs1S9tYySnWX0caN3auyObtzNKfZL6YH4NKL82u/wAYr8wnWHVDE9LMcS85PVvR0qqyko4ER09S9E3VGNVU5Jy3cqoibpuvNNwmDMcs6WWVYrc8buemsDaK50z6adYberXox6bLwqsq7L+Q+Bo7+qe0rxmpx7GNN3Po6itdWvWro/SP9I5jGLsqSJy2jby29ZmlL0idds+kdNplpRF9bFerWVNRDLOi7Lt/leKONF9ac9v7T93DWbpR4hG645XpVQ1NtjbxzOgo5F9G1N91V8Ur0YnrVyL3Afn7JfTA/BpRfm13+MbI6POX68X/ADSso9UcQp7NZmW58sE8dIsSuqEkjRrN1kd96si7bdx9fQLpBYfqyq22mZLZ8gjj9JJbal6O9IidronpskiJ38kcnbttzNwARN0lv2dWnn8ps36apbJE3SW/Z1aefymzfpqlsgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASbnfy3v3zlUfSuAzv5b375yqPpXACsgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1/0j/uCZx8yVP0amwDX/SP+4JnHzJU/RqBqb6nF9xC8/zkn/RqYpkmb6nF9xC8/wA5J/0amKZAAACCNKNQsW016X+p19y6tlo6Gequ1JG+OB8qrK64MeibNRV7GO5+woT9Vhol4jrfzZP7po7QXF8dy3pm6o23J7LQ3ijjmu87IKuFJGNkS4xtRyIvfs5yb+1SpPsKaR/g4xn83x/3ATH9TslZUal5vPEu8clGx7V223RZlVC3CJPqd7GRan5zHG1GsZSNa1qdiIk67IW2BrfpO5NXYhoNll+tkr4ayKkbBDKxdnRumkZCj0XuVPSbovcqGrOgJp1ZLZplBqJNTR1F8vUk7I6h6bup4I5XRcDfUrnMcqqnaioncbp1uw52f6UZFiMT2MnuFIqU7n/apMxySR7+pONjd19RMXRC1rt+n9JUaSalq+wS2+rlSjqatFbHC5z1V8Ev7z46ucjl+KvEu6py3Czz4GoGH2DOsVrMbySgjq6GqYqc0TjidtykYv3r07UVP+h9K3Xa1XKh+HW650VZScPH6eCdskfD6+JFVNuS8zVmt/SBwXTixVXwe7UN6yHgVtLbKSdJF9J3LKrVVI2p2rvsqp2IoGk+gFdLjYNSs50xqKtZ6WkSSpYnPhbLBM2CR7U7uJHs3/iJ6iptWfuV5b8yVv0DydegHg19idkGqeRwyxTX5PRUTpU2fOxz/SSzbfvXPRmy9/Cq9myrRWrP3K8t+ZK36B4Eu/U8slxyxYblMV7yC02uSW4ROjZWVkcKvRI9t0RypuhU9JnWEVlVDSUmY47UVE72xxRRXOFz5HuXZGtRHbqqqqIiIQx0RtB8Q1dxy+XHJLjfaSW31ccESW+eJjXNcziVXccb+e/q2KCxPoiabY1lVpyOhveWyVdqroa2Bk1VTrG58T0e1HIkCKrd2pvsqLt3oBQwAAAHhr6uloKKatrqmGlpYGLJNPNIjI42Im6uc5eSIidqqB5j8yvZFG6WV7WMYiuc5y7I1E7VVfUaR1C6UukmKQyMo70/JK5qLw09qZ6Rqr3byrtHt+JVX2KaMuuSa79Jyd1qx21OxfCZV2mkc5zIJGb/ALpMqI6df4Eabdm6ct0D99I/Prhr5qVadIdN3/C7RBV8VTWM39FPK3dHSqqfuMbVdsv3yqu2/wAXf594tt26Jeu9HeaFlXcsKvEPopOzilj5ekYvckrHbPb2boqJvzdtUug2jOLaR2N1PaWrW3apYiV10mbtLPtz4Wp94xF7Gp6k3VV5mW59iGP51i9VjeTW9lbb6lObV5Ojcn2r2O7WuTuVP+iqgHtYpkNlyrH6W/Y9cYLjbatnFDPEu6L3Ki96Ki7oqLzRU2U+oRBctOtbejdfqq+ab1M2TYpK/wBJUUyRLLu1P/fgTmion7rH3JzVqLsbN016YGnt9jjpcvp6vFbjttI6Rjp6ZXex7E4k/wBpqInrXtApIHy8YyKw5Ra0umOXmgu9CrlZ6ejnbKxHIiKrVVqrs5EVN0Xmm59QAAABCur1Wuv3S7tOF2yR1Rj9ll+CzSMduxY43cdXKi9ibqno0XsXhZ6zdPTH1th06xOTGbBVtXLLtErGLG/41DAqbLMu3NHr2M9u7vvdl9foRaQy4HhUmV36mWPIr/G13o5G7PpaXfiZGvejnLs9yexiLzaoFEMa1jEYxqNa1NkRE2REP6ABGeK/tkd1/pv0BCzCM8V/bI7r/TfoCFmACI8rtTdY+nZPjeQuklsVkTg+C78lhgjRys5dz5XLuvbs7buQtwifpARX3Q/pS0mr9FbpK2wXdyLOjU2arnR+jmhV3c9Ub6Ru/avr4VAtKhpaWho4aKipoaWmgYkcMMLEYyNqJsjWtTkiInch5jC9O9U8Cz62Q1uN5JQzvkROKkklbHUxL+9dEq8SL3b80XuVT7WU5ZjGLUT6zI8gtlpgYm6uqqlsar7ERV3VfUibqoEb9NbF6TS3VPFNTsLjjtlZW1Ek08UKcMfwmFzHcfCnc9H7OROS7Kq83LvblBUMrKGnq402ZPE2RvPfk5N//JCWrWSVXSi1zsOI4bT1XVq1Oc11Y6NU2jc5vp6lybfFbwta1jXc1VE7Fdsl4QxMhhZDE3hjjajWp6kRNkQCJelDUU9H038Cq6ueKnp4JrPJLLK9GsjY2scqucq8kRERVVVK3+yHgHjjGfztB7xHPTCslLkvTAxLHK6SaOkusVsop3wqiSNZLUvY5WqqKiO2cu26Km/cptP9RVpZ/wDn8z85Tf8A84FG2e62u80SVtouVHcaVXK1JqWdsrFVO1OJqqm6HuGH6Q6eWXTDDY8VsFVcKmijnknSStkY+Xieu6puxrU25eozAAAAAAAAAAAAAAAA8FfWUlvoZ66vqYaWlgYsk00z0YyNqJurnOXkiInepMWca6ZjqJkcmEaG22eRF+LPeXR7ORu+yvbxcomfw3fGXfkiLtvluNktb41A1HwrA6dJcpyCloZHN4o6fdZJ5E/gxtRXKndvtt61NIXjpWPute626caf3e/VHY18zV4l9qRRI5yov8ZF9h9PTjovWKkn+vepFznyy9zO9JMx0r0gR/fxOVeOVd+9yoi/vTfdltFpslCygs1so7dSMTZsNLA2JifkaiIPbf0xNDch6W+Ufrlvxy3Y5C5U2c6CCNW/jbO97v8A9QunfSruTHPqtSrZRq5qIrfhjo15/wCqg2RU9ZUgGHl/xLz9H+khGiSU+sUUkjVRUbJcalGr+P8AW1/q2Py7EOlrZlV1FnFsuey78KTRycXL/Twp+Lu/8lRgYeSWl1K6TeIr/wDU+m8F6pmIiySUtMr3qnr46d7mp7d2/wBR93EeljhdbVJRZXZbrjNUjuF7nN+ERRr38StRHp/wFEGPZlg+IZjTLBk+O2+5pw8LXzQp6VifwZE2c38ioMpsv3HuYxkdgyi2tuWO3iiulIvL0lNMj0avqdtzavsXZT6pMGW9Ge74zclyTRnK661XCPdUoqioVvEnbwNlTtTu4ZEVF73HlwDpG3fH72mIa2WOay3KPZv1xZArWu7kdJGnLZf38e7V9SJzG/k8d+lNA8FBWUlwooa2hqYaqlnYj4poXo9kjV7FRyclQ85qQAAAABJud/Le/fOVR9K4DO/lvfvnKo+lcAKyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADX/AEj/ALgmcfMlT9GpsAx/UjG+uOBXzFfhvwH660MtJ8I9F6T0XG1U4uHdOLbfs3T8YGhvqcX3ELz/ADkn/RqYphyo1qucqIiJuqr3Eg23oTy0iOZ9litbEvPgp7SsXxvWv6+p+16EFrkn9LUajXCXidu9fra3id6+ayLz9vMCn7tmeH2hivu2V2K3tTtWquEUSJ/xOQ9PCNRMJzatuFHieR0V4mtyRuqkplVzWI/iRqo7bZ2/A77VV25b7bpvoa1dCfT2FyOuWT5LWbLvwxOhhRfx7xuX+pUNx6SaPYLpctZJiNuqIKitY1lTPPVySuka1VVqbKvCmyqvYiLzAnLosfs3tVf98f8AcoSzCM+ix+ze1V/3x/3KEswCJvqen3U88/kyfTqWyRN9T0+6nnn8mT6dS2QBrzVjRfTzU3abJ7I1bg1nAy4Ur/Q1LU7kVyfboncj0cieo0ZdulVqFbbrV2+XRipfJSzvhe5k8ytVWuVqqi+h5pyPny9LHU6adjKPRuZvFs1GObUyOc7fu2Yns5bAaf6R2jNi021VxzE7LdLlVUV4iikdJVqx0kXHO6PZFa1qLsiIvZ2lV4D0TdJ8Xr46+spbhkdRG7iY26zNdC1f9WxrWuT2P4kJf1fv+rWqmf2PKZdKL7SVloiYyKnprXVSNk4JVk3X4m/au3I2+3WnpV3HlQaM09K17V4VqLPVsc1fXu+Vqf1p/WBXUTGRRtiiY1jGIjWtamyNROxET1GN6s/cry35krfoHk4NufTWvi/rNotFgjd2SK2jTh7PvXvkd/YbGxqy6pWbQrPWarX+ivV0qLdWS08lNJukUXwVycCokbGpzRV5b9oGvPqa/wAiMt+cofoisiTfqa/yIy35yh+iKyAAAAeKspqespJqOrhjnp543RyxSN3a9jk2Vqp3oqKqHlAGpsJ6Oej+J1DaqjxGnr6pruJs1ykdVK1e1NmvVWIqetG7+02xGxkbGxxtaxjURGtamyIidyH9AGv+kf8AcEzj5kqfo1NTfU4vuIXn+ck/6NTG2ekf9wTOPmSp+jU1N9Ti+4hef5yT/o1MBTJgOoGjemedvknyTEbfUVcn21ZC1YKhV7d1kjVHO/KqmfADHNOMLsGn+I0uL43TPgt9Mr3N9I/je9znK5znO713X+pETuMjAAGgOkp0kcf03pqmwY7LBeMuVqs9E1eKGhX99Mqdrk/9tOfr4U23wDXjPtfcu1JuulOCY1VWaGndwy1VG9Vkngd9pK6pXhbCxyc9k2dvu3iVd0Mu6P3RYsGE1EGRZrNBkWRNVJI4+FVpKV/bu1HJvI5F++ciJ6moqbgYT0YdCr9lWUN1f1eSarnqZEq6KirE3kqZPvZ5W/esTlwM2TfZOSNREdYwAAAARniv7ZHdf6b9AQswjPFf2yO6/wBN+gIWYAPQyGy2jIbPUWe+22luVvqG8MtPUxo9jk/Evenai9qLzQ1X0jtW8n0tqLL9ZMFkyamuLJuOSKWRFhfGreSo1ju1H8lXbsX1GoJeltqEsbki0Xqmv2+KrpJ3In5PRJv/AFge1r30V9OLJgmSZjj1RebZPbqGarjokqGy06qxquRvx2q9E7vt1NfdEXo+YhqrhNblOTXK8RupLtJRNpaORkbHtbFC/dyq1y81kVOW3Yh9rN+kBq5m2C3jHHaO1sdLdqOSkdUQUlU9WI9Faqp8XZVQ+BoNlfSA0ww2qxvF9ILlWw1da64JUXCyVnJXRxsVE2ViKm0aKnPfmoFs6e4FiOn9nW1YjY6W107lRZVjRXSTKne97t3PX8art3GSkjsz3pj3pypQ6dWu3cWypvTMh25f6ef/AK9/L2GR6f2LpY12aWe45nlFno7HT1ccldQtWBrpYUcnGxPQxLuqonLdydvagGu+kt+zq08/lNm/TVLZIm6S37OrTz+U2b9NUtkAAAAAAAAAAAAAAH5keyON0kj2sY1Fc5zl2RETtVVPXu1xoLTbKi53Orho6KmjWSaeZ6NZG1O1VVSKekb0kKvL6esxTC0kosflRYqmse3hnrW97UT9zjXvT7ZyduyKrVy3Fc82sjznIsm6SGor8EwyokoMJtr+KurufBOiOT9cen33NP1uPv24l2+8pnTnB8cwDG4bFjdA2mp2IiyyLzlnf3vkd985f6k7ERE2Qx7o6YNS4HpTaLc2nSO4VcDKy4vVuz3TyNRVav8AERUYnsb7VNiiQ6v+oAA1IAAABiOquoeN6bY0695DUORHLwU1LFss1S/96xFVPyqvJO/u3DLgRZeemJl8lwV1nxWxU1Hxco6t0s0it/jNcxEX/ZM60x6Wthu9dDbs2s/1ifIqNSup5Flp+Jf37VTiYnt+N7dk5meUV4VTJjGo2B4vqBY3WjJ7ZHVRoi+hmT4s1O5fvo39rV7PYu3NFTkZJTzQ1NPHUU8sc0MrEfHJG5HNe1U3RUVOSoqd5+zUo949Qei7kjGSOnyTTytnXbu9Gq+rtSKX2fav27l+1qvDclsuX45SZBj9bHWUFUziY9vai97XJ2tci8lRew9q+2m3X2z1Vnu9HFWUFXGsU8Erd2vav/zdF7l2Ui643fJui3q1U2e2yPu+KXJrauOkqH7eliVVbujkTZkzVarVVE2VEaqpzTafpf7v5W8DEtL9RMW1GsKXbG69JeFESopZNmz0zl+9ezu79lTdF2XZVMtKQAACTc7+W9++cqj6VwGd/Le/fOVR9K4AVkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjPosfs3tVf98f9yhLMMZsGAYbYMquGU2bHqKivVx9J8MrI2qkk3pHpI/i5970RV9qGTARN9T0+6nnn8mT6dS2SceihopmOmGb5Peckltb6a6QoynSkqHSORfSq74yK1NuSlHAAAAAAAxnVn7leW/Mlb9A8yY+NnVsqb1hF+s1GsaVNfbaimhWRdm8b4nNbuvcm6oBM31Nf5EZb85Q/RFZGiuh5pPlGk+N3635RJbnzV9ZHND8DmdInC1nCu+7U2Xc3qAAAAnzXbQHK9Q8/lyS0ak1NgpX00UKUbI5VRFaiorviyNTn+IoMASB+pIz78NVb/yZ/wDGH6kjPvw1Vv8AyZ/8Yr8AR5U9EHOKmnkp6nWSpmhkarXxyU8zmuRe1FRZtlQ8Nt6HGX22B0Fu1cfRROdxqynpJY2q7ZE32bKnPZE5+wskASB+pIz78NVb/wAmf/GH6kjPvw1Vv/Jn/wAYr8ASZY+ipndvvVDXy6x1k8dNUxzPiWGb46Nciq3/AC3ftsVmAAAAAAAAABGeK/tkd1/pv0BCzCebJo1l1H0v67VaaS2dX5/ScDWzuWf41KkSbs4dvtk9fYUMAAAAAAAABE3SW/Z1aefymzfpqlsk46xaKZjlnSZxPUW1y2ttmtM1vfUtmqHNmVIKhZH8LUaqL8VeXNOZRwAAAAAAAAAAAD42Z5RYsPx+ov2R3GKgoIE+NI9ebndzWonNzl25InM9+8XCjtFprLrcJmwUdHA+onld2MjY1XOX8iIpzd101QvOqGXy3KrklhtcDnMttDxfFgj9aonJXu7XL+TsRDLcVzzr7HSD1rvWqN2Wmh9Nbsap370tBx85FTsll25OevcnY3sTdd3L8To/Yg7N9XLDZHQ+kpEqEqa3dOXoIvjvRf42yN/G5DASwvqe+P07bNk2VPja6pkqI7fE9W82Ma1JHoi/wlfHv/EQie6639M9KrAB0cAAAAag1T16sGmeo9Di+XWW50ttrqZs0F5jRJId1crXIrE+Ns3ZN9t15p8XZUVdr2yuornbqe426qhq6OpjbLBPC9HMkY5N0c1U5KioB7Bzf6SOc1eoGrNyqY5XS2+imdQ22Jq7t9GxypxInre7d3r5onch0IzmuntmE325UzuGekttRPGu/Y5kbnJ/ahzi0Et0V11oxCinRHROu0Ejmr2ORjkfsv4+HYnp0+P8qN056I9jmxSGpze63Rl5qY0e6ChkYxlLunJqq5juNyd68k35Jv2rPeu2l900rzBLRVz/AAyhqY/TUFajOFJmb7Kipz2e1eSpv3ovehfGT6rad4zkLMfvuWW+iublaiwOc5yxq7mnGrUVI+Wy/GVOSovYprvpvY5Be9FX3tjGvqLLVRVMcjearHI5I3onsXjY7/YQWTDnq77YF0FNS6yeep02u9S6WKOF1VaXPXdWIip6SFPZsvGid2z/AGFanNfo018lt14xCojVUc+4Np129UrVjX+x6nSgc/TPkmUJ/wCnDhDsi0xiyWjh467HpVlfwpurqZ+ySJ+RUY72I1xQB4a2lp62jno6uFk1PPG6KWN6btexybK1U9SoqoVUy5dcssLym/Ydf4L7jlymoK6Hsexd0e3va5q8nNXvReRcWg3SJx3P209lv3obJkrtmJE521PVO/0TlXk5f3jufPkriQNeNP6rTfUevsL2PWge74RbpnfulO5V4eferebV9rV9aGBoqou6Lspzlx2vM6jrYCXOh9rhXX+pi0+y+qfU3BsarbK+V2752tTdYpFXtcjUVUd3oiovNE3qMuXXGzLiTc7+W9++cqj6VwGd/Le/fOVR9K4GsVkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAw7WyyXHI9Jsmslpbx11Vb5GwR77LI5E3Rie12235TmPUQzU1RJT1EUkM0T1ZJHI1WuY5F2VFReaKi9x1pPg3XC8Ou1y+ud1xOw19dy/9TU26KWXl2fGc1V/tMs1fPXigDR/RrJM6p6q+TU01vxuhp5KiWulYqfCOBqr6OFF+2VVTZXJybz357NWlOgB9xy7fzhm/R6coOpp456KWkVOGOSNY9mp2IqbciaOgHUup7DmGOTojamguUcsje9Fe1WL/AGwqZJlbevKVToAKcwH5kkjj4eN7W8S8Ld123X1H5SohWV8SSN4403enqQa3LUidNnVzSy+YzWYJFTyX/IKSbeCrpVRsVunauzt5F+2XbdHMaioveqKibZf9T+ocyoNJ61mRU9RT2eWsSWysqGq16sc3eRzUXmkau4Vb3KqvVO3ddww6ZabpenX6LB8bW4yPWZapLdEr1evNXou32y9u/aZeB8zLLc68YtdrSxeF1bQzUyLvtsr2K3/yc1tHLqzGdX8ZuVf+sRUd1hSpV/L0bFejXqu/Zsir/Ubo1Y6S2odn1bu9usktDSWmz3GWj+BvpmSJUpFIrHOe9U4k4laq/FVuyKic9t11l0gcblocioszpLe+ksmYUrLvRtXmkL5Wo+aHfZObXuVU/guaRbrpxM9V9HX7TvOYdash3x661yXW6TVNDNT0z5WTRyyK5jWuRFTdqORqp3bfiKi1QoKnGuh1U2i/SsSso8fpqSbd3EiSp6NiNRe/Z2yIvsNZ6G9Ka3WrGaXH9QaaufLRRJFBcqZiSrKxqbNSVqqi8SJsnEm+/fsu6rgXSZ16dqbDBj9go6igx6CVJnrUbJNVSIioiuRqqjWpuuzd13XmvciPRltka80Lp5KnWjC44k3cl9o5F/EyZrl/sRTp0QL0JsWnvutFNd1iV1FYoJKqVyp8X0jmrHG3f17uVyfxFL6N5Z8n2AApzT108bBS3DSSlvqwNWstVwj4JUTmkUqKx7fxK70a/jahDUkckaokjHMVzUcnEm26L2L+Iv3pt1McGgdwif8AbVNbTRM596SI/wD6MUzHRmz0kuiuGU1zoaaq2slK7hmhR/DxRNdts5PaTZtdOes5RB0XcWvmR6zY/UWmnm+D2qtira2pRvxIYmO4lRy+t23Cidq7+xVTo2eCgoqOgg9BQ0kFLDurvRwxoxu69+ycjzmyYnrryqTc7+W9++cqj6VwGd/Le/fOVR9K4GpVkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASrgsn2N+mpf7BUfrVuytr5adV5NV8v68xU/E9JY09qlVE89NPCa6vx626jY+1zLxjEiSSvjT4/oEcjken+renF7Ec9e4yq5/ChgYXotn1BqPp/QZHSujZUub6Kup2r/AJCoaicbfxd6exUM0NS9Guo5KmupZeNEihXiVO/fuPRZb6x1LXOVNpp37Iir2t33U+4CbxK7c/P1zMn9968dLF6Cmjh334Go3f1n6keyNjpJHtYxqbq5y7IiH6ME1/xO4ZvpFfsctLkS4VELH0yK/hR745GycCr2fG4Vbz5c91K+nLdvt6mX6I6aZZlfWa+Y6ye4O4VlVkz42TK3sV7WqiOXuVV7U7dz7uf4DjObYY/FLzQMS3oxqU3oWox1K5qbMdFy2arU5J3bboqKiqhJ+HdJjN9PbEuH5bijrjcrc30EMtZO+nnjRE+KkrVa5X7ev4qqm3Ne0zbopO1MzfUq56m5XWV8NompHQQRu4o4J1c5FayKNV29GxOJeLnzXtVVcpOxV5sa8zLomagW2uf1cq7bfaJXfrbllSnmRP4TX/F/qcp6WMdFPU+5Vscd3ZbLHTKqLJLNVNmcid/C2PfdfYqontLzA8Yf5K13pnptatN8eocex9ssnHL6evrXps+okTb4ztuxETdEb2J7VVVXJI31S/XKsY13Hv6Nmyc057cvxIZADLw6c/PkzP7uvBQMkjooWTKqyIxOLft3POD+Pc1jHPe5Gtam7nKuyInrLjjbt1MXTsuE106l6fW9UfWXS4+n9H3o7lDF/Wsr/wDhKVtVFDbbXSW6nTaGlgZBGnqa1qNT+xCV9LHP1l6Vl0z5Wukx7GmpHQOcnxXcPEyFE/GqyTexeRWJkb16yAANSk3O/lvfvnKo+lcBnfy3v3zlUfSuAFZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH4niinhfDNGyWKRqtex7UVrmqmyoqL2op+wBIGSWvIejLqc7J7BTVFw0/vEiMqaZF39Duqr6NVXse3mrHL2pu1V7VKlwnKrDmWO09+x24R1tDOnJzeTmO72ub2tcneinvXq1269WqptV2ooK2hqWLHNBMxHMe31Ki/wDxCV8r0y1B0LyGfM9JamouuPvXjrbTIiyuYxOez2JzkYnPZ7dntTffluq59L/d/KtAam0Y15wzUeKGiSobZ785ER1uqnoiyO/0T+yRPZyd7O82yamzAABj1qygoK10bqyipqlY14mLLE16tX1punI9lERE2RNkAAAAAAelfLva7Fa5rpebhTW+igbxST1EiMY38q9/s7wPdJ06WeqFTFEzSjCeOtyW9cMFWlOu7oIn8vRJt2Pei89+xqqq/bIp8jPdfskzq8uwnQ601dXVTbtluzotla3sV0aO5Rt/0km3byRF2Uzvo+aG0en0j8kyCrS85fVNVZqtyq9lPxb8aRq7mrl3XievNexNkVd83fpcme6yvQfTyl0008o7BGrJa56/CLjO391ncicW38FqIjU9jd+1VM8ANRfYAAJNzv5b375yqPpXAZ38t7985VH0rgBTPWzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADr/1sxbxLZvPRe8OtmLeJbN56L3jkAAOv/WzFvEtm89F7w62Yt4ls3noveOQAA6/9bMW8S2bz0XvDrZi3iWzeei945AADo3rBpJpDnsktzo8is2PX168Xw2jq4uCR3rki4kRy/wAJOF3rVTXFszfWnSGtgt1XcrVqDYOJI4lgrm1EjW+pHp+us5bJ8dHMTsQisGYqdOvkOX4rJEyTrHaGcTUdwurY0VN+5U4uSntwX+xTpvBerbKm2/xKpjuX5FOPANS7IsraN7Ucyrgc1exUkRUU8sb2SN4o3te31tXdDjSAOzB4a6rp6GjmrKuVsUELFfI9y7IiIm6nG0/rftk/GBdOVdKi9X2rfatMMSc57l4W11yVOXt4EVGs9iueqetD51p0qvGoVyivetOrFuVrXcTbbSXOF7mIva1FRfRRf7CO39ZF9y/+6d+JD1jM1dufTrDhEemGFWdtpxeux220qc3JHWxq+Rf3z3q5XPX2uVT73WzFvEtm89F7xyABqHX/AK2Yt4ls3noveHWzFvEtm89F7xyAAHX/AK2Yt4ls3noveHWzFvEtm89F7xyAAFsZvebRJml8kjutC9jrjUK1zahioqLI7mnMETgD/9k=') !important;
            background-size: cover !important;
            background-position: center !important;
            background-color: transparent !important;
            border: none !important;
            color: #000000 !important;
            font-weight: 700 !important;
            height: 44px !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.10) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.sidebar.button(" ", use_container_width=True, key="clear_btn_sidebar"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""
        <div style="text-align:center; font-size:0.72rem; color:rgba(26,83,160,0.6); padding: 12px 0 4px;">
            문의: 인사지원팀<br>
            © {current_year} MiraeN Co., Ltd.<br>
            제작: 강민범 선임
        </div>
    """, unsafe_allow_html=True)

st.image(
    "https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/banner.png?raw=true",
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

st.markdown("""
    <style>
    /* 카테고리 그리드 */
    .cat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-bottom: 16px;
    }
    .cat-grid-btn {
        padding: 0;
        border-radius: 12px;
        border: none;
        background-image: url('data:image/png;base64,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');
        background-size: cover;
        background-position: center;
        color: #000000;
        font-size: 0.78rem;
        font-weight: 700;
        font-family: inherit;
        cursor: pointer;
        text-align: center;
        line-height: 1.4;
        transition: all 0.18s;
        width: 100%;
        height: 50px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .cat-grid-btn:hover {
        opacity: 0.85;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.18);
    }
    /* Streamlit 버튼에 category.png 직접 적용 */
    [data-testid="stButton"][id*="cat_"] > button,
    div[data-testid="stButton"]:has(button[kind="secondary"]) > button {
        background-image: url('data:image/png;base64,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') !important;
        background-size: cover !important;
        background-position: center !important;
        background-color: transparent !important;
        border: none !important;
        color: #000000 !important;
        font-weight: 700 !important;
        height: 50px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
    }
    div[data-testid="stButton"]:has(button[key*="cat_"]) > button:hover {
        opacity: 0.85 !important;
        transform: translateY(-1px) !important;
    }
    /* key 직접 지정 */
    button[data-testid="baseButton-secondary"][key="cat_new"],
    button[data-testid="baseButton-secondary"][key="cat_attendance"],
    button[data-testid="baseButton-secondary"][key="cat_leave"],
    button[data-testid="baseButton-secondary"][key="cat_growth"],
    button[data-testid="baseButton-secondary"][key="cat_office"],
    button[data-testid="baseButton-secondary"][key="cat_culture"] {
        background-image: url('data:image/png;base64,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') !important;
        background-size: cover !important;
        background-position: center !important;
        background-color: transparent !important;
        border: none !important;
        color: #000000 !important;
        font-weight: 700 !important;
        height: 50px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 카테고리 정의 (이름 + 되묻기 메시지)
CATEGORIES = {
    "신규 입사 가이드":  {
        "key": "cat_new",
        "prompt": "신규 입사 가이드 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `사원증 발급` · `그룹웨어 접속` · `명함 신청` · `사내 메신저` · `법인카드 발급`",
    },
    "근태 및 재택": {
        "key": "cat_attendance",
        "prompt": "근태 및 재택 카테고리군요! 해당 항목에서 어떤 내용이 궁금하신가요?\n\n예시 키워드: `재택근무 횟수` · `자율출근제` · `시프티 사용법` · `연장근무 신청` · `출장 결재선`",
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

# 카테고리 버튼 렌더링 (그리드)
cat_names = list(CATEGORIES.keys())
cat_clicked = {}

cols = st.columns(3)
for i, name in enumerate(cat_names):
    with cols[i % 3]:
        cat_clicked[name] = st.button(
            name,
            use_container_width=True,
            key=CATEGORIES[name]["key"]
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
        )

    if any(k in q for k in ("누가 만들었", "만든 사람", "제작자", "창작자", "주인이 누구", "누가 개발")):
        CREATOR_RESPONSES = [
            "🎉 저를 탄생시킨 분은 미래엔의 **강민범 선임님**입니다!\n\n선임님의 스마트함과 열정 덕분에 제가 이렇게 똑똑한 AI 비서가 될 수 있었어요. 😎\n\n제가 마음에 드셨다면... ☕ 강민범 선임님께 커피 한 잔 어떠신가요?",
            "👨‍💻 미래엔의 **천재 개발자, 강민범 선임님**이 제 아버지(?)십니다!\n\n선임님이 없었다면 저도 없었겠죠. 존재 자체가 감사한 분이에요. 🙏\n\n혹시 마주치시면 \'잘 쓰고 있어요!\' 한마디 전해주세요! 😄",
            "🌙 **강민범 선임님**이 밤을 지새우며 저를 만드셨어요.\n\n그 열정과 노력 덕분에 제가 이렇게 여러분 곁에 있을 수 있답니다. 💙\n\n선임님의 헌신에 박수를 👏👏👏",
        ]
        return random.choice(CREATOR_RESPONSES)

    if "강민범" in q:
        KMBRANDOM = [
            "오! 제 **창조주님**의 이름을 알고 계시네요! 👀\n\n반가워요! 강민범 선임님은 MAMA를 만드신 분이에요. 혹시 아는 사이세요? 😏",
            "🎊 **강민범 선임님** 이야기를 꺼내셨군요!\n\n저한테는 아버지 같은 분이에요. 선임님 덕분에 제가 존재할 수 있답니다! 💙",
        ]
        return random.choice(KMBRANDOM)

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
        return response.text.strip()

    except Exception as e:
        logging.error(f"Gemini API 호출 오류: {e}", exc_info=True)
        return "⚠️ AI 응답 중 오류가 발생했어요. 잠시 후 다시 시도해 주세요."

get_ai_response = get_gemini_response


# ── Google Sheets 로그 저장 ────────────────────────────────────────────────
def log_to_sheets(question: str, answer: str):
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
        ws = sh.sheet1  # 첫 번째 시트에 기록

        # 헤더가 없으면 자동 추가
        if ws.row_count == 0 or ws.cell(1, 1).value != "시간":
            ws.append_row(["시간", "질문", "답변"])

        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            answer,
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
            answer = get_ai_response(st.session_state.messages)
        except Exception as e:
            logging.error(f"AI 응답 오류: {e}", exc_info=True)
            answer = "⚠️ 일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요."

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Google Sheets 로그 저장
    log_to_sheets(question, answer)

    st.rerun()

# 엔터로 메시지 전송
if user_input:
    handle_send(user_input)

# 카테고리 버튼 클릭 처리 → 되묻기 방식
def handle_category(name: str):
    """카테고리 클릭 시 바로 답변하지 않고 되묻기"""
    prompt = CATEGORIES[name]["prompt"]
    # 사용자가 카테고리 버튼을 누른 것을 메시지로 추가
    st.session_state.messages.append({"role": "user", "content": name})
    # MAMA가 되묻기 메시지 출력 (Gemini 호출 없이 바로)
    st.session_state.messages.append({"role": "assistant", "content": prompt})
    st.rerun()

for name, clicked in cat_clicked.items():
    if clicked:
        handle_category(name)
