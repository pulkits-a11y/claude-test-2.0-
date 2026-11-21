import subprocess, sys, os, json
R='/home/user/claude-test-2.0-/nike-reel'
def dur(p): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
def row(bid, t0, t1, n, w=192):
    src=f'{R}/Sources/broll/{bid}.mp4'; d=dur(src); t1=min(t1,d-0.2); ts=[t0+(t1-t0)*i/(n-1) for i in range(n)]
    files=[]
    for i,t in enumerate(ts):
        f=f'_{bid}_{int(t0)}_{i:02d}.png'
        subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{t:.2f}','-i',src,'-frames:v','1','-vf',f"scale={w}:{w*9//16},drawtext=text='{bid} {t:.1f}':x=2:y=2:fontsize=12:fontcolor=yellow:box=1:boxcolor=black@0.7",f])
        files.append(f)
    return files
groups = json.loads(sys.argv[1])
for name, specs in groups.items():
    rows=[]
    for bid,t0,t1,n in specs: rows.append(row(bid,t0,t1,n))
    n=max(len(r) for r in rows)
    lst=[f for r in rows for f in r]
    subprocess.run(['ffmpeg','-v','error','-y']+sum([['-i',f] for f in lst],[])+['-filter_complex',''.join(f'[{i}]' for i in range(len(lst)))+f'xstack=inputs={len(lst)}:layout='+'|'.join(f'{c*192}_{r*108}' for r in range(len(rows)) for c in range(len(rows[r])))+'[o]','-map','[o]',f'{name}.png'])
    for f in lst: os.remove(f)
    print(name, len(rows), 'rows')
