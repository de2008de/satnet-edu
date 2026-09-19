const CSS = __PLAYER_CSS__;
const COASTLINES = __COASTLINES__;
const WORDS = {
  en:{import:'Import JSON',language:'Language',play:'Play',pause:'Pause',previous:'Previous sample',next:'Next sample',start:'Beginning',time:'Recorded time',speed:'Speed',map:'The network, on a map',pacific:'Pacific-centred',greenwich:'Greenwich-centred',centre:'Map centre',satellite:'Satellite',ground:'Ground station',path:'Recorded path',links:'Other links',labels:'Labels',queries:'Recorded queries',query:'Select recorded query',result:'Current result',delay:'One-way propagation delay',distance:'Path distance',hops:'Link hops',inspect:'Object inspector',object:'Select a node or link',choose:'Choose an object',empty:'Import or drop a simulation trace to begin.',unrecorded:'Not recorded',unreachable:'No path at this sample',disabled:'Endpoint disabled at this sample',reachable:'Recorded path available',caption:'Satellite subpoints on a fixed longitude–latitude map. Select a node or link to inspect recorded data. Distances are three-dimensional.',hint:'To change the network or record another query, run Python again.',sample:'Sample',model:'Spherical Earth · discrete samples · propagation only',download:'Save JSON',credit:'Adapted from the UserGS research framework. Map: Natural Earth (public domain).',energy:'Energy: Not recorded',error:'Cannot load trace',noObject:'Choose an object on the map or from the list.',unavailable:'This link is not available at this sample.'},
  zh:{import:'导入 JSON',language:'语言',play:'播放',pause:'暂停',previous:'上一采样',next:'下一采样',start:'回到开始',time:'实际采样时间',speed:'速度',map:'地图上的卫星网络',pacific:'太平洋居中',greenwich:'格林尼治居中',centre:'地图中心',satellite:'卫星',ground:'地面站',path:'已记录路径',links:'其他链路',labels:'标签',queries:'已记录查询',query:'选择已记录查询',result:'当前结果',delay:'单向传播时延',distance:'路径距离',hops:'链路跳数',inspect:'对象检查器',object:'选择节点或链路',choose:'选择对象',empty:'导入或拖入仿真记录即可开始。',unrecorded:'未记录',unreachable:'此采样时刻无路径',disabled:'此采样时刻端点失效',reachable:'已有记录路径',caption:'固定经纬度地图上的卫星星下点。点击节点或链路查看已记录数据；距离按三维坐标计算。',hint:'修改网络或增加查询后，请重新运行 Python。',sample:'采样',model:'球形地球 · 离散采样 · 仅传播时延',download:'保存 JSON',credit:'改编自 UserGS 研究框架。地图：Natural Earth（公有领域）。',energy:'电量：未记录',error:'无法载入记录',noObject:'点击地图或使用列表选择对象。',unavailable:'此采样时刻该链路不可用。'}
};
function el(tag, attrs={}, content) {
  const e=document.createElement(tag);
  for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,v);
  if(content!==undefined) e.textContent=content;
  return e;
}
function svgEl(tag,attrs={}) {
  const e=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,v);
  return e;
}
// Display projection only. Splits lines at the current world seam.
function project(lon,lat,centre) {return [((lon-centre+540)%360+360)%360/360*1000,(90-lat)/180*500];}
function segment(a,b,centre) {
  let [x1,y1]=project(a[0],a[1],centre),[x2,y2]=project(b[0],b[1],centre);
  if(Math.abs(x2-x1)<=500) return `M${x1},${y1}L${x2},${y2}`;
  if(x1<x2){x1+=1000;const y=y2+(y1-y2)*(1000-x2)/(x1-x2);return `M${x2},${y2}L1000,${y}M0,${y}L${x1-1000},${y1}`;}
  x2+=1000;const y=y1+(y2-y1)*(1000-x1)/(x2-x1);return `M${x1},${y1}L1000,${y}M0,${y}L${x2-1000},${y2}`;
}
function createPlayer(container, options={}) {
  if(!(container instanceof Element)) throw new Error('container: expected DOM Element');
  const mount=el('div');container.append(mount);const root=mount.attachShadow({mode:'open'});
  const style=el('style',{},CSS);root.append(style);
  const shell=el('section',{class:'player','aria-label':'SatNet Edu'});root.append(shell);
  const abort=new AbortController();const listen=(e,name,fn)=>e.addEventListener(name,fn,{signal:abort.signal});
  let lang=options.language || 'en'; if(!WORDS[lang]) throw new Error('language: en or zh');
  const maxBytes=options.maxBytes ?? DEFAULT_MAX_BYTES;
  requireData(Number.isSafeInteger(maxBytes)&&maxBytes>0,'maxBytes','expected positive integer');
  let trace=null,index=0,queryId=null,selected=null,playing=false,raf=0,last=0,head=0,speed=60,dead=false,loadToken=0;
  const refs={}, localized=[];
  const trans=(tag,key,attrs={})=>{const e=el(tag,attrs);localized.push([e,key]);return e;};
  const button=(key,fn,attrs={})=>{const e=trans('button',key,{type:'button',...attrs});listen(e,'click',fn);return e;};
  const header=el('header'),titlebox=el('div');titlebox.append(el('h1',{},'SatNet Edu'));refs.name=el('div',{class:'name'});titlebox.append(refs.name);header.append(titlebox);
  const headerControls=el('div',{class:'header-controls'}),importLabel=trans('label','import',{class:'full'});
  refs.file=el('input',{type:'file',accept:'.json,application/json',class:'file'});importLabel.append(refs.file);
  const language=el('select',{'aria-label':'Language / 语言'});for(const [val,label] of [['en','English'],['zh','中文']])language.append(el('option',{value:val},label));language.value=lang;
  listen(language,'change',()=>{lang=language.value;translate();draw();});headerControls.append(importLabel,language);header.append(headerControls);shell.append(header);
  refs.error=el('p',{class:'error',role:'alert'});shell.append(refs.error);
  const toolbar=el('div',{class:'toolbar'});
  refs.play=button('play',()=>playing?pause():play(),{class:'primary','data-action':'play'});
  refs.start=button('start',()=>{pause();seek(trace.recording.start_s);},{'data-action':'start'});
  refs.prev=button('previous',()=>step(-1),{'data-action':'previous'});refs.next=button('next',()=>step(1),{'data-action':'next'});
  refs.clock=el('output',{'data-role':'clock'});
  refs.slider=el('input',{type:'range',min:'0',max:'0',step:'any',value:'0','data-role':'timeline'});listen(refs.slider,'input',()=>{pause();seek(Number(refs.slider.value));});
  const speedLabel=trans('label','speed');refs.speed=el('select',{'data-role':'speed'});for(const x of [1,10,30,60,120,300])refs.speed.append(el('option',{value:x},`${x}×`));refs.speed.value='60';listen(refs.speed,'change',()=>setSpeed(Number(refs.speed.value)));speedLabel.append(refs.speed);
  toolbar.append(refs.start,refs.prev,refs.play,refs.next,refs.clock,refs.slider,speedLabel);shell.append(toolbar);
  const grid=el('div',{class:'grid'}),mapArea=el('div',{class:'map-area'}),mapHead=el('div',{class:'map-head'});
  refs.centre=el('select',{'data-role':'centre'});refs.centre.append(trans('option','pacific',{value:'180'}),trans('option','greenwich',{value:'0'}));listen(refs.centre,'change',()=>{drawBackground();draw();});mapHead.append(trans('h2','map'),refs.centre);mapArea.append(mapHead);
  const view=el('div',{class:'view-options'});view.append(trans('span','satellite'),el('span',{},'○'),trans('span','ground'),el('span',{},'□'),trans('span','path'),el('span',{},'━'),el('span',{class:'spacer'}));
  function checkbox(key,checked){const label=el('label'),input=el('input',{type:'checkbox','data-role':key});input.checked=checked;label.append(input,trans('span',key));listen(input,'change',draw);view.append(label);return input;}
  refs.links=checkbox('links',true);refs.labels=checkbox('labels',false);mapArea.append(view);
  refs.map=svgEl('svg',{viewBox:'0 0 1000 500',class:'map',role:'group'});refs.background=svgEl('g');refs.edges=svgEl('g');refs.nodes=svgEl('g');refs.map.append(refs.background,refs.edges,refs.nodes);mapArea.append(refs.map,trans('p','caption',{class:'caption'}));
  refs.empty=trans('p','empty',{class:'empty'});mapArea.append(refs.empty);grid.append(mapArea);
  const side=el('aside',{class:'sidebar'}),querySection=el('section');querySection.append(trans('h2','queries'));const qlabel=trans('label','query',{class:'full'});refs.query=el('select',{'data-role':'query'});listen(refs.query,'change',()=>selectQuery(refs.query.value));qlabel.append(refs.query);querySection.append(qlabel,trans('p','hint',{class:'hint'}));side.append(querySection);
  const results=el('section');results.append(trans('h2','result'));refs.status=el('p',{class:'status','data-role':'status',role:'status'});results.append(refs.status);
  for(const key of ['delay','distance','hops']){const row=el('div',{class:'result'});refs[key]=el('strong',{'data-role':key},'—');row.append(trans('span',key),refs[key]);results.append(row);}
  refs.path=el('p',{class:'path','data-role':'path'});results.append(refs.path);side.append(results);
  refs.inspector=el('details');refs.inspector.open=options.showInspector===true;refs.inspector.append(trans('summary','inspect'));
  const olabel=trans('label','object',{class:'full'});refs.object=el('select',{'data-role':'object'});listen(refs.object,'change',()=>{selected=refs.object.value?JSON.parse(refs.object.value):null;inspect();});olabel.append(refs.object);
  refs.inspection=el('pre',{class:'inspection','data-role':'inspection'});refs.inspector.append(olabel,refs.inspection,trans('p','energy',{class:'hint'}));side.append(refs.inspector);grid.append(side);shell.append(grid);
  const footer=el('footer');refs.sample=el('span',{'data-role':'sample'});footer.append(refs.sample,button('download',download,{'data-action':'download'}));shell.append(footer,trans('p','credit',{class:'credit'}));
  function translate(){for(const [e,key] of localized){if(e.tagName==='LABEL'&&e.children.length){let t=e.firstChild;if(t?.nodeType===Node.TEXT_NODE)t.textContent=WORDS[lang][key];}else e.textContent=WORDS[lang][key];}shell.lang=lang;refs.file.setAttribute('aria-label',WORDS[lang].import);refs.slider.setAttribute('aria-label',WORDS[lang].time);refs.speed.setAttribute('aria-label',WORDS[lang].speed);refs.centre.setAttribute('aria-label',WORDS[lang].centre);refs.map.setAttribute('aria-label',WORDS[lang].map);refs.query.setAttribute('aria-label',WORDS[lang].query);refs.object.setAttribute('aria-label',WORDS[lang].object);refs.play.textContent=WORDS[lang][playing?'pause':'play'];}
  // Localized labels need a text node preceding their controls.
  for(const [e,key] of localized) if(e.tagName==='LABEL'&&e.children.length)e.prepend(document.createTextNode(WORDS[lang][key]));
  function guard(){if(dead)throw new Error('Player has been destroyed');}
  function fail(err){if(!dead)refs.error.textContent=`${WORDS[lang].error}: ${err.message}`;}
  function drawBackground(){const c=Number(refs.centre.value);refs.background.replaceChildren();let gridPath='';for(let lon=-180;lon<180;lon+=30){const [x]=project(lon,0,c);gridPath+=`M${x},0V500`;}for(let lat=-60;lat<=60;lat+=30){const y=(90-lat)/180*500;gridPath+=`M0,${y}H1000`;}refs.background.append(svgEl('path',{d:gridPath,class:'graticule'}));let d='';for(const ring of COASTLINES)for(let i=1;i<ring.length;i++)d+=segment(ring[i-1],ring[i],c);refs.background.append(svgEl('path',{d,class:'land',fill:'none'}));}
  function choose(type,id){selected=[type,id];refs.inspector.open=true;refs.object.value=JSON.stringify(selected);inspect();}
  function draw(){
    translate();refs.empty.hidden=Boolean(trace);for(const key of ['start','prev','next','play','slider','query'])refs[key].disabled=!trace;
    refs.edges.replaceChildren();refs.nodes.replaceChildren();
    if(!trace){refs.status.textContent=WORDS[lang].unrecorded;refs.sample.textContent=WORDS[lang].model;refs.clock.textContent='—';refs.inspection.textContent=WORDS[lang].noObject;for(const k of ['delay','distance','hops'])refs[k].textContent='—';refs.path.textContent='';return;}
    const f=trace.frames[index],objects=new Map(trace.objects.map(o=>[o.id,o])),states=new Map(f.node_states.map(n=>[n.id,n])),route=f.routes.find(r=>r.query_id===queryId),pathNodes=new Set(route?.node_ids||[]),pathLinks=new Set(route?.link_ids||[]),c=Number(refs.centre.value);
    refs.name.textContent=trace.experiment.name;refs.clock.textContent=`${f.t_s.toFixed(2)} s`;refs.slider.value=String(f.t_s);refs.prev.disabled=index===0;refs.next.disabled=index===trace.frames.length-1;refs.play.disabled=trace.frames.length===1;refs.query.disabled=!trace.recording.route_queries.length;
    refs.status.textContent=!route?WORDS[lang].unrecorded:route.status==='reachable'?WORDS[lang].reachable:WORDS[lang][route.reason==='endpoint_disabled'?'disabled':'unreachable'];
    refs.delay.textContent=route?.propagation_ms==null?'—':`${route.propagation_ms.toFixed(2)} ms`;refs.distance.textContent=route?.distance_km==null?'—':`${route.distance_km.toFixed(1)} km`;refs.hops.textContent=route?.hops==null?'—':String(route.hops);refs.path.textContent=route?.node_ids.join(' → ')||'';
    refs.sample.textContent=`${WORDS[lang].sample} ${index+1}/${trace.frames.length} · ${WORDS[lang].model} · t₀ ${trace.experiment.epoch_utc}`;
    const opts=[el('option',{value:''},WORDS[lang].choose)];
    for(const l of [...f.links].sort((a,b)=>Number(pathLinks.has(a.id))-Number(pathLinks.has(b.id)))) {
      opts.push(el('option',{value:JSON.stringify(['link',l.id])},`${l.kind.toUpperCase()} · ${l.source} ↔ ${l.target}`));
      if(!refs.links.checked&&!pathLinks.has(l.id))continue;
      const a=states.get(l.source),b=states.get(l.target),d=segment([a.lon_deg,a.lat_deg],[b.lon_deg,b.lat_deg],c),g=svgEl('g',{'data-link-id':l.id});
      g.append(svgEl('path',{d,class:`link ${l.kind}${pathLinks.has(l.id)?' selected':''}`}),svgEl('path',{d,class:'hit'}));
      g.addEventListener('click',()=>choose('link',l.id));refs.edges.append(g);
    }
    for(const n of [...f.node_states].sort((a,b)=>Number(objects.get(a.id).kind==='ground_station')-Number(objects.get(b.id).kind==='ground_station'))){
      const o=objects.get(n.id),[x,y]=project(n.lon_deg,n.lat_deg,c),g=svgEl('g',{'data-node-id':n.id});
      const shape=svgEl(o.kind==='satellite'?'circle':'rect',o.kind==='satellite'?{cx:x,cy:y,r:3.5}:{x:x-4,y:y-4,width:8,height:8});shape.setAttribute('class',`node${pathNodes.has(n.id)?' route':''}${n.enabled?'':' disabled'}`);
      const title=svgEl('title');title.textContent=`${o.label} (${n.id})`;g.append(title,shape);g.addEventListener('click',()=>choose('node',n.id));
      if(refs.labels.checked||o.kind==='ground_station'){const t=svgEl('text',{x:x>850?x-7:x+7,y:y-7,'text-anchor':x>850?'end':'start'});t.textContent=o.label.length>36?o.label.slice(0,33)+'…':o.label;g.append(t);}refs.nodes.append(g);
      opts.push(el('option',{value:JSON.stringify(['node',n.id])},`${o.kind==='satellite'?'○':'□'} ${o.label} (${n.id})`));
    }
    refs.object.replaceChildren(...opts);if(selected)refs.object.value=JSON.stringify(selected);inspect();
  }
  function inspect(){
    if(!trace||!selected){refs.inspection.textContent=WORDS[lang].noObject;return;}
    const f=trace.frames[index],[type,id]=selected;
    const data=type==='node'?f.node_states.find(n=>n.id===id):f.links.find(l=>l.id===id);
    refs.inspection.textContent=data?JSON.stringify(data,null,2):WORDS[lang].unavailable;
  }
  async function load(input){
    guard();pause();const token=++loadToken;trace=null;queryId=null;selected=null;refs.name.textContent='';refs.query.replaceChildren();draw();refs.error.textContent='';
    try {
      let data;
      if(typeof input==='string'){requireData(new TextEncoder().encode(input).length<=maxBytes,'file','size limit exceeded');data=JSON.parse(input);}
      else {const raw=JSON.stringify(input,(_k,v)=>{if(typeof v==='number'&&!Number.isFinite(v))throw new Error('non-finite value');return v;});requireData(new TextEncoder().encode(raw).length<=maxBytes,'trace','size limit exceeded');data=JSON.parse(raw);}
      validateTrace(data);if(dead||token!==loadToken)return;
      trace=data;index=0;head=data.frames[0].t_s;queryId=data.recording.route_queries[0]?.id||null;
      refs.query.replaceChildren(...data.recording.route_queries.map(q=>el('option',{value:q.id},`${q.id} · ${q.metric} · ${q.source} → ${q.target}`)));
      refs.slider.min=data.recording.start_s;refs.slider.max=data.recording.end_s;draw();
    }catch(e){fail(e);throw e;}
  }
  async function loadFile(file){if(!file)return;const token=++loadToken;try{requireData(file.size<=maxBytes,'file',`exceeds ${maxBytes} bytes`);const content=await file.text();if(!dead&&token===loadToken)await load(content);}catch(e){fail(e);}}
  function seek(seconds){guard();requireData(Number.isFinite(seconds),'seek','expected finite seconds');if(!trace)return;head=Math.max(trace.recording.start_s,Math.min(trace.recording.end_s,seconds));let lo=0,hi=trace.frames.length;while(lo<hi){const mid=(lo+hi)>>1;if(trace.frames[mid].t_s<=head)lo=mid+1;else hi=mid;}index=Math.max(0,lo-1);draw();}
  function step(delta){if(!trace)return;pause();seek(trace.frames[Math.max(0,Math.min(trace.frames.length-1,index+delta))].t_s);}
  function tick(now){if(!playing||dead)return;const elapsed=(now-last)/1000;last=now;seek(head+elapsed*speed);if(head>=trace.recording.end_s){pause();return;}raf=requestAnimationFrame(tick);}
  function play(){guard();if(!trace||trace.frames.length<2||playing)return;if(index===trace.frames.length-1)seek(trace.recording.start_s);playing=true;last=performance.now();refs.play.textContent=WORDS[lang].pause;raf=requestAnimationFrame(tick);}
  function pause(){playing=false;if(raf)cancelAnimationFrame(raf);raf=0;refs.play.textContent=WORDS[lang].play;}
  function setSpeed(value){guard();requireData(Number.isFinite(value)&&value>0,'speed','expected positive finite value');speed=value;}
  function selectQuery(id){guard();requireData(trace&&trace.recording.route_queries.some(q=>q.id===id),'query','unknown recorded query');queryId=id;refs.query.value=id;draw();}
  function download(){if(!trace)return;const url=URL.createObjectURL(new Blob([JSON.stringify(trace)],{type:'application/json'}));const a=el('a',{href:url,download:'satnet-edu-trace.json'});shell.append(a);a.click();a.remove();URL.revokeObjectURL(url);}
  listen(refs.file,'change',()=>loadFile(refs.file.files[0]));listen(shell,'dragover',e=>{e.preventDefault();shell.classList.add('drop-active');});listen(shell,'dragleave',()=>shell.classList.remove('drop-active'));listen(shell,'drop',e=>{e.preventDefault();shell.classList.remove('drop-active');loadFile(e.dataTransfer.files[0]);});
  function destroy(){if(dead)return;pause();dead=true;++loadToken;abort.abort();trace=null;mount.remove();}
  function getState(){return {loaded:Boolean(trace),playing,index,t_s:trace?.frames[index].t_s??null,queryId,speed,destroyed:dead};}
  drawBackground();translate();draw();
  return {load,play,pause,seek,setSpeed,selectQuery,destroy,getState};
}
