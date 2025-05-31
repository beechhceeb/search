import re
import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from albatross.enums.enums import CameraType, MountType, SensorSize
from albatross.models import Base


class Camera(Base):
    __tablename__ = "cameras"
    id: Mapped[uuid.UUID] = mapped_column(
        SQLAlchemyUUID, primary_key=True, default=uuid.uuid4
    )
    brand: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String, unique=True)
    mpb_model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    crop_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sensor_size: Mapped[SensorSize] = mapped_column(Enum(SensorSize))
    type: Mapped[CameraType] = mapped_column(Enum(CameraType))
    mount: Mapped[MountType] = mapped_column(Enum(MountType))
    ibis: Mapped[bool] = mapped_column(Boolean)
    model_url_encoded: Mapped[str] = mapped_column(String)
    mpb_model_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    formatted_price: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model_url_segment: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    recommendations = relationship(
        "Recommendations",
        back_populates="primary_camera",
        cascade="none",
    )

    def __init__(
        self,
        brand: str,
        model: str,
        crop_factor: Optional[float],
        sensor_size: SensorSize,
        type: CameraType,
        mount: MountType,
        ibis: bool = True,  # FIXME: needs to be determined
        id: Optional[uuid.UUID] = None,
        mpb_model_id: str | None = None,
        price: float | None = None,
        image_link: str | None = None,
        model_url_segment: str | None = None,
        mpb_model: str | None = None,
    ) -> None:
        super().__init__()
        self.id = id or uuid.uuid4()
        self.brand = brand
        self.model = model
        self.model_url_encoded = re.sub(r"[^a-zA-Z0-9_]", "_", model)
        self.crop_factor = crop_factor
        self.sensor_size = sensor_size
        self.type = type
        self.mount = mount
        self.ibis = ibis
        self.mpb_model_id = mpb_model_id
        self.price = price
        self.formatted_price = (
            f"{self.price / 100:,.2f}" if self.price is not None else None
        )
        self.image_link = image_link
        self.model_url_segment = model_url_segment
        self.mpb_model = mpb_model
