from flask.testing import FlaskClient


def test_index(client: FlaskClient) -> None:
    # Given a client and the root URL
    url: str = "/"

    # When the index page is requested
    response = client.get(url)

    # Then the response should be OK
    assert response.status_code == 200
