'use strict';
function runChecks(api, example) {
  let passed=0;
  const check=(condition,message)=>{if (!condition) throw new Error(message);passed++;};
  const copy=value=>JSON.parse(JSON.stringify(value));
  const rejects=(data,pattern)=>{
    let error;
    try { api.buildGuide(data); } catch(e) { error=e; }
    check(error && pattern.test(error.message),'Expected rejection '+pattern+', got '+error);
  };
  const outputs=api.buildGuide(example);
  check(Object.keys(outputs).length===4,'Four outputs');
  for (const text of Object.values(outputs)) check(text.includes('Credit to SOLE鞋履'),'Credit in each output');
  check(example.shoes.length===50,'Full 50-shoe fixture');
  const xmlText=svg=>[...svg.matchAll(/<text\b[^>]*>([^<]*)<\/text>/g)].map(m=>m[1]).join('');
  for (const name of ['comparison.svg','top3.svg']) {
    const text=xmlText(outputs[name]);
    for (const shoe of example.shoes) check(text.includes(shoe.brand+' '+shoe.model),'Missing model '+name+' '+shoe.model);
    check(!/NaN|undefined/.test(outputs[name]),'No undefined output');
    check(!/<script\b/i.test(outputs[name]),'No active script');
  }
  const small=copy(example);
  small.shoes=small.shoes.slice(0,2);
  small.shoes[1].brand='OtherBrand';
  small.shoes[1].sample='Women US8';
  small.shoes[1].protocol='independent-protocol';
  small.groups=[{id:small.shoes[0].group_id,name:'Cross-brand sample',basis:'Synthetic structural fixture, no real recommendation',top3:small.shoes.map(s=>({
    shoe_id:s.id,reason:'Fixture reason',tradeoff:'Fixture tradeoff',evidence_urls:s.sources.map(x=>x.url)
  }))}];
  const pair=api.buildGuide(small);
  check(pair['comparison.svg'].includes('Women US8'),'Mixed sample retained');
  check(pair['comparison.svg'].includes('independent-protocol'),'Mixed protocol retained');
  check(!pair['top3.prompt.txt'].includes('Top 3：'),'Two shoes do not fabricate a third recommendation');
  const unknown=copy(small);
  unknown.shoes[1].metrics=Object.fromEntries(Object.keys(unknown.shoes[1].metrics).map(k=>[k,null]));
  unknown.shoes[1].sample='unknown';unknown.shoes[1].protocol='unknown';unknown.shoes[1].note='No comparable lab measurements';
  check(api.buildGuide(unknown)['comparison.svg'].includes('—'),'Unknown measurements stay missing');
  const injection=copy(small);injection.title='<script>alert("x")</script> & title';
  const escaped=api.buildGuide(injection);
  check(!escaped['sources.html'].includes('<script>'),'HTML escapes untrusted text');
  check(escaped['comparison.svg'].includes('&lt;script&gt;'),'SVG escapes untrusted text');
  let bad=copy(small);bad.groups[0].top3[1].shoe_id='not-in-list';rejects(bad,/group members/);
  bad=copy(small);bad.groups[0].top3[1].shoe_id=bad.groups[0].top3[0].shoe_id;rejects(bad,/group members/);
  bad=copy(small);bad.groups[0].top3[0].evidence_urls=['https://example.org/unrelated'];rejects(bad,/Ranking evidence/);
  bad=copy(small);bad.shoes[0].metrics.drop_mm+=1;rejects(bad,/Stack\/drop/);
  bad=copy(small);delete bad.shoes[0].metrics.softness_ac;rejects(bad,/Invalid or missing metric/);
  bad=copy(small);bad.shoes[0].metrics.return_pct=Infinity;rejects(bad,/Invalid or missing metric/);
  bad=copy(small);bad.shoes[0].sample='unknown';rejects(bad,/Missing numeric evidence/);
  bad=copy(small);bad.shoes.push(copy(bad.shoes[0]));rejects(bad,/Duplicate shoe/);
  bad=copy(small);bad.groups[0].top3.pop();rejects(bad,/ranking_note/);
  bad.groups[0].ranking_note='Evidence insufficient for a second recommendation';
  check(api.buildGuide(bad)['top3.prompt.txt'].includes('Evidence insufficient'),'Incomplete ranking can be explained');
  check(api.buildGuide(example)['comparison.svg']===outputs['comparison.svg'],'Deterministic rendering');
  return {passed,fixtureShoes:example.shoes.length,fixtureGroups:example.groups.length};
}
module.exports={runChecks};
if (typeof require==='function' && require.main===module) {
  const fs=require('node:fs'),path=require('node:path');
  const api=require('./build_shoe_guide.cjs');
  if (!process.argv[2]) throw new Error('Usage: node test_shoe_guide.cjs HOKA_GUIDE_JSON');
  const example=JSON.parse(fs.readFileSync(path.resolve(process.argv[2]),'utf8'));
  console.log(JSON.stringify(runChecks(api,example)));
}
