// Controlled visual comparison: real local analysis replayed to BOTH UIs for layout only.
// Never describes this replay as deployed inference or an accuracy test.
const {chromium}=require('playwright');const fs=require('node:fs');
(async()=>{
 const b=await chromium.launch({channel:'chrome',headless:true});const c=await b.newContext({viewport:{width:1440,height:900}});
 const real=await (await c.request.post('http://127.0.0.1:5174/api/analyze-sample/sample_clean')).json();
 // Add backward-compatible field aliases; no finding or numerical value is changed.
 real.layer2.lasers.forEach(x=>x.is_alignment_outlier=x.is_tampered);
 real.synergy.region_overlap_found=real.synergy.synergy_multiplier_applied;
 real.synergy.primary_review_locus=real.synergy.primary_forgery_locus;
 const notes=[];
 for(const [name,origin] of [['local','http://127.0.0.1:5174'],['deployed','https://verisight-ps12.vercel.app']]){
  const p=await c.newPage();p.setDefaultTimeout(20000);
  for(const [route,label] of [['/','overview'],['/workbench','workbench'],['/evaluation','evaluation'],['/response','response'],['/','guide']]){
   try{
    await p.goto(origin+route);await p.getByRole('button',{name:'Forensic Workbench',exact:true}).waitFor();
    if(label==='workbench'){
     await p.locator('img[alt="Original Evidence"]').waitFor({timeout:45000});
     await p.screenshot({path:`output/playwright/${name}-live-workbench.png`});
     await p.route('**/api/analyze',r=>r.fulfill({json:real}));
     await p.locator('input[type=file]').first().setInputFiles('samples/sample_1_synthetic_backup.png');
     await p.getByTitle(real.file_sha256,{exact:true}).waitFor();
     await p.getByRole('button',{name:'Original',exact:true}).click();
     await p.getByRole('button',{name:'Simple',exact:true}).click();
     await p.getByRole('button',{name:'Fit',exact:true}).click();
    }
    if(label==='guide'){
     if(name==='local') await p.getByRole('button',{name:'Product Guide',exact:true}).click();
     else {await p.getByRole('button',{name:'Forensic Workbench',exact:true}).click();await p.getByRole('button',{name:'Product Guide',exact:true}).click();}
    }
    // Wait for fonts and finite entrance transitions; do not speed up analysis.
    await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(700);
    await p.screenshot({path:`output/playwright/compare-${name}-${label}.png`});
    notes.push({name,label,status:'captured',controlled_analysis:label==='workbench'});
   }catch(e){notes.push({name,label,status:'failed',error:e.message});}
  }await p.close();
 }
 fs.writeFileSync('output/playwright/comparison-results.json',JSON.stringify({sha256:real.file_sha256,method:'Same viewport, actual local result replayed for workbench layout ONLY; separate live captures preserved. Other pages use their own real API.',notes},null,2));
 await b.close();console.log(notes);
})().catch(e=>{console.error(e);process.exitCode=1;});
