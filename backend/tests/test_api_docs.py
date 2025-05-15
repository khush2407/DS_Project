import pytest
from fastapi.testclient import TestClient
from app import app
import json

def test_openapi_schema_exists():
    """Test that OpenAPI schema is properly generated"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    
    # Verify basic schema structure
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    assert "components" in schema

def test_all_endpoints_documented():
    """Test that all API endpoints have documentation"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # List of expected endpoints
    expected_endpoints = [
        "/analyze",
        "/api/activities",
        "/api/activities/{activity_id}",
        "/api/activities/favorites",
        "/api/activities/history",
        "/api/activities/{activity_id}/progress",
        "/api/activities/{activity_id}/complete",
        "/api/activities/recommendations",
        "/api/activities/{activity_id}/share",
        "/session/create",
        "/session/{session_id}",
        "/session/test/preferences",
        "/health"
    ]
    
    # Verify each endpoint exists in schema
    for endpoint in expected_endpoints:
        assert endpoint in schema["paths"], f"Endpoint {endpoint} not documented"

def test_endpoint_parameters_documented():
    """Test that all endpoint parameters are documented"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test analyze endpoint parameters
    analyze_endpoint = schema["paths"]["/analyze"]
    assert "post" in analyze_endpoint
    assert "requestBody" in analyze_endpoint["post"]
    assert "content" in analyze_endpoint["post"]["requestBody"]
    assert "application/json" in analyze_endpoint["post"]["requestBody"]["content"]
    
    # Test activity progress endpoint parameters
    progress_endpoint = schema["paths"]["/api/activities/{activity_id}/progress"]
    assert "post" in progress_endpoint
    assert "parameters" in progress_endpoint["post"]
    assert any(param["name"] == "activity_id" for param in progress_endpoint["post"]["parameters"])

def test_response_schemas_documented():
    """Test that all response schemas are documented"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test analyze endpoint response
    analyze_endpoint = schema["paths"]["/analyze"]
    assert "responses" in analyze_endpoint["post"]
    assert "200" in analyze_endpoint["post"]["responses"]
    assert "content" in analyze_endpoint["post"]["responses"]["200"]
    assert "application/json" in analyze_endpoint["post"]["responses"]["200"]["content"]
    
    # Test recommendations endpoint response
    recommendations_endpoint = schema["paths"]["/api/activities/recommendations"]
    assert "responses" in recommendations_endpoint["get"]
    assert "200" in recommendations_endpoint["get"]["responses"]
    assert "content" in recommendations_endpoint["get"]["responses"]["200"]
    assert "application/json" in recommendations_endpoint["get"]["responses"]["200"]["content"]

def test_error_responses_documented():
    """Test that error responses are documented"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test common error responses
    error_codes = ["400", "401", "403", "404", "429", "500"]
    
    for endpoint in schema["paths"].values():
        for method in endpoint.values():
            if "responses" in method:
                for code in error_codes:
                    assert code in method["responses"], f"Error response {code} not documented"

def test_security_schemes_documented():
    """Test that security schemes are documented"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Verify security schemes
    assert "components" in schema
    assert "securitySchemes" in schema["components"]
    assert "bearerAuth" in schema["components"]["securitySchemes"]
    
    # Verify bearer auth scheme
    bearer_auth = schema["components"]["securitySchemes"]["bearerAuth"]
    assert bearer_auth["type"] == "http"
    assert bearer_auth["scheme"] == "bearer"
    assert bearer_auth["bearerFormat"] == "JWT"

def test_examples_provided():
    """Test that examples are provided for request/response bodies"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test analyze endpoint examples
    analyze_endpoint = schema["paths"]["/analyze"]
    assert "examples" in analyze_endpoint["post"]["requestBody"]["content"]["application/json"]
    
    # Test activity progress endpoint examples
    progress_endpoint = schema["paths"]["/api/activities/{activity_id}/progress"]
    assert "examples" in progress_endpoint["post"]["requestBody"]["content"]["application/json"]

def test_tags_used():
    """Test that endpoints are properly tagged"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    expected_tags = [
        "Activities",
        "Emotions",
        "Sessions",
        "Health"
    ]
    
    # Verify tags exist
    assert "tags" in schema
    for tag in expected_tags:
        assert any(t["name"] == tag for t in schema["tags"])
    
    # Verify endpoints use tags
    for endpoint in schema["paths"].values():
        for method in endpoint.values():
            if "tags" in method:
                assert any(tag in method["tags"] for tag in expected_tags)

def test_descriptions_provided():
    """Test that descriptions are provided for all components"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Verify endpoint descriptions
    for path, endpoint in schema["paths"].items():
        for method, details in endpoint.items():
            assert "description" in details, f"Missing description for {method.upper()} {path}"
    
    # Verify schema descriptions
    for name, component in schema["components"]["schemas"].items():
        assert "description" in component, f"Missing description for schema {name}" 