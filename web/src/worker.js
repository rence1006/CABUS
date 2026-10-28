import {pbkdf2,scrypt,randomBytes,timingSafeEqual} from 'node:crypto';
import {emptyData,validateData} from './validation.js';
const ITERATIONS=600000,SESSION_SECONDS=7*24*60*60,MAX_BODY=524288;
const now=()=>Math.floor(Date.now()/1000);
const random=()=>randomBytes(32).toString('base64url');
const digest=async value=>Buffer.from(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value))).toString('hex');
const derive=(password,salt,iterations)=>new Promise((resolve,reject)=>pbkdf2(password,salt,iterations,32,'sha256',(err,key)=>err?reject(err):resolve(key)));
// OWASP's 16 MiB scrypt profile avoids Workers' PBKDF2 iteration cap.
const deriveScrypt=(password,salt)=>new Promise((resolve,reject)=>scrypt(password,salt,32,{N:16384,r:8,p:5,maxmem:32*1024*1024},(err,key)=>err?reject(err):resolve(key)));
async function hashPassword(password){const salt=random();return `scrypt$16384$8$5$${salt}$${(await deriveScrypt(password,salt)).toString('hex')}`;}
async function checkPassword(password,stored){let key,hash;if(stored.startsWith('scrypt$')){const parts=stored.split('$');if(parts.length!==6||parts[1]!=='16384'||parts[2]!=='8'||parts[3]!=='5')return false;hash=parts[5];key=await deriveScrypt(password,parts[4]);}else{const [,count,salt,legacyHash]=stored.split('$');hash=legacyHash;key=await derive(password,salt,Number(count));}const expected=Buffer.from(hash,'hex');return key.length===expected.length&&timingSafeEqual(key,expected);}
class Failure extends Error{constructor(status,message){super(message);this.status=status;}}
function fail(status,message){throw new Failure(status,message);}
function passwordValid(value){if(typeof value!=='string'||value.length<12||value.length>128)fail(400,'Use a password of 12 to 128 characters.');}
function emailValue(value){if(typeof value!=='string'||value.length>254||!/^\S+@[^\s@]+\.[^\s@]+$/.test(value.trim()))fail(400,'Enter a valid email address.');return value.trim().toLowerCase();}
function publicUser(row){return {id:row.id,name:row.name,email:row.email};}
function isLocal(request,env){const host=new URL(request.url).hostname;return env.DEVELOPMENT==='true'&&['localhost','127.0.0.1','[::1]'].includes(host);}
function cookie(request,env,token='',expired=false){return `cabus_session=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${expired?0:SESSION_SECONDS}${isLocal(request,env)?'':'; Secure'}`;}
function response(body,status=200,headers={}){return new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...headers}});}
async function body(request){if(!request.headers.get('content-type')?.startsWith('application/json'))fail(415,'Send JSON data.');if(Number(request.headers.get('content-length'))>MAX_BODY)fail(413,'This request is too large.');const reader=request.body?.getReader();if(!reader)fail(400,'Request data is required.');let total=0,chunks=[];while(true){const {done,value}=await reader.read();if(done)break;total+=value.byteLength;if(total>MAX_BODY){await reader.cancel();fail(413,'This request is too large.');}chunks.push(value);}const bytes=new Uint8Array(total);let pos=0;for(const chunk of chunks){bytes.set(chunk,pos);pos+=chunk.length;}try{const value=JSON.parse(new TextDecoder().decode(bytes));if(!value||typeof value!=='object'||Array.isArray(value))throw Error();return value;}catch{fail(400,'Request data must be a JSON object.');}}
async function throttle(request,env,route,email){const time=now();const source=isLocal(request,env)?request.headers.get('CF-Connecting-IP')||'local':request.headers.get('CF-Connecting-IP')||'unknown';const keys=await Promise.all([`ip:${source}`,`email:${email}`].map(k=>digest(`${route}:${k}`)));for(const key of keys){const row=await env.DB.prepare('INSERT INTO auth_attempts (key, attempts, window_start) VALUES (?, 1, ?) ON CONFLICT(key) DO UPDATE SET attempts=CASE WHEN window_start < ? THEN 1 ELSE attempts+1 END, window_start=CASE WHEN window_start < ? THEN excluded.window_start ELSE window_start END RETURNING attempts').bind(key,time,time-900,time-900).first();if(row.attempts>5)fail(429,'Too many attempts. Please try again in 15 minutes.');}await env.DB.prepare('DELETE FROM auth_attempts WHERE window_start < ?').bind(time-3600).run();}
async function authenticated(request,env){const token=request.headers.get('cookie')?.match(/(?:^|;\s*)cabus_session=([A-Za-z0-9_-]{43})(?:;|$)/)?.[1];if(!token)fail(401,'Please sign in.');const row=await env.DB.prepare('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id AND u.auth_epoch=s.auth_epoch WHERE s.token_hash=? AND s.expires_at>?').bind(await digest(token),now()).first();if(!row)fail(401,'Your session expired. Please sign in again.');return row;}
async function loginSession(request,env,user){const token=random(),hash=await digest(token);const result=await env.DB.prepare('INSERT INTO sessions (token_hash,user_id,auth_epoch,expires_at) SELECT ?,id,auth_epoch,? FROM users WHERE id=? AND password_hash=? AND auth_epoch=?').bind(hash,now()+SESSION_SECONDS,user.id,user.password_hash,user.auth_epoch).run();if(!result.meta.changes)fail(401,'Your credentials changed. Please sign in again.');await env.DB.prepare('DELETE FROM sessions WHERE expires_at < ?').bind(now()).run();return cookie(request,env,token);}
export default {async fetch(request,env){
 try{
  const url=new URL(request.url),path=url.pathname;
  if(!path.startsWith('/api/'))return env.ASSETS?env.ASSETS.fetch(request):new Response('Not found',{status:404});
  if(!['GET','POST','PUT'].includes(request.method))fail(405,'Method not allowed.');
  if(request.method!=='GET'){const origin=request.headers.get('origin');if(origin!==url.origin||request.headers.get('sec-fetch-site')==='cross-site')fail(403,'This request must come from the tracker.');}
  if(path==='/api/register'&&request.method==='POST'){
   const input=await body(request),email=emailValue(input.email);passwordValid(input.password);if(typeof input.name!=='string'||!input.name.trim()||input.name.trim().length>80)fail(400,'Enter your name (up to 80 characters).');await throttle(request,env,'register',email);
   const user={id:crypto.randomUUID(),name:input.name.trim(),email,password_hash:await hashPassword(input.password),auth_epoch:0},recoveryCode=random();
   try{await env.DB.batch([env.DB.prepare('INSERT INTO users(id,name,email,password_hash,recovery_hash,created_at) VALUES(?,?,?,?,?,?)').bind(user.id,user.name,email,user.password_hash,await digest(recoveryCode),now()),env.DB.prepare('INSERT INTO documents(user_id,data,version,updated_at) VALUES(?,?,0,?)').bind(user.id,JSON.stringify(emptyData()),now())]);}catch(error){if(/UNIQUE|constraint/i.test(error.message))fail(409,'Unable to create this account. Try signing in or use another email.');throw error;}
   return response({user:publicUser(user),recoveryCode},201,{'Set-Cookie':await loginSession(request,env,user)});
  }
  if(path==='/api/login'&&request.method==='POST'){
   const input=await body(request),email=emailValue(input.email);passwordValid(input.password);await throttle(request,env,'login',email);const user=await env.DB.prepare('SELECT * FROM users WHERE email=?').bind(email).first();
   // Use the same password work for missing users to avoid a fast account probe.
   const stored=user?.password_hash||`scrypt$16384$8$5$missing-user-salt$${'0'.repeat(64)}`;
   if(!await checkPassword(input.password,stored)||!user)fail(401,'Email or password is incorrect.');return response({user:publicUser(user)},200,{'Set-Cookie':await loginSession(request,env,user)});
  }
  if(path==='/api/recover'&&request.method==='POST'){
   const input=await body(request),email=emailValue(input.email);passwordValid(input.newPassword);await throttle(request,env,'recover',email);if(typeof input.recoveryCode!=='string'||input.recoveryCode.length>100)fail(400,'Recovery details are incorrect.');const user=await env.DB.prepare('SELECT * FROM users WHERE email=?').bind(email).first(),old=await digest(input.recoveryCode);if(!user||old!==user.recovery_hash)fail(400,'Recovery details are incorrect.');const recoveryCode=random();const result=await env.DB.prepare('UPDATE users SET password_hash=?,recovery_hash=?,auth_epoch=auth_epoch+1 WHERE id=? AND recovery_hash=?').bind(await hashPassword(input.newPassword),await digest(recoveryCode),user.id,old).run();if(!result.meta.changes)fail(400,'Recovery details are incorrect.');return response({ok:true,recoveryCode},200,{'Set-Cookie':cookie(request,env,'',true)});
  }
  const user=await authenticated(request,env);
  // Cookies are shared across tabs; bind snapshots to the account the tab loaded.
  if(path==='/api/data'){
   const expected=request.headers.get('X-CABUS-Account');
   if((request.method==='PUT'&&!expected)||(expected&&expected!==user.id))return response({error:'Your account changed in another tab. Please sign in again.',code:'account_changed'},409);
  }
  if(path==='/api/me'&&request.method==='GET')return response({user:publicUser(user)});
  if(path==='/api/logout'&&request.method==='POST'){const token=request.headers.get('cookie').match(/cabus_session=([^;]+)/)[1];await env.DB.prepare('DELETE FROM sessions WHERE token_hash=?').bind(await digest(token)).run();return response({ok:true},200,{'Set-Cookie':cookie(request,env,'',true)});}
  if(path==='/api/password'&&request.method==='POST'){const input=await body(request);passwordValid(input.newPassword);if(typeof input.currentPassword!=='string'||input.currentPassword.length>128)fail(400,'Current password is incorrect.');await throttle(request,env,'password',user.email);if(!await checkPassword(input.currentPassword,user.password_hash))fail(400,'Current password is incorrect.');const result=await env.DB.prepare('UPDATE users SET password_hash=?,auth_epoch=auth_epoch+1 WHERE id=? AND password_hash=?').bind(await hashPassword(input.newPassword),user.id,user.password_hash).run();if(!result.meta.changes)fail(409,'Your credentials changed. Please sign in again.');return response({ok:true},200,{'Set-Cookie':cookie(request,env,'',true)});}
  if(path==='/api/data'&&request.method==='GET'){const row=await env.DB.prepare('SELECT data,version FROM documents WHERE user_id=?').bind(user.id).first();return response({data:JSON.parse(row.data),version:row.version});}
  if(path==='/api/data'&&request.method==='PUT'){const input=await body(request);if(!Number.isSafeInteger(input.version)||input.version<0)fail(400,'Invalid data version.');let data;try{data=validateData(input.data);}catch(error){fail(400,error.message);}const result=await env.DB.prepare('UPDATE documents SET data=?,version=version+1,updated_at=? WHERE user_id=? AND version=?').bind(JSON.stringify(data),now(),user.id,input.version).run();if(!result.meta.changes)fail(409,'Your data changed in another tab. Reload before saving again.');return response({data,version:input.version+1});}
  fail(404,'API route not found.');
 }catch(error){if(error instanceof Failure)return response({error:error.message},error.status,error.status===429?{'Retry-After':'900'}:{});console.error('CABUS request failed:',error.name,error.message);return response({error:'Unable to complete the request. Your existing records are safe. Try again.'},503);}
}};

