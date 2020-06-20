=======
ge25519
=======

Native Python implementation of Ed25519 group elements and operations.

|pypi| |travis|

.. |pypi| image:: https://badge.fury.io/py/ge25519.svg
   :target: https://badge.fury.io/py/ge25519
   :alt: PyPI version and link.

.. |travis| image:: https://travis-ci.com/nthparty/ge25519.svg?branch=master
    :target: https://travis-ci.com/nthparty/ge25519

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

Testing and Conventions
-----------------------

Unit tests can be executed using `nose <https://nose.readthedocs.io/>`_::

    nosetests

Concise unit tests are implemented with the help of `fountains <https://pypi.org/project/fountains/>`_ and new reference bit lists for these tests can be generated in the following way::

    python test/test_ge25519.py

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    pylint ge25519

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
Beginning with version 0.1.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.
