from zowe.zos_console_for_zowe_sdk import Console

# Change <xxxx> below to the name of your zosmf profile

connection = {"plugin_profile": "xxxx"}

my_console = Console(connection)
command = "D IPLINFO"
command_result = my_console.issue_command(command)
command_output = command_result["cmd-response"].replace("\r", "\n")

print(f"Command: {command} \n Output: \n\n{command_output}")
