Running Tests
==============

The project's test suite can be run with the python test runner, `green`

.. code-block::

  green -vvv  ./tests/unit

In order to run the integration test, one will need to have a zowe profile 
and configure the `.env` file: `ZOWE_TEST_PROFILE='<myProfile>'`. If zowe cli is 
installed, the test profile lives in `~/.zowe/profiles/zosmf/<myProfile>.yaml`.

.. code-block::

  host: example.com
  port: 443
  user: XXXXX
  password: XXXXX
  rejectUnauthorized: false
  protocol: https
