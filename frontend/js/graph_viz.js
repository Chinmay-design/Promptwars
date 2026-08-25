// Interactive 2D Canvas Force-Directed Knowledge Graph Engine

const graphState = {
  nodes: [],
  edges: [],
  nodeMap: new Map(),
  selectedNode: null,
  hoveredNode: null,
  activeEntityTypes: new Set(['paper', 'author', 'method', 'dataset', 'department']),
  deptFilter: '',
  searchHighlight: '',
  
  // Transform & Physics
  transform: { x: 0, y: 0, scale: 1 },
  isDraggingCanvas: false,
  isDraggingNode: false,
  dragTarget: null,
  lastMouse: { x: 0, y: 0 },
  animationId: null
};

const ENTITY_COLORS = {
  paper: '#38bdf8',
  author: '#34d399',
  dataset: '#fbbf24',
  method: '#c084fc',
  department: '#f43f5e',
  domain: '#a855f7'
};

const ENTITY_RADIUS = {
  paper: 12,
  author: 10,
  dataset: 9,
  method: 9,
  department: 16,
  domain: 8
};

function initGraph() {
  const canvas = document.getElementById('graph-canvas');
  if (!canvas) return;

  resizeGraphCanvas();
  window.addEventListener('resize', resizeGraphCanvas);

  // Setup Interaction Handlers
  canvas.addEventListener('mousedown', handleMouseDown);
  canvas.addEventListener('mousemove', handleMouseMove);
  canvas.addEventListener('mouseup', handleMouseUp);
  canvas.addEventListener('wheel', handleWheel, { passive: false });

  loadGraphData();
}

function resizeGraphCanvas() {
  const container = document.getElementById('graph-container');
  const canvas = document.getElementById('graph-canvas');
  if (!container || !canvas) return;

  const rect = container.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  
  if (graphState.transform.x === 0 && graphState.transform.y === 0) {
    graphState.transform.x = (rect.width / 2);
    graphState.transform.y = (rect.height / 2);
  }
}

async function loadGraphData() {
  try {
    let url = `${API_BASE}/graph/topology`;
    const params = new URLSearchParams();
    if (graphState.deptFilter) params.append('department', graphState.deptFilter);
    if (params.toString()) url += `?${params.toString()}`;

    const res = await fetch(url);
    const data = await res.json();

    const container = document.getElementById('graph-container');
    const width = container ? container.clientWidth : 800;
    const height = container ? container.clientHeight : 600;

    // Filter nodes by active entity types
    const filteredNodes = data.nodes.filter(n => graphState.activeEntityTypes.has(n.type));
    const allowedNodeIds = new Set(filteredNodes.map(n => n.id));

    // Initialize node physics coordinates
    graphState.nodes = filteredNodes.map((n, i) => {
      const existing = graphState.nodeMap.get(n.id);
      const angle = (i / filteredNodes.length) * 2 * Math.PI;
      const radius = 180 + (n.community_id || 0) * 40 + Math.random() * 80;

      return {
        ...n,
        x: existing ? existing.x : Math.cos(angle) * radius,
        y: existing ? existing.y : Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: ENTITY_RADIUS[n.type] || 10
      };
    });

    graphState.nodeMap = new Map(graphState.nodes.map(n => [n.id, n]));

    // Filter edges
    graphState.edges = data.edges
      .filter(e => allowedNodeIds.has(e.source) && allowedNodeIds.has(e.target))
      .map(e => ({
        ...e,
        sourceNode: graphState.nodeMap.get(e.source),
        targetNode: graphState.nodeMap.get(e.target)
      }));

    // Update Stats Badge
    updateStatsUI(data.stats);

    // Start Force Simulation loop
    startSimulation();
  } catch (e) {
    console.error("Failed to load graph topology:", e);
  }
}

function updateStatsUI(stats) {
  if (!stats) return;
  const nEl = document.getElementById('stat-nodes');
  const eEl = document.getElementById('stat-edges');
  const dEl = document.getElementById('stat-density');
  if (nEl) nEl.textContent = stats.total_nodes;
  if (eEl) eEl.textContent = stats.total_edges;
  if (dEl) dEl.textContent = stats.density;
}

// Force Simulation Physics Loop
function startSimulation() {
  if (graphState.animationId) cancelAnimationFrame(graphState.animationId);

  let iterations = 0;
  function step() {
    simulateForces();
    renderGraph();
    iterations++;
    graphState.animationId = requestAnimationFrame(step);
  }
  step();
}

function simulateForces() {
  const nodes = graphState.nodes;
  const edges = graphState.edges;
  const repulsion = 1200;
  const springLength = 70;
  const springStrength = 0.04;
  const damping = 0.86;
  const centerGravity = 0.015;

  // Repulsion between nodes (Coulomb)
  for (let i = 0; i < nodes.length; i++) {
    const n1 = nodes[i];
    for (let j = i + 1; j < nodes.length; j++) {
      const n2 = nodes[j];
      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const distSq = dx * dx + dy * dy + 100;
      const dist = Math.sqrt(distSq);
      const force = repulsion / distSq;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;

      n1.vx -= fx;
      n1.vy -= fy;
      n2.vx += fx;
      n2.vy += fy;
    }

    // Centering force
    n1.vx -= n1.x * centerGravity;
    n1.vy -= n1.y * centerGravity;
  }

  // Edge Spring Attraction (Hooke)
  for (const edge of edges) {
    if (!edge.sourceNode || !edge.targetNode) continue;
    const dx = edge.targetNode.x - edge.sourceNode.x;
    const dy = edge.targetNode.y - edge.sourceNode.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const force = (dist - springLength) * springStrength;
    const fx = (dx / dist) * force;
    const fy = (dy / dist) * force;

    edge.sourceNode.vx += fx;
    edge.sourceNode.vy += fy;
    edge.targetNode.vx -= fx;
    edge.targetNode.vy -= fy;
  }

  // Update positions with damping
  for (const n of nodes) {
    if (graphState.isDraggingNode && graphState.dragTarget === n) continue;
    n.vx *= damping;
    n.vy *= damping;
    n.x += n.vx;
    n.y += n.vy;
  }
}

// 2D Canvas Renderer
function renderGraph() {
  const canvas = document.getElementById('graph-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;

  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Apply Camera Transform
  ctx.translate(graphState.transform.x * dpr, graphState.transform.y * dpr);
  ctx.scale(graphState.transform.scale * dpr, graphState.transform.scale * dpr);

  // 1. Draw Edges
  for (const edge of graphState.edges) {
    if (!edge.sourceNode || !edge.targetNode) continue;

    const isConnectedToHovered = graphState.hoveredNode && 
      (edge.source === graphState.hoveredNode.id || edge.target === graphState.hoveredNode.id);
    
    ctx.beginPath();
    ctx.moveTo(edge.sourceNode.x, edge.sourceNode.y);
    ctx.lineTo(edge.targetNode.x, edge.targetNode.y);

    if (isConnectedToHovered) {
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 2.5;
      ctx.globalAlpha = 0.9;
    } else {
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.35;
    }
    ctx.stroke();
  }

  // 2. Draw Nodes
  for (const node of graphState.nodes) {
    const isHovered = graphState.hoveredNode === node;
    const isSelected = graphState.selectedNode && graphState.selectedNode.id === node.id;
    const isSearched = graphState.searchHighlight && node.name.toLowerCase().includes(graphState.searchHighlight);

    const baseColor = ENTITY_COLORS[node.type] || '#94a3b8';

    // Outer glow for hovered/selected/searched
    if (isHovered || isSelected || isSearched) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius + 7, 0, Math.PI * 2);
      ctx.fillStyle = isSearched ? 'rgba(251, 191, 36, 0.4)' : 'rgba(56, 189, 248, 0.4)';
      ctx.fill();
    }

    // Node Circle Body
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
    ctx.fillStyle = baseColor;
    ctx.globalAlpha = 1.0;
    ctx.fill();
    ctx.strokeStyle = isSelected ? '#ffffff' : '#0f172a';
    ctx.lineWidth = isSelected ? 2.5 : 1.5;
    ctx.stroke();

    // Node Label
    ctx.font = `${node.type === 'paper' || node.type === 'department' ? 'bold' : 'normal'} 9px Plus Jakarta Sans, sans-serif`;
    ctx.fillStyle = '#e2e8f0';
    ctx.textAlign = 'center';
    const label = node.name.length > 20 ? node.name.slice(0, 18) + '...' : node.name;
    ctx.fillText(label, node.x, node.y + node.radius + 12);
  }

  ctx.restore();
}

// Mouse / Touch Interaction Handlers
function getTransformedMousePos(e) {
  const canvas = document.getElementById('graph-canvas');
  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;

  const worldX = (mouseX - graphState.transform.x) / graphState.transform.scale;
  const worldY = (mouseY - graphState.transform.y) / graphState.transform.scale;

  return { worldX, worldY, mouseX, mouseY };
}

function findNodeAt(worldX, worldY) {
  for (let i = graphState.nodes.length - 1; i >= 0; i--) {
    const node = graphState.nodes[i];
    const dx = node.x - worldX;
    const dy = node.y - worldY;
    if (dx * dx + dy * dy <= (node.radius + 5) * (node.radius + 5)) {
      return node;
    }
  }
  return null;
}

function handleMouseDown(e) {
  const { worldX, worldY, mouseX, mouseY } = getTransformedMousePos(e);
  const clickedNode = findNodeAt(worldX, worldY);

  if (clickedNode) {
    graphState.isDraggingNode = true;
    graphState.dragTarget = clickedNode;
    selectNode(clickedNode);
  } else {
    graphState.isDraggingCanvas = true;
    graphState.lastMouse = { x: mouseX, y: mouseY };
  }
}

function handleMouseMove(e) {
  const { worldX, worldY, mouseX, mouseY } = getTransformedMousePos(e);

  if (graphState.isDraggingNode && graphState.dragTarget) {
    graphState.dragTarget.x = worldX;
    graphState.dragTarget.y = worldY;
  } else if (graphState.isDraggingCanvas) {
    const dx = mouseX - graphState.lastMouse.x;
    const dy = mouseY - graphState.lastMouse.y;
    graphState.transform.x += dx;
    graphState.transform.y += dy;
    graphState.lastMouse = { x: mouseX, y: mouseY };
  } else {
    const hovered = findNodeAt(worldX, worldY);
    graphState.hoveredNode = hovered;
  }
}

function handleMouseUp() {
  graphState.isDraggingNode = false;
  graphState.isDraggingCanvas = false;
  graphState.dragTarget = null;
}

function handleWheel(e) {
  e.preventDefault();
  const { mouseX, mouseY } = getTransformedMousePos(e);
  const zoomFactor = e.deltaY < 0 ? 1.12 : 0.88;
  const newScale = Math.max(0.2, Math.min(3.5, graphState.transform.scale * zoomFactor));

  graphState.transform.x = mouseX - (mouseX - graphState.transform.x) * (newScale / graphState.transform.scale);
  graphState.transform.y = mouseY - (mouseY - graphState.transform.y) * (newScale / graphState.transform.scale);
  graphState.transform.scale = newScale;
}

function resetGraphZoom() {
  const container = document.getElementById('graph-container');
  if (!container) return;
  graphState.transform = {
    x: container.clientWidth / 2,
    y: container.clientHeight / 2,
    scale: 1.0
  };
}

function reloadGraph() {
  loadGraphData();
}

// Side Drawer Inspection
async function selectNode(node) {
  graphState.selectedNode = node;
  const drawer = document.getElementById('node-drawer');
  if (!drawer) return;

  try {
    const res = await fetch(`${API_BASE}/graph/node/${node.id}`);
    const details = await res.json();
    populateDrawer(details);
    drawer.classList.remove('translate-x-full');
  } catch (e) {
    console.error("Failed to load node details:", e);
  }
}

function closeNodeDrawer() {
  const drawer = document.getElementById('node-drawer');
  if (drawer) drawer.classList.add('translate-x-full');
  graphState.selectedNode = null;
}

function populateDrawer(data) {
  const node = data.node;
  const conns = data.connections;

  const tag = document.getElementById('drawer-tag');
  const title = document.getElementById('drawer-title');
  const dept = document.getElementById('drawer-dept');
  const abstract = document.getElementById('drawer-abstract');
  const abstractContainer = document.getElementById('drawer-abstract-container');
  const propsEl = document.getElementById('drawer-props');
  const connsEl = document.getElementById('drawer-connections');

  if (tag) {
    tag.textContent = node.type;
    tag.className = `px-2 py-0.5 text-[10px] font-bold uppercase rounded border tag-${node.type}`;
  }
  if (title) title.textContent = node.name;
  if (dept) dept.textContent = node.department || 'Interdisciplinary Core';

  if (node.properties.abstract) {
    if (abstractContainer) abstractContainer.classList.remove('hidden');
    if (abstract) abstract.textContent = node.properties.abstract;
  } else {
    if (abstractContainer) abstractContainer.classList.add('hidden');
  }

  if (propsEl) {
    propsEl.innerHTML = Object.entries(node.properties)
      .filter(([k]) => k !== 'abstract')
      .map(([k, v]) => `<div><span class="text-slate-500">${k}:</span> <span class="text-slate-200">${JSON.stringify(v)}</span></div>`)
      .join('') || '<div class="text-slate-500">No additional properties</div>';
  }

  if (connsEl) {
    connsEl.innerHTML = conns.map(c => `
      <div onclick="selectNodeById('${c.node.id}')" class="p-2 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 cursor-pointer transition flex items-center justify-between group">
        <div class="flex items-center space-x-2">
          <span class="w-2 h-2 rounded-full dot-${c.node.type}"></span>
          <span class="text-xs text-slate-200 group-hover:text-blue-400 font-medium">${c.node.name}</span>
        </div>
        <span class="text-[10px] text-slate-500 font-mono">${c.relation}</span>
      </div>
    `).join('') || '<div class="text-xs text-slate-500">No active links</div>';
  }
}

function selectNodeById(nodeId) {
  const node = graphState.nodeMap.get(nodeId);
  if (node) selectNode(node);
}

function toggleEntityTypeFilter(type) {
  if (graphState.activeEntityTypes.has(type)) {
    graphState.activeEntityTypes.delete(type);
  } else {
    graphState.activeEntityTypes.add(type);
  }
  
  // Toggle UI filter button active state
  document.querySelectorAll(`.tag-${type}`).forEach(btn => {
    if (graphState.activeEntityTypes.has(type)) {
      btn.classList.add('active', 'opacity-100');
      btn.classList.remove('opacity-40');
    } else {
      btn.classList.remove('active', 'opacity-100');
      btn.classList.add('opacity-40');
    }
  });

  loadGraphData();
}

function applyGraphFilters() {
  const deptSelect = document.getElementById('graph-dept-filter');
  if (deptSelect) graphState.deptFilter = deptSelect.value;
  loadGraphData();
}

function highlightGraphNode(searchTerm) {
  graphState.searchHighlight = searchTerm.trim().toLowerCase();
}
