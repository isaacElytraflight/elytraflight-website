/* Skillgrove Auth & Sync — Supabase integration
   localStorage remains primary for offline use; Supabase syncs when signed in */
(function() {
'use strict';

const CONFIG = window.SKILLTREE_CONFIG;
const PROGRESS_KEY = 'skilltree.progress.v1';
const TIMING_KEY = 'skilltree.timing.v1';

let supabase = null;
let currentUser = null;
let syncStatus = 'signed_out';
let syncDebounceTimer = null;
const SYNC_DEBOUNCE_MS = 2000;

function getSupabase() {
  if (!supabase && window.supabase && CONFIG?.supabase) {
    supabase = window.supabase.createClient(CONFIG.supabase.url, CONFIG.supabase.anonKey);
  }
  return supabase;
}

function setSyncStatus(status) {
  syncStatus = status;
  const el = document.getElementById('syncStatus');
  if (!el) return;
  
  const statusText = {
    signed_out: '',
    synced: 'Synced',
    syncing: 'Syncing…',
    offline: 'Offline',
    error: 'Sync error'
  }[status] || '';
  
  el.textContent = statusText;
  el.className = 'sync-status ' + status;
}

function getAuthUI() {
  return document.getElementById('authUI');
}

function updateAuthUI() {
  const ui = getAuthUI();
  if (!ui) return;
  
  if (currentUser) {
    const email = currentUser.email || 'User';
    ui.innerHTML = `
      <span id="syncStatus" class="sync-status ${syncStatus}"></span>
      <span class="user-email" title="${email}">${email.length > 20 ? email.slice(0, 18) + '…' : email}</span>
      <button class="btn small" id="btnSignOut">Sign out</button>
    `;
    document.getElementById('btnSignOut').onclick = signOut;
    setSyncStatus(syncStatus === 'signed_out' ? 'synced' : syncStatus);
  } else {
    ui.innerHTML = `<button class="btn" id="btnSignIn">Sign in</button>`;
    document.getElementById('btnSignIn').onclick = openSignInModal;
    setSyncStatus('signed_out');
  }
}

function openSignInModal() {
  const body = document.createElement('div');
  body.className = 'auth-modal-body';
  
  const emailSection = document.createElement('div');
  emailSection.className = 'auth-section';
  emailSection.innerHTML = `
    <p>Sign in to sync your progress across devices. We'll send a magic link to your email.</p>
    <div class="auth-input-row">
      <input type="email" id="authEmail" placeholder="your@email.com" autocomplete="email" />
      <button class="btn primary" id="btnSendLink">Send magic link</button>
    </div>
    <p id="authMsg" class="auth-msg"></p>
  `;
  body.appendChild(emailSection);
  
  if (CONFIG?.auth?.googleEnabled) {
    const divider = document.createElement('div');
    divider.className = 'auth-divider';
    divider.innerHTML = '<span>or</span>';
    body.appendChild(divider);
    
    const googleSection = document.createElement('div');
    googleSection.className = 'auth-section';
    googleSection.innerHTML = `
      <button class="btn google-btn" id="btnGoogleSignIn">
        <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
          <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
          <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
          <path fill="#FBBC05" d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71s.102-1.17.282-1.71V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.332z"/>
          <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
        </svg>
        Continue with Google
      </button>
    `;
    body.appendChild(googleSection);
  }
  
  window.__skillgrove?.openModal?.({
    title: 'Sign in to sync',
    body,
    actions: [{ label: 'Cancel' }]
  });
  
  setTimeout(() => {
    const emailInput = document.getElementById('authEmail');
    const sendBtn = document.getElementById('btnSendLink');
    const googleBtn = document.getElementById('btnGoogleSignIn');
    const msgEl = document.getElementById('authMsg');
    
    if (emailInput && sendBtn) {
      sendBtn.onclick = async () => {
        const email = emailInput.value.trim();
        if (!email || !email.includes('@')) {
          msgEl.textContent = 'Please enter a valid email.';
          msgEl.className = 'auth-msg error';
          return;
        }
        sendBtn.disabled = true;
        sendBtn.textContent = 'Sending…';
        try {
          const { error } = await getSupabase().auth.signInWithOtp({
            email,
            options: { emailRedirectTo: CONFIG?.auth?.redirectUrl }
          });
          if (error) throw error;
          msgEl.textContent = 'Check your email for the magic link!';
          msgEl.className = 'auth-msg success';
          emailInput.disabled = true;
        } catch (e) {
          msgEl.textContent = e.message || 'Failed to send link. Try again.';
          msgEl.className = 'auth-msg error';
          sendBtn.disabled = false;
          sendBtn.textContent = 'Send magic link';
        }
      };
      emailInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') sendBtn.click();
      });
    }
    
    if (googleBtn) {
      googleBtn.onclick = async () => {
        try {
          const { error } = await getSupabase().auth.signInWithOAuth({
            provider: 'google',
            options: { redirectTo: CONFIG?.auth?.redirectUrl }
          });
          if (error) throw error;
        } catch (e) {
          if (msgEl) {
            msgEl.textContent = e.message || 'Failed to start Google sign in.';
            msgEl.className = 'auth-msg error';
          }
        }
      };
    }
  }, 50);
}

async function signOut() {
  try {
    await getSupabase().auth.signOut();
    currentUser = null;
    updateAuthUI();
    window.__skillgrove?.toast?.('Signed out');
  } catch (e) {
    console.error('Sign out error:', e);
  }
}

function mergeSkill(local, remote) {
  return window.SkillgroveMigrate.mergeSkillRecords(local, remote);
}

function retirementMap() {
  const fromApp = window.__skillgrove && window.__skillgrove.retired && window.__skillgrove.retired();
  return fromApp && typeof fromApp === 'object' ? fromApp : {};
}

/** Migrate retired ids on each side, then keep the higher tier and later practice time. */
function migrateSyncedProgress(localProgress, remoteProgress) {
  return window.SkillgroveMigrate.combineMigratedProgress(
    localProgress, remoteProgress, retirementMap(), mergeProgress
  );
}

function mergeProgress(local, remote) {
  if (!local || !local.skills) return remote;
  if (!remote || !remote.skills) return local;
  
  const merged = { version: 1, skills: {} };
  const allIds = new Set([...Object.keys(local.skills), ...Object.keys(remote.skills)]);
  
  for (const id of allIds) {
    const m = mergeSkill(local.skills[id], remote.skills[id]);
    if (m) merged.skills[id] = m;
  }
  
  return merged;
}

function mergeTiming(local, remote) {
  if (!local) return remote;
  if (!remote) return local;
  
  const merged = {};
  for (const key of ['practice', 'challenge']) {
    const lArr = Array.isArray(local[key]) ? local[key] : [];
    const rArr = Array.isArray(remote[key]) ? remote[key] : [];
    const seen = new Set(lArr.map(s => s.t));
    merged[key] = [...lArr, ...rArr.filter(s => !seen.has(s.t))].sort((a, b) => a.t - b.t).slice(-50);
  }
  return merged;
}

async function fetchRemote() {
  const sb = getSupabase();
  if (!sb || !currentUser) return null;
  
  try {
    const { data, error } = await sb
      .from('progress')
      .select('data')
      .eq('user_id', currentUser.id)
      .maybeSingle();
    
    if (error) throw error;
    return data?.data || null;
  } catch (e) {
    console.error('Fetch remote error:', e);
    return null;
  }
}

async function upsertRemote(data) {
  const sb = getSupabase();
  if (!sb || !currentUser) return false;
  
  try {
    setSyncStatus('syncing');
    const { error } = await sb
      .from('progress')
      .upsert({
        user_id: currentUser.id,
        data,
        updated_at: new Date().toISOString()
      }, { onConflict: 'user_id' });
    
    if (error) throw error;
    setSyncStatus('synced');
    return true;
  } catch (e) {
    console.error('Upsert error:', e);
    setSyncStatus(navigator.onLine ? 'error' : 'offline');
    return false;
  }
}

function getLocalData() {
  try {
    const progress = JSON.parse(localStorage.getItem(PROGRESS_KEY) || 'null');
    const timing = JSON.parse(localStorage.getItem(TIMING_KEY) || 'null');
    return { progress, timing };
  } catch (e) {
    return { progress: null, timing: null };
  }
}

function setLocalData(progress, timing) {
  try {
    if (progress) localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));
    if (timing) localStorage.setItem(TIMING_KEY, JSON.stringify(timing));
  } catch (e) {
    console.error('setLocalData error:', e);
  }
}

async function syncOnSignIn() {
  setSyncStatus('syncing');
  
  const local = getLocalData();
  const remote = await fetchRemote();
  
  const remoteProgress = remote && remote.progress;
  const remoteTiming = remote && remote.timing;
  const migrated = migrateSyncedProgress(local.progress, remoteProgress);
  const mergedTiming = mergeTiming(local.timing, remoteTiming);

  if (!remote) {
    if (migrated.changed) setLocalData(migrated.progress, null);
    if (migrated.progress || local.timing) {
      await upsertRemote({ progress: migrated.progress, timing: local.timing });
    }
    if (migrated.changed && window.__skillgrove) {
      window.__skillgrove.reloadProgress?.();
      window.__skillgrove.refreshAll?.();
    }
    setSyncStatus('synced');
    return;
  }

  setLocalData(migrated.progress, mergedTiming);
  await upsertRemote({ progress: migrated.progress, timing: mergedTiming });
  
  if (window.__skillgrove) {
    window.__skillgrove.reloadProgress?.();
    window.__skillgrove.reloadTiming?.();
    window.__skillgrove.refreshAll?.();
  }
  
  setSyncStatus('synced');
  window.__skillgrove?.toast?.('Progress synced');
}

function debouncedSync() {
  if (!currentUser) return;
  
  clearTimeout(syncDebounceTimer);
  syncDebounceTimer = setTimeout(async () => {
    const local = getLocalData();
    const mig = window.SkillgroveMigrate.migrateRetiredProgress(local.progress, retirementMap());
    if (mig.changed) setLocalData(mig.progress, null);
    await upsertRemote({ progress: mig.progress, timing: local.timing });
  }, SYNC_DEBOUNCE_MS);
}

async function initAuth() {
  const sb = getSupabase();
  if (!sb) {
    console.warn('Supabase not available — auth disabled');
    return;
  }
  
  try {
    const { data: { session } } = await sb.auth.getSession();
    if (session?.user) {
      currentUser = session.user;
      updateAuthUI();
      await syncOnSignIn();
    } else {
      updateAuthUI();
    }
  } catch (e) {
    console.error('Auth init error:', e);
    updateAuthUI();
  }
  
  sb.auth.onAuthStateChange(async (event, session) => {
    const wasSignedIn = !!currentUser;
    currentUser = session?.user || null;
    updateAuthUI();
    
    if (currentUser && !wasSignedIn) {
      await syncOnSignIn();
    }
  });
  
  window.addEventListener('online', () => {
    if (currentUser && (syncStatus === 'offline' || syncStatus === 'error')) {
      debouncedSync();
    }
  });
  
  window.addEventListener('offline', () => {
    if (currentUser) {
      setSyncStatus('offline');
    }
  });
}

const originalSetItem = localStorage.setItem.bind(localStorage);
localStorage.setItem = function(key, value) {
  originalSetItem(key, value);
  if (key === PROGRESS_KEY || key === TIMING_KEY) {
    debouncedSync();
  }
};

window.SkillgroveAuth = {
  init: initAuth,
  openSignIn: openSignInModal,
  signOut,
  getUser: () => currentUser,
  getSyncStatus: () => syncStatus,
  mergeProgress,
  mergeTiming,
  mergeSkill,
  migrateSyncedProgress
};

})();
