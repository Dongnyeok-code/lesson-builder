# 사용하는 곳별 안내 (Claude · 안티그래비티 · ChatGPT)

스킬 내용(0~9단계, 규칙 문서, 템플릿, 스크립트)은 어디서나 같다. 달라지는 것은 **파일을 어디에 두는지, 인터넷과 화면 검사가 되는지**뿐이다.
새 환경에서는 먼저 `python3 scripts/doctor.py`로 도구를 확인한다.

## 공통 원칙
- 스킬 폴더 전체(SKILL.md + references/ + templates/ + scripts/ + schemas/ + examples/)를 함께 옮긴다. SKILL.md만 옮기면 build.py가 없어 만들 수 없다.
- 교과서·지도서 PDF와 작업 결과는 스킬 폴더가 아니라 교사 작업 폴더(`수업자료/...`)에 둔다.
- 인터넷이 안 되는 곳에서는 5단계(그림·영상 찾기)를 **교사에게 링크·그림을 받는 방식**으로 바꾸고, 그 사실을 4단계 질문에서 미리 알린다.

## 1. Claude (지금 쓰는 곳)
| 항목 | 내용 |
|---|---|
| 스킬 폴더 | 교사 컴퓨터 `~/수업/스킬/lesson-builder` (원본), 스킬 등록은 저장 카드로 |
| 실행 | 교사 컴퓨터 셸에서 build.py·check.py·kordoc (Claude 데스크톱 앱이 켜져 있어야 함) |
| 인터넷 | 내장 브라우저로 유튜브·위키미디어·출판사 QR 영상 (environment.md) |
| 화면 검사 | 클라우드 셸의 Playwright로 shots.js |
| 주의 | 한글 경로(NFD), 파일 삭제 막힘 → environment.md |

## 2. 구글 안티그래비티 (2026-10 공식 문서로 확인)
| 항목 | 내용 |
|---|---|
| 스킬 폴더 | 전역(앱·IDE): `~/.gemini/config/skills/lesson-builder/` · 전역(CLI): `~/.gemini/antigravity-cli/skills/lesson-builder/` · 프로젝트별: `<작업 폴더>/.agents/skills/lesson-builder/` |
| 설치 | Claude와 같은 Mac이면 복사하지 말고 **연결(심볼릭 링크)**: `ln -s ~/수업/스킬/lesson-builder ~/.gemini/config/skills/lesson-builder` → 한 곳만 고치면 둘 다 바뀜. 다른 컴퓨터면 `git clone https://github.com/Dongnyeok-code/lesson-builder ~/.gemini/config/skills/lesson-builder` |
| 부르기 | 요청 문장이 description과 맞으면 자동으로 씀. 앱에서는 `/lesson-builder`로 직접 부름 |
| 실행 | 교사 컴퓨터에서 바로 실행되므로 build.py·check.py·kordoc 그대로 사용. 작업 공간(workspace)은 `~/수업` 폴더로 연다 |
| 인터넷 | 에이전트 브라우저로 유튜브·위키미디어 검색 가능. 안 되면 교사가 링크 제공 |
| 화면 검사 | 교사 컴퓨터에 `npm i -g playwright && npx playwright install chromium` 후 shots.js |
| 바꿀 것 | environment.md(Claude 전용)는 따르지 않는다. 모든 명령을 같은 컴퓨터에서 실행하고, 한글 경로(NFD) 문제도 없다 |

## 3. ChatGPT (2026-10 공식 도움말로 확인)
**스킬 기능은 ChatGPT Business·Enterprise·Healthcare·Edu 요금제에서만 된다.** 개인 Free·Plus·Pro에는 없다.

| 항목 | 내용 |
|---|---|
| 등록 (Business·Edu 등) | 왼쪽 **Plugins** → **Skills** 탭 → **Create** → **Upload from your computer**. 스킬 폴더(examples·docs 빼도 됨)를 zip으로 묶어 올린다. 올린 스킬은 검사 후 "Needs Review"가 될 수 있다 |
| 대안 (개인 Plus) | **GPT 만들기(Custom GPT)**: 지침 칸에 "첨부한 SKILL.md를 따라라, 0~9단계를 지켜라"만 쓰고, 지식 파일로 SKILL.md·references/*.md·templates/*·scripts/build.py·check.py를 올린다. **코드 인터프리터**를 켠다 |
| 실행 | 코드 실행 환경에서 build.py·check.py 가능. kordoc(npx)·poppler가 없을 수 있음 → doctor.py로 확인 |
| 교과서 | PDF를 대화에 올리고, 해당 쪽만 읽도록 쪽 번호를 함께 알려 준다 |
| 인터넷 | 코드 실행 환경은 인터넷이 막혀 있다. 그림·영상은 ChatGPT 웹 검색으로 후보를 찾고, 그림 파일은 교사가 올려 준다 |
| 결과 | 만든 HTML·활동지를 내려받아 교사 컴퓨터 작업 폴더에 둔다 |
| 화면 검사 | Playwright가 없으면 교사가 화면용 HTML을 열어 직접 확인 (qa-checklist의 '화면' 항목) |

## 옮길 때 고칠 곳 목록
- `SKILL.md` description: 그 도구가 스킬을 고르는 기준이므로 그대로 둔다.
- `references/environment.md`: Claude 전용 내용이다. 다른 곳에서는 이 문서 대신 위 표를 따른다.
- 교육과정 MCP(`scripts/mcp_call.py`)는 npx가 되는 곳에서만 쓴다. 안 되면 1단계를 단원 md·지도서 단일 출처로 진행하고 표시한다.
