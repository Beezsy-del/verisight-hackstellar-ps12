/* Run with Playwright installed/resolvable. Uses actual local API results. */
const {chromium}=require('playwright');
const fs=require('node:fs'); const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{
 const out=path.resolve('output/playwright'); fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:900},acceptDownloads:true});
 const page=await context.newPage(); const errors=[]; const checks=[]; const networkFailures=[];page.on('response',r=>{if(r.status()>=400)networkFailures.push({url:r.url(),status:r.status()});});
 page.on('pageerror',e=>errors.push(e.message));
 const check=async(name,fn)=>{try{await fn();checks.push({name,status:'PASS'});}catch(e){checks.push({name,status:'FAIL',error:e.message,body:(await page.locator('body').innerText()).slice(0,2000),images:await page.locator('img').evaluateAll(es=>es.map(e=>({alt:e.alt,src:e.getAttribute('src'),complete:e.complete,width:e.naturalWidth})))});console.log('FAIL',name,e.message.slice(0,220));}};
 const base=process.env.BASE_URL||'http://127.0.0.1:5174';
 const navigate=async(route)=>{await page.goto(base+route);await page.getByRole('navigation',{name:'Product navigation'}).waitFor();};
 const ready=async()=>{await page.getByRole('img',{name:'Original Evidence',exact:true}).waitFor({timeout:30000});await page.waitForFunction(()=>{const i=document.querySelector('img[alt="Original Evidence"]');return i&&i.complete&&i.naturalWidth>0;},{},{timeout:120000});};
 await check('workbench startup',async()=>{await navigate('/workbench');await ready();assert(await page.getByText('Likely misleading',{exact:true}).isVisible());});
 await check('all image channels change',async()=>{
  const sources=[];
  for(const [label,alt] of [['Original','Original Evidence'],['Compression (ELA)','Compression Analysis (Inferno Heatmap)'],['Noise (Wavelet)','Noise Consistency (Daubechies db4)'],['Clones (ORB)','Copy-Move Clones (ORB Keypoint Vectors)']]){
   await page.getByRole('button',{name:label,exact:true}).click();const img=page.getByAltText(alt,{exact:true});sources.push(await img.getAttribute('src'));await img.evaluate(e=>e.decode());assert(await img.evaluate(e=>e.complete&&e.naturalWidth>0));
  }assert.equal(new Set(sources).size,4);
  await page.getByRole('button',{name:'Split Slider',exact:true}).click();assert(await page.getByRole('slider').count());
  await page.getByRole('slider').press('ArrowRight');
  await page.getByRole('button',{name:'Dual Loupe',exact:true}).click();assert(await page.getByText('3X SYNCHRONIZED LOUPE').isVisible());
  await page.getByRole('button',{name:'Original',exact:true}).click();
 });
 await check('native zoom and fit',async()=>{
  const img=page.getByAltText('Original Evidence',{exact:true});
  await page.getByRole('button',{name:'1x',exact:true}).click();await page.waitForFunction(()=>Math.abs(document.querySelector('img[alt="Original Evidence"]').getBoundingClientRect().width-720)<2);
  await page.getByRole('button',{name:'2X',exact:true}).click();await page.waitForFunction(()=>Math.abs(document.querySelector('img[alt="Original Evidence"]').getBoundingClientRect().width-1440)<2);
  await page.getByRole('button',{name:'Zoom out',exact:true}).click();
  await page.getByRole('button',{name:'Fit',exact:true}).click();assert((await img.boundingBox()).height<800);
 });
 await check('simple forensic and dossier',async()=>{
  await page.getByRole('button',{name:'Forensic',exact:true}).click();
  await page.getByRole('button',{name:/Layer 3: Metadata/}).click();
  await page.getByRole('button',{name:/Layer 4: Heuristics/}).click();
  await page.getByRole('button',{name:'Simple',exact:true}).click();
  await page.getByRole('button',{name:'Copy complete SHA-256 hash'}).click();
 });
 await check('draft is not a subpoena',async()=>{
  await page.getByRole('button',{name:'Draft request',exact:true}).click();
  assert(await page.getByText('Evidence preservation request draft',{exact:true}).isVisible());
  assert((await page.locator('body').innerText()).includes('Not a subpoena'));
  await page.keyboard.press('Escape');
  // Modal has an explicit close button; use its observed SVG-only control if Escape is absent.
  if(await page.getByText('Evidence preservation request draft',{exact:true}).isVisible()) await page.locator('.fixed.inset-0').last().locator('button').first().click();
 });
 await check('review memo print action and scientific labels',async()=>{
  await page.getByRole('button',{name:'Review Memo',exact:true}).click();
  assert(await page.getByText('INTERNAL REVIEW — NOT CERTIFIED',{exact:true}).isVisible());
  await page.evaluate(()=>{window.__printCalled=false;window.print=()=>{window.__printCalled=true;};});
  await page.getByRole('button',{name:'Print / Save as PDF',exact:true}).click();
  assert(await page.evaluate(()=>window.__printCalled));await page.keyboard.press('Escape');
 });
 await check('mobile intake exposes a session-scoped handoff',async()=>{
  await page.getByRole('button',{name:'Mobile intake',exact:true}).click();
  assert(await page.getByText('Mobile evidence intake',{exact:true}).isVisible());
  await page.getByRole('dialog',{name:'Mobile intake'}).getByRole('button',{name:'Close mobile intake',exact:true}).click();
 });
 await check('recompression simulation uses real reanalysis',async()=>{
  await page.getByTitle('Simulate WhatsApp compression laundering',{exact:true}).click();
  await page.getByRole('button',{name:'Load Laundered Screenshot in Workbench',exact:true}).waitFor({timeout:30000});
  await page.getByRole('button',{name:'Load Laundered Screenshot in Workbench',exact:true}).click();await ready();
  assert(await page.getByAltText('Original Evidence',{exact:true}).evaluate(e=>e.naturalWidth>0));
 });
 await check('latest case wins and no stale dossier',async()=>{
  await page.keyboard.press('2');await page.keyboard.press('5');
  await page.waitForResponse(r=>r.url().includes('/analyze-sample/sample_5')&&r.status()===200,{timeout:30000}).catch(()=>{});
  await page.getByRole('button',{name:/CASE: Synthetic copy-move/}).waitFor();await ready();
  const expected=require('node:crypto').createHash('sha256').update(fs.readFileSync('samples/sample_5_cloned_chat_receipt.jpg')).digest('hex');
  await page.getByTitle(expected,{exact:true}).waitFor();
 });
 await check('upload clears old state and binds actual bytes',async()=>{
  await page.locator('input[type=file]').first().setInputFiles('samples/sample_1_synthetic_backup.png');await ready();
  await page.getByRole('button',{name:/CASE: Custom Screenshot/}).waitFor();
  const expected=require('node:crypto').createHash('sha256').update(fs.readFileSync('samples/sample_1_synthetic_backup.png')).digest('hex');
  await page.getByTitle(expected,{exact:true}).waitFor();
  await page.locator('input[type=file]').first().setInputFiles({name:'broken.png',mimeType:'image/png',buffer:Buffer.from('corrupt')});
  await page.getByRole('alert').waitFor();assert.equal(await page.getByTitle(expected,{exact:true}).count(),0);
 });
 const routes=[['overview','/'],['workbench','/workbench'],['evaluation','/evaluation'],['response','/response'],['guide','/guide']];
 for(const [width,height] of [[1440,900],[1280,800],[1024,768],[390,844]]){
  await page.setViewportSize({width,height});
  for(const [name,route] of routes) await check(`${name} ${width}x${height}`,async()=>{
   await navigate(route);if(name==='workbench'){await ready();}
   if(name==='evaluation')await page.getByText('heuristic-review-v2',{exact:true}).waitFor();
   await page.waitForTimeout(1200); // Let route entrance animations settle before visual capture.
   await page.screenshot({path:path.join(out,`local-${name}-${width}.png`)});
   const size=await page.evaluate(()=>({w:innerWidth,body:document.documentElement.scrollWidth}));assert(size.body<=size.w+1,JSON.stringify(size));
   for(const label of ['Product Overview','Forensic Workbench','Evaluation & Research','Response & Guidance','Product Guide']) assert(await page.getByRole('navigation').getByRole('button',{name:label,exact:true}).isVisible(),`Navigation hidden: ${label}`);
  });
 }
 await check('evaluation controls unavailable rather than fabricated',async()=>{await navigate('/evaluation');assert(await page.getByLabel('Evaluation dataset').isDisabled());assert(await page.getByLabel('Operating threshold').isDisabled());});
 await page.setViewportSize({width:1440,height:900});
 await check('incident extraction and complaint workflow',async()=>{
  await navigate('/response');await page.getByRole('button',{name:'Voice Assistant',exact:true}).click();
  const area=page.getByPlaceholder(/Your voice transcription/);
  await area.fill('I sold a laptop and received a suspicious receipt for INR 45000 through PhonePe. No money arrived. Reference 492019283712. Please help me prepare a draft.');
  await page.getByRole('button',{name:'Analyze Incident & Extract Facts',exact:true}).click();
  await page.getByText('RULE-BASED EXTRACTION — REVIEW FIELDS',{exact:true}).waitFor();
  fs.writeFileSync(path.join(out,'response-controls.txt'),await page.locator('body').innerText());
  await page.screenshot({path:path.join(out,'response-extraction.png')});
 });
 await check('complaint edit, PDF download and persistent case notes',async()=>{
  await page.getByRole('button',{name:'Proceed to Formal Complaint Builder',exact:true}).click();
  await page.getByRole('button',{name:'Download PDF',exact:true}).waitFor();
  await page.waitForFunction(()=>Array.from(document.querySelectorAll('button')).some(b=>b.textContent.trim()==='Download PDF'&&!b.disabled));
  const downloadPromise=page.waitForEvent('download');
  await page.getByRole('button',{name:'Download PDF',exact:true}).click();
  const download=await downloadPromise;await download.saveAs(path.join(out,'complaint-test.pdf'));
  assert(fs.readFileSync(path.join(out,'complaint-test.pdf')).subarray(0,4).toString()==='%PDF');
  await page.getByRole('button',{name:'Save Case',exact:true}).click();
  await page.getByText('Complaint Tracking',{exact:true}).first().waitFor();
  const caseControls=await page.locator('body').innerText();fs.writeFileSync(path.join(out,'case-controls.txt'),caseControls);
  // Case cards are observed from the rendered case list; select the generated title.
  const card=page.getByText(/Online Marketplace Buyer\/Seller Scam/).first();await card.click();
  const notes=page.getByPlaceholder('Record IO officer details, police station GD number, or bank chargeback communication...');
  await notes.fill('QA synthetic case: no complaint submitted. Notes persistence check.');
  await page.getByRole('button',{name:'Save Case Progress',exact:true}).click();
  await page.getByText('Case updates saved successfully.',{exact:true}).waitFor();
  await page.reload();await page.getByRole('button',{name:'Complaint Tracking',exact:true}).click();
  await page.getByText(/Online Marketplace Buyer\/Seller Scam/).first().click();
  assert.equal(await notes.inputValue(),'QA synthetic case: no complaint submitted. Notes persistence check.');
 });
 await check('microphone denied retains typing',async()=>{
  await page.getByRole('button',{name:'Voice Assistant',exact:true}).click();
  await page.evaluate(()=>{navigator.mediaDevices.getUserMedia=async()=>{throw new DOMException('Denied by browser test','NotAllowedError');};});
  await page.getByRole('button',{name:'Start Recording',exact:true}).click();
  await page.getByText('Microphone permission was denied. You can still type your statement directly.',{exact:true}).waitFor();
  assert(await page.getByPlaceholder(/Your voice transcription/).isEditable());
 });
 await check('no uncaught browser errors',async()=>assert.deepEqual(errors,[]));
 fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify({base,checks,errors,networkFailures},null,2));
 console.log(JSON.stringify({passed:checks.filter(c=>c.status==='PASS').length,failed:checks.filter(c=>c.status==='FAIL')},null,2));
 await browser.close();process.exitCode=checks.some(c=>c.status==='FAIL')?1:0;
})().catch(e=>{console.error(e);process.exitCode=1;});
