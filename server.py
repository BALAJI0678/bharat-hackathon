"""Local-only HTTP app. Python 3.10+; no pip dependencies."""
import argparse, json, os, sqlite3, secrets, threading, uuid
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from agent import parse_evidence, digest, canonical, run_agent, render_report, utc, verify_audit
ROOT=Path(__file__).resolve().parent
TOKEN=secrets.token_urlsafe(32)
LOCK=threading.RLock()
DB=None

def initialize(path):
    global DB
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    DB=sqlite3.connect(path,check_same_thread=False)
    DB.execute('CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
    DB.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, case_id TEXT NOT NULL, data TEXT NOT NULL)')
    DB.commit()

def get_case(cid):
    row=DB.execute('SELECT data FROM cases WHERE id=?',(cid,)).fetchone()
    if not row:raise ValueError('Case not found')
    c=json.loads(row[0])
    if digest(c['records'])!=c['snapshot_sha256']:raise ValueError('Case snapshot integrity mismatch')
    return c

def get_run(rid):
    row=DB.execute('SELECT case_id,data FROM runs WHERE id=?',(rid,)).fetchone()
    if not row:raise ValueError('Run not found')
    r=json.loads(row[1])
    if not verify_audit(r['audit']):raise ValueError('Audit integrity mismatch')
    return row[0],r

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass # do not log evidence or tokens
    def send(self,status,body,kind='application/json; charset=utf-8',download=None):
        if isinstance(body,(dict,list)): body=json.dumps(body,ensure_ascii=False).encode()
        elif isinstance(body,str): body=body.encode()
        self.send_response(status)
        self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        if download:self.send_header('Content-Disposition',f'attachment; filename="{download}"')
        self.end_headers();self.wfile.write(body)
    def safe_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def do_GET(self):
        if not self.safe_host():return self.send(403,{'error':'Local host required'})
        path=urlparse(self.path).path
        try:
            with LOCK:
                if path=='/api/session':return self.send(200,{'token':TOKEN,'version':'1.0.0'})
                if path.startswith('/api/') and self.headers.get('X-Session-Token')!=TOKEN:return self.send(403,{'error':'Session required'})
                if path=='/api/cases':
                    cases=[json.loads(x[0]) for x in DB.execute('SELECT data FROM cases')]
                    return self.send(200,[{k:c[k] for k in ('id','title','mode','created_at','record_count')} for c in cases])
                if path=='/api/demo':return self.send(200,json.loads((ROOT/'samples/bharat-demo.json').read_text(encoding='utf-8')))
                if path.startswith('/api/cases/'):
                    cid=path.split('/')[3]; c=get_case(cid)
                    runs=[json.loads(x[0]) for x in DB.execute('SELECT data FROM runs WHERE case_id=?',(cid,))]
                    return self.send(200,{'case':c,'runs':runs})
                if path.startswith('/api/report/'):
                    cid,r=get_run(path.split('/')[3])
                    if r['status']!='approved':return self.send(409,{'error':'Human approval required before export'})
                    return self.send(200,render_report(get_case(cid),r),'text/markdown; charset=utf-8','reviewed-report.md')
                if path.startswith('/api/audit/'):
                    _,r=get_run(path.split('/')[3]);return self.send(200,r,'application/json; charset=utf-8','agent-audit.json')
                assets={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
                if path in assets:
                    mime='text/html' if path=='/' else 'text/javascript' if path.endswith('.js') else 'text/css'
                    return self.send(200,(ROOT/'static'/assets[path]).read_bytes(),mime+'; charset=utf-8')
                return self.send(404,{'error':'Not found'})
        except ValueError as e:self.send(400,{'error':str(e)})
        except Exception:self.send(500,{'error':'Internal error; see local test/setup documentation'})
    def do_POST(self):
        if not self.safe_host() or self.headers.get('X-Session-Token')!=TOKEN:return self.send(403,{'error':'Invalid local session'})
        origin=self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
            return self.send(403,{'error':'Cross-origin request rejected'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<=0 or length>8_000_000:return self.send(413,{'error':'Request limit 8 MB'})
            data=json.loads(self.rfile.read(length));path=urlparse(self.path).path
            with LOCK:
                if path=='/api/import':
                    if data.get('authorized') is not True:raise ValueError('Authorization acknowledgement required')
                    title=str(data.get('title','')).strip()
                    if not title or len(title)>150:raise ValueError('Case title must be 1–150 characters')
                    raw=data.get('raw');filename=str(data.get('filename','evidence.json'))
                    records,warnings=parse_evidence(raw,filename)
                    mode=data.get('mode','authorized_export')
                    if mode not in ('synthetic_demo','authorized_export'):raise ValueError('Invalid evidence mode')
                    cid=str(uuid.uuid4());c={'id':cid,'title':title,'mode':mode,'created_at':utc(),'filename':Path(filename).name,
                        'record_count':len(records),'file_sha256':digest(raw.encode()),'snapshot_sha256':digest(records),
                        'records':records,'warnings':warnings,'authorization_acknowledged_at':utc()}
                    DB.execute('INSERT INTO cases VALUES (?,?)',(cid,canonical(c)));DB.commit()
                    return self.send(201,c)
                if path=='/api/run':
                    c=get_case(data.get('case_id'));r=run_agent(c['records'],data.get('goal'),c['warnings'])
                    DB.execute('INSERT INTO runs VALUES (?,?,?)',(r['run_id'],c['id'],canonical(r)));DB.commit()
                    return self.send(201,r)
                if path=='/api/approve':
                    cid,r=get_run(data.get('run_id'));get_case(cid)
                    reviewer=str(data.get('reviewer','')).strip();note=str(data.get('note','')).strip()
                    if not reviewer or len(reviewer)>120 or not note or len(note)>1000:raise ValueError('Reviewer name and review note required (120 / 1000 character limits)')
                    if data.get('confirmed') is not True:raise ValueError('Confirm you reviewed the cited evidence')
                    if r['status']=='approved':raise ValueError('Already approved; run again for a new review')
                    e={'sequence':len(r['audit'])+1,'at':utc(),'agent':'Human reviewer','stage':'Act','tool':'approve_report',
                        'decision':note,'output':{'reviewer':reviewer},'previous_hash':r['audit_root']}
                    e['event_hash']=digest(e);r['audit'].append(e);r['audit_root']=e['event_hash']
                    r.update(status='approved',reviewer=reviewer,review_note=note,approved_at=e['at'])
                    DB.execute('UPDATE runs SET data=? WHERE id=?',(canonical(r),r['run_id']));DB.commit()
                    return self.send(200,r)
                return self.send(404,{'error':'Not found'})
        except (ValueError,TypeError,KeyError) as e:self.send(400,{'error':str(e)})
        except Exception:self.send(500,{'error':'Internal error'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8787);p.add_argument('--db',default=str(ROOT/'data/cases.sqlite3'))
    args=p.parse_args();initialize(args.db)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Bharat Evidence Agent: http://127.0.0.1:{args.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close();DB.close()
