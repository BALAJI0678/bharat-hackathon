"""Offline, deterministic, tool-using triage agent. No model or network required."""
import csv, io, json, hashlib, re, uuid
from datetime import datetime, timezone
from collections import defaultdict

VERSION = '1.0.0'
MAX_RECORDS = 5000

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def digest(x):
    return hashlib.sha256(x if isinstance(x, bytes) else canonical(x).encode()).hexdigest()

def utc():
    return datetime.now(timezone.utc).isoformat()

def stamp(value):
    try:
        d = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if d.tzinfo is None: return None
        return d.astimezone(timezone.utc).isoformat()
    except (ValueError, TypeError): return None

def parse_evidence(raw, filename):
    if not isinstance(raw, str): raise ValueError('File content must be text')
    if len(raw.encode()) > 5_000_000: raise ValueError('Maximum file size is 5 MB')
    if filename.lower().endswith('.csv'):
        rows = list(csv.DictReader(io.StringIO(raw)))
    else:
        try: rows = json.loads(raw)
        except Exception as e: raise ValueError('Invalid JSON evidence') from e
        if isinstance(rows, dict): rows = rows.get('records')
    if not isinstance(rows, list) or not rows: raise ValueError('Supply a non-empty JSON array or CSV with a header')
    if len(rows) > MAX_RECORDS: raise ValueError('Maximum 5000 records per case')
    records, seen, warnings = [], set(), []
    for i, r in enumerate(rows):
        if not isinstance(r, dict): raise ValueError(f'Row {i+1}: record must be an object')
        rid = str(r.get('id') or f'E-{i+1:04d}')
        if len(rid)>100 or rid in seen: raise ValueError(f'Row {i+1}: duplicate or overly long evidence ID')
        seen.add(rid)
        content = r.get('content', r.get('body', ''))
        if content == '': content = {k:v for k,v in r.items() if k not in ('id','type','timestamp')}
        kind = str(r.get('type', r.get('evidenceType', 'UNKNOWN'))).upper()
        t = stamp(r.get('timestamp'))
        if not t: warnings.append(f'{rid}: missing/invalid timezone-aware timestamp; excluded from timed correlations')
        claimed = r.get('sha256')
        if claimed: warnings.append(f'{rid}: supplied hash is not proof of acquisition authenticity; computed import hashes used')
        records.append({'id': rid, 'type':kind, 'timestamp':t, 'content':content,
                        'metadata':r.get('metadata', {}), 'record_sha256':digest(r), 'source_record':r})
    return records, warnings

PATTERNS = [
 ('credential_request', r'\b(?:otp|one.time.password|pin|password)\b|ओटीपी|पासवर्ड|पिन', 'Credential-related language', 'medium'),
 ('payment_pressure', r'urgent|immediate|blocked|verify.*account|केवाईसी|खाता.*बंद|तुरंत|जल्दी|तत्काल', 'Urgency or account-pressure language', 'medium'),
 ('link', r'https?://[^\s<>"\']+', 'External link in message', 'low'),
]

def text(r): return canonical(r['content']) if isinstance(r['content'], (dict,list)) else str(r['content'])

def entities(records):
    result = defaultdict(list)
    for r in records:
        s = text(r)
        for token in set(re.findall(r'[\w.+-]+@[\w.-]+|https?://[^\s<>"\']+|(?<!\w)\+?\d[\d -]{8,14}\d(?!\w)', s)):
            result[token].append(r['id'])
    return [{'value':k,'evidence_ids':v} for k,v in sorted(result.items())]

def scan(records):
    findings=[]
    for r in records:
        if r['type'] not in ('SMS','CHAT','MESSAGE','EMAIL','BROWSER'): continue
        s=text(r); matched=[]
        for rule, pattern, title, priority in PATTERNS:
            if re.search(pattern, s, re.I): matched.append(rule)
        if matched:
            findings.append({'id': 'F-'+str(len(findings)+1), 'title': 'Review communication indicators',
                'priority': 'high' if len(matched)>=2 else 'medium' if 'link' not in matched or len(matched)>1 else 'low',
                'evidence_ids':[r['id']], 'rules':matched,
                'reasoning':'Matched explicit rules: '+', '.join(matched)+'. A match is a review lead, not proof of fraud.',
                'observation':s[:600]})
    return findings

def correlate(records, findings):
    out=[]
    flagged={eid for f in findings for eid in f['evidence_ids']}
    for r in records:
        if r['type'] not in ('TRANSACTION','PAYMENT','UPI'):continue
        if not r['timestamp']:continue
        t=datetime.fromisoformat(r['timestamp']); neighbors=[]
        for m in records:
            if m['id'] not in flagged or not m['timestamp']:continue
            delta=(t-datetime.fromisoformat(m['timestamp'])).total_seconds()
            if 0<=delta<=1800: neighbors.append(m['id'])
        if neighbors:
            out.append({'id':'C-'+str(len(out)+1),'priority':'medium','title':'Payment within 30 minutes after a flagged communication',
                'evidence_ids':neighbors+[r['id']], 'rules':['temporal_window_30m'],
                'reasoning':'Timestamp proximity only; sender identity, account ownership and causality are not established.',
                'observation':text(r)[:600]})
    return out

def timeline(records):
    return [{'timestamp':r['timestamp'], 'type':r['type'], 'evidence_id':r['id'], 'preview':text(r)[:200]}
            for r in sorted(records, key=lambda x: x['timestamp'] or '~') if r['timestamp']]

def verify_records(records):
    bad=[r['id'] for r in records if digest(r['source_record'])!=r['record_sha256']]
    if bad: raise ValueError('Stored record integrity mismatch: '+', '.join(bad))
    return {'checked':len(records), 'status':'matches_import_snapshot',
            'limitation':'Import-time integrity only. Does not authenticate the source device or establish legal chain of custody.'}

TOOLS={'verify_integrity':verify_records,'extract_entities':entities,'scan_indicators':scan,'build_timeline':timeline}

def run_agent(records, goal, warnings=()):
    if not isinstance(goal,str) or not goal.strip() or len(goal)>1000: raise ValueError('Objective must be 1–1000 characters')
    audit=[]; previous='0'*64
    def log(agent,stage,tool,decision,output):
        nonlocal previous
        event={'sequence':len(audit)+1,'at':utc(),'agent':agent,'stage':stage,'tool':tool,
               'decision':decision,'output':output,'previous_hash':previous}
        previous=digest(event);event['event_hash']=previous;audit.append(event)
    g=goal.lower()
    intent='timeline' if any(x in g for x in ['timeline','chronology','समय']) else 'entities' if any(x in g for x in ['contact','entities','identifier','संपर्क']) else 'fraud_triage'
    plan=['verify_integrity','build_timeline']
    if intent != 'timeline': plan+=['extract_entities']
    if intent=='fraud_triage':plan+=['scan_indicators']
    log('Intake','Understand','inspect_case','Classify objective using transparent keyword routing',{'intent':intent,'records':len(records),'goal':goal})
    log('Planner','Plan','select_tools','Only tools relevant to the objective are allowed',{'initial_plan':plan})
    result={'run_id':str(uuid.uuid4()), 'engine':'Offline deterministic tool agent (no LLM)', 'intent':intent,'goal':goal,
            'findings':[],'entities':[],'timeline':[],'warnings':list(warnings),'status':'awaiting_review','created_at':utc()}
    for tool in plan:
        output=TOOLS[tool](records)
        if tool=='verify_integrity':result['integrity']=output
        elif tool=='build_timeline':result['timeline']=output
        elif tool=='extract_entities':result['entities']=output
        elif tool=='scan_indicators':result['findings']=output
        log('Integrity' if tool=='verify_integrity' else 'Triage','Use Tools',tool,'Execute local tool on immutable imported records',{'count':len(output) if isinstance(output,list) else output})
    if intent=='fraud_triage':
        has_payments=any(r['type'] in ('TRANSACTION','PAYMENT','UPI') for r in records)
        if has_payments and result['findings']:
            log('Planner','Reason','replan','Flagged messages and payment records exist; add temporal correlation',{'added_tool':'correlate_payments'})
            extra=correlate(records,result['findings']);result['findings']+=extra
            log('Correlation','Use Tools','correlate_payments','Use 30-minute forward window; do not infer causation',{'count':len(extra)})
        else:
            log('Planner','Reason','replan','Skip payment correlation: requires both payments and communication indicators',{'added_tool':None})
    ids={r['id'] for r in records}
    if any(not set(f['evidence_ids'])<=ids for f in result['findings']):raise ValueError('Invalid evidence citation')
    result['summary']=f"{len(records)} imported records; {len(result['findings'])} review leads; {len(result['timeline'])} timestamped events. No conclusion of guilt or fraud is made."
    result['recommendations']=['Validate acquisition authority and original export independently.',
        'Review each cited record before approving a report.', 'Confirm payment ownership and context independently; temporal proximity is not causality.']
    log('Reporting','Act','save_review_packet','Prepare a review packet; external action and final export are approval-gated',{'state':'awaiting_review','finding_count':len(result['findings'])})
    result['audit']=audit;result['audit_root']=previous
    return result

def verify_audit(events):
    prev='0'*64
    for e in events:
        body={k:v for k,v in e.items() if k!='event_hash'}
        if e.get('previous_hash')!=prev or digest(body)!=e.get('event_hash'):return False
        prev=e['event_hash']
    return True

def render_report(case, run):
    lines=['# Bharat Evidence Agent — Reviewed triage report','',f"Case: {case['title']}",f"Mode: {case['mode']}",
           f"Reviewer: {run['reviewer']}",f"Approved: {run['approved_at']}",f"Run: {run['run_id']}",'',
           '## Important limits','Rule-based triage, not forensic attribution, legal advice, or proof of wrongdoing.',
           'Hashes establish an import snapshot only, not the authenticity of acquisition.', '', '## Objective', run['goal'],'','## Summary',run['summary'],'','## Findings']
    for f in run['findings']:
        lines += [f"### {f['id']} · {f['priority']} · {f['title']}", 'Evidence: '+', '.join(f['evidence_ids']),f['reasoning'],f['observation'],'']
    lines+=['## Timeline']
    lines += [f"- {e['timestamp']} | {e['type']} | {e['evidence_id']} | {e['preview']}" for e in run['timeline']]
    lines+=['','## Import manifest',f"SHA-256 (uploaded UTF-8 file bytes): {case['file_sha256']}",f"Records snapshot: {case['snapshot_sha256']}",f"Audit root: {run['audit_root']}",'','## Warnings']+list(run['warnings'])
    return '\n'.join(lines)
