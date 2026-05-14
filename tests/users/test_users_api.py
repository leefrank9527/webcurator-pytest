import pytest
from uuid import uuid4

unique_suffix = uuid4().hex[:8]
test_user_name = f"lql_{unique_suffix}"
email = f"{test_user_name}@dia.govt.nz"


def test_get_users(api_client):
    rsp = api_client.get("users")
    assert rsp.ok
    users = rsp.json()
    assert isinstance(users, dict)


def test_get_user_by_id(api_client, current_user):
    if not current_user:
        pytest.skip("No users found, skipping test.")
    user_id = current_user.get("id")
    rsp = api_client.get(f"users/{user_id}")
    assert rsp.ok
    user = rsp.json()
    assert user.get("id") == user_id


def test_add_and_delete_valid_user(api_client):
    new_user = {
        "userName": test_user_name,
        "firstName": "Frank",
        "lastName": "Lee",
        "email": email,
        "agency": "bootstrap",
        "password": "1qaz@WSX",
        "notificationsByEmail": True,
        "tasksByEmail": True,
        "title": "Mr",
        "active": True,
        "externalAuth": False,
        "phone": "02040690298",
        "address": "2B Belize Grove Grenada Village",
        "notifyOnGeneral": True,
        "notifyOnHarvestWarnings": True,
    }
    rsp = api_client.post("users", json=new_user)
    assert rsp.ok, f"status={rsp.status_code}, body={rsp.text}"

    created_user_url = rsp.headers.get("Location")
    assert created_user_url, f"Location header missing. headers={dict(rsp.headers)}"

    created_rsp = api_client.get(created_user_url)
    assert created_rsp.ok, f"status={created_rsp.status_code}, body={created_rsp.text}"

    created = created_rsp.json()
    assert created is not None

    assert (
        created.get("userName") == test_user_name
        or created.get("name") == test_user_name
    )
    assert created.get("email") == email
    assert created.get("firstName") == new_user["firstName"]
    assert created.get("lastName") == new_user["lastName"]
    assert created.get("agency") == new_user["agency"]

    api_client.delete(f"users/{created.get('id')}")
    assert True


def test_update_user(api_client, current_user):
    if not current_user:
        pytest.skip("No users found, skipping test.")
    user_id = current_user.get("id")
    updated_data = {"firstName": "UpdatedFirstName", "lastName": "UpdatedLastName"}
    rsp = api_client.put(f"users/{user_id}", json=updated_data)
    assert rsp.ok, f"status={rsp.status_code}, body={rsp.text}"

    updated_rsp = api_client.get(f"users/{user_id}")
    assert updated_rsp.ok, f"status={updated_rsp.status_code}, body={updated_rsp.text}"
    updated_user = updated_rsp.json()
    assert updated_user.get("firstName") == updated_data["firstName"]
    assert updated_user.get("lastName") == updated_data["lastName"]
