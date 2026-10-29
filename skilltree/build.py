import json
C = {1:"Linear Time-Invariant Systems",2:"AC Circuits and AC Analysis",3:"Introduction to Semiconductors",4:"IC Resistors, Capacitors, Electrostatics",5:"PN Junctions in Equilibrium",6:"PN Junction Currents",7:"MOS Capacitor",8:"MOSFET Device Physics",9:"MOS Small-Signal Models",10:"MOSFET Capacitance and Body Effect",11:"Bipolar Junction Transistors",12:"Single-Stage Amplifiers",13:"Current Mirrors and Biasing",14:"Frequency Response of Amplifiers",15:"Multi-Stage Amplifiers",16:"Differential Amplifiers",17:"Feedback and Op-Amps",18:"Op-Amp Non-Idealities"}
S = """
1|lti-def|Linear time-invariant systems and superposition|1.3|
1|rc-lpf|Solve a first-order RC low-pass filter in the time domain|1.2|
1|cx-exp|Complex exponentials and Euler's relations|1.4|
1|sinusoid-resp|Sinusoidal steady state using complex exponentials|1.5|cx-exp,lti-def,rc-lpf
1|impulse-conv|Impulse response and convolution|1.8|lti-def
1|step-resp|Step and pulse response|1.9|impulse-conv,rc-lpf
1|freq-char|Frequency-domain view of linear systems|1.10|sinusoid-resp,impulse-conv
2|tf|Transfer functions, voltage and current gain, transimpedance|2.2|sinusoid-resp
2|phasors|Phasors and impedance of R, L, C|2.4|sinusoid-resp
2|direct-h|Find H(jw) directly with impedances|2.4.4|phasors,tf
2|pole-zero|Poles and zeros of a transfer function|2.3|tf
2|rlc|Series RLC circuits|2.5.3|direct-h,pole-zero
2|bode|Bode plots: magnitude and phase|2.6|pole-zero
2|ac-power|AC power flow and RMS|2.7|phasors
3|drude|Conduction in metals, mobility, microscopic Ohm's law|3.2|
3|si-props|Silicon bond model, electrons and holes|3.3|drude
3|intrinsic|Intrinsic carrier concentration and the mass-action law|3.4|si-props
3|doping|Doping with donors and acceptors, carrier concentrations|3.5|intrinsic
3|drift|Drift current and mobility|3.6|drude,doping
3|diffusion|Diffusion current and the Einstein relation|3.7|doping
3|total-current|Total current and boundary conditions|3.7.4|drift,diffusion
4|ic-fab|IC fabrication basics: oxide, implantation|4.2|
4|sheet-res|Sheet resistance and IC resistors|4.3|drude,ic-fab
4|electrostatics|1D electrostatics, fields and potential|4.4|
4|mim-cap|Capacitor review and MIM capacitors|4.5|electrostatics
4|nl-cap|Non-linear capacitors and small-signal capacitance|4.5.3|mim-cap
5|carrier-pot|Carrier concentration versus potential (Boltzmann)|5.3|doping
5|pn-overview|PN junction in equilibrium: structure and currents|5.4|carrier-pot,total-current
5|depl-approx|Depletion approximation, fields and depletion width|5.4.5|pn-overview,electrostatics
5|contact-pot|Built-in contact potential|5.4.7|pn-overview
5|rev-bias|Reverse-biased junction: width and charge|5.5|depl-approx,contact-pot
5|junction-cap|Depletion capacitance and varactors|5.5.3|rev-bias,nl-cap
6|diode-qual|Qualitative diode I-V: equilibrium, forward, reverse|6.2|pn-overview
6|excess-carriers|Non-equilibrium carriers and recombination-generation|6.3|doping
6|continuity|Continuity equation for excess carriers|6.4|excess-carriers,total-current
6|minority-profile|Minority carrier distribution at junction edges|6.5|continuity,diode-qual
6|diode-iv|Ideal diode equation|6.5.3|minority-profile
6|diode-ss|Diode small-signal model and diffusion capacitance|6.6|diode-iv,junction-cap,nl-cap
6|solar-cell|Solar cells: short-circuit current and open-circuit voltage|6.7|diode-iv
6|led|Light-emitting diodes|6.7.6|diode-iv
7|mos-struct|MOS capacitor structure and gate contact potential|7.2|electrostatics,contact-pot
7|mos-regions|Accumulation, depletion and inversion|7.3|mos-struct,depl-approx
7|vt|Threshold voltage derivation|7.4|mos-regions
7|mos-fields|Fields and potential in oxide and substrate|7.5|mos-regions
7|mos-cv|MOS Q-V and C-V curves|7.6|mos-regions,vt
8|mosfet-struct|MOSFET layout, cross section, CMOS and symbols|8.2|mos-struct
8|nmos-regions|NMOS regions of operation and observed I-V|8.3|vt,mosfet-struct
8|triode|Triode region and the MOSFET as a variable resistor|8.4.1|nmos-regions
8|square-law|Square-law derivation|8.4.5|triode
8|saturation|Saturation and pinch-off|8.5|square-law
8|clm|Channel-length modulation|8.5.5|saturation
8|pmos|PMOS device and regions of operation|8.6|saturation
9|cs-intro|Common-source amplifier and its bias point|9.2|saturation,tf
9|op-point|Large-signal versus small-signal and bias selection|9.3|cs-intro
9|gm|MOS transconductance gm|9.4.2|op-point
9|ro|MOS output resistance ro|9.4.3|clm,gm
9|ss-model|MOS small-signal model|9.4.4|gm,ro
9|ss-steps|Small-signal analysis procedure|9.4.5|ss-model
9|pmos-ss|PMOS small-signal model and amplifier|9.5|ss-model,pmos
10|mos-caps|MOSFET capacitances CGS, CGD, CDB, CSB|10.2|ss-model,junction-cap
10|body-effect|Body effect on threshold voltage and signals|10.3|vt,ss-model
10|ss-4term|Four-terminal small-signal model|10.4|mos-caps,body-effect
11|bjt-struct|BJT structure, layout and symbol|11.2|pn-overview
11|bjt-iv|BJT observed I-V characteristics|11.3|bjt-struct,diode-iv
11|bjt-action|Transistor action and BJT currents|11.4|bjt-iv,minority-profile
11|bjt-gain|Collector current, base current and current gain|11.5|bjt-action
11|ebers-moll|Ebers-Moll model|11.6.1|bjt-gain
11|early|Forward-active region and the Early effect|11.6.3|ebers-moll
11|bjt-ss|BJT small-signal model|11.6.5|early,ss-steps
12|two-port|Two-port amplifier models, Zin and Zout|12.2|ss-steps
12|bias-coupling|Isolating bias points, DC versus AC coupling|12.3.1|op-point
12|cs-analysis|Common-source gain, input and output impedance|12.3|two-port,ss-steps
12|cg|Common-gate amplifier|12.3.3|two-port,ss-steps
12|cd|Common-drain (source follower) amplifier|12.4|two-port,ss-steps
12|body-amp|Impact of body effect on amplifiers|12.5|cd,body-effect
12|amp-choice|Choosing among CS, CG and CD|12.6|cs-analysis,cg,cd
13|high-load|High load impedance, headroom and gain|13.2|cs-analysis
13|diode-conn|Diode-connected transistor|13.3.1|ss-model,saturation
13|mirror|Basic current mirror|13.3.3|diode-conn
13|mirror-ratio|Mirror with multiplication ratio and multiple outputs|13.3.4|mirror
13|mirror-ro|Small-signal resistance of a current source|13.3.6|mirror,ro
13|degeneration|Source degeneration|13.4.2|ss-steps
13|cascode-src|Cascode current source and its drawback|13.4.3|degeneration,mirror-ro
13|cd-real|Source follower with a real current source|13.6|cd,mirror
13|ref-gen|Constant-gm current reference|13.7|mirror
14|freq-basics|Frequency response considerations and coupling capacitors|14.2|bode,cs-analysis
14|cs-brute|Common-source frequency response, brute force|14.5|freq-basics,mos-caps
14|miller|Miller theorem and Miller effect|14.6|cs-brute
14|cs-miller|Common-source bandwidth using Miller|14.7|miller
14|cd-freq|Source follower frequency response|14.8|miller,cd
14|cg-freq|Common-gate bandwidth|14.9|freq-basics,cg
14|ft|Unity-gain frequency fT|14.10|mos-caps,gm
14|octc|Open-circuit time constants|14.11|pole-zero,cs-miller
15|z-match|Input and output impedance in cascades|15.3|two-port
15|cs-cascade|Two-stage common-source cascade|15.4|z-match,cs-analysis
15|cs-cascade-freq|Cascade frequency response and bandwidth extension|15.4.3|cs-cascade,miller
15|cs-cap-load|Common-source with a large capacitive load|15.5|cs-miller
15|cascode-amp|Cascode amplifier: gain and bandwidth|15.6|cs-cascade,cg,miller
15|cascode-bias|Cascode biasing and complete design|15.6.6|cascode-amp
15|big-circuit|Simplifying a big circuit|15.7|cascode-amp,cs-cascade
16|diff-intro|Motivation and the source-coupled pair|16.2|degeneration
16|diff-dc|Differential pair DC bias and large-signal behavior|16.4|diff-intro
16|dm-cm|Differential-mode and common-mode decomposition|16.5|diff-intro,ss-steps
16|half-circuit|Differential half-circuit analysis|16.5.4|dm-cm
16|cm-gain|Common-mode gain with a real current source|16.5.6|dm-cm,mirror-ro
16|cmrr|CMRR and DC offsets|16.6|cm-gain
16|mirror-load|Differential pair with current mirror load|16.7|diff-intro,mirror,half-circuit
17|fb-intro|Feedback block diagram|17.2|tf
17|loop-gain|Loop gain and why feedback helps|17.3|fb-intro
17|opamp-models|Op-amp circuit models and OTA|17.4|ss-model,fb-intro
17|gbw|Gain-bandwidth trade-off|17.5|loop-gain,bode,opamp-models
17|inverting|Inverting amplifier with feedback|17.6|loop-gain,opamp-models
17|fb-errors|Static and dynamic errors in feedback systems|17.7|loop-gain
17|fb-impedance|Feedback effect on input and output impedance|17.8|fb-intro,two-port
17|stability|Stability, non-dominant poles and oscillation|17.9|gbw,pole-zero
18|offset|Op-amp offset voltage|18.2|opamp-models,cmrr
18|bias-current|Input bias and offset currents|18.2.3|offset
18|opamp-fr|Open-loop and closed-loop op-amp frequency response|18.3|gbw
18|slew|Output swing, slew rate and full-power bandwidth|18.4|opamp-fr
18|noise-dist|Op-amp noise and distortion|18.5|opamp-models
18|datasheet|Reading op-amp datasheets|18.6|offset,slew,noise-dist
"""
skills=[]
for l in S.strip().splitlines():
    ch,id,name,sec,pre=l.split("|")
    skills.append(dict(id=id,name=name,chapter=int(ch),reader_section=sec,prereqs=[p for p in pre.split(",") if p]))
ids={s["id"] for s in skills}
assert len(ids)==len(skills)
for s in skills:
    for p in s["prereqs"]: assert p in ids,(s["id"],p)
# cycle check
seen={}
def dfs(i,stack):
    if seen.get(i)==2: return
    assert seen.get(i)!=1,("cycle",i)
    seen[i]=1
    for p in next(s for s in skills if s["id"]==i)["prereqs"]: dfs(p,stack)
    seen[i]=2
for i in ids: dfs(i,[])
json.dump(dict(course="EE 105",source="Niknejad EE105 Reader (Oct 31, 2022)",version=1,chapters={str(k):v for k,v in C.items()},skills=skills),open("ee105_skills_draft.json","w"),indent=1)
print(len(skills))
from collections import Counter
print(Counter(s["chapter"] for s in skills))
