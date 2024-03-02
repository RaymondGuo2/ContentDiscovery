from app import app


def test_index():
    client = app.test_client()
    response = client.get('/shows')
    assert response.status_code == 200
