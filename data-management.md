# Data Management

Data Management is hard, and before you know it, you can ended up with `final_final_final_project_data-2019.csv.bak` as the source of your project data.

Below is a series of tips, tricks and usecases for managing data throughout the lifecycle of a projects. 


## Reading and Writing Data 
### S3
Our team often uses Amazon S3 as a bucket storage. To access data in S3, you'll have to have AWS access credentials stored at `~/.aws/credentials` per the [documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). 

S3 can store anything, of arbitrary object size and shape. It's like a giant folder in the cloud. You can use it to store CSVs, Pickes, Videos, whatever. 

To write and read a pandas dataframe as a CSV to S3: 

```
import pandas as pd
df.to_csv(s3://bucket-name/my_df_name.csv)

pd.read_csv(s3://bucket-name/my_df_name.csv)
```

You can read more in the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html) docs. By putting data on S3, anybody on the team can use / access/ and replicate without having to transfer data files between machines. 

### Local Folders 
Sometimes, it is easiest to simply use your local file system to store data. As a manner of conventions, we use the `data` and `processed` directories, which  are automatically ignored from git from the project base `.gitignore`. 

`/data` should be used for raw data, while `/processed` should be used for any intermediate steps. You can also duplicate this on S3. Finally, `outputs/` for outputs. This should all best setup by our [data science template](https://github.com/CityOfLosAngeles/cookiecutter-data-science). If you use `data`, make sure all the data in it is documented in your README. 

Don't hardcode paths, such as `//Users/YOUR_EID/. You might need to use S3 or a cloud database if your data is big. 

### Databases 
Finally, for analysis and storage purposes, it is sometimes best to store the data in a structured database for querying. We use `postgreSQL` for this purposes. 

To access, you'll need to set the $POSTGRES_URI [environment variable](https://devblogs.microsoft.com/commandline/share-environment-vars-between-wsl-and-windows/) equal to the proper connection string. Once that is set, you'll be able to read and write SQL queries into dataframes as follows: 

```
import os 
from sqlalchemy import create_engine
import pandas as pd 

connection_string = os.environ.get('POSTGRES_URI')

engine = create_engine(connection_string)

df.to_sql(
    "my_table_name",
    engine,
    schema="public",
    if_exists="replace",
    dtype={"geom": Geometry("POINT", srid=srid)},
)

query = "SELECT * FROM my_table_name LIMIT 10;"

pd.read_sql(query,engine) 

```

Note: This example shows how to make sure that Geometry types are inserted into POSTGIS (a point example) and limits the number of rows returned to 10 in the Query. You can execute abritrary SQL inside `pd.read_sql()`.

## Formats and use-cases 
Data Interchange: Where everything can be broken. 

### CSVs 
CSVs are the lowest common denominator of data files. Best for getting raw data from SQL and storing large blobs on cloud services. For interchange, it is better to use paraquet or even excel as they preserve datatypes. 

### Excel / XLSX

Best for sharing with other teams, except for geographic info (use shapefiles or geojson instead).

You often might want to write multiple dataframes to a single excel files as sheets. Here's a guide: 

```
## init a writer 
writer = pd.ExcelWriter('../outputs/filename.xlsx', engine='xlsxwriter')

## assume district_dfs is a list of dataframes by council district 
Write each dataframe to a different worksheet.
for key, value in district_dfs.items(): 
    value.to_excel(writer, sheet_name=key)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
```
### Paraquet 
Paraquet is an "open source columnar storage format for use in data analysis systems". Paraquet files are faster to read than CSVs, preserve datatypes (ie, Number,  Timestamps, Points). Best for intermediate data storage and large datasets (1GB+) on S3. 

Also good for passing dataframes between Python + R. A similar option is [feather](https://blog.rstudio.com/2016/03/29/feather/).

Not good for being able to quickly look at the dataset in GUI based (Excel, QGIS, etc) programs. 
[Docs](https://arrow.apache.org/docs/python/parquet.html)

### Shapefiles 
The original file format for geospatial data, geopandas has good support for reading / writing shapefiles. 

One weird thing, however, is that a shapefile isn't a _file_, it's a _folder_, containing multiple subfiles (such as .dbf, .shpx, etc). To properly read/write shapefiles, make sure to read the entire folder or write to a folder each time. 

It is often better to use `geojson` vs `shapefiles` since the former is easier to render on the web. The latter is better when you have a bespoke projection. 

```

import geopandas as gpd 
import os

# read shapefile 
gpd.read_file('./my_folder/')

# write shapefile 
if not os.path.exists('./outputs/my_dir_name'):
    os.mkdirs('./outputs/my_dir_name')
gdf.to_file('./outputs/my_dir_name')
```
### Databases 
A whole field of study, it is often useful to use a DB for analytics and aggegrated queries, rather than just your production datastore. Our team maintains a Postgresql + PostGIS DB to help us make complex spatial + geospatial queries. However, it is best practice to move those queries to python or a `Makefile` ASAP. 

### Pickles
A way of  storing arbitrary python objects. Danger lives here. 

### GeoJSON 
The other important open geodata spec, geojson is often easier to work with than a shapefile. However, it can get very large very quickly. 