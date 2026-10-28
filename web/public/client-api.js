export function staleSessionError(){const error=Error('Your account changed. Sign in again before continuing.');error.staleSession=true;return error;}
export function sameSession(a,b){return a.generation===b.generation&&a.accountId===b.accountId;}
export function createAccountApi({getSession,fetch=globalThis.fetch,onAccountChanged=()=>{}}){
 return async function api(path,method='GET',body){
  const session={...getSession()},headers=body?{'Content-Type':'application/json'}:{};
  if(path==='data'&&session.accountId)headers['X-CABUS-Account']=session.accountId;
  const assertCurrent=()=>{if(!sameSession(session,getSession()))throw staleSessionError();};
  let response;
  try{response=await fetch('/api/'+path,{method,credentials:'same-origin',headers,body:body?JSON.stringify(body):undefined});}catch(error){assertCurrent();throw error;}
  assertCurrent();let result;try{result=await response.json();}catch{assertCurrent();throw Error('The server is unavailable. Please try again.');}
  assertCurrent();
  if(!response.ok){if(result.code==='account_changed'||response.status===401&&session.accountId){onAccountChanged();throw staleSessionError();}const error=Error(result.error||'Request failed. Please try again.');error.status=response.status;throw error;}
  return result;
 };
}
