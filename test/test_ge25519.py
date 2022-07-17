"""
Test suite containing functional unit tests for the exported primitives and
classes.
"""
# pylint: disable=missing-function-docstring
from __future__ import annotations
from typing import Union, Optional, Callable, Iterable
from unittest import TestCase
from parts import parts
from bitlist import bitlist
from fountains import fountains

from ge25519.ge25519 import * # pylint: disable=wildcard-import,unused-wildcard-import

# Constant for the number of input-output pairs to include in each test.
TRIALS_PER_TEST = 256

def check_or_generate(
        testcase: TestCase,
        fs: Union[Iterable[int], Iterable[bool]],
        bits: Optional[str]
    ) -> Optional[str]:
    """
    Wrapper that enables switching between performing a test or
    generating specifications compatible with :obj:`fountains`.
    """
    if bits is None:
        return bitlist(list(fs)).hex() # Return target bits for this test.

    testcase.assertTrue(all(fs)) # Check that all tests succeeded.
    return None # Do not return a test input.

def check_or_generate_operation(
        testcase: TestCase,
        fun: Union[Callable[[bytes], bytes], Callable[[bytes], bitlist]],
        lengths: Iterable[int],
        bits: Optional[str]
    ):
    """
    Wrapper that enables switching between performing a test or
    generating specifications compatible with :obj:`fountains`.
    """
    fs = fountains( # Generate the input bit stream.
        sum(lengths),
        seed=bytes(0), # This is also the default; explicit for clarity.
        limit=min(TRIALS_PER_TEST, (len(bits) * 4) if bits is not None else 256),
        bits=bits[:(TRIALS_PER_TEST // 4)] if bits is not None else None,
        function=fun
    )
    return check_or_generate(testcase, fs, bits)

class Test_ge25519(TestCase):
    """
    Tests for all class methods.
    """
    def test_is_canonical(
            self,
            bits='ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        ):
        def fun(bs):
            return bitlist([ge25519.is_canonical(bs)])
        return check_or_generate_operation(self, fun, [32], bits)

    def test_has_small_order(
            self,
            bits='0000000000000000000000000000000000000000000000000000000000000000'
        ):
        def fun(bs):
            return bitlist([ge25519.has_small_order(bs)])
        return check_or_generate_operation(self, fun, [32], bits)

    def test_is_on_curve(
            self,
            bits='4dbd939e58fc59860feac3f1e63fa428519472415073f2ca850b662c25bbd05b'
        ):
        def fun(bs):
            return bitlist([ge25519_p3.from_bytes(bs).is_on_curve()])
        return check_or_generate_operation(self, fun, [32], bits)

    def test_is_on_main_subgroup(
            self,
            bits='4020000200040800090081804410040010003000000110028100040824020010'
        ):
        def fun(bs):
            return bitlist([ge25519_p3.from_bytes(bs).is_on_main_subgroup()])
        return check_or_generate_operation(self, fun, [32], bits)

    def test_from_p3(
            self,
            bits='37b1cbf6ef16f5a00e5470ecc6b4c93b20893bb308962300b2081e8aa7e8702a'
        ):
        def fun(bs):
            p1p1 = ge25519_p2.from_p3(ge25519_p3.from_bytes(bs)).dbl()
            return ge25519_p3.from_p1p1(p1p1).to_bytes()
        return check_or_generate_operation(self, fun, [32], bits)

    def test_dbl(self, bits='37b1cbf6ef16f5a00e5470ecc6b4c93b20893bb308962300b2081e8aa7e8702a'):
        def fun(bs):
            p1p1 = ge25519_p1p1.dbl(ge25519_p3.from_bytes(bs))
            return ge25519_p3.from_p1p1(p1p1).to_bytes()
        return check_or_generate_operation(self, fun, [32], bits)

    def test_mul_l(
            self,
            bits='22b0eb2b1d06d970c1dba41540d9255228625c871e2c4d1655c784167f43b104'
        ):
        fun = lambda bs: ge25519_p3.from_bytes(bs).mul_l().to_bytes()
        return check_or_generate_operation(self, fun, [32], bits)

    def test_scalar_mult_base(
            self,
            bits='ec909cfc24cf1721d21dda8b350dafc277f29470ea03b5560e19d47f9e668f09'
        ):
        def fun(bs):
            return ge25519_p3.scalar_mult_base(bs).to_bytes()
        return check_or_generate_operation(self, fun, [32], bits)

    def test_scalar_mult(
            self,
            bits='242fd0294a256e12f5a82955d223baeab5a04b7db5f9d46552f34b08a858e9a8'
        ):
        def fun(bs):
            (bs1, bs2) = parts(bs, length=32)
            return ge25519_p3.from_bytes(bs1).scalar_mult(bs2).to_bytes()
        return check_or_generate_operation(self, fun, [32, 32], bits)

    def test_from_uniform(
            self,
            bits='fa3b6f0f3a7222b45d44ac42eb03f7beec0039f61f0814a4f3a2f178e44fd26d'
        ):
        fun = lambda bs: ge25519_p3.from_uniform(bs).to_bytes()
        return check_or_generate_operation(self, fun, [32], bits)

    def test_from_hash_ristretto255(
            self,
            bits='baf12de24e54deae0aa116816bf5eee23b1168c78e892372e08a9884de9d4c1b'
        ):
        return check_or_generate_operation(self, ge25519_p3.from_hash_ristretto255, [64], bits)

    def test_from_bytes_ristretto255(
            self,
            bits='80200300300085008000260000000800008a006000800c041040800420130182'
        ):
        def fun(bs):
            p3 = ge25519_p3.from_bytes_ristretto255(bs)
            return p3.to_bytes() if p3 is not None else bitlist([0])
        return check_or_generate_operation(self, fun, [32], bits)

    def test_to_bytes_ristretto255(
            self,
            bits='4240c56beef1f9d6b8dfe7856fbae94999b8bc5e27b350f01ee5db7ee2b5ad45'
        ):
        fun = lambda bs: ge25519_p3.from_bytes(bs).to_bytes_ristretto255()
        return check_or_generate_operation(self, fun, [32], bits)

    def test_add(self, bits='f9a298467cf064593c9998917f3e2b1fb00f738e92e3c3187ce9986b70389245'):
        def fun(bs):
            (bs1, bs2) = parts(bs, length=32)
            p3 = ge25519_p3.from_bytes(bs1)
            cached = ge25519_cached.from_p3(ge25519_p3.from_bytes(bs2))
            return ge25519_p3.from_p1p1((ge25519_p1p1.add(p3, cached))).to_bytes()
        return check_or_generate_operation(self, fun, [32, 32], bits)

    def test_madd(self, bits='4b4d0b3a86c787f295d53e4a42656ba2ba6123f14a819b3c2d544f574d0030bb'):
        def fun(bs):
            (p3, i, j) = (ge25519_p3.from_bytes(bs[:32]), bs[32]%32, (bs[32]//32)%8)
            # pylint: disable=protected-access,unsubscriptable-object
            p2 = ge25519_p2.from_p1p1(ge25519_p1p1.madd(p3, ge25519_precomp._base[i][j]))
            return ge25519_p3.from_p1p1(p2.dbl()).to_bytes()
        return check_or_generate_operation(self, fun, [32, 1], bits)

    def test_sub(self, bits='c349d67e124af7943ee8ceeaf774c43fca0472c245dad7e52585c62e71343082'):
        def fun(bs):
            (bs1, bs2) = parts(bs, length=32)
            p3 = ge25519_p3.from_bytes(bs1)
            cached = ge25519_cached.from_p3(ge25519_p3.from_bytes(bs2))
            return ge25519_p3.from_p1p1((ge25519_p1p1.sub(p3, cached))).to_bytes()
        return check_or_generate_operation(self, fun, [32, 32], bits)

    def test_cmov8_base(
            self,
            bits='450fa303840940b93e104413b952865464b0fffc8321b030ac956537029bf61e'
        ):
        def fun(bs):
            (pos, b) = (bs[0] % 32, (bs[0] // 32) % 8)
            precomp = ge25519_precomp._cmov8_base(pos, b) # pylint: disable=protected-access
            return \
                precomp.yplusx.to_bytes() + \
                precomp.yminusx.to_bytes() + \
                precomp.xy2d.to_bytes()
        return check_or_generate_operation(self, fun, [1], bits)

    def test_cmov_cached(
            self,
            bits='2c81a643db31e92474c23b47d5a568fab19b90385855fccbe53fbfcd3ac32e45'
        ):
        def fun(bs):
            ((bs1, bs2), b) = (parts(bs, length=32), bs[-1]%2)
            cached1 = ge25519_cached.from_p3(ge25519_p3.from_bytes(bs1))
            cached2 = ge25519_cached.from_p3(ge25519_p3.from_bytes(bs2))
            cached1._cmov_cached(cached2, b) # pylint: disable=protected-access
            return \
                cached1.YplusX.to_bytes() + \
                cached1.YminusX.to_bytes() + \
                cached1.Z.to_bytes() + \
                cached1.T2d.to_bytes()
        return check_or_generate_operation(self, fun, [32, 32], bits)

if __name__ == '__main__':
    # Generate specifications for tests.
    test_ge25519 = Test_ge25519()
    for m in [m for m in dir(test_ge25519) if m.startswith('test_')]:
        print(m + ': ' + getattr(test_ge25519, m)(bits=None))
