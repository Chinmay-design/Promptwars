import asyncio
import logging
from ..models.database import db
from ..models.schemas import Node, Edge, EntityType, RelationType
from .vertex_ai import vertex_ai_service

logger = logging.getLogger("research_kg.seed")

RESEARCH_DEPARTMENTS = [
    {"id": "dept_cs", "name": "Computer Science & AI", "type": EntityType.DEPARTMENT, "properties": {"faculty_head": "Dr. Elena Vance", "building": "Turing Hall"}},
    {"id": "dept_bio", "name": "Genomics & Bioinformatics", "type": EntityType.DEPARTMENT, "properties": {"faculty_head": "Dr. Marcus Thorne", "building": "Franklin Genomics Center"}},
    {"id": "dept_climate", "name": "Earth & Climate Sciences", "type": EntityType.DEPARTMENT, "properties": {"faculty_head": "Prof. Sarah Lin", "building": "Curie Earth Sciences Lab"}},
    {"id": "dept_neuro", "name": "Neuroscience & Cognitive Science", "type": EntityType.DEPARTMENT, "properties": {"faculty_head": "Dr. David Chen", "building": "Cajal Brain Institute"}},
    {"id": "dept_physics", "name": "Physics & Quantum Engineering", "type": EntityType.DEPARTMENT, "properties": {"faculty_head": "Dr. Rajiv Patel", "building": "Feynman Quantum Center"}}
]

RESEARCH_AUTHORS = [
    {"id": "auth_vance", "name": "Dr. Elena Vance", "type": EntityType.AUTHOR, "department": "Computer Science & AI", "properties": {"h_index": 34, "lab": "Scalable Foundation Models Lab"}},
    {"id": "auth_thorne", "name": "Dr. Marcus Thorne", "type": EntityType.AUTHOR, "department": "Genomics & Bioinformatics", "properties": {"h_index": 29, "lab": "Computational Epigenomics Lab"}},
    {"id": "auth_lin", "name": "Prof. Sarah Lin", "type": EntityType.AUTHOR, "department": "Earth & Climate Sciences", "properties": {"h_index": 41, "lab": "Global Climate Modeling Lab"}},
    {"id": "auth_chen", "name": "Dr. David Chen", "type": EntityType.AUTHOR, "department": "Neuroscience & Cognitive Science", "properties": {"h_index": 27, "lab": "Neural Connectomics Lab"}},
    {"id": "auth_patel", "name": "Dr. Rajiv Patel", "type": EntityType.AUTHOR, "department": "Physics & Quantum Engineering", "properties": {"h_index": 31, "lab": "Quantum Computing & Information Lab"}},
    {"id": "auth_ross", "name": "Dr. Amanda Ross", "type": EntityType.AUTHOR, "department": "Computer Science & AI", "properties": {"h_index": 22, "lab": "Robotics & Multi-Agent Systems"}},
    {"id": "auth_kim", "name": "Dr. Jin Kim", "type": EntityType.AUTHOR, "department": "Genomics & Bioinformatics", "properties": {"h_index": 19, "lab": "Structural Biology Group"}}
]

RESEARCH_DATASETS = [
    {"id": "ds_tcga", "name": "TCGA-PanCancer-MultiOmics", "type": EntityType.DATASET, "properties": {"size": "3.5TB", "format": "BAM/FASTQ/VCF", "license": "NIH Open Access"}},
    {"id": "ds_era5", "name": "ERA5-Atmospheric-Reanalysis", "type": EntityType.DATASET, "properties": {"size": "1.8TB", "format": "NetCDF-4", "license": "Copernicus Open"}},
    {"id": "ds_hcp", "name": "Human-Connectome-Project-fMRI", "type": EntityType.DATASET, "properties": {"size": "4.2TB", "format": "NIfTI", "license": "Open Science"}},
    {"id": "ds_quantum", "name": "Qubits-Noise-Tomography-128Q", "type": EntityType.DATASET, "properties": {"size": "450GB", "format": "HDF5", "license": "University Proprietary"}},
    {"id": "ds_nlp", "name": "BioMedical-Preprint-Corpus-2026", "type": EntityType.DATASET, "properties": {"size": "120GB", "format": "Parquet", "license": "CC-BY 4.0"}}
]

RESEARCH_METHODS = [
    {"id": "meth_transformer", "name": "Multi-Head Cross-Attention Transformer", "type": EntityType.METHOD, "properties": {"framework": "PyTorch / JAX", "domain": "Deep Learning"}},
    {"id": "meth_gnn", "name": "Equivariant Graph Neural Networks (EGNN)", "type": EntityType.METHOD, "properties": {"framework": "PyTorch Geometric", "domain": "Geometric DL"}},
    {"id": "meth_pinn", "name": "Physics-Informed Neural Operators (PINO)", "type": EntityType.METHOD, "properties": {"framework": "TensorFlow / JAX", "domain": "Scientific ML"}},
    {"id": "meth_diffusion", "name": "Latent Flow Matching & SDEs", "type": EntityType.METHOD, "properties": {"framework": "Diffusers / JAX", "domain": "Generative Modeling"}},
    {"id": "meth_spectral", "name": "High-Order Spectral Graph Laplacian", "type": EntityType.METHOD, "properties": {"framework": "SciPy / Julia", "domain": "Network Analysis"}}
]

RESEARCH_PAPERS = [
    {
        "id": "paper_genomics_llm",
        "name": "Cross-Attention Transformers for Pan-Cancer Somatic Mutation Prediction",
        "type": EntityType.PAPER,
        "department": "Genomics & Bioinformatics",
        "properties": {
            "year": 2026,
            "doi": "10.1038/s41587-026-01290-x",
            "abstract": "Accurate prediction of driver non-coding somatic mutations remains a fundamental hurdle in precision oncology. We propose GenomicCrossAttn, a hierarchical transformer that incorporates 3D chromatin accessibility and transcription factor motifs to identify pathogenic variants across 12,000 tumor genomes.",
            "citations_count": 48
        },
        "authors": ["auth_thorne", "auth_kim"],
        "methods": ["meth_transformer", "meth_gnn"],
        "datasets": ["ds_tcga", "ds_nlp"]
    },
    {
        "id": "paper_climate_pinn",
        "name": "Physics-Informed Neural Operators for Sub-Seasonal Extreme Weather Forecasting",
        "type": EntityType.PAPER,
        "department": "Earth & Climate Sciences",
        "properties": {
            "year": 2026,
            "doi": "10.1175/JCLI-D-26-0042.1",
            "abstract": "Sub-seasonal atmospheric prediction suffers from chaotic divergence at 14+ day horizons. We demonstrate that continuous Fourier Neural Operators conditioned on Navier-Stokes conservation laws predict extreme temperature anomalies with 40% lower RMSE than traditional ensemble simulations.",
            "citations_count": 32
        },
        "authors": ["auth_lin"],
        "methods": ["meth_pinn", "meth_diffusion"],
        "datasets": ["ds_era5"]
    },
    {
        "id": "paper_brain_connectome",
        "name": "Equivariant Graph Diffusion on Whole-Brain Structural and Functional Connectomes",
        "type": EntityType.PAPER,
        "department": "Neuroscience & Cognitive Science",
        "properties": {
            "year": 2025,
            "doi": "10.1016/j.neuroimage.2025.120194",
            "abstract": "Mapping the information flow between cortical regions requires preserving SO(3) rotational symmetries. Our work applies SE(3)-equivariant graph diffusion to reconstruct dynamical neuro-trajectories in resting-state fMRI, discovering modular sub-networks involved in cognitive flexibility.",
            "citations_count": 21
        },
        "authors": ["auth_chen"],
        "methods": ["meth_gnn", "meth_spectral"],
        "datasets": ["ds_hcp"]
    },
    {
        "id": "paper_quantum_ml",
        "name": "Quantum Variational Eigensolvers Enhanced by Graph Neural Networks",
        "type": EntityType.PAPER,
        "department": "Physics & Quantum Engineering",
        "properties": {
            "year": 2026,
            "doi": "10.1103/PhysRevLett.136.040601",
            "abstract": "Noisy Intermediate-Scale Quantum (NISQ) devices suffer from barren plateau optimization landscapes. We employ graph neural networks to dynamically prune variational quantum circuits, demonstrating quadratic convergence speedups on 64-qubit Hamiltonian ground-state estimations.",
            "citations_count": 39
        },
        "authors": ["auth_patel"],
        "methods": ["meth_gnn"],
        "datasets": ["ds_quantum"]
    },
    {
        "id": "paper_scalable_diffusion",
        "name": "Discrete Flow Matching for High-Dimensional Scientific PDE Simulation",
        "type": EntityType.PAPER,
        "department": "Computer Science & AI",
        "properties": {
            "year": 2026,
            "doi": "10.1145/3618490.3627118",
            "abstract": "Simulating high-dimensional nonlinear PDEs on unstructured meshes demands adaptive resolution. We introduce Continuous-Time Discrete Flow Matching, achieving 100x speedups over classical finite element solvers while preserving vorticity invariants.",
            "citations_count": 55
        },
        "authors": ["auth_vance", "auth_ross"],
        "methods": ["meth_diffusion", "meth_pinn"],
        "datasets": ["ds_era5"]
    }
]

async def seed_initial_knowledge_graph():
    logger.info("Initializing University Research Knowledge Graph Seed Data...")
    
    # 1. Add Departments
    for d in RESEARCH_DEPARTMENTS:
        node = Node(id=d["id"], name=d["name"], type=d["type"], properties=d["properties"])
        vec = await vertex_ai_service.generate_embedding(f"{d['name']} {d['properties'].get('faculty_head', '')}")
        db.add_node(node, embedding=vec)

    # 2. Add Authors
    for a in RESEARCH_AUTHORS:
        node = Node(id=a["id"], name=a["name"], type=a["type"], department=a["department"], properties=a["properties"])
        vec = await vertex_ai_service.generate_embedding(f"{a['name']} {a['department']} {a['properties'].get('lab', '')}")
        db.add_node(node, embedding=vec)
        
        # Edge: Author -> Department
        dept_node_id = next((d["id"] for d in RESEARCH_DEPARTMENTS if d["name"] == a["department"]), None)
        if dept_node_id:
            db.add_edge(Edge(
                id=f"edge_{a['id']}_{dept_node_id}",
                source=a["id"],
                target=dept_node_id,
                relation=RelationType.AFFILIATED_WITH,
                weight=1.0
            ))

    # 3. Add Datasets
    for ds in RESEARCH_DATASETS:
        node = Node(id=ds["id"], name=ds["name"], type=ds["type"], properties=ds["properties"])
        vec = await vertex_ai_service.generate_embedding(f"{ds['name']} {ds['properties'].get('format', '')} {ds['properties'].get('size', '')}")
        db.add_node(node, embedding=vec)

    # 4. Add Methods
    for m in RESEARCH_METHODS:
        node = Node(id=m["id"], name=m["name"], type=m["type"], properties=m["properties"])
        vec = await vertex_ai_service.generate_embedding(f"{m['name']} {m['properties'].get('domain', '')} {m['properties'].get('framework', '')}")
        db.add_node(node, embedding=vec)

    # 5. Add Papers & Edges
    for p in RESEARCH_PAPERS:
        node = Node(id=p["id"], name=p["name"], type=p["type"], department=p["department"], properties=p["properties"])
        vec = await vertex_ai_service.generate_embedding(f"{p['name']} {p['properties'].get('abstract', '')}")
        db.add_node(node, embedding=vec)

        # Edges to Authors (CO_AUTHORED / WRITTEN_BY)
        for auth_id in p["authors"]:
            db.add_edge(Edge(
                id=f"edge_{p['id']}_{auth_id}",
                source=p["id"],
                target=auth_id,
                relation=RelationType.CO_AUTHORED,
                weight=1.0
            ))

        # Edges to Methods (APPLIES_METHOD)
        for meth_id in p["methods"]:
            db.add_edge(Edge(
                id=f"edge_{p['id']}_{meth_id}",
                source=p["id"],
                target=meth_id,
                relation=RelationType.APPLIES_METHOD,
                weight=1.0
            ))
            # Author -> Method connection
            for auth_id in p["authors"]:
                db.add_edge(Edge(
                    id=f"edge_{auth_id}_{meth_id}",
                    source=auth_id,
                    target=meth_id,
                    relation=RelationType.APPLIES_METHOD,
                    weight=0.8
                ))

        # Edges to Datasets (USES_DATASET)
        for ds_id in p["datasets"]:
            db.add_edge(Edge(
                id=f"edge_{p['id']}_{ds_id}",
                source=p["id"],
                target=ds_id,
                relation=RelationType.USES_DATASET,
                weight=1.0
            ))
            for meth_id in p["methods"]:
                db.add_edge(Edge(
                    id=f"edge_{meth_id}_{ds_id}",
                    source=meth_id,
                    target=ds_id,
                    relation=RelationType.USES_DATASET,
                    weight=0.6
                ))

    logger.info(f"Knowledge Graph Seed Complete: {len(db.nodes)} nodes, {len(db.edges)} edges, {len(db.vectors)} vector embeddings.")
