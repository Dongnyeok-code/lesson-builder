# 작업 환경과 도구 사용법

MVP 테스트(6학년 실과 10·11차시)에서 실제로 확인한 내용이다. 환경이 바뀌면 이 문서를 고친다.

## 어디서 무엇이 되나

| 하려는 일 | 되는 곳 | 안 되는 곳 |
|---|---|---|
| 교사 폴더(`~/수업`) 읽기·쓰기, build.py·check.py 실행, kordoc | 교사 컴퓨터 셸(device bash) | — |
| 인터넷 접속(유튜브, 위키미디어) | **내장 브라우저**(Claude_Browser)의 JavaScript `fetch` | 클라우드 셸·교사 컴퓨터 셸 모두 막힘 (curl, yt-dlp, WebFetch의 youtube) |
| 화면 캡처 검사(Playwright) | 클라우드 셸 | 교사 컴퓨터 셸(설치 안 됨) |

## 파일 옮기기

- 교사 컴퓨터 → 클라우드: `device_stage_files`로 올린다. 올라간 경로는 한글 정규화 때문에 그대로 쓰면 못 찾을 수 있으니 `find /mnt/user-data/uploads -name "*.html"`로 찾는다.
- 클라우드 → 교사 컴퓨터: `/mnt/user-data/outputs/` 아래에 두고 `device_commit_files`로 보낸다.
- 큰 파일을 출력(base64)으로 옮기지 않는다. 느리고 잘린다.

## 교사 컴퓨터 셸 주의

- 한글 경로는 macOS 방식(NFD)으로 저장돼 있어서, **명령에 직접 쓴 한글(NFC)과 글자가 달라 못 찾는다.** `ls "$HOME/mnt/수업/"`도, `find -name "10_11차시_build"`도 실패할 수 있다.
  → 한글을 쓰지 않는 패턴으로 찾는다: `find "$HOME"/mnt/ -type d -name "*_build"`, `ls -d "$HOME"/mnt/*/*/lesson-builder`. 찾은 경로는 변수에 담아 쓴다.
- 파일 삭제가 막혀 있다 → `PYTHONDONTWRITEBYTECODE=1`로 캐시를 만들지 않는다. 지울 일이 있으면 교사에게 허락을 받는다.
- `/tmp` 쓰기가 막힐 수 있다 → `mktemp -d` 또는 `$HOME` 아래를 쓴다.

## 유튜브

1. 내장 브라우저로 `https://www.youtube.com/results?search_query=<검색어>`를 연다.
2. JavaScript로 `ytd-video-renderer`에서 제목·채널·길이·videoId를 읽는다.
3. 고른 영상은 `fetch('https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<ID>&format=json')`가 200이면 임베드 가능.
4. 교사가 준 링크는 watch 페이지를 열고 `meta[itemprop=duration]`(예: PT3M44S)로 길이를 확인한다.

## 위키미디어 공용 그림

1. 내장 브라우저로 `https://commons.wikimedia.org`를 연다.
2. 검색: `/w/api.php?action=query&generator=search&gsrsearch=<영어 검색어>&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=700&format=json`
   → 파일 이름, `LicenseShortName`, `Artist`를 읽는다. 라이선스가 공공영역·CC BY·CC BY-SA인 것만 쓴다.
3. 후보를 캔버스로 이어 붙인 미리보기 한 장(dataURL)을 받아 **눈으로 확인한 뒤** 고른다.
4. 고른 그림을 dataURL로 받아 클라우드에서 jpg로 풀고, `device_commit_files`로 `images/web/`에 넣는다.
5. `media`에 `source`(파일 이름·저자), `license`, `credit`을 적는다. 자료 출처 슬라이드에 자동으로 나온다.

## 화면 캡처 검사

```
node scripts/shots.js <화면용.html> <출력폴더>
```
- 차시·슬라이드마다 PNG, 넘친 슬라이드 목록(`overflow.txt`), 12장씩 모은 `contact_N.png`를 만든다.
- 모아보기를 Read로 열어 직접 본다. 넘침 0개여도 글씨가 작거나 그림이 작은 장은 고친다.

## 교과서 QR 참고 영상 (아이스크림)

- QR 링크(`http://xcms.kr/...`)는 `https://qr.i-scream.co.kr/v.do?cno=...` 영상 페이지로 넘어간다. 내장 브라우저에서 두 사이트를 허용해야 열린다.
- 영상 내용 확인: 페이지의 `<video>`를 시점별로 캔버스에 그려 6장 모아 보기 → 제목·길이를 기록한다.
- 이 페이지는 X-Frame-Options가 없어 슬라이드에 `embedUrl`로 그대로 넣을 수 있다 (mp4 주소는 시간이 지나면 만료되므로 쓰지 않는다).

## 브라우저 결과로 그림 옮기기 (크기 제한)

- 내장 브라우저 JavaScript 결과는 약 26만 자에서 잘린다. 그림은 **한 번에 하나씩**, 가로 700~800px · JPEG 0.7~0.8로 줄여 dataURL로 받는다 (그림 하나 20만 자 이하).
- 먼저 `window._w`에 모두 받아 두고, 크기를 확인한 다음 하나씩 꺼내면 다시 내려받지 않아도 된다.
- 컴퓨터 연결이 끊기면(잠자기 등) 클라우드에서 할 수 있는 일(슬라이드 초안 작성)을 먼저 하고, 연결이 돌아오면 이어서 한다.

## 유튜브 오류 153 (영상 플레이어 구성 오류)

- 원인: HTML을 더블클릭해 `file://`로 열면 브라우저가 Referer(어느 사이트인지)를 보내지 않아 유튜브가 화면 안 재생을 막는다.
- 템플릿 대응: iframe에 `referrerpolicy="strict-origin-when-cross-origin"`, `file://`일 때는 썸네일 + '유튜브에서 보기' 버튼.
- 교사 안내: 자동으로 생기는 '영상 안내' 탭 + `수업자료_열기.command/.bat`(로컬 서버 `http://localhost:8765`로 열기). 영구 해결은 GitHub Pages·Vercel 등에 올려 https 주소로 열기.
- 출판사(아이스크림) QR 영상은 file://에서도 재생된다.
- 화면 캡처 검사(shots.js)는 슬라이드로 바로 이동하고 단계 공개(누르면 나오는 것)를 모두 연 상태로 찍는다.
