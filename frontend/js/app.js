// Global Application State & SSO Management
const API_BASE = '/api';

const state = {
  currentUser: {
    id: "usr_vance_01",
    name: "Dr. Elena Vance",
    email: "elena.vance@university.edu",
    department: "Computer Science & AI",
    role: "researcher",
    avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
  },
  token: null,
  currentTab: 'graph'
};

document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  await fetchUserProfile();
  initGraph();
  checkBackendHealth();
});

function switchTab(tabId) {
  state.currentTab = tabId;
  
  // Hide all panels
  document.querySelectorAll('.view-panel').forEach(el => el.classList.add('hidden'));
  
  // Show active panel
  const activeView = document.getElementById(`view-${tabId}`);
  if (activeView) {
    activeView.classList.remove('hidden');
  }

  // Update tab button styles
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-blue-600', 'text-white', 'shadow-sm');
    btn.classList.add('text-slate-400');
  });

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.remove('text-slate-400');
    activeBtn.classList.add('bg-blue-600', 'text-white', 'shadow-sm');
  }

  // Re-trigger layout/data for specific views
  if (tabId === 'graph') {
    setTimeout(() => {
      resizeGraphCanvas();
      if (typeof reloadGraph === 'function') reloadGraph();
    }, 50);
  } else if (tabId === 'insights') {
    if (typeof loadInsights === 'function') loadInsights();
  } else if (tabId === 'audit') {
    loadAuditLogs();
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    const badge = document.getElementById('ai-pipeline-badge');
    if (badge) {
      badge.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        <span>${data.mode}</span>
      `;
    }
  } catch (e) {
    console.warn("Backend health check warning:", e);
  }
}

async function fetchUserProfile() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {}
    });
    if (res.ok) {
      const user = await res.json();
      state.currentUser = user;
      updateUserUI();
    }
  } catch (e) {
    console.error("Auth fetch failed:", e);
  }
}

function updateUserUI() {
  const nameEl = document.getElementById('user-name');
  const deptEl = document.getElementById('user-dept');
  const avatarEl = document.getElementById('user-avatar');

  if (nameEl) nameEl.textContent = state.currentUser.name;
  if (deptEl) deptEl.textContent = state.currentUser.department;
  if (avatarEl && state.currentUser.avatar_url) avatarEl.src = state.currentUser.avatar_url;
}

async function openSSOModal() {
  const modal = document.getElementById('sso-modal');
  const list = document.getElementById('faculty-list');
  if (!modal || !list) return;

  try {
    const res = await fetch(`${API_BASE}/auth/faculty-directory`);
    const directory = await res.json();

    list.innerHTML = directory.map(fac => `
      <div onclick="loginAs('${fac.email}')" class="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 cursor-pointer transition flex items-center space-x-3 group">
        <img src="${fac.avatar_url}" class="w-9 h-9 rounded-full object-cover border border-slate-700">
        <div class="flex-1">
          <div class="text-xs font-bold text-white group-hover:text-blue-400">${fac.name}</div>
          <div class="text-[10px] text-slate-400">${fac.department} • <span class="capitalize text-blue-300 font-medium">${fac.role.replace('_', ' ')}</span></div>
        </div>
        <i data-lucide="log-in" class="w-4 h-4 text-slate-500 group-hover:text-blue-400"></i>
      </div>
    `).join('');

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  } catch (e) {
    console.error("Failed to load faculty directory:", e);
  }
}

function closeSSOModal() {
  const modal = document.getElementById('sso-modal');
  if (modal) modal.classList.add('hidden');
}

async function loginAs(email) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (res.ok) {
      const data = await res.json();
      state.currentUser = data.user;
      state.token = data.access_token;
      updateUserUI();
      closeSSOModal();
      showToast(`Authenticated via SSO as ${data.user.name}`);
    }
  } catch (e) {
    showToast("SSO Authentication failed");
  }
}

async function loadAuditLogs() {
  const tbody = document.getElementById('audit-table-body');
  if (!tbody) return;
  try {
    const res = await fetch(`${API_BASE}/insights/audit-logs`, {
      headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {}
    });
    const data = await res.json();
    
    if (!data.events || data.events.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500">No events logged yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.events.map(ev => {
      const dt = new Date(ev.timestamp * 1000).toLocaleTimeString();
      return `
        <tr class="hover:bg-slate-900/40">
          <td class="py-2.5 text-slate-400">${dt}</td>
          <td class="py-2.5 font-semibold text-blue-400">${ev.action}</td>
          <td class="py-2.5 text-slate-300">${ev.user_id}</td>
          <td class="py-2.5 text-slate-400">${ev.document_id || '-'}</td>
          <td class="py-2.5 text-slate-500">${JSON.stringify(ev.details)}</td>
        </tr>
      `;
    }).join('');
  } catch (e) {
    console.error("Failed to load audit logs:", e);
  }
}

function showToast(message) {
  const toast = document.getElementById('toast');
  const msg = document.getElementById('toast-msg');
  if (!toast || !msg) return;

  msg.textContent = message;
  toast.classList.remove('translate-y-20', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');

  setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('translate-y-20', 'opacity-0');
  }, 3500);
}
