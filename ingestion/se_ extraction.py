import tarfile
import zipfile
import pandas as pd
import numpy as np

import boto3
import botocore


#Get ACS data from the s3 bucket
BUCKET_NAME = 'sharedbikedata'
PREFIX = 'Land_use/'
SUFFIX = 'Tracts_Block_Groups_Only.tar'
DESTINATION = '/tmp/Tracts_Block_Groups_Only.tar'
OUTCSV = "acs.csv"

s3 = boto3.resource('s3')

try:
    print("Downloading ACS file from s3")
    s3.Bucket(BUCKET_NAME).download_file(''.join([PREFIX, SUFFIX]), DESTINATION)
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise


# s3_path = "/home/ubuntu/bikeiq/data/Tracts_Block_Groups_Only.tar"
#open the ACS tar file
tar = tarfile.open(DESTINATION)

#set up variables to get from the ACS
#file_id: var column
lookup_dic = {
    "0002": [7, 31],
    "0003": [99, 100, 101, 129],
    "0004": [7, 8, 10],
    "0027": [111, 112, 113, 114],
    "0028": [157, 165, 173, 174],
    "0044": [45],
    "0059": [176],
    "0103": [10, 11, 12],
    "0105": [243]
}

#set up names for the ACS variables, the structure has to replicate lookup_dic
#file_id: name
lookup_dic2 = {
    "0002": ["male_tot", "fmale_tot"],
    "0003": ["med_age", "med_age_m", "med_age_f", "pop_tot"],
    "0004": ["race_white", "race_black", "asian"],
    "0027": ["trips_tot", "trips_u10", "trips_1014", "trips_1519"],
    "0028": ["car", "transit", "bike", "walk"],
    "0044": ["bach_edu"],
    "0059": ["med_hh_inc"],
    "0103": ["units_tot", "owned", "rented"],
    "0105": ["med_rent"]
}

#unused variables
# "0002" "male_u5", "male_59", "male_1014", "male_1517",
#              "male_1819", "male_20", "male_21", "male_2224", "male_2529",
#              "male_3034", "male_3539", "male_4044", "male_4549", "male_5054",
#              "male_5559", "male_6061", "male_6264", "male_6566", "male_6769",
#              "male_7074", "male_7579", "male_8084", "male_o85",
# 8,9,10,11,12,13,14,15,16,17,18,19,20,
#              21,22,23,24,25,26,27,28,29,30,
# "0002" "fmale_u5", "fmale_59", "fmale_1014", "fmale_1517",
#              "fmale_1819", "fmale_20", "fmale_21", "fmale_2224", "fmale_2529",
#              "fmale_3034", "fmale_3539", "fmale_4044", "fmale_4549", "fmale_5054",
#              "fmale_5559", "fmale_6061", "fmale_6264", "fmale_6566", "fmale_6769",
#              "fmale_7074", "fmale_7579", "fmale_8084", "fmale_o85"
# 32,33,34,35,36,37,38,39,40,41,42,43,
#              44,45,46,47,48,49,50,51,52,53,54
#     "0128": [10]
# ,
#     "0128": ["smartphone"]



#defining geographies: block=groups
print("Loading ACS geographies")
geo_dic = {}

for member in tar.getmembers():
    f = tar.extractfile(member)
    zipf = zipfile.ZipFile(f)
    contents = zipf.namelist()
    geo_file = [s for s in contents if "g20" in s][0]



    with zipfile.ZipFile(f) as z:
        with z.open(geo_file) as f:
            line = (f.readline())
            while line:
                if line[46] != 32:
                    logrecno = line[6:20].decode('UTF-8')
                    fips = line[178:197].decode('UTF-8')
                    geo_dic[logrecno] = fips
                line = f.readline()


geo_df = pd.DataFrame.from_dict(geo_dic, orient="index")
geo_df.columns = ["FIPS"]
geo_df['logrecno'] = geo_df.index
geo_df['state'] = geo_df.logrecno.str[:2].str.lower()
geo_df.logrecno = geo_df.logrecno.str[-7:].astype(int)



df_val = {}
for key in lookup_dic2.keys():
    cols = [['state'], ['logrecno'], lookup_dic2[key]]
    cols = [item for sublist in cols for item in sublist]
    df_val[key] = pd.DataFrame(columns=cols, dtype=np.int8)




for member in tar.getmembers():
    f = tar.extractfile(member)
    zipf = zipfile.ZipFile(f)
    contents = zipf.namelist()
    data_file = {}
    for key in lookup_dic.keys():
        data_file[[s for s in contents if key in s][0]] = key
    print(data_file)


    with zipfile.ZipFile(f) as z:
        for file in data_file.keys():
            with z.open(file) as f:
                try:
                    df = pd.read_csv(f, header=None, error_bad_lines=False)
                    cols = [[2], [5], lookup_dic[data_file[file]]]
                    cols = [item for sublist in cols for item in sublist]
                    df = df.iloc[:, cols]
                    new_cols = [['state'], ['logrecno'], lookup_dic2[data_file[file]]]
                    new_cols = [item for sublist in new_cols for item in sublist]
                    new_cols = dict(zip(cols, new_cols))
                    df.rename(columns=new_cols, inplace=True)
                    df_val[data_file[file]] = df_val[data_file[file]].append(df, ignore_index=True)
                except:
                    print("Failure to parse")



tar.close()



output = None

for key in lookup_dic2.keys():
    # print(df_val[key].head())
    result = pd.merge(geo_df, df_val[key], how="left", left_on=['state', 'logrecno'], right_on=['state', 'logrecno'])
    # print(result.head())
    result.drop(['state', 'logrecno'], axis=1, inplace=True)
    if output is None:
        output = result
    else:
        output = pd.merge(output, result, how="left", left_on=["FIPS"], right_on=["FIPS"])
print(output.head())
# print(output.columns)
output.to_csv("/home/ubuntu/bikeiq/data/acs.csv", index=False)

s3.Object(BUCKET_NAME, ''.join([PREFIX, OUTCSV])).put(Body=open('/home/ubuntu/bikeiq/data/acs.csv', 'rb'))




