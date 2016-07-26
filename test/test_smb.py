from io import BytesIO
from pathlib import Path
import tempfile

import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry.polygon import Polygon
from smb.SMBConnection import SMBConnection

import eecisc
from eecisc import smb

SHAPE_FILE_SUFFIXES = ['.shp', '.shx', '.dbf']


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


@pytest.yield_fixture
def remote_shape_file(connection):
    """Path to a shape file on the remote.

    Files are uploaded before the test and deleted afterwards.
    """
    path = '/test-shape-file'
    p = Polygon([(0, 0), (1, 0), (1, 1)])
    shape_file = gpd.GeoDataFrame(geometry=[p], data={'a': [100]})
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_file = Path(tmpdir) / 'test-shape-file'
            shape_file.to_file(tmp_file.with_suffix('.shp').as_posix())
            assert connection.connect(eecisc.IP_ADDRESS, smb.SMB_PORT)
            for suffix in SHAPE_FILE_SUFFIXES:
                with tmp_file.with_suffix(suffix).open('rb') as open_file:
                    connection.storeFile(smb.NAME_OF_SMB_SHARE, path + suffix, open_file, timeout=5)
        yield path
        for suffix in SHAPE_FILE_SUFFIXES:
            connection.deleteFiles(smb.NAME_OF_SMB_SHARE, path + suffix, timeout=5)
    finally:
        connection.close()


def test_csv_retrieval(credentials, remote_test_csv):
    csv = pd.read_csv(eecisc.read_file(remote_test_csv))
    assert type(csv) == pd.DataFrame
    assert set(csv.columns) == set(['A', 'B', 'C'])
    assert csv.index.size == 2


def test_shp_retrieval(credentials, remote_shape_file):
    data = eecisc.read_shapefile(remote_shape_file)
    assert type(data) == gpd.GeoDataFrame
    assert data.index.size == 1
    assert data.iloc[0].a == 100


def test_shp_retrieval_with_suffix(credentials, remote_shape_file):
    remote_shape_file = Path(remote_shape_file)
    assert remote_shape_file.suffix == ''
    eecisc.read_shapefile(remote_shape_file.with_suffix('.shp'))
