from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.recommendations import Recommendations
from albatross.models.results import Results
from albatross.repository.base_repository import AlbatrossRepository


def test_get_camera_by_model(repository: AlbatrossRepository, camera: Camera) -> None:
    # Given: A camera exists in the database
    repository.persist(camera)

    # When: Retrieving the camera by model
    result = repository.get_camera_by_model(camera.model)

    # Then: The correct camera is returned
    assert result is not None
    assert result.model == camera.model


def test_get_lens_by_model(repository: AlbatrossRepository, lens: Lens) -> None:
    # Given: A lens exists in the database
    repository.persist(lens)

    # When: Retrieving the lens by model
    result = repository.get_lens_by_model(lens.model)

    # Then: The correct lens is returned
    assert result is not None
    assert result.model == lens.model
    assert result.brand == lens.brand


def test_persist_camera(repository: AlbatrossRepository, camera: Camera) -> None:
    # Given: A new camera object
    # When: Persisting the camera
    camera_id = repository.persist(camera)

    # Then: The camera is saved and has an ID
    assert camera_id is not None


def test_persist_lens(repository: AlbatrossRepository, lens: Lens) -> None:
    # Given: A new lens object
    # When: Persisting the lens
    lens_id = repository.persist(lens)

    # Then: The lens is saved and has an ID
    assert lens_id is not None


def test_persist(
    repository: AlbatrossRepository,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A recommendations object
    # When: Persisting the recommendation
    recommendation = repository.persist(recommendations_without_llm_response)

    # Then: The recommendation is saved and has an ID
    assert recommendation is not None
    assert recommendation.id


def test_get_recommendation(
    repository: AlbatrossRepository,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A recommendation exists in the database
    recommendation = repository.persist(recommendations_without_llm_response)

    # When: Retrieving the recommendation by ID
    result = repository.get_recommendation(recommendation.id)

    # Then: The correct recommendation is returned
    assert result is not None
    assert result.id == recommendation.id


def test_persist_and_retrieve_full_recommendation(
    repository: AlbatrossRepository,
    recommendations_with_llm_response: Recommendations,
) -> None:
    # Given: a recommendations object with results and llm data
    persisted = repository.persist(recommendations_with_llm_response)

    # When: retrieving from the database
    retrieved = repository.get_recommendation(persisted.id)

    # Then: the data should be intact
    assert retrieved is not None
    assert retrieved.results.metrics.total_images == (
        recommendations_with_llm_response.results.metrics.total_images
    )
    assert (
        retrieved.llm_lens_recommendation
        == recommendations_with_llm_response.llm_lens_recommendation
    )
    assert (
        retrieved.llm_camera_recommendation
        == recommendations_with_llm_response.llm_camera_recommendation
    )


def test_persist_without_camera_and_lenses(
    repository: AlbatrossRepository,
    results: Results,
) -> None:
    """Persisting a recommendation lacking related objects should succeed."""

    recommendation = Recommendations(
        primary_camera=None,
        primary_mount_lenses=[],
        current_widest_aperture=None,
        favourite_focal_length=None,
        recommended_aperture=None,
        recommended_focal_length=None,
        recommendation_statement="",
        results=results,
    )

    persisted = repository.persist(recommendation)
    assert persisted.primary_camera is None
    assert persisted.primary_mount_lenses == []

    retrieved = repository.get_recommendation(persisted.id)
    assert retrieved is not None
    assert retrieved.primary_camera is None
    assert retrieved.primary_mount_lenses == []


def test_get_recommendation_handles_missing_json(
    repository: AlbatrossRepository,
    recommendations_without_llm_response: Recommendations,
) -> None:
    """get_recommendation should cope with missing json fields."""

    persisted = repository.persist(recommendations_without_llm_response)

    with repository.session_scope() as session:
        rec = session.get(Recommendations, persisted.id)
        rec.results_json = None
        rec.llm_camera_recommendation_json = None
        rec.llm_lens_recommendation_json = None
        session.add(rec)

    retrieved = repository.get_recommendation(persisted.id)
    assert retrieved is not None
    assert getattr(retrieved, "results", None) is None
    assert getattr(retrieved, "llm_camera_recommendation", None) is None
    assert getattr(retrieved, "llm_lens_recommendation", None) is None
