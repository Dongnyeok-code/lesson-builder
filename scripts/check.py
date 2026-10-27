#!/usr/bin/env python3
"""7단계 자동 품질 검사.

사용법:  python3 check.py <build폴더>
- build폴더 안의 lesson.json과 build.py가 만든 HTML을 검사한다.
- 결과를 <build폴더>/qa-report.md 로 저장한다.
- 실패(❌)가 하나라도 있으면 종료 코드 1 → 6단계로 돌아가 lesson.json을 고친다.
"""
import json, re, sys
from pathlib import Path

DOMAINS = ["knowledge", "skill", "attitude"]
KO = {"knowledge": "지식", "skill": "기능", "attitude": "태도"}

# 평가·목표 문장에서는 실패, 그 밖의 곳(교과 내용)에서는 경고
DEFICIT = ["못한다", "못함", "미흡", "하 수준", "하위권", "낮은 학생", "이해하지 못", "지도가 필요", "틀렸", "오답", "부족한 학생", "부족함", "부족하다"]
SOFT = ["부족"]  # '영양 부족'처럼 교과 내용일 수 있어 경고만
BAD_ENDINGS = ["안다", "이해한다", "깨닫는다", "익힌다", "기른다", "관심을 가진다", "이해할 수 있다", "알 수 있다"]
GROWTH_MARKERS = ["수 있음", "다가갈", "깊어질", "넓어질", "성장", "나아갈", "해낼"]

fails, warns, passes = [], [], []


def ok(cond, msg, level="fail"):
    if cond:
        passes.append(msg)
    else:
        (fails if level == "fail" else warns).append(msg)
    return cond


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def visible_text(html):
    html = re.sub(r"data:[^\"')\s]+", "", html)
    return re.sub(r"<[^>]+>", " ", html)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    d = Path(sys.argv[1]).resolve()
    lj = d / "lesson.json"
    if not lj.is_file():
        print(f"❌ {lj} 가 없습니다."); sys.exit(1)
    L = json.loads(lj.read_text(encoding="utf-8"))
    meta, C, A = L.get("meta", {}), L.get("curriculum", {}), L.get("assessment", {})

    # 1. 교육과정
    stds = C.get("standards", [])
    ok(len(stds) > 0, "1단계: 성취기준이 1개 이상 있음")
    for s in stds:
        ok(s.get("cross_check") != "불일치", f'1단계: {s.get("code")} 원문 교차 검증이 불일치가 아님')
        ok(bool(s.get("official_text")), f'1단계: {s.get("code")} 공식 원문이 있음')
        if s.get("cross_check") == "단일 출처":
            warns.append(f'1단계: {s.get("code")} 원문이 한 출처에서만 확인됨 — 교사 확인 권장')
    ok(len(C.get("evidence_hints", [])) > 0, "1단계: 평가 단서가 1개 이상 있음")

    # 2. 학습목표 3영역
    obj = A.get("objectives", {})
    ok(obj.get("focus") in DOMAINS, "2단계: 중심 영역(focus)이 표시됨")
    for dmn in DOMAINS:
        text = obj.get(dmn, "").strip()
        if ok(bool(text), f"2단계: {KO[dmn]} 목표가 있음"):
            bad = [e for e in BAD_ENDINGS if text.rstrip(".").endswith(e)]
            ok(not bad, f"2단계: {KO[dmn]} 목표가 확인 가능한 동사로 끝남" + (f" (현재: '{bad[0]}')" if bad else ""))
    if obj.get("attitude"):
        ok(any(w in obj["attitude"] for w in ["노력", "실천", "점검", "시도"]),
           "2단계: 태도 목표가 시도·과정 표현(노력/실천/점검)을 담음", "warn")

    # 평가 증거·성공 기준·성장 단계
    ev_domains = {e.get("domain") for e in A.get("evidence", [])}
    for dmn in DOMAINS:
        ok(dmn in ev_domains, f"2단계: {KO[dmn]} 영역에 평가 증거가 있음")
    sc = {c.get("domain"): c for c in A.get("success_criteria", [])}
    for dmn in DOMAINS:
        c = sc.get(dmn, {})
        ok(bool(c.get("student")) and bool(c.get("not_yet")), f'2단계: {KO[dmn]} 성공 기준에 "아직이라면" 짝이 있음')
    gl = A.get("growth_levels", {})
    for dmn in DOMAINS:
        g = gl.get(dmn, {})
        ok(all(g.get(k) for k in ["deepening", "achieving", "starting"]), f"2단계: {KO[dmn]} 성장 단계 3개가 모두 있음")
        st = g.get("starting", "")
        if st:
            ok(any(m in st for m in GROWTH_MARKERS), f'2단계: {KO[dmn]} "시작하는 중"에 다음 성장 방향이 담김', "warn")

    # 확인 질문
    ch = A.get("checks", {})
    ok(bool(ch.get("intro", {}).get("question")), "2단계: 도입 진단 질문이 있음")
    ok(bool(ch.get("exit", {}).get("question")), "2단계: 출구표 질문이 있음")
    opts = ch.get("hinge", {}).get("options", [])
    ok(len(opts) >= 3, "2단계: 힌지 질문 선택지가 3개 이상")
    ok(sum(1 for o in opts if o.get("correct")) == 1, "2단계: 힌지 질문 정답이 정확히 1개")
    for i, o in enumerate(opts, 1):
        if not o.get("correct"):
            ok(bool(o.get("misconception")) and bool(o.get("teacher_move")), f"2단계: 힌지 오답 {i}번에 오개념과 교사 대응이 있음")
    ok(len(A.get("self_check", [])) >= 2, "2단계: 자기 점검 문항이 2개 이상")

    # 금지 표현 (평가 영역은 실패, 그 밖은 경고)
    eval_paths = ("assessment", "flow")
    for path, text in walk(L):
        strict = path.startswith(eval_paths)
        for w in DEFICIT:
            if w in text:
                (fails if strict else warns).append(f'금지 표현 "{w}" — {path}')
        if strict:
            for w in SOFT:
                if w in text and not any(x in text for x in DEFICIT):
                    warns.append(f'확인 필요 표현 "{w}" — {path} (교과 내용이면 무시)')
    if not any("금지 표현" in f for f in fails):
        passes.append("2단계: 평가·목표 문장에 결손 중심 표현 없음")

    # 3. 교과서 근거
    ev = L.get("evidence", [])
    figs = L.get("figures") or (L.get("evidence_meta") or {}).get("figures") or {}
    n_ext = sum(1 for sub in ("tb", "gd") for _ in (d / "images" / sub).glob("image_*.png")) if (d / "images").is_dir() else 0
    if n_ext:
        ok(len(figs) > 0, f"3단계: 추출 그림 {n_ext}장을 모아보기로 확인해 figures에 기록함 ({len(figs)}개 기록)", "warn")
    ok(len(ev) > 0, "3단계: 교과서 근거 항목이 있음")
    missing = [i for i, e in enumerate(ev) if not str(e.get("page", "")).strip()]
    ok(not missing, "3단계: 모든 근거 항목에 쪽 번호가 있음" + (f" (빠진 항목: {missing})" if missing else ""))

    # 4. 수업 흐름
    F = L.get("flow", {})
    ok(F.get("approved") is True, "4단계: 교사 승인(approved=true)")
    steps = F.get("steps", [])
    total = sum(s.get("minutes", 0) for s in steps)
    ok(total == meta.get("minutes"), f'4단계: 활동 시간 합({total}분) = 수업 시간({meta.get("minutes")}분)')
    ok(all(s.get("evidence_link") for s in steps), "4단계: 모든 활동에 연결 평가 증거가 있음")

    # 5. 미디어
    for i, m in enumerate(L.get("media", [])):
        ok(bool(m.get("source")), f"5단계: 미디어 {i+1}번에 출처가 있음")
        if m.get("type") == "image":
            ok(bool(m.get("license")), f'5단계: 이미지 {m.get("file", i+1)}에 라이선스가 기록됨')
    sessions = L.get("sessions") or [{"label": "단일 차시", "slides": L.get("slides", [])}]
    slides = [x for ss in sessions for x in ss.get("slides", [])]
    types = [s.get("type") for s in slides]
    for ss in sessions:
        n = len(ss.get("slides", []))
        ok(n >= 30, f'스타일: {ss.get("label")} 슬라이드 {n}장 (기준 30장 이상, 채우기용 없이)', "warn")
        ss_sl = ss.get("slides", [])
        n_img = sum(1 for s in ss_sl if s.get("src") or s.get("img") or s.get("imgs")
                    or any(c.get("img") for c in s.get("cards", [])))
        ok(n_img >= 6, f'스타일: {ss.get("label")} 교과서·지도서 그림이 들어간 슬라이드 {n_img}장 (기준 6장 이상)', "warn")
        emo = sum(1 for s in ss_sl for c in s.get("cards", []) if c.get("emoji") and not c.get("img"))
        ok(emo == 0 or n_img >= 6, f'스타일: {ss.get("label")} 그림 대신 이모지만 쓴 카드 {emo}개', "warn")
    ok("word" in types, '스타일: "낱말 알기" 슬라이드가 있음', "warn")
    ok(bool(meta.get("theme")), "스타일: 단원 컨셉(meta.theme)이 정해짐", "warn")
    for need in ["goals", "hinge", "exit"]:
        ok(need in types, f"6단계: 슬라이드에 {need} 가 있음")
    if any(s.get("type") in ("image", "stage", "video") for s in slides) or L.get("media"):
        ok("sources" in types, "6단계: 출처 슬라이드가 있음", "warn")
    for i, s in enumerate(slides):
        if s.get("type") in ("text", "cards", "stage", "image", "activity") and not s.get("page"):
            warns.append(f'6단계: 슬라이드 {i+1}번({s.get("type")} "{s.get("heading", "")}")에 교과서 쪽 표시가 없음')

    # 6·7. 산출물
    label = (lambda q: f"{q[0]}_{q[-1]}" if len(q) > 1 else str(q[0]))(list(meta.get("periods", []))) + "차시"
    sl, ws, pl = d / f"{label}_화면용.html", d / f"{label}_활동지.html", d / f"{label}_수업안.md"
    for f in (sl, ws, pl):
        ok(f.is_file(), f"8단계: {f.name} 파일이 있음")
    if sl.is_file():
        h = sl.read_text(encoding="utf-8")
        ok("fsBtn" in h and "fullscreenchange" in h and ("fs-mode" in h or "scale(" in h), "화면용: 전체화면 버튼 + 전체화면 시 화면 확대")
        ok("ArrowRight" in h and "prevBtn" in h, "화면용: 버튼·키보드 이동")
        if "video" in types:
            ok("video-fallback" in h or "유튜브에서 열기" in h, "화면용: 유튜브 재생 안 될 때 대체 링크")
        vt = visible_text(h)
        for w in ["틀렸어요", "오답"]:
            if w in vt:
                warns.append(f'화면용: 학생에게 보이는 문구에 "{w}"')
    if ws.is_file():
        h = ws.read_text(encoding="utf-8")
        ok("break-inside:avoid" in h.replace(" ", ""), "활동지: 표·문항 쪽 잘림 방지")
        ok("<table" in h, "활동지: 실제 표(table) 사용")
    for f in (sl, ws, pl):
        if f.is_file():
            t = f.read_text(encoding="utf-8")
            if re.search(r"\d{6}-\d{7}", t):
                fails.append(f"{f.name}: 주민등록번호 형태의 숫자가 있음")

    # 보고서
    lines = [f'# 품질 검사 보고서 — {meta.get("subject", "")} {meta.get("grade", "")}학년 {meta.get("unit", "")}단원 {label}', "",
             f"- 실패: **{len(fails)}개** / 경고: {len(warns)}개 / 통과: {len(passes)}개", ""]
    if fails:
        lines += ["## ❌ 실패 (고쳐야 다음 단계로)", ""] + [f"- {x}" for x in fails] + [""]
    if warns:
        lines += ["## ⚠️ 경고 (확인 권장)", ""] + [f"- {x}" for x in warns] + [""]
    lines += ["## ✅ 통과", ""] + [f"- {x}" for x in passes] + ["",
              "## 수동 확인 (references/qa-checklist.md)", "",
              "- [ ] 교과서와 화면 내용·정답을 쪽별로 대조", "- [ ] 전체화면에서 맨 뒷자리 가독성",
              "- [ ] 활동지 인쇄 미리보기에서 잘림 없음", "- [ ] 학생 실명·개인정보 없음", ""]
    (d / "qa-report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"실패 {len(fails)} / 경고 {len(warns)} / 통과 {len(passes)}  → {d / 'qa-report.md'}")
    for x in fails:
        print("  ❌", x)
    for x in warns:
        print("  ⚠️ ", x)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
