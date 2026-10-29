/* Skillgrove configuration — public values only, no secrets */
window.SKILLTREE_CONFIG = {
  supabase: {
    url: 'https://yjnwgfjbuwgkmxcreblw.supabase.co',
    anonKey: 'sb_publishable_yQrS56HMDZf7xzzjMKJE-w_l8OrLPeg'
  },
  auth: {
    googleEnabled: false,
    redirectUrl: typeof window !== 'undefined'
      ? window.location.origin + '/skilltree/'
      : 'https://elytraflight.com/skilltree/'
  }
};
