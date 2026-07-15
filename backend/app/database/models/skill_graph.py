"""Skill Graph database models.

Models the relational knowledge graph representation of candidates, skills,
projects, platforms, and evidence.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import GraphNodeType, GraphRelationshipType

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class SkillGraphNode(Base):
    """A node in the candidate's skill knowledge graph."""

    __tablename__ = "skill_graph_nodes"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this node belongs to.",
    )
    node_type: Mapped[GraphNodeType] = mapped_column(
        Enum(GraphNodeType, name="graph_node_type", native_enum=True),
        nullable=False,
        doc="The type of entity this node represents (SKILL, PROJECT, etc.).",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Label/name of the node.",
    )
    properties: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Arbitrary node metadata and parameters.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="skill_graph_nodes",
    )


class SkillGraphEdge(Base):
    """A directed edge in the candidate's skill knowledge graph."""

    __tablename__ = "skill_graph_edges"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this edge belongs to.",
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skill_graph_nodes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The starting node ID.",
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skill_graph_nodes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The ending node ID.",
    )
    relationship_type: Mapped[GraphRelationshipType] = mapped_column(
        Enum(GraphRelationshipType, name="graph_relationship_type", native_enum=True),
        nullable=False,
        doc="The relationship name (KNOWS, USES, IMPLEMENTS, etc.).",
    )
    properties: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Arbitrary edge metadata and parameters.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="skill_graph_edges",
    )
    source_node: Mapped[SkillGraphNode] = relationship(
        "SkillGraphNode",
        foreign_keys=[source_node_id],
        backref="outgoing_edges",
    )
    target_node: Mapped[SkillGraphNode] = relationship(
        "SkillGraphNode",
        foreign_keys=[target_node_id],
        backref="incoming_edges",
    )
