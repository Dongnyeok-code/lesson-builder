// 화면용 HTML의 모든 슬라이드를 캡처하고 넘친 슬라이드를 찾는다.
// 사용: node shots.js <화면용.html> <출력폴더>
// 결과: <출력폴더>/s{차시}_{번호}.png, overflow.txt, contact_N.png (12장씩 모아보기)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const [html, outArg] = process.argv.slice(2);
  if (!html) { console.log('사용: node shots.js <화면용.html> <출력폴더>'); process.exit(2); }
  const out = path.resolve(outArg || 'shots');
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
  await p.goto('file://' + path.resolve(html));
  await p.waitForTimeout(800);
  const counts = await p.evaluate(() => (DATA.sessions || [{ slides: DATA.slides }]).map(s => s.slides.length));
  const files = [], over = [];
  for (let si = 0; si < counts.length; si++) {
    await p.evaluate(i => sw(i), si);
    await p.waitForTimeout(300);
    for (let t = 0; t < counts[si]; t++) {
      await p.evaluate(i => { idx = i; render(); }, t);
      await p.evaluate(() => { let k = 0; while (typeof revealNext === 'function' && revealNext() && k++ < 20); });
      await p.waitForTimeout(1800); // 등장 애니메이션 끝까지 기다림
      const n = await p.evaluate(() => {
        const c = document.querySelector('#canvas'), R = c.getBoundingClientRect();
        return [...c.querySelectorAll('.slide *')].filter(e => {
          if (e.closest('iframe') || e.closest('.cover') || e.classList.contains('pno') || e.classList.contains('foot')) return false;
          const r = e.getBoundingClientRect();
          return r.width && (r.bottom > R.bottom - 30 || r.right > R.right + 2);
        }).length;
      });
      const f = path.join(out, `s${si + 1}_${String(t + 1).padStart(2, '0')}.png`);
      await (await p.$('#canvas')).screenshot({ path: f });
      files.push(f);
      if (n) over.push(`${si + 1}차시 묶음 ${t + 1}번 슬라이드: 넘친 요소 ${n}개`);
    }
  }
  fs.writeFileSync(path.join(out, 'overflow.txt'), over.join('\n') || '넘친 슬라이드 없음');
  // 모아보기
  for (let k = 0; k < files.length; k += 12) {
    const chunk = files.slice(k, k + 12);
    const cells = chunk.map(f => `<div><img src="file://${f}"><span>${path.basename(f, '.png')}</span></div>`).join('');
    await p.setViewportSize({ width: 1920, height: 1440 });
    await p.setContent(`<style>body{margin:0;display:grid;grid-template-columns:repeat(3,640px);background:#fff}
      div{position:relative;width:640px;height:360px}img{width:640px;height:360px}
      span{position:absolute;left:4px;top:2px;color:red;font:bold 14px sans-serif;background:#fff}</style>${cells}`);
    await p.waitForTimeout(500);
    await p.screenshot({ path: path.join(out, `contact_${k / 12}.png`), fullPage: true });
  }
  console.log(`캡처 ${files.length}장, 넘침 ${over.length}장 → ${out}`);
  if (over.length) console.log(over.join('\n'));
  await b.close();
})();
