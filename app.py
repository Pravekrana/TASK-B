"""Local review assistant. No network calls or API keys."""
import json, math, time
from pathlib import Path
import pandas as pd
from flask import Flask,request,jsonify,send_from_directory
from werkzeug.exceptions import HTTPException
from features import features,CAT,serial_key
from risk_model import RiskModel

ROOT=Path(__file__).resolve().parent
app=Flask(__name__,static_folder='static');app.config['MAX_CONTENT_LENGTH']=32768
model=None; startup_error=None
try:
    model=RiskModel.load(ROOT/'artifacts'/'policy_model.json')
    partners=pd.read_csv(ROOT/'artifacts'/'partners.csv');products=pd.read_csv(ROOT/'artifacts'/'products.csv')
    metadata=json.loads((ROOT/'artifacts'/'metadata.json').read_text())
except Exception:
    startup_error='Model artifacts unavailable. Run python train_model.py with the private data pack, then restart.'

REQUIRED=['claim_id','submitted_at','partner_id','sku','product_serial','days_since_purchase','claim_amount_inr','photo_attached','partner_inspected','customer_prior_claims']
LABELS={'days_since_purchase':'Time since purchase','claim_amount_inr':'Claim amount','customer_prior_claims':'Earlier customer claims','amount_price_ratio':'Claim amount compared with product price','warranty_age_ratio':'Product age compared with standard warranty','serial_prior_claims':'Earlier claims using this serial','serial_prior_partners':'Earlier partners using this serial','serial_valid':'Serial format','under_auto_approval_limit':'Amount below the inspection threshold','post_policy':'Submission after the May policy change','missing_photo':'Missing photo','sku':'Product model','family':'Product family','photo_attached':'Photo availability','partner_inspected':'Partner inspection sign-off','partner_type':'Partner type','city':'Partner city'}

def validate(d):
    if not isinstance(d,dict):raise ValueError('Send one JSON object.')
    missing=[c for c in REQUIRED if c not in d]
    if missing:raise ValueError('Missing fields: '+', '.join(missing))
    for c in ['claim_id','partner_id','sku','product_serial','submitted_at']:
        if not isinstance(d[c],str) or not d[c].strip() or len(d[c])>100:raise ValueError(c+' must be a nonempty string, at most 100 characters.')
    for c in ['days_since_purchase','claim_amount_inr','customer_prior_claims']:
        v=d[c]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:raise ValueError(c+' must be a finite nonnegative number.')
    for c in ['days_since_purchase','customer_prior_claims']:
        if int(d[c])!=d[c]:raise ValueError(c+' must be an integer.')
    for c in ['photo_attached','partner_inspected']:
        if d[c] not in ['Y','N']:raise ValueError(c+' must be Y or N.')
    try:
        date=pd.Timestamp(d['submitted_at'])
        if date.tzinfo is not None:raise ValueError()
    except Exception:raise ValueError('submitted_at must be a valid local IST date/time without timezone, e.g. 2026-07-01 10:00.')
    return d

def predict(d):
    started=time.perf_counter();d=validate(d)
    score,reasons=model.predict(d)
    expected=score*d['claim_amount_inr']-(1-score)*380-260
    warnings=[]
    if d['partner_id'] not in set(partners.partner_id):warnings.append('Unknown partner: reference checks needed.')
    if d['sku'] not in set(products.sku):warnings.append('Unknown product: price and warranty references unavailable.')
    product=products[products.sku==d['sku']]
    if len(product) and d['days_since_purchase']>float(product.iloc[0].warranty_months)*365.25/12:warnings.append('Beyond standard warranty age; verify Shield entitlement before deciding eligibility.')
    if d['claim_amount_inr']>=2000 and d['partner_inspected']=='N':warnings.append('Policy requires inspection for claims of Rs 2,000 or more.')
    if pd.Timestamp(d['submitted_at'])<=pd.Timestamp(metadata['training_cutoff']):warnings.append('Historical input: model was trained through '+metadata['training_cutoff']+'. This is not an unbiased retrospective prediction.')
    if pd.Timestamp(d['submitted_at'])>pd.Timestamp('2026-10-01'):warnings.append('Input is later than the tested deployment period; monitor drift.')
    return {'claim_id':d['claim_id'],'score':score,'model_version':metadata['model_version'],'deployment_mode':'shadow_only','recommendation':'review_candidate' if expected>0 else 'routine_processing','expected_net_review_value_inr':round(expected,2),'reasons':reasons,'warnings':warnings,'decision_note':'SHADOW ONLY: do not change customer processing from this score yet. Employee review only; never automatically deny. For a later approved pilot, rank positive-value candidates across the monthly queue and select at most 40; a single request cannot reserve capacity.','history_cutoff':metadata['history_cutoff'],'latency_ms':round((time.perf_counter()-started)*1000,2)}

@app.get('/')
def index():return send_from_directory(ROOT/'static','index.html')
@app.get('/health')
def health():return jsonify({'ready':model is not None and startup_error is None,'message':startup_error or 'ready'}),503 if startup_error else 200
@app.get('/evidence')
def evidence_page():
    import html
    allowed={'README.md','evidence-report.md','submission-form.md','risk_model.py','train_policy.py','train_model.py','data-audit.md'}
    name=request.args.get('file','evidence-report.md')
    if name not in allowed:return 'Not available',404
    path=ROOT/name
    if not path.exists():return 'Report not installed',404
    nav=' | '.join(f'<a href="/evidence?file={html.escape(n)}">{html.escape(n)}</a>' for n in sorted(allowed))
    return '<html><title>Kestrel | Evidence and source</title><style>body{font:16px system-ui;max-width:1150px;margin:35px auto;color:#173548;background:#f5f7f8}nav{padding:18px;background:white;line-height:2}pre{white-space:pre-wrap;line-height:1.5;background:white;padding:25px;font:15px Consolas,monospace}a{color:#087d80}</style><h1>Kestrel review assistant - working evidence</h1><nav><a href="/">Live service</a> | '+nav+'</nav><pre>'+html.escape(path.read_text(encoding='utf-8'))+'</pre></html>'
@app.post('/predict')
def endpoint():
    if startup_error:return jsonify({'error':startup_error}),503
    if not request.is_json:return jsonify({'error':'Content-Type must be application/json.'}),415
    try:return jsonify(predict(request.get_json(silent=True)))
    except ValueError as e:return jsonify({'error':str(e)}),400
    except HTTPException as e:return jsonify({'error':e.description}),e.code
    except Exception:app.logger.exception('prediction failed');return jsonify({'error':'Unable to score this record. Keep it in the normal manual workflow.'}),500
if __name__=='__main__':app.run(host='127.0.0.1',port=8000,debug=False)
