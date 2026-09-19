// Shared schema is bundled at build time. Validation checks recorded data only.
const TRACE_SCHEMA = __TRACE_SCHEMA__;
const DEFAULT_MAX_BYTES = 128 * 1024 * 1024;
const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
function requireData(ok, path, message) { if (!ok) throw new Error(`${path}: ${message}`); }
function same(a,b) {
  if (a === b) return true;
  if (!a || !b || typeof a !== 'object' || typeof b !== 'object') return false;
  const keys = Object.keys(a);
  return keys.length === Object.keys(b).length && keys.every(k => own(b,k) && same(a[k],b[k]));
}
// Implements exactly the JSON Schema keywords emitted by tools/build_schemas.py.
function checkSchema(v, s, path='$') {
  if (s.$ref) return checkSchema(v,TRACE_SCHEMA.$defs[s.$ref.split('/').pop()],path);
  if (s.anyOf) {
    requireData(s.anyOf.some(option => {try {checkSchema(v,option,path);return true;} catch {return false;}}),path,'invalid value'); return;
  }
  if (own(s,'const')) requireData(v===s.const,path,`expected ${s.const}`);
  if (s.enum) requireData(s.enum.includes(v),path,'unsupported value');
  if (s.type) {
    const valid = s.type==='null' ? v===null : s.type==='array' ? Array.isArray(v) : s.type==='object' ? v!==null && typeof v==='object' && !Array.isArray(v) : s.type==='integer' ? Number.isSafeInteger(v) : typeof v===s.type;
    requireData(valid,path,`expected ${s.type}`);
  }
  if (typeof v==='number') {
    requireData(Number.isFinite(v),path,'expected finite number');
    if (own(s,'minimum')) requireData(v>=s.minimum,path,`minimum ${s.minimum}`);
    if (own(s,'maximum')) requireData(v<=s.maximum,path,`maximum ${s.maximum}`);
    if (own(s,'exclusiveMinimum')) requireData(v>s.exclusiveMinimum,path,`must exceed ${s.exclusiveMinimum}`);
  }
  if (typeof v==='string') {
    if (s.minLength) requireData(v.length>=s.minLength,path,'string too short');
    if (s.maxLength) requireData([...v].length<=s.maxLength,path,'string too long');
  }
  if (Array.isArray(v)) {
    if (s.minItems) requireData(v.length>=s.minItems,path,'array too short');
    if (s.maxItems) requireData(v.length<=s.maxItems,path,'array too long');
    if (s.items) v.forEach((x,i)=>checkSchema(x,s.items,`${path}[${i}]`));
  } else if (v && typeof v==='object') {
    for (const k of s.required || []) requireData(own(v,k),path,`missing ${k}`);
    for (const k of Object.keys(v)) {
      if (s.properties && own(s.properties,k)) checkSchema(v[k],s.properties[k],`${path}.${k}`);
      else if (s.additionalProperties===false) throw new Error(`${path}: unknown field ${k}`);
      else if (s.additionalProperties && typeof s.additionalProperties==='object') checkSchema(v[k],s.additionalProperties,`${path}.${k}`);
    }
  }
}
function indexBy(list,key,path) {
  const map=new Map();
  for (const x of list) {requireData(!map.has(x[key]),path,`duplicate ${x[key]}`);map.set(x[key],x);}
  return map;
}
function near(a,b,path) { requireData(a!==null && Math.abs(a-b)<=Math.max(1e-6,1e-9*Math.max(Math.abs(a),Math.abs(b))),path,'recorded metric mismatch'); }
function validateTrace(data) {
  requireData(data?.format==='satnet-edu.trace' && data.schema_version==='1.0.0','$','supported format satnet-edu.trace version 1.0.0');
  checkSchema(data,TRACE_SCHEMA);
  const s=data.experiment.scenario, r=data.recording, objects=indexBy(data.objects,'id','objects'), queries=indexBy(r.route_queries,'id','queries');
  const scenarioObjects=indexBy(s.objects,'id','scenario.objects'), shells=indexBy(s.constellations,'id','constellations'), slots=new Set();
  requireData(/(?:Z|\+00:00)$/.test(s.epoch_utc) && Number.isFinite(Date.parse(s.epoch_utc)) && +s.epoch_utc.slice(0,4)>=1957 && +s.epoch_utc.slice(0,4)<=2056,'epoch_utc','expected UTC, year 1957–2056');
  for (const k of ['epoch_utc','name','seed']) requireData(s[k]===data.experiment[k],`experiment.${k}`,'scenario mismatch');
  requireData(same(s.link_policy,data.model.link_policy),'model.link_policy','scenario mismatch');
  requireData(objects.size===scenarioObjects.size && objects.size<=s.limits.max_nodes,'objects','count mismatch/limit');
  for (const [id,o] of objects) {
    requireData(same(o,scenarioObjects.get(id)),`objects.${id}`,'scenario mismatch');
    const fields=o.kind==='satellite'?['tle','orbit']:['lat_deg','lon_deg'];
    requireData(fields.every(k=>own(o,k)),`objects.${id}`,'missing object definition');
    const forbidden=o.kind==='satellite'?['lat_deg','lon_deg']:['tle','orbit','constellation_id','plane','slot'];
    requireData(forbidden.every(k=>!own(o,k)),`objects.${id}`,'incompatible fields');
    if (own(o,'constellation_id')) {
      const c=shells.get(o.constellation_id), key=JSON.stringify([o.constellation_id,o.plane,o.slot]);
      requireData(c && own(o,'plane') && own(o,'slot') && o.plane<c.planes && o.slot<c.sats_per_plane && !slots.has(key),`objects.${id}`,'invalid/duplicate slot'); slots.add(key);
    } else requireData(!own(o,'plane') && !own(o,'slot'),`objects.${id}`,'slot needs constellation');
  }
  for (const [id,c] of shells) requireData(s.objects.filter(o=>o.constellation_id===id).length===c.planes*c.sats_per_plane,`constellations.${id}`,'missing slots');
  requireData(r.capabilities.routes===Boolean(queries.size),'capabilities.routes','query mismatch');
  for (const q of queries.values()) requireData(objects.has(q.source)&&objects.has(q.target),'queries','unknown endpoint');
  requireData(r.end_s>=r.start_s,'recording','reversed interval');
  const count=Math.floor((r.end_s-r.start_s)/r.step_s);
  requireData(count+1<=s.limits.max_samples,'recording','sample limit exceeded');
  const times=new Set([r.start_s,r.end_s]);
  for (let i=1;i<=count;i++) if(r.start_s+i*r.step_s<r.end_s) times.add(r.start_s+i*r.step_s);
  const events=[];
  for (const f of s.failures) {
    requireData(objects.has(f.node_id)&&f.end_s>f.start_s,'failures','invalid interval/node');
    for (const [k,kind] of [['start_s','failure_start'],['end_s','failure_end']]) if(f[k]>=r.start_s&&f[k]<=r.end_s) {times.add(f[k]);events.push([f[k],f.node_id,kind]);}
  }
  requireData(times.size<=s.limits.max_samples && data.frames.length===r.sample_count && same(data.frames.map(f=>f.t_s),[...times].sort((a,b)=>a-b)),'frames.t_s','sample grid mismatch');
  requireData(same(events.map(JSON.stringify).sort(),data.events.map(e=>JSON.stringify([e.t_s,e.node_id,e.kind])).sort()),'events','scheduled event mismatch');
  data.frames.forEach((f,i)=>{
    const p=`frames[${i}]`, states=indexBy(f.node_states,'id',p), links=indexBy(f.links,'id',p), routes=indexBy(f.routes,'query_id',p), pairs=new Set();
    requireData(states.size===objects.size&&[...states.keys()].every(k=>objects.has(k)),p,'missing/unknown node state');
    requireData(routes.size===queries.size&&[...routes.keys()].every(k=>queries.has(k)),p,'missing/unknown query result');
    for (const [id,state] of states) {
      const scheduled=s.failures.some(fault=>fault.node_id===id&&fault.start_s<=f.t_s&&f.t_s<fault.end_s);
      requireData(state.enabled!==scheduled,p,'scheduled failure state mismatch');
    }
    for (const l of links.values()) {
      requireData(states.has(l.source)&&states.has(l.target)&&l.source!==l.target,p,'unknown endpoint/self loop');
      const pair=JSON.stringify([l.source,l.target].sort());requireData(!pairs.has(pair),p,'duplicate pair');pairs.add(pair);
      requireData(states.get(l.source).enabled&&states.get(l.target).enabled,p,'disabled link endpoint');
      const ground=[l.source,l.target].filter(k=>objects.get(k).kind==='ground_station').length;
      requireData(ground===(l.kind==='gsl'?1:0),p,'invalid link kind');near(l.propagation_ms,l.distance_km/data.model.c_km_s*1000,p);
    }
    for (const [qid,route] of routes) {
      const q=queries.get(qid), nodes=route.node_ids, lids=route.link_ids, disabled=!states.get(q.source).enabled||!states.get(q.target).enabled;
      if(route.status==='unreachable') {
        requireData(!nodes.length&&!lids.length&&['hops','distance_km','propagation_ms'].every(k=>route[k]===null),p,'unreachable needs empty path and null metrics');
        requireData(route.reason===(disabled?'endpoint_disabled':'no_path'),p,'invalid reason');continue;
      }
      requireData(!disabled&&route.reason===null&&nodes.length>0&&nodes[0]===q.source&&nodes.at(-1)===q.target&&new Set(nodes).size===nodes.length,p,'invalid path endpoints/cycle');
      requireData(lids.length===nodes.length-1&&route.hops===lids.length,p,'hop mismatch');
      requireData(nodes.every(n=>states.has(n)&&states.get(n).enabled),p,'unknown/disabled path node');
      requireData(nodes.slice(1,-1).every(n=>objects.get(n).kind==='satellite'),p,'GS cannot relay');
      lids.forEach((id,j)=>{const l=links.get(id);requireData(l&&((l.source===nodes[j]&&l.target===nodes[j+1])||(l.target===nodes[j]&&l.source===nodes[j+1])),p,'missing/mismatched path edge');});
      near(route.distance_km,lids.reduce((a,id)=>a+links.get(id).distance_km,0),p);
      near(route.propagation_ms,lids.reduce((a,id)=>a+links.get(id).propagation_ms,0),p);
    }
  });
  return data;
}
