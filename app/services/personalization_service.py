from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    Collection,
    CollectionItem,
    FavoritePublication,
    Publication,
    SavedSearch,
    Topic,
    TopicSubscription,
    User,
)
from app.schemas.personalization import (
    CollectionCreate,
    CollectionItemCreate,
    FavoriteCreate,
    SavedSearchCreate,
    TopicSubscriptionCreate,
)


def get_or_create_publication(db: Session, publication_data) -> Publication:
    publication = (
        db.query(Publication)
        .filter(Publication.openalex_id == publication_data.openalex_id)
        .first()
    )
    if publication:
        publication.title = publication_data.title
        publication.publication_year = publication_data.publication_year
        publication.cited_by_count = publication_data.cited_by_count
        publication.doi = publication_data.doi
        publication.primary_location_source = publication_data.primary_location_source
        return publication

    publication = Publication(
        openalex_id=publication_data.openalex_id,
        title=publication_data.title,
        publication_year=publication_data.publication_year,
        cited_by_count=publication_data.cited_by_count,
        doi=publication_data.doi,
        primary_location_source=publication_data.primary_location_source,
    )
    db.add(publication)
    db.flush()
    return publication


def get_or_create_topic(db: Session, topic_data) -> Topic:
    topic = db.query(Topic).filter(Topic.openalex_id == topic_data.openalex_id).first()
    if topic:
        topic.name = topic_data.name
        topic.description = topic_data.description
        topic.works_count = topic_data.works_count
        topic.keywords_cache = topic_data.keywords_cache
        return topic

    topic = Topic(
        openalex_id=topic_data.openalex_id,
        name=topic_data.name,
        description=topic_data.description,
        works_count=topic_data.works_count,
        keywords_cache=topic_data.keywords_cache,
    )
    db.add(topic)
    db.flush()
    return topic


def list_favorites(db: Session, user: User) -> list[FavoritePublication]:
    return (
        db.query(FavoritePublication)
        .options(joinedload(FavoritePublication.publication))
        .filter(FavoritePublication.user_id == user.id)
        .order_by(FavoritePublication.id.desc())
        .all()
    )


def add_favorite(db: Session, user: User, payload: FavoriteCreate) -> FavoritePublication:
    publication = get_or_create_publication(db, payload.publication)
    favorite = (
        db.query(FavoritePublication)
        .filter(
            FavoritePublication.user_id == user.id,
            FavoritePublication.publication_id == publication.id,
        )
        .first()
    )
    if favorite:
        return favorite

    favorite = FavoritePublication(user_id=user.id, publication_id=publication.id)
    db.add(favorite)
    db.commit()
    return (
        db.query(FavoritePublication)
        .options(joinedload(FavoritePublication.publication))
        .filter(FavoritePublication.id == favorite.id)
        .one()
    )


def remove_favorite(db: Session, user: User, publication_id: int) -> None:
    favorite = (
        db.query(FavoritePublication)
        .filter(
            FavoritePublication.user_id == user.id,
            FavoritePublication.publication_id == publication_id,
        )
        .first()
    )
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")

    db.delete(favorite)
    db.commit()


def list_saved_searches(db: Session, user: User) -> list[SavedSearch]:
    return db.query(SavedSearch).filter(SavedSearch.user_id == user.id).order_by(SavedSearch.id.desc()).all()


def create_saved_search(db: Session, user: User, payload: SavedSearchCreate) -> SavedSearch:
    saved_search = SavedSearch(
        user_id=user.id,
        name=payload.name,
        query=payload.query,
        filters_json=payload.filters_json,
    )
    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)
    return saved_search


def list_collections(db: Session, user: User) -> list[Collection]:
    return (
        db.query(Collection)
        .options(joinedload(Collection.items).joinedload(CollectionItem.publication))
        .filter(Collection.user_id == user.id)
        .order_by(Collection.id.desc())
        .all()
    )


def create_collection(db: Session, user: User, payload: CollectionCreate) -> Collection:
    collection = Collection(user_id=user.id, name=payload.name, description=payload.description)
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def add_collection_item(
    db: Session,
    user: User,
    collection_id: int,
    payload: CollectionItemCreate,
) -> Collection:
    collection = (
        db.query(Collection)
        .options(joinedload(Collection.items).joinedload(CollectionItem.publication))
        .filter(Collection.id == collection_id, Collection.user_id == user.id)
        .first()
    )
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    publication = get_or_create_publication(db, payload.publication)
    existing_item = (
        db.query(CollectionItem)
        .filter(
            CollectionItem.collection_id == collection.id,
            CollectionItem.publication_id == publication.id,
        )
        .first()
    )
    if not existing_item:
        db.add(CollectionItem(collection_id=collection.id, publication_id=publication.id))
        db.commit()

    return (
        db.query(Collection)
        .options(joinedload(Collection.items).joinedload(CollectionItem.publication))
        .filter(Collection.id == collection.id)
        .one()
    )


def list_topic_subscriptions(db: Session, user: User) -> list[TopicSubscription]:
    return (
        db.query(TopicSubscription)
        .options(joinedload(TopicSubscription.topic))
        .filter(TopicSubscription.user_id == user.id)
        .order_by(TopicSubscription.id.desc())
        .all()
    )


def create_topic_subscription(
    db: Session,
    user: User,
    payload: TopicSubscriptionCreate,
) -> TopicSubscription:
    topic = get_or_create_topic(db, payload.topic)
    subscription = (
        db.query(TopicSubscription)
        .filter(TopicSubscription.user_id == user.id, TopicSubscription.topic_id == topic.id)
        .first()
    )
    if subscription:
        return subscription

    subscription = TopicSubscription(user_id=user.id, topic_id=topic.id)
    db.add(subscription)
    db.commit()
    return (
        db.query(TopicSubscription)
        .options(joinedload(TopicSubscription.topic))
        .filter(TopicSubscription.id == subscription.id)
        .one()
    )
