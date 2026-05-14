import os
from dotenv import load_dotenv
import pytest
import requests


def running_in_container():
    # Docker
    if os.path.exists("/.dockerenv"):
        return True
    # Podman
    if os.path.exists("/run/.containerenv"):
        return True
    # Check cgroups for hints
    try:
        with open("/proc/1/cgroup", "rt") as f:
            for line in f:
                if any(x in line for x in ("docker", "kubepods", "podman", "libpod")):
                    return True
    except FileNotFoundError:
        pass
    return False


if not running_in_container():
    from dotenv import load_dotenv

    load_dotenv()


@pytest.fixture(scope="session")
def token():
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8080/wct")

    rsp = requests.post(
        f"{BASE_URL}/auth/v1/token",
        data={"username": USERNAME, "password": PASSWORD},
    )
    rsp.raise_for_status()
    token = rsp.text
    yield token


class ApiClient(requests.Session):
    def __init__(self, base_url: str, token: str):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": token})

    def request(self, method, url, **kwargs):
        if url.startswith("http://") or url.startswith("https://"):
            request_url = url
        else:
            request_url = f"{self.base_url}/api/v1/{url}"
        return super().request(method, request_url, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, json=None, **kwargs):
        return self.request("POST", url, json=json, **kwargs)

    def put(self, url, json=None, **kwargs):
        return self.request("PUT", url, json=json, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)


@pytest.fixture(scope="session")
def api_client(token):
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8080/wct")
    yield ApiClient(base_url=BASE_URL, token=token)


@pytest.fixture(scope="session")
def current_user(api_client):
    rsp = api_client.get("users")
    rsp.raise_for_status()
    rsp_dict = rsp.json()
    users = rsp_dict.get("users", [])
    if not users:
        yield None
    else:
        USERNAME = os.getenv("USERNAME")
        for user in users:
            if user.get("name") == USERNAME:
                yield user
                break
        else:
            yield None
