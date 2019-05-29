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

`/data` should be used for raw data, while `/processed` should be used for any intermediate steps. You can also duplicate this on S3. 

Don't hardcode paths, such as `//Users/YOUR_EID/

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
Data Interchange: Where everything can be broken

### CSVs 
CSVs are the lowest common denominator of data files.  

### Excel / XLSX
Excel Files 
Best 

### Paraquet 

### Shapefiles 

### Databases 

### Pickles

## Geospatial 