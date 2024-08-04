import requests
from os import getenv

from src import crud, schemas
from src.common import get_db, get_random_hash

db = get_db()

def user_gen():
    return requests.post('http://127.0.0.1:8000/auth/', json={
        "login": get_random_hash(),
        "password": "string"
    }).json()

req1 = user_gen() # gen user for test
req2 = user_gen() # gen user for test
user1, token1, user2, token2 = schemas.User(**req1["user"]), req1["token"], schemas.User(**req2["user"]), req2["token"]

task1 = None
task2 = None # deleted in below
permisson_id = None

def test_user_not_same():
    assert (user1 != user2) and (token1 != token2)

def test_wrong_auth():
    assert requests.post('http://127.0.0.1:8000/auth/', json={
        "login": user1.login,
        "password": "string2"
    }).status_code == 400

def test_authed_endpoint_without_token():
    assert requests.get('http://127.0.0.1:8000/task/').status_code == 401

def test_task_creation():
    global task1, task2
    task1 = schemas.Task(**requests.post('http://127.0.0.1:8000/task/', headers={
        "Authorization" : token1
    }, json={
        "title" : "Test QUQUQUQU"
    }).json())

    task2 = schemas.Task(**requests.post('http://127.0.0.1:8000/task/',
        headers={"Authorization" : token2}, 
        json={"title" : "Test QUQUQUQU"}
    ).json())

def test_access_to_own_task():
    assert requests.get(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token1}, 
    ).status_code == 200

def test_access_to_not_own_task():
    assert requests.get(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
    ).status_code == 400

def test_update_own_task():
    global task1 
    old_title = task1.title
    task1 = schemas.Task(**requests.put(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token1}, 
        json={"title" : "Test No Qu :("}
    ).json())
    assert old_title != task1.title

def test_access_to_update_not_own_task():
    assert requests.put(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
        json={"title" : "No access to task"}
    ).status_code == 400

def test_change_own_task_delete_status():
    assert requests.delete(f'http://127.0.0.1:8000/task/{task2.id}',
        headers={"Authorization" : token2},
        params={"is_deleted": "true"} 
    ).status_code == 204

def test_change_not_own_task_delete_status():
    assert requests.delete(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2},
        params={"is_deleted": "true"} 
    ).status_code == 400

def test_add_permission_for_not_own_task():
    assert requests.post(f'http://127.0.0.1:8000/permisson/',
        headers={"Authorization" : token1},
        params={"task_id": task2.id, "user_id": user1.id},
        json={"is_permite_to_write": True}
    ).status_code == 400

def test_add_permission_for_task():
    global permisson_id
    tasks_without_shared = requests.get(f'http://127.0.0.1:8000/task/',
        headers={"Authorization" : token2}, 
    ).json()
    permisson_res = requests.post(f'http://127.0.0.1:8000/permisson/',
        headers={"Authorization" : token1},
        params={"task_id": task1.id, "user_id": user2.id},
        json={"is_permite_to_write": True}
    ).json()
    permisson_id = permisson_res["id"] 
    tasks_with_shared = requests.get(f'http://127.0.0.1:8000/task/',
        headers={"Authorization" : token2}, 
    ).json()
    assert len(tasks_without_shared["shared_tasks"]) != len(tasks_with_shared["shared_tasks"])

def test_update_shared_task():
    global task1
    old_title = task1.title
    task1 = schemas.Task(**requests.put(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
        json={"title" : "Of course Qu is here! :)"}
    ).json())
    assert old_title != task1.title

def test_change_permission():
    task_before_change = requests.get(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
    ).json()
    requests.put(f'http://127.0.0.1:8000/permisson/{permisson_id}',
        headers={"Authorization" : token1},
        json={"is_permite_to_write": False}
    )
    task_after_change = requests.get(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
    ).json()
    assert task_before_change["share_data"]["is_permite_to_write"] != task_after_change["share_data"]["is_permite_to_write"]

def test_update_now_not_shared_task():
    global task1
    assert requests.put(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
        json={"title" : "This Qu change not Working :^"}
    ).status_code == 400

def test_change_not_own_permission():
    assert requests.put(f'http://127.0.0.1:8000/permisson/{permisson_id}',
        headers={"Authorization" : token2},
        json={"is_permite_to_write": False}
    ).status_code == 400

def test_delete_permission():
    tasks_without_shared = requests.get(f'http://127.0.0.1:8000/task/',
        headers={"Authorization" : token2}, 
    ).json()
    requests.delete(f'http://127.0.0.1:8000/permisson/{permisson_id}',
        headers={"Authorization" : token1},
        params={"is_deleted": "true"},
    )
    tasks_with_shared = requests.get(f'http://127.0.0.1:8000/task/',
        headers={"Authorization" : token2}, 
    ).json()
    assert len(tasks_without_shared["shared_tasks"]) != len(tasks_with_shared["shared_tasks"])

def test_delete_not_own_permission():
    assert requests.delete(f'http://127.0.0.1:8000/permisson/{permisson_id}',
        headers={"Authorization" : token2},
        params={"is_deleted": "true"},
    ).status_code == 400

def test_get_all_permissons():
    assert requests.get(f'http://127.0.0.1:8000/permisson/',
        headers={"Authorization" : token2},
    ).status_code == 200