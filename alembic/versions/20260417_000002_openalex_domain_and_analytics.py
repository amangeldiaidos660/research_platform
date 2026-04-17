"""openalex domain and analytics schema

Revision ID: 20260417_000002
Revises: 20260417_000001
Create Date: 2026-04-17 00:00:02
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260417_000002"
down_revision = "20260417_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("publications", sa.Column("normalized_title", sa.String(length=1000), nullable=True))
    op.add_column("publications", sa.Column("abstract_text", sa.Text(), nullable=True))
    op.add_column("publications", sa.Column("abstract_summary", sa.Text(), nullable=True))
    op.add_column("publications", sa.Column("publication_date", sa.String(length=25), nullable=True))
    op.add_column("publications", sa.Column("open_access_url", sa.String(length=1000), nullable=True))
    op.add_column("publications", sa.Column("type", sa.String(length=100), nullable=True))
    op.add_column("publications", sa.Column("language", sa.String(length=50), nullable=True))
    op.add_column("publications", sa.Column("keywords_cache", sa.Text(), nullable=True))
    op.add_column("publications", sa.Column("raw_json", sa.Text(), nullable=True))
    op.create_index("ix_publications_normalized_title", "publications", ["normalized_title"])

    op.add_column("topics", sa.Column("cited_by_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("topics", sa.Column("domain_name", sa.String(length=255), nullable=True))
    op.add_column("topics", sa.Column("field_name", sa.String(length=255), nullable=True))
    op.add_column("topics", sa.Column("subfield_name", sa.String(length=255), nullable=True))

    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("openalex_id", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("orcid", sa.String(length=255), nullable=True),
        sa.Column("works_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cited_by_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_stats_json", sa.Text(), nullable=True),
        sa.Column("last_known_institution", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("openalex_id"),
    )
    op.create_index("ix_authors_display_name", "authors", ["display_name"])

    op.create_table(
        "publication_authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("publication_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("author_position", sa.String(length=50), nullable=True),
        sa.Column("is_corresponding", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_id", "author_id", name="uq_publication_author"),
    )

    op.create_table(
        "publication_topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("publication_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_id", "topic_id", name="uq_publication_topic"),
    )

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("query_text", sa.String(length=255), nullable=True),
        sa.Column("filters_json", sa.Text(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("processed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ingestion_jobs")
    op.drop_table("publication_topics")
    op.drop_table("publication_authors")
    op.drop_index("ix_authors_display_name", table_name="authors")
    op.drop_table("authors")
    op.drop_column("topics", "subfield_name")
    op.drop_column("topics", "field_name")
    op.drop_column("topics", "domain_name")
    op.drop_column("topics", "cited_by_count")
    op.drop_index("ix_publications_normalized_title", table_name="publications")
    op.drop_column("publications", "raw_json")
    op.drop_column("publications", "keywords_cache")
    op.drop_column("publications", "language")
    op.drop_column("publications", "type")
    op.drop_column("publications", "open_access_url")
    op.drop_column("publications", "publication_date")
    op.drop_column("publications", "abstract_summary")
    op.drop_column("publications", "abstract_text")
    op.drop_column("publications", "normalized_title")
