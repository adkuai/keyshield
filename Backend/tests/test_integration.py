import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_complete_api_lifecycle():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Test User Signup Registration
        signup_res = await ac.post("/api/auth/register", json={"email": "integration@test.com", "password": "secure_password_string"})
        assert signup_res.status_code == 201
        
        # 2. Test User Session Token Generation Form Login
        login_res = await ac.post("/api/auth/login", data={"username": "integration@test.com", "password": "secure_password_string"})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test Project Provisioning Pipeline Creation
        proj_res = await ac.post("/api/projects", json={"name": "Test Suite Engine", "rate_limit_rpm": 5}, headers=headers)
        assert proj_res.status_code == 201
        p_id = proj_res.json()["id"]
        
        # 4. Test Key Generation Creation Inside Context Module
        key_res = await ac.post(f"/api/projects/{p_id}/keys", json={"name": "QA Key Token Instance", "environment": "Production", "scopes": ["read", "write"]}, headers=headers)
        assert key_res.status_code == 201
        raw_token = key_res.json()["raw_key"]
        
        # 5. Test Accessing Protected Gateways Using Valid Scopes Check
        gate_headers = {"X-API-Key": raw_token}
        gate_res = await ac.get("/api/v1/products", headers=gate_headers)
        assert gate_res.status_code == 200
