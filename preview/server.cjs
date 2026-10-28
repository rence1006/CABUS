const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const files = {'/':'index.html','/index.html':'index.html','/style.css':'style.css','/app.js':'app.js'};
http.createServer((req,res)=>{
  const file = files[new URL(req.url,'http://localhost').pathname];
  if (!file) {res.writeHead(404);res.end('Not found');return;}
  fs.readFile(path.join(__dirname,file),(error,data)=>{
    if(error){res.writeHead(500);res.end('Preview file unavailable');return;}
    res.writeHead(200,{'Content-Type':file.endsWith('.css')?'text/css':file.endsWith('.js')?'application/javascript':'text/html','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(data);
  });
}).listen(4173,'127.0.0.1',()=>console.log('CABUS preview: http://127.0.0.1:4173'));
