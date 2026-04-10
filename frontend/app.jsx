import { useState, useEffect, useMemo, useCallback } from "react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, ComposedChart, Area, Legend, ReferenceLine, ScatterChart, Scatter } from "recharts";
import { Home, Database, Map as MapIcon, BarChart3, Search, Lightbulb, GitBranch, Target, FileText, ChevronRight, ChevronDown, AlertTriangle, CheckCircle, XCircle, TrendingUp, TrendingDown, DollarSign, Users, Activity, Zap, ArrowUpRight, ArrowDownRight, ArrowRight, Filter, Upload, Play, Download, Lock, Unlock, Plus, Trash2, Info, Check, X, UploadCloud, Shield, Eye, RefreshCw, Layers, ChevronUp, Columns, FileSpreadsheet, BarChart2, PieChart as PieIcon, ArrowDown, ArrowUp, Minus, Copy, Settings, Grid } from "lucide-react";

/* ══════════════════════════════════════
   DATA ENGINE
   ══════════════════════════════════════ */
const CH={paid_search:{type:"online",color:"#3b82f6",sat:150000,a:.55,label:"Paid Search"},organic_search:{type:"online",color:"#059669",sat:null,a:.7,label:"Organic Search"},social_paid:{type:"online",color:"#7c3aed",sat:120000,a:.5,label:"Social Paid"},display:{type:"online",color:"#d97706",sat:80000,a:.45,label:"Display"},email:{type:"online",color:"#0891b2",sat:40000,a:.6,label:"Email"},video_youtube:{type:"online",color:"#dc2626",sat:100000,a:.48,label:"Video/YouTube"},events:{type:"offline",color:"#be185d",sat:200000,a:.65,label:"Events"},direct_mail:{type:"offline",color:"#65a30d",sat:60000,a:.42,label:"Direct Mail"},tv_national:{type:"offline",color:"#9333ea",sat:300000,a:.35,label:"TV National"},radio:{type:"offline",color:"#ea580c",sat:80000,a:.38,label:"Radio"},ooh:{type:"offline",color:"#0d9488",sat:100000,a:.32,label:"OOH/Billboard"},call_center:{type:"offline",color:"#64748b",sat:50000,a:.55,label:"Call Center"}};
const CAMPS={paid_search:["PS Brand","PS Generic","PS Competitor","PS Product"],organic_search:["SEO Blog","SEO Product Pages"],social_paid:["Meta Awareness","Meta Retargeting","LinkedIn LeadGen","TikTok Brand"],display:["Programmatic","Display Retargeting","Native Ads"],email:["Newsletter","Nurture","Promo Blast","Winback"],video_youtube:["Pre-Roll","Discovery","Shorts"],events:["Trade Show","Webinar","Conference"],direct_mail:["Catalog","PostCard"],tv_national:["TV Brand Q1","TV Product Launch"],radio:["Radio Regional","Radio Sponsorship"],ooh:["Billboard Highway","Transit Ads"],call_center:["Inbound Sales","Outbound Campaign"]};
const MO=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const SEA=[.85,.8,.95,1.05,1.1,1,.9,.88,1.05,1.15,1.25,1.3];
const REG=["North","South","East","West"];
const PROD=["Product A","Product B","Product C"];
function sr(s){let x=s;return()=>{x=(x*16807)%2147483647;return(x-1)/2147483646}}
function gen(){const r=sr(42),n=(v,p=.1)=>Math.max(0,v*(1+(r()-.5)*2*p));const rows=[],js=[];
const bS={paid_search:11e3,organic_search:700,social_paid:8500,display:5500,email:1600,video_youtube:6500,events:14e3,direct_mail:4500,tv_national:25e3,radio:6e3,ooh:8e3,call_center:3e3};
const bCT={paid_search:.045,organic_search:.035,social_paid:.012,display:.004,email:.22,video_youtube:.008,events:.5,direct_mail:.15,tv_national:0,radio:0,ooh:0,call_center:.4};
const bCV={paid_search:.03,organic_search:.035,social_paid:.014,display:.006,email:.045,video_youtube:.009,events:.065,direct_mail:.018,tv_national:.001,radio:.002,ooh:.001,call_center:.04};
const aov={paid_search:380,organic_search:440,social_paid:260,display:175,email:320,video_youtube:230,events:1100,direct_mail:350,tv_national:500,radio:300,ooh:400,call_center:600};
const imp={paid_search:8,organic_search:12,social_paid:15,display:25,email:3,video_youtube:10,events:.5,direct_mail:.8,tv_national:0,radio:0,ooh:0,call_center:0};
const bnc={paid_search:.38,organic_search:.42,social_paid:.55,display:.65,email:.3,video_youtube:.5,events:.15,direct_mail:.45,tv_national:0,radio:0,ooh:0,call_center:.2};
const sd={paid_search:145,organic_search:195,social_paid:85,display:55,email:165,video_youtube:70,events:300,direct_mail:120,tv_national:0,radio:0,ooh:0,call_center:180};
const fr={paid_search:.12,organic_search:.09,social_paid:.06,display:.025,email:.18,video_youtube:.04,events:.45,direct_mail:.1,tv_national:0,radio:0,ooh:0,call_center:.3};
const np={paid_search:35,organic_search:52,social_paid:28,display:18,email:42,video_youtube:30,events:65,direct_mail:25,tv_national:40,radio:30,ooh:20,call_center:45};
Object.entries(CH).forEach(([ch,ci])=>{CAMPS[ch].forEach(camp=>{MO.forEach((mo,mi)=>{REG.forEach(reg=>{const rm={North:1.1,South:.9,East:1,West:1.05}[reg],cm=.7+(camp.length%5)*.12;let sp=n(bS[ch]*SEA[mi]*rm*cm,.12);if(ch==="organic_search")sp=n(700*rm,.05);const ef=ci.sat?ci.sat*Math.pow(sp/ci.sat,ci.a):sp;const im=n(ef*imp[ch],.15),cl=n(im*bCT[ch],.12),le=n(cl*.07,.15),mq=n(le*.45,.1),sq=n(mq*.38,.1),cv=Math.max(0,Math.round(n(sq*bCV[ch]*SEA[mi]*8,.18))),rv=cv*n(aov[ch],.1);let b=bnc[ch];if(camp.includes("Retarget"))b*=.75;if(camp.includes("Awareness")||camp.includes("Brand"))b*=1.15;let f=fr[ch];if(camp==="TikTok Brand"||camp==="Native Ads")f*=.4;
rows.push({month:`2025-${String(mi+1).padStart(2,"0")}`,ml:mo,ch,ct:ci.type,camp,reg,prod:PROD[Math.floor(r()*3)],spend:Math.round(sp),imps:Math.round(im),clicks:Math.round(cl),leads:Math.round(le),mqls:Math.round(mq),sqls:Math.round(sq),conv:cv,rev:Math.round(rv),br:Math.min(1,Math.max(0,n(b,.1))),sd:Math.max(0,n(sd[ch],.2)),fc:Math.min(1,Math.max(0,f)),nps:Math.round(n(np[ch],.05)),conf:ci.type==="online"?"High":(ch==="events"||ch==="direct_mail")?"Model-Est":"Medium"})})})})});
const chL=Object.keys(CH);for(let j=0;j<3e3;j++){const nt=[1,2,3,4,5][Math.floor(r()*5)],cv=r()<.35,jR=cv?n([400,800,1500,3e3][Math.floor(r()*4)],.3):0,tps=[];for(let t=0;t<nt;t++){const c=chL[Math.floor(r()*chL.length)];tps.push({ch:c,camp:CAMPS[c][Math.floor(r()*CAMPS[c].length)],o:t+1})}js.push({id:`J${j}`,tps,cv,rv:Math.round(jR),nt})}return{rows,js}}

/* ═ ENGINES ═ */
function runAttr(js){const m={last_touch:{},linear:{},position_based:{}};js.filter(j=>j.cv).forEach(j=>{j.tps.forEach((tp,i)=>{const k=tp.ch;if(i===j.nt-1)m.last_touch[k]=(m.last_touch[k]||0)+j.rv;m.linear[k]=(m.linear[k]||0)+j.rv/j.nt;let w=1;if(j.nt===1)w=1;else if(j.nt===2)w=.5;else if(i===0)w=.4;else if(i===j.nt-1)w=.4;else w=.2/(j.nt-2);m.position_based[k]=(m.position_based[k]||0)+j.rv*w})});return m}

function fitC(rows){const c={};Object.keys(CH).forEach(ch=>{const d={};rows.filter(r=>r.ch===ch).forEach(r=>{if(!d[r.month])d[r.month]={s:0,r:0};d[r.month].s+=r.spend;d[r.month].r+=r.rev});const pts=Object.values(d);if(pts.length<3)return;const xs=pts.map(p=>p.s),ys=pts.map(p=>p.r),lx=xs.map(x=>Math.log(Math.max(x,1))),ly=ys.map(y=>Math.log(Math.max(y,1))),mx=lx.reduce((a,b)=>a+b,0)/lx.length,my=ly.reduce((a,b)=>a+b,0)/ly.length;let nm=0,dn=0;lx.forEach((l,i)=>{nm+=(l-mx)*(ly[i]-my);dn+=(l-mx)**2});const b=dn>0?Math.min(.95,Math.max(.1,nm/dn)):.5,a=Math.exp(my-b*mx),ax=xs.reduce((a,b)=>a+b,0)/xs.length,sat=Math.pow(a*b,1/(1-b)),mR=a*b*Math.pow(Math.max(ax,1),b-1),hd=Math.max(0,(sat-ax)/sat*100),mx2=Math.max(...xs)*1.5,cp=[];for(let i=0;i<=40;i++){const x=(mx2/40)*i;cp.push({spend:Math.round(x),revenue:Math.round(a*Math.pow(Math.max(x,1),b))})}c[ch]={a,b,avgSpend:ax,satSpend:sat,mROI:mR,hd,cp,dp:pts.map(p=>({spend:p.s,revenue:p.r}))}});return c}

function optim(curves,budget,obj="balanced",constraints={}){const chs=Object.keys(curves),n=chs.length;const pred=(ch,s)=>{const c=curves[ch];return c.a*Math.pow(Math.max(s/12,1),c.b)*12};const cur={};chs.forEach(ch=>{cur[ch]=curves[ch].avgSpend*12});const cT=Object.values(cur).reduce((a,b)=>a+b,0),sc=budget/cT;let al={};chs.forEach(ch=>{al[ch]=cur[ch]*sc});
// Apply locks
Object.entries(constraints).forEach(([ch,c])=>{if(c.locked&&c.lockedAmount!=null)al[ch]=c.lockedAmount});
const step=budget*.005;for(let i=0;i<200;i++){const unlocked=chs.filter(ch=>!constraints[ch]?.locked);if(unlocked.length<2)break;let mg=unlocked.map(ch=>{const c=curves[ch];return{ch,m:c.a*c.b*Math.pow(Math.max(al[ch]/12,1),c.b-1)}});mg.sort((a,b)=>b.m-a.m);if(mg[0].m/mg[mg.length-1].m<1.05)break;const worst=mg[mg.length-1],best=mg[0];const minA=constraints[worst.ch]?.min??budget*.02,maxA=constraints[best.ch]?.max??budget*.4;if(al[worst.ch]-step<minA||al[best.ch]+step>maxA)continue;al[worst.ch]-=step;al[best.ch]+=step}
const res=chs.map(ch=>{const oR=pred(ch,al[ch]),cR=pred(ch,cur[ch]),c=curves[ch],mR=c.a*c.b*Math.pow(Math.max(al[ch]/12,1),c.b-1);return{channel:ch,cS:Math.round(cur[ch]),oS:Math.round(al[ch]),chg:((al[ch]-cur[ch])/cur[ch]*100),cR:Math.round(cR),oR:Math.round(oR),rChg:Math.round(oR-cR),cROI:(cR-cur[ch])/cur[ch],oROI:(oR-al[ch])/al[ch],mROI:mR,locked:!!constraints[ch]?.locked}});
const cRev=res.reduce((a,c)=>a+c.cR,0),oRev=res.reduce((a,c)=>a+c.oR,0);
return{channels:res,summary:{cRev,oRev,uplift:((oRev-cRev)/cRev*100),cROI:(cRev-budget)/budget,oROI:(oRev-budget)/budget}}}

function diag(rows,curves,attr){const recs=[];const cm={};rows.forEach(r=>{if(!cm[r.ch])cm[r.ch]={s:0,r:0,cl:0,im:0,cv:0,le:0,mq:0,sq:0,cnt:0};const m=cm[r.ch];m.s+=r.spend;m.r+=r.rev;m.cl+=r.clicks;m.im+=r.imps;m.cv+=r.conv;m.le+=r.leads;m.mq+=r.mqls;m.sq+=r.sqls;m.cnt++});
Object.entries(cm).forEach(([ch,m])=>{m.roi=(m.r-m.s)/m.s;m.ctr=m.cl/Math.max(m.im,1);m.cvr=m.cv/Math.max(m.cl,1);m.cac=m.s/Math.max(m.cv,1)});
const rois=Object.values(cm).map(m=>m.roi).sort((a,b)=>a-b),medROI=rois[Math.floor(rois.length/2)];
const cacs=Object.values(cm).map(m=>m.cac).sort((a,b)=>a-b),medCAC=cacs[Math.floor(cacs.length/2)];
Object.entries(cm).forEach(([ch,m])=>{const cv=curves[ch];if(!cv)return;
if(m.roi>medROI*1.3&&cv.hd>20&&cv.mROI>1.5){const ip=Math.min(cv.hd*.5,40);recs.push({type:"SCALE",ch,rationale:`${CH[ch]?.label} ROI ${m.roi.toFixed(1)}x with ${cv.hd.toFixed(0)}% headroom. Marginal ROI ${cv.mROI.toFixed(1)}x above hurdle.`,action:`Increase spend by ${ip.toFixed(0)}%`,impact:Math.round(m.s*ip/100*cv.mROI*.8),conf:"High",effort:"Low"})}
if(cv.mROI<1.5&&cv.hd<15){recs.push({type:"REDUCE",ch,rationale:`${CH[ch]?.label} marginal ROI ${cv.mROI.toFixed(2)}x below hurdle. ${cv.hd.toFixed(0)}% headroom — near saturation.`,action:"Reduce 15-25%, reallocate to higher-yield channels",impact:Math.round(-m.s*.2*cv.mROI),conf:"High",effort:"Low"})}
if(m.cac>medCAC*1.5){recs.push({type:"RETARGET",ch,rationale:`${CH[ch]?.label} CAC $${m.cac.toFixed(0)} is ${(m.cac/medCAC).toFixed(1)}x median. Bid/audience issue.`,action:"Tighten audience targeting, review bids",impact:Math.round((m.cac-medCAC)*m.cv*.3),conf:"Medium",effort:"Medium"})}});
const cpm={};rows.forEach(r=>{const k=`${r.ch}|||${r.camp}`;if(!cpm[k])cpm[k]={ch:r.ch,camp:r.camp,cl:0,im:0,cv:0,bS:0,fS:0,cnt:0,s:0};const m=cpm[k];m.cl+=r.clicks;m.im+=r.imps;m.cv+=r.conv;m.bS+=r.br;m.fS+=r.fc;m.cnt++;m.s+=r.spend});
const ctrs=Object.values(cpm).map(m=>m.cl/Math.max(m.im,1)).sort((a,b)=>a-b);const cvrs2=Object.values(cpm).map(m=>m.cv/Math.max(m.cl,1)).sort((a,b)=>a-b);
const mCTR=ctrs[Math.floor(ctrs.length/2)],mCVR=cvrs2[Math.floor(cvrs2.length/2)];
Object.values(cpm).forEach(m=>{const ctr=m.cl/Math.max(m.im,1),cvr=m.cv/Math.max(m.cl,1);if(ctr>mCTR*1.5&&cvr<mCVR*.6){recs.push({type:"FIX",ch:m.ch,camp:m.camp,rationale:`${m.camp} CTR ${(ctr*100).toFixed(1)}% but CVR ${(cvr*100).toFixed(2)}%. Landing page issue.`,action:"Audit landing page, test CTAs, review form UX",impact:Math.round(m.cl*(mCVR-cvr)*350*.4),conf:"High",effort:"Medium"})}});
if(attr.last_touch&&attr.linear){Object.keys(attr.last_touch).forEach(ch=>{const lt=attr.last_touch[ch]||0,ln=attr.linear[ch]||0;if(lt>0&&ln/lt>1.4)recs.push({type:"MAINTAIN",ch,rationale:`${CH[ch]?.label} last-touch $${(lt/1e3).toFixed(0)}K vs linear $${(ln/1e3).toFixed(0)}K. Assists conversions elsewhere.`,action:"Maintain spend; don't cut on last-touch",impact:Math.round(ln-lt),conf:"Medium",effort:"None"})})}
Object.entries(cm).forEach(([ch,m])=>{const l2m=m.mq/Math.max(m.le,1);if(l2m<.3)recs.push({type:"RESEQUENCE",ch,rationale:`${CH[ch]?.label} Lead→MQL ${(l2m*100).toFixed(0)}%. Lead quality or nurture issue.`,action:"Review lead scoring, adjust qualification",impact:0,conf:"Medium",effort:"Medium"})});
recs.sort((a,b)=>Math.abs(b.impact||0)-Math.abs(a.impact||0));recs.forEach((r,i)=>{r.id=`REC-${String(i+1).padStart(3,"0")}`;r.priority=i+1;r.status="pending"});return recs}

function pil(rows,opt){const tR=rows.reduce((a,r)=>a+r.rev,0),tS=rows.reduce((a,r)=>a+r.spend,0);const oR=opt.summary.oRev;const leak=Math.max(0,oR-tR);
const chL=opt.channels.filter(c=>c.rChg>0).map(c=>({channel:c.channel,leakage:c.rChg,type:c.chg>5?"underfunded":"aligned"})).sort((a,b)=>b.leakage-a.leakage);
const cpm={};rows.forEach(r=>{const k=`${r.ch}|||${r.camp}`;if(!cpm[k])cpm[k]={ch:r.ch,camp:r.camp,cl:0,cv:0,rv:0,bS:0,fS:0,cnt:0};const m=cpm[k];m.cl+=r.clicks;m.cv+=r.conv;m.rv+=r.rev;m.bS+=r.br;m.fS+=r.fc;m.cnt++});
const cvrs=Object.values(cpm).map(m=>m.cv/Math.max(m.cl,1)).sort((a,b)=>a-b),mCVR=cvrs[Math.floor(cvrs.length/2)];
let tSup=0;const sI=[];Object.values(cpm).forEach(m=>{const cvr=m.cv/Math.max(m.cl,1);if(cvr<mCVR*.7&&m.cl>1e3){const gap=mCVR-cvr,sR=m.cl*gap*(m.rv/Math.max(m.cv,1));tSup+=sR;sI.push({ch:m.ch,camp:m.camp,cvr,gap,sR:Math.round(sR),br:m.bS/m.cnt,fc:m.fS/m.cnt})}});
const chC={};rows.forEach(r=>{if(!chC[r.ch])chC[r.ch]={s:0,c:0};chC[r.ch].s+=r.spend;chC[r.ch].c+=r.conv});
const cacs=Object.entries(chC).map(([ch,m])=>({ch,cac:m.s/Math.max(m.c,1),cv:m.c})),mCAC=cacs.map(c=>c.cac).sort((a,b)=>a-b)[Math.floor(cacs.length/2)];
let tAv=0;const cI=[];cacs.forEach(c=>{if(c.cac>mCAC*1.3){const ex=(c.cac-mCAC)*c.cv;tAv+=ex;cI.push({type:"Excess CAC",ch:c.ch,cac:Math.round(c.cac),bm:Math.round(mCAC),av:Math.round(ex)})}});
return{leak:{total:Math.round(leak),pct:leak/tR*100,byCh:chL},exp:{total:Math.round(tSup),items:sI.sort((a,b)=>b.sR-a.sR)},cost:{total:Math.round(tAv),items:cI.sort((a,b)=>b.av-a.av)},totalRisk:Math.round(leak+tSup+tAv)}}

/* ═ TREND ANALYSIS ═ */
function trendAnalysis(rows){
const mo={};rows.forEach(r=>{if(!mo[r.month])mo[r.month]={month:r.ml,s:0,rv:0,cv:0};mo[r.month].s+=r.spend;mo[r.month].rv+=r.rev;mo[r.month].cv+=r.conv});
const mArr=Object.values(mo);
// MoM changes
for(let i=1;i<mArr.length;i++){mArr[i].rvChg=((mArr[i].rv-mArr[i-1].rv)/mArr[i-1].rv*100);mArr[i].sChg=((mArr[i].s-mArr[i-1].s)/mArr[i-1].s*100);mArr[i].roi=(mArr[i].rv-mArr[i].s)/mArr[i].s}
mArr[0].rvChg=0;mArr[0].sChg=0;mArr[0].roi=(mArr[0].rv-mArr[0].s)/mArr[0].s;
// Moving averages
for(let i=0;i<mArr.length;i++){const w=mArr.slice(Math.max(0,i-2),i+1);mArr[i].ma3=w.reduce((a,x)=>a+x.rv,0)/w.length}
// Anomaly detection (z-score)
const vals=mArr.map(m=>m.rv),mean=vals.reduce((a,b)=>a+b,0)/vals.length,std=Math.sqrt(vals.reduce((a,v)=>a+(v-mean)**2,0)/vals.length);
const anomalies=[];mArr.forEach(m=>{const z=(m.rv-mean)/(std||1);if(Math.abs(z)>1.8)anomalies.push({month:m.month,value:m.rv,z:Math.round(z*100)/100,dir:z>0?"spike":"dip"});m.zScore=Math.round(z*100)/100});
// Channel variance: H1 vs H2
const h1m=rows.filter(r=>parseInt(r.month.split("-")[1])<=6),h2m=rows.filter(r=>parseInt(r.month.split("-")[1])>6);
const varDecomp=Object.keys(CH).map(ch=>{const h1r=h1m.filter(r=>r.ch===ch).reduce((a,r)=>a+r.rev,0);const h2r=h2m.filter(r=>r.ch===ch).reduce((a,r)=>a+r.rev,0);return{ch,h1:h1r,h2:h2r,change:h2r-h1r,changePct:h1r>0?((h2r-h1r)/h1r*100):0}}).sort((a,b)=>b.change-a.change);
// ROI consistency per channel
const roiCons={};Object.keys(CH).forEach(ch=>{const chMo={};rows.filter(r=>r.ch===ch).forEach(r=>{if(!chMo[r.month])chMo[r.month]={s:0,rv:0};chMo[r.month].s+=r.spend;chMo[r.month].rv+=r.rev});const rois=Object.values(chMo).map(m=>(m.rv-m.s)/m.s);const avg=rois.reduce((a,b)=>a+b,0)/rois.length;const sd=Math.sqrt(rois.reduce((a,v)=>a+(v-avg)**2,0)/rois.length);const cv=avg!==0?sd/Math.abs(avg):0;roiCons[ch]={mean:avg,std:sd,cv,consistency:cv<.15?"High":cv<.3?"Medium":"Low"}});
return{monthly:mArr,anomalies,varDecomp,roiCons}}

/* ═ FUNNEL ANALYSIS ═ */
function funnelAnalysis(rows){
const stages=["imps","clicks","leads","mqls","sqls","conv"];const labels=["Impressions","Clicks","Leads","MQLs","SQLs","Conversions"];
// Overall funnel
const totals=stages.map(s=>rows.reduce((a,r)=>a+(r[s]||0),0));
const overall=stages.map((s,i)=>({stage:labels[i],key:s,volume:totals[i],rate:i>0&&totals[i-1]>0?(totals[i]/totals[i-1]):null,dropOff:i>0&&totals[i-1]>0?(1-totals[i]/totals[i-1]):null}));
// Benchmarks
const benchmarks={clicks:.02,leads:.08,mqls:.45,sqls:.38,conv:.25};
const bottlenecks=[];overall.forEach((st,i)=>{if(i===0||!st.rate)return;const bm=benchmarks[st.key];if(bm&&st.rate<bm*.7){const lost=Math.round(totals[i-1]*(bm-st.rate));bottlenecks.push({stage:st.stage,from:labels[i-1],actual:st.rate,benchmark:bm,gap:Math.round((bm-st.rate)/bm*100),lostVolume:lost,severity:st.rate<bm*.5?"critical":"warning"})}});
// Per channel funnel
const chFunnels=Object.keys(CH).map(ch=>{const cr=rows.filter(r=>r.ch===ch);const t=stages.map(s=>cr.reduce((a,r)=>a+(r[s]||0),0));return{ch,stages:stages.map((s,i)=>({stage:labels[i],volume:t[i],rate:i>0&&t[i-1]>0?(t[i]/t[i-1]):null})),overallRate:t[0]>0?t[5]/t[0]:0}});
// Revenue impact if bottlenecks fixed
const avgRPC=rows.reduce((a,r)=>a+r.rev,0)/Math.max(rows.reduce((a,r)=>a+r.conv,0),1);
const impacts=bottlenecks.map(b=>({...b,additionalConv:Math.round(b.lostVolume*.3),additionalRev:Math.round(b.lostVolume*.3*avgRPC)}));
return{overall,bottlenecks,chFunnels,impacts,avgRPC:Math.round(avgRPC),totalImpact:impacts.reduce((a,i)=>a+i.additionalRev,0)}}

/* ═ ROI FORMULAS (ALL 5) ═ */
function roiFormulas(rows,curves,gmPct=.65){
const ch={};rows.forEach(r=>{if(!ch[r.ch])ch[r.ch]={s:0,rv:0,cv:0,cl:0,le:0};const m=ch[r.ch];m.s+=r.spend;m.rv+=r.rev;m.cv+=r.conv;m.cl+=r.clicks;m.le+=r.leads});
const result=Object.entries(ch).map(([c,m])=>{
const baseROI=(m.rv-m.s)/m.s;const gmROI=(m.rv*gmPct-m.s)/m.s;const roas=m.rv/m.s;
// Incremental: compare Q1 baseline to rest
const q1=rows.filter(r=>r.ch===c&&parseInt(r.month.split("-")[1])<=3);const rest=rows.filter(r=>r.ch===c&&parseInt(r.month.split("-")[1])>3);
const q1s=q1.reduce((a,r)=>a+r.spend,0)/3,q1r=q1.reduce((a,r)=>a+r.rev,0)/3;
const rs=rest.reduce((a,r)=>a+r.spend,0)/9,rr=rest.reduce((a,r)=>a+r.rev,0)/9;
const incROI=(rs-q1s)>0?((rr-q1r)-(rs-q1s))/(rs-q1s):0;
// Marginal from curves
let margROI=0;if(curves[c]){const cv=curves[c];margROI=cv.a*cv.b*Math.pow(Math.max(cv.avgSpend,1),cv.b-1)}
// Payback
const months=rows.filter(r=>r.ch===c);const moData={};months.forEach(r=>{if(!moData[r.month])moData[r.month]={s:0,rv:0};moData[r.month].s+=r.spend;moData[r.month].rv+=r.rev});
let cumS=0,cumR=0,payback=12;Object.values(moData).forEach((m,i)=>{cumS+=m.s;cumR+=m.rv;if(cumR>=cumS&&payback===12)payback=i+1});
return{ch:c,baseROI,gmROI,roas,incROI,margROI,payback,spend:m.s,revenue:m.rv,cac:m.s/Math.max(m.cv,1),
ltv:Math.round(m.rv/Math.max(m.cv,1)*2.5),costToServe:Math.round(m.s/Math.max(m.cv,1)*.15)}});
return result.sort((a,b)=>b.baseROI-a.baseROI)}

/* ═ AUTO MAPPING ═ */
function autoMap(cols){
const std={date:["date","month","period"],channel:["channel","source","medium"],campaign:["campaign","campaign_name"],spend:["spend","cost","ad_spend","budget"],revenue:["revenue","sales","income"],impressions:["impressions","imps","views"],clicks:["clicks","click"],leads:["leads","lead"],conversions:["conversions","conversion","orders"],region:["region","geo","market"],product:["product","category"]};
const map={};Object.entries(std).forEach(([field,aliases])=>{let best=null,bestS=0;cols.forEach(col=>{const cl=col.toLowerCase().replace(/_/g," ");aliases.forEach(a=>{const s=cl===a?1:cl.includes(a)||a.includes(cl)?.8:0;if(s>bestS){bestS=s;best=col}})});if(best&&bestS>.3)map[field]={src:best,conf:bestS,status:bestS>.7?"auto":"suggested"};else map[field]={src:null,conf:0,status:"unmapped"}});
return map}

/* ═ PHASE 2: MARKOV ATTRIBUTION ═ */
function markovAttr(js){
const trans={};const chs=new Set();
js.filter(j=>j.cv).forEach(j=>{const path=["start",...j.tps.sort((a,b)=>(a.o||0)-(b.o||0)).map(t=>t.ch),"conv"];
path.forEach(p=>{if(p!=="start"&&p!=="conv")chs.add(p)});
for(let i=0;i<path.length-1;i++){if(!trans[path[i]])trans[path[i]]={};trans[path[i]][path[i+1]]=(trans[path[i]][path[i+1]]||0)+1}});
js.filter(j=>!j.cv).forEach(j=>{const path=["start",...j.tps.sort((a,b)=>(a.o||0)-(b.o||0)).map(t=>t.ch),"null"];
for(let i=0;i<path.length-1;i++){if(!trans[path[i]])trans[path[i]]={};trans[path[i]][path[i+1]]=(trans[path[i]][path[i+1]]||0)+1}});
// Normalize to probabilities
const prob={};Object.entries(trans).forEach(([from,tos])=>{const t=Object.values(tos).reduce((a,b)=>a+b,0);prob[from]={};Object.entries(tos).forEach(([to,c])=>{prob[from][to]=c/t})});
// Simulate conversion probability
const simProb=(matrix,channels)=>{const states=["start",...channels,"conv","null"];const n=states.length;const idx={};states.forEach((s,i)=>idx[s]=i);const T=Array(n).fill(null).map(()=>Array(n).fill(0));Object.entries(matrix).forEach(([f,tos])=>{if(idx[f]===undefined)return;Object.entries(tos).forEach(([t,p])=>{if(idx[t]!==undefined)T[idx[f]][idx[t]]=p})});T[idx["conv"]][idx["conv"]]=1;T[idx["null"]][idx["null"]]=1;let st=Array(n).fill(0);st[idx["start"]]=1;for(let i=0;i<50;i++){const ns=Array(n).fill(0);st.forEach((v,r)=>{T[r].forEach((p,c)=>{ns[c]+=v*p})});st=ns}return st[idx["conv"]]};
const chArr=[...chs];const baseP=simProb(prob,chArr);
const totalRev=js.filter(j=>j.cv).reduce((a,j)=>a+j.rv,0);
const effects={};chArr.forEach(ch=>{const mod={};Object.entries(prob).forEach(([f,tos])=>{if(f===ch){mod[f]={"null":1}}else{const nt={};let removed=0;Object.entries(tos).forEach(([t,p])=>{if(t===ch)removed+=p;else nt[t]=p});if(removed>0)nt["null"]=(nt["null"]||0)+removed;const tot=Object.values(nt).reduce((a,b)=>a+b,0);Object.keys(nt).forEach(k=>{nt[k]/=tot||1});mod[f]=nt}});
const rP=simProb(mod,chArr.filter(c=>c!==ch));effects[ch]=Math.max(0,baseP-rP)});
const totalE=Object.values(effects).reduce((a,b)=>a+b,0)||1;
const result={};chArr.forEach(ch=>{const w=effects[ch]/totalE;result[ch]={weight:w,revenue:Math.round(totalRev*w),pct:Math.round(w*100*10)/10,effect:Math.round(effects[ch]*1e4)/1e4}});
// Top transitions
const topTrans=[];Object.entries(prob).forEach(([f,tos])=>{if(f==="conv"||f==="null")return;Object.entries(tos).forEach(([t,p])=>{if(p>.05)topTrans.push({from:f,to:t,prob:Math.round(p*1e3)/1e3})})});
topTrans.sort((a,b)=>b.prob-a.prob);
return{channels:result,baseProb:Math.round(baseP*1e4)/1e4,totalRev,transitions:topTrans.slice(0,15)}}

/* ═ PHASE 2: SIMPLIFIED MMM ═ */
function simpleMMM(rows,curves){
// Estimate channel contributions using response curves + seasonal decomposition
const monthly={};rows.forEach(r=>{if(!monthly[r.month])monthly[r.month]={rv:0,s:0};monthly[r.month].rv+=r.rev;monthly[r.month].s+=r.spend});
const totalRev=Object.values(monthly).reduce((a,m)=>a+m.rv,0);
const totalSpend=Object.values(monthly).reduce((a,m)=>a+m.s,0);
// Channel contributions from response curves
const contribs={};let modeledTotal=0;
Object.entries(curves).forEach(([ch,cv])=>{const chSpend=rows.filter(r=>r.ch===ch).reduce((a,r)=>a+r.spend,0);
const contrib=cv.a*Math.pow(Math.max(chSpend/12,1),cv.b)*12;contribs[ch]={contribution:Math.round(contrib),spend:Math.round(chSpend),roas:contrib/Math.max(chSpend,1)};modeledTotal+=contrib});
// Baseline = unexplained revenue
const baseline=Math.max(0,totalRev-modeledTotal);
// Normalize and add confidence
Object.values(contribs).forEach(c=>{c.pct=Math.round(c.contribution/totalRev*1000)/10;c.roas=Math.round(c.roas*100)/100;
c.roas_lower=Math.round(c.roas*.8*100)/100;c.roas_upper=Math.round(c.roas*1.2*100)/100;
c.confidence=CH[Object.keys(contribs).find(k=>contribs[k]===c)]?.type==="online"?"High":"Model-Estimated"});
return{contributions:contribs,baseline:Math.round(baseline),baselinePct:Math.round(baseline/totalRev*1000)/10,totalRev:Math.round(totalRev),r2:.75}}

/* ═ PHASE 2: FORECAST ═ */
function simpleForecast(rows,periods=12){
const monthly={};rows.forEach(r=>{if(!monthly[r.month])monthly[r.month]={m:r.ml,rv:0,s:0,cv:0};monthly[r.month].rv+=r.rev;monthly[r.month].s+=r.spend;monthly[r.month].cv+=r.conv});
const mArr=Object.values(monthly);const n=mArr.length;
const rvs=mArr.map(m=>m.rv),sps=mArr.map(m=>m.s);
// Linear trend + seasonality
const x=Array.from({length:n},(_, i)=>i);
const mx=x.reduce((a,b)=>a+b,0)/n,my=rvs.reduce((a,b)=>a+b,0)/n;
let num=0,den=0;x.forEach((xi,i)=>{num+=(xi-mx)*(rvs[i]-my);den+=(xi-mx)**2});
const slope=den>0?num/den:0,intercept=my-slope*mx;
// Seasonal factors
const seasonal=mArr.map((m,i)=>rvs[i]/(slope*i+intercept||1));
// Forecast
const forecast=[];for(let i=0;i<periods;i++){
const trendVal=slope*(n+i)+intercept;
const seasonIdx=i%n;const sf=seasonal[seasonIdx]||1;
const pred=Math.max(0,trendVal*sf);
forecast.push({month:MO[i%12],predicted:Math.round(pred),lower:Math.round(pred*.82),upper:Math.round(pred*1.18)})}
const fcTotal=forecast.reduce((a,f)=>a+f.predicted,0);
return{historical:mArr.map(m=>({month:m.m,actual:m.rv})),forecast,summary:{historicalTotal:Math.round(my*n),forecastTotal:fcTotal,yoyPct:Math.round((fcTotal-my*n)/(my*n)*1000)/10}}}

/* ═ PHASE 2: CROSS-CHANNEL LEAKAGE ═ */
function crossChannelLeak(rows){
// Timing leakage
const monthly={};rows.forEach(r=>{if(!monthly[r.month])monthly[r.month]={s:0,rv:0};monthly[r.month].s+=r.spend;monthly[r.month].rv+=r.rev});
const mArr=Object.values(monthly);const tS=mArr.reduce((a,m)=>a+m.s,0),tR=mArr.reduce((a,m)=>a+m.rv,0);
const timing=mArr.map(m=>({spendShare:m.s/tS,revShare:m.rv/tR,misalign:Math.abs(m.s/tS-m.rv/tR),status:m.s/tS>m.rv/tR*1.15?"overspend":m.s/tS<m.rv/tR*.85?"underspend":"aligned"}));
const timingLeak=mArr.reduce((a,m)=>{const ss=m.s/tS,rs=m.rv/tR;if(ss>rs*1.15){return a+(m.s-tS*rs)*(tR/tS)*.3}return a},0);
// Online vs Offline flow
const on=rows.filter(r=>r.ct==="online"),off=rows.filter(r=>r.ct==="offline");
const onRev=on.reduce((a,r)=>a+r.rev,0),offRev=off.reduce((a,r)=>a+r.rev,0);
const onS=on.reduce((a,r)=>a+r.spend,0),offS=off.reduce((a,r)=>a+r.spend,0);
// Regional leakage
const regions={};rows.forEach(r=>{if(!regions[r.reg])regions[r.reg]={s:0,rv:0};regions[r.reg].s+=r.spend;regions[r.reg].rv+=r.rev});
const regArr=Object.entries(regions).map(([reg,m])=>({reg,spend:m.s,revenue:m.rv,roi:(m.rv-m.s)/m.s,spendShare:m.s/tS,revShare:m.rv/tR,efficiency:m.rv/tR/(m.s/tS),status:m.rv/tR/(m.s/tS)>1.3?"underfunded":m.rv/tR/(m.s/tS)<.7?"overfunded":"balanced"}));
const audLeak=regArr.filter(r=>r.status==="underfunded").reduce((a,r)=>{const optS=tS*r.revShare;return a+Math.max(0,(optS-r.spend)*r.roi*.5)},0);
return{timingLeak:Math.round(timingLeak),timing,audienceLeak:Math.round(audLeak),regions:regArr,onlineOffline:{onRev:Math.round(onRev),offRev:Math.round(offRev),onSpend:Math.round(onS),offSpend:Math.round(offS),onROI:Math.round((onRev-onS)/onS*100)/100,offROI:Math.round((offRev-offS)/offS*100)/100},total:Math.round(timingLeak+audLeak)}}

/* ═ PHASE 2: ADSTOCK VISUALIZATION ═ */
function adstockViz(rows){
const result={};Object.keys(CH).forEach(ch=>{const chRows=rows.filter(r=>r.ch===ch);const monthly={};chRows.forEach(r=>{if(!monthly[r.month])monthly[r.month]={s:0,rv:0};monthly[r.month].s+=r.spend;monthly[r.month].rv+=r.rev});
const pts=Object.values(monthly);if(pts.length<3)return;const spend=pts.map(p=>p.s),rev=pts.map(p=>p.rv);
// Fit best decay
let bestD=.5,bestC=-1;for(let d=.1;d<.95;d+=.05){const ad=[spend[0]];for(let i=1;i<spend.length;i++)ad.push(spend[i]+d*ad[i-1]);
const mx=ad.reduce((a,b)=>a+b,0)/ad.length,my2=rev.reduce((a,b)=>a+b,0)/rev.length;
let n2=0,d2=0;ad.forEach((a,i)=>{n2+=(a-mx)*(rev[i]-my2);d2+=(a-mx)**2});
const c=d2>0?n2/Math.sqrt(d2*rev.reduce((a,v)=>a+(v-my2)**2,0)):0;
if(c>bestC){bestC=c;bestD=d}}
// Apply best decay
const adstocked=[spend[0]];for(let i=1;i<spend.length;i++)adstocked.push(spend[i]+bestD*adstocked[i-1]);
const carryover=Math.round((adstocked.reduce((a,b)=>a+b,0)-spend.reduce((a,b)=>a+b,0))/spend.reduce((a,b)=>a+b,0)*1000)/10;
result[ch]={decay:Math.round(bestD*100)/100,correlation:Math.round(bestC*1000)/1000,carryoverPct:carryover,original:spend,adstocked,revenue:rev}});
return result}

/* ═ FORMAT ═ */
const F=(n,p="$")=>{if(n==null||isNaN(n))return"—";const a=Math.abs(n),s=a>=1e6?`${(a/1e6).toFixed(1)}M`:a>=1e3?`${(a/1e3).toFixed(0)}K`:a.toFixed(0);return`${n<0?"-":""}${p}${s}`};
const FP=n=>n==null||isNaN(n)?"—":`${n>=0?"+":""}${n.toFixed(1)}%`;const FX=n=>n==null||isNaN(n)?"—":`${n.toFixed(2)}x`;
const FN=ch=>CH[ch]?.label||ch?.replace(/_/g," ")||"";

/* ══════════════════════════════════════
   APP
   ══════════════════════════════════════ */
export default function App(){
const[tab,setTab]=useState("data");const[D,setD]=useState(null);const[loading,setL]=useState(false);
const[atM,setAtM]=useState("linear");const[selCh,setSelCh]=useState(null);const[selCp,setSelCp]=useState(null);
const[bM,setBM]=useState(1);const[obj,setObj]=useState("balanced");
const[fl,setFl]=useState({reg:"All",prod:"All",ct:"All",q:"All"});
const[scn,setScn]=useState([]);const[aScn,setAScn]=useState(null);
const[recs,setRecs]=useState([]);const[cons,setCons]=useState({});
const[dataOk,setDataOk]=useState(false);const[mapOk,setMapOk]=useState(false);
const[qScore]=useState(94);const[colMap,setColMap]=useState({});const[uploadStep,setUploadStep]=useState(0);
const[roiMode,setRoiMode]=useState("baseROI");
const[trend,setTrend]=useState(null);const[funnel,setFunnel]=useState(null);const[roiData,setRoiData]=useState(null);
const[recalc,setRecalc]=useState(false);const[gmPct,setGmPct]=useState(65);
const[role,setRole]=useState("analyst");
const[markov,setMarkov]=useState(null);const[mmm,setMmm]=useState(null);const[fc,setFc]=useState(null);const[xChl,setXChl]=useState(null);const[adst,setAdst]=useState(null);
const[recFilter,setRecFilter]=useState("ALL");
const[objWeights,setObjWeights]=useState({revenue:40,roi:30,leakage:15,cost:15});
const[hillMode,setHillMode]=useState(false);
const availCols=["month","ch","camp","spend","rev","imps","clicks","leads","mqls","sqls","conv","reg","prod","br","sd","fc","nps"];
// Realization tracker mock
const[realData]=useState(MO.map((m,i)=>({month:m,planned:Math.round(1e6+i*8e4+Math.random()*5e4),actual:i<9?Math.round(1e6+i*7e4+Math.random()*8e4):null})));
const[rawRows,setRawRows]=useState(null);const[rawJs,setRawJs]=useState(null);const[analysisRun,setAnalysisRun]=useState(false);

// CSV Parser
const parseCSV=useCallback((text)=>{
const lines=text.split("\n").filter(l=>l.trim());if(lines.length<2)return{headers:[],rows:[]};
const headers=lines[0].split(",").map(h=>h.trim().toLowerCase().replace(/['"]/g,""));
const rows=lines.slice(1).map(line=>{const vals=line.split(",");const row={};headers.forEach((h,i)=>{const v=(vals[i]||"").trim().replace(/['"]/g,"");row[h]=isNaN(v)||v===""?v:parseFloat(v)});return row});
return{headers,rows}},[]);

// Standardize columns based on mapping
const standardize=useCallback((rows,mapping)=>{
const stdMap={};Object.entries(mapping).forEach(([std,m])=>{const src=typeof m==="string"?m:m?.src;if(src)stdMap[src]=std});
return rows.map(r=>{const nr={};Object.entries(r).forEach(([k,v])=>{const std=stdMap[k.toLowerCase()]||k;nr[std]=v});
// Internal field aliases
nr.ch=nr.channel||nr.ch||"";nr.camp=nr.campaign||nr.camp||"";nr.ml=nr.date?String(nr.date).slice(5,7):nr.ml||"";
nr.month=nr.date||nr.month||"";nr.ct=CH[nr.ch]?.type||"online";nr.spend=parseFloat(nr.spend)||0;nr.rev=parseFloat(nr.revenue||nr.rev)||0;
nr.imps=parseInt(nr.impressions||nr.imps)||0;nr.clicks=parseInt(nr.clicks)||0;nr.leads=parseInt(nr.leads)||0;
nr.mqls=parseInt(nr.mqls)||0;nr.sqls=parseInt(nr.sqls)||0;nr.conv=parseInt(nr.conversions||nr.conv)||0;
nr.reg=nr.region||nr.reg||"All";nr.prod=nr.product||nr.prod||"All";
nr.br=parseFloat(nr.bounce_rate||nr.br)||0;nr.sd=parseFloat(nr.avg_session_duration_sec||nr.sd)||0;
nr.fc=parseFloat(nr.form_completion_rate||nr.fc)||0;nr.nps=parseInt(nr.nps_score||nr.nps)||0;
nr.conf=nr.confidence_tier||nr.conf||(CH[nr.ch]?.type==="online"?"High":"Model-Est");
const mo=nr.month?String(nr.month).slice(5,7):"01";const moIdx=parseInt(mo)-1;nr.ml=MO[moIdx]||nr.ml||"";
return nr})},[]);

// Standardize journey data
const standardizeJs=useCallback((rows)=>{
return rows.map(r=>({id:r.journey_id||r.id||"",tps:[{ch:r.channel||r.ch||"",camp:r.campaign||r.camp||"",o:parseInt(r.touchpoint_order||r.o)||1}],cv:String(r.converted||r.cv).toLowerCase()==="true",rv:parseFloat(r.conversion_revenue||r.rv)||0,nt:parseInt(r.total_touchpoints||r.nt)||1}))
// Group by journey_id
.reduce((acc,r)=>{const existing=acc.find(j=>j.id===r.id);if(existing){existing.tps.push(r.tps[0]);existing.nt=Math.max(existing.nt,r.tps[0].o)}else acc.push(r);return acc},[])},[]);

// Run all engines on data
const runAllEngines=useCallback((rows,js)=>{
setRecalc(true);setTimeout(()=>{
const attr=js&&js.length>0?runAttr(js):{last_touch:{},linear:{},position_based:{}};
const curves=fitC(rows);const tS=rows.reduce((a,r)=>a+r.spend,0);
const opt=optim(curves,tS);const dg=diag(rows,curves,attr);const pl2=pil(rows,opt);
setD({rows,js:js||[],attr,curves,opt,pl:pl2,tS});setRecs(dg);
setTrend(trendAnalysis(rows));setFunnel(funnelAnalysis(rows));setRoiData(roiFormulas(rows,curves));
// Phase 2 engines
if(js&&js.length>0)setMarkov(markovAttr(js));
setMmm(simpleMMM(rows,curves));setFc(simpleForecast(rows,12));setXChl(crossChannelLeak(rows));setAdst(adstockViz(rows));
setScn([{id:"baseline",name:"Current Baseline",budget:tS,obj:"balanced",opt,locked:true}]);
setAScn("baseline");setAnalysisRun(true);setRecalc(false)},200)},[]);

// Load demo data
const loadDemo=useCallback(()=>{
const mock=gen();setRawRows(mock.rows);setRawJs(mock.js);setDataOk(true);setMapOk(true);setUploadStep(1);
setColMap(autoMap(["month","ch","camp","spend","rev","imps","clicks","leads","mqls","sqls","conv","reg","prod","br","nps"]));
runAllEngines(mock.rows,mock.js);setL(false)},[runAllEngines]);

// Handle CSV upload
const handleUpload=useCallback((text,type)=>{
const{headers,rows}=parseCSV(text);
if(type==="campaign"){const mapping=autoMap(headers);setColMap(mapping);const stdRows=standardize(rows,mapping);setRawRows(stdRows);setDataOk(true);setUploadStep(2)}
else if(type==="journey"){const stdJs=standardizeJs(rows);setRawJs(stdJs);setUploadStep(3)}
},[parseCSV,standardize,standardizeJs]);

// Initial: don't auto-load, wait for upload
useEffect(()=>{setL(false)},[]);

const reOpt=useCallback(()=>{if(!D)return;setRecalc(true);setTimeout(()=>{const nb=D.tS*bM;const opt=optim(D.curves,nb,obj,cons);const pl2=pil(D.rows,opt);setD(d=>({...d,opt,pl:pl2}));setRecalc(false)},200)},[D,bM,obj,cons]);

const createScnFromRecs=useCallback(()=>{if(!D)return;
const approved=recs.filter(r=>r.status==="approved");const newCons={};
approved.forEach(r=>{if(r.type==="SCALE")newCons[r.ch]={min:D.tS*.05};if(r.type==="REDUCE")newCons[r.ch]={max:D.tS*.08}});
const opt=optim(D.curves,D.tS,"balanced",newCons);
setScn(s=>[...s,{id:`recs_${Date.now()}`,name:`From ${approved.length} Recommendations`,budget:D.tS,obj:"balanced",opt,locked:false}])},[D,recs]);

const exportCSV=useCallback(()=>{if(!D)return;
// Optimization plan
const h1=["Channel","Current Spend","Optimized Spend","Change %","Current Revenue","Optimized Revenue","Marginal ROI","Confidence"];
const r1=D.opt.channels.map(c=>[FN(c.channel),c.cS,c.oS,c.chg.toFixed(1),c.cR,c.oR,c.mROI.toFixed(2),CH[c.channel]?.type==="online"?"High":"Model-Est"]);
// Business case summary
const summary=[["",""],["BUSINESS CASE SUMMARY",""],["Total Current Revenue",D.opt.summary.cRev],["Total Optimized Revenue",D.opt.summary.oRev],["Revenue Uplift %",D.opt.summary.uplift.toFixed(1)],["Current ROI",D.opt.summary.cROI.toFixed(2)],["Optimized ROI",D.opt.summary.oROI.toFixed(2)],["",""],["THREE PILLAR IMPACT",""],["Revenue Leakage",D.pl.leak.total],["CX Suppression",D.pl.exp.total],["Avoidable Cost",D.pl.cost.total],["Total Value at Risk",D.pl.totalRisk],["",""],["RECOMMENDATIONS",""],...recs.slice(0,10).map(r=>[`${r.type}: ${FN(r.ch)}`,r.action])];
const csv=[h1.join(","),...r1.map(r=>r.join(",")),...summary.map(r=>r.join(","))].join("\n");
const blob=new Blob([csv],{type:"text/csv"});const url=URL.createObjectURL(blob);
const a=document.createElement("a");a.href=url;a.download="yield_intelligence_business_case.csv";a.click();URL.revokeObjectURL(url)},[D,recs]);

// Filtered data
const fd=useMemo(()=>{if(!D)return[];return D.rows.filter(r=>{if(fl.reg!=="All"&&r.reg!==fl.reg)return false;if(fl.prod!=="All"&&r.prod!==fl.prod)return false;if(fl.ct!=="All"&&r.ct!==fl.ct)return false;if(fl.q!=="All"){const q=Math.ceil(parseInt(r.month.split("-")[1])/3);if(`Q${q}`!==fl.q)return false}return true})},[D,fl]);

const kp=useMemo(()=>{if(!fd.length)return{};const s=fd.reduce((a,x)=>a+x.spend,0),rv=fd.reduce((a,x)=>a+x.rev,0),cv=fd.reduce((a,x)=>a+x.conv,0),cl=fd.reduce((a,x)=>a+x.clicks,0);return{s,rv,roi:(rv-s)/s,roas:rv/s,cv,cac:s/cv,cvr:cv/cl,cl}},[fd]);

const chD=useMemo(()=>{if(!fd.length)return[];const c={};fd.forEach(r=>{if(!c[r.ch])c[r.ch]={ch:r.ch,ct:r.ct,s:0,rv:0,im:0,cl:0,le:0,cv:0,col:CH[r.ch]?.color};const m=c[r.ch];m.s+=r.spend;m.rv+=r.rev;m.im+=r.imps;m.cl+=r.clicks;m.le+=r.leads;m.cv+=r.conv});return Object.values(c).map(m=>({...m,roi:(m.rv-m.s)/m.s,roas:m.rv/m.s,ctr:m.cl/m.im,cvr:m.cv/Math.max(m.cl,1),cac:m.s/Math.max(m.cv,1)})).sort((a,b)=>b.roi-a.roi)},[fd]);

const cpD=useMemo(()=>{if(!fd.length)return[];const c={};fd.forEach(r=>{const k=`${r.ch}|||${r.camp}`;if(!c[k])c[k]={ch:r.ch,camp:r.camp,ct:r.ct,s:0,rv:0,im:0,cl:0,le:0,cv:0,col:CH[r.ch]?.color};const m=c[k];m.s+=r.spend;m.rv+=r.rev;m.im+=r.imps;m.cl+=r.clicks;m.le+=r.leads;m.cv+=r.conv});return Object.values(c).map(m=>({...m,roi:(m.rv-m.s)/m.s,roas:m.rv/m.s,ctr:m.cl/m.im,cvr:m.cv/Math.max(m.cl,1),cac:m.s/Math.max(m.cv,1)})).sort((a,b)=>b.rv-a.rv)},[fd]);

const mT=useMemo(()=>{if(!fd.length)return[];const m={};fd.forEach(r=>{if(!m[r.month])m[r.month]={month:r.ml,s:0,rv:0,cv:0};m[r.month].s+=r.spend;m[r.month].rv+=r.rev;m[r.month].cv+=r.conv});return Object.values(m).map(v=>({...v,roi:(v.rv-v.s)/v.s}))},[fd]);

// ROI heatmap data
const heatData=useMemo(()=>{if(!cpD.length)return[];return cpD.map(c=>({name:`${c.camp}`,channel:FN(c.ch),roi:c.roi,spend:c.s,rev:c.rv,color:c.roi>5?"#10b981":c.roi>2?"#FFE600":c.roi>1?"#d97706":"#ef4444"}))},[cpD]);

// Marginal ROI table
const margTable=useMemo(()=>{if(!D)return[];const mults=[.5,.75,1,1.25,1.5,2];const rows=[];Object.entries(D.curves).forEach(([ch,cv])=>{mults.forEach(m=>{const sp=cv.avgSpend*m,tr=cv.a*Math.pow(Math.max(sp,1),cv.b),mr=cv.a*cv.b*Math.pow(Math.max(sp,1),cv.b-1);rows.push({ch,mult:`${(m*100).toFixed(0)}%`,spend:Math.round(sp),rev:Math.round(tr),mROI:mr,avgROI:tr/sp})})});return rows},[D]);

// Online vs offline comparison
const oVo=useMemo(()=>{if(!fd.length)return{};const d={online:{s:0,rv:0,cv:0,cl:0,le:0},offline:{s:0,rv:0,cv:0,cl:0,le:0}};fd.forEach(r=>{const t=r.ct;d[t].s+=r.spend;d[t].rv+=r.rev;d[t].cv+=r.conv;d[t].cl+=r.clicks;d[t].le+=r.leads});return Object.fromEntries(Object.entries(d).map(([k,v])=>[k,{...v,roi:(v.rv-v.s)/v.s,roas:v.rv/v.s,cac:v.s/Math.max(v.cv,1),cvr:v.cv/Math.max(v.cl,1)}]))},[fd]);

// Cross-channel influence
const xCh=useMemo(()=>{if(!D)return[];const paths={};D.js.filter(j=>j.cv&&j.nt>1).forEach(j=>{for(let i=0;i<j.tps.length-1;i++){const k=`${j.tps[i].ch}→${j.tps[i+1].ch}`;paths[k]=(paths[k]||0)+1}});return Object.entries(paths).map(([k,v])=>({path:k,from:k.split("→")[0],to:k.split("→")[1],count:v})).sort((a,b)=>b.count-a.count).slice(0,12)},[D]);

if(loading)return<div style={{height:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"#1A1A24",color:"#FFE600",fontFamily:"'Plus Jakarta Sans',system-ui"}}><div style={{textAlign:"center"}}><RefreshCw size={32} style={{animation:"spin 1s linear infinite"}}/><div style={{marginTop:16,fontSize:13,color:"#6B7280"}}>Initializing Yield Intelligence engines...</div><style>{`@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}`}</style></div></div>;

/* Guard: if no data loaded, force data tab */
const activeTab=(!D&&tab!=="data"&&tab!=="mapping")?"data":tab;

const TABS=[{id:"home",i:Home,l:"Executive",roles:["executive","analyst","planner","admin"]},{id:"data",i:Database,l:"Data",roles:["analyst","admin"]},{id:"mapping",i:MapIcon,l:"Mapping",roles:["analyst","admin"]},{id:"performance",i:BarChart3,l:"Performance",roles:["executive","analyst","planner"]},{id:"deepdive",i:Search,l:"Deep Dive",roles:["analyst","planner"]},{id:"pillars",i:AlertTriangle,l:"Leakage",roles:["executive","analyst"]},{id:"recommendations",i:Lightbulb,l:"Actions",roles:["executive","analyst"]},{id:"scenarios",i:GitBranch,l:"Scenarios",roles:["planner","analyst"]},{id:"optimizer",i:Target,l:"Optimizer",roles:["planner","analyst"]},{id:"business",i:FileText,l:"Business Case",roles:["executive","analyst","planner"]}];
const visibleTabs=TABS.filter(t=>t.roles.includes(role));

const gated=!dataOk&&!["home","data"].includes(activeTab);
const C=({children,style:s,...p})=><div style={{background:"#22222E",borderRadius:8,padding:14,border:"1px solid #2E2E3E",...s}} {...p}>{children}</div>;
const K=({l,v,a="#FFE600",sub,onClick})=><C style={{cursor:onClick?"pointer":"default",position:"relative",overflow:"hidden",paddingLeft:18}} onClick={onClick}><div style={{position:"absolute",top:0,left:0,width:3,height:"100%",background:a}}/><div style={{fontSize:9,color:"#6B7280",textTransform:"uppercase",letterSpacing:1,fontWeight:600,marginBottom:3}}>{l}</div><div style={{fontSize:18,fontWeight:800,color:"#F3F4F6",letterSpacing:-.5}}>{v}</div>{sub&&<div style={{fontSize:10,color:sub.c||"#6B7280",marginTop:2}}>{sub.t}</div>}</C>;
const B=({children,c="#FFE600"})=><span style={{display:"inline-flex",padding:"1px 7px",borderRadius:3,background:`${c}15`,color:c,fontSize:9,fontWeight:700,letterSpacing:.5}}>{children}</span>;
const Btn=({children,primary,onClick,style:s})=><button onClick={onClick} style={{padding:"7px 14px",background:primary?"#FFE600":"transparent",color:primary?"#1A1A24":"#9CA3AF",border:primary?"none":"1px solid #3D3D4E",borderRadius:5,cursor:"pointer",fontSize:11,fontWeight:700,fontFamily:"inherit",display:"inline-flex",alignItems:"center",gap:5,...s}}>{children}</button>;
const tt={background:"#2E2E3E",border:"1px solid #3D3D4E",borderRadius:5,fontSize:10,color:"#E5E7EB"};
const Tip=({children})=><div style={{background:"#FFE60008",border:"1px solid #FFE60020",borderRadius:6,padding:"8px 12px",fontSize:11,color:"#FFE600",display:"flex",gap:6,alignItems:"center",marginBottom:14}}><Zap size={12}/><div>{children}</div></div>;
const NB=({l,onClick})=><Btn primary onClick={onClick} style={{marginTop:10}}>{l}<ArrowRight size={13}/></Btn>;

return(<div style={{minHeight:"100vh",background:"#1A1A24",color:"#E5E7EB",fontFamily:"'Plus Jakarta Sans','Segoe UI',system-ui"}}>
<style>{`*{box-sizing:border-box;margin:0;padding:0}::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-thumb{background:#3D3D4E;border-radius:2px}table{width:100%;border-collapse:collapse;font-size:10px}th{text-align:left;padding:6px 8px;color:#6B7280;font-weight:600;border-bottom:1px solid #2E2E3E;font-size:9px;text-transform:uppercase;letter-spacing:.7px}td{padding:6px 8px;border-bottom:1px solid #25252F}tr:hover td{background:#25252F}select{background:#22222E;color:#E5E7EB;border:1px solid #3D3D4E;padding:4px 6px;border-radius:4px;font-size:10px;font-family:inherit}input[type=range]{accent-color:#FFE600;width:100%}`}</style>

{/* HEADER */}
<div style={{background:"#22222E",borderBottom:"1px solid #2E2E3E"}}>
<div style={{maxWidth:1400,margin:"0 auto",padding:"0 20px",display:"flex",alignItems:"center",justifyContent:"space-between"}}>
<div style={{display:"flex",alignItems:"center",gap:8,padding:"12px 0"}}>
<div style={{width:26,height:26,background:"#FFE600",borderRadius:3,display:"flex",alignItems:"center",justifyContent:"center"}}><Target size={14} color="#1A1A24"/></div>
<div><div style={{fontSize:13,fontWeight:800,color:"#FFE600",letterSpacing:-.3}}>YIELD INTELLIGENCE</div><div style={{fontSize:8,color:"#6B7280",letterSpacing:1.5,textTransform:"uppercase"}}>Marketing ROI & Budget Optimization</div></div>
</div>
<div style={{display:"flex",alignItems:"center",gap:14,fontSize:10,color:"#6B7280"}}>
<select value={role} onChange={e=>setRole(e.target.value)} style={{background:"#2E2E3E",color:"#E5E7EB",border:"1px solid #3D3D4E",padding:"3px 6px",borderRadius:4,fontSize:9}}>
<option value="executive">CMO / Executive</option><option value="analyst">Analyst</option><option value="planner">Media Planner</option><option value="admin">Data Admin</option>
</select>
<div style={{display:"flex",alignItems:"center",gap:3}}><Shield size={11} color={qScore>80?"#10b981":"#d97706"}/> Quality: <span style={{color:qScore>80?"#10b981":"#d97706",fontWeight:700}}>{qScore}%</span></div>
<span>FY 2025</span>
</div></div></div>

{/* NAV */}
<div style={{background:"#1F1F2B",borderBottom:"1px solid #2E2E3E",overflowX:"auto"}}>
<div style={{maxWidth:1400,margin:"0 auto",padding:"0 20px",display:"flex",gap:0}}>
{visibleTabs.map(t=><button key={t.id} onClick={()=>setTab(t.id)} style={{display:"flex",alignItems:"center",gap:5,padding:"9px 12px",border:"none",background:activeTab===t.id?"#FFE60012":"transparent",color:activeTab===t.id?"#FFE600":"#6B7280",cursor:"pointer",fontSize:10,fontWeight:activeTab===t.id?700:500,borderBottom:activeTab===t.id?"2px solid #FFE600":"2px solid transparent",whiteSpace:"nowrap",fontFamily:"inherit"}}><t.i size={13}/>{t.l}</button>)}
</div></div>

{/* FILTERS */}
{!["data","mapping"].includes(tab)&&<div style={{background:"#1F1F2B",borderBottom:"1px solid #2E2E3E",padding:"6px 20px"}}>
<div style={{maxWidth:1400,margin:"0 auto",display:"flex",alignItems:"center",gap:10,fontSize:10}}>
<Filter size={11} color="#6B7280"/>
{[{k:"q",o:["All","Q1","Q2","Q3","Q4"],l:"Quarter"},{k:"reg",o:["All",...REG],l:"Region"},{k:"prod",o:["All",...PROD],l:"Product"},{k:"ct",o:["All","online","offline"],l:"Type"}].map(f=><div key={f.k} style={{display:"flex",alignItems:"center",gap:3}}><span style={{color:"#6B7280"}}>{f.l}:</span><select value={fl[f.k]} onChange={e=>setFl(p=>({...p,[f.k]:e.target.value}))}>{f.o.map(o=><option key={o} value={o}>{o}</option>)}</select></div>)}
{Object.values(fl).some(v=>v!=="All")&&<button onClick={()=>setFl({reg:"All",prod:"All",ct:"All",q:"All"})} style={{background:"none",border:"none",color:"#FFE600",cursor:"pointer",fontSize:10,fontFamily:"inherit"}}>Clear</button>}
</div></div>}

{gated&&<div style={{maxWidth:1400,margin:"20px auto",padding:"0 20px"}}><C style={{textAlign:"center",padding:40,border:"1px solid #ef444440"}}><AlertTriangle size={24} color="#ef4444" style={{margin:"0 auto 10px"}}/><div style={{fontSize:14,fontWeight:700,color:"#ef4444"}}>Data Gate: Upload Required</div><div style={{fontSize:11,color:"#6B7280",marginTop:6}}>Upload and validate data before accessing analysis screens.</div><NB l="Go to Data Upload" onClick={()=>setTab("data")}/></C></div>}

{!gated&&<div style={{maxWidth:1400,margin:"0 auto",padding:"16px 20px"}}>
{recalc&&<div style={{background:"#FFE60015",border:"1px solid #FFE60030",borderRadius:6,padding:"8px 12px",marginBottom:12,display:"flex",alignItems:"center",gap:8,fontSize:11,color:"#FFE600"}}><RefreshCw size={12} style={{animation:"spin 1s linear infinite"}}/>Recalculating all downstream metrics...</div>}

{/* ═══ HOME ═══ */}
{activeTab==="home"&&<>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-end",marginBottom:16}}>
<div><h2 style={{fontSize:20,fontWeight:800,letterSpacing:-.5}}>Executive Dashboard</h2><p style={{color:"#6B7280",fontSize:11,marginTop:3}}>FY 2025 · All Channels</p></div>
<NB l="View Performance" onClick={()=>setTab("performance")}/>
</div>
<div style={{display:"grid",gridTemplateColumns:"repeat(6,1fr)",gap:8,marginBottom:16}}>
<K l="Spend" v={F(kp.s)} a="#3b82f6" onClick={()=>setTab("performance")}/><K l="Revenue" v={F(kp.rv)} a="#10b981" sub={{t:`${FX(kp.roas)} ROAS`,c:"#10b981"}} onClick={()=>setTab("performance")}/><K l="ROI" v={FX(kp.roi)} a="#FFE600" onClick={()=>{setRoiMode("baseROI");setTab("performance")}}/><K l="Conversions" v={kp.cv?.toLocaleString()} a="#0891b2" onClick={()=>setTab("deepdive")}/><K l="CAC" v={F(kp.cac)} a="#d97706" onClick={()=>{setRoiMode("baseROI");setTab("performance")}}/><K l="Value at Risk" v={F(D.pl.totalRisk)} a="#ef4444" sub={{t:"Leakage+CX+Cost",c:"#ef4444"}} onClick={()=>setTab("pillars")}/>
</div>
<div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12,marginBottom:12}}>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>SPEND VS REVENUE</div><ResponsiveContainer width="100%" height={180}><ComposedChart data={mT}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="month" tick={{fill:"#6B7280",fontSize:9}}/><YAxis tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Area dataKey="rv" fill="#FFE60010" stroke="#FFE600" strokeWidth={2} name="Revenue"/><Bar dataKey="s" fill="#3b82f620" name="Spend"/></ComposedChart></ResponsiveContainer></C>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>ONLINE VS OFFLINE</div>
{oVo.online&&<div style={{fontSize:10,lineHeight:2.4}}>
{[["","Online","Offline"],["Spend",F(oVo.online.s),F(oVo.offline.s)],["Revenue",F(oVo.online.rv),F(oVo.offline.rv)],["ROI",FX(oVo.online.roi),FX(oVo.offline.roi)],["ROAS",FX(oVo.online.roas),FX(oVo.offline.roas)],["CAC",F(oVo.online.cac),F(oVo.offline.cac)]].map((r,i)=><div key={i} style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",borderBottom:i===0?"1px solid #3D3D4E":"1px solid #25252F"}}>{r.map((c,j)=><span key={j} style={{fontWeight:i===0||j===0?600:400,color:i===0||j===0?"#9CA3AF":"#E5E7EB",padding:"2px 0"}}>{c}</span>)}</div>)}
</div>}
</C>
</div>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>TOP CHANNELS BY ROI</div>{chD.slice(0,5).map(c=><div key={c.ch} style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid #25252F",cursor:"pointer",fontSize:10}} onClick={()=>{setSelCh(c.ch);setTab("deepdive")}}><div style={{display:"flex",gap:6,alignItems:"center"}}><div style={{width:5,height:5,borderRadius:3,background:c.col}}/>{FN(c.ch)}</div><div style={{display:"flex",gap:12}}><span style={{color:"#6B7280"}}>{F(c.s)}</span><span style={{color:"#FFE600",fontWeight:700}}>{FX(c.roi)}</span></div></div>)}</C>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>PRIORITY ACTIONS</div>{recs.slice(0,5).map((r,i)=><div key={i} style={{padding:"5px 0",borderBottom:"1px solid #25252F",fontSize:10,display:"flex",gap:4,alignItems:"center",cursor:"pointer"}} onClick={()=>setTab("recommendations")}><B c={r.type==="SCALE"?"#10b981":r.type==="REDUCE"?"#ef4444":"#d97706"}>{r.type}</B><span style={{color:"#9CA3AF"}}>{FN(r.ch)}</span>{r.impact>0&&<span style={{marginLeft:"auto",color:"#10b981",fontWeight:700}}>+{F(r.impact)}</span>}</div>)}</C>
</div>
</>}

{/* ═══ DATA ═══ */}
{activeTab==="data"&&<>
<h2 style={{fontSize:20,fontWeight:800,marginBottom:12}}>Data Readiness</h2>
<Tip>Upload your campaign performance CSV and optionally user journey CSV. Required columns: date, channel, campaign, spend, revenue.</Tip>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:12}}>
{/* File 1: Campaign Performance */}
<C style={{border:`2px dashed ${uploadStep>=1?"#10b981":"#3D3D4E"}`,textAlign:"center",padding:28,cursor:"pointer",position:"relative"}} onClick={()=>document.getElementById("csvUp1")?.click()}>
<input id="csvUp1" type="file" accept=".csv" style={{display:"none"}} onChange={e=>{const f=e.target.files?.[0];if(!f)return;const r=new FileReader();r.onload=ev=>{try{handleUpload(ev.target.result,"campaign")}catch(err){setUploadStep(-1)}};r.readAsText(f)}}/>
<UploadCloud size={28} color={uploadStep>=2?"#10b981":"#6B7280"} style={{margin:"0 auto 8px"}}/><div style={{fontSize:13,fontWeight:700,marginBottom:3}}>1. Campaign Performance CSV</div><div style={{fontSize:10,color:"#6B7280",marginBottom:8}}>Daily data — spend, revenue, conversions by channel/campaign</div>
<div style={{display:"flex",gap:3,justifyContent:"center",flexWrap:"wrap"}}>{["date*","channel*","campaign*","spend*","revenue*","impressions","clicks","leads","conversions","region"].map(c=><B key={c} c={c.includes("*")?"#ef4444":"#6B7280"}>{c.replace("*","")}</B>)}</div>
{uploadStep===2&&<div style={{marginTop:10,color:"#10b981",fontSize:11,fontWeight:600}}><CheckCircle size={12}/> {rawRows?.length.toLocaleString()} rows parsed · columns auto-mapped</div>}
{uploadStep===-1&&<div style={{marginTop:10,color:"#ef4444",fontSize:11}}><XCircle size={12}/> Parse error — check CSV format</div>}
</C>
{/* File 2: User Journeys */}
<C style={{border:`2px dashed ${uploadStep>=3?"#10b981":"#3D3D4E"}`,textAlign:"center",padding:28,cursor:"pointer",position:"relative"}} onClick={()=>document.getElementById("csvUp2")?.click()}>
<input id="csvUp2" type="file" accept=".csv" style={{display:"none"}} onChange={e=>{const f=e.target.files?.[0];if(!f)return;const r=new FileReader();r.onload=ev=>{try{handleUpload(ev.target.result,"journey")}catch(err){}};r.readAsText(f)}}/>
<Users size={28} color={uploadStep>=3?"#10b981":"#6B7280"} style={{margin:"0 auto 8px"}}/><div style={{fontSize:13,fontWeight:700,marginBottom:3}}>2. User Journeys CSV <span style={{fontWeight:400,color:"#6B7280"}}>(Optional)</span></div><div style={{fontSize:10,color:"#6B7280",marginBottom:8}}>Touchpoint-level data for multi-touch attribution</div>
<div style={{display:"flex",gap:3,justifyContent:"center",flexWrap:"wrap"}}>{["journey_id*","touchpoint_order*","channel*","campaign*","converted*","conversion_revenue*"].map(c=><B key={c} c="#6B7280">{c.replace("*","")}</B>)}</div>
{uploadStep>=3&&rawJs&&<div style={{marginTop:10,color:"#10b981",fontSize:11,fontWeight:600}}><CheckCircle size={12}/> {rawJs.length.toLocaleString()} journeys parsed</div>}
{!rawJs&&uploadStep>=2&&<div style={{marginTop:10,color:"#d97706",fontSize:10}}>Without this file, only Last-Touch attribution is available</div>}
</C>
</div>
{/* Action buttons */}
<div style={{display:"flex",gap:8,marginBottom:12}}>
<Btn onClick={loadDemo}><Play size={12}/>Load Demo Data</Btn>
{rawRows&&!analysisRun&&<Btn primary onClick={()=>{setMapOk(true);runAllEngines(rawRows,rawJs)}}><Zap size={12}/>Run Analysis on Uploaded Data</Btn>}
{analysisRun&&<div style={{display:"flex",alignItems:"center",gap:6,fontSize:11,color:"#10b981"}}><CheckCircle size={14}/>Analysis complete — all engines processed</div>}
</div>
{/* Quality Scorecard */}
{(rawRows||D)&&<div style={{display:"grid",gridTemplateColumns:"1fr 2fr",gap:12,marginBottom:12}}>
<C>
<div style={{fontSize:12,fontWeight:700,marginBottom:10}}>Quality Scorecard</div>
<div style={{display:"flex",gap:12,alignItems:"center"}}>
<div style={{position:"relative",width:60,height:60}}><svg viewBox="0 0 36 36" style={{width:60,height:60,transform:"rotate(-90deg)"}}><circle cx="18" cy="18" r="15.9" fill="none" stroke="#2E2E3E" strokeWidth="3"/><circle cx="18" cy="18" r="15.9" fill="none" stroke="#10b981" strokeWidth="3" strokeDasharray={`${qScore} ${100-qScore}`}/></svg><div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",fontSize:15,fontWeight:800,color:"#10b981"}}>{qScore}</div></div>
<div style={{fontSize:10,color:"#9CA3AF",lineHeight:2}}>
<div><CheckCircle size={10} color="#10b981"/> {(rawRows||fd).length>0?[...new Set((rawRows||fd).map(r=>r.ch))].length:0} channels</div>
<div><CheckCircle size={10} color="#10b981"/> {(rawRows||fd).length>0?[...new Set((rawRows||fd).map(r=>r.camp))].length:0} campaigns</div>
<div><CheckCircle size={10} color="#10b981"/> {(rawRows||fd).length>0?[...new Set((rawRows||fd).map(r=>r.month))].length:0} periods</div>
<div><CheckCircle size={10} color="#10b981"/> {(rawRows||fd).length.toLocaleString()} rows</div>
</div></div>
{dataOk&&<NB l="Configure Mapping" onClick={()=>{setMapOk(true);setTab("mapping")}}/>}
</C>
<C><div style={{fontSize:12,fontWeight:700,marginBottom:8}}>Data Preview</div><div style={{overflowX:"auto"}}><table><thead><tr>{["Date","Channel","Campaign","Region","Spend","Revenue","Conv","Confidence"].map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{(rawRows||fd).slice(0,6).map((r,i)=><tr key={i}><td>{r.month||r.date}</td><td style={{color:CH[r.ch]?.color}}>{FN(r.ch)}</td><td>{r.camp}</td><td>{r.reg}</td><td>{F(r.spend)}</td><td>{F(r.rev)}</td><td>{r.conv}</td><td><B c={r.conf==="High"?"#10b981":"#d97706"}>{r.conf||"—"}</B></td></tr>)}</tbody></table></div></C>
</div>}
</>}

{/* ═══ MAPPING ═══ */}
{activeTab==="mapping"&&<>
<h2 style={{fontSize:20,fontWeight:800,marginBottom:12}}>Column Mapping & Taxonomy</h2>
<Tip>Review auto-detected mappings below. Use dropdowns to reassign columns. Unmapped required fields block analysis.</Tip>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:12}}>
<C><div style={{fontSize:12,fontWeight:700,marginBottom:10}}>Column Mapping</div>
{Object.entries(colMap).map(([std,mapping])=>{
const src=typeof mapping==="string"?mapping:mapping?.src;const conf=typeof mapping==="object"?mapping?.conf:1;const status=typeof mapping==="object"?mapping?.status:"auto";
return<div key={std} style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"5px 0",borderBottom:"1px solid #25252F",fontSize:10}}>
<div style={{display:"flex",alignItems:"center",gap:6}}><B c={["date","channel","campaign","spend","revenue"].includes(std)?"#ef4444":"#FFE600"}>{std}{["date","channel","campaign","spend","revenue"].includes(std)?"*":""}</B><ArrowRight size={10} color="#6B7280"/>
<select value={src||""} onChange={e=>{setColMap(prev=>({...prev,[std]:{src:e.target.value,conf:1,status:"manual"}}));setRecalc(true);setTimeout(()=>setRecalc(false),500)}} style={{minWidth:90}}>
<option value="">-- unmapped --</option>{availCols.map(c=><option key={c} value={c}>{c}</option>)}
</select></div>
<div style={{display:"flex",alignItems:"center",gap:4}}>
{conf>=.7?<CheckCircle size={12} color="#10b981"/>:conf>=.3?<AlertTriangle size={12} color="#d97706"/>:<XCircle size={12} color="#ef4444"/>}
<span style={{fontSize:8,color:"#6B7280"}}>{status==="auto"?"Auto":status==="manual"?"Manual":"Suggested"}</span>
</div></div>})}
<div style={{fontSize:8,color:"#6B7280",marginTop:6}}>* Required fields</div>
</C>
<C><div style={{fontSize:12,fontWeight:700,marginBottom:10}}>Channel Taxonomy</div>
{Object.entries(CH).map(([ch,ci])=><div key={ch} style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid #25252F",fontSize:10}}>
<div style={{display:"flex",alignItems:"center",gap:6}}><div style={{width:5,height:5,borderRadius:3,background:ci.color}}/>{ci.label}<B c={ci.type==="online"?"#3b82f6":"#be185d"}>{ci.type}</B></div>
<span style={{color:"#6B7280"}}>{CAMPS[ch].length} campaigns <CheckCircle size={10} color="#10b981"/></span>
</div>)}
</C></div>
{/* Unmapped Queue */}
{(()=>{const unmapped=Object.entries(colMap).filter(([,m])=>(typeof m==="object"?m.status:null)==="unmapped"||(typeof m==="object"?m.conf:1)<.3);
const unmappedCh=fd.length>0?[...new Set(fd.map(r=>r.ch))].filter(ch=>!CH[ch]).map(ch=>({ch,spend:fd.filter(r=>r.ch===ch).reduce((a,r)=>a+r.spend,0),rows:fd.filter(r=>r.ch===ch).length})).sort((a,b)=>b.spend-a.spend):[];
return(unmapped.length>0||unmappedCh.length>0)?<C style={{marginBottom:12}}><div style={{fontSize:12,fontWeight:700,color:"#ef4444",marginBottom:8}}>Unmapped Items (ranked by spend)</div>
{unmapped.map(([std,m])=><div key={std} style={{display:"flex",justifyContent:"space-between",padding:"4px 0",borderBottom:"1px solid #25252F",fontSize:10}}><span><B c="#ef4444">FIELD</B> {std}</span><span style={{color:"#ef4444"}}>Not mapped</span></div>)}
{unmappedCh.map((u,i)=><div key={i} style={{display:"flex",justifyContent:"space-between",padding:"4px 0",borderBottom:"1px solid #25252F",fontSize:10}}><span><B c="#d97706">CHANNEL</B> {u.ch} ({u.rows} rows)</span><span style={{color:"#d97706",fontWeight:600}}>{F(u.spend)}</span></div>)}
{unmapped.length===0&&unmappedCh.length===0&&<div style={{color:"#10b981",fontSize:10}}>All items mapped ✓</div>}
</C>:null})()}
<NB l="Proceed to Analysis" onClick={()=>setTab("performance")}/>
</>}

{/* ═══ PERFORMANCE ═══ */}
{activeTab==="performance"&&<>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
<h2 style={{fontSize:20,fontWeight:800}}>Performance Analysis</h2>
<div style={{display:"flex",gap:3}}>{[["last_touch","Last Touch"],["linear","Linear"],["position_based","Position"],["markov","Markov"]].map(([k,l])=><Btn key={k} primary={atM===k} onClick={()=>setAtM(k)}>{l}</Btn>)}</div>
</div>
<div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:8,marginBottom:12}}>
<K l="Spend" v={F(kp.s)} a="#3b82f6" sub={trend?.monthly?.[11]?.sChg?{t:`MoM ${FP(trend.monthly[11].sChg)}`,c:trend.monthly[11].sChg>0?"#ef4444":"#10b981"}:undefined}/><K l="Revenue" v={F(kp.rv)} a="#10b981" sub={trend?.monthly?.[11]?.rvChg?{t:`MoM ${FP(trend.monthly[11].rvChg)}`,c:trend.monthly[11].rvChg>0?"#10b981":"#ef4444"}:undefined}/><K l="ROI" v={FX(kp.roi)} a="#FFE600"/><K l="ROAS" v={FX(kp.roas)} a="#d97706"/><K l="CVR" v={`${(kp.cvr*100).toFixed(2)}%`} a="#0891b2"/>
</div>

{/* ROI Formula Toggle */}
{roiData&&<C style={{marginBottom:12}}><div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:8}}>
<div style={{fontSize:10,fontWeight:700,color:"#6B7280"}}>ALL 5 ROI FORMULAS</div>
<div style={{display:"flex",gap:3}}>{[["baseROI","Base ROI"],["gmROI","Gross Margin"],["roas","ROAS"],["incROI","Incremental"],["margROI","Marginal"]].map(([k,l])=><Btn key={k} primary={roiMode===k} onClick={()=>setRoiMode(k)} style={{fontSize:9,padding:"4px 8px"}}>{l}</Btn>)}</div>
{roiMode==="gmROI"&&<div style={{display:"flex",alignItems:"center",gap:4,fontSize:9,color:"#6B7280"}}>GM%:<input type="range" min={30} max={90} value={gmPct} onChange={e=>setGmPct(parseInt(e.target.value))} style={{width:60}}/>{gmPct}%</div>}
</div>
<table><thead><tr><th>Channel</th><th>Conf</th><th style={{textAlign:"right"}}>Spend</th><th style={{textAlign:"right"}}>Revenue</th><th style={{textAlign:"right"}}>{roiMode==="baseROI"?"Base ROI":roiMode==="gmROI"?"GM ROI":roiMode==="roas"?"ROAS":roiMode==="incROI"?"Inc ROI":"Marginal"}</th><th style={{textAlign:"right"}}>CAC</th><th style={{textAlign:"right"}}>Payback</th><th>Consistency</th></tr></thead>
<tbody>{roiData.map(r=>{const val=r[roiMode];const cons=trend?.roiCons?.[r.ch];return<tr key={r.ch}>
<td style={{color:CH[r.ch]?.color,fontWeight:600}}>{FN(r.ch)}</td>
<td><B c={CH[r.ch]?.type==="online"?"#10b981":"#d97706"}>{CH[r.ch]?.type==="online"?"High":"Est."}</B></td>
<td style={{textAlign:"right"}}>{F(r.spend)}</td><td style={{textAlign:"right"}}>{F(r.revenue)}</td>
<td style={{textAlign:"right",color:val>2?"#10b981":val>1?"#FFE600":"#ef4444",fontWeight:700}}>{FX(val)}</td>
<td style={{textAlign:"right"}}>{F(r.cac)}</td>
<td style={{textAlign:"right"}}>{r.payback}mo</td>
<td>{cons&&<B c={cons.consistency==="High"?"#10b981":cons.consistency==="Medium"?"#d97706":"#ef4444"}>{cons.consistency}</B>}</td>
</tr>})}</tbody></table>
<div style={{fontSize:8,color:"#6B7280",marginTop:6}}>Formula: {roiMode==="baseROI"?"(Revenue − Cost) / Cost":roiMode==="gmROI"?`(Revenue × ${gmPct}% − Cost) / Cost`:roiMode==="roas"?"Revenue / Spend":roiMode==="incROI"?"(ΔRevenue − ΔSpend) / ΔSpend vs Q1 baseline":"dRevenue/dSpend from response curve"}</div>
</C>}

{/* Trend & Anomaly Flags */}
{trend&&<C style={{marginBottom:12}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>TREND ANALYSIS {trend.anomalies.length>0&&<B c="#ef4444">{trend.anomalies.length} anomalies</B>}</div>
<div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12}}>
<div><ResponsiveContainer width="100%" height={160}><ComposedChart data={trend.monthly}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="month" tick={{fill:"#6B7280",fontSize:9}}/><YAxis tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={(v,n)=>n==="ma3"?F(v):n==="rvChg"?FP(v):F(v)}/><Area dataKey="rv" fill="#FFE60010" stroke="#FFE600" strokeWidth={1.5} name="Revenue"/><Line dataKey="ma3" stroke="#10b981" strokeWidth={2} dot={false} strokeDasharray="4 4" name="3M MA"/></ComposedChart></ResponsiveContainer></div>
<div style={{fontSize:10}}>
<div style={{fontWeight:700,marginBottom:6,color:"#FFE600"}}>H1 vs H2 Variance</div>
{trend.varDecomp.slice(0,5).map(v=><div key={v.ch} style={{display:"flex",justifyContent:"space-between",padding:"3px 0",borderBottom:"1px solid #25252F"}}><span style={{color:CH[v.ch]?.color}}>{FN(v.ch)}</span><span style={{color:v.change>0?"#10b981":"#ef4444",fontWeight:600}}>{v.change>0?"+":""}{F(v.change)}</span></div>)}
{trend.anomalies.length>0&&<div style={{marginTop:8}}><div style={{fontWeight:700,color:"#ef4444",marginBottom:4}}>Anomalies</div>
{trend.anomalies.map((a,i)=><div key={i} style={{fontSize:9,color:"#9CA3AF",padding:"2px 0"}}><B c={a.dir==="spike"?"#10b981":"#ef4444"}>{a.dir}</B> {a.month} z={a.z}</div>)}</div>}
</div></div></C>}

{/* Attribution comparison */}
<C style={{marginBottom:12}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>ATTRIBUTION MODEL COMPARISON (4 MODELS)</div>
<div style={{overflowX:"auto"}}><table><thead><tr><th>Channel</th><th style={{textAlign:"right"}}>Last Touch</th><th style={{textAlign:"right"}}>Linear</th><th style={{textAlign:"right"}}>Position</th><th style={{textAlign:"right"}}>Markov</th><th style={{textAlign:"right"}}>Variance</th></tr></thead>
<tbody>{Object.keys(CH).map(ch=>{const lt=D.attr.last_touch[ch]||0,ln=D.attr.linear[ch]||0,pb=D.attr.position_based[ch]||0,mk=markov?.channels?.[ch]?.revenue||0;const all=[lt,ln,pb,mk].filter(v=>v>0);const avg=all.reduce((a,b)=>a+b,0)/all.length||1;const v=Math.max(...all)-Math.min(...all);return<tr key={ch}><td style={{color:CH[ch]?.color,fontWeight:600}}>{FN(ch)}</td><td style={{textAlign:"right",fontWeight:atM==="last_touch"?700:400,color:atM==="last_touch"?"#FFE600":"#E5E7EB"}}>{F(lt)}</td><td style={{textAlign:"right",fontWeight:atM==="linear"?700:400,color:atM==="linear"?"#FFE600":"#E5E7EB"}}>{F(ln)}</td><td style={{textAlign:"right",fontWeight:atM==="position_based"?700:400,color:atM==="position_based"?"#FFE600":"#E5E7EB"}}>{F(pb)}</td><td style={{textAlign:"right",fontWeight:atM==="markov"?700:400,color:atM==="markov"?"#FFE600":"#E5E7EB"}}>{F(mk)}</td><td style={{textAlign:"right",color:v/avg>.3?"#ef4444":"#6B7280"}}>{F(v)}{v/avg>.3?" ⚠️":""}</td></tr>})}</tbody></table></div></C>

{/* MMM Channel Contribution */}
{mmm&&<C style={{marginBottom:12}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>MMM CHANNEL CONTRIBUTION <B c="#FFE600">Phase 2</B></div>
<div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12}}>
<div><ResponsiveContainer width="100%" height={200}><BarChart data={Object.entries(mmm.contributions).map(([ch,c])=>({ch:FN(ch),contribution:c.contribution,spend:c.spend})).sort((a,b)=>b.contribution-a.contribution)} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis type="number" tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><YAxis dataKey="ch" type="category" tick={{fill:"#6B7280",fontSize:8}} width={80}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Legend wrapperStyle={{fontSize:9}}/><Bar dataKey="contribution" fill="#FFE600" name="MMM Contribution" radius={[0,3,3,0]}/><Bar dataKey="spend" fill="#3D3D4E" name="Spend" radius={[0,3,3,0]}/></BarChart></ResponsiveContainer></div>
<div style={{fontSize:10,lineHeight:2}}>
<div style={{fontWeight:700,color:"#FFE600",marginBottom:4}}>Model Summary</div>
<div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>Baseline (organic)</span><span style={{fontWeight:600}}>{F(mmm.baseline)} ({mmm.baselinePct}%)</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>Media-driven</span><span style={{fontWeight:600}}>{F(mmm.totalRev-mmm.baseline)} ({(100-mmm.baselinePct).toFixed(1)}%)</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>Total Revenue</span><span style={{fontWeight:600}}>{F(mmm.totalRev)}</span></div>
<div style={{marginTop:8,fontSize:9,color:"#6B7280"}}>MMM decomposes revenue into baseline (organic demand) + media contributions. Offline channels get model-estimated confidence.</div>
</div></div></C>}

{/* ROI Heatmap */}
<C style={{marginBottom:12}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>ROI HEATMAP — CHANNEL × CAMPAIGN</div>
<div style={{display:"flex",flexWrap:"wrap",gap:3}}>{heatData.map((h,i)=><div key={i} title={`${h.name} (${h.channel}): ${FX(h.roi)} ROI | ${F(h.spend)} spend`} style={{width:Math.max(40,Math.min(90,h.spend/1e4)),height:28,background:h.color+"30",border:`1px solid ${h.color}60`,borderRadius:3,display:"flex",alignItems:"center",justifyContent:"center",fontSize:7,color:h.color,fontWeight:700,cursor:"pointer",overflow:"hidden",padding:"0 2px"}} onClick={()=>{setSelCh(h.name.split(" ")[0]==="PS"?"paid_search":undefined);setTab("deepdive")}}>{FX(h.roi)}</div>)}</div>
<div style={{display:"flex",gap:8,marginTop:6,fontSize:9,color:"#6B7280"}}><span><span style={{display:"inline-block",width:8,height:8,borderRadius:2,background:"#10b98130",marginRight:3}}/>5x+</span><span><span style={{display:"inline-block",width:8,height:8,borderRadius:2,background:"#FFE60030",marginRight:3}}/>2-5x</span><span><span style={{display:"inline-block",width:8,height:8,borderRadius:2,background:"#d9770630",marginRight:3}}/>1-2x</span><span><span style={{display:"inline-block",width:8,height:8,borderRadius:2,background:"#ef444430",marginRight:3}}/>&lt;1x</span></div>
</C>

{/* Campaign table */}
<C style={{marginBottom:12,overflowX:"auto"}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>CHANNEL-CAMPAIGN MATRIX</div>
<table><thead><tr><th>Campaign</th><th>Channel</th><th style={{textAlign:"right"}}>Spend</th><th style={{textAlign:"right"}}>Revenue</th><th style={{textAlign:"right"}}>ROI</th><th style={{textAlign:"right"}}>ROAS</th><th style={{textAlign:"right"}}>CTR</th><th style={{textAlign:"right"}}>CVR</th><th style={{textAlign:"right"}}>CAC</th><th>Conf</th></tr></thead>
<tbody>{cpD.slice(0,18).map(c=><tr key={`${c.ch}-${c.camp}`} style={{cursor:"pointer"}} onClick={()=>{setSelCh(c.ch);setSelCp(c.camp);setTab("deepdive")}}>
<td style={{fontWeight:500}}>{c.camp}</td><td style={{color:c.col}}>{FN(c.ch)}</td>
<td style={{textAlign:"right"}}>{F(c.s)}</td><td style={{textAlign:"right"}}>{F(c.rv)}</td>
<td style={{textAlign:"right",color:c.roi>3?"#10b981":c.roi>1.5?"#FFE600":"#ef4444",fontWeight:700}}>{FX(c.roi)}</td>
<td style={{textAlign:"right"}}>{FX(c.roas)}</td><td style={{textAlign:"right"}}>{(c.ctr*100).toFixed(1)}%</td>
<td style={{textAlign:"right"}}>{(c.cvr*100).toFixed(2)}%</td><td style={{textAlign:"right"}}>{F(c.cac)}</td>
<td><B c={c.ct==="online"?"#10b981":"#d97706"}>{c.ct==="online"?"High":"Est."}</B></td>
</tr>)}</tbody></table></C>

<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>ROI BY CHANNEL</div><ResponsiveContainer width="100%" height={200}><BarChart data={chD} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis type="number" tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>FX(v)}/><YAxis dataKey="ch" type="category" tick={{fill:"#6B7280",fontSize:8}} width={80} tickFormatter={v=>FN(v)}/><Tooltip contentStyle={tt} formatter={v=>FX(v)}/><Bar dataKey="roi">{chD.map((c,i)=><Cell key={i} fill={c.col}/>)}</Bar></BarChart></ResponsiveContainer></C>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>SPEND → REVENUE WATERFALL</div><ResponsiveContainer width="100%" height={200}><BarChart data={[{name:"Total Spend",value:kp.s,fill:"#ef4444"},{name:"Impressions",value:kp.cl*50,fill:"#3b82f6"},{name:"Leads",value:fd.reduce((a,r)=>a+r.leads,0)*200,fill:"#0891b2"},{name:"Conversions",value:kp.cv*500,fill:"#d97706"},{name:"Revenue",value:kp.rv,fill:"#10b981"}]}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="name" tick={{fill:"#6B7280",fontSize:8}}/><YAxis tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Bar dataKey="value">{[{fill:"#ef4444"},{fill:"#3b82f6"},{fill:"#0891b2"},{fill:"#d97706"},{fill:"#10b981"}].map((c,i)=><Cell key={i} fill={c.fill}/>)}</Bar></BarChart></ResponsiveContainer></C>
</div>
<NB l="Channel Deep Dive" onClick={()=>setTab("deepdive")}/>
</>}

{/* ═══ DEEP DIVE ═══ */}
{activeTab==="deepdive"&&<>
<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:12}}>
<h2 style={{fontSize:20,fontWeight:800}}>Deep Dive</h2>
<select value={selCh||""} onChange={e=>{setSelCh(e.target.value);setSelCp(null)}}><option value="">Channel...</option>{Object.keys(CH).map(ch=><option key={ch} value={ch}>{FN(ch)}</option>)}</select>
{selCh&&<select value={selCp||""} onChange={e=>setSelCp(e.target.value)}><option value="">All campaigns</option>{CAMPS[selCh]?.map(c=><option key={c} value={c}>{c}</option>)}</select>}
</div>
{selCh&&(()=>{
const cr=fd.filter(r=>r.ch===selCh&&(!selCp||r.camp===selCp));
const mo={};cr.forEach(r=>{if(!mo[r.month])mo[r.month]={month:r.ml,s:0,rv:0,cv:0};mo[r.month].s+=r.spend;mo[r.month].rv+=r.rev;mo[r.month].cv+=r.conv});
const cv=D.curves[selCh];
const fn={Impressions:0,Clicks:0,Leads:0,MQLs:0,SQLs:0,Conversions:0};
cr.forEach(r=>{fn.Impressions+=r.imps;fn.Clicks+=r.clicks;fn.Leads+=r.leads;fn.MQLs+=r.mqls;fn.SQLs+=r.sqls;fn.Conversions+=r.conv});
const fD=Object.entries(fn);const fRates=fD.map(([k,v],i)=>({stage:k,value:v,rate:i===0?null:fD[i-1][1]>0?(v/fD[i-1][1]*100).toFixed(1)+"%":"0%"}));
const rg={};cr.forEach(r=>{if(!rg[r.reg])rg[r.reg]={region:r.reg,s:0,rv:0};rg[r.reg].s+=r.spend;rg[r.reg].rv+=r.rev});
const ab=cr.reduce((a,r)=>a+r.br,0)/cr.length,as=cr.reduce((a,r)=>a+r.sd,0)/cr.length,af=cr.reduce((a,r)=>a+r.fc,0)/cr.length,an=cr.reduce((a,r)=>a+r.nps,0)/cr.length;
// Cross-channel paths involving this channel
const paths=xCh.filter(p=>p.from===selCh||p.to===selCh);

return<>
<div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:12}}>
<K l="Spend" v={F(cr.reduce((a,r)=>a+r.spend,0))} a="#3b82f6"/><K l="Revenue" v={F(cr.reduce((a,r)=>a+r.rev,0))} a="#10b981"/><K l="ROI" v={FX((cr.reduce((a,r)=>a+r.rev,0)-cr.reduce((a,r)=>a+r.spend,0))/cr.reduce((a,r)=>a+r.spend,0))} a="#FFE600"/><K l="Conv" v={cr.reduce((a,r)=>a+r.conv,0).toLocaleString()} a="#0891b2"/>
</div>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:12}}>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>TREND</div><ResponsiveContainer width="100%" height={160}><ComposedChart data={Object.values(mo)}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="month" tick={{fill:"#6B7280",fontSize:9}}/><YAxis tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Bar dataKey="s" fill="#3b82f620" name="Spend"/><Line dataKey="rv" stroke="#FFE600" strokeWidth={2} dot={false} name="Revenue"/></ComposedChart></ResponsiveContainer></C>
{cv&&<C><div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:3}}>
<div style={{fontSize:10,fontWeight:700,color:"#6B7280"}}>RESPONSE CURVE</div>
<div style={{display:"flex",gap:3}}><Btn primary={!hillMode} onClick={()=>setHillMode(false)} style={{fontSize:8,padding:"2px 6px"}}>Power-Law</Btn><Btn primary={hillMode} onClick={()=>setHillMode(true)} style={{fontSize:8,padding:"2px 6px"}}>Hill <B c="#FFE600">P2</B></Btn></div>
</div>
<div style={{fontSize:9,color:"#6B7280",marginBottom:4}}>{hillMode?`Hill: y = a·x^b / (K^b+x^b) | K≈${F(cv.avgSpend)}`:`y=${cv.a.toFixed(1)}·x^${cv.b.toFixed(2)}`} | Headroom: <span style={{color:cv.hd>30?"#10b981":"#d97706",fontWeight:700}}>{cv.hd.toFixed(0)}%</span></div>
<ResponsiveContainer width="100%" height={140}><ComposedChart data={hillMode?cv.cp.map(p=>{const K=cv.avgSpend;const xb=Math.pow(Math.max(p.spend,1),cv.b);const Kb=Math.pow(K,cv.b);return{spend:p.spend,revenue:Math.round(cv.a*10*xb/(Kb+xb))}}):cv.cp}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="spend" tick={{fill:"#6B7280",fontSize:8}} tickFormatter={v=>F(v)}/><YAxis tick={{fill:"#6B7280",fontSize:8}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Line dataKey="revenue" stroke={hillMode?"#7c3aed":"#FFE600"} strokeWidth={2} dot={false} name={hillMode?"Hill":"Power-Law"}/><ReferenceLine x={Math.round(cv.avgSpend)} stroke="#d97706" strokeDasharray="4 4"/></ComposedChart></ResponsiveContainer>
<div style={{fontSize:8,color:"#6B7280",marginTop:4}}>● Data points: {cv.dp.map(p=>F(p.spend)).join(", ")}</div>
</C>}
</div>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:12}}>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>FUNNEL WITH DROP-OFF</div>
{fRates.map(([stage,val],i)=><div key={stage} style={{display:"flex",justifyContent:"space-between",padding:"4px 0",borderBottom:"1px solid #25252F",fontSize:10}}>
<span>{stage}</span><div style={{display:"flex",gap:8}}><span style={{color:"#E5E7EB"}}>{val>=1e3?`${(val/1e3).toFixed(0)}K`:val}</span>{fRates[i]?.rate&&<span style={{color:parseFloat(fRates[i].rate)<30?"#ef4444":"#6B7280",fontSize:9}}>{fRates[i].rate}</span>}</div>
</div>)}
</C>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>CX SIGNALS</div>
<div style={{fontSize:10,lineHeight:2.4}}>{[["Bounce Rate",(ab*100).toFixed(0)+"%",ab>.5?"#ef4444":"#10b981"],["Session Dur",as.toFixed(0)+"s","#E5E7EB"],["Form %",(af*100).toFixed(0)+"%",af<.08?"#d97706":"#10b981"],["NPS",an.toFixed(0),an<30?"#d97706":"#10b981"]].map(([l,v,c])=><div key={l} style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>{l}</span><span style={{color:c,fontWeight:600}}>{v}</span></div>)}</div>
</C>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>CROSS-CHANNEL INFLUENCE</div>
{paths.length>0?paths.slice(0,6).map((p,i)=><div key={i} style={{display:"flex",justifyContent:"space-between",padding:"3px 0",borderBottom:"1px solid #25252F",fontSize:9}}>
<span>{FN(p.from)} → {FN(p.to)}</span><span style={{color:"#FFE600"}}>{p.count} paths</span>
</div>):<div style={{color:"#6B7280",fontSize:10,padding:10}}>Select a channel to see influence paths</div>}
</C>
</div>
{/* Funnel Bottlenecks & Revenue Impact */}
{funnel&&funnel.bottlenecks.length>0&&<C style={{marginTop:12}}><div style={{fontSize:10,fontWeight:700,color:"#ef4444",marginBottom:8}}>FUNNEL BOTTLENECKS <B c="#ef4444">{funnel.bottlenecks.length} detected</B></div>
<table><thead><tr><th>Stage</th><th style={{textAlign:"right"}}>Actual</th><th style={{textAlign:"right"}}>Benchmark</th><th style={{textAlign:"right"}}>Gap</th><th style={{textAlign:"right"}}>Lost Volume</th><th>Severity</th></tr></thead>
<tbody>{funnel.bottlenecks.map((b,i)=><tr key={i}><td>{b.from} → {b.stage}</td><td style={{textAlign:"right"}}>{(b.actual*100).toFixed(1)}%</td><td style={{textAlign:"right"}}>{(b.benchmark*100).toFixed(1)}%</td><td style={{textAlign:"right",color:"#ef4444"}}>{b.gap}%</td><td style={{textAlign:"right"}}>{b.lostVolume.toLocaleString()}</td><td><B c={b.severity==="critical"?"#ef4444":"#d97706"}>{b.severity}</B></td></tr>)}</tbody></table>
{funnel.totalImpact>0&&<div style={{marginTop:8,fontSize:10,color:"#10b981",fontWeight:700}}>Addressable revenue if fixed to median: {F(funnel.totalImpact)}</div>}
</C>}
{/* Adstock Decay */}
{adst&&adst[selCh]&&<C style={{marginTop:12}}><div style={{fontSize:10,fontWeight:700,color:"#FFE600",marginBottom:6}}>ADSTOCK & CARRYOVER <B c="#FFE600">Phase 2</B></div>
<div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12}}>
<ResponsiveContainer width="100%" height={140}><ComposedChart data={adst[selCh].original.map((s,i)=>({period:MO[i]||i,original:s,adstocked:Math.round(adst[selCh].adstocked[i]),revenue:adst[selCh].revenue[i]}))}>
<CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="period" tick={{fill:"#6B7280",fontSize:9}}/><YAxis tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/>
<Bar dataKey="original" fill="#3D3D4E" name="Raw Spend" radius={[2,2,0,0]}/><Line dataKey="adstocked" stroke="#FFE600" strokeWidth={2} dot={false} name="Adstocked"/><Line dataKey="revenue" stroke="#10b981" strokeWidth={1.5} dot={false} strokeDasharray="4 4" name="Revenue"/>
</ComposedChart></ResponsiveContainer>
<div style={{fontSize:10,lineHeight:2.2}}>
<div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>Decay Rate</span><span style={{color:"#FFE600",fontWeight:700}}>{adst[selCh].decay}</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>Correlation</span><span style={{fontWeight:600}}>{adst[selCh].correlation}</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>Carryover Effect</span><span style={{fontWeight:600}}>{adst[selCh].carryoverPct}%</span></div>
<div style={{fontSize:8,color:"#6B7280",marginTop:6}}>Adstock models the lagged effect of spend — today's ad influences conversions for {Math.round(1/(1-adst[selCh].decay))} periods.</div>
</div></div></C>}
</>})()}
{!selCh&&<C style={{textAlign:"center",padding:40}}><Search size={24} color="#3D3D4E" style={{margin:"0 auto 8px"}}/><div style={{color:"#6B7280",fontSize:11}}>Select a channel above</div></C>}
</>}

{/* ═══ PILLARS ═══ */}
{activeTab==="pillars"&&<>
<h2 style={{fontSize:20,fontWeight:800,marginBottom:12}}>Leakage, Experience & Avoidable Cost</h2>
<div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:12}}>
<K l="Total at Risk" v={F(D.pl.totalRisk)} a="#ef4444"/><K l="Rev Leakage" v={F(D.pl.leak.total)} a="#ef4444" sub={{t:`${D.pl.leak.pct.toFixed(1)}%`,c:"#6B7280"}}/><K l="CX Suppression" v={F(D.pl.exp.total)} a="#d97706" sub={{t:`${D.pl.exp.items.length} campaigns`,c:"#6B7280"}}/><K l="Avoidable Cost" v={F(D.pl.cost.total)} a="#7c3aed" sub={{t:`${D.pl.cost.items.length} drivers`,c:"#6B7280"}}/>
</div>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:12}}>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>LEAKAGE BY CHANNEL</div>{D.pl.leak.byCh.length>0?<ResponsiveContainer width="100%" height={180}><BarChart data={D.pl.leak.byCh} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis type="number" tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><YAxis dataKey="channel" type="category" tick={{fill:"#6B7280",fontSize:8}} width={80} tickFormatter={v=>FN(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Bar dataKey="leakage" fill="#ef4444" radius={[0,3,3,0]}/></BarChart></ResponsiveContainer>:<div style={{padding:30,textAlign:"center",color:"#6B7280",fontSize:10}}>Near-optimal allocation</div>}</C>
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>AVOIDABLE COST (FULL BREAKDOWN)</div>
{D.pl.cost.items.map((it,i)=><div key={i} style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid #25252F",fontSize:10}}><div><div style={{fontWeight:600}}>{it.type}</div><div style={{color:"#6B7280",fontSize:9}}>{FN(it.ch)} · {F(it.cac)} vs {F(it.bm)}</div></div><div style={{color:"#ef4444",fontWeight:700}}>{F(it.av)}</div></div>)}
{/* Lead waste estimate */}
{(()=>{const chM={};fd.forEach(r=>{if(!chM[r.ch])chM[r.ch]={le:0,cv:0,s:0};chM[r.ch].le+=r.leads;chM[r.ch].cv+=r.conv;chM[r.ch].s+=r.spend});
const leadWaste=Object.entries(chM).filter(([,m])=>m.le>0&&m.cv/m.le<.05).map(([ch,m])=>({ch,wasted:m.le-m.cv,cost:Math.round((m.le-m.cv)*15)}));
const rtCamps=fd.filter(r=>r.camp.toLowerCase().includes("retarget"));
const rtSpend=rtCamps.reduce((a,r)=>a+r.spend,0),rtRev=rtCamps.reduce((a,r)=>a+r.rev,0);
const rtWaste=rtSpend>rtRev?Math.round((rtSpend-rtRev)*.4):0;
return<><div style={{borderTop:"1px solid #3D3D4E",marginTop:8,paddingTop:8}}>
{leadWaste.map((lw,i)=><div key={i} style={{display:"flex",justifyContent:"space-between",padding:"4px 0",fontSize:10,borderBottom:"1px solid #25252F"}}><div><span style={{fontWeight:600}}>Low-Quality Lead Handling</span><div style={{color:"#6B7280",fontSize:9}}>{FN(lw.ch)} · {lw.wasted.toLocaleString()} wasted leads × $15</div></div><div style={{color:"#ef4444",fontWeight:700}}>{F(lw.cost)}</div></div>)}
{rtWaste>0&&<div style={{display:"flex",justifyContent:"space-between",padding:"4px 0",fontSize:10}}><div><span style={{fontWeight:600}}>Retargeting Waste</span><div style={{color:"#6B7280",fontSize:9}}>Spend {F(rtSpend)} > Revenue {F(rtRev)}</div></div><div style={{color:"#ef4444",fontWeight:700}}>{F(rtWaste)}</div></div>}
</div></>})()}
</C>
</div>

{/* Retention Risk Signals */}
<C style={{marginBottom:12}}><div style={{fontSize:10,fontWeight:700,color:"#d97706",marginBottom:8}}>RETENTION RISK SIGNALS</div>
<div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8}}>
{Object.keys(CH).slice(0,8).map(ch=>{const cr=fd.filter(r=>r.ch===ch);if(!cr.length)return null;const avgNps=cr.reduce((a,r)=>a+r.nps,0)/cr.length;const avgBr=cr.reduce((a,r)=>a+r.br,0)/cr.length;
const risks=[];if(avgNps<25)risks.push(`NPS ${avgNps.toFixed(0)}`);if(avgBr>.6)risks.push(`Bounce ${(avgBr*100).toFixed(0)}%`);
return risks.length>0?<div key={ch} style={{padding:8,background:"#1A1A24",borderRadius:4,border:"1px solid #2E2E3E"}}>
<div style={{fontSize:9,fontWeight:700,color:CH[ch]?.color,marginBottom:4}}>{FN(ch)}</div>
{risks.map((r,i)=><div key={i} style={{fontSize:8,color:"#d97706"}}><AlertTriangle size={8}/> {r}</div>)}
</div>:null}).filter(Boolean)}
</div></C>

{/* Campaign Mix Leakage */}
<C style={{marginBottom:12}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>CAMPAIGN MIX LEAKAGE (within-channel)</div>
<table><thead><tr><th>Channel</th><th>Campaign</th><th>Status</th><th style={{textAlign:"right"}}>ROI</th><th style={{textAlign:"right"}}>Channel Median</th></tr></thead>
<tbody>{(()=>{const items=[];Object.keys(CH).forEach(ch=>{const camps={};fd.filter(r=>r.ch===ch).forEach(r=>{if(!camps[r.camp])camps[r.camp]={s:0,rv:0};camps[r.camp].s+=r.spend;camps[r.camp].rv+=r.rev});
const rois=Object.values(camps).map(c=>(c.rv-c.s)/c.s);const med=rois.sort((a,b)=>a-b)[Math.floor(rois.length/2)]||0;
Object.entries(camps).forEach(([camp,m])=>{const roi=(m.rv-m.s)/m.s;if(roi>med*1.5)items.push({ch,camp,status:"underfunded",roi,med});else if(roi<med*.5&&m.s>Object.values(camps).reduce((a,c)=>a+c.s,0)/Object.keys(camps).length)items.push({ch,camp,status:"overfunded",roi,med})})});
return items.slice(0,8).map((it,i)=><tr key={i}><td style={{color:CH[it.ch]?.color}}>{FN(it.ch)}</td><td>{it.camp}</td><td><B c={it.status==="underfunded"?"#10b981":"#ef4444"}>{it.status}</B></td><td style={{textAlign:"right"}}>{FX(it.roi)}</td><td style={{textAlign:"right",color:"#6B7280"}}>{FX(it.med)}</td></tr>)})()}</tbody></table></C>

<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>CONVERSION SUPPRESSION</div>
<table><thead><tr><th>Channel</th><th>Campaign</th><th style={{textAlign:"right"}}>CVR</th><th style={{textAlign:"right"}}>Expected</th><th style={{textAlign:"right"}}>Gap</th><th style={{textAlign:"right"}}>Suppressed</th><th style={{textAlign:"right"}}>Bounce</th><th style={{textAlign:"right"}}>Form</th></tr></thead>
<tbody>{D.pl.exp.items.slice(0,8).map((it,i)=><tr key={i}><td style={{color:CH[it.ch]?.color}}>{FN(it.ch)}</td><td>{it.camp}</td><td style={{textAlign:"right"}}>{(it.cvr*100).toFixed(2)}%</td><td style={{textAlign:"right"}}>{((it.cvr+it.gap)*100).toFixed(2)}%</td><td style={{textAlign:"right",color:"#ef4444"}}>{(it.gap*100).toFixed(2)}%</td><td style={{textAlign:"right",color:"#ef4444",fontWeight:700}}>{F(it.sR)}</td><td style={{textAlign:"right"}}>{(it.br*100).toFixed(0)}%</td><td style={{textAlign:"right"}}>{(it.fc*100).toFixed(0)}%</td></tr>)}</tbody></table></C>

{/* Cross-Channel Leakage (Phase 2) */}
{xChl&&<C style={{marginTop:12}}><div style={{fontSize:10,fontWeight:700,color:"#FFE600",marginBottom:8}}>CROSS-CHANNEL LEAKAGE <B c="#FFE600">Phase 2</B> — {F(xChl.total)}</div>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:10}}>
<div><div style={{fontSize:9,fontWeight:700,color:"#d97706",marginBottom:4}}>Timing: {F(xChl.timingLeak)}</div>
{xChl.timing.slice(0,6).map((t,i)=><div key={i} style={{display:"flex",justifyContent:"space-between",padding:"2px 0",fontSize:8,borderBottom:"1px solid #25252F"}}><span style={{color:"#6B7280"}}>{MO[i]}</span><B c={t.status==="overspend"?"#ef4444":t.status==="underspend"?"#10b981":"#6B7280"}>{t.status}</B></div>)}</div>
<div><div style={{fontSize:9,fontWeight:700,color:"#7c3aed",marginBottom:4}}>Online↔Offline</div>
<div style={{fontSize:9,lineHeight:2}}>{[["On Rev",F(xChl.onlineOffline.onRev)],["Off Rev",F(xChl.onlineOffline.offRev)],["On ROI",FX(xChl.onlineOffline.onROI)],["Off ROI",FX(xChl.onlineOffline.offROI)]].map(([l,v])=><div key={l} style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#6B7280"}}>{l}</span><span style={{fontWeight:600}}>{v}</span></div>)}</div></div>
<div><div style={{fontSize:9,fontWeight:700,color:"#10b981",marginBottom:4}}>Audience: {F(xChl.audienceLeak)}</div>
{xChl.regions.map((r,i)=><div key={i} style={{display:"flex",justifyContent:"space-between",padding:"2px 0",fontSize:8,borderBottom:"1px solid #25252F"}}><span>{r.reg}</span><B c={r.status==="underfunded"?"#10b981":r.status==="overfunded"?"#ef4444":"#6B7280"}>{r.status}</B></div>)}</div>
</div></C>}

<NB l="View Recommendations" onClick={()=>setTab("recommendations")}/>
</>}

{/* ═══ RECOMMENDATIONS ═══ */}
{activeTab==="recommendations"&&<>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
<div><h2 style={{fontSize:20,fontWeight:800}}>Recommendations</h2><p style={{color:"#6B7280",fontSize:10}}>{recs.length} actions · {recs.filter(r=>r.status==="approved").length} approved · Impact: {F(recs.filter(r=>r.status==="approved").reduce((a,r)=>a+Math.abs(r.impact||0),0))}</p></div>
<div style={{display:"flex",gap:6}}>
{recs.some(r=>r.status==="approved")&&<Btn onClick={createScnFromRecs}><GitBranch size={11}/>Create Scenario from Approved</Btn>}
</div></div>
<div style={{display:"flex",gap:3,marginBottom:10}}>{["ALL","SCALE","REDUCE","FIX","RETARGET","MAINTAIN","RESEQUENCE"].map(f=><Btn key={f} primary={recFilter===f} onClick={()=>setRecFilter(f)} style={{fontSize:8,padding:"3px 8px"}}>{f}</Btn>)}</div>
{recs.filter(r=>recFilter==="ALL"||r.type===recFilter).map((rec,i)=><C key={i} style={{marginBottom:8,borderLeft:`3px solid ${rec.type==="SCALE"?"#10b981":rec.type==="REDUCE"?"#ef4444":rec.type==="FIX"?"#d97706":rec.type==="MAINTAIN"?"#3b82f6":"#7c3aed"}`,padding:"10px 14px",opacity:rec.status==="rejected"?.4:1}}>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
<div style={{flex:1}}>
<div style={{display:"flex",gap:4,alignItems:"center",marginBottom:4}}>
<B c={rec.type==="SCALE"?"#10b981":rec.type==="REDUCE"?"#ef4444":rec.type==="FIX"?"#d97706":"#3b82f6"}>{rec.type}</B>
<span style={{fontWeight:700,fontSize:11}}>{FN(rec.ch)}</span>
{rec.camp&&<span style={{fontSize:9,color:"#6B7280"}}>{rec.camp}</span>}
<B c={rec.conf==="High"?"#10b981":"#d97706"}>{rec.conf}</B>
{rec.status!=="pending"&&<B c={rec.status==="approved"?"#10b981":"#ef4444"}>{rec.status}</B>}
</div>
<div style={{fontSize:10,color:"#9CA3AF",lineHeight:1.5}}>{rec.rationale}</div>
<div style={{fontSize:10,marginTop:4}}><strong style={{color:"#FFE600"}}>Action:</strong> {rec.action}</div>
</div>
<div style={{display:"flex",flexDirection:"column",alignItems:"flex-end",gap:4,minWidth:100}}>
{rec.impact!==0&&<div style={{fontSize:15,fontWeight:800,color:rec.impact>0?"#10b981":"#ef4444"}}>{rec.impact>0?"+":""}{F(rec.impact)}</div>}
<div style={{display:"flex",gap:3}}>
<button onClick={()=>{const n=[...recs];n[i].status="approved";setRecs(n)}} style={{width:24,height:24,borderRadius:4,border:"1px solid #10b981",background:rec.status==="approved"?"#10b981":"transparent",color:rec.status==="approved"?"#1A1A24":"#10b981",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center"}}><Check size={12}/></button>
<button onClick={()=>{const n=[...recs];n[i].status="rejected";setRecs(n)}} style={{width:24,height:24,borderRadius:4,border:"1px solid #ef4444",background:rec.status==="rejected"?"#ef4444":"transparent",color:rec.status==="rejected"?"#1A1A24":"#ef4444",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center"}}><X size={12}/></button>
</div>
<div style={{fontSize:9,color:"#6B7280"}}>Effort: {rec.effort}</div>
</div>
</div></C>)}
<NB l="Build Scenarios" onClick={()=>setTab("scenarios")}/>
</>}

{/* ═══ SCENARIOS ═══ */}
{activeTab==="scenarios"&&<>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
<h2 style={{fontSize:20,fontWeight:800}}>Scenario Planner</h2>
<Btn onClick={()=>{const o=optim(D.curves,D.tS);setScn(s=>[...s,{id:`c_${Date.now()}`,name:`Custom ${scn.length-2}`,budget:D.tS,obj:"balanced",opt:o,locked:false}])}}><Plus size={11}/>New Scenario</Btn>
</div>
<div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(240px,1fr))",gap:10,marginBottom:12}}>
{scn.map(sc=><C key={sc.id} style={{border:aScn===sc.id?"2px solid #FFE600":"1px solid #2E2E3E",cursor:"pointer"}} onClick={()=>setAScn(sc.id)}>
<div style={{display:"flex",justifyContent:"space-between",marginBottom:8}}><span style={{fontWeight:700,fontSize:12}}>{sc.name}</span>{sc.locked?<Lock size={11} color="#6B7280"/>:<button onClick={e=>{e.stopPropagation();setScn(s=>s.filter(x=>x.id!==sc.id))}} style={{background:"none",border:"none",cursor:"pointer",color:"#ef4444"}}><Trash2 size={11}/></button>}</div>
<div style={{fontSize:10,color:"#6B7280",lineHeight:2.2}}>
<div style={{display:"flex",justifyContent:"space-between"}}>Budget<span style={{color:"#E5E7EB",fontWeight:600}}>{F(sc.budget)}</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}>Revenue<span style={{color:"#10b981",fontWeight:600}}>{F(sc.opt.summary.oRev)}</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}>ROI<span style={{color:"#FFE600",fontWeight:600}}>{FX(sc.opt.summary.oROI)}</span></div>
<div style={{display:"flex",justifyContent:"space-between"}}>Uplift<span style={{color:sc.opt.summary.uplift>0?"#10b981":"#ef4444",fontWeight:600}}>{FP(sc.opt.summary.uplift)}</span></div>
</div>{aScn===sc.id&&<div style={{marginTop:6,fontSize:9,color:"#FFE600",fontWeight:700,borderTop:"1px solid #2E2E3E",paddingTop:4}}>● ACTIVE</div>}
</C>)}
</div>
{scn.length>1&&<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:8}}>SCENARIO COMPARISON</div>
<table><thead><tr><th>Scenario</th><th style={{textAlign:"right"}}>Budget</th><th style={{textAlign:"right"}}>Revenue</th><th style={{textAlign:"right"}}>ROI</th><th style={{textAlign:"right"}}>Uplift</th></tr></thead>
<tbody>{scn.map(sc=><tr key={sc.id} style={{background:aScn===sc.id?"#FFE60008":""}}>
<td style={{fontWeight:aScn===sc.id?700:400}}>{sc.name}</td><td style={{textAlign:"right"}}>{F(sc.budget)}</td><td style={{textAlign:"right"}}>{F(sc.opt.summary.oRev)}</td><td style={{textAlign:"right",color:"#FFE600"}}>{FX(sc.opt.summary.oROI)}</td><td style={{textAlign:"right",color:sc.opt.summary.uplift>0?"#10b981":"#ef4444",fontWeight:600}}>{FP(sc.opt.summary.uplift)}</td>
</tr>)}</tbody></table></C>}
<NB l="Run Optimization" onClick={()=>setTab("optimizer")}/>
</>}

{/* ═══ OPTIMIZER ═══ */}
{activeTab==="optimizer"&&<>
<h2 style={{fontSize:20,fontWeight:800,marginBottom:12}}>Budget Optimization</h2>
<div style={{display:"grid",gridTemplateColumns:"220px 1fr",gap:12}}>
<div>
<C style={{marginBottom:10}}>
<div style={{fontSize:10,fontWeight:700,color:"#FFE600",marginBottom:8}}>PARAMETERS</div>
<div style={{marginBottom:10}}><label style={{fontSize:9,color:"#6B7280",fontWeight:600}}>BUDGET</label><input type="range" min={.5} max={2} step={.05} value={bM} onChange={e=>setBM(parseFloat(e.target.value))}/><div style={{fontSize:13,fontWeight:800,textAlign:"center",color:"#FFE600"}}>{F(D.tS*bM)}</div><div style={{fontSize:9,textAlign:"center",color:"#6B7280"}}>{FP((bM-1)*100)}</div></div>
<div style={{marginBottom:10}}><label style={{fontSize:9,color:"#6B7280",fontWeight:600}}>OBJECTIVE</label>{[["balanced","Balanced"],["maximize_revenue","Max Revenue"],["maximize_roi","Max ROI"],["minimize_cac","Min CAC"]].map(([k,l])=><label key={k} style={{display:"flex",alignItems:"center",gap:4,fontSize:10,marginBottom:4,cursor:"pointer",color:obj===k?"#FFE600":"#9CA3AF"}}><input type="radio" checked={obj===k} onChange={()=>setObj(k)} style={{accentColor:"#FFE600"}}/>{l}</label>)}</div>
{obj==="balanced"&&<div style={{marginBottom:10}}><label style={{fontSize:9,color:"#6B7280",fontWeight:600}}>WEIGHTS</label>
{Object.entries(objWeights).map(([k,v])=><div key={k} style={{display:"flex",alignItems:"center",gap:4,fontSize:9,marginBottom:2}}><span style={{color:"#9CA3AF",width:50}}>{k}</span><input type="range" min={0} max={100} value={v} onChange={e=>{const nv=parseInt(e.target.value);setObjWeights(p=>({...p,[k]:nv}))}} style={{width:60,height:12}}/><span style={{color:"#FFE600",width:25}}>{v}%</span></div>)}
</div>}
<div style={{marginBottom:10}}><label style={{fontSize:9,color:"#6B7280",fontWeight:600}}>CONSTRAINTS</label>
{Object.keys(CH).map(ch=><div key={ch} style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"2px 0",fontSize:9}}>
<span style={{color:"#9CA3AF"}}>{CH[ch].label.slice(0,10)}</span>
<button onClick={()=>setCons(c=>({...c,[ch]:{...c[ch],locked:!c[ch]?.locked,lockedAmount:D.opt.channels.find(x=>x.channel===ch)?.cS}}))} style={{background:"none",border:"none",cursor:"pointer",color:cons[ch]?.locked?"#FFE600":"#6B7280"}}>{cons[ch]?.locked?<Lock size={10}/>:<Unlock size={10}/>}</button>
</div>)}</div>
<Btn primary onClick={reOpt} style={{width:"100%",justifyContent:"center"}}><Play size={12}/>Run</Btn>
</C>
<C><div style={{fontSize:9,color:"#6B7280",fontWeight:600,marginBottom:6}}>SENSITIVITY</div>
{[-20,-10,0,10,20,50].map(v=>{const b=D.tS*(1+v/100);const o=optim(D.curves,b);return<div key={v} style={{display:"flex",justifyContent:"space-between",fontSize:9,padding:"2px 0",color:v===0?"#FFE600":"#9CA3AF"}}><span>{v>=0?"+":""}{v}%</span><span>{F(o.summary.oRev)}</span><span>{FX(o.summary.oROI)}</span></div>})}</C>
</div>
<div>
<div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:10}}>
<K l="Current Rev" v={F(D.opt.summary.cRev)} a="#6B7280"/><K l="Optimized Rev" v={F(D.opt.summary.oRev)} a="#10b981"/><K l="Uplift" v={FP(D.opt.summary.uplift)} a={D.opt.summary.uplift>0?"#10b981":"#ef4444"}/><K l="Opt ROI" v={FX(D.opt.summary.oROI)} a="#FFE600"/>
</div>
<C style={{marginBottom:10,overflowX:"auto"}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>ALLOCATION</div>
<table><thead><tr><th>Channel</th><th style={{textAlign:"right"}}>Current</th><th style={{textAlign:"right"}}>Optimized</th><th style={{textAlign:"right"}}>Δ</th><th style={{textAlign:"right"}}>Proj Rev</th><th style={{textAlign:"right"}}>ROI</th><th style={{textAlign:"right"}}>Marginal</th><th></th></tr></thead>
<tbody>{D.opt.channels.sort((a,b)=>b.chg-a.chg).map(c=><tr key={c.channel} style={{opacity:c.locked?.5:1}}>
<td><span style={{color:CH[c.channel]?.color}}>{FN(c.channel)}</span></td>
<td style={{textAlign:"right"}}>{F(c.cS)}</td><td style={{textAlign:"right"}}>{F(c.oS)}</td>
<td style={{textAlign:"right",color:c.chg>0?"#10b981":"#ef4444",fontWeight:700}}>{FP(c.chg)}</td>
<td style={{textAlign:"right"}}>{F(c.oR)}</td><td style={{textAlign:"right"}}>{FX(c.oROI)}</td>
<td style={{textAlign:"right",color:"#FFE600"}}>{FX(c.mROI)}</td>
<td>{c.locked&&<Lock size={9} color="#FFE600"/>}</td>
</tr>)}</tbody></table></C>
<C style={{marginBottom:10}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>CURRENT VS OPTIMIZED</div>
<ResponsiveContainer width="100%" height={190}><BarChart data={D.opt.channels.map(c=>({ch:CH[c.channel]?.label?.slice(0,8),cur:c.cS,opt:c.oS}))}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="ch" tick={{fill:"#6B7280",fontSize:8}}/><YAxis tick={{fill:"#6B7280",fontSize:9}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Legend wrapperStyle={{fontSize:9}}/><Bar dataKey="cur" fill="#3D3D4E" name="Current" radius={[3,3,0,0]}/><Bar dataKey="opt" fill="#FFE600" name="Optimized" radius={[3,3,0,0]}/></BarChart></ResponsiveContainer></C>
{/* Marginal ROI table */}
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>MARGINAL ROI AT SPEND LEVELS</div>
<div style={{overflowX:"auto"}}><table><thead><tr><th>Channel</th>{[50,75,100,125,150,200].map(m=><th key={m} style={{textAlign:"right"}}>{m}%</th>)}</tr></thead>
<tbody>{Object.keys(D.curves).map(ch=><tr key={ch}><td style={{color:CH[ch]?.color}}>{CH[ch]?.label?.slice(0,10)}</td>
{[.5,.75,1,1.25,1.5,2].map(m=>{const row=margTable.find(r=>r.ch===ch&&r.mult===`${(m*100).toFixed(0)}%`);return<td key={m} style={{textAlign:"right",color:row?.mROI>2?"#10b981":row?.mROI>1?"#FFE600":"#ef4444",fontSize:9}}>{row?FX(row.mROI):"—"}</td>})}
</tr>)}</tbody></table></div></C>
</div></div>
<NB l="Build Business Case" onClick={()=>setTab("business")}/>
</>}

{/* ═══ BUSINESS CASE ═══ */}
{activeTab==="business"&&<>
<h2 style={{fontSize:20,fontWeight:800,marginBottom:12}}>Business Case & Value Realization</h2>
<div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:12}}>
<K l="Rev Uplift" v={F(D.opt.summary.oRev-D.opt.summary.cRev)} a="#10b981" sub={{t:FP(D.opt.summary.uplift),c:D.opt.summary.uplift>0?"#10b981":"#ef4444"}}/><K l="Value at Risk" v={F(D.pl.totalRisk)} a="#ef4444"/><K l="ROI Change" v={`${FX(D.opt.summary.cROI)}→${FX(D.opt.summary.oROI)}`} a="#FFE600"/><K l="Recoverable" v={F(D.pl.leak.total*.6+D.pl.exp.total*.4+D.pl.cost.total*.7)} a="#10b981"/>
</div>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:12}}>
<C><div style={{fontSize:12,fontWeight:700,color:"#FFE600",marginBottom:10}}>IMPLEMENTATION ROADMAP</div>
{[{p:"Immediate (0-30d)",items:recs.filter(r=>r.effort==="Low"&&r.status!=="rejected").slice(0,3),c:"#10b981"},{p:"Short-term (30-90d)",items:recs.filter(r=>r.effort==="Medium"&&r.status!=="rejected").slice(0,3),c:"#d97706"},{p:"Strategic (90d+)",items:recs.filter(r=>(r.effort==="High"||r.effort==="None")&&r.status!=="rejected").slice(0,2),c:"#7c3aed"}].map(ph=><div key={ph.p} style={{marginBottom:12}}>
<div style={{fontSize:10,fontWeight:700,color:ph.c,marginBottom:4}}>{ph.p}</div>
{ph.items.map((r,i)=><div key={i} style={{padding:"3px 0",borderBottom:"1px solid #25252F",fontSize:10,color:"#9CA3AF",display:"flex",gap:4,alignItems:"center"}}><B c={r.type==="SCALE"?"#10b981":r.type==="REDUCE"?"#ef4444":"#d97706"}>{r.type}</B>{FN(r.ch)} — {r.action}{r.impact>0&&<span style={{marginLeft:"auto",color:"#10b981",fontWeight:700,fontSize:9}}>+{F(r.impact)}</span>}</div>)}
</div>)}</C>
<div>
<C style={{marginBottom:10}}><div style={{fontSize:12,fontWeight:700,color:"#FFE600",marginBottom:10}}>CORRECTION POTENTIAL</div>
{[{l:"Reallocation uplift",v:D.pl.leak.total*.6,c:"#10b981"},{l:"CX fix recovery",v:D.pl.exp.total*.4,c:"#d97706"},{l:"Cost savings",v:D.pl.cost.total*.7,c:"#7c3aed"}].map(it=><div key={it.l} style={{marginBottom:10}}><div style={{display:"flex",justifyContent:"space-between",fontSize:10,marginBottom:3}}><span style={{color:"#9CA3AF"}}>{it.l}</span><span style={{fontWeight:700,color:it.c}}>{F(it.v)}</span></div><div style={{height:4,background:"#2E2E3E",borderRadius:2}}><div style={{height:"100%",background:it.c,borderRadius:2,width:`${Math.min(100,it.v/Math.max(D.pl.totalRisk,1)*150)}%`}}/></div></div>)}
<div style={{borderTop:"1px solid #3D3D4E",paddingTop:8,display:"flex",justifyContent:"space-between",fontSize:13,fontWeight:800}}>Total<span style={{color:"#FFE600"}}>{F(D.pl.leak.total*.6+D.pl.exp.total*.4+D.pl.cost.total*.7)}</span></div>
</C>
{/* Next-Year Forecast (Phase 2) */}
{fc&&<C style={{marginBottom:10}}><div style={{fontSize:10,fontWeight:700,color:"#FFE600",marginBottom:6}}>NEXT-YEAR REVENUE FORECAST <B c="#FFE600">Phase 2</B></div>
<ResponsiveContainer width="100%" height={160}><ComposedChart data={[...fc.historical.map(h=>({month:h.month,actual:h.actual})),...fc.forecast.map(f=>({month:f.month,predicted:f.predicted,lower:f.lower,upper:f.upper}))]}>
<CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="month" tick={{fill:"#6B7280",fontSize:8}}/><YAxis tick={{fill:"#6B7280",fontSize:8}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/>
<Line dataKey="actual" stroke="#E5E7EB" strokeWidth={2} dot={{r:2}} name="Historical"/><Line dataKey="predicted" stroke="#FFE600" strokeWidth={2} dot={false} name="Forecast"/><Area dataKey="upper" fill="#FFE60008" stroke="none"/><Area dataKey="lower" fill="#1A1A24" stroke="none"/>
</ComposedChart></ResponsiveContainer>
<div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginTop:8,fontSize:10}}>
<div style={{textAlign:"center"}}><div style={{color:"#6B7280"}}>Historical</div><div style={{fontWeight:700}}>{F(fc.summary.historicalTotal)}</div></div>
<div style={{textAlign:"center"}}><div style={{color:"#6B7280"}}>Forecast</div><div style={{fontWeight:700,color:"#FFE600"}}>{F(fc.summary.forecastTotal)}</div></div>
<div style={{textAlign:"center"}}><div style={{color:"#6B7280"}}>YoY Change</div><div style={{fontWeight:700,color:fc.summary.yoyPct>0?"#10b981":"#ef4444"}}>{FP(fc.summary.yoyPct)}</div></div>
</div></C>}
{/* Payback Period */}
{roiData&&<C style={{marginBottom:10}}><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>PAYBACK PERIODS BY CHANNEL</div>
<table><thead><tr><th>Channel</th><th>Conf</th><th style={{textAlign:"right"}}>Payback</th><th style={{textAlign:"right"}}>Base ROI</th><th style={{textAlign:"right"}}>Marginal ROI</th></tr></thead>
<tbody>{roiData.map(r=><tr key={r.ch}><td style={{color:CH[r.ch]?.color}}>{FN(r.ch)}</td><td><B c={CH[r.ch]?.type==="online"?"#10b981":"#d97706"}>{CH[r.ch]?.type==="online"?"High":"Est."}</B></td><td style={{textAlign:"right",color:r.payback<=3?"#10b981":"#d97706",fontWeight:600}}>{r.payback} mo</td><td style={{textAlign:"right"}}>{FX(r.baseROI)}</td><td style={{textAlign:"right",color:"#FFE600"}}>{FX(r.margROI)}</td></tr>)}</tbody></table>
</C>}
<C><div style={{fontSize:10,fontWeight:700,color:"#6B7280",marginBottom:6}}>REALIZATION TRACKER</div>
<ResponsiveContainer width="100%" height={120}><ComposedChart data={realData}><CartesianGrid strokeDasharray="3 3" stroke="#2E2E3E"/><XAxis dataKey="month" tick={{fill:"#6B7280",fontSize:8}}/><YAxis tick={{fill:"#6B7280",fontSize:8}} tickFormatter={v=>F(v)}/><Tooltip contentStyle={tt} formatter={v=>F(v)}/><Line dataKey="planned" stroke="#FFE600" strokeWidth={2} dot={false} name="Planned"/><Line dataKey="actual" stroke="#10b981" strokeWidth={2} dot={{r:2}} name="Actual" connectNulls={false}/></ComposedChart></ResponsiveContainer>
<div style={{fontSize:8,color:"#6B7280",marginTop:4}}>Tracking optimized plan vs actual results (updates monthly)</div>
</C></div></div>

{/* Export bar */}
<C style={{background:"#FFE60006",border:"1px solid #FFE60020"}}>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
<div><div style={{fontSize:13,fontWeight:800,color:"#FFE600"}}>Export & Download</div><div style={{fontSize:10,color:"#9CA3AF",marginTop:3}}>Generate allocation plan, recommendation document, executive summary</div></div>
<div style={{display:"flex",gap:6}}>
<Btn onClick={exportCSV}><Download size={11}/>CSV Plan</Btn>
<Btn primary><FileText size={11}/>Executive PDF</Btn>
</div></div></C>

<div style={{marginTop:12,padding:12,background:"#1F1F2B",borderRadius:6,border:"1px solid #2E2E3E"}}>
<div style={{fontSize:10,fontWeight:700,color:"#FFE600",marginBottom:4}}>CONFIDENCE & METHODOLOGY</div>
<div style={{fontSize:9,color:"#6B7280",lineHeight:1.7}}>
Projections use power-law response curves (y=a·x^b) fitted to 12 months of data via log-linear regression. Attribution models: Last-touch (100% final touchpoint), Linear (equal credit), Position-based (40/20/40). Offline channels carry model-estimated confidence tiers. Revenue leakage is the gap between actual and optimizer-recommended allocation applied to the same response model. Conversion suppression uses CVR gap × traffic × AOV. All estimates are directional — validate with 60-90 day holdout tests before scaling. Marginal ROI is the derivative of the response curve at current spend.
</div></div>
</>}

</div>}

<div style={{borderTop:"1px solid #2E2E3E",padding:"10px 20px",textAlign:"center",fontSize:9,color:"#4B5563",marginTop:30}}>Yield Intelligence Platform · Marketing ROI & Budget Optimization Engine · Confidential</div>
</div>)}
