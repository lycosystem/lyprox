"""Test some utility functions."""

from lyprox.dataexplorer.utils import get_nested_fields
from pydantic import BaseModel
import pytest


class NestedModel(BaseModel):
    field_a: int
    field_b: str


class MainModel(BaseModel):
    nested: NestedModel
    field_c: float


def test_get_nested_fields():
    fields = get_nested_fields(MainModel)
    assert "nested" in fields
    assert "field_c" in fields
    assert "field_a" in fields["nested"]
    assert "field_b" in fields["nested"]
