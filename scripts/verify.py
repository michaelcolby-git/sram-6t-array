"""Generate and verify a 2x2 SRAM array with ideal peripheral controls."""
import json
from pathlib import Path
from spice_utils import simulate,at,logic,svg
ROOT=Path(__file__).resolve().parents[1]
def pwl(name,node,points): return f'V{name} {node} 0 PWL('+ ' '.join(f'{t}n {v}' for t,v in points)+')'
def pulse_windows(windows,voltage=1):
    p=[(0,0)]
    for start,end in windows: p.extend([(start,0),(start+.1,voltage),(end,voltage),(end+.1,0)])
    return p
def make_deck(name,vdd,temp,pd,ax,pu):
    lines=['2x2 SRAM read write hold reference','.include spice/cell.cir',f'.temp {temp}',f'VDD vdd 0 {vdd}',
           '.model SW SW(Ron=10 Roff=1e12 Vt=0.5 Vh=0.05)']
    # Each row is written as a word: row0=10, row1=01, later row0=01.
    for row in range(2):
        for col in range(2):
            lines += [f'X{row}{col} q{row}{col} qb{row}{col} bl{col} bb{col} wl{row} vdd 0 sram6t PD={pd} AX={ax} PU={pu}',
                      f'Cq{row}{col} q{row}{col} 0 2f',f'Cqb{row}{col} qb{row}{col} 0 2f']
    lines += [pwl('wl0','wl0',pulse_windows([(10,18),(50,58),(90,98),(110,118)],vdd)),
              pwl('wl1','wl1',pulse_windows([(30,38),(70,78),(130,138)],vdd)),
              pwl('write','write',pulse_windows([(5,20),(25,40),(85,100)])),
              pwl('pre','pre',pulse_windows([(42,48),(62,68),(102,108),(122,128)]))]
    for col in range(2):
        first=vdd if col==0 else 0; other=vdd-first
        points=[(0,first),(23,first),(23.1,other),(150,other)]
        inverse=[(t,vdd-v) for t,v in points]
        lines += [pwl(f'd{col}',f'd{col}',points),pwl(f'db{col}',f'db{col}',inverse),
                  f'Sw{col} bl{col} d{col} write 0 SW',f'Swb{col} bb{col} db{col} write 0 SW',
                  f'Sp{col} bl{col} vdd pre 0 SW',f'Spb{col} bb{col} vdd pre 0 SW',
                  f'Cbl{col} bl{col} 0 100f',f'Cbb{col} bb{col} 0 100f']
    # Deterministic initial state; both polarities are then exercised through writes.
    lines += ['.ic '+ ' '.join(f'V(q{r}{c})=0 V(qb{r}{c})={vdd}' for r in range(2) for c in range(2)),
              '.control','set noaskquit','set wr_singlescale','set wr_vecnames','tran 0.02n 150n 0 0.02n uic',
              'let power = -v(vdd)*i(VDD)',f'wrdata build/{name}.dat '+ ' '.join(f'v(q{r}{c}) v(qb{r}{c})' for r in range(2) for c in range(2))+' v(bl0) v(bb0) v(bl1) v(bb1) v(wl0) v(wl1) power',
              'quit','.endc','.end']
    return '\n'.join(lines)
def main():
    results=[]
    for vdd,temp,pd,ax,pu in [(1.8,25,2e-6,1e-6,.6e-6),(1.62,85,2e-6,1e-6,.6e-6),(1.98,-20,2e-6,1e-6,.6e-6),(1.8,25,2.4e-6,1e-6,.6e-6)]:
        name=f'array_{len(results)}'; deck=make_deck(name,vdd,temp,pd,ax,pu)
        rows=simulate(ROOT,name,deck)
        checks=0
        for t,expected in [(22,[1,0,0,0]),(40,[1,0,0,1]),(60,[1,0,0,1]),(80,[1,0,0,1]),(100,[0,1,0,1]),(120,[0,1,0,1]),(140,[0,1,0,1]),(149,[0,1,0,1])]:
            for i,value in enumerate(expected):
                q=logic(at(rows,t*1e-9,1+i*2),vdd); qb=logic(at(rows,t*1e-9,2+i*2),vdd)
                if (q,qb)!=(value,1-value): raise AssertionError((name,t,i,q,qb,value))
                checks+=1
        diffs=[]
        for t,expected in [(52,[1,0]),(72,[0,1]),(112,[0,1]),(132,[0,1])]:
            for col,value in enumerate(expected):
                diff=at(rows,t*1e-9,9+col*2)-at(rows,t*1e-9,10+col*2)
                if (diff if value else -diff)<.1*vdd: raise AssertionError((name,'insufficient read differential',t,col,diff))
                diffs.append(abs(diff))
        results.append(dict(name=name,vdd=vdd,temperature_c=temp,pull_down_w_m=pd,access_w_m=ax,pull_up_w_m=pu,
                            state_checks=checks,read_checks=len(diffs),min_read_differential_v=min(diffs)))
        if name=='array_0':
            (ROOT/'spice/array_2x2.cir').write_text(deck)
            svg(rows,[('Q00',1,'#58a6ff'),('Q01',3,'#3fb950'),('WL0',13,'#d29922')],ROOT/'build/array-operation.svg','6T SRAM | write, read, overwrite, retention',vdd)
    (ROOT/'build/results.json').write_text(json.dumps({'model':'generic Level-1','cases':results},indent=2)+'\n')
    print(f'PASS {len(results)} SRAM configurations; {sum(x["state_checks"] for x in results)} cell-state checks; {sum(x["read_checks"] for x in results)} bitline-differential checks')
if __name__=='__main__': main()
