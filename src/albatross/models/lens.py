import re
import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from albatross.config import MountType
from albatross.models import Base


class Lens(Base):
    __tablename__ = "lenses"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    brand: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String, unique=True)
    focal_length_min: Mapped[float] = mapped_column(Float)
    focal_length_max: Mapped[float] = mapped_column(Float)
    largest_aperture_at_minimum_focal_length: Mapped[float] = mapped_column(Float)
    largest_aperture_at_maximum_focal_length: Mapped[float] = mapped_column(Float)
    mount: Mapped[Optional[MountType]] = mapped_column(Enum(MountType))
    prime: Mapped[bool] = mapped_column(Boolean)
    model_url_encoded: Mapped[str] = mapped_column(String, unique=True)
    mpb_model_id: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True
    )
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    formatted_price: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model_url_segment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mpb_model: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    recommendations = relationship(
        "Recommendations",
        secondary="recommendation_lenses",
        back_populates="primary_mount_lenses",
        cascade="none",
    )

    def __init__(
        self,
        brand: str,
        model: str,
        focal_length_min: float,
        focal_length_max: float,
        largest_aperture_at_minimum_focal_length: float,
        largest_aperture_at_maximum_focal_length: float,
        prime: Optional[bool] = None,
        mount: Optional[MountType] = None,
        crop_factor: Optional[float] = None,
        id: Optional[uuid.UUID] = None,
        mpb_model_id: Optional[str] = None,
        price: Optional[float] = None,
        image_link: Optional[str] = None,
        model_url_segment: Optional[str] = None,
        mpb_model: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.id = id or uuid.uuid4()
        self.brand = brand
        self.model = model
        self.model_url_encoded = re.sub(r"[^a-zA-Z0-9_]", "_", model)
        self.focal_length_min = focal_length_min
        self.focal_length_max = focal_length_max
        self.largest_aperture_at_minimum_focal_length = (
            largest_aperture_at_minimum_focal_length
        )
        self.largest_aperture_at_maximum_focal_length = (
            largest_aperture_at_maximum_focal_length
        )
        self.prime = prime or self._is_prime()
        self.mount = mount
        self.crop_factor = crop_factor
        self.mpb_model_id = mpb_model_id
        self.price = price
        self.formatted_price = (
            f"{self.price / 100:,.2f}" if self.price is not None else None
        )
        self.image_link = image_link
        self.model_url_segment = model_url_segment
        self.mpb_model = mpb_model

    def _is_prime(self) -> bool:
        return self.focal_length_min == self.focal_length_max
