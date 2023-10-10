import os
import time

from zowe.zos_jobs_for_zowe_sdk import Jobs

# -----------------------------------------------------
# Test drive the jobs SDK with jcl from a file
# -----------------------------------------------------
# Change <xxxx> below to the name of your zosmf profile

connection = {"plugin_profile": "xxxx"}


print("...Submit a sleeper job\n")
my_jobs = Jobs(connection)
job = my_jobs.submit_from_local_file("jcl\sleep.jcl")
job_name = job["jobname"]
job_id = job["jobid"]
print(f"Job {job_name} ID {job_id} submitted")

# -----------------------------------------------------
# Wait until the job completes
# -----------------------------------------------------

boolJobNotDone = True
while boolJobNotDone:
    status = my_jobs.get_job_status(job_name, job_id)
    job_status = status["status"]
    if job_status != "OUTPUT":
        print(f"Status {job_status}")
        time.sleep(5)
    else:
        boolJobNotDone = False

# -----------------------------------------------------
# Get the return code
# -----------------------------------------------------
job_retcode = status["retcode"]
job_correlator = status["job-correlator"]
print(f"Job {job_name} ID {job_id} ended with {job_retcode}")

# -----------------------------------------------------
# Get all the spool files and dump them in <output_dir>
# -----------------------------------------------------
output_dir = "./output"
my_jobs.get_job_output_as_files(status, output_dir)
