from pathlib import Path
from tqdm import tqdm

import pandas as pd
import cv2 as cv

df = pd.read_csv("./Images/prompts_150.csv")
promptList = []

outputFolder_s1 = Path(df.iloc[0].s1_fileName).parent.__str__()
Path(f"../../Dataset/{outputFolder_s1}").mkdir(parents=True, exist_ok=True)
outputFolder_s2 = Path(df.iloc[0].s2_fileName).parent.__str__()
Path(f"../../Dataset/{outputFolder_s2}").mkdir(parents=True, exist_ok=True)

k = 0
for idx, row in tqdm(df.iterrows(), total=df.shape[0]) :

    s1_image = cv.imread(f"Images/{row.s1_fileName}")
    s2_image = cv.imread(f"Images/{row.s2_fileName}")

    extracted_info = row.s1_fileName.split('/')[-1].split('_')
    season = extracted_info[0]
    region = extracted_info[2]

    for i in tqdm(range(81), leave=False) :

        k += 1

        x = i % 9   # Move columns
        y = i // 9   # Move rows

        crop_s1 = s1_image[256*x : 256*(x+1), 256*y : 256*(y+1)]
        crop_s2 = s2_image[256*x : 256*(x+1), 256*y : 256*(y+1)]

        cv.imwrite(f"../../Dataset/{outputFolder_s1}/{season}_img_{region}_p{k}.png", crop_s1)
        cv.imwrite(f"../../Dataset/{outputFolder_s2}/{season}_img_{region}_p{k}.png", crop_s2)

        promptList.append([
            f"{outputFolder_s1}/{season}_img_{region}_p{k}.png",
            f"{outputFolder_s2}/{season}_img_{region}_p{k}.png",
            row.prompt
            ])
        
prompt_df = pd.DataFrame(promptList, columns=["s1_fileName", "s2_fileName", "prompt"])
prompt_df.to_csv("../../Dataset/fall/prompts_150.csv", index=False)

print("DONE")