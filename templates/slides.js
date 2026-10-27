const sessions = /*__SESSIONS_JSON__*/[];
let cur = 0;
let slides = sessions[0].slides;
let idx = 0;
const tabbar = document.getElementById('tabbar');
function renderTabs(){
  if(sessions.length < 2){ tabbar.style.display='none'; return; }
  tabbar.innerHTML = sessions.map((ss,i)=>`<button class="tab ${i===cur?'active':''}" data-i="${i}">${ss.label}${ss.title?`<span class="tab-sub">${ss.title}</span>`:''}</button>`).join('');
  tabbar.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>switchSession(+b.dataset.i)));
}
function switchSession(i){
  if(i<0||i>=sessions.length) return;
  cur=i; slides=sessions[i].slides; idx=0; renderTabs(); renderSlide();
}
const stage = document.getElementById('stage');
const counter = document.getElementById('counter');
const dotsWrap = document.getElementById('dots');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const DOMAIN = {knowledge:'지식', skill:'기능', attitude:'태도'};
const EXTS = ['png','jpg','jpeg','gif','webp'];

function renderDots(){
  dotsWrap.innerHTML = slides.map((_,i)=>`<span class="dot ${i===idx?'active':''}"></span>`).join('');
}
function pageBadge(p){ return p ? `<span class="page-badge">교과서 ${p}쪽</span>` : ''; }

function imgTag(src, alt, cls){
  if(src && /\.\*$/.test(src)){
    const base = src.slice(0,-2);
    return `<img class="${cls||''}" data-base="${base}" data-try="0" src="${base}.${EXTS[0]}" alt="${alt}" onerror="nextExt(this)">`;
  }
  return `<img class="${cls||''}" src="${src}" alt="${alt}">`;
}
function nextExt(el){
  const i = parseInt(el.dataset.try||'0',10)+1;
  if(el.dataset.base && i < EXTS.length){ el.dataset.try=i; el.src = el.dataset.base+'.'+EXTS[i]; return; }
  const box = document.createElement('div');
  box.className='ph-box';
  box.innerHTML = `🖼️ 사진 자리<br><b>${(el.dataset.base||el.getAttribute('src'))}.*</b><br>위 이름으로 images 폴더에 사진을 넣으면 자동으로 보여요.`;
  el.replaceWith(box);
}

function renderSlide(){
  const s = slides[idx];
  let html = '';
  const t = s.type;
  if(t==="title"){
    html = `<div class="center-col"><div class="kicker">${s.kicker||''}</div>
      <h1 class="big-title">${s.title}</h1><div class="sub-title">${s.sub||''}</div>
      <div style="font-size:3rem;margin-top:10px;">${s.emoji||''}</div></div>`;
  } else if(t==="goals"){
    html = `<h2 class="slide-title">${s.heading||'오늘의 학습 목표'} ${pageBadge(s.page)}</h2>
      <ul class="goal-list goal3">${s.goals.map(g=>`<li class="${g.domain===s.focus?'focus':''}">
        <span class="domain-tag ${g.domain}">${DOMAIN[g.domain]}</span>
        <span>${g.text}${g.domain===s.focus?'<span class="focus-star">★ 오늘의 중심</span>':''}</span></li>`).join('')}</ul>
      ${s.criteria?`<div class="criteria">${s.criteria.map(c=>`✅ ${c.student} <span class="notyet">— 아직이라면: ${c.not_yet}</span>`).join('<br>')}</div>`:''}`;
  } else if(t==="criteria"){
    html = `<h2 class="slide-title">${s.heading||'이렇게 할 수 있으면 성공!'}</h2>
      <ul class="goal-list goal3">${s.items.map(c=>`<li><span class="domain-tag ${c.domain}">${DOMAIN[c.domain]}</span>
        <span>✅ ${c.student}<br><span class="notyet" style="font-size:.78em;color:#3d4b57">🌱 아직이라면: ${c.not_yet}</span></span></li>`).join('')}</ul>`;
  } else if(t==="text"){
    html = `<h2 class="slide-title">${s.heading} ${pageBadge(s.page)}</h2>
      ${s.tag?`<div class="step-tag">${s.tag}</div>`:''}
      <div class="body-text" style="${s.big?'font-size:1.6rem;text-align:center;':''}">${s.body}</div>`;
  } else if(t==="cards"){
    html = `<h2 class="slide-title" style="justify-content:center;">${s.heading} ${pageBadge(s.page)}</h2>
      <div class="card-row">${s.cards.map((c,i)=>`<div class="info-card ${s.reveal?'reveal-item':''}" ${s.reveal?`style="animation-delay:${i*0.5+0.15}s"`:''}><span class="emoji">${c.emoji||''}</span><div class="label">${c.label}</div><div class="desc">${c.desc}</div></div>`).join('')}</div>`;
  } else if(t==="reveal"){
    html = `<h2 class="slide-title" style="justify-content:center;">${s.heading}</h2>
      <div class="reveal-stack">${s.items.map((x,i)=>`<div class="reveal-line reveal-item" style="animation-delay:${i*0.9+0.2}s">${x}</div>`).join('')}</div>`;
  } else if(t==="stage"){
    html = `<h2 class="slide-title">${s.heading} ${pageBadge(s.page)}</h2>
      <div class="stage-flex"><div class="stage-img-wrap">${imgTag(s.img, s.heading)}</div>
      <div class="stage-text-wrap">${s.tag?`<div class="step-tag">${s.tag}</div>`:''}<div class="body-text">${s.body}</div></div></div>`;
  } else if(t==="image"){
    html = `<h2 class="slide-title">${s.heading} ${pageBadge(s.page)}</h2>
      <div class="img-wrap">${imgTag(s.src, s.heading)}<div class="caption">${s.caption||''}</div></div>`;
  } else if(t==="fillblank"){
    html = `<h2 class="slide-title" style="justify-content:center;">${s.heading} ${pageBadge(s.page)}</h2>
      <div class="fill-blank" id="fbRow">${s.sequence.map((v,i)=>v==="?"?`<span class="blank" data-i="${i}">?</span>`:`<span>${v} ${i<s.sequence.length-1?'→':''}</span>`).join('')}</div>
      <div style="text-align:center;margin-top:18px;"><button class="nav-btn" id="fbReveal" style="background:var(--pink);">정답 확인</button></div>`;
  } else if(t==="video" && !s.videoId){
    const q = encodeURIComponent(s.search||s.heading);
    html = `<h2 class="slide-title" style="justify-content:center;">${s.heading}</h2>
      <div class="ph-box">🎬 영상 자리 — ${s.note||'수업 전에 알맞은 영상을 골라 주세요.'}<br><br>
      <a class="nav-btn" style="display:inline-block;text-decoration:none" href="https://www.youtube.com/results?search_query=${q}" target="_blank">유튜브에서 "${s.search||s.heading}" 검색</a></div>`;
  } else if(t==="video"){
    const st = s.start?`?start=${s.start}${s.end?`&end=${s.end}`:''}`:'';
    html = `<h2 class="slide-title" style="justify-content:center;">${s.heading}</h2>
      <div class="video-wrap"><iframe src="https://www.youtube.com/embed/${s.videoId}${st}" title="${s.videoTitle}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
      <div class="video-fallback">🎬 ${s.videoTitle} — 재생이 안 되면 <a href="https://www.youtube.com/watch?v=${s.videoId}" target="_blank">여기를 클릭</a>해서 열어주세요.</div>`;
  } else if(t==="activity"){
    html = `<h2 class="slide-title">${s.heading} ${pageBadge(s.page)}</h2>
      <div class="activity-box"><div class="a-title">🎯 ${s.title}</div><div class="body-text">${s.desc}</div>${s.materials?`<div class="materials">🧰 ${s.materials}</div>`:''}</div>`;
  } else if(t==="oxquiz"){
    html = `<h2 class="slide-title" style="justify-content:center;">${s.heading}</h2>
      <div class="quiz-box"><div class="quiz-q">${s.q}</div>
      <div class="ox-row"><button class="ox-btn o-btn" data-v="O">O</button><button class="ox-btn x-btn" data-v="X">X</button></div>
      <div class="reveal" id="revealText"></div></div>`;
  } else if(t==="hinge"){
    const L = ['①','②','③','④','⑤'];
    html = `<div class="hinge-wrap"><h2 class="slide-title" style="justify-content:center;">${s.heading||'생각 점검'} ${pageBadge(s.page)}</h2>
      <div class="quiz-q">${s.question}</div>
      <div class="hinge-opts">${s.options.map((o,i)=>`<button class="hinge-opt" data-i="${i}">${L[i]} ${o.text}</button>`).join('')}</div>
      <div class="reveal" id="revealText"></div>
      <div style="text-align:center;margin-top:10px;"><button class="nav-btn teacher-btn" id="teacherBtn">👩‍🏫 교사용 대응 보기</button></div>
      <div class="teacher-panel" id="teacherPanel">${s.options.map((o,i)=>o.correct?`${L[i]} 정답 — 다음 활동으로 나아가요.`:`${L[i]} ${o.misconception||''} → ${o.teacher_move||''}`).join('<br>')}</div></div>`;
  } else if(t==="write" || t==="exit"){
    html = `<h2 class="slide-title">${s.heading||(t==="exit"?'출구표':'')} ${pageBadge(s.page)}</h2>
      ${t==="exit"?'<div class="step-tag">오늘 배운 것 확인 ✍️</div>':''}
      <div class="body-text">${s.prompt}</div>
      ${t==="exit"?'<div class="video-fallback">활동지의 출구표 칸에 써 보세요.</div>':'<div class="write-line"></div><div class="write-line"></div>'}`;
  } else if(t==="self_check"){
    html = `<h2 class="slide-title">${s.heading||'스스로 점검해요'}</h2>
      ${s.items.map(it=>`<div class="self-row"><span>${it}</span><span class="self-faces"><span>😊 잘했어요</span><span>🙂 해 보는 중</span><span>🌱 다음엔 더</span></span></div>`).join('')}`;
  } else if(t==="sources"){
    html = `<h2 class="slide-title">${s.heading||'자료 출처'}</h2>
      <div class="source-list">${s.items.map(x=>`• ${x}`).join('<br>')}</div>`;
  } else if(t==="word"){
    html = `<h2 class="slide-title">${s.heading||'낱말 알기'} ${pageBadge(s.page)}</h2>
      <div class="word-card"><div style="flex:1">
        <div class="word-main">${s.word}</div>
        ${s.origin?`<div class="word-origin">${s.origin}</div>`:''}
        <div class="word-mean">💡 ${s.meaning}</div>
        ${s.example?`<div class="word-ex">🏠 예) ${s.example}</div>`:''}
      </div>${s.img?`<div class="word-img">${imgTag(s.img, s.word)}</div>`:''}</div>`;
  } else if(t==="closing"){
    html = `<div class="closing-wrap"><div class="closing-emoji">${s.emoji||'👏'}</div>
      <h1 class="big-title">${s.title}</h1><div class="sub-title">${s.sub||''}</div></div>`;
  } else {
    html = `<div class="ph-box">알 수 없는 슬라이드 종류: ${t}</div>`;
  }
  stage.innerHTML = `<div class="slide">${html}</div>`;
  counter.textContent = `${idx+1} / ${slides.length}`;
  prevBtn.disabled = idx===0;
  nextBtn.disabled = idx===slides.length-1;
  renderDots();

  if(t==="oxquiz"){
    const revealEl = document.getElementById('revealText');
    stage.querySelectorAll('.ox-btn').forEach(btn=>btn.addEventListener('click', ()=>{
      const ok = btn.dataset.v === s.answer;
      revealEl.textContent = (ok? "✅ 맞았어요! ":"🤔 다시 생각해 볼까요? ") + (s.explain||'');
      revealEl.className = "reveal " + (s.answer==="O" ? "show-o":"show-x");
    }));
  }
  if(t==="fillblank"){
    document.getElementById('fbReveal').addEventListener('click', ()=>{
      document.querySelectorAll('#fbRow .blank').forEach(el=>{
        el.textContent = s.answer[el.dataset.i]; el.style.borderStyle='solid'; el.style.color='var(--pink)';
      });
    });
  }
  if(t==="hinge"){
    const revealEl = document.getElementById('revealText');
    stage.querySelectorAll('.hinge-opt').forEach(btn=>btn.addEventListener('click', ()=>{
      const o = s.options[btn.dataset.i];
      btn.classList.add(o.correct?'is-correct':'is-rethink');
      revealEl.textContent = o.correct ? "✅ 맞았어요! " + (s.explain||'') : "🤔 다시 생각해 볼 답이에요. 교과서를 한 번 더 살펴봐요.";
    }));
    document.getElementById('teacherBtn').addEventListener('click', ()=>document.getElementById('teacherPanel').classList.toggle('show'));
  }
}

function go(delta){ idx = Math.max(0, Math.min(slides.length-1, idx+delta)); renderSlide(); }
prevBtn.addEventListener('click', ()=>go(-1));
nextBtn.addEventListener('click', ()=>go(1));
document.addEventListener('keydown', (e)=>{
  if(e.key==="ArrowRight" || e.key===" "){ e.preventDefault(); go(1); }
  if(e.key==="ArrowLeft") go(-1);
  if(/^[1-9]$/.test(e.key)) switchSession(parseInt(e.key,10)-1);
});
const fsBtn = document.getElementById('fsBtn');
fsBtn.addEventListener('click', ()=>{
  if(!document.fullscreenElement){ document.documentElement.requestFullscreen(); } else { document.exitFullscreen(); }
});
document.addEventListener('fullscreenchange', ()=>{
  document.body.classList.toggle('fs-mode', !!document.fullscreenElement);
  fsBtn.textContent = document.fullscreenElement ? "⛶ 전체화면 종료" : "⛶ 전체화면";
});
renderTabs();
renderSlide();
