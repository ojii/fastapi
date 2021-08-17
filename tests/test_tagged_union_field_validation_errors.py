from typing import Literal, Union

from fastapi import FastAPI
from pydantic import BaseModel, conint
from starlette.testclient import TestClient

app = FastAPI()


class A(BaseModel):
    tag: Literal["a"]


class B(BaseModel):
    tag: Literal["b"]
    value: conint(ge=0, le=1)


class Item(BaseModel):
    value: Union[A, B]


@app.post("/items/")
def save_union_body(item: Item):
    return {"item": item}


client = TestClient(app)


def test_post_a():
    response = client.post("/items/", json={"value": {"tag": "a"}})
    assert response.status_code == 200, response.text
    assert response.json() == {"item": {"value": {"tag": "a"}}}


def test_post_b():
    response = client.post("/items/", json={"value": {"tag": "b", "value": 1}})
    assert response.status_code == 200, response.text
    assert response.json() == {"item": {"value": {"tag": "b", "value": 1}}}


def test_post_b_invalid_value():
    response = client.post("/items/", json={"value": {"tag": "b", "value": 2}})
    assert response.status_code == 422, response.text
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "value", "value"],
                "msg": "ensure this value is less than or equal to 1",
                "type": "value_error.number.not_le",
                "ctx": {"limit_value": 1},
            },
        ]
    }
