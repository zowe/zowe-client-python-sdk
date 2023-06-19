"""Unit tests for the Zowe Python SDK z/OS Files package."""
from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files, exceptions


class TestFilesClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = {"host": "mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Files class."""
        files = Files(self.test_profile)
        self.assertIsInstance(files, Files)

    @mock.patch('requests.Session.send')
    def test_delete_uss(self, mock_send_request):
        """Test deleting a directory recursively sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_uss("filepath_name", recursive=True)
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_create_zFS_file_system(self, mock_send_request):
        """Test creating a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms":100, "cylsPri": 16777213, "cylsSec": 16777215})
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_delete_zFS_file_system(self, mock_send_request):
        """Test deleting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_zFS_file_system("file_system_name")
        mock_send_request.assert_called_once()
    
    def test_invalid_permission(self):
        """Test that the correct exception is raised when an invalid permission option is provided"""
        with self.assertRaises(exceptions.InvalidPermsOption) as e_info:
            Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms": -1, "cylsPri": 16777213, "cylsSec": 16777215})
        self.assertEqual(str(e_info.exception), "Invalid zos-files create command 'perms' option: -1")

    def test_invalid_memory_allocation(self):
        """Test that the correct exception is raised when an invalid memory allocation option is provided"""
        with self.assertRaises(exceptions.MaxAllocationQuantityExceeded) as e_info:
            Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms": 775, "cylsPri": 1677755513, "cylsSec": 16777215})
        self.assertEqual(str(e_info.exception), "Maximum allocation quantity of 16777215 exceeded")
    
    @mock.patch('requests.Session.send')
    def test_mount_zFS_file_system(self, mock_send_request):
        """Test mounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).mount_file_system("file_system_name", "mount_point")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_unmount_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).unmount_file_system("file_system_name")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_list_dsn(self, mock_send_request):
        """Test creating a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        test_values = [
            ('MY.DSN',False),
            ('MY.DSN',True)
        ]
        for test_case in test_values:
            Files(self.test_profile).list_dsn(*test_case)
            mock_send_request.assert_called()
       
        

    @mock.patch('requests.Session.send')
    def test_list_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).list_unix_file_systems("file_system_name")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_recall_migrated_dataset(self, mock_send_request):
        """Test recalling migrated data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).recall_migrated_dataset("dataset_name")
        mock_send_request.assert_called_once()
    
    @mock.patch('requests.Session.send')
    def test_copy_uss_to_dataset(self, mock_send_request):
        """Test copy_uss_to_dataset sends a request"""
        
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).copy_uss_to_dataset("from_filename","to_dataset_name","to_member_name",replace=True)
        
        
        mock_send_request.assert_called_once()
   
    def test_copy_dataset_or_member_raises_exception(self):
        """Test copying a data set or member raises error when assigning invalid values to enq parameter"""

        test_case = {
        "from_dataset_name": "MY.OLD.DSN",
        "to_dataset_name": "MY.NEW.DSN",
        "from_member_name": "MYMEM1",
        "to_member_name": "MYMEM2",
        "volser":'ABC',
        "alias":False,
        "enq": "RANDOM",
        "replace": True
        }
        with self.assertRaises(ValueError) as e_info:
            Files(self.test_profile).copy_dataset_or_member(**test_case)
        self.assertEqual(str(e_info.exception), "Invalid value for enq.")
            
    @mock.patch('requests.Session.send')
    def test_copy_dataset_or_member(self, mock_send_request):
        """Test copying a data set or member sends a request"""
        
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        test_values = [
           {
        "from_dataset_name": "MY.OLD.DSN",
        "to_dataset_name": "MY.NEW.DSN",
        "from_member_name": "MYMEM1",
        "to_member_name": "MYMEM2",
        "volser":'ABC',
        "alias":False,
        "enq": "SHRW",
        "replace": False
        },
           {
        "from_dataset_name": "MY.OLD.DSN",
        "to_dataset_name": "MY.NEW.DSN",
        "from_member_name": "MYMEM1",
        "to_member_name": "MYMEM2",
        "volser":'ABC',
        "alias":False,
        "enq": "SHRW",
        "replace": True
        }
        ]
        for test_case in test_values:
            Files(self.test_profile).copy_dataset_or_member(**test_case)
            mock_send_request.assert_called()
            
    def test_recall_migrated_dataset_parameterized(self):
        """Testing recall migrated_dataset with different values"""

        test_values = [
            ("MY.OLD.DSN", False),
            ("MY.OLD.DSN", True),
            ("MY.NEW.DSN", False),
            ("MY.NEW.DSN", True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "hrecall",
                "wait": test_case[1]
            }

            files_test_profile.recall_migrated_dataset(test_case[0], test_case[1])
            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0])
            files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args, expected_code=[200])

    @mock.patch('requests.Session.send')
    def test_delete_migrated_data_set(self, mock_send_request):
        """Test deleting a migrated data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).delete_migrated_data_set("dataset_name")
        mock_send_request.assert_called_once()

    def test_delete_migrated_data_set_parameterized(self):
        """Test deleting a migrated data set with different values"""

        test_values = [
            ("MY.OLD.DSN", False, False),
            ("MY.OLD.DSN", False, True),
            ("MY.OLD.DSN", True, True),
            ("MY.NEW.DSN", True, True),
            ("MY.NEW.DSN", False, True),
            ("MY.NEW.DSN", False, False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "hdelete",
                "purge": test_case[1],
                "wait": test_case[2],

            }

            files_test_profile.delete_migrated_data_set(test_case[0], test_case[1], test_case[2])
            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0])
            files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args, expected_code=[200])

    @mock.patch('requests.Session.send')
    def test_migrate_data_set(self, mock_send_request):
        """Test migrating a data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).migrate_data_set("dataset_name")
        mock_send_request.assert_called_once()

    def test_migrate_data_set_parameterized(self):
        """Test migrating a data set with different values"""

        test_values = [
            ("MY.OLD.DSN", False),
            ("MY.OLD.DSN", True),
            ("MY.NEW.DSN", True),
            ("MY.NEW.DSN", False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "hmigrate",
                "wait": test_case[1],
            }

            files_test_profile.migrate_data_set(test_case[0], test_case[1])

            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0])
            files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args, expected_code=[200])

    @mock.patch('requests.Session.send')
    def test_rename_dataset(self, mock_send_request):
        """Test renaming dataset sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset("MY.OLD.DSN", "MY.NEW.DSN")
        mock_send_request.assert_called_once()

    def test_rename_dataset_parametrized(self):
        """Test renaming a dataset with different values"""
        test_values = [
            (('DSN.OLD', "DSN.NEW"), True),
            (('DS.NAME.CURRENT', "DS.NAME.NEW"), True),
            (('MY.OLD.DSN', "MY.NEW.DSN"), True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "rename",
                "from-dataset": {
                    "dsn": test_case[0][0].strip(),
                }
            }

            files_test_profile.rename_dataset(test_case[0][0], test_case[0][1])

            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0][1])
            files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args, expected_code=[200])

    @mock.patch('requests.Session.send')
    def test_rename_dataset_member(self, mock_send_request):
        """Test renaming dataset member sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBEROLD", "MEMBERNEW")
        mock_send_request.assert_called_once()

    def test_rename_dataset_member_raises_exception(self):
        """Test renaming a dataset member raises error when assigning invalid values to enq parameter"""
        with self.assertRaises(ValueError) as e_info:
            Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBER1", "MEMBER1N", "RANDOM")
        self.assertEqual(str(e_info.exception), "Invalid value for enq.")

    def test_rename_dataset_member_parametrized(self):
        """Test renaming a dataset member with different values"""
        test_values = [
            (('DSN', "MBROLD", "MBRNEW", "EXCLU"), True),
            (('DSN', "MBROLD", "MBRNEW", "SHRW"), True),
            (('DSN', "MBROLD", "MBRNEW", "INVALID"), False),
            (('DATA.SET.NAME', 'MEMBEROLD', 'MEMBERNEW'), True),
            (('DS.NAME', "MONAME", "MNNAME"), True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "rename",
                "from-dataset": {
                    "dsn": test_case[0][0].strip(),
                    "member": test_case[0][1].strip(),
                }
            }

            if len(test_case[0]) > 3:
                data["enq"] = test_case[0][3].strip()
            if test_case[1]:
                files_test_profile.rename_dataset_member(*test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = data
                custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}({})".format(
                    test_case[0][0], test_case[0][2])
                files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args,
                                                                                           expected_code=[200])
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.rename_dataset_member(*test_case[0])
                self.assertEqual(str(e_info.exception), "Invalid value for enq.")

    def test_create_data_set_raises_error_without_required_arguments(self):
        """Test not providing required arguments raises an error"""
        with self.assertRaises(ValueError) as e_info:
            obj = Files(self.test_profile).create_data_set("DSNAME123", options={
                "alcunit": "CYL",
                "dsorg": "PO",
                "recfm": "FB",
                "blksize": 6160,
                "dirblk": 25
            })
        self.assertEqual(str(e_info.exception), "If 'like' is not specified, you must specify 'primary' or 'lrecl'.")

    def test_create_data_set_raises_error_with_invalid_arguments_parameterized(self):
        """Test not providing valid arguments raises an error"""
        test_values = [
            {
                "alcunit": "invalid",
                "dsorg": "PO",
                "primary": 1,
                "dirblk": 5,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80
            },
            {
                "dsorg": "PO",
                "alcunit": "CYL",
                "primary": 1,
                "recfm": "invalid",
                "blksize": 32760,
                "lrecl": 260,
                "dirblk": 25
            },
            {
                "alcunit": "CYL",
                "dsorg": "invalid",
                "primary": 1,
                "dirblk": 5,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80
            },
            {
                "dsorg": "PO",
                "alcunit": "CYL",
                "primary": 10,
                "recfm": "U",
                "blksize": 27998,
                "lrecl": 27998,
                "dirblk": 0
            },
            {
                "alcunit": "CYL",
                "dsorg": "PO",
                "primary": 99777215,
                "dirblk": 5,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80
            }
        ]

        for test_case in test_values:
            with self.assertRaises((KeyError, ValueError)):
                obj = Files(self.test_profile).create_data_set("MY.OLD.DSN", options=test_case)

    def test_create_dataset_parameterized(self):
        """Test create dataset with different values"""
        test_values = [
            (("DSN", {
                "alcunit": "CYL",
                "dsorg": "PO",
                "primary": 1,
                "dirblk": 5,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80
            }), True),
            (("DSN", {
                "alcunit": "CYL",
                "dsorg": "PO",
                "primary": 1,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80,
                "dirblk": 25
            }), True),
            (("DSN", {
                "dsorg": "PO",
                "alcunit": "CYL",
                "primary": 1,
                "recfm": "VB",
                "blksize": 32760,
                "lrecl": 260,
                "dirblk": 25
            }), True),
            (("DSN", {
                "alcunit": "CYL",
                "dsorg": "PS",
                "primary": 1,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80
            }), True),
            (("DSN", {
                "alcunit": "CYL",
                "dsorg": "PS",
                "recfm": "FB",
                "blksize": 6160,
            }), False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            if test_case[1]:
                files_test_profile.create_data_set(*test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = test_case[0][1]
                custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0][0])
                files_test_profile.request_handler.perform_request.assert_called_once_with("POST", custom_args, expected_code=[201])
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.create_data_set(*test_case[0])
                self.assertEqual(str(e_info.exception), "If 'like' is not specified, you must specify 'primary' or 'lrecl'.")

    @mock.patch('requests.Session.send')
    def test_create_default_dataset(self, mock_send_request):
        """Test creating a default data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_default_data_set("dataset_name", "partitioned")
        mock_send_request.assert_called_once()

    def test_create_default_dataset_parameterized(self):
        """Test create default dataset with different values"""
        test_values = [
            (("DSN", "partitioned"), True),
            (("DSN", "sequential"), True),
            (("DSN", "classic"), True),
            (("DSN", "c"), True),
            (("DSN", "binary"), True),
            (("DSN", "invalid"), False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            options = {
                "partitioned": {
                    "alcunit": "CYL",
                    "dsorg": "PO",
                    "primary": 1,
                    "dirblk": 5,
                    "recfm": "FB",
                    "blksize": 6160,
                    "lrecl": 80
                },
                "sequential": {
                    "alcunit": "CYL",
                    "dsorg": "PS",
                    "primary": 1,
                    "recfm": "FB",
                    "blksize": 6160,
                    "lrecl": 80
                },
                "classic": {
                    "alcunit": "CYL",
                    "dsorg": "PO",
                    "primary": 1,
                    "recfm": "FB",
                    "blksize": 6160,
                    "lrecl": 80,
                    "dirblk": 25
                },
                "c": {
                    "dsorg": "PO",
                    "alcunit": "CYL",
                    "primary": 1,
                    "recfm": "VB",
                    "blksize": 32760,
                    "lrecl": 260,
                    "dirblk": 25
                },
                "binary": {
                    "dsorg": "PO",
                    "alcunit": "CYL",
                    "primary": 10,
                    "recfm": "U",
                    "blksize": 27998,
                    "lrecl": 27998,
                    "dirblk": 25
                }
            }

            if test_case[1]:
                files_test_profile.create_default_data_set(*test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = options.get(test_case[0][1])
                custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0][0])
                files_test_profile.request_handler.perform_request.assert_called_once_with("POST", custom_args, expected_code=[201])
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.create_default_data_set(*test_case[0])
                self.assertEqual(str(e_info.exception), "Invalid type for default data set.")
