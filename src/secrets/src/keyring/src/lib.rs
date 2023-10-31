use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

extern crate secrets_core;
use secrets_core::*;

#[pyfunction]
fn set_password(service: String, account: String, password: String) -> PyResult<()> {
    match os::set_password(&service, &account, &password) {
        Ok(_) => Ok(()),
        Err(e) => Err(PyValueError::new_err("error in set_password")),
    }
}

#[pyfunction]
fn get_password(service: String, account: String) -> PyResult<String> {
    match os::get_password(&service, &account) {
        Ok(pw) => Ok(pw.unwrap_or("".to_string())),
        Err(e) => Err(PyValueError::new_err("error in get_password")),
    }
}

#[pyfunction]
fn delete_password(service: String, account: String) -> PyResult<bool> {
    match os::delete_password(&service, &account) {
        Ok(res) => Ok(res),
        Err(e) => Err(PyValueError::new_err("error in delete_password")),
    }
}

#[pyfunction]
fn find_password(service: String) -> PyResult<String> {
    match os::find_password(&service) {
        Ok(res) => match res {
            Some(val) => Ok(val),
            _ => Ok("".to_owned()),
        },
        Err(e) => Err(PyValueError::new_err("error in find_password")),
    }
}

#[pyfunction]
fn find_credentials(service: String) -> PyResult<Vec<(String, String)>> {
    let mut creds: Vec<(String, String)> = vec![];
    match os::find_credentials(&service, &mut creds) {
        Ok(res) => Ok(creds),
        Err(e) => Err(PyValueError::new_err("error in find_credentials")),
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn keyring_test(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_password, m)?)?;
    m.add_function(wrap_pyfunction!(set_password, m)?)?;
    m.add_function(wrap_pyfunction!(delete_password, m)?)?;
    m.add_function(wrap_pyfunction!(find_password, m)?)?;
    m.add_function(wrap_pyfunction!(find_credentials, m)?)?;
    Ok(())
}