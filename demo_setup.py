"""Synthetic demo only. Does not overwrite private artifacts."""
import csv,json
from pathlib import Path
from risk_model import RiskModel
root=Path(__file__).resolve().parent;out=root/'artifacts'
if (out/'policy_model.json').exists():raise SystemExit('Model already exists; refusing to overwrite it.')
out.mkdir(exist_ok=True)
records=[]
for partner,frauds in [('SP3033',1),('SYNTHETIC-HIGH',7)]:
    for i in range(20):records.append({'partner_id':partner,'claim_amount_inr':1995 if i<10 else 1200,'is_fraud':int(i<frauds)})
RiskModel.fit(records).save(out/'policy_model.json')
for name,headers,rows in [('partners.csv',['partner_id','city','onboarded_date','partner_type'],[['SP3033','Synthetic City','2020-01-01','synthetic'],['SYNTHETIC-HIGH','Synthetic City','2020-01-01','synthetic']]),('products.csv',['sku','family','list_price_inr','warranty_months'],[['KH-AF-01','Synthetic appliance',5000,12]])]:
    with (out/name).open('w',newline='') as f:w=csv.writer(f);w.writerow(headers);w.writerows(rows)
(out/'metadata.json').write_text(json.dumps({'model_version':'SYNTHETIC-DEMO','training_cutoff':'2026-06-30 23:40','history_cutoff':'2026-06-30 23:40','deployment_mode':'shadow_only'}))
print('Synthetic demo ready. Run python app.py. These are not assignment scores.')
