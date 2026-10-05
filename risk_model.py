"""Policy-era hierarchical empirical Bayes risk, fixed shrinkage strengths.

Scores are posterior means, not proven calibrated probabilities. Partner evidence
is predictive, not a finding that a partner caused fraud. No partner age input.
"""
import json
from pathlib import Path

def bucket(row):
    amount=float(row['claim_amount_inr'])
    if amount>=2000:return 'inspection_required'
    return 'near_cutoff' if amount>=1950 else 'below_cutoff'

class RiskModel:
    def __init__(self,state):self.state=state
    @classmethod
    def fit(cls,records):
        s={'version':'policy-bayes-v2','n':0,'frauds':0,'partners':{},'buckets':{},'cells':{}}
        for r in records:
            y=int(r['is_fraud']);b=bucket(r);p=r['partner_id'];s['n']+=1;s['frauds']+=y
            for table,key in [('partners',p),('buckets',b),('cells',p+'|'+b)]:
                c=s[table].setdefault(key,{'n':0,'frauds':0});c['n']+=1;c['frauds']+=y
        return cls(s)
    def save(self,path):Path(path).write_text(json.dumps(self.state,indent=2))
    @classmethod
    def load(cls,path):return cls(json.loads(Path(path).read_text()))
    def predict(self,row):
        s=self.state;g=(s['frauds']+.5)/(s['n']+1);p=row['partner_id'];b=bucket(row)
        pc=s['partners'].get(p,{'n':0,'frauds':0});bc=s['buckets'].get(b,{'n':0,'frauds':0});cell=s['cells'].get(p+'|'+b,{'n':0,'frauds':0})
        bp=(bc['frauds']+3*g)/(bc['n']+3)
        # Known partners pool across amount bands; unseen partners use band prevalence.
        pp=(pc['frauds']+3*g)/(pc['n']+3) if pc['n'] else bp
        score=(cell['frauds']+3*pp)/(cell['n']+3)
        reason=[{'factor':'Recent investigated claims for this partner','observed':f"{pc['frauds']} fraud outcomes / {pc['n']} decided claims",'direction':'raises risk' if pp>g else 'lowers risk','explanation':f"Recent partner evidence: {pc['frauds']} fraud outcomes in {pc['n']} decided claims. The estimate is shrunk toward the recent base rate; this is not proof of fraud."},
                {'factor':'Amount band after the May policy change','observed':b,'direction':'raises risk' if score>pp else 'lowers risk','explanation':f"In this partner's {b.replace('_',' ')} band, {cell['frauds']} of {cell['n']} decided claims were fraud. Sparse evidence is pooled with the partner estimate, not treated as proof of fraud."},
                {'factor':'Policy-era base rate','observed':round(g,5),'direction':'context','explanation':f"The reference population is {s['n']} decided claims submitted after 1 May, with {s['frauds']} fraud outcomes. Investigation selection may bias this rate; it is not proof of fraud."},
                {'factor':'Evidence strength','observed':cell['n'],'direction':'context','explanation':f"This amount band has {cell['n']} decided claims for the partner. Three prior-equivalent observations stabilise the estimate; small samples remain uncertain and are not proof of fraud."}]
        return float(score),reason
