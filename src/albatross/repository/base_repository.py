from contextlib import contextmanager
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload, sessionmaker

import json

from albatross.config import DATABASE_URL
from albatross.models import Base
from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.recommendations import Recommendations
from albatross.photographer_classifier import PhotographerClassifier
from albatross.serializers.results import ResultsSerializer


class AlbatrossRepository:
    def __init__(self, session: Optional[sessionmaker[Session]] = None) -> None:
        if session is None:
            engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(
                engine
            )  # Create tables for all models inheriting from Base
            self.session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        else:
            self.session_factory = session

    @contextmanager
    def session_scope(self) -> Any:  # pragma: no cover
        """Provide a transactional scope around a series of operations."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_camera_by_model(self, camera_model: str) -> Camera | None:
        """
        Get a camera from the database if it exists.
        """
        with self.session_scope() as session:
            camera = session.query(Camera).filter_by(model=camera_model).first()
            if camera:  # pragma: no branch
                # Detach from session instance
                session.expunge(camera)
            return camera

    def get_lens_by_model(self, lens_model: str) -> Lens | None:
        """
        Get a lens from the database if it exists.
        """
        with self.session_scope() as session:
            lens = session.query(Lens).filter_by(model=lens_model).first()
            if lens:  # pragma: no branch
                # Detach from session instance
                session.expunge(lens)
            return lens

    def persist(self, instance: Base) -> Base:
        with self.session_scope() as session:
            if isinstance(instance, Recommendations):
                instance.results_json = ResultsSerializer().to_json(instance.results)
                instance.llm_lens_recommendation_json = (
                    json.dumps(instance.llm_lens_recommendation)
                    if hasattr(instance, "llm_lens_recommendation")
                    else None
                )
                instance.llm_camera_recommendation_json = (
                    json.dumps(instance.llm_camera_recommendation)
                    if hasattr(instance, "llm_camera_recommendation")
                    else None
                )

                # ensure related objects are part of the session so that
                # SQLAlchemy does not warn when flushing the recommendation
                if instance.primary_camera is not None:
                    instance.primary_camera = session.merge(instance.primary_camera)
                if instance.primary_mount_lenses:
                    instance.primary_mount_lenses = [
                        session.merge(lens) for lens in instance.primary_mount_lenses
                    ]
            if instance.id is None:
                session.add(instance)
            else:
                instance = session.merge(instance)  # Merge if ID exists

            # Ensure SQLAlchemy flushes pending changes before the instance
            # is detached from the session. Otherwise the object would be
            # removed from the session before any INSERT or UPDATE occurs.
            session.flush()
            print(f"[persist] Flushed and assigned ID: {instance.id}")
            session.expunge(instance)
            if not isinstance(instance.id, UUID):
                raise TypeError(
                    f"Expected instance.id to be of type UUID, but got "
                    f"{type(instance.id).__name__}"
                )
            return instance

    def get_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendations | None:
        print(
            f"[get_recommendation] Looking for recommendation ID: {recommendation_id}"
        )
        with self.session_scope() as session:
            recommendation = session.get(
                Recommendations,
                recommendation_id,
                options=[
                    joinedload(Recommendations.primary_camera),
                    joinedload(Recommendations.primary_mount_lenses),
                ],
            )
            print(f"[get_recommendation] Fetched recommendation: {recommendation}")
            if recommendation:  # pragma: no branch
                session.expunge(recommendation)
                if recommendation.primary_camera is not None:
                    session.expunge(recommendation.primary_camera)
                for lens in recommendation.primary_mount_lenses:
                    session.expunge(lens)
                if recommendation.results_json:
                    recommendation.results = ResultsSerializer.from_json(
                        recommendation.results_json
                    )
                    recommendation.photographer_classifier = PhotographerClassifier(
                        results=recommendation.results,
                        current_widest_aperture=recommendation.current_widest_aperture,
                    )
                if recommendation.llm_lens_recommendation_json:
                    recommendation.llm_lens_recommendation = json.loads(
                        recommendation.llm_lens_recommendation_json
                    )
                if recommendation.llm_camera_recommendation_json:
                    recommendation.llm_camera_recommendation = json.loads(
                        recommendation.llm_camera_recommendation_json
                    )
                return recommendation
            else:
                return None


repository = AlbatrossRepository()
