import assert from 'node:assert/strict';
import {randomBytes} from 'node:crypto';

const base=process.argv[2];
if(!base?.startsWith('https://'))throw Error('Pass the deployed HTTPS URL.');
const password=randomBytes(32).toString('base64url');
const created=[];
function client(){
 let cookie='',account='';
 return async function request(path,method='GET',body,expectedAccount){
  const headers={Origin:new URL(base).origin};
  if(cookie)headers.Cookie=cookie;
  if(account&&path==='data')headers['X-CABUS-Account']=expectedAccount||account;
  if(body)headers['Content-Type']='application/json';
  const response=await fetch(base+'/api/'+path,{method,headers,body:body?JSON.stringify(body):undefined});
  const result=await response.json();
  if(response.headers.get('set-cookie'))cookie=response.headers.get('set-cookie').split(';')[0];
  if(result.user)account=result.user.id;
  return {status:response.status,body:result};
 };
}
try{
 const a=client(),b=client(),stamp=crypto.randomUUID();
 const email=`cabus-check-${stamp}@example.invalid`;
 const first=await a('register','POST',{name:'Deployment check',email,password});
 assert.equal(first.status,201,JSON.stringify(first.body));created.push(first.body.user.id);
 const original=await a('data');assert.equal(original.status,200);
 const data=original.body.data;
 data.tasks.push({id:crypto.randomUUID(),title:'Synthetic deployment check',category:'Work',priority:'Low',status:'Pending',deadline:'2026-10-28'});
 const saved=await a('data','PUT',{data,version:original.body.version});assert.equal(saved.status,200,JSON.stringify(saved.body));
 assert.equal((await a('data')).body.data.tasks.length,1);
 assert.equal((await a('data','PUT',{data,version:original.body.version})).status,409);
 assert.equal((await a('logout','POST',{})).status,200);
 const login=await a('login','POST',{email,password});assert.equal(login.status,200,JSON.stringify(login.body));
 const second=await b('register','POST',{name:'Isolation check',email:`cabus-check-b-${stamp}@example.invalid`,password});
 assert.equal(second.status,201,JSON.stringify(second.body));created.push(second.body.user.id);
 assert.equal((await b('data')).body.data.tasks.length,0);
 const mismatch=await b('data','PUT',{data,version:0},first.body.user.id);
 assert.equal(mismatch.status,409);assert.equal(mismatch.body.code,'account_changed');
 assert.equal((await b('data')).body.data.tasks.length,0);
 assert.equal((await a('data')).body.data.tasks.length,1);
 await a('logout','POST',{});await b('logout','POST',{});
 console.log('PASS: live registration, login, persistence, conflicts, account isolation and logout.');
}finally{
 console.log('Synthetic account IDs for cleanup:',JSON.stringify(created));
}
