import json, subprocess
VO='/root/.claude/uploads/4fb0ae1d-39b3-5573-9ed2-8168ea5e1189/f2e6ea7d-Soi_Muban_Rewat_Niwet_2_4.m4a'
segs=[(7.30,10.60),(12.30,13.10),(13.90,14.65),(16.60,17.40),(18.15,19.90),(21.35,22.50),(23.10,23.80),(25.55,27.00),(27.35,29.85),(30.55,34.90)]
PAD=0.08
gaps_after=[1.2,0.35,1.2,0.35,1.2,0.35,1.2,0.35,0.35,0.6]  # 1.2 = ช่วงนับถอยหลัง
LEAD=0.15
t=LEAD; times=[]
fc=[];parts=[]
fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{LEAD}[z0]"); parts.append("[z0]")
for i,((s,e),g) in enumerate(zip(segs,gaps_after)):
    s0,e0=s-PAD,e+PAD
    times.append((round(t,3),round(t+(e0-s0),3)))
    fc.append(f"[0:a]atrim={s0}:{e0},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={e0-s0-0.04:.3f}:d=0.04,aformat=sample_rates=48000:channel_layouts=stereo[p{i}]")
    fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{g}[g{i}]"); parts+= [f"[p{i}]",f"[g{i}]"]
    t+=(e0-s0)+g
fc.append("".join(parts)+f"concat=n={len(parts)}:v=0:a=1,highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11[out]")
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',VO,'-filter_complex',';'.join(fc),'-map','[out]','-ar','44100','vo.wav'],check=True)
total=round(t,2)
T=times
hook,fh,q2,gob,q3,qot,q4,dots,last,outro=T
plan=json.load(open('plan-viral.json'))
plan['duration']=total
plan['challenge']={"text":"คอซีรีส์ต้องทายได้!","until":hook[1]}
q=plan['questions']
q[0].update(start=0.0,countdown=hook[1]+0.05,reveal=fh[0])
q[1].update(start=q2[0]-0.1,countdown=q2[1]+0.05,reveal=gob[0])
q[2].update(start=q3[0]-0.1,countdown=q3[1]+0.05,reveal=qot[0])
q[3].update(start=q4[0]-0.1,countdown=q4[1]+0.05,reveal=dots[0])
q[4].update(start=last[0]-0.1)
plan['outro']['start']=outro[0]-0.1
json.dump(plan,open('plan-final.json','w'),ensure_ascii=False,indent=1)
subs=[
 {"start":0.0,"end":hook[1]+0.05,"text":"[คอซีรีส์]ต้องทายได้\nข้อแรกง่ายมาก"},
 {"start":q2[0]-0.1,"end":gob[0],"text":"[ข้อสอง]"},
 {"start":q3[0]-0.1,"end":qot[0],"text":"ข้อสาม [เริ่มยาก]ละ"},
 {"start":q4[0]-0.1,"end":dots[0],"text":"[ข้อสี่]"},
 {"start":last[0]-0.1,"end":outro[0]-0.1,"text":"ข้อสุดท้าย [ยากสุด]\nไม่เฉลยนะ"},
]
json.dump(subs,open('subs-final.json','w'),ensure_ascii=False,indent=1)
print('total',total); print(T)
