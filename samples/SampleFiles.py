from zowe.zos_files_for_zowe_sdk import Files

# Change <xxxx> below to the name of your zosmf profile

connection = {
    "plugin_profile": "xxxx"
}

# -----------------------------------------------------
# print list of zos datasets
# ----------------------------------------------------- 
print("...SYS1 datasets\n")
my_files = Files(connection)
my_dsn_list = my_files.list_dsn("SYS1.**.*")
datasets = my_dsn_list['items']
for ds in datasets:
    print(ds['dsname'])

# -----------------------------------------------------
# Now try the uss side... Not in the SDK in GitHub yet

# ----------------------------------------------------- 
print("...files in /etc\n")
my_file_list = my_files.list_files("/etc")
files = my_file_list["items"]
for file in files:
    print(file["name"], file["mode"])

# -----------------------------------------------------
# Get the content of one of the files.
# ----------------------------------------------------- 
print("...content of a file\n")
my_file_content = my_files.get_file_content("/z/tm891807/file.txt")
print(my_file_content["response"])

