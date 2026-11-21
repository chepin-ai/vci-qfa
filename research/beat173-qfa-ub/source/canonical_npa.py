import numpy as np
import sys
sys.path.insert(0,'/mnt/agents/output/.scratch/beat172-qfa-replay-01/inputs')
from npa_twirl import TwirlNPA
class CanonicalTwirlNPA(TwirlNPA):
    """Same frozen SDP engine; complete commuting-projector normal form.
    Within each party all operators commute. Products are sorted; repeated
    projectors collapse and distinct outcomes of one POVM annihilate.
    """
    def norm_side(self,seq):
        if not seq:return tuple()
        ordered=tuple(sorted(seq))
        by={}
        for l in ordered:by.setdefault(self.povm_of[l],[]).append(l)
        out=[]
        for povm,ls in by.items():
            u=set(ls)
            if len(u)>1:return None
            out.append(ls[0])
        return tuple(sorted(out))
    def norm_class(self,seq):
        As=tuple(l for l in seq if self.povm_of[l][0]==0)
        Bs=tuple(l for l in seq if self.povm_of[l][0]==1)
        ra=self.norm_side(As);rb=self.norm_side(Bs)
        if ra is None or rb is None:return 'Z'
        return (ra,rb)
    def class_key(self,wi,wj):
        key=(wi,wj);c=self._classcache.get(key)
        if c is not None:return c
        c=self.norm_class(tuple(reversed(self.W[wi]))+self.W[wj])
        self._classcache[key]=c;return c
    def _g_on_class(self,ck,gi):
        if ck=='Z':return 'Z'
        g=self.G[gi];ra,rb=ck
        return self.norm_class(tuple(g[l] for l in ra+rb))
