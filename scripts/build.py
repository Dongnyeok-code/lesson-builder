#!/usr/bin/env python3
"""lesson.json → 화면용 HTML, 인쇄용 활동지 HTML, 수업안 Markdown 생성.

사용법:  python3 build.py <build폴더>/lesson.json [--no-embed]
- 내용은 lesson.json에만 쓴다. 디자인은 ../templates 를 쓴다.
- 이미지 경로가 'images/이름.*' 이면 빈 자리(자동 확장자 탐지)로 둔다.
- 그 밖의 로컬 이미지는 찾아서 base64로 넣어 한 파일로 만든다. 못 찾으면 빈 자리로 바꾸고 경고한다.
"""
import base64, html, json, mimetypes, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
DOMAIN = {"knowledge": "지식", "skill": "기능", "attitude": "태도"}
ORDER = ["knowledge", "skill", "attitude"]
warnings = []


def find_image(src, base_dir):
    p = Path(src)
    cands = [base_dir / p, base_dir / "images" / p.name]
    for up in list(base_dir.parents)[:4]:
        cands += [up / p, up / "images" / p.name]
    for c in cands:
        if c.is_file():
            return c
    return None


def embed(src, base_dir, do_embed):
    if not src or src.endswith(".*") or src.startswith(("http", "data:")):
        return src
    if not do_embed:
        return src
    f = find_image(src, base_dir)
    if not f:
        stem = Path(src).stem
        warnings.append(f"이미지를 찾지 못해 빈 자리로 바꿈: {src} → images/{stem}.*")
        return f"images/{stem}.*"
    return "data:" + compress(f)


_CACHE = {}


def compress(f, max_side=1100, q=82):
    key = (str(f), max_side, q)
    if key not in _CACHE:
        _CACHE[key] = _compress(f, max_side, q)
    return _CACHE[key]


def _compress(f, max_side=1100, q=82):
    """이미지를 화면용 크기로 줄여 WebP로 넣는다(투명 배경 유지). PIL이 없으면 원본 그대로."""
    mime = mimetypes.guess_type(f.name)[0] or "image/png"
    raw = f.read_bytes()
    if mime == "image/gif":
        return f"{mime};base64," + base64.b64encode(raw).decode()
    try:
        from PIL import Image
        import io
        im = Image.open(f)
        im.thumbnail((max_side, max_side))
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA")
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=q, method=4)
        if buf.tell() < len(raw):
            return "image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        pass
    return f"{mime};base64," + base64.b64encode(raw).decode()


def dedupe_images(obj, table, index):
    """같은 그림(data:)을 한 번만 저장하고, 슬라이드에는 '@img:번호'만 남긴다."""
    if isinstance(obj, dict):
        return {k: dedupe_images(v, table, index) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dedupe_images(v, table, index) for v in obj]
    if isinstance(obj, str) and obj.startswith("data:") and len(obj) > 200:
        if obj not in index:
            index[obj] = len(table)
            table.append(obj)
        return f"@img:{index[obj]}"
    return obj


def period_label(periods):
    """파일 이름용: [10,11] → 10_11차시, [1,2,3] → 1_3차시 (처음_끝)"""
    p = list(periods)
    return (f"{p[0]}_{p[-1]}" if len(p) > 1 else str(p[0])) + "차시"


def period_text(periods):
    """화면·문서 표시용: [1,2,3] → 1~3차시, [10,11] → 10~11차시"""
    p = list(periods)
    return (f"{p[0]}~{p[-1]}" if len(p) > 1 else str(p[0])) + "차시"


def fill_slide(s, L, base_dir, do_embed):
    s = dict(s)
    A = L["assessment"]
    if s["type"] == "goals" and "goals" not in s:
        obj = A["objectives"]
        s["focus"] = obj["focus"]
        s["goals"] = [{"domain": d, "text": obj[d]} for d in ORDER]
    if s["type"] == "criteria" and "items" not in s:
        s["items"] = A["success_criteria"]
    if s["type"] == "hinge" and "options" not in s:
        s.update({k: v for k, v in A["checks"]["hinge"].items() if k not in s})
    if s["type"] == "exit" and "prompt" not in s:
        s["prompt"] = A["checks"]["exit"]["question"]
    if s["type"] == "self_check" and "items" not in s:
        s["items"] = A["self_check"]
    if s["type"] == "sources" and "items" not in s:
        s["items"] = [f'{m.get("credit") or m.get("file") or m.get("videoId")} — {m["source"]}'
                      + (f' ({m["license"]})' if m.get("license") else "") for m in L["media"]]
    for key in ("src", "img", "left", "right"):
        if key in s:
            s[key] = embed(s[key], base_dir, do_embed)
    for c in s.get("cards", []):
        if c.get("img"):
            c["img"] = embed(c["img"], base_dir, do_embed)
    if s.get("imgs"):
        s["imgs"] = [embed(p, base_dir, do_embed) if p else p for p in s["imgs"]]
    return s


def get_sessions(L):
    """여러 차시는 L["sessions"] = [{label, title, slides}], 한 차시는 L["slides"]."""
    if L.get("sessions"):
        return L["sessions"]
    return [{"label": period_label(L["meta"]["periods"]), "title": "", "slides": L["slides"]}]


def theme_css(meta):
    th = meta.get("theme") or {}
    out = []
    colors = th.get("colors") or {}
    if colors:
        out.append(":root{" + "".join(f"--{k.lstrip('-')}:{v};" for k, v in colors.items()) + "}")
    if th.get("background"):
        out.append(f"html,body{{background:{th['background']};}}")
    if th.get("bullet"):
        out.append(f'.bullet-list li::before{{content:"{th["bullet"]}";}}')
    if th.get("title_decoration"):
        out.append(f'h2.slide-title::before{{content:"{th["title_decoration"]}";}}')
    if th.get("extra_css"):
        out.append(th["extra_css"])
    return "\n  ".join(out)


PALETTE_KEYS = ["cream", "mint", "sky", "pinkbg", "navy", "blue", "green", "pink", "yellow", "ink", "muted", "line", "lightblue"]


def editorial_theme_css(th):
    """meta.theme.palette 로 단원 컨셉 색을 바꾼다. 역할 이름은 그대로 두고 실제 색만 바꾼다."""
    pal = th.get("palette") or {}
    vars_ = "".join(f"--{k}:{v};" for k, v in pal.items() if k in PALETTE_KEYS)
    return (f":root{{{vars_}}}" if vars_ else "") + th.get("extra_css", "")



HELP_SLIDES = [
    {"type": "section", "kicker": "선생님용 안내", "title": "영상이 안 나올 때<br>(유튜브 오류 153)",
     "sub": "이 탭은 수업 전에 한 번 읽어 두세요"},
    {"type": "text", "heading": "왜 오류 153이 생기나요?", "tag": "원인",
     "body": "HTML 파일을 <b>더블클릭</b>해서 열면 주소가 <span class='em'>file://</span>로 시작해요.<br>이때 유튜브는 어느 사이트에서 튼 영상인지 알 수 없어서<br>화면 안 재생을 막고 <b>오류 153</b>을 띄워요. (출판사 영상은 괜찮아요)"},
    {"type": "text", "heading": "방법 1. ‘수업자료_열기’ 파일로 열기", "tag": "가장 쉬움 · 매번 1번 클릭",
     "body": "이 HTML과 같은 폴더의 <b>수업자료_열기.command</b>(맥) 또는 <b>수업자료_열기.bat</b>(윈도)을 더블클릭해요.<br>브라우저가 <span class='em'>http://localhost:8765</span> 주소로 열리고 유튜브가 화면 안에서 재생돼요.<br>맥에서 처음 열 때 경고가 나오면 <b>오른쪽 클릭 → 열기</b>를 누르세요."},
    {"type": "text", "heading": "방법 2. 인터넷 주소로 올려 두기", "tag": "한 번만 설정 · 다음부터 할 일 없음",
     "body": "HTML 파일을 <b>GitHub Pages</b>, <b>Vercel</b>, <b>Firebase</b> 같은 곳에 올리면<br><span class='em'>https://</span> 주소가 생겨요. 그 주소로 열면 매번 따로 할 일이 없어요.<br>교실 컴퓨터 어디서나 같은 주소로 열 수 있어요."},
    {"type": "text", "heading": "방법 3. 지금 바로 보기", "tag": "급할 때",
     "body": "파일로 열었을 때 영상 슬라이드에는 <b>‘▶ 유튜브에서 보기’</b> 버튼이 나와요.<br>누르면 유튜브 새 창에서 바로 재생돼요."},
]


def write_launchers(base, html_name):
    """유튜브 오류 153을 피하려고 로컬 서버로 여는 실행 파일을 만든다."""
    import os, urllib.parse, unicodedata
    url = "http://localhost:8765/" + urllib.parse.quote(unicodedata.normalize("NFC", html_name))
    mac = base / "수업자료_열기.command"
    mac.write_text("#!/bin/bash\n"
                   'cd "$(dirname "$0")"\n'
                   "PORT=8765\n"
                   "if ! lsof -i :$PORT >/dev/null 2>&1; then\n"
                   "  nohup python3 -m http.server $PORT >/dev/null 2>&1 &\n"
                   "  sleep 1\n"
                   "fi\n"
                   f'open "{url}"\n', encoding="utf-8")
    os.chmod(mac, 0o755)
    win = base / "수업자료_열기.bat"
    win.write_text("@echo off\r\n"
                   'cd /d "%~dp0"\r\n'
                   'start "" /min python -m http.server 8765\r\n'
                   "timeout /t 1 >nul\r\n"
                   f'start "" "{url}"\r\n', encoding="utf-8")


def build_slides(L, base_dir, do_embed, out):
    sessions = [{"label": ss["label"], "title": ss.get("title", ""),
                 "slides": [fill_slide(x, L, base_dir, do_embed) for x in ss["slides"]]} for ss in get_sessions(L)]
    meta = L["meta"]
    if meta.get("design", "editorial") == "editorial":
        page = (TPL / "editorial.html").read_text(encoding="utf-8")
        js = (TPL / "editorial.js").read_text(encoding="utf-8")
        has_yt = any(x.get("videoId") for ss in sessions for x in ss["slides"])
        if has_yt and meta.get("help_tab", True):
            sessions.append({"label": "영상 안내", "title": "", "slides": [dict(x) for x in HELP_SLIDES]})
            write_launchers(base_dir, out.name)
        data = {"meta": {k: meta.get(k) for k in ("title", "unit", "unit_title", "theme")}, "sessions": sessions}
        imgs = []
        data = dedupe_images(data, imgs, {})
        js = js.replace("/*__DATA_JSON__*/{}", json.dumps(data, ensure_ascii=False, indent=1))
        js = js.replace("/*__IMGS_JSON__*/[]", json.dumps(imgs))
        th = meta.get("theme") or {}
        page = (page.replace("__TITLE__", html.escape(f'{meta["unit"]}단원 {period_text(meta["periods"])} - {meta["title"]}'))
                    .replace("/*__THEME_CSS__*/", editorial_theme_css(th))
                    .replace("/*__SCRIPT__*/", js))
        out.write_text(page, encoding="utf-8")
        return
    page = (TPL / "slides.html").read_text(encoding="utf-8")
    js = (TPL / "slides.js").read_text(encoding="utf-8")
    js = js.replace("/*__SESSIONS_JSON__*/[]", json.dumps(sessions, ensure_ascii=False, indent=1))
    topbar = f'{meta["unit"]}. {meta.get("unit_title", "")} — {meta["title"]}'
    page = (page.replace("__TITLE__", html.escape(f'{meta["unit"]}단원 {period_text(meta["periods"])} - {meta["title"]}'))
                .replace("__TOPBAR__", topbar)
                .replace("/*__THEME_CSS__*/", theme_css(meta))
                .replace("/*__SCRIPT__*/", js))
    out.write_text(page, encoding="utf-8")


def ws_section(sec):
    t, title = sec["type"], sec.get("title", "")
    ref = f'<span class="page-ref">교과서 {sec["page"]}쪽</span>' if sec.get("page") else ""
    head = f"<h2>{title}{ref}</h2>" if title else ""
    if t == "write":
        body = (f'<p>{sec["prompt"]}</p>' if sec.get("prompt") else "") + '<div class="line"></div>' * sec.get("lines", 3)
    elif t == "box":
        body = (f'<p>{sec["prompt"]}</p>' if sec.get("prompt") else "") + f'<div class="box" style="height:{sec.get("height", 120)}px"></div>'
    elif t == "table":
        cols = sec["columns"]
        rows = sec.get("rows") or [""] * sec.get("blank_rows", 3)
        th = "".join(f"<th>{c}</th>" for c in cols)
        trs = "".join("<tr>" + f'<td style="height:{sec.get("row_height", 46)}px">{r}</td>' + "<td></td>" * (len(cols) - 1) + "</tr>" for r in rows)
        body = (f'<p>{sec["prompt"]}</p>' if sec.get("prompt") else "") + f"<table><tr>{th}</tr>{trs}</table>"
    elif t == "choice":
        lis = "".join(f"<li>{o}</li>" for o in sec["options"])
        body = f'<p>{sec["question"]}</p><ol class="choice">{lis}</ol>'
    else:
        body = f'<p>{sec.get("text", "")}</p>'
    return f'<div class="block">{head}{body}</div>'


def build_worksheet(L, out):
    meta, A = L["meta"], L["assessment"]
    obj = A["objectives"]
    parts = ['<div class="page">',
             f'<h1>{meta["unit"]}단원 {period_text(meta["periods"])} 활동지</h1>',
             f'<div class="sub">{meta["title"]}</div>',
             '<table class="idtable"><tr><th>학년</th><td></td><th>반</th><td></td><th>번호</th><td></td><th>이름</th><td style="width:30%"></td></tr></table>',
             '<div class="goal-box"><b>오늘의 학습 목표</b><br>']
    for d in ORDER:
        star = " ★" if d == obj["focus"] else ""
        parts.append(f'<span class="tag t-{d}">{DOMAIN[d]}</span>{obj[d]}{star}<br>')
    parts.append("</div>")
    for sec in L["worksheet"]["sections"]:
        parts.append(ws_section(sec))
    ex = A["checks"]["exit"]
    parts.append(f'<div class="block"><h2>출구표</h2><p>{ex["question"]}</p>' + '<div class="line"></div>' * 3 + "</div>")
    rows = "".join(f'<tr><td>{it}</td><td class="face">😊 잘했어요</td><td class="face">🙂 해 보는 중</td><td class="face">🌱 다음엔 더</td></tr>' for it in A["self_check"])
    parts.append(f'<div class="block self"><h2>스스로 점검해요</h2><p>나에게 맞는 칸에 ○ 하세요.</p><table>{rows}</table></div>')
    crit = "".join(f'<tr><td>{DOMAIN[c["domain"]]}</td><td>{c["student"]}<br><span class="notyet">아직이라면: {c["not_yet"]}</span></td></tr>' for c in A["success_criteria"])
    parts.append(f'<div class="block"><h2>나의 성공 기준</h2><table><tr><th style="width:14%">영역</th><th>나는 이렇게 할 수 있어요</th></tr>{crit}</table></div>')
    parts.append("</div>")
    key = L["worksheet"].get("answer_key")
    if key:
        lis = "".join(f"<li>{k}</li>" for k in key)
        parts.append(f'<div class="page key"><h1>교사용 정답·지도 참고</h1><ol>{lis}</ol></div>')
    page = (TPL / "worksheet.html").read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html.escape(f'{meta["unit"]}단원 {period_text(meta["periods"])} 활동지')).replace("__CONTENT__", "\n".join(parts))
    out.write_text(page, encoding="utf-8")


def build_plan(L, out):
    meta, C, A, F = L["meta"], L["curriculum"], L["assessment"], L["flow"]
    obj = A["objectives"]
    lines = [f'# {meta["subject"]} {meta["grade"]}학년 {meta["unit"]}단원 {period_text(meta["periods"])} 교수·학습 과정안', "",
             f'- 주제: {meta["title"]}', f'- 수업 시간: {meta["minutes"]}분 ({meta["lesson_type"]})', "", "## 성취기준", ""]
    for s in C["standards"]:
        lines.append(f'- {s["code"]} {s["official_text"]} (출처: {s["source"]}, 대조: {s["cross_check"]})')
    lines += ["", "## 학습목표", ""]
    for d in ORDER:
        lines.append(f'- **{DOMAIN[d]}**{" (중심)" if d == obj["focus"] else ""}: {obj[d]}')
    lines += ["", "## 교수·학습 과정", "", "| 단계 | 시간 | 활동 | 연결 평가 증거 | 자료 |", "|---|---|---|---|---|"]
    for st in F["steps"]:
        lines.append(f'| {st["phase"]} | {st["minutes"]}분 | {st["activity"]} | {st["evidence_link"]} | {st.get("materials", "")} |')
    lines += ["", "## 평가 계획", "", "| 영역 | 평가 방법 | 깊어지는 중 | 해내는 중 | 시작하는 중 |", "|---|---|---|---|---|"]
    for d in ORDER:
        how = ", ".join(f'{e["type"]}({e["how"]})' for e in A["evidence"] if e["domain"] == d)
        g = A["growth_levels"][d]
        lines.append(f'| {DOMAIN[d]} | {how} | {g["deepening"]} | {g["achieving"]} | {g["starting"]} |')
    h = A["checks"]["hinge"]
    lines += ["", "## 확인 질문", "", f'- 도입 진단: {A["checks"]["intro"]["question"]}', f'- 힌지 질문: {h["question"]}']
    for o in h["options"]:
        lines.append(f'  - {o["text"]} → ' + ("정답" if o.get("correct") else f'{o.get("misconception", "")} / 대응: {o.get("teacher_move", "")}'))
    lines += [f'- 출구표: {A["checks"]["exit"]["question"]}', "", "## 자료 출처", ""]
    for m in L["media"]:
        lines.append(f'- {m.get("credit") or m.get("file") or m.get("videoId")} — {m["source"]} {m.get("license", "")}')
    if F.get("teacher_note"):
        lines += ["", "## 교사 메모", "", F["teacher_note"]]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = Path(sys.argv[1]).resolve()
    do_embed = "--no-embed" not in sys.argv
    L = json.loads(src.read_text(encoding="utf-8"))
    for k in ["meta", "curriculum", "assessment", "evidence", "flow", "media", "worksheet"]:
        if k not in L:
            print(f"❌ lesson.json에 '{k}' 항목이 없습니다."); sys.exit(1)
    if not (L.get("slides") or L.get("sessions")):
        print("❌ lesson.json에 'slides' 또는 'sessions' 항목이 없습니다."); sys.exit(1)
    if L["flow"].get("approved") is not True:
        print("❌ 4단계 교사 승인(flow.approved=true) 전에는 만들 수 없습니다."); sys.exit(1)
    base = src.parent
    label = period_label(L["meta"]["periods"])
    outs = {"slides": base / f"{label}_화면용.html", "ws": base / f"{label}_활동지.html", "plan": base / f"{label}_수업안.md"}
    build_slides(L, base, do_embed, outs["slides"])
    build_worksheet(L, outs["ws"])
    build_plan(L, outs["plan"])
    for w in warnings:
        print("⚠️ ", w)
    for o in outs.values():
        print("✅", o.name, f"({o.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
