# eecisc

## User Guide

### Installation

You can install this package with conda:

    $ conda install eecisc -c timtroendle -c conda-forge

### Usage

You can use this package to read files from the smb share on EECISC. For example:

```python
import eecisc
import pandas as pd
import geopandas as gpd

# read pure file
csv_file = eecisc.read_file('/remote-csv-file.csv')

# read into data frame
df = pd.read_csv(csv_file)

# read shape file into geopandas data frame
gdf = eecisc.read_shapefile('/remote-shape-file')
```

## Developer Guide

### Installation

Best install eecisc in editable mode:

    $ pip install -e .

You will furthermore need ``pytest`` and its ``pytest-variables`` extension.

    $ pip install pytest
    $ pip install pytest-variables[yaml]

### Run the test suite

First you will need a credentials file with EECISC credentials. As the file contains the credentials in clear text rather do not use your credentials, but the ones from the "Test" user.

```yaml
# credentials.yaml
username: "Test"
password: "<password>"
```

Then, run the test suite with py.test:

    $ py.test --variables credentials.yaml
