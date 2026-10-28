import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createAccountApi} from '../public/client-api.js';

test('data requests carry the captured account expectation on GET and PUT',async()=>{
 const calls=[];const api=createAccountApi({getSession:()=>({generation:1,accountId:'account-a'}),fetch:async(url,options)=>{calls.push(options);return Response.json({data:{},version:0});}});
 await api('data');await api('data','PUT',{data:{},version:0});
 assert.deepEqual(calls.map(c=>c.headers['X-CABUS-Account']),['account-a','account-a']);
});
test('responses after sign-out or account replacement are rejected as stale',async()=>{
 for(const accountId of [null,'account-b','account-a']){
  let session={generation:1,accountId:'account-a'},complete;
  const api=createAccountApi({getSession:()=>session,fetch:()=>new Promise(resolve=>{complete=resolve;})});
  const pending=api('data');session={generation:2,accountId};complete(Response.json({data:{private:'A'},version:1}));
  await assert.rejects(pending,error=>error.staleSession===true);
 }
});
test('account mismatch rejects and triggers sign-in recovery rather than a version reload',async()=>{
 let recovery=0;const api=createAccountApi({getSession:()=>({generation:1,accountId:'account-a'}),onAccountChanged:()=>recovery++,fetch:async()=>Response.json({error:'Account changed',code:'account_changed'},{status:409})});
 await assert.rejects(api('data','PUT',{}),error=>error.staleSession===true);assert.equal(recovery,1);
});
