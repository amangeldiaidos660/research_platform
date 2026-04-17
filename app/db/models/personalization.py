from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    works_count: Mapped[int] = mapped_column(default=0, server_default="0")
    cited_by_count: Mapped[int] = mapped_column(default=0, server_default="0")
    domain_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    field_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subfield_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    keywords_cache: Mapped[str | None] = mapped_column(Text, nullable=True)

    subscriptions = relationship("TopicSubscription", back_populates="topic", cascade="all,delete")
    publication_links = relationship(
        "PublicationTopic",
        back_populates="topic",
        cascade="all,delete-orphan",
    )


class PublicationAuthor(Base):
    __tablename__ = "publication_authors"
    __table_args__ = (
        UniqueConstraint("publication_id", "author_id", name="uq_publication_author"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    author_position: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_corresponding: Mapped[bool | None] = mapped_column(nullable=True)

    publication = relationship("Publication", back_populates="author_links")
    author = relationship("Author", back_populates="publication_links")


class PublicationTopic(Base):
    __tablename__ = "publication_topics"
    __table_args__ = (
        UniqueConstraint("publication_id", "topic_id", name="uq_publication_topic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"))
    score: Mapped[float | None] = mapped_column(nullable=True)

    publication = relationship("Publication", back_populates="topic_links")
    topic = relationship("Topic", back_populates="publication_links")


class FavoritePublication(Base):
    __tablename__ = "favorite_publications"
    __table_args__ = (
        UniqueConstraint("user_id", "publication_id", name="uq_user_publication_favorite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    user = relationship("User", back_populates="favorites")
    publication = relationship("Publication", back_populates="favorites")


class SavedSearch(TimestampMixin, Base):
    __tablename__ = "saved_searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    query: Mapped[str] = mapped_column(String(500))
    filters_json: Mapped[dict] = mapped_column(JSON, default=dict)

    user = relationship("User", back_populates="saved_searches")


class Collection(TimestampMixin, Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="collections")
    items = relationship("CollectionItem", back_populates="collection", cascade="all,delete")


class CollectionItem(Base):
    __tablename__ = "collection_items"
    __table_args__ = (
        UniqueConstraint("collection_id", "publication_id", name="uq_collection_publication_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"))
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    collection = relationship("Collection", back_populates="items")
    publication = relationship("Publication", back_populates="collection_items")


class TopicSubscription(Base):
    __tablename__ = "topic_subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_user_topic_subscription"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    user = relationship("User", back_populates="topic_subscriptions")
    topic = relationship("Topic", back_populates="subscriptions")
