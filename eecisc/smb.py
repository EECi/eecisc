import smb
from getpass import getpass
from io import BytesIO

import tempfile
from smb.SMBConnection import SMBConnection

from eecisc.eecisc import COMPUTER_NAME, IP_ADDRESS

NAME_OF_SMB_SHARE = 'share'
SMB_PORT = 139


def read_file(remote_path):
    """Reads a remote file on eecisc into file like object in memory."""
    conn = SMBConnection(
        username=input("User name on {}: ".format(COMPUTER_NAME)),
        password=getpass("Password: "),
        my_name="local_machine",
        remote_name=COMPUTER_NAME,
        use_ntlm_v2=True
    )
    try:
        assert conn.connect(IP_ADDRESS, SMB_PORT)
        bytesIO = BytesIO()
        conn.retrieveFile(NAME_OF_SMB_SHARE, remote_path, bytesIO)
    finally:
        conn.close()
    bytesIO.seek(0)
    return bytesIO
