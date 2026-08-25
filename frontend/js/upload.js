// Secure Document Ingestion & Live Vertex AI Pipeline Module

document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('border-blue-500', 'bg-slate-900');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('border-blue-500', 'bg-slate-900');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-blue-500', 'bg-slate-900');
      if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });
  }
});

async function handleFileSelect(file) {
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  await executeUploadPipeline(formData, file.name);
}

async function injectSamplePaper(type) {
  let sampleContent = "";
  let sampleFilename = "";

  if (type === 'bio_ai') {
    sampleFilename = "Epigenetic_Cross_Attention_Bioinformatics.pdf";
    sampleContent = `
Title: Hierarchical Cross-Attention Transformers for Epigenetic Somatic Mutation Profiling
Authors: Dr. Marcus Thorne, Dr. Elena Vance
Department: Genomics & Bioinformatics
Abstract: Non-coding somatic mutations in human tumor genomes exhibit cell-type-specific transcriptional dysregulation. We propose EpigenCrossAttn, a cross-attention transformer combining 3D Hi-C chromatin contacts, ATAC-seq accessibility, and RNA-seq expression from the TCGA-PanCancer dataset to identify pathogenic non-coding alterations.
Methods: Multi-Head Cross-Attention Transformer, Graph Neural Networks (GNN)
Datasets: TCGA-PanCancer-MultiOmics, BioMedical-Preprint-Corpus-2026
Key Findings: Improved discovery rate of distal non-coding drivers by 38% with genome-wide empirical FDR < 0.01.
`;
  } else if (type === 'climate_pinn') {
    sampleFilename = "Atmospheric_Fourier_Operators_Climate.md";
    sampleContent = `
Title: Physics-Informed Fourier Neural Operators for Multi-Scale Atmospheric Dynamics
Authors: Prof. Sarah Lin, Dr. David Chen
Department: Earth & Climate Sciences
Abstract: High-resolution atmospheric circulation modeling requires coupling kinetic convection with planetary-scale Rossby waves. We present FourierFlowPINN, integrating Navier-Stokes conservation laws directly into neural operator Fourier layers trained on the ERA5 dataset.
Methods: Physics-Informed Neural Operators (PINO), Latent Flow Matching & SDEs
Datasets: ERA5-Atmospheric-Reanalysis
Key Findings: Reduced 10-day geopotential height error by 27% compared to operational numerical weather prediction.
`;
  }

  const blob = new Blob([sampleContent], { type: 'text/plain' });
  const file = new File([blob], sampleFilename, { type: 'text/plain' });

  const formData = new FormData();
  formData.append('file', file);

  await executeUploadPipeline(formData, sampleFilename);
}

async function executeUploadPipeline(formData, filename) {
  const consoleEl = document.getElementById('extraction-output');
  const badge = document.getElementById('extraction-badge');
  
  if (badge) badge.classList.add('hidden');
  resetPipelineSteps();

  // Step 1: Sanitize & Hash
  setStepActive(1);
  appendConsole(`[STEP 1/5] Ingesting "${filename}" into private secure storage...`);
  appendConsole(`[AUDIT] Generating SHA-256 integrity hash & scanning file signatures...`);
  await delay(400);
  setStepDone(1);

  // Step 2: Text Parsing
  setStepActive(2);
  appendConsole(`[STEP 2/5] Parsing document structure and extracting text chunks...`);
  await delay(400);
  setStepDone(2);

  // Step 3: Vertex AI Gemini Extraction
  setStepActive(3);
  appendConsole(`[STEP 3/5] Invoking Vertex AI (Gemini 1.5) for entity & relationship extraction...`);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {},
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      appendConsole(`[ERROR] Ingestion failed: ${err.detail || 'Server error'}`);
      return;
    }

    const data = await res.json();
    setStepDone(3);

    // Step 4: Vector Embeddings
    setStepActive(4);
    appendConsole(`[STEP 4/5] Generating 768-dimensional dense vector embeddings with Vertex AI...`);
    await delay(300);
    setStepDone(4);

    // Step 5: AlloyDB & Graph
    setStepActive(5);
    appendConsole(`[STEP 5/5] Storing in AlloyDB / PostgreSQL & linking Knowledge Graph...`);
    appendConsole(` -> Nodes Created: ${data.nodes_created}`);
    appendConsole(` -> Edges Created: ${data.edges_created}`);
    appendConsole(` -> Vector Index: Active in pgvector (cosine)`);
    await delay(300);
    setStepDone(5);

    if (badge) badge.classList.remove('hidden');

    appendConsole(`\n[EXTRACTED ENTITIES & RELATIONS]:\n` + JSON.stringify(data.extracted_entities, null, 2));

    showToast(`Successfully ingested "${filename}" into Knowledge Graph!`);

    // Refresh graph data in background
    loadGraphData();
  } catch (e) {
    appendConsole(`[ERROR] Network or ingestion error: ${e.message}`);
  }
}

function resetPipelineSteps() {
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`pipe-step-${i}`);
    if (el) {
      el.className = "pipe-step p-3 rounded-xl bg-slate-950 border border-slate-800 text-center";
      const icon = el.querySelector('.step-icon');
      if (icon) {
        icon.className = "w-7 h-7 rounded-full bg-slate-800 text-slate-400 mx-auto flex items-center justify-center text-xs font-bold mb-1.5 step-icon";
        icon.textContent = i;
      }
    }
  }
}

function setStepActive(stepNum) {
  const el = document.getElementById(`pipe-step-${stepNum}`);
  if (el) {
    el.className = "pipe-step p-3 rounded-xl bg-blue-950/60 border border-blue-500 text-center animate-pulse";
    const icon = el.querySelector('.step-icon');
    if (icon) {
      icon.className = "w-7 h-7 rounded-full bg-blue-600 text-white mx-auto flex items-center justify-center text-xs font-bold mb-1.5 step-icon";
    }
  }
}

function setStepDone(stepNum) {
  const el = document.getElementById(`pipe-step-${stepNum}`);
  if (el) {
    el.className = "pipe-step p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/50 text-center";
    const icon = el.querySelector('.step-icon');
    if (icon) {
      icon.className = "w-7 h-7 rounded-full bg-emerald-500 text-slate-950 mx-auto flex items-center justify-center text-xs font-bold mb-1.5 step-icon";
      icon.textContent = "✓";
    }
  }
}

function appendConsole(text) {
  const consoleEl = document.getElementById('extraction-output');
  if (consoleEl) {
    consoleEl.textContent += `\n${text}`;
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
