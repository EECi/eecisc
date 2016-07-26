import smb
from getpass import getpass
from io import BytesIO
from pathlib import Path
import tempfile

import tempfile
from smb.SMBConnection import SMBConnection
import geopandas as gpd

from eecisc.eecisc import COMPUTER_NAME, IP_ADDRESS

NAME_OF_SMB_SHARE = 'share'
SMB_PORT = 139


def read_file(remote_path):
    """Reads a remote file on eecisc into file like object in memory."""
    conn = _connection()
    try:
        assert conn.connect(IP_ADDRESS, SMB_PORT)
        bytesIO = BytesIO()
        conn.retrieveFile(NAME_OF_SMB_SHARE, remote_path, bytesIO)
    finally:
        conn.close()
    bytesIO.seek(0)
    return bytesIO


def read_shapefile(remote_path):
    """Reads a remote shape file on eecisc into geopandas data frame."""
    remote_path = Path(remote_path)
    conn = _connection()
    try:
        assert conn.connect(IP_ADDRESS, SMB_PORT)
        remote_files = conn.listPath(
            NAME_OF_SMB_SHARE,
            path=remote_path.parent.as_posix(),
            pattern=(remote_path.stem + '.*')
        )
        with tempfile.TemporaryDirectory(prefix='eecisc-') as tmpdir:
            for suffix in [Path(file.filename).suffix for file in remote_files]:
                with (Path(tmpdir) / remote_path.stem).with_suffix(suffix).open('bw') as tmp_file:
                    conn.retrieveFile(
                        NAME_OF_SMB_SHARE,
                        remote_path.with_suffix(suffix).as_posix(),
                        tmp_file
                    )
            data = gpd.read_file((Path(tmpdir) / remote_path.stem).with_suffix('.shp').as_posix())
    finally:
        conn.close()
    return data


def _connection():
    return SMBConnection(
        username=input("User name on {}: ".format(COMPUTER_NAME)),
        password=getpass("Password: "),
        my_name="local_machine",
        remote_name=COMPUTER_NAME,
        use_ntlm_v2=True
    )
