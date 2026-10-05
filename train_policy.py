"""Exploratory post-policy replay, followed by May/June refit. Preserves failed baseline."""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score
from train_model import ROOT,pack,evaluate
from risk_model import RiskModel

def main():
    d=pd.read_csv(pack('train.csv')).sort_values('submitted_at',kind='stable').drop_duplicates('claim_id').reset_index(drop=True)
    policy=d[(d.submitted_at>='2026-05-01') & d.is_fraud.notna()].copy()
    may=policy[policy.submitted_at<'2026-06-01'];june=policy[policy.submitted_at>='2026-06-01']
    m=RiskModel.fit(may.to_dict('records'));p=np.array([m.predict(r)[0] for r in june.to_dict('records')]);metrics,z=evaluate(june,p)
    z.to_csv(ROOT/'evidence'/'policy_june_replay.csv',index=False)
    rng=np.random.default_rng(42);y=june.is_fraud.astype(int).to_numpy();ap=[];auc=[];money=[]
    for _ in range(1000):
        ii=rng.integers(0,len(y),len(y))
        if len(set(y[ii]))==2:ap.append(average_precision_score(y[ii],p[ii]));auc.append(roc_auc_score(y[ii],p[ii]))
        # fixed observed review decisions; CI does not represent future queue re-ranking.
        vals=np.where(z.review,np.where(y==1,z.claim_amount_inr-260,-640),0)
        money.append(float(vals[ii].sum()))
    metrics['ap_bootstrap_95']=np.quantile(ap,[.025,.975]).tolist();metrics['roc_auc_bootstrap_95']=np.quantile(auc,[.025,.975]).tolist();metrics['fixed_decision_savings_bootstrap_95']=np.quantile(money,[.025,.975]).tolist()
    report={'evaluation_status':'Exploratory: May/June baseline failure and June outcomes were inspected before this redesign. Not a pristine holdout or prospective evidence.','fit_month':'May 2026','fit_n':len(may),'fit_frauds':int(may.is_fraud.sum()),'june_replay':metrics,'final_fit_n':len(policy),'final_fit_frauds':int(policy.is_fraud.sum()),'prior_strength_partner':3,'prior_strength_band':3,'band_cutoff_inr':1950,'score_interpretation':'Smoothed observed fraud frequency; uncertain and potentially selection-biased. Validate prospectively before intervention.'}
    final=RiskModel.fit(policy.to_dict('records'));final.save(ROOT/'artifacts'/'policy_model.json')
    test=pd.read_csv(pack('test_unlabelled.csv'));scores=[final.predict(r)[0] for r in test.to_dict('records')]
    pred=pd.read_csv(pack('sample_submission.csv'))[['claim_id']].merge(pd.DataFrame({'claim_id':test.claim_id,'score':scores}),on='claim_id',validate='one_to_one');pred.to_csv(ROOT/'predictions.csv',index=False)
    (ROOT/'evidence'/'policy_metrics.json').write_text(json.dumps(report,indent=2))
    meta=json.loads((ROOT/'artifacts'/'metadata.json').read_text());meta.update({'model_version':'policy-bayes-v2','deployment_mode':'shadow_only','policy_fit_start':'2026-05-01','evaluation_status':report['evaluation_status']});(ROOT/'artifacts'/'metadata.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
