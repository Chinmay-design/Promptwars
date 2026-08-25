// Hybrid & Vector Research Search Module

let currentFilterDept = '';

function updateAlphaLabel(val) {
  const label = document.getElementById('alpha-val');
  if (label) label.textContent = `${Math.round(val * 100)}%`;
}

function setQuickSearchFilter(dept) {
  currentFilterDept = dept;
  document.querySelectorAll('.search-filter-tag').forEach(tag => {
    tag.classList.remove('bg-blue-600', 'text-white');
    tag.classList.add('bg-slate-800', 'text-slate-300');
  });
  event.target.classList.remove('bg-slate-800', 'text-slate-300');
  event.target.classList.add('bg-blue-600', 'text-white');
  
  const query = document.getElementById('search-query-input').value;
  if (query.trim()) executeSearch();
}

async function executeSearch(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('search-query-input');
  const query = input ? input.value.trim() : '';
  if (!query) return;

  const alphaInput = document.getElementById('hybrid-alpha');
  const alpha = alphaInput ? parseFloat(alphaInput.value) : 0.7;

  const resultsList = document.getElementById('search-results-list');
  const metaBar = document.getElementById('search-meta-bar');
  const totalCountEl = document.getElementById('search-total-count');
  const timeEl = document.getElementById('search-time');
  const expTagsEl = document.getElementById('query-expansion-tags');

  if (resultsList) {
    resultsList.innerHTML = `
      <div class="py-12 text-center text-slate-400">
        <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p class="text-xs">Running Vertex AI semantic vector search & graph indexing...</p>
      </div>
    `;
  }

  try {
    const payload = {
      query: query,
      hybrid_alpha: alpha,
      top_k: 15,
      filters: currentFilterDept ? { departments: [currentFilterDept] } : null
    };

    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (metaBar) metaBar.classList.remove('hidden');
    if (metaBar) metaBar.classList.add('flex');
    if (totalCountEl) totalCountEl.textContent = data.total_matches;
    if (timeEl) timeEl.textContent = `${data.execution_time_ms}ms`;

    // Render Query Expansion Tags
    if (expTagsEl && data.query_expansion) {
      expTagsEl.innerHTML = data.query_expansion.map(t => `
        <span class="px-2 py-0.5 rounded-full bg-blue-900/40 text-blue-300 border border-blue-700/50 text-[10px]">
          + ${t}
        </span>
      `).join('');
    }

    if (!data.results || data.results.length === 0) {
      resultsList.innerHTML = `
        <div class="text-center py-12 bg-slate-900/40 rounded-2xl border border-slate-800">
          <p class="text-xs text-slate-400">No matching research nodes found for "${query}".</p>
        </div>
      `;
      return;
    }

    resultsList.innerHTML = data.results.map(r => {
      const simPercent = Math.round(r.vector_similarity * 100);
      const isPaper = r.type === 'paper';
      const year = r.metadata.year || '2026';
      const doi = r.metadata.doi || '';

      return `
        <div class="bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 p-4 rounded-xl shadow-lg transition space-y-2.5">
          <div class="flex flex-wrap items-start justify-between gap-2">
            <div class="space-y-1 max-w-2xl">
              <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tag-${r.type}">${r.type}</span>
                <span class="text-xs text-slate-400">${r.department || 'Interdisciplinary'}</span>
                ${year ? `<span class="text-xs text-slate-500">• ${year}</span>` : ''}
              </div>
              <h3 class="text-sm font-bold text-white hover:text-blue-400 transition cursor-pointer" onclick="jumpToGraphNode('${r.id}')">
                ${r.name}
              </h3>
            </div>

            <!-- Vector Relevance Badge & Action -->
            <div class="flex items-center space-x-2">
              <div class="text-right">
                <div class="text-xs font-bold text-emerald-400">${simPercent}% Match</div>
                <div class="text-[10px] text-slate-500">Vector Sim: ${r.vector_similarity}</div>
              </div>
              <button onclick="jumpToGraphNode('${r.id}')" title="Explore in Graph" class="p-2 rounded-lg bg-slate-800 hover:bg-blue-600 text-slate-300 hover:text-white transition">
                <i data-lucide="network" class="w-4 h-4"></i>
              </button>
            </div>
          </div>

          <p class="text-xs text-slate-300 leading-relaxed">${r.snippet}</p>

          <!-- Connected Methods & Datasets Pills -->
          <div class="flex flex-wrap items-center gap-1.5 pt-1 text-[10px]">
            ${r.matched_methods.map(m => `<span class="px-2 py-0.5 rounded bg-purple-950/60 border border-purple-800/50 text-purple-300">Method: ${m}</span>`).join('')}
            ${r.matched_datasets.map(d => `<span class="px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/50 text-amber-300">Dataset: ${d}</span>`).join('')}
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    console.error("Search execution failed:", e);
  }
}

function jumpToGraphNode(nodeId) {
  switchTab('graph');
  setTimeout(() => {
    selectNodeById(nodeId);
  }, 100);
}
