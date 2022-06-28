Running Tests
==============

The project's test suite can be run with the python test runner, `green`

.. code-block::

  green -vvv  ./tests/unit

In order to run the integration test, one will need to have a zowe profile. If zowe cli is installed, the test profile lives in ``~/.zowe/profiles/zomsf/Zowe.yaml``

.. code-block::

  host: zzow03.zowe.marist.cloud
  port: 10443
  user: XXXXX
  password: XXXXX
  rejectUnauthorized: false
  protocol: https
