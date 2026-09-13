"""Small stdlib-only ngspice runner and numeric waveform utilities."""
import math,os,re,subprocess
from pathlib import Path
def simulate(root,name,deck):
    build=root/'build'; build.mkdir(exist_ok=True)
    path=build/(name+'.cir'); path.write_text(deck)
    p=subprocess.run([os.getenv('NGSPICE','ngspice'),'-b',str(path.relative_to(root))],cwd=root,
                     text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    (build/(name+'.log')).write_text(p.stdout)
    if p.returncode or re.search(r'(?im)^\s*(?:error|fatal)|timestep too small|simulation interrupted',p.stdout):
        raise RuntimeError(f'{name}: ngspice failed; see {build/(name+".log")}\n'+p.stdout[-2000:])
    data=build/(name+'.dat')
    if not data.exists(): raise RuntimeError('Missing waveform '+str(data))
    rows=[]
    for line in data.read_text().splitlines():
        try: row=[float(x) for x in line.split()]
        except ValueError: continue
        if row:
            if not all(math.isfinite(x) for x in row): raise ValueError('Nonfinite waveform')
            rows.append(row)
    if len(rows)<2: raise ValueError('Empty waveform')
    return rows
def at(rows,t,col):
    if not rows[0][0]<=t<=rows[-1][0]: raise ValueError('Sample outside waveform')
    for a,b in zip(rows,rows[1:]):
        if a[0]<=t<=b[0] and b[0]>a[0]:
            return a[col]+(b[col]-a[col])*(t-a[0])/(b[0]-a[0])
    raise ValueError('Unable to interpolate')
def crossing(rows,col,level,start,stop,rising):
    for a,b in zip(rows,rows[1:]):
        if b[0]<start or a[0]>stop: continue
        yes=(a[col]<level<=b[col]) if rising else (a[col]>level>=b[col])
        if yes:
            t=a[0]+(level-a[col])*(b[0]-a[0])/(b[col]-a[col])
            if start<=t<=stop: return t
    raise ValueError('Expected crossing absent')
def average(rows,col,start,stop):
    points=[[start,at(rows,start,col)]]+[[r[0],r[col]] for r in rows if start<r[0]<stop]+[[stop,at(rows,stop,col)]]
    return sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(points,points[1:]))/(stop-start)
def logic(value,vdd):
    if value < .2*vdd: return 0
    if value > .8*vdd: return 1
    raise AssertionError(f'Invalid logic level {value} at VDD={vdd}')
def svg(rows,series,path,title,vdd):
    """Write a simple, readable waveform SVG with time and voltage axes."""
    from html import escape
    width,height=1000,360; left,top=70,50; w,h=880,245
    lo,hi=rows[0][0],rows[-1][0]
    text=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
          '<rect width="100%" height="100%" fill="#0d1117"/>',
          f'<text x="70" y="26" fill="#f0f6fc" font-family="sans-serif" font-size="18">{escape(title)}</text>']
    for i in range(6):
        x=left+i*w/5
        text += [f'<path d="M{x},{top} V{top+h}" stroke="#30363d"/>',f'<text x="{x}" y="{top+h+22}" text-anchor="middle" fill="#c9d1d9" font-family="sans-serif" font-size="12">{(lo+(hi-lo)*i/5)*1e9:.0f}</text>']
    for fraction in (0,.5,1):
        y=top+h*(1-fraction)
        text += [f'<path d="M{left},{y} H{left+w}" stroke="#30363d"/>',f'<text x="58" y="{y+4}" text-anchor="end" fill="#c9d1d9" font-family="sans-serif" font-size="12">{fraction*vdd:.2f}</text>']
    for idx,(name,col,color) in enumerate(series):
        # Retain dense data for edge accuracy; only reduce very large traces.
        step=max(1,len(rows)//5000)
        pts=' '.join(f'{left+(r[0]-lo)/(hi-lo)*w:.2f},{top+h*(1-r[col]/vdd):.2f}' for r in rows[::step])
        text += [f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5"/>',f'<text x="{110+idx*170}" y="345" fill="{color}" font-family="sans-serif" font-size="13">{escape(name)}</text>']
    text+=['<text x="925" y="322" fill="#c9d1d9" font-family="sans-serif" font-size="12">Time (ns)</text>', '<text x="10" y="30" fill="#c9d1d9" font-family="sans-serif" font-size="12">V</text>','</svg>']
    path.write_text('\n'.join(text))
