Advanced steps
===============

- Use a custom Certificate Authority if working in a restricted environment.
   The Python SDK supports the commonly used environmental variables `REQUESTS_CA_BUNDLE` and `CURL_CA_BUNDLE` to provide a certificate chain.
   
   You can also use the `SSL_CERT_FILE` environmental variable in project-level configurations.
