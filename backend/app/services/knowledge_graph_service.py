"""Knowledge Graph Service.

Constructs skill nodes and relationships inside the relational skill graph tables
representing candidates, projects, skills, platforms, and evidence.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import GraphNodeType, GraphRelationshipType
from app.database.models.skill_graph import SkillGraphEdge, SkillGraphNode
from app.database.models.evaluation_history import EvaluationHistory

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Service to create, update, and inspect the Candidate Skill Knowledge Graph."""

    async def build_graph(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        extracted_skills: dict[str, dict[str, Any]],
        github_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Rebuild the knowledge graph nodes and edges for the candidate."""
        # 1. Purge existing graph nodes and edges for candidate to ensure idempotency
        await db.execute(
            delete(SkillGraphEdge).where(SkillGraphEdge.candidate_profile_id == candidate_id)
        )
        await db.execute(
            delete(SkillGraphNode).where(SkillGraphNode.candidate_profile_id == candidate_id)
        )
        await db.flush()

        nodes_count = 0
        edges_count = 0

        # Helper to insert nodes
        async def _create_node(ntype: GraphNodeType, name: str, props: dict | None = None) -> SkillGraphNode:
            nonlocal nodes_count
            node = SkillGraphNode(
                candidate_profile_id=candidate_id,
                node_type=ntype,
                name=name,
                properties=props or {},
            )
            db.add(node)
            await db.flush()
            nodes_count += 1
            return node

        # Helper to insert edges
        async def _create_edge(
            src: uuid.UUID, target: uuid.UUID, rel: GraphRelationshipType, props: dict | None = None
        ) -> None:
            nonlocal edges_count
            edge = SkillGraphEdge(
                candidate_profile_id=candidate_id,
                source_node_id=src,
                target_node_id=target,
                relationship_type=rel,
                properties=props or {},
            )
            db.add(edge)
            await db.flush()
            edges_count += 1

        # ── 2. Create Candidate Root Node ─────────────────────────────────────
        candidate_node = await _create_node(
            GraphNodeType.EVIDENCE, "Candidate Root", {"candidate_id": str(candidate_id)}
        )

        # ── 3. Build Nodes and Edges ─────────────────────────────────────────
        skill_nodes: dict[str, SkillGraphNode] = {}
        for sname, info in extracted_skills.items():
            # Create Skill node
            snode = await _create_node(
                GraphNodeType.SKILL, sname, {"category": str(info["category"])}
            )
            skill_nodes[sname.lower()] = snode

            # Add Candidate KNOWS Skill relationship
            await _create_edge(candidate_node.id, snode.id, GraphRelationshipType.KNOWS)

            # Analyze evidences to map CLAIMS or PROVES relationships
            for ev in info.get("evidences", []):
                source = ev.get("source")
                if source == "RESUME":
                    # Resume CLAIMS Skill
                    await _create_edge(candidate_node.id, snode.id, GraphRelationshipType.CLAIMS, {"text": ev["evidence"]})
                else:
                    # Platform PROVES Skill
                    await _create_edge(candidate_node.id, snode.id, GraphRelationshipType.PROVES, {"source": str(source)})

        # ── 4. Build Project Nodes and USES/IMPLEMENTS relationships ──────────
        if github_profile and github_profile.get("projects"):
            for proj in github_profile["projects"]:
                pname = proj.get("name", "Project")
                pnode = await _create_node(
                    GraphNodeType.PROJECT, pname, {"url": proj.get("url", ""), "stars": proj.get("stars", 0)}
                )

                # Candidate USES Project
                await _create_edge(candidate_node.id, pnode.id, GraphRelationshipType.USES)

                # Link Project USES Technology / IMPLEMENTS Framework
                plang = proj.get("primary_language", "").lower()
                if plang in skill_nodes:
                    await _create_edge(pnode.id, skill_nodes[plang].id, GraphRelationshipType.USES)

                for lang in proj.get("languages", []):
                    lang_lower = lang.lower()
                    if lang_lower in skill_nodes and lang_lower != plang:
                        await _create_edge(pnode.id, skill_nodes[lang_lower].id, GraphRelationshipType.USES)

        # ── 5. Record History ────────────────────────────────────────────────
        history = EvaluationHistory(
            candidate_profile_id=candidate_id,
            action="GRAPH_CREATION",
            metadata_json={
                "nodes_created": nodes_count,
                "edges_created": edges_count,
            },
        )
        db.add(history)
        await db.commit()

        logger.info(
            "Knowledge graph built for candidate %s (%d nodes, %d edges)",
            candidate_id,
            nodes_count,
            edges_count,
        )

        return {"nodes": nodes_count, "edges": edges_count}

    async def get_graph(self, db: AsyncSession, candidate_id: uuid.UUID) -> dict[str, Any]:
        """Fetch nodes and edges representing the candidate's skill graph."""
        stmt_nodes = select(SkillGraphNode).where(
            SkillGraphNode.candidate_profile_id == candidate_id,
            SkillGraphNode.deleted_at.is_(None),
        )
        res_nodes = await db.execute(stmt_nodes)
        nodes = res_nodes.scalars().all()

        stmt_edges = select(SkillGraphEdge).where(
            SkillGraphEdge.candidate_profile_id == candidate_id,
            SkillGraphEdge.deleted_at.is_(None),
        )
        res_edges = await db.execute(stmt_edges)
        edges = res_edges.scalars().all()

        return {
            "nodes": [
                {
                    "id": str(n.id),
                    "node_type": n.node_type,
                    "name": n.name,
                    "properties": n.properties,
                }
                for n in nodes
            ],
            "edges": [
                {
                    "id": str(e.id),
                    "source": str(e.source_node_id),
                    "target": str(e.target_node_id),
                    "relationship_type": e.relationship_type,
                    "properties": e.properties,
                }
                for e in edges
            ],
        }
