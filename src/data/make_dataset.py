# %%
import pandas as pd
from glob import glob


# --------------------------------------------------------------
# Read single CSV file
# --------------------------------------------------------------

single_file_acc = pd.read_csv("../../data/raw/MetaMotion/A-bench-heavy2-rpe8_MetaWear_2019-01-11T16.10.08.270_C42732BE255C_Accelerometer_12.500Hz_1.4.4.csv")
single_file_gyr = pd.read_csv("../../data/raw/MetaMotion/A-bench-heavy2-rpe8_MetaWear_2019-01-11T16.10.08.270_C42732BE255C_Gyroscope_25.000Hz_1.4.4.csv")
# --------------------------------------------------------------
# List all data in data/raw/MetaMotion
# --------------------------------------------------------------


files = glob("../../data/raw/MetaMotion/*.csv")
len(files)

# --------------------------------------------------------------
# Extract features from filename
# --------------------------------------------------------------
data_path = "../../data/raw/MetaMotion/"
f = files[1]

# Extracts the participant ID from the file path:
# 1. Split the file path at the first dash ("-") and take the part before it.
# 2. Remove the data_path prefix from that part so only the participant ID remains.
participant = f.split("-")[0].replace(data_path, "")

#label
label = f.split("-")[1]

#either light or heavy the set
# 1. Split the string `f` by the dash "-" into parts.
# 2. Take the third part (index 2).
# 3. Remove any trailing '1', '2', or '3' characters from the end of that part.

category = f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019") 

df = pd.read_csv(f)

df["partcipant"] = participant
df["label"] = label
df["category"] = category
# --------------------------------------------------------------
# Read all files
# --------------------------------------------------------------
acc_df = pd.DataFrame()
gyr_df = pd.DataFrame()

acc_set = 1
gyr_set = 1

for f in files:
    
    #Extracts the features
    participant = f.split("-")[0].replace(data_path, "")
    label = f.split("-")[1]
    category = f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019") 
    #Reads in a data frame
    df = pd.read_csv(f)
    
    df["partcipant"] = participant
    df["label"] = label
    df["category"] = category
    
    if "Accelerometer" in f:
        df["set"] = acc_set
        acc_set += 1
        acc_df = pd.concat([acc_df, df])
        
    if "Gyroscope" in f:
        df["set"] = gyr_set
        gyr_set += 1
        gyr_df = pd.concat([gyr_df, df])

#acc_df[acc_df["set"] == 1]    

# --------------------------------------------------------------
# Working with datetimes
# --------------------------------------------------------------
#uses unix time stamp as a form of standardisation

acc_df.info()

pd.to_datetime(df["epoch (ms)"], unit ="ms")

acc_df.index = pd.to_datetime(acc_df["epoch (ms)"], unit ="ms")

gyr_df.index = pd.to_datetime(gyr_df["epoch (ms)"], unit ="ms")

del acc_df["epoch (ms)"]
del acc_df["time (01:00)"]
del acc_df["elapsed (s)"]

del gyr_df["epoch (ms)"]
del gyr_df["time (01:00)"]
del gyr_df["elapsed (s)"]

# --------------------------------------------------------------
# Turn into function
# --------------------------------------------------------------
#Functions allows code to be more readable and less lines of code
files = glob("../../data/raw/MetaMotion/*.csv")

def read_data_from_files(files):

    acc_df = pd.DataFrame()
    gyr_df = pd.DataFrame()

    acc_set = 1
    gyr_set = 1

    for f in files:
        
        #Extracts the features
        participant = f.split("-")[0].replace(data_path, "")
        label = f.split("-")[1]
        category = f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019") 
        #Reads in a data frame
        df = pd.read_csv(f)
        
        df["partcipant"] = participant
        df["label"] = label
        df["category"] = category
        
        if "Accelerometer" in f:
            df["set"] = acc_set
            acc_set += 1
            acc_df = pd.concat([acc_df, df])
            
        if "Gyroscope" in f:
            df["set"] = gyr_set
            gyr_set += 1
            gyr_df = pd.concat([gyr_df, df])

    acc_df.index = pd.to_datetime(acc_df["epoch (ms)"], unit ="ms")

    gyr_df.index = pd.to_datetime(gyr_df["epoch (ms)"], unit ="ms")

    del acc_df["epoch (ms)"]
    del acc_df["time (01:00)"]
    del acc_df["elapsed (s)"]

    del gyr_df["epoch (ms)"]
    del gyr_df["time (01:00)"]
    del gyr_df["elapsed (s)"]

    return acc_df, gyr_df

acc_df, gyr_df = read_data_from_files(files)



# --------------------------------------------------------------
# Merging datasets
# --------------------------------------------------------------
data_merged = pd.concat([acc_df.iloc[:,:3], gyr_df], axis=1)

#data_merged.dropna(50)

data_merged.columns = [
    "acc_x",
    "acc_y",
    "acc_z",
    "gyr_x",
    "gyr_y",
    "gyr_z",
    "label",
    "category",
    "participant",
    "set",
]


# --------------------------------------------------------------
# Resample data (frequency conversion)
# --------------------------------------------------------------

# Accelerometer:    12.500HZ
# Gyroscope:        25.000Hz

sampling = {
    "acc_x": "mean",
    "acc_y": "mean",
    "acc_z": "mean",
    "gyr_x": "mean",
    "gyr_y": "mean",
    "gyr_z": "mean",
    "label": "last",
    "category": "last",
    "participant": "last",
    "set": "last",
}


data_merged[:1000].resample(rule="200ms").apply(sampling)
 
# Split by day
days = [g for n, g in data_merged.groupby(pd.Grouper(freq="D"))]

data_resampled = pd.concat([df.resample(rule="200ms").apply(sampling).dropna() for df in days])

data_resampled.info()

data_resampled["set"] = data_resampled["set"].astype("int")

# --------------------------------------------------------------
# Export dataset
# --------------------------------------------------------------
# Save the resampled dataset as a pickle to preserve pandas dtypes and index.
# This intermediate artifact allows fast loading in downstream analysis and modeling steps.
data_resampled.to_pickle("../../data/interim/01_data_processed.pkl")

# %%
