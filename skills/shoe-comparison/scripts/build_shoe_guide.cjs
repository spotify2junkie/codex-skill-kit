#!/usr/bin/env node
'use strict';

/** Dependency-free, deterministic shoe-guide SVG renderer. Node.js 18+. */
const CREDIT = 'Credit to SOLE鞋履';
const CREDIT_NOTE = '参数决策卡与表达方式的灵感来源；本次数据核验与推荐独立整理。';
const KEYS = ['weight_g','softness_ac','shock_sa','return_pct','forefoot_mm','heel_mm','drop_mm'];
const LIMITS = [[1,3000],[0,100],[0,500],[0,100],[0,200],[0,200],[-50,50]];
const W = 1900, M = 64;
const COLOR = {bg:'#0d1416',white:'#edf3f1',muted:'#a8bbbd',cyan:'#50cddd',orange:'#ffad5b'};
const LEGEND = [
  'AC 越低，泡棉越软；SA 越高，同条件冲击衰减能力越强。',
  '回弹是实验能量回馈比例，不等于舒适或跑步效率；不同用途不设总冠军。',
  '厚度顺序：前掌 / 后跟；坡差 = 后跟 − 前掌；— 表示暂无同口径实测。'
];
function fail(message) { throw new Error(message); }
function requireText(obj, keys) {
  for (const key of keys) if (typeof obj[key] !== 'string' || !obj[key].trim()) fail('Missing text: '+key);
}
function httpUrl(value) {
  if (typeof value !== 'string' || !/^https?:\/\/[^\s/?#]+(?:[/?#]|$)/.test(value)) fail('Invalid source URL');
}
function validateGuide(data) {
  requireText(data,['title','date','scope','selection_note']);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(data.date) || !Number.isFinite(Date.parse(data.date))) fail('Invalid date');
  if (!Array.isArray(data.shoes) || !data.shoes.length || !Array.isArray(data.groups) || !data.groups.length) fail('Provide shoes and groups');
  const shoes = new Map(), groups = new Map(), names = new Set();
  for (const group of data.groups) {
    requireText(group,['id','name','basis']);
    if (groups.has(group.id)) fail('Duplicate group id');
    groups.set(group.id,group);
  }
  for (const shoe of data.shoes) {
    requireText(shoe,['id','brand','model','group_id','sample','protocol']);
    const name = shoe.brand+'\0'+shoe.model;
    if (shoes.has(shoe.id) || names.has(name)) fail('Duplicate shoe id or model/variant');
    if (!groups.has(shoe.group_id)) fail('Unknown group');
    if (!shoe.metrics || typeof shoe.metrics !== 'object') fail('Missing metrics');
    const values = KEYS.map(key=>shoe.metrics[key]);
    for (let i=0;i<values.length;i++) {
      const value = values[i], [low,high] = LIMITS[i];
      if (value !== null && (typeof value !== 'number' || !Number.isFinite(value) || value<low || value>high)) fail('Invalid or missing metric: '+KEYS[i]);
    }
    const hasData = values.some(value=>value !== null);
    const sources = shoe.sources || [];
    if (!Array.isArray(sources)) fail('sources must be an array');
    for (const source of sources) { requireText(source,['label','url']); httpUrl(source.url); }
    if (hasData && (!sources.length || shoe.sample==='unknown' || shoe.protocol==='unknown')) fail('Missing numeric evidence or sample/protocol');
    if (!hasData) requireText(shoe,['note']);
    const m = shoe.metrics;
    if ([m.heel_mm,m.forefoot_mm,m.drop_mm].every(value=>value !== null) &&
        Math.abs(m.heel_mm-m.forefoot_mm-m.drop_mm)>0.201) fail('Stack/drop discrepancy: '+shoe.model);
    shoes.set(shoe.id,shoe); names.add(name);
  }
  for (const group of data.groups) {
    const count = data.shoes.filter(shoe=>shoe.group_id===group.id).length;
    if (!count || !Array.isArray(group.top3)) fail('Empty group or missing top3');
    if (group.top3.length>Math.min(3,count)) fail('Too many Top 3 entries');
    if (group.top3.length<Math.min(3,count)) requireText(group,['ranking_note']);
    const seen = new Set();
    for (const pick of group.top3) {
      requireText(pick,['shoe_id','reason','tradeoff']);
      const shoe = shoes.get(pick.shoe_id);
      if (!shoe || shoe.group_id!==group.id || seen.has(pick.shoe_id)) fail('Top 3 must reference distinct group members');
      const allowed = new Set((shoe.sources||[]).map(source=>source.url));
      if (!Array.isArray(pick.evidence_urls) || !pick.evidence_urls.length ||
          pick.evidence_urls.some(url=>!allowed.has(url))) fail('Ranking evidence must appear in shoe sources');
      seen.add(pick.shoe_id);
    }
  }
  if (data.method_url) httpUrl(data.method_url);
  if (data.notes && (!Array.isArray(data.notes) || data.notes.some(n=>typeof n!=='string'))) fail('Invalid notes');
  return shoes;
}
function escapeXml(value) {
  return String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function label(shoe) { return shoe.brand+' '+shoe.model; }
function members(data,group) { return data.shoes.filter(shoe=>shoe.group_id===group.id); }
function blocks(shoes) {
  const result = new Map();
  for (const shoe of shoes) {
    const key = JSON.stringify([shoe.sample,shoe.protocol]);
    if (!result.has(key)) result.set(key,{sample:shoe.sample,protocol:shoe.protocol,shoes:[]});
    result.get(key).shoes.push(shoe);
  }
  return [...result.values()];
}
function format(value,decimals=1) { return value===null ? '—' : value.toFixed(decimals); }
function values(shoe) {
  const m=shoe.metrics;
  return [label(shoe),format(m.weight_g,0),format(m.softness_ac),format(m.shock_sa,0),
    format(m.return_pct),format(m.forefoot_mm)+' / '+format(m.heel_mm),format(m.drop_mm)];
}
class Canvas {
  constructor() { this.ops=[]; }
  lines(text,width,size) {
    const result=[];
    // Conservative width budgeting: CJK 1.10em; ASCII 0.72em, wide Latin 1.0em.
    for (const paragraph of String(text).split('\n')) {
      let line='', used=0;
      for (const ch of paragraph) {
        const advance=size*(/[\u0000-\u007f]/.test(ch) ? (/[MW@%]/.test(ch) ? 1 : 0.72) : 1.10);
        if (line && used+advance>width) { result.push(line); line=''; used=0; }
        line+=ch; used+=advance;
      }
      result.push(line);
    }
    return result;
  }
  height(text,width,size) { return this.lines(text,width,size).length*(size+14); }
  text(text,x,y,width,size=28,color=COLOR.white) {
    for (const line of this.lines(text,width,size)) {
      this.ops.push('<text x="'+x+'" y="'+(y+size)+'" font-size="'+size+'" fill="'+color+'">'+escapeXml(line)+'</text>');
      y+=size+14;
    }
    return y;
  }
  rect(x,y,width,height,fill) {
    this.ops.push('<rect x="'+x+'" y="'+y+'" width="'+width+'" height="'+height+'" fill="'+fill+'"/>');
  }
  svg(height,title) {
    if (height>60000) fail('Image too tall; split into numbered sections retaining every shoe');
    return '<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+Math.ceil(height)+'" viewBox="0 0 '+W+' '+Math.ceil(height)+'" role="img"><title>'+escapeXml(title)+'</title><rect width="100%" height="100%" fill="'+COLOR.bg+'"/><g font-family="Noto Sans CJK SC, Noto Sans SC, Microsoft YaHei, PingFang SC, Arial, sans-serif">'+this.ops.join('')+'</g></svg>\n';
  }
}
function header(canvas,data,subtitle) {
  let y=canvas.text(data.title,M,42,W-2*M,58);
  y=canvas.text(data.shoes.length+' 款 · '+subtitle,M,y+8,W-2*M,42,COLOR.cyan);
  y=canvas.text(data.selection_note,M,y+12,W-2*M,26,COLOR.orange);
  return canvas.text('核验：'+data.date+' · '+data.scope,M,y+6,W-2*M,24,COLOR.muted)+28;
}
function footer(canvas,data,y) {
  canvas.rect(M,y,W-2*M,2,'#36555a');
  y=canvas.text(CREDIT,M,y+24,W-2*M,30,COLOR.orange);
  y=canvas.text(CREDIT_NOTE,M,y+4,W-2*M,23,COLOR.muted);
  return canvas.text('原始数据、逐款来源和推荐依据见 sources.html；核验：'+data.date,M,y+6,W-2*M,23,COLOR.muted)+36;
}
function comparisonSvg(data) {
  const c=new Canvas();
  let y=header(c,data,'完整鞋款参数对照');
  const widths=[592,160,160,160,180,310,210], x=[M];
  for (const width of widths) x.push(x[x.length-1]+width);
  const indices=new Map(data.shoes.map((shoe,i)=>[shoe.id,i+1]));
  const headers=['鞋款 / 用途','重量 g','泡棉 AC','吸震 SA','回弹 %','前掌/后跟 mm','坡差 mm'];
  for (const group of data.groups) {
    y=c.text(group.name,M,y+22,W-2*M,35,COLOR.orange)+10;
    for (const block of blocks(members(data,group))) {
      y=c.text('本块口径：'+block.sample+' / '+block.protocol,M,y,W-2*M,22,COLOR.muted)+8;
      const hh=Math.max(...headers.map((h,i)=>c.height(h,widths[i]-24,23)))+20;
      c.rect(M,y,W-2*M,hh,'#21363a');
      headers.forEach((h,i)=>c.text(h,x[i]+12,y+10,widths[i]-24,23,COLOR.muted));
      y+=hh;
      block.shoes.forEach((shoe,i)=>{
        const row=values(shoe), title=String(indices.get(shoe.id)).padStart(2,'0')+'  '+row[0], detail=shoe.use||'';
        const rowHeight=Math.max(100,c.height(title,widths[0]-26,30)+(detail ? c.height(detail,widths[0]-26,22):0)+32);
        c.rect(M,y,W-2*M,rowHeight,i%2 ? '#121d20':'#1b272a');
        const yy=c.text(title,M+13,y+12,widths[0]-26,30,COLOR.cyan);
        if (detail) c.text(detail,M+13,yy+4,widths[0]-26,22,COLOR.muted);
        row.slice(1).forEach((value,j)=>c.text(value,x[j+1]+12,y+rowHeight/2-22,widths[j+1]-24,30,j===5?COLOR.orange:COLOR.white));
        y+=rowHeight+2;
      });
    }
  }
  y+=24;
  for (const note of [...LEGEND,...(data.notes||[])]) y=c.text(note,M,y+4,W-2*M,24,COLOR.muted);
  return c.svg(footer(c,data,y+24),data.title+' 完整参数对照');
}
function top3Svg(data,shoes) {
  const c=new Canvas();
  let y=header(c,data,'我的分组推荐 TOP 3');
  y=c.text('组内推荐顺序；不是销量榜。先看首选，再看理由和取舍。',M,y,W-2*M,28,COLOR.orange)+22;
  const gap=28, cw=(W-2*M-gap)/2;
  for (let first=0;first<data.groups.length;first+=2) {
    const bottoms=[];
    data.groups.slice(first,first+2).forEach((group,col)=>{
      const x=M+col*(cw+gap), inner=cw-44, start=c.ops.length;
      let yy=c.text(group.name,x+22,y+20,inner,36,COLOR.orange);
      yy=c.text(group.basis,x+22,yy+7,inner,25,COLOR.muted)+20;
      group.top3.forEach((pick,i)=>{
        const color=i===0?COLOR.orange:(i===1?COLOR.white:COLOR.cyan);
        yy=c.text((i+1)+(i===0?' 首选  ':' 备选  ')+label(shoes.get(pick.shoe_id)),x+22,yy,inner,34,color);
        yy=c.text('推荐：'+pick.reason,x+22,yy+4,inner,26);
        yy=c.text('取舍：'+pick.tradeoff,x+22,yy+3,inner,25,COLOR.muted)+22;
      });
      const chosen=new Set(group.top3.map(p=>p.shoe_id));
      const others=members(data,group).filter(s=>!chosen.has(s.id)).map(label);
      if (others.length) {
        yy=c.text('其他备选（未排序）',x+22,yy,inner,25,COLOR.cyan);
        yy=c.text(others.join(' / '),x+22,yy+5,inner,23)+12;
      }
      if (group.ranking_note) yy=c.text(group.ranking_note,x+22,yy+3,inner,24,COLOR.orange)+12;
      const bottom=yy+18;
      c.ops.splice(start,0,'<rect x="'+x+'" y="'+y+'" width="'+cw+'" height="'+(bottom-y)+'" fill="#182528"/>');
      bottoms.push(bottom);
    });
    y=Math.max(...bottoms)+gap;
  }
  return c.svg(footer(c,data,y+12),data.title+' 分组 Top 3');
}
function promptText(data,shoes) {
  const lines=[
    'Create a high-resolution portrait Chinese shoe recommendation poster.',
    'Charcoal background; cyan model names; orange #1 首选; white #2; cyan #3. Readable typography before decoration.',
    'This is a qualitative editorial guide. Do not add lab values, prices, scores, sales claims, health promises or endorsements.',
    '主标题：'+data.title+' · '+data.shoes.length+' 款',
    '副标题：我的分组推荐 TOP 3',
    '说明：基于资料的选购判断；不是销量榜，不是跨用途总榜。',
    '范围：'+data.selection_note,'核验日期：'+data.date,
    'Keep exact model names, categories and rank order. Include every shoe. Expand canvas as needed; do not silently omit entries.'
  ];
  for (const group of data.groups) {
    lines.push('','分组：'+group.name,'排序依据：'+group.basis);
    group.top3.forEach((pick,i)=>lines.push('Top '+(i+1)+(i===0?' 首选':'')+'：'+label(shoes.get(pick.shoe_id)),'推荐：'+pick.reason,'取舍：'+pick.tradeoff));
    const chosen=new Set(group.top3.map(p=>p.shoe_id));
    const others=members(data,group).filter(s=>!chosen.has(s.id)).map(label);
    if (others.length) lines.push('其他备选（未排序）：'+others.join(' / '));
    if (group.ranking_note) lines.push('条件说明：'+group.ranking_note);
  }
  lines.push('','Footer, visibly readable: '+CREDIT,CREDIT_NOTE,
    '原始数据与推荐依据见配套来源页。Credit 不是数据来源，也不是本次排名作者。',
    'If shoe illustrations are used, mark 鞋图为示意. Avoid implying an exact product photo.',
    'Before finalizing, verify all supplied model names and all group rank orders, no duplicates or substitutions.');
  return lines.join('\n')+'\n';
}
function sourcesHtml(data,shoes) {
  const e=escapeXml;
  const out=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(data.title)+'</title>',
    '<style>body{background:#0d1416;color:#edf3f1;font:17px/1.7 system-ui,sans-serif;max-width:1500px;margin:auto;padding:30px}h1,h2,h3{color:#ffad5b}a{color:#50cddd}table{border-collapse:collapse;min-width:1050px;width:100%}td,th{padding:13px;border-bottom:1px solid #34494b;text-align:left}tr:nth-child(even){background:#192325}.scroll{overflow:auto}small{display:block;color:#a8bbbd}.credit{border:1px solid #ffad5b;padding:18px}li{margin:10px 0}</style>',
    '<h1>'+e(data.title)+'</h1><p>'+e(data.selection_note)+'</p><p>核验：'+e(data.date)+' · '+e(data.scope)+'</p>',
    '<p class="credit"><strong>'+CREDIT+'</strong><br>'+CREDIT_NOTE+'</p>'];
  const headers=['鞋款','重量 g','泡棉 AC','后跟吸震 SA','后跟回弹 %','前掌/后跟 mm','坡差 mm'];
  for (const group of data.groups) {
    out.push('<h2>'+e(group.name)+'</h2><p>推荐标准：'+e(group.basis)+'</p><ol>');
    for (const pick of group.top3) {
      const links=pick.evidence_urls.map((url,i)=>'<a href="'+e(url)+'">依据 '+(i+1)+'</a>').join(' / ');
      out.push('<li><strong>'+e(label(shoes.get(pick.shoe_id)))+'</strong>：'+e(pick.reason)+'；取舍：'+e(pick.tradeoff)+'。 '+links+'</li>');
    }
    out.push('</ol>');
    if (group.ranking_note) out.push('<p>'+e(group.ranking_note)+'</p>');
    for (const block of blocks(members(data,group))) {
      out.push('<h3>'+e(block.sample+' / '+block.protocol)+'</h3><div class="scroll"><table><thead><tr>'+headers.map(h=>'<th>'+e(h)+'</th>').join('')+'</tr></thead><tbody>');
      for (const shoe of block.shoes) out.push('<tr>'+values(shoe).map(v=>'<td>'+e(v)+'</td>').join('')+'</tr>');
      out.push('</tbody></table></div>');
    }
  }
  out.push('<h2>逐款来源与口径</h2><ol>');
  for (const shoe of data.shoes) {
    const links=(shoe.sources||[]).map(s=>'<a href="'+e(s.url)+'">'+e(s.label)+'</a>').join(' / ');
    const detail=[shoe.use,shoe.tradeoff,shoe.note].filter(Boolean).join('；');
    out.push('<li>'+e(label(shoe))+' — '+(links||'暂无原始实测')+'<small>'+e(shoe.sample+' / '+shoe.protocol+'；'+detail)+'</small></li>');
  }
  out.push('</ol><h2>读图说明</h2><ul>'+[...LEGEND,...(data.notes||[])].map(n=>'<li>'+e(n)+'</li>').join('')+'</ul>',
    '<p>名次为本次选购判断，不等于销量、来源方排名或医疗效果。</p>');
  if (data.method_url) out.push('<a href="'+e(data.method_url)+'">测试方法</a>');
  return out.join('')+'</html>\n';
}
function buildGuide(data) {
  const shoes=validateGuide(data);
  return {'comparison.svg':comparisonSvg(data),'top3.svg':top3Svg(data,shoes),
    'sources.html':sourcesHtml(data,shoes),'top3.prompt.txt':promptText(data,shoes)};
}
module.exports={validateGuide,buildGuide,CREDIT};
if (typeof require==='function' && require.main===module) {
  const fs=require('node:fs'),path=require('node:path'),args=process.argv.slice(2);
  if (args.length!==2) { console.error('Usage: node build_shoe_guide.cjs guide.json OUTPUT_DIRECTORY'); process.exitCode=2; }
  else {
    const data=JSON.parse(fs.readFileSync(args[0],'utf8'));
    const files=buildGuide(data);
    fs.mkdirSync(args[1],{recursive:true});
    for (const [name,content] of Object.entries(files)) fs.writeFileSync(path.join(args[1],name),content,'utf8');
    console.log(JSON.stringify({shoes:data.shoes.length,groups:data.groups.length,images:['comparison.svg','top3.svg'],credit:CREDIT}));
  }
}
