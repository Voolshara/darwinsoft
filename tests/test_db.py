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
task2 = None

def test_user_not_same():
    assert (user1 != user2) and (token1 != token2)

def test_wrong_auth():
    assert requests.post('http://127.0.0.1:8000/auth/', json={
        "login": user1.login,
        "password": "string2"
    }).status_code == 400

def test_authed_route_without_token():
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

def test_assecc_to_own_task():
    assert requests.get(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token1}, 
    ).status_code == 200

def test_assecc_to_not_own_task():
    assert requests.get(f'http://127.0.0.1:8000/task/{task1.id}',
        headers={"Authorization" : token2}, 
    ).status_code == 400

# def test_get_user():
    # assert schemas.User(**crud.get_user_by_login(db=next(db), login=user1.login)) == user1 

# def test_create_and_read_tasks():
    # task1 = requests.post("")

# def test_create_user():
#     user = schemas.UserSign(
#         login="test",
#         password="quququ"
#     )
#     assert crud.create_user(db=next(db), user=user) is not None