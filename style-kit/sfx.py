import numpy as np,wave
sr=44100;w=wave.open('../013.wav');raw=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float);ch=w.getnchannels();
if ch==2: raw=raw.reshape(-1,2).mean(1)
sr0=w.getframerate();n=int(63*sr);v=np.zeros(n);v[:min(n,len(raw))]=raw[:n]
fx=np.zeros(n)
def add(t,sig,g=1):
    i=int(t*sr);e=min(n,i+len(sig));fx[i:e]+=sig[:e-i]*g
def tone(f,d,dec=30):
    x=np.arange(int(d*sr))/sr;return np.sin(2*np.pi*f*x)*np.exp(-dec*x)
pop=lambda:tone(740,.12,35)+.4*tone(1180,.12,50)
tick=lambda:tone(1500,.03,120)
thud=lambda:tone(90,.3,12)
ding=lambda:tone(1320,.35,10)+.5*tone(1980,.35,14)
add(.05,thud(),1.3)
for t in [6.2,11.1,24.6,31.5,40.2,40.5,41.6,46.5,46.8,47.1,48.5,52.8,55.6]: add(t,pop(),.8)
for t in np.arange(2.4,4.2,.09): add(float(t),tick(),.35)
for t in np.arange(15.6,18.7,.11): add(float(t),tick(),.3)
for t in np.arange(21.3,23.8,.11): add(float(t),tick(),.3)
for t in [18.8,23.9,35.1,36.4,37.3,55.65]: add(t,ding(),.5)
for t in np.arange(25,26.8,.08): add(float(t),tick(),.35)
mix=v+fx*2200
mix=np.clip(mix,-32000,32000).astype(np.int16)
o=wave.open('mix.wav','w');o.setnchannels(1);o.setsampwidth(2);o.setframerate(sr);o.writeframes(mix.tobytes());o.close();print(sr0,ch)
