# bp09/test_twirl.py -- validation ladder for the twirl engine
# Ladder: W-L1 twirled == 0.7803300859 ; RAC4-L1 twirled == 0.7803300859 (both certified untwirled in beat-129)
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from npa_twirl import TwirlNPA

def build_W_1AB():  # W game, 1+AB basis (153 words): target = beat-129 certified W-1AB UB
    A=[('A',u,a) for u in range(4) for a in range(4)]
    B=[('B',y,b) for y in range(2) for b in range(4)]
    letters=A+B
    povm_of={}
    for u in range(4):
        for a in range(4): povm_of[letters.index(('A',u,a))]=(0,u)
    for y in range(2):
        for b in range(4): povm_of[letters.index(('B',y,b))]=(1,y)
    words=[()]+[(i,) for i in range(len(letters))]+[(ai,bi) for ai in range(16) for bi in range(16,24)]
    # group Z4 shift: a->a+1, b->b-1
    gen={}
    for i,l in enumerate(letters):
        if l[0]=='A': gen[i]=letters.index((l[0],l[1],(l[2]+1)%4))
        else: gen[i]=letters.index((l[0],l[1],(l[2]-1)%4))
    gens=[(gen,(1,))]
    obj=[]
    for u in range(4):
        for y in range(2):
            for a in range(4):
                for b in range(4):
                    if (a+b)%4==(u*y)%4:
                        obj.append((1+u*4+a, 1+16+y*4+b, 1.0/8))
    return letters,povm_of,words,gens,obj

def build_RAC4_L1():
    A=[('A',x,m) for x in range(16) for m in range(4)]
    B=[('B',y,m,v) for y in range(2) for m in range(4) for v in range(4)]
    letters=A+B
    povm_of={}
    for x in range(16):
        for m in range(4): povm_of[letters.index(('A',x,m))]=(0,x)
    for y in range(2):
        for m in range(4):
            for v in range(4): povm_of[letters.index(('B',y,m,v))]=(1,y,m)
    words=[()]+[(i,) for i in range(len(letters))]
    def shift_x(i,d1,d2):
        l=letters[i]
        if l[0]=='A':
            _,x,m=l; X1,X2=x//4,x%4
            return letters.index(('A',((X1+d1)%4)*4+((X2+d2)%4),m))
        else:
            _,y,m,v=l
            dv=d1 if y==0 else d2
            return letters.index(('B',y,m,(v+dv)%4))
    def shift_m(i):
        l=letters[i]
        if l[0]=='A': return letters.index(('A',l[1],(l[2]+1)%4))
        return letters.index(('B',l[1],(l[2]+1)%4,l[3]))
    gens=[({i:shift_x(i,1,0) for i in range(len(letters))},(1,0,0)),
          ({i:shift_x(i,0,1) for i in range(len(letters))},(0,1,0)),
          ({i:shift_m(i) for i in range(len(letters))},(0,0,1))]
    obj=[]
    for x in range(16):
        Xy=[x//4,x%4]
        for y in range(2):
            for m in range(4):
                obj.append((1+x*4+m, 1+64+(y*4+m)*4+Xy[y], 1.0/32))
    return letters,povm_of,words,gens,obj

def make_chars_Z4(T):
    # one generator, chars p=0,1,2 (p=3 is conjugate of p=1)
    w=1j
    chars=[[w**(p*e[0]) for e in T.exps] for p in [0,1,2]]
    return chars,['p0','p1','p2']

def build_RAC4_1AB():
    letters,povm_of,words0,gens,obj=build_RAC4_L1()
    nA=64; nB=32
    words=words0+[(ai,bi) for ai in range(nA) for bi in range(nA,nA+nB)]
    return letters,povm_of,words,gens,obj

def make_chars_Z4cube(T):
    # chars (p,q,r); keep one per conjugate pair: (p,q,r) <= (-p,-q,-r)%4 lex
    w=1j; sel=[]
    for p in range(4):
        for q in range(4):
            for r in range(4):
                neg=((-p)%4,(-q)%4,(-r)%4)
                if (p,q,r)<=neg: sel.append((p,q,r))
    chars=[[w**(p*e[0]+q*e[1]+r*e[2]) for e in T.exps] for (p,q,r) in sel]
    return chars,[str(s) for s in sel]

if __name__=='__main__':
    which=sys.argv[1] if len(sys.argv)>1 else 'W'
    if which=='W':
        letters,povm_of,words,gens,obj=build_W_1AB()
        T=TwirlNPA(letters,povm_of,words,gens,obj)
        chars,names=make_chars_Z4(T); T.set_chars(chars,names)
        T.build()
        r=T.solve(mu=0.1,iters=1500)
        print('W-1AB twirled: cert=%.10f  target<=0.7441360147 (and >= see-saw 0.7404886669)'%r['cert'])
    else:
        letters,povm_of,words,gens,obj=build_RAC4_L1()
        T=TwirlNPA(letters,povm_of,words,gens,obj)
        chars,names=make_chars_Z4cube(T); T.set_chars(chars,names)
        T.build()
        r=T.solve(mu=0.1,iters=1500)
        print('RAC4-L1 twirled: cert=%.10f  target=0.7803300859'%r['cert'])
