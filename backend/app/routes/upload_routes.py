import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
from ..models.schemas import DocumentUploadResponse, User, Node, Edge, EntityType, RelationType
from ..models.database import db
from ..services.auth import get_current_user
from ..services.storage import storage_service
from ..services.pdf_parser import pdf_parser
from ..services.vertex_ai import vertex_ai_service

router = APIRouter(prefix="/upload", tags=["Secure Ingestion & Extraction"])

@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Securely uploads a research document (PDF, Markdown, Code), audits storage,
    triggers Vertex AI entity extraction & embedding generation, and updates the knowledge graph.
    """
    # 1. Validate file extension
    filename = file.filename or "unnamed_document"
    ext = os.path.splitext(filename)[1].lower()
    allowed_exts = [".pdf", ".md", ".txt", ".markdown", ".py", ".r", ".jl", ".ipynb", ".tex"]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(allowed_exts)}"
        )

    # 2. Secure Storage & Audit Hash
    doc_id, local_path, audit_meta = await storage_service.save_file(file, current_user.id)
    db.log_audit(
        action="DOCUMENT_UPLOADED",
        user_id=current_user.id,
        document_id=doc_id,
        details={"filename": filename, "file_size": audit_meta["file_size_bytes"]}
    )

    # 3. Parse Document Content
    parsed_doc = pdf_parser.parse_file(local_path)

    # 4. Extract Entities & Relationships via Vertex AI / Gemini
    extracted = await vertex_ai_service.extract_entities(parsed_doc["full_text"], filename)

    # 5. Generate Vector Embedding for Paper
    paper_text_for_embed = f"{extracted.title} {extracted.abstract} {' '.join(extracted.key_findings)}"
    paper_vector = await vertex_ai_service.generate_embedding(paper_text_for_embed)

    # 6. Insert Paper Node
    primary_dept = extracted.departments[0] if extracted.departments else current_user.department
    paper_node = Node(
        id=doc_id,
        name=extracted.title,
        type=EntityType.PAPER,
        department=primary_dept,
        properties={
            "year": extracted.year,
            "doi": extracted.doi or f"10.1145/{doc_id}",
            "abstract": extracted.abstract,
            "filename": filename,
            "file_size": audit_meta["file_size_bytes"],
            "uploader": current_user.name,
            "key_findings": extracted.key_findings,
            "domains": extracted.domains
        }
    )
    db.add_node(paper_node, embedding=paper_vector)
    nodes_created = 1
    edges_created = 0

    # 7. Insert Authors & Edges
    for author_name in extracted.authors:
        auth_id = f"auth_{author_name.lower().replace(' ', '_').replace('.', '')}"
        if not db.get_node(auth_id):
            auth_vec = await vertex_ai_service.generate_embedding(f"{author_name} {primary_dept}")
            db.add_node(Node(
                id=auth_id,
                name=author_name,
                type=EntityType.AUTHOR,
                department=primary_dept,
                properties={"auto_extracted": True}
            ), embedding=auth_vec)
            nodes_created += 1

        db.add_edge(Edge(
            id=f"edge_{doc_id}_{auth_id}",
            source=doc_id,
            target=auth_id,
            relation=RelationType.CO_AUTHORED,
            weight=1.0
        ))
        edges_created += 1

    # 8. Insert Methods & Edges
    for meth in extracted.methods:
        meth_name = meth.get("name") if isinstance(meth, dict) else str(meth)
        meth_id = f"meth_{meth_name.lower().replace(' ', '_')[:30]}"
        if not db.get_node(meth_id):
            m_vec = await vertex_ai_service.generate_embedding(meth_name)
            db.add_node(Node(
                id=meth_id,
                name=meth_name,
                type=EntityType.METHOD,
                properties=meth if isinstance(meth, dict) else {"category": "Extracted Method"}
            ), embedding=m_vec)
            nodes_created += 1

        db.add_edge(Edge(
            id=f"edge_{doc_id}_{meth_id}",
            source=doc_id,
            target=meth_id,
            relation=RelationType.APPLIES_METHOD,
            weight=1.0
        ))
        edges_created += 1

    # 9. Insert Datasets & Edges
    for ds in extracted.datasets:
        ds_name = ds.get("name") if isinstance(ds, dict) else str(ds)
        ds_id = f"ds_{ds_name.lower().replace(' ', '_')[:30]}"
        if not db.get_node(ds_id):
            ds_vec = await vertex_ai_service.generate_embedding(ds_name)
            db.add_node(Node(
                id=ds_id,
                name=ds_name,
                type=EntityType.DATASET,
                properties=ds if isinstance(ds, dict) else {"type": "Extracted Dataset"}
            ), embedding=ds_vec)
            nodes_created += 1

        db.add_edge(Edge(
            id=f"edge_{doc_id}_{ds_id}",
            source=doc_id,
            target=ds_id,
            relation=RelationType.USES_DATASET,
            weight=1.0
        ))
        edges_created += 1

    db.log_audit(
        action="EXTRACTION_COMPLETED",
        user_id=current_user.id,
        document_id=doc_id,
        details={"nodes_created": nodes_created, "edges_created": edges_created}
    )

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=filename,
        status="PROCESSED_AND_INDEXED",
        file_type=parsed_doc.get("file_type", ext),
        file_size_bytes=audit_meta["file_size_bytes"],
        extracted_entities=extracted,
        nodes_created=nodes_created,
        edges_created=edges_created,
        vector_indexed=True,
        audit_log=audit_meta
    )
