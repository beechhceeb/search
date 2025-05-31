import logging
import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from albatross.models import Base
from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.results import Results
from albatross.photographer_classifier import PhotographerClassifier

log = logging.getLogger(__name__)

recommendation_lenses = Table(
    "recommendation_lenses",
    Base.metadata,
    Column(
        "recommendation_id", Uuid, ForeignKey("recommendations.id"), primary_key=True
    ),
    Column("lens_id", Uuid, ForeignKey("lenses.id"), primary_key=True),
)


class Recommendations(Base):
    """
    Class to generate recommendations based on the results
    """

    __tablename__ = "recommendations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    primary_camera_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("cameras.id"), nullable=True
    )
    current_widest_aperture: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    favourite_focal_length: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    recommended_aperture: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recommended_focal_length: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    recommendation_statement: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_lens_recommendation_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    llm_camera_recommendation_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    primary_camera = relationship(
        "Camera", back_populates="recommendations", cascade="none"
    )
    primary_mount_lenses = relationship(
        "Lens",
        secondary="recommendation_lenses",
        back_populates="recommendations",
        cascade="none",
    )

    def __init__(
        self,
        primary_camera: Camera | None,
        primary_mount_lenses: list[Lens],
        current_widest_aperture: float | None,
        favourite_focal_length: int | None,
        recommended_aperture: float | None,
        recommended_focal_length: int | None,
        results: Results,
        recommendation_statement: str = "",
        llm_lens_recommendation: str | None = None,
        llm_camera_recommendation: str | None = None,
    ):
        self.primary_camera = primary_camera
        self.primary_mount_lenses = primary_mount_lenses
        self.current_widest_aperture: float | None = current_widest_aperture
        self.favourite_focal_length: int | None = favourite_focal_length
        self.recommended_aperture: float | None = recommended_aperture
        self.recommended_focal_length: int | None = recommended_focal_length
        self.results: Results = results
        self.photographer_classifier: PhotographerClassifier = PhotographerClassifier(
            results=results, current_widest_aperture=current_widest_aperture
        )
        self.recommendation_statement: str = recommendation_statement

        self.llm_lens_recommendation = llm_lens_recommendation
        self.llm_camera_recommendation = llm_camera_recommendation
