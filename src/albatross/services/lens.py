import logging
import math
import re
import sqlite3
from typing import Any, Dict, Optional

from albatross.config import BRANDS, DB_ENABLED
from albatross.enums.enums import MountType
from albatross.models.lens import Lens
from albatross.models.search import SearchResultModel
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.search.query import Search
from albatross.utils import clean_string

log = logging.getLogger(__name__)


class LensService:
    @staticmethod
    def from_model_name(
        model: str,
        brand: Optional[str],
        mount: Optional[MountType],
        repo: AlbatrossRepository,
        db_enabled: bool = DB_ENABLED,
    ) -> Optional[Lens]:
        aperture_min, aperture_max = LensService.get_aperture_values_from_model_name(
            model
        )
        (
            focal_length_min,
            focal_length_max,
        ) = LensService.get_focal_length_values_from_model_name(model)

        lens = Lens(
            brand=brand,
            model=model,
            focal_length_min=focal_length_min,
            focal_length_max=focal_length_max,
            largest_aperture_at_minimum_focal_length=aperture_min,
            largest_aperture_at_maximum_focal_length=aperture_max,
            prime=bool(focal_length_min == focal_length_max),
            mount=mount,
        )

        if db_enabled:
            repo.persist(lens)  # pragma: no cover

        return lens

    @staticmethod
    def get_aperture_values_from_model_name(model: str) -> tuple[float, float]:
        aperture_pattern: str = r"f\/?(\d+(\.\d+)?)(?:-(\d+(\.\d+)?))?"

        match = re.search(aperture_pattern, model)
        if match:
            aperture_min: float = float(match.group(1))  # First aperture value
            if match.group(3):
                aperture_max: float = float(
                    match.group(3)
                )  # Second aperture value (if present)
            else:
                aperture_max = aperture_min

            return aperture_min, aperture_max

        else:
            raise ValueError("No aperture values found in the model name.")

    @staticmethod
    def get_focal_length_values_from_model_name(model: str) -> tuple[float, float]:
        focal_length_pattern: str = r"(\d+)(?:\s*-\s*(\d+))?mm"

        match = re.search(focal_length_pattern, model)
        if match:
            focal_length_min: float = float(match.group(1))
            if match.group(2):
                focal_length_max: float = float(match.group(2))
            else:
                focal_length_max = focal_length_min

            return focal_length_min, focal_length_max

        else:
            raise ValueError("No focal length values found in the model name.")

    @staticmethod
    def from_exif(
        exif_data: Dict[str, Any],
        repo: AlbatrossRepository,
        mount: Optional[MountType] = None,
        camera_brand: Optional[str] = None,
        crop_factor: Optional[float] = None,
        db_enabled: bool = DB_ENABLED,
    ) -> Lens:
        lens_model: str = clean_string(exif_data.get("LensModel", "Unknown Model"))
        lens_brand: str = exif_data.get("LensMake", "Unknown Brand")

        if lens_model != "Unknown Model" and db_enabled:
            if lens := repo.get_lens_by_model(lens_model):  # pragma: no cover
                return lens

        # some lens data comes back as this string, we can assume there is no lens data
        if lens_model == "0.0 mm f/0.0":
            raise ValueError("No lens data found in the EXIF metadata.")

        if lens_brand == "Unknown Brand":
            result: str | None = LensService.attempt_to_get_brand_from_model_name(
                lens_model
            )
            lens_brand = result if result else lens_brand

        if "LensSpecification" in exif_data and len(exif_data["LensSpecification"]) > 3:
            lens_spec: list[Any] = exif_data["LensSpecification"]
            try:
                if type(lens_spec[0]) is list:
                    lens_focal_length_min = float(lens_spec[0][0] / lens_spec[0][1])
                    if crop_factor:  # pragma: no branch
                        lens_focal_length_min *= crop_factor
                else:
                    lens_focal_length_min = float(lens_spec[0])
                    if crop_factor:
                        lens_focal_length_min *= crop_factor
                if type(lens_spec[1]) is list:
                    lens_focal_length_max = float(lens_spec[1][0] / lens_spec[1][1])
                    if crop_factor:  # pragma: no branch
                        lens_focal_length_max *= crop_factor
                else:
                    lens_focal_length_max = float(lens_spec[1])
                    if crop_factor:
                        lens_focal_length_max *= crop_factor
                # FIXME: we should probably be using the crop factor here too
                #  but that's a can of worms I don't want to open without discussion
                if type(lens_spec[2]) is list:
                    lens_max_aperture_at_minimum_fl = float(
                        lens_spec[2][0] / lens_spec[2][1]
                    )
                else:
                    lens_max_aperture_at_minimum_fl = float(lens_spec[2])
                if type(lens_spec[3]) is list:
                    lens_max_aperture_at_max_fl = float(
                        lens_spec[3][0] / lens_spec[3][1]
                    )
                else:
                    lens_max_aperture_at_max_fl = float(lens_spec[3])
            except ZeroDivisionError:
                log.warning("Division by zero error in lens data")
                lens_focal_length_min = lens_focal_length_max = (
                    lens_max_aperture_at_minimum_fl
                ) = lens_max_aperture_at_max_fl = 0.0

            search_model: SearchResultModel | None = None
            if lens_model not in ["Unknown Model", ""]:  # pragma: no cover
                query = lens_model
                if lens_brand != "Unknown Brand":
                    query = f"{lens_brand} {lens_model}"
                elif camera_brand != "unknown brand":
                    query = f"{camera_brand} {lens_model}"
                # We can try to get the model from the search service
                search_model = Search.search_model_via_proxy(query)

            lens = Lens(
                brand=lens_brand,
                model=lens_model,
                focal_length_min=(
                    lens_focal_length_min
                    if not math.isnan(lens_focal_length_min.real)
                    else None
                ),
                focal_length_max=(
                    lens_focal_length_max
                    if not math.isnan(lens_focal_length_max.real)
                    else None
                ),
                largest_aperture_at_minimum_focal_length=(
                    lens_max_aperture_at_minimum_fl
                    if lens_max_aperture_at_minimum_fl
                    else None
                ),
                largest_aperture_at_maximum_focal_length=(
                    lens_max_aperture_at_max_fl if lens_max_aperture_at_max_fl else None
                ),
                prime=bool(lens_focal_length_min == lens_focal_length_max),
                mount=mount if mount else None,
                crop_factor=crop_factor,
                mpb_model_id=getattr(search_model, "model_id", None),
                price=getattr(search_model, "price", None),
                image_link=getattr(search_model, "image_link", None),
                model_url_segment=getattr(search_model, "model_url_segment", None),
                mpb_model=getattr(search_model, "model_name", None),
            )

            if (
                db_enabled
                and lens_model != "Unknown Model"
                and lens_max_aperture_at_minimum_fl
                and lens_focal_length_min
            ):
                try:  # pragma: no cover
                    # only persist lenses that have a model, aperture and focal length
                    repo.persist(lens)
                except sqlite3.IntegrityError as e:  # pragma: no cover
                    log.warning(f"Could not persist lens {lens.model} in database: {e}")

            return lens

        elif "LensModel" in exif_data:  # pragma: no cover
            return LensService.from_model_name(
                brand=lens_brand,
                model=lens_model,
                mount=mount if mount else None,
                db_enabled=db_enabled,
                repo=repo,
            )

        else:
            raise ValueError("No lens data found in the EXIF metadata.")

    @staticmethod
    def attempt_to_get_brand_from_model_name(model: str) -> Optional[str]:
        # FIXME: this isn't perfect. if the model name contains multiple brands it just
        #  returns the first one it finds.
        for brand in BRANDS:
            if brand in model.lower():
                return brand  # type: ignore

        return None
