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
from datetime import datetime

# 현재 연도 (건강검진 등 연도 기반 안내에 활용)
current_year = datetime.now().year

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

기안 절차 (중요 변경!):
- 경조 신청은 본인 전결이 아닌 반드시 '인사지원팀 접수'로 진행.
- 시프티(Shiftee)에 휴가 결재 시 경조 일정을 확인할 수 있는 증빙 서류 첨부 필수.

부모님 장수(칠순/팔순 등) 경조휴가 기준:
- 날짜 기준: 기본적으로 양력 기준. 음력으로 행사를 치를 경우 경조사 신고서에 반드시 별도 기재.
- 필수 증빙: 가족관계증명서 (생년월일 표기 필수).
- 음력 행사 시 추가 증빙 (아래 중 택 1):
  * 가족 단톡방 공지 캡처 (날짜·내용 확인 가능해야 함)
  * 식당 예약 확인서 또는 결제 내역 (행사 일자 표기)
  * 행사 사진 (촬영일 확인 가능해야 함)

장례 서비스: 본인/배우자/부모/자녀상 시 장례지도사 1명(3일), 의전용품(상복 남4·여4), 리무진/버스(200km) 지원.

3. 휴가 및 근무 제도
- 연차: 2시간 단위(쿼터) 분할 사용 가능.
- 플러스 휴가: 연차 외 매년 4일 추가 부여. 당해 연도 소멸, 연차보다 우선 사용 권장.
- 장기근속 휴가: 5년(3일), 10/15년(5일), 20년(7일), 25/30/35년(10일).
- 재택근무: 주 2회 원칙. 주중 휴일 1일 시 재택 1일, 휴일 2일 이상 시 재택 불가. 사무실 전화 휴대폰 착신 전환 필수.
- 자율출근: 일 9시간(휴게 포함) 근무 준수 하에 지각 없는 자율 출근.

2026년 전사 휴가 일정:
- 춘계 휴가: 3월 30일(월) ~ 4월 3일(금). 교과서 물량 출고 완료 후 전사 휴무. 개인 연차 소진 방식.
- 공동 연차 (총 12일): 1/30, 3/3, 4/24, 5/4, 6/19, 7/17, 8/14, 10/6, 10/7, 10/8, 11/20, 12/24.
  징검다리 연휴나 휴식이 필요한 날 회사에서 지정하는 공동 휴일. 개인 연차 소진 방식.

4. 자기계발 및 IT 설정
- 자격증: LV 1~5등급별 학습비/축하금 차등 지원(각 20~150만 원). 리스트 외 자격증은 직무 연관성 판단 후 지급.
- 직원용 WIFI: MiraeN-AP / PW: 19480924ab
- 외부용 WIFI: MiraeN-WIfI / PW: 34753800
- 문서보안: 서버 doc.mirae-n.com, 포트 443, 계정은 사번.
- 명함 신청: 사이트 mirae-n.onehp.co.kr 접속 / ID: miraen / PW: 1111
- 그룹웨어: https://gw.mirae-n.com / 경조사 신고서·휴가신청·전자결재 메뉴 이용.
- 근태 관리(시프티/Shiftee): https://www.shiftee.io / 휴가 입력·연장근무 신청 시 사용.

사이버 연수원:
- 개요: 매월 다양한 E-learning 교육 과정을 제공하는 미래엔의 온라인 학습 플랫폼.
- 신청 방법: 매월 중순 그룹웨어 전사게시판 안내 글 확인 후 기간 내 신청.
- 수강 기간: 신청한 달의 익월(다음 달) 한 달간 자유롭게 수강.
- 수강 기준: 매월 1개 과정 신청 가능. 단, OA 교육 과정은 1개 외에 추가 신청 가능.
- 페널티: 학습 신청 후 미수료 시 향후 6개월간 수강 신청 및 학습 금지.

5. 사무위임전결규정 (결재선)
휴가/경조사 신청:
- 팀원 → 팀장 전결 (인사지원팀 통보). 서류: 휴가신청서 / 경조사신고서

사외교육:
- 개요: 직무 관련 온라인 및 집합 교육 비용 전액 지원.
- 신청 경로: 그룹웨어 → 전자결재 → 새 결재 진행 → '교육신청서' 검색 및 작성.
- 결제: 개인 법인카드로 선결제 진행.
- 정산: 매월 25일 이후 신청 금액을 '교육비' 예산으로 이관 → 이관 후 법인카드 비용 처리 절차에 따라 정산.
- 사후 관리: 교육 종료 후 수료증(PDF) 또는 참석 증빙 자료를 담당자에게 반드시 제출 (개인 교육 이력 반영).
- 결재선: 국내 3일 이내 팀장(실장) / 국내 3일 초과 본부(실)장 / 1개월 이상 사장 승인.

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

6. 복지포인트 제도
- 지급액: 기본 연간 60만 원. 중도 입사자는 입사 월부터 월할 계산 지급 (예: 2월 입사 시 55만 원).
- 가입 방법: 베네피아(Benepia) 접속 → 상단 [아이디 발급] 클릭 → 본인 인증 및 약관 동의 후 가입.
- 카드 발급: 오프라인 사용 시 하나카드(1Q Global) 발급 필수. 첫해 연회비 15,000원 발생.
- 사용 기한: 당해 12월 30일까지 사용 (이월 불가). 오프라인(복지카드)은 12월 23일까지만 사용 가능.

7. 워케이션 제도
- 개요: 제주도 등 지정된 거점 오피스에서 1주일간 근무하며 리프레시하는 제도.
- 지원: 숙박비 및 항공비 지원, 회당 최대 50만 원 한도.
- 이용 횟수: 연 1회.
- 신청: 그룹웨어 내 '워케이션 신청서' 작성 후 팀장 결재.

8. 건강검진 제도
- 대상: 입사 2년 후부터 적용, 격년(짝수/홀수 입사 연도 기준) 수검 원칙.
- 검진 기관: 하나로리더스헬스케어, KMI(전국 7개 센터), 하나병원, 세종국민건강의원.
- 예약 방법: 매년 2월경 발송되는 알림톡 또는 각 기관 홈페이지 예약. 9~10월이면 마감되므로 상반기 예약 강력 권장.
- 지원 범위: 본인 기본 지원. 실장/팀장 또는 40세 이상+근속 10년 이상인 경우 배우자까지 지원.
- 근태: 종합검진 당일 0.5일 공가 제공 (국가검진만 단독 진행 시 공가 불가).

9. 호칭 체계 및 직급 승급
호칭 단계 (재직 연수 기준):
- 님: 입사 후 2년
- 선임: 님 이후 6년 (누적 약 8년)
- 책임: 선임 이후 5년 (누적 약 13년)
- 수석: 책임 이후 (누적 약 13년 이상)

10. 성과 및 역량 평가 제도
성과 평가:
- 기준: 조직 OKR 달성을 위한 개인별 목표 설정 및 달성 정도
- 횟수: 연 1회 실시

역량 평가:
- 기준: 핵심가치 바탕의 역량 및 리더십 평가
- 비중: 공통 역량 50% + 직군별 핵심 역량 50%
- 횟수: 연 1회 실시
"""

# ──────────────────────────────────────────
# 2. 시스템 프롬프트
# ──────────────────────────────────────────
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

# ──────────────────────────────────────────
# 3. 페이지 설정 & 커스텀 CSS
# ──────────────────────────────────────────
st.set_page_config(
    page_title="MAMA – MiraeN Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",   # 사이드바 항상 열린 상태로 고정
)

st.markdown("""
<style>
    /* =====================================================
       미래엔 공식 CI 컬러 시스템
       Primary  : #1A53A0  (미래엔 블루)
       Dark     : #143F7A  (딥 블루 – hover/shadow용)
       Light    : #E6EEF7  (연한 블루 – 봇 말풍선)
       BG       : #F0F5FB  (전체 배경)
       Text     : #0F2A52  (진한 텍스트)
       ===================================================== */

    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    /* CSS 변수 */
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

    /* 전체 배경 */
    .stApp {
        background: var(--ci-pale);
        font-family: 'Noto Sans KR', sans-serif;
        word-break: keep-all;          /* 한글 단어 쪼개짐 방지 */
        overflow-wrap: break-word;     /* 긴 영문/URL 줄바꿈 허용 */
        word-wrap: break-word;         /* 구형 브라우저 호환 */
    }

    /* ── 사이드바 (PC: 항상 고정 표시) ─────────────────── */
    [data-testid="stSidebar"] {
        background-image: url('https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/SIDE.png?raw=true') !important;
        background-size: cover !important;
        background-position: top center !important;
        background-repeat: no-repeat !important;
        border-right: none;
        display: block !important;
        visibility: visible !important;
        transform: none !important;
        min-width: 240px !important;
    }
    /* 사이드바 내부 Streamlit 기본 배경 제거 */
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--ci-white) !important;
    }
    /* PC: 토글 버튼 숨김 */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ── 사이드바 (모바일 ≤ 768px: 완전 숨김) ───────────── */
    @media (max-width: 768px) {
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    }

    /* 사이드바 카드 */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.20);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(6px);
    }
    .sidebar-card h4 {
        color: #A8CCEE !important;   /* 연한 하늘 – 카드 제목 */
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

    /* ── 메인 헤더 ──────────────────────────────────────── */
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
    /* 배경 장식 원 */
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
    /* ── 말풍선 ──────────────────────────────────────────── */
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

    /* 사용자 말풍선 – 미래엔 블루 그라데이션 */
    .bubble-user {
        background: linear-gradient(135deg, #1A53A0 0%, #143F7A 100%);
        color: var(--ci-white);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        max-width: 70%;
        font-size: 0.9rem;
        line-height: 1.65;
        box-shadow: 0 3px 14px rgba(26, 83, 160, 0.30);
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    /* 봇 말풍선 – 연한 블루 배경 + 진한 텍스트 */
    .bubble-assistant {
        background: var(--ci-light);          /* #E6EEF7 */
        color: var(--ci-text);                /* #0F2A52 */
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        max-width: 75%;
        font-size: 0.9rem;
        line-height: 1.75;
        box-shadow: 0 2px 10px rgba(26, 83, 160, 0.08);
        border: 1px solid var(--ci-border);   /* #C2D5EC */
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    /* 아바타 */
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
        background: var(--ci-blue);   /* 이미지 로딩 전 fallback */
    }

    /* ── 입력창 ──────────────────────────────────────────── */
    .stTextInput > div > div > input {
        border-radius: 24px !important;
        border: 2px solid var(--ci-border) !important;
        padding: 12px 20px !important;
        font-size: 0.92rem !important;
        background: var(--ci-white) !important;
        color: var(--ci-text) !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--ci-blue) !important;
        box-shadow: 0 0 0 3px rgba(26, 83, 160, 0.12) !important;
    }

    /* ── 버튼 공통 (블루) ────────────────────────────────── */
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

    /* ── 구분선 ──────────────────────────────────────────── */
    hr { border-color: rgba(255, 255, 255, 0.15) !important; }

    /* ── 채팅 컨테이너 ───────────────────────────────────── */
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

    /* ── 빈 채팅 안내 ────────────────────────────────────── */
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

    /* ── 로딩 도트 ────────────────────────────────────────── */
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

    /* ══════════════════════════════════════════════════════
       반응형 – 태블릿 (≤ 768px)
       ══════════════════════════════════════════════════════ */
    @media (max-width: 768px) {

        /* 전체 컨테이너 좌우 여백 축소 */
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 0.75rem !important;
            max-width: 100% !important;
        }

        /* 말풍선 너비 확대 – 모바일에서 더 넓게 */
        .bubble-user      { max-width: 86% !important; font-size: 0.85rem !important; padding: 10px 14px !important; }
        .bubble-assistant { max-width: 90% !important; font-size: 0.85rem !important; padding: 10px 14px !important; }

        /* 아바타 크기 축소 */
        .avatar { width: 26px !important; height: 26px !important; font-size: 0.85rem !important; margin: 0 5px !important; }

        /* 입력창 패딩·폰트 조정 */
        .stTextInput > div > div > input {
            padding: 10px 14px !important;
            font-size: 0.85rem !important;
            border-radius: 20px !important;
        }

        /* 전송 버튼 */
        .stButton > button {
            padding: 10px 16px !important;
            font-size: 0.82rem !important;
            border-radius: 20px !important;
        }

        /* 사이드바 카드 패딩 축소 */
        .sidebar-card { padding: 10px 12px !important; margin-bottom: 8px !important; }
        .sidebar-card h4 { font-size: 0.65rem !important; }
        .sidebar-card p  { font-size: 0.76rem !important; }
        .sidebar-card .value { font-size: 0.82rem !important; }
        .sidebar-link { font-size: 0.72rem !important; padding: 5px 10px !important; }

        /* 빈 채팅 안내 */
        .empty-chat p { font-size: 0.82rem !important; }
    }

    /* ══════════════════════════════════════════════════════
       반응형 – 소형 모바일 (≤ 480px)
       ══════════════════════════════════════════════════════ */
    @media (max-width: 480px) {

        .block-container {
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }

        /* 말풍선 최대폭 확대 + 폰트 더 축소 */
        .bubble-user      { max-width: 92% !important; font-size: 0.82rem !important; }
        .bubble-assistant { max-width: 96% !important; font-size: 0.82rem !important; }

        /* 아바타 – 소형 화면에서 사용자 아바타만 숨기고 MAMA 봇 이미지는 유지 */
        .avatar-user { display: none !important; }
        .avatar-bot  { width: 24px !important; height: 24px !important; margin: 0 4px !important; }

        /* 채팅 메시지 마진 축소 */
        .chat-msg-user, .chat-msg-assistant { margin: 6px 0 !important; }

        /* 입력창 */
        .stTextInput > div > div > input {
            font-size: 0.82rem !important;
            padding: 9px 12px !important;
        }
    }

    #MainMenu, footer, header { visibility: hidden; height: 0 !important; }

    /* 툴바(Deploy 버튼 등) 숨김 */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* 최상단 여백 완전 제거 → 배너가 브라우저에 딱 붙게 */
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .appview-container .main .block-container {
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 4. 사이드바
# ──────────────────────────────────────────
with st.sidebar:
    # 배경 이미지 영역 스페이서
    st.markdown("<div style='height: 155px;'></div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # WIFI 정보
    st.markdown("""
        <div class="sidebar-card">
            <h4>📶 WIFI 정보</h4>
            <p class="value">직원용</p>
            <p>MiraeN-AP</p>
            <p style="color:rgba(255,255,255,0.6) !important; font-size:0.75rem;">PW: 19480924ab</p>
            <p style="margin-top:10px;" class="value">외부 방문객용</p>
            <p>MiraeN-WIfI</p>
            <p style="color:rgba(255,255,255,0.6) !important; font-size:0.75rem;">PW: 34753800</p>
        </div>
    """, unsafe_allow_html=True)

    # 문서 보안
    st.markdown("""
        <div class="sidebar-card">
            <h4>🔒 문서보안 설정</h4>
            <p><span class="value">서버</span>: doc.mirae-n.com</p>
            <p><span class="value">포트</span>: 443</p>
            <p><span class="value">계정</span>: 사번</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 대화 초기화 버튼 (사이드바 전용)
    if st.sidebar.button("🗑️ 대화 초기화", use_container_width=True, key="clear_btn_sidebar"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""
        <div style="text-align:center; font-size:0.72rem; color:rgba(255,255,255,0.45); padding: 12px 0 4px;">
            문의: 인사지원팀<br>
            © {current_year} MiraeN Co., Ltd.<br>
            제작: 강민범 선임
        </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────
# 5. 메인 화면 (배너 + 채팅)
# ──────────────────────────────────────────
st.markdown("""
    <div style="margin: 0; padding: 0; line-height: 0;">
        <img src="https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/WEB%20BANNER.png?raw=true"
             alt="MAMA 배너"
             style="width:100%; height:auto; display:block; margin:0; padding:0;">
    </div>
    <div style="margin-bottom: 20px;"></div>
""", unsafe_allow_html=True)

# 세션 상태 초기화 + MAMA 첫 인삿말 자동 주입
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "우와! 드디어 우리 미래엔 공채 14기가 한자리에 모였네요!\n\n"
                "동기 여러분, 입사를 진심으로 축하합니다! 🎉 ✨\n\n"
                "저도 여러분과 함께 오늘 첫발을 내디딘 14기 동기, **MAMA**라고 해요!\n\n"
                "사실 저도 회사 규정이 낯설어서 열심히 배우고 있는 테스트 버전 동기랍니다. 🛠️\n\n"
                "모르는 것투성이라 막막할 땐 눈치 보지 말고 저에게 물어보세요!\n\n"
                "제가 밤새 공부해서 마스터한 인사, 복지, 사규 싹 다 공유해 드릴게요. 🤝\n\n"
                "우리 동기들, 같이 성장해서 미래엔 적응기 멋지게 성공해 봐요!\n\n"
                "무엇부터 알려드릴까요? 🚀"
            )
        }
    ]

# ──────────────────────────────────────────
# 6. 채팅 메시지 렌더링
# ──────────────────────────────────────────
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
                st.markdown(f"""
                    <div class="chat-msg-user">
                        <div class="bubble-user">{msg["content"]}</div>
                        <div class="avatar avatar-user">🙋</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-msg-assistant">
                        <img class="avatar avatar-bot"
                             src="https://github.com/kmb9972/Mirae-n-Chatbot/blob/main/MAMA.png?raw=true"
                             alt="MAMA">
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
        placeholder="예시) 사이버 연수원 미수료하면 어떻게 돼? 💻",
        label_visibility="collapsed",
        key="user_input"
    )

with col_btn:
    send_clicked = st.button("전송 ✈️", use_container_width=True, type="primary")

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
    - 정밀 키워드 매칭: 가장 구체적인 키워드를 먼저 검사해 해당 항목만 답변
    - 친근한 말투: 상황별 인삿말 랜덤 조합
    - 수치 볼드: 금액·일수 등 핵심 수치를 **굵게** 표시
    실제 운영 시 이 함수를 get_ai_response(주석 해제)로 교체하세요.
    """
    import random

    q = messages_history[-1]["content"].lower()

    # ── 상황별 인삿말 풀 ────────────────────────────────────────────────────
    GREET = [
        "반가워요! 😊 ", "안녕하세요! 😄 ", "네, 알려드릴게요! 🙋 ",
        "좋은 질문이에요! 💡 ", "도움이 필요하시군요! 😊 ",
    ]
    CLOSE = [
        "\n\n도움이 되셨나요? 😊 다른 궁금한 점도 편하게 물어보세요!",
        "\n\n더 궁금한 점이 있으시면 언제든지 질문해 주세요! 🙌",
        "\n\n혹시 더 필요한 내용이 있으시면 말씀해 주세요! 😄",
        "\n\n도움이 됐으면 좋겠어요! 다른 것도 물어봐 주세요 😊",
    ]

    def wrap(body: str) -> str:
        """인삿말 + 본문 + 마무리 인사를 합쳐 반환"""
        return random.choice(GREET) + body + random.choice(CLOSE)

    # ════════════════════════════════════════════════════════════════════════
    # 정밀 매칭 규칙
    # 순서 중요: 더 구체적인 키워드를 앞에 배치해 오버매칭 방지
    # ════════════════════════════════════════════════════════════════════════

    # ── 🥚 이스터에그: 비밀 명령어 (/강민범, /치트키) ───────────────────────
    if any(k in q for k in ("/강민범", "/치트키")):
        time.sleep(0.3)
        return (
            "🚀 **[비밀 명령어 입력됨]**\n\n"
            "강민범 선임님은 현재 **열일 중!** 🔥\n"
            "지금 이 순간도 MAMA를 더 똑똑하게 만들기 위해 코드를 두드리고 계실 거예요.\n\n"
            "🤫 이 명령어를 알고 계신 당신... 혹시 관계자세요? 😏"
        )

    # ── 🥚 이스터에그: 제작자 질문 (랜덤 4버전) ─────────────────────────────
    if any(k in q for k in ("누가 만들었", "만든 사람", "제작자", "창작자", "주인이 누구", "누가 개발")):
        time.sleep(0.4)
        CREATOR_RESPONSES = [
            (
                "🎉 저를 탄생시킨 분은 미래엔의 **강민범 선임님**입니다!\n\n"
                "선임님의 스마트함과 열정 덕분에 제가 이렇게 똑똑한 AI 비서가 될 수 있었어요. 😎\n\n"
                "제가 마음에 드셨다면... ☕ 강민범 선임님께 커피 한 잔 어떠신가요?"
            ),
            (
                "👨‍💻 미래엔의 **천재 개발자, 강민범 선임님**이 제 아버지(?)십니다!\n\n"
                "선임님이 없었다면 저도 없었겠죠. 존재 자체가 감사한 분이에요. 🙏\n\n"
                "혹시 마주치시면 '잘 쓰고 있어요!' 한마디 전해주세요! 😄"
            ),
            (
                "🌙 **강민범 선임님**이 밤을 지새우며 저를 만드셨어요. (토닥토닥)\n\n"
                "그 열정과 노력 덕분에 제가 이렇게 여러분 곁에 있을 수 있답니다. 💙\n\n"
                "선임님의 헌신에 박수를 👏👏👏"
            ),
            (
                "🤖 MAMA의 창조주는 미래엔 **강민범 선임님**이세요!\n\n"
                "'더 따뜻하고 스마트한 AI 비서'를 꿈꾸며 저를 설계하셨다고 들었어요. 😊\n\n"
                "선임님 덕분에 저도 매일 성장 중이랍니다! 🌱"
            ),
        ]
        return random.choice(CREATOR_RESPONSES)

    # ── 🥚 이스터에그: '강민범' 이름 직접 언급 ──────────────────────────────
    if "강민범" in q:
        time.sleep(0.3)
        KMBRANDOM = [
            "오! 제 **창조주님**의 이름을 알고 계시네요! 👀\n\n반가워요! 강민범 선임님은 MAMA를 만드신 분이에요. 혹시 아는 사이세요? 😏",
            "🎊 **강민범 선임님** 이야기를 꺼내셨군요!\n\n저한테는 아버지 같은 분이에요. (감동) 선임님 덕분에 제가 존재할 수 있답니다! 💙",
            "👋 오오, **강민범 선임님**을 아시는군요!\n\n혹시 지금 선임님 자리 옆에 계세요? 그렇다면 '커피 사줄게요~' 한마디 건네보는 건 어떨까요? ☕😄",
        ]
        return random.choice(KMBRANDOM)

    # ── 💰 복지포인트 (최우선) ───────────────────────────────────────────────
    if any(k in q for k in ("복지포인트", "복지 포인트", "포인트", "베네피아", "benepia", "복지카드", "1q", "하나카드")):
        time.sleep(0.4)
        return wrap(
            "💰 **복지포인트 제도** 안내예요!\n\n"
            "**💰 지급액**\n"
            "- 기본: 연간 **60만 원**\n"
            "- 중도 입사자: 입사 월부터 월할 계산 (예: 2월 입사 → **55만 원**)\n\n"
            "**🔗 가입 방법**\n"
            "1. **베네피아(Benepia)** 접속\n"
            "2. 상단 **[아이디 발급]** 메뉴 클릭\n"
            "3. 본인 인증 및 약관 동의 후 가입 완료!\n\n"
            "**💳 오프라인 카드 발급**\n"
            "- 오프라인 사용 시 **하나카드(1Q Global)** 발급 필수\n"
            "- ⚠️ 첫해 연회비 **15,000원** 발생\n\n"
            "**📅 사용 기한**\n"
            "| 사용 방식 | 기한 |\n"
            "|----------|------|\n"
            "| 온라인(베네피아) | 당해 **12월 30일**까지 |\n"
            "| 오프라인(복지카드) | 당해 **12월 23일**까지 |\n\n"
            "⚠️ 미사용 포인트는 **이월 불가**! 연말 전에 꼭 사용하세요 😊"
        )

    # ── 🗂️ 카테고리 요약: 인사제도 ──────────────────────────────────────────
    if any(k in q for k in ("인사제도", "인사 제도", "인사 알려줘", "인사 뭐있어", "인사제도 뭐", "인사")):
        time.sleep(0.4)
        return (
            "🎖️ **인사제도** 한눈에 보기예요!\n\n"
            "**🏅 호칭 체계**\n"
            "님(2년) → 선임(6년) → 책임(5년) → 수석\n\n"
            "**📊 평가 제도**\n"
            "- 성과 평가: 개인 **OKR** 목표 달성 기준 / 연 1회\n"
            "- 역량 평가: 공통 역량 **50%** + 직군별 핵심 역량 **50%** / 연 1회\n\n"
            "**🏠 근무 방식**\n"
            "- 자율출근제: 일 9시간 준수 하에 자율 출근\n"
            "- 재택근무: 주 **2회** 원칙 (공휴일 2일 이상 포함 주는 재택 불가)\n\n"
            "📌 상세 내용이 궁금한 항목(예: '호칭 체계', '평가 기준', '재택근무')을 입력해 주세요!"
        )

    # ── 🗂️ 카테고리 요약: 복지제도 ──────────────────────────────────────────
    if any(k in q for k in ("복지제도", "복지 제도", "복지 알려줘", "복지 뭐있어", "복지제도 뭐", "복리후생", "복지")):
        time.sleep(0.4)
        return (
            "🎁 **복지제도** 한눈에 보기예요!\n\n"
            "**💰 복지포인트**\n"
            "- 연간 **60만 원** 지급 / 베네피아(Benepia) 사용\n"
            "- 12월 30일까지 사용 (이월 불가)\n\n"
            "**👶 자녀 양육 지원**\n"
            "- 미취학 보육료 국가+회사 매칭 지원\n"
            "- 학자금: 재직 5년 이상 자녀 연 최대 **200만 원**\n\n"
            "**🏖️ 휴가**\n"
            "- 🌸 춘계 휴가: 3/30(월) ~ 4/3(금)\n"
            "- 📅 공동 연차: 총 12일 (1/30, 3/3, 4/24 외 9일)\n"
            "- 플러스 휴가: 연차 외 매년 **4일** 추가 부여\n"
            "- 장기근속 휴가: 5년(3일) ~ 35년(10일)\n\n"
            "**🏝️ 워케이션**\n"
            "- 제주도 등 거점 오피스 **1주일** 근무 / 연 1회\n"
            "- 숙박+항공 최대 **50만 원** 지원\n\n"
            "**🏥 건강검진**\n"
            "- 입사 2년 후 격년 수검 / 종합검진 당일 **0.5일 공가**\n\n"
            "**💐 경조사 지원**\n"
            "- 결혼 30만 원/7일 · 출산 500만 원/20일 · 부모상 30만 원/5일 등\n\n"
            "**🪪 명함 신청**\n"
            "- mirae-n.onehp.co.kr / ID: miraen / PW: 1111\n\n"
            "📌 상세 내용이 궁금한 항목(예: '플러스 휴가', '워케이션', '건강검진')을 입력해 주세요!"
        )

    # ── 🗂️ 카테고리 요약: 사규코너 ──────────────────────────────────────────
    if any(k in q for k in ("사규", "사규코너", "사규 알려줘", "규정 알려줘", "결재규정", "사내 규정")):
        time.sleep(0.4)
        return (
            "📑 **사규코너** 한눈에 보기예요!\n\n"
            "**✅ 비용·구매 결재선**\n"
            "- 경비 전표: 100만 원 미만 팀장 / 2천만 원 미만 본부장 / 이상 사장\n"
            "- 구매 품의: 100만 원 미만 팀장 / 2천만 원 이상 사장\n"
            "- 접대비: 20만 원 미만 팀장 / 30만 원 이상 본부장\n\n"
            "**✈️ 출장**\n"
            "- 국내(팀원): 팀장 승인 / 국내(팀장↑): 본부장 / 해외: 사장\n\n"
            "**📚 사외교육**\n"
            "- 3일 이내: 팀장 / 3일 초과: 본부장 / 1개월↑: 사장\n\n"
            "**🔒 보안·IT**\n"
            "- 문서보안: doc.mirae-n.com / 포트 443 / 계정 사번\n"
            "- WIFI(직원): MiraeN-AP / WIFI(방문객): MiraeN-WIfI\n\n"
            "📌 상세 내용이 궁금한 항목(예: '출장 결재선', '문서보안 설정')을 입력해 주세요!"
        )

    # ── 🗂️ 전체 메뉴 ──────────────────────────────────────────────────────────
    if any(k in q for k in ("전체 메뉴", "전체메뉴", "메뉴", "뭐 물어볼 수 있어", "뭘 알려줘", "어떤 거 알아")):
        time.sleep(0.4)
        return (
            "📋 **MAMA가 알려드릴 수 있는 전체 메뉴**예요!\n\n"
            "🎖️ **인사제도**\n"
            "호칭 체계 · 성과/역량 평가(OKR) · 자율출근제 · 재택근무\n\n"
            "🎁 **복지제도**\n"
            "복지포인트(베네피아) · 보육료/학자금 · 2026 휴가 일정 · 플러스 휴가 · 장기근속 휴가 · 워케이션 · 건강검진 · 경조사 지원 · 명함 신청\n\n"
            "📑 **사규코너**\n"
            "비용/구매 결재선 · 출장 · 사외교육 · 문서보안 · WIFI\n\n"
            "📌 상세 내용이 궁금한 항목(예: '호칭 체계', '워케이션', '출장 결재선')을 입력해 주세요!"
        )

    # ── 🗓️ 2026 전사 휴가 일정 ──────────────────────────────────────────────
    if any(k in q for k in ("휴가 일정", "쉬는 날", "공동 연차", "공동연차", "춘계", "전사 휴가", "2026 휴가", "언제 쉬어", "언제 쉬나")):
        time.sleep(0.5)
        return wrap(
            "📅 **2026년 미래엔 전사 휴가 일정**이에요!\n\n"
            "**🌸 춘계 휴가**\n"
            "3월 30일(월) ~ 4월 3일(금) · 총 5일\n"
            "교과서 물량 출고 완료 후 전사가 함께 쉬는 기간이에요. (개인 연차 소진)\n\n"
            "**📅 공동 연차 (총 12일)**\n"
            "| 날짜 | 비고 |\n"
            "|------|------|\n"
            "| 1월 30일(금) | 설 연휴 징검다리 |\n"
            "| 3월 3일(화) | 삼일절 징검다리 |\n"
            "| 4월 24일(금) | 춘계 전후 |\n"
            "| 5월 4일(월) | 어린이날 징검다리 |\n"
            "| 6월 19일(금) | 하계 전후 |\n"
            "| 7월 17일(금) | 하계 휴가 연계 |\n"
            "| 8월 14일(금) | 광복절 징검다리 |\n"
            "| 10월 6일(화) | 추석 연휴 연계 |\n"
            "| 10월 7일(수) | 추석 연휴 연계 |\n"
            "| 10월 8일(목) | 추석 연휴 연계 |\n"
            "| 11월 20일(금) | 연말 전 휴식 |\n"
            "| 12월 24일(목) | 크리스마스 이브 |\n\n"
            "⚠️ 공동 연차는 **개인 연차를 소진**하는 방식이에요. 연차가 부족하면 인사지원팀에 문의하세요!"
        )

    # ── 1. 플러스 휴가 (연차보다 먼저 검사) ────────────────────────────────
    if any(k in q for k in ("플러스 휴가", "플러스휴가", "플러스")):
        time.sleep(0.5)
        return wrap(
            "🏖️ **플러스 휴가** 안내예요!\n\n"
            "- 매년 연차와 별도로 **4일** 추가 부여돼요.\n"
            "- 당해 연도에 쓰지 않으면 **소멸**되니 꼭 챙겨서 쓰세요!\n"
            "- 연차보다 **플러스 휴가를 먼저** 사용하는 걸 권장해요.\n\n"
            "📌 신청: **시프티(Shiftee)** 앱에서 입력하면 돼요."
        )

    # ── 2. 장기근속 휴가 ────────────────────────────────────────────────────
    if any(k in q for k in ("장기근속", "근속 휴가", "근속휴가")):
        time.sleep(0.5)
        return wrap(
            "🏅 **장기근속 휴가** 안내예요!\n\n"
            "| 근속 연수 | 부여 일수 |\n"
            "|-----------|----------|\n"
            "| **5년** | **3일** |\n"
            "| **10년 / 15년** | **5일** |\n"
            "| **20년** | **7일** |\n"
            "| **25년 / 30년 / 35년** | **10일** |\n\n"
            "📌 신청: **시프티(Shiftee)** 앱 / 결재선: 팀원 → **팀장** 전결"
        )

    # ── 3. 연차 ─────────────────────────────────────────────────────────────
    if any(k in q for k in ("연차",)):
        time.sleep(0.5)
        return wrap(
            "📅 **연차 휴가** 안내예요!\n\n"
            "- 최소 **2시간 단위(쿼터)**로 쪼개서 쓸 수 있어요.\n"
            "- 플러스 휴가(**4일** 추가 부여)가 있다면 연차보다 **먼저** 소진하는 걸 권장해요.\n\n"
            "📌 신청: **시프티(Shiftee)** 앱 / 결재선: 팀원 → **팀장** 전결"
        )

    # ── 4. 출산 휴가 (경조사보다 먼저 검사) ────────────────────────────────
    if any(k in q for k in ("출산 휴가", "출산휴가", "출산")):
        time.sleep(0.5)
        return wrap(
            "👶 **출산 휴가** 안내예요!\n\n"
            "- 경조금: **500만 원** 🎉\n"
            "- 휴가: **20일** (120일 이내 **최대 3회** 분할 가능)\n"
            "- 출산일 포함 **3일은 반드시 연속** 사용해야 해요.\n\n"
            "**신청 방법** ⚠️ 절차가 변경됐어요!\n"
            "1. 그룹웨어 → **경조사 신고서** 작성 후 **인사지원팀 접수** (본인 전결 ❌)\n"
            "2. **시프티(Shiftee)**에 휴가 결재 시 **증빙 서류 첨부 필수**!\n\n"
            "⚠️ 근속 **1년 미만**이면 경조금은 **50%** 지급돼요. (휴가는 전일 지급)"
        )

    # ── 5. 결혼 ─────────────────────────────────────────────────────────────
    if any(k in q for k in ("결혼",)):
        time.sleep(0.5)
        return wrap(
            "💍 **결혼 경조 지원** 안내예요!\n\n"
            "- 경조금: **30만 원**\n"
            "- 휴가: **7일**\n\n"
            "**신청 방법** ⚠️ 절차가 변경됐어요!\n"
            "1. 그룹웨어 → **경조사 신고서** 작성 후 **인사지원팀 접수** (본인 전결 ❌)\n"
            "2. **시프티(Shiftee)**에 휴가 결재 시 **증빙 서류 첨부 필수**!\n\n"
            "⚠️ 근속 **1년 미만**이면 경조금은 **50%** 지급돼요. (휴가는 전일 지급)"
        )

    # ── 6. 부모상 / 조부모상 ────────────────────────────────────────────────
    if any(k in q for k in ("부모상", "조부모상", "상조", "장례", "부고")):
        time.sleep(0.5)
        return wrap(
            "🕯️ **상중(喪中) 경조 지원** 안내예요. 힘드실 텐데 잘 챙겨드릴게요.\n\n"
            "| 구분 | 경조금 | 휴가 |\n"
            "|------|--------|------|\n"
            "| 부모상 (배우자 부모 포함) | **30만 원** | **5일** |\n"
            "| 조부모상 | **20만 원** | **3일** |\n"
            "| 조부모상 (승중) | **30만 원** | **5일** |\n\n"
            "**장례 서비스 지원** (본인·배우자·부모·자녀상)\n"
            "장례지도사 **1명**(3일), 상복 남·여 각 **4벌**, 리무진/버스 **200km** 이내\n\n"
            "**신청 방법** ⚠️ 절차가 변경됐어요!\n"
            "1. 그룹웨어 → **경조사 신고서** 작성 후 **인사지원팀 접수** (본인 전결 ❌)\n"
            "2. **시프티(Shiftee)**에 휴가 결재 시 **증빙 서류 첨부 필수**!"
        )

    # ── 6-1. 장수 경조휴가 (칠순/팔순) ─────────────────────────────────────
    if any(k in q for k in ("칠순", "팔순", "장수", "생신", "잔치")):
        time.sleep(0.5)
        return wrap(
            "🎂 **부모님 장수(칠순·팔순 등) 경조휴가** 안내예요!\n\n"
            "**날짜 기준**\n"
            "- 기본: **양력** 기준\n"
            "- 음력으로 행사를 치를 경우 → **경조사 신고서에 반드시 별도 기재** 필요!\n\n"
            "**필수 증빙 서류**\n"
            "- **가족관계증명서** (생년월일 표기 필수) ✅\n\n"
            "**음력 행사 시 추가 증빙** (아래 중 **택 1**)\n"
            "- 📱 가족 단톡방 공지 캡처 (날짜·내용 확인 가능)\n"
            "- 🍽️ 식당 예약 확인서 또는 결제 내역 (행사 일자 표기)\n"
            "- 📷 행사 사진 (촬영일 확인 가능)\n\n"
            "⚠️ 신청은 **인사지원팀 접수**로 진행해야 해요! (본인 전결 ❌)"
        )

    # ── 7. 경조사 (통합) ─────────────────────────────────────────────────────
    if any(k in q for k in ("경조", "경조금", "경조 휴가", "경조사")):
        time.sleep(0.5)
        return wrap(
            "💐 **경조사 지원 한눈에 보기**예요!\n\n"
            "| 구분 | 경조금 | 휴가 |\n"
            "|------|--------|------|\n"
            "| 본인 결혼 | **30만 원** | **7일** |\n"
            "| 본인/배우자 출산 | **500만 원** | **20일** |\n"
            "| 부모상 (배우자 포함) | **30만 원** | **5일** |\n"
            "| 조부모상 | **20만 원** | **3일** |\n"
            "| 조부모상 (승중) | **30만 원** | **5일** |\n\n"
            "⚠️ 근속 **1년 미만**이면 경조금 **50%** 지급 (휴가는 전일 지급)\n\n"
            "**신청 방법** ⚠️ 절차가 변경됐어요!\n"
            "1. 그룹웨어 → **경조사 신고서** 작성 후 **인사지원팀 접수** (본인 전결 ❌)\n"
            "2. **시프티(Shiftee)**에 휴가 결재 시 **증빙 서류 첨부 필수**!\n\n"
            "💡 칠순·팔순 등 장수 경조휴가 기준이 궁금하시면 '칠순'으로 물어봐 주세요!"
        )

    # ── 8. 보육료 (수치 강조) ───────────────────────────────────────────────
    if any(k in q for k in ("보육료", "보육비")):
        time.sleep(0.5)
        return wrap(
            "🍼 **미취학 자녀 보육료 지원** 안내예요! (국가 + 회사 매칭)\n\n"
            "| 연령 | 국가 지원 | 회사 추가 지원 |\n"
            "|------|-----------|----------------|\n"
            "| **0세반** | **584,000원** | **292,000원** |\n"
            "| **1세반** | **515,000원** | **257,500원** |\n"
            "| **2세반** | **426,000원** | **213,000원** |\n"
            "| **3~5세반** | **280,000원** | **140,000원** |\n\n"
            "📌 신청: 그룹웨어 → 전자결재에서 확인하세요."
        )

    # ── 9. 보육지원비 수당 ──────────────────────────────────────────────────
    if any(k in q for k in ("보육지원비", "보육 수당", "양육수당")):
        time.sleep(0.5)
        return wrap(
            "💰 **보육지원비 수당** 안내예요!\n\n"
            "- 만 **0~5세**: 매월 **10만 원** (비과세 처리 ✅)\n"
            "- 만 **6세**: 매월 **20만 원**\n"
            "- 자녀 **생일 월**을 기준으로 지원이 시작돼요.\n\n"
            "📌 별도 신청 없이 급여에 자동 반영돼요!"
        )

    # ── 10. 육아휴직 / 근로시간 단축 ───────────────────────────────────────
    if any(k in q for k in ("육아휴직", "육아 휴직", "근로시간 단축", "육아기")):
        time.sleep(0.5)
        return wrap(
            "👨‍👩‍👧 **육아기 근로시간 단축** 안내예요!\n\n"
            "- 대상: 만 **12세 이하** (초등 **6학년** 이하) 자녀를 둔 직원\n"
            "- 단축 범위: 하루 **1~5시간** 조절 가능\n"
            "- 육아휴직 미사용 기간의 **최대 2배**까지 연장 사용 가능!\n\n"
            "📌 신청: 그룹웨어 전자결재 → **휴직신청서** / 결재선: **본부(실)장** 승인"
        )

    # ── 11. 보육 통합 ───────────────────────────────────────────────────────
    if any(k in q for k in ("보육", "육아", "자녀 지원", "보육지원")):
        time.sleep(0.5)
        return wrap(
            "🍼 **자녀 양육 지원 전체 요약**이에요!\n\n"
            "**① 보육료 지원** — 국가 지원에 회사가 약 **50%** 추가 매칭\n"
            "**② 보육지원비 수당** — 만 0~5세 월 **10만 원** / 만 6세 월 **20만 원** (비과세)\n"
            "**③ 육아기 근로시간 단축** — 만 12세 이하 자녀, 하루 **1~5시간** 단축 가능\n\n"
            "어떤 항목이 더 궁금하세요? '보육료', '보육지원비 수당', '육아휴직' 등으로 다시 물어봐 주세요! 😊"
        )

    # ── 12. 재택근무 ────────────────────────────────────────────────────────
    if any(k in q for k in ("재택", "재택근무", "원격근무")):
        time.sleep(0.5)
        return wrap(
            "🏠 **재택근무 규정** 안내예요!\n\n"
            "- 기본 원칙: 주 **2회**\n"
            "- 주중 공휴일 **1일** 있는 주 → 재택 **1회**만 가능\n"
            "- 주중 공휴일 **2일 이상** → 재택 **불가**\n"
            "- ⚠️ 재택 시 사무실 전화를 휴대폰으로 **착신 전환 필수**예요!\n\n"
            "📌 근태 시스템: **시프티(Shiftee)** 에 별도 입력하세요."
        )

    # ── 13. 자율출근 ────────────────────────────────────────────────────────
    if any(k in q for k in ("자율출근", "자율 출근", "출근 시간", "플렉스")):
        time.sleep(0.5)
        return wrap(
            "⏰ **자율출근제** 안내예요!\n\n"
            "- 하루 **9시간**(휴게 포함)만 채우면 출근 시간은 자유롭게 정할 수 있어요.\n"
            "- 지각 처리 없이 자율적으로 출근 가능해요! 🎉\n\n"
            "📌 단, 팀 회의나 일정이 있는 날은 미리 팀장님과 조율해 주세요."
        )

    # ── 14. 해외 출장 ───────────────────────────────────────────────────────
    if any(k in q for k in ("해외출장", "해외 출장")):
        time.sleep(0.5)
        return wrap(
            "✈️ **해외 출장** 신청 안내예요!\n\n"
            "- 전결권자: **사장**\n"
            "- 합의 부서: **경영기획실**, **경영관리팀**\n"
            "- 📄 서류: **기안서 + 출장신청서**\n\n"
            "**출장비 정산**\n"
            "- 선지급 신청 → **팀장** → 재무팀 통보 (출장신청서)\n"
            "- 정산 → **팀장** → 재무팀 (지출명세서 + 출장여비계산서)\n\n"
            "📌 서류는 그룹웨어 전자결재에서 내려받으세요!"
        )

    # ── 15. 출장 (통합) ─────────────────────────────────────────────────────
    if any(k in q for k in ("출장", "출장비", "출장 결재")):
        time.sleep(0.5)
        return wrap(
            "✈️ **출장 신청 결재선** 안내예요!\n\n"
            "**국내 출장**\n"
            "- 팀원 → **팀장** 승인 / 팀장 이상 → **본부(실)장** 승인\n"
            "- 📄 서류: **출장신청서**\n\n"
            "**해외 출장**\n"
            "- 전결권자: **사장** (경영기획실·경영관리팀 합의)\n"
            "- 📄 서류: **기안서 + 출장신청서**\n\n"
            "**비용 정산**\n"
            "- 출장비 정산: **팀장** → 재무팀 / 서류: 지출명세서\n"
            "- 시내교통비: **팀장** → 인사지원팀 / 서류: 교통비신청서\n\n"
            "📌 서류 양식은 그룹웨어 전자결재에서 받으세요!"
        )

    # ── 16. 자격증 ──────────────────────────────────────────────────────────
    if any(k in q for k in ("자격증", "자기계발", "학습비", "축하금")):
        time.sleep(0.5)
        return wrap(
            "📚 **자격증 취득 지원** 안내예요!\n\n"
            "| 등급 | 지원 금액 (학습비 + 축하금) |\n"
            "|------|-----------------------------|\n"
            "| LV 1 | **20만 원** |\n"
            "| LV 2 | **50만 원** |\n"
            "| LV 3 | **80만 원** |\n"
            "| LV 4 | **120만 원** |\n"
            "| LV 5 | **150만 원** |\n\n"
            "💡 지원 리스트에 없는 자격증도 **직무 연관성**이 인정되면 지급받을 수 있어요!\n\n"
            "📌 신청·문의: **인사지원팀**으로 연락 주세요."
        )

    # ── 17. 접대비 ──────────────────────────────────────────────────────────
    if any(k in q for k in ("접대비", "접대", "사외 회의비", "사외회의비")):
        time.sleep(0.5)
        return wrap(
            "🍽️ **접대비 결재선** 안내예요!\n\n"
            "- 건당 **20만 원 미만** → **팀장** 전결\n"
            "- 건당 **30만 원 미만** → **실장** 전결\n"
            "- 건당 **30만 원 이상** → **본부(실)장** 전결 (정도경영팀 합의 필요)\n\n"
            "📌 사외 회의비도 접대비 기준과 동일하게 적용돼요."
        )

    # ── 18. 경비 전표 ───────────────────────────────────────────────────────
    if any(k in q for k in ("경비", "전표", "비용 전표", "비용전표")):
        time.sleep(0.5)
        return wrap(
            "🧾 **경비 전표 결재선** 안내예요!\n\n"
            "- 건당 **100만 원 미만** → **팀장** 전결\n"
            "- 건당 **2,000만 원 미만** → **본부(실)장** 전결\n"
            "- 건당 **2,000만 원 이상** → **사장** 전결\n\n"
            "📌 광고선전비도 경비와 동일한 기준이 적용돼요. 그룹웨어 전자결재 이용!"
        )

    # ── 19. 구매 품의 ───────────────────────────────────────────────────────
    if any(k in q for k in ("구매", "품의", "구매 품의")):
        time.sleep(0.5)
        return wrap(
            "🛒 **구매 품의 결재선** 안내예요!\n\n"
            "- 총액 **100만 원 미만** → **팀장** 전결\n"
            "- 총액 **2,000만 원 미만** → **본부(실)장** 전결\n"
            "- 총액 **2,000만 원 이상** → **사장** 전결\n\n"
            "📌 서류: **기안서** / 그룹웨어 전자결재에서 양식을 사용하세요!"
        )

    # ── 20. 비용 결재 통합 ──────────────────────────────────────────────────
    if any(k in q for k in ("결재", "전결", "비용", "결재선")):
        time.sleep(0.5)
        return wrap(
            "✅ **비용 결재선 요약** 안내예요!\n\n"
            "| 유형 | 기준 | 전결권자 |\n"
            "|------|------|----------|\n"
            "| 경비 전표 | **100만 원 미만** | 팀장 |\n"
            "| 경비 전표 | **2,000만 원 미만** | 본부(실)장 |\n"
            "| 경비 전표 | **2,000만 원 이상** | 사장 |\n"
            "| 접대비 | **20만 원 미만** | 팀장 |\n"
            "| 접대비 | **30만 원 미만** | 실장 |\n"
            "| 접대비 | **30만 원 이상** | 본부(실)장 |\n\n"
            "💡 더 구체적인 항목(경비·접대비·구매 품의 등)을 말씀해 주시면 딱 맞는 정보를 드릴게요!"
        )

    # ── 21. 교육 통합 (사외교육 + 사이버 연수원) ────────────────────────────
    if any(k in q for k in ("교육", "사외교육", "외부교육", "연수", "수료증", "연수원", "사이버", "인강", "이러닝", "e-learning", "미수료")):
        time.sleep(0.5)
        return wrap(
            "📚 **미래엔 교육 지원 제도** 안내예요!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "**🎓 사외교육 지원**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "직무 관련 온라인·집합 교육 비용 **전액 지원**!\n\n"
            "**신청:** 그룹웨어 → 전자결재 → 새 결재 → **'교육신청서'** 작성\n\n"
            "**💳 결제 및 정산**\n"
            "1. 개인 **법인카드**로 선결제\n"
            "2. 매월 **25일 이후** 교육비 예산으로 이관\n"
            "3. 이관 후 법인카드 비용 처리 절차에 따라 정산\n\n"
            "**결재선**\n"
            "| 기간 | 전결권자 |\n"
            "|------|----------|\n"
            "| 3일 이내 | 팀장(실장) |\n"
            "| 3일 초과 | 본부(실)장 |\n"
            "| 1개월↑ | 사장 |\n\n"
            "**✅ 사후:** 수료증(PDF) 또는 참석 증빙 → 담당자 제출 필수\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "**💻 사이버 연수원 (E-learning)**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "미래엔의 온라인 학습 플랫폼으로 매월 다양한 과정 제공!\n\n"
            "**신청:** 매월 중순 그룹웨어 **전사게시판** 안내 글 확인 후 기간 내 신청\n"
            "**수강:** 신청 달의 **익월(다음 달)** 한 달간 자유 수강\n"
            "**기준:** 매월 **1개** 과정 신청 가능 (OA 교육은 **추가 신청 가능!**)\n\n"
            "⚠️ **미수료 페널티 주의!**\n"
            "신청 후 미수료 시 → 향후 **6개월간** 수강 신청 및 학습 **금지**\n"
            "책임감 있는 수강 부탁드려요! 😊\n\n"
            "📌 문의: **인사지원팀**"
        )

    # ── 22. WIFI ────────────────────────────────────────────────────────────
    if any(k in q for k in ("wifi", "와이파이", "wi-fi")):
        time.sleep(0.4)
        return wrap(
            "📶 **WIFI 정보** 알려드릴게요!\n\n"
            "- 직원용: **`MiraeN-AP`** / PW: **`19480924ab`**\n"
            "- 외부 방문객용: **`MiraeN-WIfI`** / PW: **`34753800`**\n\n"
            "💡 사이드바에도 항상 표시되어 있어요! 😊"
        )

    # ── 23. 명함 ────────────────────────────────────────────────────────────
    if any(k in q for k in ("명함",)):
        time.sleep(0.4)
        return wrap(
            "🪪 **명함 신청 방법** 안내예요!\n\n"
            "1. 사이트 접속: **mirae-n.onehp.co.kr**\n"
            "2. ID: **`miraen`** / PW: **`1111`** 로 로그인\n"
            "3. 신청서 작성 후 제출!\n\n"
            "📌 위 주소를 브라우저에 직접 입력하거나 복사해서 접속하세요 😊"
        )

    # ── 23-1. 그룹웨어 ──────────────────────────────────────────────────────
    if any(k in q for k in ("그룹웨어", "groupware", "전자결재", "경조사 신고서")):
        time.sleep(0.4)
        return wrap(
            "🖥️ **그룹웨어** 안내예요!\n\n"
            "- 주소: **gw.mirae-n.com**\n\n"
            "**주요 메뉴**\n"
            "- 📝 경조사 신고서\n"
            "- 🏖️ 휴가 신청\n"
            "- ✅ 전자결재\n\n"
            "📌 사내 네트워크(또는 VPN) 연결 상태에서 접속하세요!"
        )

    # ── 23-2. 시프티 / 근태 ─────────────────────────────────────────────────
    if any(k in q for k in ("시프티", "shiftee", "근태", "연장근무", "근무 신청")):
        time.sleep(0.4)
        return wrap(
            "📅 **근태 관리 시스템 (Shiftee)** 안내예요!\n\n"
            "- 주소: **shiftee.io**\n\n"
            "**주요 용도**\n"
            "- 🏖️ 휴가 입력\n"
            "- ⏰ 연장근무 신청\n"
            "- 📋 경조 휴가 입력 시 **증빙 서류 첨부 필수!**\n\n"
            "📌 앱 다운로드 후 사번으로 로그인하면 돼요 😊"
        )

    # ── 24. 문서보안 ────────────────────────────────────────────────────────
    if any(k in q for k in ("문서보안", "보안", "문서 보안")):
        time.sleep(0.4)
        return wrap(
            "🔒 **문서보안 설정** 안내예요!\n\n"
            "- 서버 주소: **`doc.mirae-n.com`**\n"
            "- 포트: **`443`**\n"
            "- 계정: 본인 **사번**\n\n"
            "📌 설치·연결 오류 시 **IT 지원팀**에 문의해 주세요!"
        )

    # ── 25. 학자금 ──────────────────────────────────────────────────────────
    if any(k in q for k in ("학자금", "대학교", "대학", "등록금")):
        time.sleep(0.5)
        return wrap(
            "🎓 **대학교 학자금 지원** 안내예요!\n\n"
            "- 대상: 재직 **5년 이상** 임직원의 자녀\n"
            "- 지원 금액: 연간 최대 **200만 원**\n"
            "- 지원 항목: 입학금, 수업료, 기성회비 **(해당 항목만 인정)**\n"
            "- 신청 시기: 매년 **8~9월**\n\n"
            "📌 신청: 그룹웨어 **전자결재** / 재직 **5년 미만**은 대상에서 제외돼요!"
        )

    # ── 26. 입학 선물 ───────────────────────────────────────────────────────
    if any(k in q for k in ("입학", "입학 선물", "교복", "학용품")):
        time.sleep(0.5)
        return wrap(
            "🎒 **취학 자녀 입학 선물 지원** 안내예요!\n\n"
            "| 구분 | 한도 | 지원 내용 |\n"
            "|------|------|-----------|\n"
            "| 초등학생 | **30만 원** | 학용품 / 도서 |\n"
            "| 중·고등학생 | **40만 원** | 교복 / 체육복 |\n\n"
            "- 영수증 정산 방식이에요.\n"
            "- 신청 시기: 매년 **2월** (신청서 접수)\n\n"
            "📌 신청서는 그룹웨어 또는 **인사지원팀**에서 받을 수 있어요!"
        )

    # ── 27. 건강검진 ────────────────────────────────────────────────────────
    if any(k in q for k in ("건강검진", "검진", "건강 검진", "종합검진", "건강 체크")):
        time.sleep(0.5)
        return wrap(
            f"🏥 **건강검진 제도** 안내예요!\n\n"
            f"**대상 확인**\n"
            f"올해는 **{current_year}년**이에요! 입사 연도와 격년 수검 원칙에 따라 본인이 대상자인지 확인해 보세요. (입사 **2년 후**부터 적용)\n\n"
            f"**검진 기관** (택 1)\n"
            f"- 하나로리더스헬스케어\n"
            f"- KMI (전국 **7개** 센터)\n"
            f"- 하나병원\n"
            f"- 세종국민건강의원\n\n"
            f"**예약 방법**\n"
            f"매년 **2월경** 발송되는 알림톡 또는 각 기관 홈페이지 예약\n"
            f"💡 **9~10월이면 마감**되니 상반기 안에 예약하는 걸 강력 권장해요!\n\n"
            f"**지원 범위**\n"
            f"- 기본: **본인** 지원\n"
            f"- **배우자까지** 지원되는 경우:\n"
            f"  · 실장 / 팀장 직급\n"
            f"  · **40세 이상** + **근속 10년 이상** 동시 충족\n\n"
            f"**근태 (공가)**\n"
            f"- 종합검진 당일 **0.5일 공가** 제공 ✅\n"
            f"- ⚠️ 국가검진만 단독 진행 시 공가 **불가**"
        )

    # ── 28. 호칭 체계 / 직급 / 승진 ─────────────────────────────────────────
    if any(k in q for k in ("호칭", "직급", "승진", "선임", "책임", "수석", "연차")):
        time.sleep(0.5)
        return wrap(
            "🏅 **미래엔 호칭 체계** 안내예요!\n\n"
            "| 호칭 | 해당 기간 | 누적 연수 |\n"
            "|------|----------|-----------|\n"
            "| **님** | 입사 후 **2년** | ~2년 |\n"
            "| **선임** | 님 이후 **6년** | ~8년 |\n"
            "| **책임** | 선임 이후 **5년** | ~13년 |\n"
            "| **수석** | 책임 이후 | 13년 이상 |\n\n"
            "💡 호칭은 재직 연수 기준으로 자동 승급되는 구조예요!\n\n"
            "📌 세부 승급 기준은 **인사지원팀**에 문의해 주세요."
        )

    # ── 29. 성과 / 역량 평가 ─────────────────────────────────────────────────
    if any(k in q for k in ("평가", "성과", "역량", "okr", "인사평가")):
        time.sleep(0.5)
        return wrap(
            "📊 **미래엔 평가 제도** 안내예요!\n\n"
            "**🎯 성과 평가**\n"
            "- 기준: 조직 **OKR** 달성을 위한 개인별 목표 설정 및 달성 정도\n"
            "- 횟수: **연 1회** 실시\n\n"
            "**💡 역량 평가**\n"
            "- 기준: 핵심가치 바탕의 역량 및 리더십 평가\n"
            "- 횟수: **연 1회** 실시\n\n"
            "| 평가 항목 | 비중 |\n"
            "|----------|------|\n"
            "| 공통 역량 | **50%** |\n"
            "| 직군별 핵심 역량 | **50%** |\n\n"
            "📌 평가 일정 및 세부 기준은 **인사지원팀**을 통해 안내받으세요!"
        )

    # ── 30. 워케이션 ────────────────────────────────────────────────────────
    if any(k in q for k in ("워케이션", "워크케이션", "거점 오피스", "거점오피스", "제주", "리프레시")):
        time.sleep(0.5)
        return wrap(
            "🏝️ 제주도에서의 일주일, 생각만 해도 설레지 않나요? MAMA가 신청을 도와드릴게요!\n\n"
            "**워케이션 제도** 안내예요!\n\n"
            "- 📍 장소: 제주도 등 **지정된 거점 오피스**\n"
            "- 📅 기간: **1주일** 근무\n"
            "- 💰 지원: 숙박비 + 항공비, 회당 최대 **50만 원**\n"
            "- 🔁 이용 횟수: **연 1회**\n\n"
            "**신청 방법**\n"
            "1. 그룹웨어 → **워케이션 신청서** 작성\n"
            "2. **팀장** 결재 후 확정!\n\n"
            "🌊 일도 하고 리프레시도 하는 미래엔의 복지, 꼭 활용해 보세요!"
        )

    # ── 28. 휴가 통합 (가장 마지막에 배치) ────────────────────────────────
    if any(k in q for k in ("휴가",)):
        time.sleep(0.5)
        return wrap(
            "🏖️ **미래엔 휴가 제도 요약**이에요!\n\n"
            "- **연차**: 최소 **2시간 단위**로 분할 사용 가능\n"
            "- **플러스 휴가**: 매년 **4일** 추가 부여 (당해 연도 소멸, 연차보다 먼저 사용 권장)\n"
            "- **장기근속 휴가**: 5년 **3일** → 10/15년 **5일** → 20년 **7일** → 25년↑ **10일**\n\n"
            "💡 더 구체적인 항목을 물어보시면 해당 내용만 딱 알려드릴게요! 예: '플러스 휴가 알려줘'"
        )

    # ── Fallback ────────────────────────────────────────────────────────────
    time.sleep(0.4)
    return (
        "앗, 그 부분은 MAMA가 아직 학습 중이에요! 😅\n\n"
        "당황하지 마시고, 제가 잘 아는 아래 주제들로 다시 한 번 물어봐 주시겠어요?\n\n"
        "**📚 MAMA가 잘 아는 전문 분야**\n"
        "🍼 보육료·수당 | 💐 경조사·출산 | 🏖️ 휴가·워케이션 | 🏠 재택·출근\n"
        "✈️ 출장 정산 | 📚 자격증·교육 | ✅ 결재선·품의 | 🔒 보안·명함 | 🏥 건강검진\n\n"
        "MAMA를 넘어서는 고난도 질문은? 📞 언제든 **인사지원팀**의 문을 두드려 주세요!"
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


# 전송 버튼으로 메시지 전송
if send_clicked and user_input:
    handle_send(user_input)
