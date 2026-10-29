import importlib
from qlib import ORDER
mods = ['s_lti_def','s_rc_lpf','s_cx_exp','s_sinusoid_resp','s_impulse_conv','s_step_resp','s_freq_char','s_tf','s_phasors','s_direct_h','s_pole_zero','s_rlc','s_bode','s_ac_power']
for m in mods:
    sk = importlib.import_module(m).build()
    sk.save()
    print("wrote", sk.sid, len(sk.qs))
