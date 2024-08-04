from src import crud, schemas
from src.common import get_db

db = get_db()

def test_get_user():
    assert crud.get_user_by_login(db=next(db), login="test") is not None 

# def test_create_user():
#     user = schemas.UserSign(
#         login="test",
#         password="quququ"
#     )
#     assert crud.create_user(db=next(db), user=user) is not None