#!/usr/bin/env python3
"""TTS for each segment: edge-tts zh-TW-YunJheNeural
Usage: python3 tts.py REEL_DIR"""
import json, os, re, subprocess, sys, time
try: import edge_tts
except ImportError: subprocess.run([sys.executable,'-m','pip','install','-q','edge-tts'],check=True)
d=sys.argv[1]; os.makedirs(d+'/audio',exist_ok=True)
s=json.load(open(d+'/script.json'))
LANG=json.load(open(d+'/meta.json')).get('lang','zh') if os.path.exists(d+'/meta.json') else 'zh'
VOICE,RATE=('en-US-AndrewNeural','+5%') if LANG=='en' else ('zh-TW-YunJheNeural','+15%')
ENV={k:v for k,v in os.environ.items() if 'proxy' not in k.lower()}
ENV['PYTHONPATH']=os.path.join(os.path.dirname(os.path.abspath(__file__)),'.pylib')+':'+ENV.get('PYTHONPATH','')
for x in s:
    raw=f"{d}/audio/raw{x['id']}.mp3"; wav=f"{d}/audio/s{x['id']}.wav"
    if os.path.exists(wav) and os.path.getsize(wav)>1000: continue
    texts=[x['say'], re.sub(r'[！!？?～~「」『』]', '，', x['say']).strip('，')]
    ok=False
    for attempt in range(30):
        t=texts[attempt%2]
        r=subprocess.run([sys.executable,'-m','edge_tts','--voice',VOICE,'--rate='+RATE,'--text',t,'--write-media',raw],env=ENV,capture_output=True,text=True)
        if r.returncode==0 and os.path.exists(raw) and os.path.getsize(raw)>1000: ok=True; break
        time.sleep(min(1+attempt,8))
    if not ok: raise SystemExit('edge-tts failed (請稍後重跑 tts.py，不要換聲音): '+r.stderr[-500:])
    subprocess.run(['ffmpeg','-v','error','-y','-i',raw,'-ar','44100','-ac','1',wav],check=True)
print('tts engine: edge-tts',VOICE)
