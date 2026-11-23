# Original hyped music bed for Rich in Life, made in code (no samples, no licence issues).
# 140 BPM, A minor: punchy kick, clap, fast hats, 808 bass slides, dark synth stabs. 32 bars, loops cleanly.
import numpy as np, wave, sys
SR=44100; BPM=140; beat=60/BPM; bar=4*beat; BARS=40
N=int(BARS*bar*SR); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(3)
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); e=min(N,i+len(sig))
    if i>=N: return
    L[i:e]+=sig[:e-i]*g*(1-max(0,pan)); R[i:e]+=sig[:e-i]*g*(1+min(0,pan))
def env(n,a=0.002,d=0.2):
    t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/d)
def kick():
    n=int(0.45*SR); t=np.arange(n)/SR
    f=45+110*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*7)+0.3*np.sin(ph)*np.exp(-t*40)
    click=rng.normal(0,1,n)*np.exp(-t*400)*0.3
    return np.tanh(2.2*(s+click))
def clap():
    n=int(0.3*SR); t=np.arange(n)/SR; nz=rng.normal(0,1,n)
    e=np.zeros(n)
    for o in (0,0.011,0.022): e+=np.exp(-np.clip(t-o,0,None)*60)*(t>=o)
    e+=np.exp(-t*14)*0.5
    from numpy.fft import rfft,irfft
    X=rfft(nz*e); fr=np.fft.rfftfreq(n,1/SR); X*=((fr>900)&(fr<6000)); return irfft(X,n)*3
def hat(open_=False):
    n=int((0.18 if open_ else 0.05)*SR); t=np.arange(n)/SR; nz=rng.normal(0,1,n)
    nz=np.diff(np.concatenate([[0],nz])); return nz*np.exp(-t*(18 if open_ else 90))*0.5
def b808(freq,dur,slide_to=None):
    n=int(dur*SR); t=np.arange(n)/SR
    f=np.full(n,freq) if slide_to is None else freq+(slide_to-freq)*np.clip((t-dur*0.6)/(dur*0.3),0,1)
    s=np.sin(2*np.pi*np.cumsum(f)/SR); return np.tanh(1.8*s)*env(n,0.003,dur*0.9)
def stab(freqs,dur):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for f in freqs:
        for det in (-0.12,0,0.12):
            ph=(t*f*(1+det/100))%1; s+=(2*ph-1)
    s/=len(freqs)*3; return s*env(n,0.004,0.18)
A=55.0
def hz(semi): return A*2**(semi/12)
# progression (A minor): Am - F - G - Em
prog=[(0,[12,15,19]),(-4,[8,12,15]),(-2,[10,14,17]),(-5,[7,10,14])]
K=kick();C=clap();H=hat();HO=hat(True)
for b in range(BARS):
    t0=b*bar; root,ch=prog[b%4]
    intro = b<2
    # kick pattern (trap-ish)
    for k in ([0,2.5] if b%2==0 else [0,1.75,2.5]):
        if not intro or k==0: add(K,t0+k*beat,0.9)
    if not intro:
        for c in (1,3): add(C,t0+c*beat,0.55)
    # hats: 8ths, with 16th/32nd rolls at bar end
    for s in range(16):
        tt=t0+s*beat/4
        if s%2==0 or (b%2==1 and s>=12): add(H,tt,0.35 if s%4==0 else 0.22,pan=0.3 if s%2 else -0.2)
    if b%4==3:
        for r in range(6): add(H,t0+3.5*beat+r*beat/12,0.18)
    add(HO,t0+3.5*beat,0.2,pan=0.4)
    # 808
    if not intro:
        add(b808(hz(root),beat*1.9),t0,0.75)
        add(b808(hz(root),beat*1.4, hz(root+(3 if b%2 else 7))),t0+2.5*beat,0.7)
    # stabs on offbeats
    for s in (0,0.75,1.5,2.5,3.25):
        add(stab([hz(root+n+12) for n in ch],beat*0.5),t0+s*beat,0.22 if not intro else 0.3,pan=0.15)
# riser into bar 2 (drop)
n=int(bar*SR); t=np.arange(n)/SR; nz=rng.normal(0,1,n)*(t/bar)**2*0.25; add(nz,bar,1.0)
mix=np.stack([L,R],1); mix=np.tanh(mix*1.3); mix/=np.abs(mix).max()*1.12
o=wave.open(sys.argv[1],'w'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((mix*32767).astype(np.int16).tobytes()); o.close()
print(N/SR,'s')
