import sys; sys.path.insert(0,'.')
import batch2a_figmap as FM
import batch2a_s_ch3a as a, batch2a_s_ch3b as b, batch2a_s_ch5 as c, batch2a_s_ch6 as d, batch2a_s_ch7 as e
fns=[a.si_props,a.drude,a.intrinsic,a.doping,b.drift,b.diffusion,b.total_current,b.carrier_pot,
     c.pn_overview,c.depl_approx,c.contact_pot,c.rev_bias,d.excess_carriers,d.continuity,d.minority_profile,
     e.mos_struct,e.mos_regions,e.vt,e.mos_fields,e.mos_cv]
tot=mc=fig=0; ci=[0]*4
for f in fns:
    s=f(); FM.attach(s.qs); s.save()
    for q in s.qs:
        tot+=1; fig+='figure' in q
        if q['type']=='mc': mc+=1; ci[q['correct_index']]+=1
print(len(fns),tot,'mc',mc,'fig',fig,'ci',ci)
