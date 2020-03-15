=======
ge25519
=======

Native Python implementation of Ed25519 group elements and operations.

.. image:: https://badge.fury.io/py/ge25519.svg
   :target: https://badge.fury.io/py/ge25519
   :alt: PyPI version and link.

Purpose
-------
This library provides a native Python implementation of `Ed25519 <https://ed25519.cr.yp.to/>`_ group elements and a number of operations over them. The library makes it possible to fill gaps in application prototypes that may have specific limitations with respect to their operating environment or their ability to rely on dependencies.

The implementation is based upon and is compatible with the corresponding implementation of Ed25519 group elements used in `libsodium <https://github.com/jedisct1/libsodium>`_.

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install ge25519

The library can be imported in the usual ways::

    import ge25519
    from ge25519 import *
