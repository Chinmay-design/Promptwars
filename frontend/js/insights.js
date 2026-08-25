// Research Insights, Cross-Disciplinary Synergies & Redundancy Detection

async function loadInsights() {
  const collabList = document.getElementById('collab-cards-list');
  const redundancyList = document.getElementById('redundancy-cards-list');
  const datasetTable = document.getElementById('dataset-reuse-table');
  const trendsList = document.getElementById('cross-dept-synergies');

  try {
    const res = await fetch(`${API_BASE}/insights`);
    const data = await res.json();

    // 1. Render Hidden Collaborations
    if (collabList) {
      if (!data.collaboration_opportunities || data.collaboration_opportunities.length === 0) {
        collabList.innerHTML = `<div class="text-xs text-slate-500 py-4 text-center">No unlinked faculty synergies detected yet.</div>`;
      } else {
        collabList.innerHTML = data.collaboration_opportunities.map(c => `
          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <span class="font-bold text-xs text-emerald-400">${c.author_a}</span>
                <span class="text-[10px] text-slate-500">(${c.dept_a})</span>
                <i data-lucide="arrow-left-right" class="w-3 h-3 text-slate-500"></i>
                <span class="font-bold text-xs text-emerald-400">${c.author_b}</span>
                <span class="text-[10px] text-slate-500">(${c.dept_b})</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
                ${Math.round(c.synergy_score * 100)}% Synergy
              </span>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">${c.rationale}</p>
            <div class="flex flex-wrap gap-1 pt-1 text-[10px]">
              ${c.shared_methods.map(m => `<span class="px-2 py-0.5 rounded bg-purple-950/60 text-purple-300 border border-purple-800/40">Shared: ${m}</span>`).join('')}
              ${c.shared_datasets.map(d => `<span class="px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800/40">Shared Dataset: ${d}</span>`).join('')}
            </div>
          </div>
        `).join('');
      }
    }

    // 2. Render Redundancy Alerts
    if (redundancyList) {
      if (!data.redundancy_alerts || data.redundancy_alerts.length === 0) {
        redundancyList.innerHTML = `<div class="text-xs text-slate-500 py-4 text-center">No overlapping studies flagged. All grant tracks distinct.</div>`;
      } else {
        redundancyList.innerHTML = data.redundancy_alerts.map(r => `
          <div class="p-3.5 rounded-xl bg-slate-950 border border-amber-900/40 hover:border-amber-700 transition space-y-2">
            <div class="flex items-center justify-between">
              <div class="text-xs font-bold text-amber-300 flex items-center space-x-1.5">
                <i data-lucide="alert-circle" class="w-3.5 h-3.5 text-amber-400"></i>
                <span>Potential Study Overlap</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
                ${Math.round(r.similarity_score * 100)}% Similarity
              </span>
            </div>
            <div class="text-xs text-slate-200">
              <div><strong>[${r.dept_a}]</strong> ${r.paper_a_title}</div>
              <div class="text-slate-500 text-[10px] my-0.5">vs</div>
              <div><strong>[${r.dept_b}]</strong> ${r.paper_b_title}</div>
            </div>
            <p class="text-xs text-slate-400 leading-relaxed">${r.description}</p>
          </div>
        `).join('');
      }
    }

    // 3. Render Dataset Reuse Distribution Table
    if (datasetTable && data.dataset_reuse_distribution) {
      datasetTable.innerHTML = `
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400">
              <th class="pb-2 font-medium">Dataset Name</th>
              <th class="pb-2 font-medium">Format / Type</th>
              <th class="pb-2 font-medium">Size</th>
              <th class="pb-2 font-medium">Active Papers</th>
              <th class="pb-2 font-medium">Cross-Dept Lineage</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">
            ${data.dataset_reuse_distribution.map(d => `
              <tr class="hover:bg-slate-900/50">
                <td class="py-2.5 font-bold text-amber-400 font-sans">${d.name}</td>
                <td class="py-2.5 text-slate-400">${d.type}</td>
                <td class="py-2.5 text-slate-400">${d.size}</td>
                <td class="py-2.5 font-bold text-white">${d.paper_count} papers</td>
                <td class="py-2.5 text-slate-300 font-sans">
                  ${d.departments_using.length > 0 ? d.departments_using.map(dp => `<span class="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] mr-1">${dp}</span>`).join('') : '<span class="text-slate-500">Unattached</span>'}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    // 4. Render Cross-Department Trends
    if (trendsList && data.cross_department_synergies) {
      trendsList.innerHTML = data.cross_department_synergies.map(t => `
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
          <div class="flex items-center justify-between">
            <span class="font-bold text-white text-[11px]">${t.department_pair}</span>
            <span class="text-[10px] font-bold text-emerald-400">${t.growth_rate}</span>
          </div>
          <p class="text-slate-400 text-[11px]">Technique: <span class="text-blue-300">${t.shared_technique}</span></p>
        </div>
      `).join('');
    }

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    console.error("Failed to load insights:", e);
  }
}
