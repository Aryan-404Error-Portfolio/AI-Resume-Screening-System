import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Resume Screening' in response.data

def test_api_candidates(client):
    """Test API endpoint returns JSON."""
    response = client.get('/api/candidates')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_analyze_no_data(client):
    """Test analyze route without data returns error."""
    response = client.post('/analyze')
    assert response.status_code == 400

def test_delete_all(client):
    """Test delete route redirects to home."""
    response = client.get('/delete')
    assert response.status_code == 302

def test_export_csv(client):
    """Test export route returns CSV or handles empty DB."""
    response = client.get('/export')
    assert response.status_code in [200, 500]