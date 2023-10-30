use pyo3::prelude::*;

extern crate keyring;
use keyring::os::*;

#[pyfunction]
fn py_set_password(service: &str, account: &str, password: &str) -> PyResult<()> {
    match set_password(service, account, password) {
        Ok(_) => Ok(()),
        Err(e) => Err(e),
    }
}

#[pyfunction]
fn py_get_password(service: &str, account: &str) -> PyResult<String> {
    match get_password(service, account) {
        Ok(_) => Ok(()),
        Err(e) => Err(e),
    }
}

#[pyfunction]
fn py_delete_password(service: &str, account: &str) -> PyResult<String> {
    match delete_password(service, account) {
        Ok(res) => Ok(res),
        Err(e) => Err(e),
    }
}

#[pyfunction]
fn py_find_password(service: &str) -> PyResult<String> {
    match find_password(service) {
        Ok(res) => Ok(res),
        Err(e) => Err(e),
    }
}

#[pyfunction]
fn py_find_credentials(service: &str) -> PyResult<Vec<(String, String)>> {
    let mut creds: Vec<(String, String)> = vec![];
    match find_credentials(service, &mut creds) {
        Ok(res) => Ok(creds),
        Err(e) => Err(e),
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn keyring_test(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_get_password, m)?)?;
    m.add_function(wrap_pyfunction!(py_set_password, m)?)?;
    m.add_function(wrap_pyfunction!(py_delete_password, m)?)?;
    m.add_function(wrap_pyfunction!(py_find_password, m)?)?;
    m.add_function(wrap_pyfunction!(py_find_credentials, m)?)?;
    Ok(())
}
