# Libraries
!pip install openeo rasterio  --quiet

# Imports
import os, zipfile, random, io
import numpy as np
import pandas as pd
import cv2
import rasterio
import openeo
from google.colab import files
from pathlib import Path

#  Upload kaggle.json
uploaded = files.upload()
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

#  Download & unzip dataset
!kaggle datasets download -d shambac/tum-sentinel-1-2 --unzip
!ls Sentinel_fall

# Upload CSV with all season coordinates
uploaded = files.upload()
csv_filename = list(uploaded.keys())[0]
roi_df = pd.read_csv(io.BytesIO(uploaded[csv_filename]))

#  Filter only Fall season rows
fall_df = roi_df[roi_df["Season"].str.lower() == "fall"].reset_index(drop=True)
print(f" Loaded {len(fall_df)} Fall coordinates from uploaded CSV.")


FALL_DIR = os.path.join("/content/tum-sentinel-1-2", "Sentinel_fall", "ROIs1970_fall")
YEAR = 2017

# Connect to Copernicus OpenEO
session = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
print(" Connected to OpenEO")

#  ORB Matching Function
def orb_match_score(img1, img2):
    try:
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)
        if des1 is None or des2 is None:
            return 0
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        return len(matches)
    except:
        return 0

# Process Each s2 Folder
results = []
s2_folders = sorted([f.path for f in os.scandir(FALL_DIR) if f.is_dir() and "s2_" in f.name])

for folder in s2_folders:
    folder_name = os.path.basename(folder)
    print(f"\n Processing {folder_name}...")

    images = [img for img in os.listdir(folder) if img.endswith(".png")]
    if not images:
        print(" No PNGs in", folder)
        continue

    target_img_name = random.choice(images)
    target_path = os.path.join(folder, target_img_name)
    target_img = cv2.imread(target_path, cv2.IMREAD_COLOR)
    if target_img is None:
        print(" Couldn't load target image:", target_img_name)
        continue

    best_score = 0
    best_img_arr = None
    best_coord = None
    best_collection = None

    
    for i, row in fall_df.iterrows():
        lat, lon = row["lat"], row["lon"]
        bbox = [lon - 0.1, lat - 0.1, lon + 0.1, lat + 0.1]

        try:
            s2_collection = session.load_collection(
                "SENTINEL2_L2A",
                spatial_extent={"west": bbox[0], "south": bbox[1], "east": bbox[2], "north": bbox[3]},
                temporal_extent=[f"{YEAR}-09-01", f"{YEAR}-11-30"],
                bands=["B04", "B03", "B02"]
            ).filter_bbox(west=bbox[0], south=bbox[1], east=bbox[2], north=bbox[3])

            s2_pngs = s2_collection.reduce_dimension(dimension='bands', reducer='mean').preview().get_data()

# Matching of Sentinel-2 and target image 
            for img in s2_pngs:
                img_arr = (np.array(img) * 255).astype(np.uint8)
                score = orb_match_score(target_img, img_arr)
                if score > best_score:
                    best_score = score
                    best_img_arr = img_arr
                    best_coord = (lat, lon)
                    best_collection = s2_collection
        except Exception as e:
            print(f" Error for coordinate ({lat},{lon}):", e)

    if best_collection is None:
        print(" No suitable match found for", folder_name)
        continue

    print(f" Best match score: {best_score}")

    try:
        job = best_collection.save_result(format="GTIFF")
        job_id = job.send_job().job_id
        job = session.job(job_id).start_and_wait()
        output_file = job.download_results()[0]

        with rasterio.open(output_file) as tif:
            bounds = tif.bounds
            center_lat = (bounds.top + bounds.bottom) / 2
            center_lon = (bounds.left + bounds.right) / 2

        hemisphere = "Northern" if center_lat >= 0 else "Southern"
        lat_abs = abs(center_lat)
        temp_zone = "Tropical" if lat_abs < 23.5 else "Temperate" if lat_abs < 66.5 else "Polar"

        for img_name in images:
            results.append({
                "s2_folder": folder_name,
                "image_name": img_name,
                "latitude": center_lat,
                "longitude": center_lon,
                "hemisphere": hemisphere,
                "temperature_zone": temp_zone,
                "match_score": best_score
            })

    except Exception as e:
        print(" Error during TIFF download or processing:", e)

# Save results
output_df = pd.DataFrame(results)
csv_output_path = "/content/Fall_ROI_results.csv"
output_df.to_csv(csv_output_path, index=False)
print("\n Final CSV saved at", csv_output_path)
files.download(csv_output_path)
