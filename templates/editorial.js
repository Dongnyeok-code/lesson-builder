const DATA = /*__DATA_JSON__*/{};
const IMGS = /*__IMGS_JSON__*/[];
(function fixImgs(o){ for(const k in o){ const v=o[k];
  if(typeof v==='string' && v.startsWith('@img:')) o[k]=IMGS[+v.slice(5)];
  else if(v && typeof v==='object') fixImgs(v); } })(DATA);
const sessions = DATA.sessions, META = DATA.meta;
const ACC = ['blue','green','pink','yellow'];
const DOM = {knowledge:['지식','blue'], skill:['기능','green'], attitude:['태도','pink']};
const BGS = {blue:'sky', green:'mint', pink:'pink', yellow:'cream'};
const EXTS = ['png','jpg','jpeg','gif','webp'];
const concepts = (META.theme && META.theme.concepts) || {};
let cur = 0, idx = 0;
const canvas = document.getElementById('canvas');

function strip(t){ return String(t==null?'':t).replace(/\p{Extended_Pictographic}|️|‍/gu,'').replace(/[ \t]{2,}/g,' ').trim(); }
function plain(t){ return strip(t).replace(/<br\s*\/?>/gi,' '); }
function accentOf(s, i){
  if (s.accent) return s.accent;
  const key = plain(s.word||s.heading||s.title||'');
  for (const k in concepts) if (key.includes(k)) return concepts[k];
  return ACC[(i||0)%ACC.length];
}
function foot(s){ if(!s.page) return ''; const p=String(s.page); return /^\d/.test(p)?`교과서 ${p}쪽`:p; }
function img(src, alt){
  if(!src) return '';
  if(/\.\*$/.test(src)){ const b=src.slice(0,-2); return `<img data-base="${b}" data-try="0" src="${b}.png" alt="${alt||''}" onerror="nextExt(this)">`; }
  return `<img src="${src}" alt="${alt||''}">`;
}
function nextExt(el){
  const i=+(el.dataset.try||0)+1;
  if(el.dataset.base && i<EXTS.length){ el.dataset.try=i; el.src=el.dataset.base+'.'+EXTS[i]; return; }
  const d=document.createElement('div'); d.className='ph'; d.textContent=`그림 자리: ${(el.dataset.base||el.getAttribute('src'))} (images 폴더에 넣으면 보여요)`; el.replaceWith(d);
}
function parseChars(origin){
  const out=[]; const re=/([^·()]+?)\s*[(（]([㐀-鿿]+)[)）]/g; let m;
  while((m=re.exec(origin||''))) out.push({rd:m[1].trim(), ch:m[2]});
  return out;
}
function frame(s, bg, acc, inner){
  const n = String(idx+1).padStart(2,'0');
  const kick = `${META.unit_title||''} · ${sessions[cur].label}`;
  return `<div class="slide bg-${bg}"><div class="topbar b-${acc}"></div><div class="kicker">${kick}</div>${inner}
    <div class="foot">${foot(s)}</div><div class="pno">${n}</div></div>`;
}
function pill(text, acc){ return text?`<div class="pill b-${acc}">${strip(text)}</div>`:''; }

function render(){
  const list = sessions[cur].slides, s = list[idx], t = s.type, acc = accentOf(s, idx);
  let h='';
  if(t==='title'){
    const cov = s.img || (list.find(x=>x.type==='image')||{}).src;
    h = `<div class="slide" style="padding:0"><div class="cover"><div class="l"><div class="ck">${strip(s.kicker)}</div>
      <h1>${strip(s.title)}</h1><div class="sub">${strip(s.lead||META.title||'')}</div><div class="pg">${strip(s.sub)}</div></div>
      <div class="r">${img(cov,'')}</div></div></div>`;
  } else if(t==='goals'){
    h = frame(s,'cream','blue',`<h2 class="t">${strip(s.heading||'오늘의 학습 목표')}</h2><div class="body"><ol class="numlist">${
      s.goals.map((g,i)=>`<li><span class="n c-${DOM[g.domain][1]}">${i+1}</span><span><span class="tagline b-${DOM[g.domain][1]}">${DOM[g.domain][0]}${g.domain===s.focus?' · 중심':''}</span>${strip(g.text)}</span></li>`).join('')}</ol></div>${pill(s.pill,'navy')}`);
  } else if(t==='criteria'){
    h = frame(s,'cream','green',`<h2 class="t">${strip(s.heading||'이렇게 할 수 있으면 성공')}</h2><div class="body"><div class="cols crit" style="grid-template-columns:repeat(${s.items.length},1fr)">${
      s.items.map(c=>`<div class="col c-${DOM[c.domain][1]}"><h3>${DOM[c.domain][0]}</h3><div class="d">${strip(c.student)}</div><div class="s">아직이라면 · ${strip(c.not_yet)}</div></div>`).join('')}</div></div>`);
  } else if(t==='word'){
    const chars = parseChars(s.origin), han = chars.map(c=>c.ch).join('');
    const left = han ? `<div class="hanja c-${acc}">${han}</div><div class="wkor">${strip(s.word)}</div>`
                     : `<div class="hanja c-${acc}" style="font-size:132px">${strip(s.word)}</div><div class="wkor" style="font-size:35px;color:var(--muted)">${strip(s.origin||'')}</div>`;
    h = frame(s,BGS[acc]||'cream',acc,`<div class="word"><div>${left}<div class="wrule b-${acc}"></div><div class="wmean">${strip(s.meaning)}</div></div>
      <div class="chars">${chars.map(c=>`<div><div class="ch c-${acc}">${c.ch} ${c.rd.split(' ').pop()}</div><div class="rd">${c.rd}</div></div>`).join('')}
      ${s.example?`<div class="wex">예) ${strip(s.example)}</div>`:''}</div></div>`);
  } else if(t==='cards'){
    const n=s.cards.length, hasImg=s.cards.some(c=>c.img);
    h = frame(s,s.bg||'white',acc,`<h2 class="t">${strip(s.heading)}</h2><div class="body"><div class="cols" style="grid-template-columns:repeat(${n},1fr)">${
      s.cards.map((c,i)=>{const a=accentOf({heading:c.label},i);return `<div class="col c-${a}">${hasImg?`<div class="cimg">${c.img?img(c.img,c.label):''}</div>`:''}<h3>${strip(c.label)}</h3>${s.list?`<div class="lis">${strip(c.desc).split(/<br\s*\/?>/i).filter(x=>x.trim()).map((x,k)=>`<div class="li"><b>${k+1}</b><span>${x}</span></div>`).join('')}</div>`:`<div class="d">${strip(c.desc)}</div>`}</div>`}).join('')}</div></div>${pill(s.pill,acc)}`);
  } else if(t==='reveal'){
    h = frame(s,'navy','yellow',`<h2 class="t">${strip(s.heading)}</h2><div class="body"><ol class="numlist" style="align-self:center;max-width:1250px">${
      s.items.map((x,i)=>`<li style="color:#fff;opacity:0;animation:fi .5s ease ${i*0.9+0.2}s forwards"><span class="n" style="color:var(--yellow)">${i+1}</span><span>${strip(x)}</span></li>`).join('')}</ol></div>`);
  } else if(t==='text'){
    h = frame(s,s.bg||'cream',acc,`${s.tag?`<div class="c-${acc}" style="font-size:28px;font-weight:700;margin-top:10px">${strip(s.tag)}</div>`:''}<h2 class="t" style="margin-top:${s.tag?6:18}px">${strip(s.heading)}</h2>
      <div class="body"><div style="font-size:52px;line-height:1.6;max-width:1300px">${strip(s.body)}</div></div>${pill(s.pill,acc)}`);
  } else if(t==='image' || t==='stage'){
    const side = s.points ? `<div class="side">${s.points.map((p,i)=>`<p><b class="c-${ACC[i%4]}">${i+1}</b>  ${strip(p)}</p>`).join('')}</div>`
               : (t==='stage' ? `<div class="side ${s.big?'big':''}">${s.tag?`<div class="c-${acc}" style="font-size:35px;font-weight:700">${strip(s.tag)}</div>`:''}${s.hide?`<button class="revealbtn showans" style="align-self:flex-start;margin-top:10px">${strip(s.hide_label||'예시 답안 보기')}</button><p class="step hidans">${strip(s.body)}</p>`:`<p>${strip(s.body)}</p>`}</div>` : '');
    h = frame(s,'white',acc,`<h2 class="t">${strip(s.heading)}</h2><div class="imgrow"><div class="imgbox ${side?'':'full'}">${img(s.src||s.img,s.heading)}<div class="cap">${strip(s.caption||'')}</div></div>${side}</div>`);
  } else if(t==='section'){
    h = frame(s,'navy','yellow',`<div class="body sec"><div class="sk">${strip(s.kicker||'다음에 살펴볼 내용')}</div><div class="st1">${strip(s.title)}</div>${s.sub?`<div class="ss">${strip(s.sub)}</div>`:''}${s.items?`<ol class="si">${s.items.map(x=>`<li>${strip(x)}</li>`).join('')}</ol>`:''}</div>`);
  } else if(t==='textbook'){
    const hl=(s.highlights||[]).map((b,k)=>`<span class="mk" style="left:${b.x}%;top:${b.y}%;width:${b.w}%;height:${b.h}%;animation-delay:${0.3+k*0.28}s"></span>`).join('');
    const st=(s.stars||[]).map((b,k)=>`<svg class="star" viewBox="0 0 100 100" style="left:${b.x}%;top:${b.y}%;animation-delay:${0.2+k*0.28}s"><path d="M50 6 L61 38 L95 38 L67 58 L78 92 L50 71 L22 92 L33 58 L5 38 L39 38 Z" filter="url(#crayon)"/></svg>`).join('');
    h = frame(s,'white','yellow',`<div class="c-pink" style="font-size:30px;font-weight:700;margin-top:6px">${strip(s.tag||'교과서 함께 읽기')}</div><h2 class="t" style="margin-top:4px">${strip(s.heading)}</h2><div class="tbk"><div class="tbin">${img(s.src,'교과서 본문')}${hl}${st}</div></div>`);
  } else if(t==='compare'){
    const dots=(side)=>s.rows.map((r,k)=>{const p=r[side+'pos']; return p?`<span class="dot c-${r.color||ACC[k%4]}" data-k="${k}" style="left:${p.x}%;top:${p.y}%"></span>`:''}).join('');
    h = frame(s,'white','blue',`<h2 class="t">${strip(s.heading)}</h2><div class="cmp"><div class="cimgw">${img(s.left,'')}${dots('l')}<div class="clab">${strip(s.left_label||'')}</div></div>
      <div class="crows">${s.rows.map((r,k)=>`<div class="crow step" data-k="${k}"><span class="chip b-${r.color||ACC[k%4]}">${strip(r.l)}</span><span class="cd">${strip(r.desc)}</span><span class="chip b-${r.color||ACC[k%4]}">${strip(r.r)}</span></div>`).join('')}
      <div class="chint">화면을 누르면 하나씩 나와요</div></div>
      <div class="cimgw">${img(s.right,'')}${dots('r')}<div class="clab">${strip(s.right_label||'')}</div></div></div>`);
  } else if(t==='fillblank'){
    h = frame(s,'cream',acc,`<h2 class="t">${strip(s.heading)}</h2><div class="body"><div class="seq" id="seq">${
      s.sequence.map((v,i)=>`${i?'<span class="ar">→</span>':''}${s.imgs?`<div class="sq">${s.imgs[i]?img(s.imgs[i],''):''}`:''}<span class="it ${String(v).includes('?')?'bl':''}" data-i="${i}">${strip(v)}</span>${s.imgs?'</div>':''}`).join('')}</div>
      <button class="revealbtn" id="rv">정답 확인</button></div>`);
  } else if(t==='video'){
    const m=(s.videoTitle||'').match(/\(([^,()]+),\s*([\d:]+)\)\s*$/);
    const title=(s.videoTitle||'').replace(/\s*\([^()]*\)\s*$/,'');
    const src = s.videoId ? `https://www.youtube.com/embed/${s.videoId}` : (s.embedUrl||'');
    const open = s.videoId ? `https://www.youtube.com/watch?v=${s.videoId}` : (s.openUrl||s.embedUrl||'');
    const fileMode = location.protocol==='file:' && s.videoId;
    const inner = fileMode ? `<a class="vframe vthumb" href="${open}" target="_blank"><img src="https://i.ytimg.com/vi/${s.videoId}/hqdefault.jpg" alt=""><span class="vplay">▶ 유튜브에서 보기</span><span class="vnote">파일로 열면 유튜브가 화면 안 재생을 막아요(오류 153). '영상 안내' 탭을 보세요.</span></a>`
      : src ? `<div class="vframe"><iframe src="${src}" title="${title}" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>`
      : `<div class="ph">영상 자리 — ${strip(s.note||'')}</div>`;
    h = frame(s,'navy','yellow',`<h2 class="t" style="text-align:left">${strip(s.heading)}</h2><div class="vid"><div class="vmeta"><div class="dur">${m?m[2]:''}</div>
      <div class="vt">${strip(title)}</div><div class="ch">${m?m[1]:''}</div>${open?`<a href="${open}" target="_blank">${s.videoId?'재생이 안 되면 유튜브에서 열기':'재생이 안 되면 새 창에서 열기'}</a>`:''}</div>${inner}</div>`);
  } else if(t==='activity'){
    const steps = strip(s.desc).split(/<br\s*\/?>/i).filter(x=>x.trim());
    h = frame(s,'cream',acc,`<div class="c-${acc}" style="font-size:28px;font-weight:700;margin-top:10px">${strip(s.heading)}</div><h2 class="t" style="margin-top:6px">${strip(s.title)}</h2>
      <div class="body"><div class="steps">${steps.map(x=>`<div class="st">${x}</div>`).join('')}</div>${s.materials?`<div class="mat">준비물 · ${strip(s.materials)}</div>`:''}</div>`);
  } else if(t==='oxquiz'){
    h = frame(s,'sky','blue',`<h2 class="t">${strip(s.heading)}</h2><div class="body qbox"><div class="q">${strip(s.q)}</div>
      <div class="ox"><button class="o" data-v="O">O</button><button class="x" data-v="X">X</button></div><div class="ans" id="ans"></div></div>`);
  } else if(t==='hinge'){
    const L=['①','②','③','④','⑤'];
    h = frame(s,'pink','pink',`<h2 class="t">${strip(s.heading||'생각 점검')}</h2><div class="q" style="font-size:47px;margin-top:24px">${strip(s.question)}</div>
      <div class="opts">${s.options.map((o,i)=>`<button data-i="${i}">${L[i]}  ${strip(o.text)}</button>`).join('')}</div><div class="ans" id="ans" style="text-align:center"></div>
      <button class="tbtn" id="tb">선생님 지도 팁</button><div class="tpanel" id="tp">${s.options.map((o,i)=>o.correct?`${L[i]} 정답`:`${L[i]} ${strip(o.misconception||'')} → ${strip(o.teacher_move||'')}`).join('<br>')}</div>`);
  } else if(t==='write'||t==='exit'){
    h = frame(s,'cream','navy',`<div class="c-blue" style="font-size:28px;font-weight:700;margin-top:10px">${t==='exit'?'출구표 · 활동지에 써요':''}</div><h2 class="t" style="margin-top:6px">${strip(s.heading||'오늘 배운 것 확인')}</h2>
      <div class="body"><div style="font-size:50px;line-height:1.55">${strip(s.prompt)}</div><div class="line"></div><div class="line"></div></div>`);
  } else if(t==='self_check'){
    h = frame(s,'cream','green',`<h2 class="t">${strip(s.heading||'스스로 점검해요')}</h2><div class="body">${
      s.items.map(x=>`<div class="selfrow"><span>${strip(x)}</span><span class="sc">잘했어요 · 해 보는 중 · 다음엔 더</span></div>`).join('')}</div>`);
  } else if(t==='sources'){
    h = frame(s,'white','navy',`<h2 class="t">${strip(s.heading||'자료 출처')}</h2><div class="body"><div class="src ${s.items.length>24?'dense':''}">${s.items.map(strip).join('<br>')}</div></div>`);
  } else if(t==='closing'){
    h = frame(s,'navy','yellow',`<div class="body" style="align-items:center;text-align:center"><div style="font-size:35px;color:var(--yellow);font-weight:700">오늘의 핵심</div>
      <div style="font-size:76px;font-weight:700;margin-top:24px">${strip(s.title)}</div><div style="font-size:40px;color:#cfdbe6;margin-top:24px">${strip(s.sub||'')}</div></div>`);
  } else {
    h = frame(s,'cream','navy',`<div class="ph">알 수 없는 슬라이드: ${t}</div>`);
  }
  canvas.innerHTML = h;
  document.getElementById('counter').textContent = `${idx+1} / ${list.length}`;
  document.getElementById('pos').textContent = `${sessions[cur].label}  ${idx+1} / ${list.length}`;
  wire(s);
}
function revealNext(){
  const st=canvas.querySelector('.step:not(.on)'); if(!st) return false;
  st.classList.add('on');
  if(st.dataset.k!==undefined) canvas.querySelectorAll(`.dot[data-k="${st.dataset.k}"]`).forEach(d=>d.classList.add('on'));
  if(st.classList.contains('hidans')){ const b=canvas.querySelector('.showans'); if(b) b.style.display='none'; }
  return true;
}
function wire(s){
  const sa=canvas.querySelector('.showans'); if(sa) sa.onclick=e=>{e.stopPropagation(); revealNext();};
  if(s.type==='compare') canvas.querySelector('.cmp').onclick=()=>revealNext();
  if(s.type==='oxquiz') canvas.querySelectorAll('.ox button').forEach(b=>b.onclick=()=>{
    const ok=b.dataset.v===s.answer; const a=document.getElementById('ans');
    a.textContent=(ok?'맞았어요. ':'다시 생각해 볼까요? ')+strip(s.explain||''); a.style.color=ok?'var(--green)':'var(--blue)'; });
  if(s.type==='fillblank') document.getElementById('rv').onclick=()=>canvas.querySelectorAll('#seq .bl').forEach(e=>{e.textContent=strip(s.answer[e.dataset.i]);e.classList.remove('bl');e.style.borderColor='var(--pink)';e.style.color='var(--pink)';});
  if(s.type==='hinge'){
    canvas.querySelectorAll('.opts button').forEach(b=>b.onclick=()=>{const o=s.options[b.dataset.i]; b.classList.add(o.correct?'ok':'re');
      document.getElementById('ans').textContent=o.correct?('맞았어요. '+strip(s.explain||'')):'다시 생각해 볼 답이에요. 교과서를 한 번 더 살펴봐요.';});
    document.getElementById('tb').onclick=()=>document.getElementById('tp').classList.toggle('show');
    document.getElementById('tp').onclick=()=>document.getElementById('tp').classList.remove('show');
  }
}
function fit(){
  const v=document.getElementById('viewport'); const k=Math.min(v.clientWidth/1600, v.clientHeight/900);
  canvas.style.transform=`scale(${k})`;
}
function tabs(){
  const el=document.getElementById('tabs');
  if(sessions.length<2){el.innerHTML='';return;}
  el.innerHTML=sessions.map((x,i)=>`<button class="tab ${i===cur?'active':''}" data-i="${i}">${x.label}${x.title?' · '+strip(x.title):''}</button>`).join('');
  el.querySelectorAll('.tab').forEach(b=>b.onclick=()=>sw(+b.dataset.i));
}
function sw(i){ if(i<0||i>=sessions.length) return; cur=i; idx=0; tabs(); render(); }
function go(d){ if(d>0 && revealNext()) return; const n=sessions[cur].slides.length; idx=Math.max(0,Math.min(n-1,idx+d)); render(); }
document.getElementById('prevBtn').onclick=()=>go(-1);
document.getElementById('nextBtn').onclick=()=>go(1);
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();go(1);}
  if(e.key==='ArrowLeft'||e.key==='PageUp') go(-1);
  if(/^[1-9]$/.test(e.key)) sw(+e.key-1);
});
const fsBtn=document.getElementById('fsBtn');
fsBtn.onclick=()=>{ if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); };
document.addEventListener('fullscreenchange',()=>{ document.body.classList.toggle('fs',!!document.fullscreenElement); fsBtn.textContent=document.fullscreenElement?'전체화면 종료':'전체화면'; setTimeout(fit,50); });
window.addEventListener('resize',fit);
tabs(); render(); fit();
