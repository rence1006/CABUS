import {test} from 'node:test';
import assert from 'node:assert/strict';
import {prepareImport,mergeImport,emptyData,reconcileMilestones} from '../public/imports.js';

test('legacy duplicate task IDs preserve both records with fresh IDs',async()=>{
 const rows=[{id:2,title:'First',category:'Work',priority:'High',status:'Pending',deadline:'2026-10-28'},{id:2,title:'Second',category:'Personal',priority:'Low',status:'Completed',deadline:'2026-10-29'}];
 const preview=await prepareImport(JSON.stringify(rows),'tasks_data.json');
 assert.equal(preview.data.tasks.length,2);assert.notEqual(preview.data.tasks[0].id,preview.data.tasks[1].id);
 const merged=mergeImport(emptyData(),preview);assert.equal(merged.tasks.length,2);assert.throws(()=>mergeImport(merged,preview),/already imported/);
});
test('invalid nested values and impossible dates fail before mutation',async()=>{
 await assert.rejects(()=>prepareImport('{bad','broken.json'),/JSON/);
 await assert.rejects(()=>prepareImport(JSON.stringify({budget:{amount:50},expenses:[{description:'x',amount:-5,date:'10/28/2026',category:'Food'}]}),'expenses_data.json'),/amount/);
 await assert.rejects(()=>prepareImport(JSON.stringify([{title:'x',deadline:'2026-02-31',category:'Work',priority:'High',status:'Pending'}]),'tasks_data.json'),/date/);
});
test('web export roundtrips completed goal milestones, draft, reminders and budgets',async()=>{
 const original=emptyData();original.goals=[{id:'old',title:'Read',description:'',type:'short-term',deadline:'2026-10-28',milestones:[{text:'Book',done:true}]}];original.budgets={'2026-10':8000};original.reminders=[{id:'r',text:'Pay bill',done:false}];original.draft={title:'Session',date:'2026-10-28',startedAt:'2026-10-28T10:00:00Z',exercises:[]};
 const preview=await prepareImport(JSON.stringify({format:'cabus-backup-v1',data:original}),'backup.json');
 const merged=mergeImport(emptyData(),preview);assert.equal(merged.goals[0].milestones[0].done,true);assert.equal(merged.budgets['2026-10'],8000);assert.equal(merged.reminders[0].text,'Pay bill');assert.equal(merged.draft.title,'Session');
});

test('restored backups preserve receipt history and reject replay of an earlier legacy file',async()=>{
 const legacy=JSON.stringify([{id:2,title:'Original task',category:'Work',priority:'High',status:'Pending',deadline:'2026-10-28'}]);
 const originalPreview=await prepareImport(legacy,'tasks_data.json');
 const original=mergeImport(emptyData(),originalPreview);
 const backupPreview=await prepareImport(JSON.stringify({format:'cabus-backup-v1',data:original}),'backup.json');
 const restored=mergeImport(emptyData(),backupPreview);
 assert.equal(restored.imports.length,2);
 assert.ok(restored.imports.some(receipt=>receipt.digest===originalPreview.digest));
 assert.throws(()=>mergeImport(restored,originalPreview),/already imported/);
 const overlap=mergeImport(original,backupPreview);
 assert.equal(overlap.imports.filter(receipt=>receipt.digest===originalPreview.digest).length,1);
});

test('legacy goal descriptions are preserved through 2000 characters and oversized text is rejected',async()=>{
 const record={id:'legacy',title:'Read',description:'A'.repeat(1200),goal_type:'short-term',target_date:'2026-10-28',milestones:[]};
 const imported=await prepareImport(JSON.stringify([record]),'goals.json');
 assert.equal(imported.data.goals[0].description,record.description);
 record.description='B'.repeat(2000);
 assert.equal((await prepareImport(JSON.stringify([record]),'goals.json')).data.goals[0].description,record.description);
 record.description='C'.repeat(2001);
 await assert.rejects(()=>prepareImport(JSON.stringify([record]),'goals.json'),/description/);
});

test('malformed receipt history in backups is rejected rather than discarded',async()=>{
 const data=emptyData();data.imports=[{digest:'invalid',filename:'tasks.json',importedAt:'2026-10-28T00:00:00Z'}];
 await assert.rejects(()=>prepareImport(JSON.stringify({format:'cabus-backup-v1',data}),'backup.json'),/receipt/);
});

test('full backups support the server record limit above 1000',async()=>{
 const data=emptyData();data.tasks=Array.from({length:1001},(_,i)=>({id:`t${i}`,title:`Task ${i}`,category:'Work',priority:'Low',status:'Pending',deadline:'2026-10-28'}));
 const preview=await prepareImport(JSON.stringify({format:'cabus-backup-v1',data},null,2),'backup.json');
 assert.equal(preview.data.tasks.length,1001);
});

test('pretty backups over 450 KB load and oversized merged API payload is rejected before saving',async()=>{
 const data=emptyData();data.tasks=Array.from({length:1700},(_,i)=>({id:`t${i}`,title:'Task '+i+'x'.repeat(100),category:'Work',priority:'Low',status:'Pending',deadline:'2026-10-28'}));
 const source=JSON.stringify({format:'cabus-backup-v1',data},null,2);assert.ok(new TextEncoder().encode(source).length>450000);
 const preview=await prepareImport(source,'backup.json');assert.equal(mergeImport(emptyData(),preview).tasks.length,1700);
 const occupied=emptyData();occupied.goals=Array.from({length:200},(_,i)=>({id:`g${i}`,title:'Goal',description:'x'.repeat(2000),type:'short-term',deadline:'2026-10-28',milestones:[]}));
 assert.throws(()=>mergeImport(occupied,preview),/size|512|2,000/);
});

test('editing duplicate milestone labels preserves completion for each occurrence',()=>{
 const old=[{text:'Read',done:false},{text:'Read',done:true}];
 assert.deepEqual(reconcileMilestones('Read\nRead',old),old);
 assert.deepEqual(reconcileMilestones('Read\nRead\nRead',old),[...old,{text:'Read',done:false}]);
});

test('a full-length API milestone survives backup restore',async()=>{
 const data=emptyData();data.goals=[{id:'g',title:'Read',description:'',type:'short-term',deadline:'2026-10-28',milestones:[{text:'M'.repeat(250),done:true}]}];
 const preview=await prepareImport(JSON.stringify({format:'cabus-backup-v1',data}),'backup.json');
 assert.equal(mergeImport(emptyData(),preview).goals[0].milestones[0].text,'M'.repeat(250));
});
