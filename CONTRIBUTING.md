# Contributing

This document contains the contribution guidelines for the Zowe Client Python SDK.

Notice that the Python SDK is still in early development stages, meaning that major architectural changes might be made by the development team at any given moment. **For this reason, only bug fixes and documentation changes are being accepted as contribution at this moment** . This document will be updated as soon as the stable release of the SDK is published (v1.0.0)

- [Contributing](#contributing)
  - [Git branching model](#git-branching-model)
  - [Pull requests](#pull-requests)
  - [Running Tests](#running-tests)
  - [Code standards](#code-standards)


Git branching model
-------------------

This project follows the [Git flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model.

Pull requests
-------------

Consider the following when you interact with pull requests:

* Pull request reviewers should be assigned to a same-team member.
* Pull requests should remain open for at least 24 hours, or until close of the business next business day (accounting for weekends and holidays).
* Anyone can comment on a pull request to request delay on merging or to get questions answered.

Running Tests
-------------
The project's test suite can be run with the python test runner, `green`
```
green -vvv  ./tests/unit
```

In order to run the integration test, one will need to have a zowe profile and configure the `.env` file – `ZOWE_TEST_PROFILE='<myProfile>'`. If zowe cli is installed, the test profile lives in `~/.zowe/profiles/zosmf/<myProfile>.yaml`.

```
host: example.com
port: 443
user: XXXXX
password: XXXXX
rejectUnauthorized: false
protocol: https
```
Code standards
--------------

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
