"""Group element data structure and operations.

Native Python implementation of Ed25519 group elements and
operations.
"""

from __future__ import annotations
from typing import Sequence
from fe25519 import *
import doctest

def _signed_char(c):
    return (c - 256) if c >= 128 else ((c + 256) if c < -128 else c)

class Ge25519Error(Exception):
    """A general-purpose catch-all for any usage error."""

    def __init__(self, message):
        super(Ge25519Error, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)

class ge25519():
    """
    Class for group elements.
    """

    @staticmethod
    def is_canonical(s):
        c = (s[31] & 127) ^ 127
        for i in range(30, 0, -1):
            c |= s[i] ^ 255;

        c = (((c - 1)%(2**32)) >> 8) % (2**8)
        d = (((237 - 1 - s[0])%(2**32)) >> 8) % (2**8)

        return 1 - (c & d & 1)

    @staticmethod
    def has_small_order(s):
        # Incomplete.
        return 0

class ge25519_p2(ge25519):
    def __init__(self: ge25519_p2, X: fe25519, Y: fe25519, Z: fe25519):
        self.X = X
        self.Y = Y
        self.Z = Z

    @staticmethod
    def from_p3(p: ge25519_p3) -> ge25519_p2:
        return ge25519_p2(p.X.copy(), p.Y.copy(), p.Z.copy())

    @staticmethod
    def from_p1p1(p: ge25519_p1p1) -> ge25519_p2:
        return ge25519_p2(p.X * p.T, p.Y * p.Z, p.Z * p.T)

    def dbl(self: ge25519_p2) -> ge25519_p2: # ge25519_p2_dbl()
        p = self
        r = ge25519_p1p1(p.X**2, p.X + p.Y, p.Y**2, p.Z.sq2())
        t0 = r.Y ** 2
        r.Y = r.Z + r.X
        r.Z = r.Z - r.X
        r.X = t0 - r.Y
        r.T = r.T - r.Z
        return r

class ge25519_p3(ge25519):
    def __init__(\
            self: ge25519_p3, 
            X: fe25519 = None, 
            Y: fe25519 = None, 
            Z: fe25519 = None,
            T: fe25519 = None, 
            root_check: bool = None
        ):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.T = T
        self.root_check = root_check

    @staticmethod
    def zero() -> ge25519_p3:
        return ge25519_p3(fe25519.zero(), fe25519.one(), fe25519.one(), fe25519.zero())

    def is_on_curve(self: ge25519_p3) -> int:
        d = fe25519([929955233495203, 466365720129213, 1662059464998953, 2033849074728123, 1442794654840575])
        x2 = self.X ** 2
        y2 = self.Y ** 2
        z2 = self.Z ** 2
        t0 = y2 - x2
        t0 = t0 * z2

        t1 = x2 * y2
        t1 = t1 * d
        z4 = z2 ** 2
        t1 = t1 + z4
        t0 = t0 - t1

        return t0.is_zero()

    def is_on_main_subgroup(self: ge25519_p3) -> int:
        #ge25519_p3 pl;
        #ge25519_mul_l(&pl, p);
        #return fe25519_iszero(pl.X);
        return 1

    def dbl(self: ge25519_p3) -> ge25519_p3:
        return ge25519_p2.from_p3(self).dbl()

    def scalar_mult(self: ge25519_p3, a: Sequence[int]) -> ge25519_p3:
        p = self
        pi = [None]*8 # ge25519_cached[8]

        pi[1 - 1] = ge25519_cached.from_p3(p) # p

        t2 = p.dbl()
        p2 = ge25519_p3.from_p1p1(t2)
        pi[2 - 1] = ge25519_cached.from_p3(p2) # 2p = 2*p

        t3 = ge25519_p1p1.add(p, pi[2 - 1])
        p3 = ge25519_p3.from_p1p1(t3)
        pi[3 - 1] = ge25519_cached.from_p3(p3) # 3p = 2p+p

        t4 = p2.dbl()
        p4 = ge25519_p3.from_p1p1(t4)
        pi[4 - 1] = ge25519_cached.from_p3(p4) # 4p = 2*2p

        t5 = ge25519_p1p1.add(p, pi[4 - 1])
        p5 = ge25519_p3.from_p1p1(t5)
        pi[5 - 1] = ge25519_cached.from_p3(p5) # 5p = 4p+p

        t6 = p3.dbl()
        p6 = ge25519_p3.from_p1p1(t6)
        pi[6 - 1] = ge25519_cached.from_p3(p6) # 6p = 2*3p

        t7 = ge25519_p1p1.add(p, pi[6 - 1])
        p7 = ge25519_p3.from_p1p1(t7)
        pi[7 - 1] = ge25519_cached.from_p3(p7) # 7p = 6p+p

        t8 = p4.dbl()
        p8 = ge25519_p3.from_p1p1(t8)
        pi[8 - 1] = ge25519_cached.from_p3(p8) # 8p = 2*4p

        e = [None]*64 # signed chars
        for i in range(32):
            e[2 * i + 0] = (a[i] >> 0) & 15
            e[2 * i + 1] = (a[i] >> 4) & 15
        # each e[i] is between 0 and 15
        # e[63] is between 0 and 7

        carry = 0 # signed char
        for i in range(63):
            e[i] = _signed_char(e[i] + carry) # signed char
            carry = _signed_char(e[i] + 8) # signed char
            carry = _signed_char(carry >> 4) # signed char
            e[i] = _signed_char(e[i] - (_signed_char(carry * (1 << 4)))) # signed char   e[i] -= carry * ((signed char) 1 << 4)
        e[63] = _signed_char(e[63] + carry)
        # each e[i] is between -8 and 8

        h = ge25519_p3.zero()

        for i in range(63, 0, -1):
            t = ge25519_cached.cmov8_cached(pi, e[i])

            r = ge25519_p1p1.add(h, t)
            s = ge25519_p2.from_p1p1(r)
            r = s.dbl()
            s = ge25519_p2.from_p1p1(r)
            r = s.dbl()
            s = ge25519_p2.from_p1p1(r)
            r = s.dbl()
            s = ge25519_p2.from_p1p1(r)
            r = s.dbl()

            h = ge25519_p3.from_p1p1(r) # *16

        t = ge25519_cached.cmov8_cached(pi, e[0])
        r = ge25519_p1p1.add(h, t)
        return ge25519_p3.from_p1p1(r)

    @staticmethod
    def from_p1p1(p: ge25519_p1p1) -> ge25519_p3:
        return ge25519_p3(p.X * p.T, p.Y * p.Z, p.Z * p.T, p.X * p.Y)

    @staticmethod
    def from_bytes(bs: bytes) -> ge25519_p3:
        h = ge25519_p3()
        d = fe25519([929955233495203, 466365720129213, 1662059464998953, 2033849074728123, 1442794654840575])
        sqrtm1 = fe25519([1718705420411056, 234908883556509, 2233514472574048, 2117202627021982, 765476049583133])

        h.Y = fe25519.from_bytes(bs)
        h.Z = fe25519.one()
        u = h.Y ** 2
        v = u * d
        u = u - h.Z # u = y^2-1
        v = v + h.Z # v = dy^2+1

        v3 = v ** 2
        v3 = v3 * v # v3 = v^3
        v3 = v3 * v
        h.X = v3 ** 2
        h.X = h.X * v
        h.X = h.X * u # x = uv^7

        h.X = h.X.pow22523() # x = (uv^7)^((q-5)/8)
        h.X = h.X * v3
        h.X = h.X * u # x = uv^3(uv^7)^((q-5)/8)

        vxx = h.X ** 2
        vxx = vxx * v
        m_root_check = vxx - u # vx^2-u
        p_root_check = vxx + u # vx^2+u
        has_m_root = m_root_check.is_zero()
        has_p_root = p_root_check.is_zero()
        x_sqrtm1 = h.X * sqrtm1 # x*sqrt(-1)
        h.X = h.X.cmov(x_sqrtm1, 1 - has_m_root)

        negx = -h.X
        h.X = h.X.cmov(negx, h.X.is_negative() ^ (bs[31] >> 7))
        h.T = h.X * h.Y
        h.root_check = (has_m_root | has_p_root) - 1

        return h

    def to_bytes(self: ge25519_p3) -> bytearray:
        recip = self.Z.invert()
        x = self.X * recip
        y = self.Y * recip

        bs = y.to_bytes()
        bs[31] ^= (x.is_negative() << 7)
        return bs

class ge25519_p1p1(ge25519):
    def __init__(\
            self: ge25519_p1p1, 
            X: fe25519 = None, 
            Y: fe25519 = None, 
            Z: fe25519 = None,
            T: fe25519 = None
        ):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.T = T

    @staticmethod
    def add(p: ge25519_p3, q: ge25519_cached) -> ge25519_p1p1:
        r = ge25519_p1p1()
        r.X = p.Y + p.X
        r.Y = p.Y - p.X
        r.Z = r.X * q.YplusX
        r.Y = r.Y * q.YminusX
        r.T = q.T2d * p.T
        r.X = p.Z * q.Z
        t0 = r.X + r.X
        r.X = r.Z - r.Y
        r.Y = r.Z + r.Y
        r.Z = t0 + r.T
        r.T = t0 - r.T
        return r

class ge25519_cached(ge25519):
    def __init__(\
            self: ge25519_cached,
            YplusX: fe25519 = None,
            YminusX: fe25519 = None,
            Z: fe25519 = None,
            T2d: fe25519 = None
        ):
        self.YplusX = YplusX
        self.YminusX = YminusX
        self.Z = Z
        self.T2d = T2d

    @staticmethod
    def zero() -> ge25519_cached:
        return ge25519_cached(fe25519.one(), fe25519.one(), fe25519.one(), fe25519.zero())

    def cmov_cached(self: ge25519_cached, u: ge25519_cached, b: int): #ge25519_cmov_cached()
        t = self
        t.YplusX = t.YplusX.cmov(u.YplusX, b)
        t.YminusX = t.YminusX.cmov(u.YminusX, b)
        t.Z = t.Z.cmov(u.Z, b)
        t.T2d = t.T2d.cmov(u.T2d, b)

    @staticmethod
    def cmov8_cached(cached: Sequence[ge25519_cached], b: int) -> ge25519_cached:

        def negative(b): #signed char b
            # 18446744073709551361..18446744073709551615: yes; 0..255: no
            x = b % (2**64)
            x >>= 63
            return x % (2**8) # unsigned char

        def equal(b, c): #signed char b, signed char c
            ub = b % (2**8) # unsigned char
            uc = c % (2**8) # unsigned char
            x  = ub ^ uc; # 0: yes; 1..255: no
            y  = x % (2**32) # 0: yes; 1..255: no

            y = (y - 1) % (2**32)  # 4294967295: yes; 0..254: no
            y >>= 31 # 1: yes; 0: no

            return (y % (2**8)) # unsigned char

        bnegative = negative(b)
        babs      = _signed_char(b - _signed_char((((-bnegative)%(2**8)) & _signed_char(b)) * (1 << 1)))

        t = ge25519_cached.zero()
        t.cmov_cached(cached[0], equal(babs, 1))
        t.cmov_cached(cached[1], equal(babs, 2))
        t.cmov_cached(cached[2], equal(babs, 3))
        t.cmov_cached(cached[3], equal(babs, 4))
        t.cmov_cached(cached[4], equal(babs, 5))
        t.cmov_cached(cached[5], equal(babs, 6))
        t.cmov_cached(cached[6], equal(babs, 7))
        t.cmov_cached(cached[7], equal(babs, 8))

        minust = ge25519_cached(t.YminusX.copy(), t.YplusX.copy(), t.Z.copy(), -t.T2d.copy())
        t.cmov_cached(minust, bnegative)

        return t

    @staticmethod
    def from_p3(p: ge25519_p3) -> ge25519_cached:
        d2 = fe25519([1859910466990425, 932731440258426, 1072319116312658, 1815898335770999, 633789495995903])
        return ge25519_cached(p.Y + p.X, p.Y - p.X, p.Z.copy(), p.T * d2)

if __name__ == "__main__":
    doctest.testmod()
