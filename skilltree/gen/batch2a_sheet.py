import sys, xml.etree.ElementTree as ET
sys.path.insert(0, '/workspace/skilltree/gen')
import batch2a_fig as F
figs = {'band_n': F.band_diagram('n'), 'lat_d': F.lattice('donor', broken=True), 'lat_a': F.lattice('acceptor'), 'bar': F.bar(), 'rg': F.rg_centers(),
 'pn': F.pn_profiles(NA=1, ND=4), 'pnb': F.pn_block(note='reverse bias'), 'mos_dep': F.mos_stack('depletion', vlabel='V_{GB}'), 'mos_inv': F.mos_stack('inversion'),
 'mos_acc': F.mos_stack('accumulation'), 'mosprof': F.mos_profiles(), 'cv': F.cv_curve(cmin_label='C_{min}'), 'dec': F.profile_decay(), 'decl': F.profile_decay(long=True),
 'res': F.resistor_circuit(), 'plot': F.plot([dict(fn=lambda x: x * x, label='y')], (0, 2), (0, 4), 'x', 'y')}
for k, v in figs.items(): ET.fromstring(v)
html = '<html><body style="background:#fff;color:#111">' + ''.join(f'<div style="display:inline-block;width:390px;margin:6px;border:1px solid #ccc"><small>{k}</small>{v}</div>' for k, v in figs.items()) + '</body></html>'
open('/tmp/figs.html', 'w').write(html)
