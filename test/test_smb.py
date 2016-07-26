from io import BytesIO

import pytest
import pandas as pd
from smb.SMBConnection import SMBConnection

import eecisc
from eecisc import smb


@pytest.fixture(scope='module')
def credentials(variables):
    """Monkey patches the credential mechanism, so that the user is not prompted.

    This is necessary because pytest doesn't allow a prompt.
    """
    def input_mock(prompt):
        return variables['username']
    smb.input = input_mock

    def password_mock(prompt):
        return variables['password']
    smb.getpass = password_mock


@pytest.fixture
def connection(variables):
    """SMBConnection object to eecisc."""
    return SMBConnection(
        username=variables['username'],
        password=variables['password'],
        my_name="local_machine",
        remote_name=eecisc.COMPUTER_NAME,
        use_ntlm_v2=True
    )


@pytest.yield_fixture
def remote_test_csv(connection):
    """Path to a temp csv file on the remote.

    File is uploaded before the test and deleted afterwards.
    """
    path = '/test.csv'
    csv = BytesIO(
        b"""A,B,C
        1,2,3
        4,5,6
        """
    )
    try:
        assert connection.connect(eecisc.IP_ADDRESS, smb.SMB_PORT)
        connection.storeFile(smb.NAME_OF_SMB_SHARE, path, csv, timeout=5)
        yield path
        connection.deleteFiles(smb.NAME_OF_SMB_SHARE, path, timeout=5)
    finally:
        connection.close()


def test_csv_retrieval(credentials, remote_test_csv):
    csv = pd.read_csv(eecisc.read_file('/test.csv'))
    assert type(csv) == pd.DataFrame
    assert set(csv.columns) == set(['A', 'B', 'C'])
    assert csv.index.size == 2
