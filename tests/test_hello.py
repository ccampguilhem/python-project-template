#!coding: utf-8
from mylib.hello import hello


def test_hello():
    assert hello("Cédric") == "Hello Cédric!"
    assert hello("") == "Hello !"
