import http from 'node:http';
import {readFile,stat,mkdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import worker from './src/worker.js';
import {createDatabase} from './src/local-db.mjs';
const directory=path.dirname(fileURLToPath(import.meta.url));
const root=path.join(directory,'public');
await mkdir(path.join(directory,'.local'),{recursive:true});
const DB=createDatabase(process.env.CABUS_DB_PATH||path.join(directory,'.local','cabus.sqlite'));
const port=Number(process.env.PORT||4174);
const mime={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2'};
const securityHeaders={'X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'none'"};
const server=http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,`http://${req.headers.host}`);
  if(url.pathname.startsWith('/api/')){
   const headers=new Headers(req.headers);headers.set('CF-Connecting-IP',req.socket.remoteAddress||'local');
   let size=0,chunks=[];for await(const chunk of req){size+=chunk.length;if(size>524288){res.writeHead(413,{'Content-Type':'application/json'});res.end(JSON.stringify({error:'This request is too large.'}));return;}chunks.push(chunk);}
   const response=await worker.fetch(new Request(url,{method:req.method,headers,body:['GET','HEAD'].includes(req.method)?undefined:Buffer.concat(chunks)}),{DB,DEVELOPMENT:'true'});
   res.writeHead(response.status,{...securityHeaders,...Object.fromEntries(response.headers)});res.end(Buffer.from(await response.arrayBuffer()));return;
  }
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
  const pathname=decodeURIComponent(url.pathname),relative=pathname==='/'?'index.html':pathname.slice(1);
  const filename=path.resolve(root,relative);
  if(!filename.startsWith(root+path.sep)||relative.split(/[\\/]/).some(p=>p.startsWith('.'))){res.writeHead(404);res.end('Not found');return;}
  if(!(await stat(filename)).isFile()){res.writeHead(404);res.end('Not found');return;}
  const bytes=await readFile(filename);res.writeHead(200,{...securityHeaders,'Cache-Control':'no-store','Content-Type':mime[path.extname(filename)]||'application/octet-stream'});res.end(req.method==='HEAD'?undefined:bytes);
 }catch(error){res.writeHead(error.code==='ENOENT'?404:500,{'Content-Type':'text/plain'});res.end(error.code==='ENOENT'?'Not found':'Unable to serve this request.');}
});
server.listen(port,'127.0.0.1',()=>console.log(`CABUS app: http://127.0.0.1:${port}\nLocal SQLite storage: web/.local/ (private, excluded from deployment)`));
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>{DB.close();process.exit(0);}));
