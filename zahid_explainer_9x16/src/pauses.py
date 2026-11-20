import numpy as np, wave, json
w=wave.open('voice16k.wav'); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
hop=int(sr*0.010); win=int(sr*0.025)
n=(len(x)-win)//hop
rms=np.array([np.sqrt(np.mean(x[i*hop:i*hop+win]**2)) for i in range(n)])
db=20*np.log10(rms+1e-7)
print('dur',len(x)/sr,'db pcts',np.percentile(db,[5,10,25,50,75,95]))
np.save('db.npy',db)
