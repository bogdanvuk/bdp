from bdp.prototype import CallablePrototype

def test_arraws_meta():
    p1 = CallablePrototype(a=0, b=1)
    p2 = p1(b=2)
    p31 = p2(b=3)
    p32 = p2(a=1, b=4)

    assert p2.b == 2
    assert p2.a == p1.a

    assert p31.b == 3
    assert p31.a == p1.a

    assert p32.a == 1
    assert p32.b == 4

    p1.a = 2
    p1.b = 5

    assert p2.b == 2
    assert p2.a == p1.a

    assert p31.b == 3
    assert p31.a == p1.a

    assert p32.a == 1
    assert p32.b == 4
