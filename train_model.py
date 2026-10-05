"""Reproducible temporal evaluation and final refit. Run from this folder."""
import json,time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss,confusion_matrix
from features import features,CAT,serial_key

ROOT=Path(__file__).resolve().parent
def pack(name):
    exact=ROOT/name
    return exact if exact.exists() else next(ROOT.glob('*-'+name))
def model(depth=4):
    return CatBoostClassifier(iterations=450,depth=depth,learning_rate=.035,l2_leaf_reg=10,loss_function='Logloss',random_seed=42,verbose=False,thread_count=4,allow_writing_files=False)
def evaluate(d,p):
    y=d.is_fraud.astype(int).to_numpy()
    z=d[['claim_id','submitted_at','claim_amount_inr','is_fraud']].copy(); z['score']=p
    z['month']=z.submitted_at.str[:7]
    z['expected_net_inr']=p*z.claim_amount_inr-(1-p)*380-260
    z['review']=False
    for _,g in z.groupby('month'):
        chosen=g[g.expected_net_inr>0].nlargest(40,'expected_net_inr').index
        z.loc[chosen,'review']=True
    sel=z.review.to_numpy()
    tp=int(((y==1)&sel).sum()); fp=int(((y==0)&sel).sum())
    gain=float(z.loc[sel & (y==1),'claim_amount_inr'].sum()-380*fp-260*sel.sum())
    return {'n':len(y),'frauds':int(y.sum()),'prevalence':float(y.mean()),'roc_auc':float(roc_auc_score(y,p)),'average_precision':float(average_precision_score(y,p)),'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p,labels=[0,1])),'accuracy_at_0_5':float(((p>=.5)==y).mean()),'always_genuine_accuracy':float((y==0).mean()),'confusion_at_0_5':confusion_matrix(y,p>=.5,labels=[0,1]).tolist(),'reviewed':int(sel.sum()),'caught':tp,'genuine_delayed':fp,'review_precision':tp/max(int(sel.sum()),1),'fraud_recall':tp/max(int(y.sum()),1),'net_savings_inr':gain,'net_savings_monthly_inr':gain/z.month.nunique()},z

def main():
    started=time.time(); (ROOT/'artifacts').mkdir(exist_ok=True); (ROOT/'evidence').mkdir(exist_ok=True)
    raw=pd.read_csv(pack('train.csv')); test=pd.read_csv(pack('test_unlabelled.csv')); partners=pd.read_csv(pack('partners.csv')); products=pd.read_csv(pack('products.csv'))
    conflict=raw.groupby('claim_id').is_fraud.nunique().gt(1)
    clean=raw.sort_values('submitted_at',kind='stable').drop_duplicates('claim_id',keep='first')
    clean=clean[~clean.claim_id.isin(conflict[conflict].index)].reset_index(drop=True)
    labelled=clean[clean.is_fraud.notna()].copy()
    fit=labelled[labelled.submitted_at<'2026-01-01']; val=labelled[(labelled.submitted_at>='2026-01-01')&(labelled.submitted_at<'2026-05-01')]; hold=labelled[labelled.submitted_at>='2026-05-01']
    X=features(labelled,partners,products,clean); X.index=labelled.index
    trials=[]; candidates={}
    for depth in [3,5]:
        m=model(depth);m.fit(X.loc[fit.index],fit.is_fraud.astype(int),cat_features=CAT)
        metric,_=evaluate(val,m.predict_proba(X.loc[val.index])[:,1]); trials.append({'name':f'catboost_depth_{depth}',**metric}); candidates[depth]=m
    # Test the client hypothesis only on development validation, not the final holdout.
    Xa=features(labelled,partners,products,clean,include_age=True); Xa.index=labelled.index
    ma=model(3);ma.fit(Xa.loc[fit.index],fit.is_fraud.astype(int),cat_features=CAT)
    age_metric,_=evaluate(val,ma.predict_proba(Xa.loc[val.index])[:,1]);trials.append({'name':'age_ablation_depth_3',**age_metric})
    best=max([3,5],key=lambda k:next(t['average_precision'] for t in trials if t['name']==f'catboost_depth_{k}'))
    # Hyperparameters locked before May/June outcomes are evaluated.
    pre=labelled[labelled.submitted_at<'2026-05-01']
    locked=model(best);locked.fit(X.loc[pre.index],pre.is_fraud.astype(int),cat_features=CAT)
    p=locked.predict_proba(X.loc[hold.index])[:,1]; metrics,z=evaluate(hold,p);z.to_csv(ROOT/'evidence'/'holdout_predictions.csv',index=False)
    monthly=[]
    for month,g in hold.groupby(hold.submitted_at.str[:7]):
        idx=hold.index.get_indexer(g.index);a,_=evaluate(g,p[idx]);monthly.append({'month':month,**a})
    # Case-level bootstrap CI, conditional on the observed holdout; no claim of drift coverage.
    rng=np.random.default_rng(42);y=hold.is_fraud.astype(int).to_numpy();auc=[];ap=[]
    for _ in range(1000):
        ii=rng.integers(0,len(y),len(y))
        if len(np.unique(y[ii]))==2: auc.append(roc_auc_score(y[ii],p[ii]));ap.append(average_precision_score(y[ii],p[ii]))
    metrics['roc_auc_bootstrap_95']=np.quantile(auc,[.025,.975]).tolist();metrics['ap_bootstrap_95']=np.quantile(ap,[.025,.975]).tolist()
    final=model(best);final.fit(X,labelled.is_fraud.astype(int),cat_features=CAT);final.save_model(str(ROOT/'artifacts'/'model.cbm'))
    # Freeze history at training cutoff: same result from batch and single-record service.
    history=clean[['claim_id','submitted_at','product_serial','partner_id']].copy(); history.to_csv(ROOT/'artifacts'/'history.csv',index=False)
    partners.to_csv(ROOT/'artifacts'/'partners.csv',index=False);products.to_csv(ROOT/'artifacts'/'products.csv',index=False)
    pt=final.predict_proba(features(test,partners,products,history))[:,1]
    submission=pd.read_csv(pack('sample_submission.csv'))[['claim_id']].merge(pd.DataFrame({'claim_id':test.claim_id,'score':pt}),on='claim_id',validate='one_to_one')
    assert len(submission)==len(test) and submission.score.between(0,1).all() and submission.claim_id.is_unique
    submission.to_csv(ROOT/'predictions.csv',index=False)
    imp=pd.DataFrame({'feature':X.columns,'importance':final.feature_importances_}).sort_values('importance',ascending=False);imp.to_csv(ROOT/'evidence'/'feature_importance.csv',index=False)
    injected=raw.claim_description.str.contains('automated|Reviewer tools|ops note',case=False,regex=True)
    audit={'raw_rows':len(raw),'unique_claims':len(clean),'duplicate_rows_removed':len(raw)-len(clean),'undecided_unique':int(clean.is_fraud.isna().sum()),'labelled_unique':len(labelled),'fraud_unique':int(labelled.is_fraud.sum()),'conflicting_labels':int(conflict.sum()),'embedded_instruction_rows':int(injected.sum()),'missing_email_thread':not (ROOT/'email-thread.txt').exists(),'train_cutoff':clean.submitted_at.max(),'test_rows':len(test),'unknown_test_partners':int((~test.partner_id.isin(partners.partner_id)).sum()),'unknown_test_skus':int((~test.sku.isin(products.sku)).sum()),'test_negative_partner_age':int((pd.to_datetime(test.submitted_at)-pd.to_datetime(test.merge(partners,on='partner_id').onboarded_date)).dt.days.lt(0).sum()),'runtime_seconds':round(time.time()-started,2)}
    report={'audit':audit,'development':trials,'chosen_depth':best,'holdout':metrics,'holdout_months':monthly,'features':list(X.columns),'fit_n':len(fit),'validation_n':len(val),'pre_holdout_fit_n':len(pre),'final_fit_n':len(labelled),'review_assumptions':{'capacity_per_month':40,'genuine_delay_inr':380,'contact_per_review_inr':260,'fraud_block_success':1.0}}
    (ROOT/'evidence'/'metrics.json').write_text(json.dumps(report,indent=2))
    metadata={'model_version':'kestrel-v1','depth':best,'features':list(X.columns),'training_cutoff':clean.submitted_at.max(),'history_cutoff':clean.submitted_at.max(),'holdout':metrics}
    (ROOT/'artifacts'/'metadata.json').write_text(json.dumps(metadata,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
