use pyo3::exceptions::PyValueError;
use pyo3::{prelude::*, py_run};

extern crate secrets_core;
use secrets_core::*;

#[pyfunction]
fn set_password(service: String, account: String, password: String) -> PyResult<()> {
    match os::set_password(&service, &account, &password) {
        Ok(_) => Ok(()),
        Err(e) => Err(PyValueError::new_err(format!("{:#?}", e))),
    }
}

#[pyfunction]
fn get_password(service: String, account: String) -> PyResult<String> {
    match os::get_password(&service, &account) {
        Ok(pw) => Ok(pw.unwrap_or("".to_string())),
        Err(e) => Err(PyValueError::new_err(format!("{:#?}", e))),
    }
}

#[pyfunction]
fn delete_password(service: String, account: String) -> PyResult<bool> {
    match os::delete_password(&service, &account) {
        Ok(res) => Ok(res),
        Err(e) => Err(PyValueError::new_err(format!("{:#?}", e))),
    }
}

#[pyfunction]
fn find_password(service: String) -> PyResult<String> {
    match os::find_password(&service) {
        Ok(res) => match res {
            Some(val) => Ok(val),
            _ => Ok("".to_owned()),
        },
        Err(e) => Err(PyValueError::new_err(format!("{:#?}", e))),
    }
}

#[pyfunction]
fn find_credentials(service: String) -> PyResult<Vec<(String, String)>> {
    let mut creds: Vec<(String, String)> = vec![];
    match os::find_credentials(&service, &mut creds) {
        Ok(res) => Ok(creds),
        Err(e) => Err(PyValueError::new_err(format!("{:#?}", e))),
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn zowe_secrets_for_zowe_sdk(py: Python, module: &PyModule) -> PyResult<()> {
    let submodule = PyModule::new(py, "zowe.secrets_for_zowe_sdk.keyring")?;
    submodule.add_function(wrap_pyfunction!(get_password, submodule)?)?;
    submodule.add_function(wrap_pyfunction!(set_password, submodule)?)?;
    submodule.add_function(wrap_pyfunction!(delete_password, submodule)?)?;
    submodule.add_function(wrap_pyfunction!(find_password, submodule)?)?;
    submodule.add_function(wrap_pyfunction!(find_credentials, submodule)?)?;
    // Hack from https://github.com/PyO3/pyo3/issues/1517
    py_run!(
        py,
        submodule,
        "import sys; sys.modules['zowe.secrets_for_zowe_sdk.keyring'] = submodule"
    );
    module.add_submodule(submodule)?;
    Ok(())
}
