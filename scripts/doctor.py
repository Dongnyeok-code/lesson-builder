"""이 환경에서 lesson-builder에 필요한 도구가 있는지 한 번에 확인한다.
사용: python3 scripts/doctor.py
없는 도구는 '없음'으로 나오고, 그 도구가 필요한 단계를 알려 준다. 새 환경(다른 컴퓨터, 안티그래비티, ChatGPT)에서 처음 한 번 실행한다."""
import importlib, shutil, subprocess

def has_mod(m):
    try:
        importlib.import_module(m); return True
    except Exception:
        return False

def node_playwright():
    if not shutil.which("node"): return False
    r = subprocess.run(["node", "-e", "require('playwright')"], capture_output=True)
    return r.returncode == 0

checks = [
    ("python3 Pillow (그림 줄이기)", has_mod("PIL"), "6단계 build.py — 없으면 그림을 원본 크기로 넣음(파일이 커짐)"),
    ("npx (kordoc 실행)", bool(shutil.which("npx")), "3단계 교과서·지도서 읽기, 8단계 hwpx"),
    ("pdftoppm / pdftotext (poppler)", bool(shutil.which("pdftoppm") and shutil.which("pdftotext")), "3단계 교과서 본문 캡처·형광펜 위치"),
    ("OpenCV (QR 읽기)", has_mod("cv2"), "3단계 교과서 QR 영상 링크 읽기 — 없으면 교사에게 링크를 받음"),
    ("node + playwright (화면 캡처)", node_playwright(), "7단계 shots.js — 없으면 화면 검사를 다른 곳에서 하거나 교사가 직접 확인"),
]
for name, ok, need in checks:
    print(("있음  " if ok else "없음  ") + name + ("" if ok else "\n      → 필요한 곳: " + need))
print("\n인터넷(유튜브·위키미디어 검색)은 이 스크립트로 확인할 수 없다. references/platforms.md 참고.")
