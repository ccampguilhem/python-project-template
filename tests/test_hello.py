#!coding: utf-8
import mylib


def test_hello():
    assert mylib.hello.hello("Cédric") == "Hello Cédric!"
    assert mylib.hello.hello("") == "Hello !"
