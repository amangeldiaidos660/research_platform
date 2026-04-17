"""initial auth and personalization schema

Revision ID: 20260417_000001
Revises: None
Create Date: 2026-04-17 00:00:01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260417_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("openalex_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=1000), nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("cited_by_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("doi", sa.String(length=255), nullable=True),
        sa.Column("primary_location_source", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doi"),
        sa.UniqueConstraint("openalex_id"),
    )
    op.create_index("ix_publications_publication_year", "publications", ["publication_year"])

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("openalex_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("works_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("keywords_cache", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("openalex_id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "favorite_publications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("publication_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "publication_id", name="uq_user_publication_favorite"),
    )

    op.create_table(
        "saved_searches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("filters_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "collection_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("publication_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "collection_id",
            "publication_id",
            name="uq_collection_publication_item",
        ),
    )

    op.create_table(
        "topic_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "topic_id", name="uq_user_topic_subscription"),
    )


def downgrade() -> None:
    op.drop_table("topic_subscriptions")
    op.drop_table("collection_items")
    op.drop_table("collections")
    op.drop_table("saved_searches")
    op.drop_table("favorite_publications")
    op.drop_table("users")
    op.drop_table("topics")
    op.drop_index("ix_publications_publication_year", table_name="publications")
    op.drop_table("publications")

