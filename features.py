"""Only submission-time information. No labels, IDs, notes or free-text instructions."""
import re
import pandas as pd

NUMERIC = ['days_since_purchase','claim_amount_inr','customer_prior_claims','amount_price_ratio','warranty_age_ratio','serial_prior_claims','serial_prior_partners','serial_valid','under_auto_approval_limit','post_policy','missing_photo']
CAT = ['sku','family','photo_attached','partner_inspected','partner_type','city']

def serial_key(value):
    return re.sub(r'[^A-Z0-9]', '', str(value).upper())

def features(records, partners, products, history=None, include_age=False):
    d=records.copy()
    d=d.merge(partners, on='partner_id', how='left', validate='many_to_one').merge(products,on='sku',how='left',validate='many_to_one')
    date=pd.to_datetime(d.submitted_at)
    d['amount_price_ratio']=d.claim_amount_inr/d.list_price_inr
    d['warranty_age_ratio']=d.days_since_purchase/(d.warranty_months*365.25/12)
    d['serial_valid']=d.product_serial.map(lambda x:int(bool(re.fullmatch(r'KH\d{9}',serial_key(x)))))
    d['serial_prior_claims']=0
    d['serial_prior_partners']=0
    if history is not None and len(history):
        h=history[['claim_id','submitted_at','product_serial','partner_id']].copy()
        h['key']=h.product_serial.map(serial_key)
        h['date']=pd.to_datetime(h.submitted_at)
        groups={k:g for k,g in h.groupby('key')}
        for i,row in d.iterrows():
            g=groups.get(serial_key(row.product_serial))
            if g is not None:
                prior=g[(g.date<date.iloc[i]) & (g.claim_id!=row.claim_id)]
                d.loc[i,'serial_prior_claims']=prior.claim_id.nunique()
                d.loc[i,'serial_prior_partners']=prior.partner_id.nunique()
    d['under_auto_approval_limit']=(d.claim_amount_inr<2000).astype(int)
    d['post_policy']=(date>=pd.Timestamp('2026-05-01')).astype(int)
    d['missing_photo']=(d.photo_attached=='N').astype(int)
    columns=NUMERIC+CAT
    if include_age:
        d['partner_age_days']=(date-pd.to_datetime(d.onboarded_date)).dt.days
        columns=columns+['partner_age_days']
    for c in CAT: d[c]=d[c].fillna('unknown').astype(str)
    return d[columns].fillna(-1)
