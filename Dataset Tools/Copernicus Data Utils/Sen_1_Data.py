from AuthClient import SessionData
from utils.calcCoords import getCoords

oauth, token = SessionData

IW_COLLECTION_ID = 'byoc-3c662330-108b-4378-8899-525fd5a225cb'
INITIAL_LONGITUDE = 75.41529108199907
INITIAL_LATITUDE = 27.136261288968445

coords_data = getCoords(INITIAL_LONGITUDE, INITIAL_LATITUDE)

# Earth engine format
# Coords are in (longitude, latitude) format
boxCoords = coords_data[0]

########################################################################
#                       IMAGE PROPERTIES                               #
########################################################################

img_height = 2500
img_width = 2500

bbox = coords_data[1]

evalScript = """
//VERSION=3
function setup() {
    return {
        input: ["VV"],
        output: { bands: 1 }
    };
}

function evaluatePixel(sample) {
    return [sample.VV];
}

"""

########################################################################
#                    LOCATION AND SEASON DATA                          #
########################################################################

import pandas as pd
from pathlib import Path

season_map = {}

season = "winter"
region = ""

Path(f"./Images/{season}").mkdir(parents=True, exist_ok=True)

if INITIAL_LATITUDE <= 23.5 and INITIAL_LATITUDE >= -23.5 :
    region = "tropical"
elif (INITIAL_LATITUDE > 23.5 and INITIAL_LATITUDE < 66.5) or (INITIAL_LATITUDE < -23.5 and INITIAL_LATITUDE > -66.5) :
    region = "temperate"
else :
    region = "arctic"

# TODO Implement looping on coords
fileName = f"Images/{season}/img_{region}_0.png"

########################################################################
#                              REQUEST                                 #
########################################################################

request = {
    "input": {
        "bounds": {
            "bbox": bbox
        },
        "data": [
            {
                "dataFilter": {
                    "timerange": {
                        "from": "2023-11-29T23:59:59Z",
                        "to": "2024-01-01T00:00:00Z"
                    }
                },
                "type": IW_COLLECTION_ID
            }
        ]
    },
    "output": {
        "width": img_width,
        "height": img_height,
        "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/png"
                }
            }
        ]
    },
    "evalscript": evalScript
}

url = "https://sh.dataspace.copernicus.eu/api/v1/process"
response = oauth.post(url, json=request)

if response.ok :
    print("Response OK")
    with open(fileName, 'wb') as fp :
        fp.write(response.content)
        print("Done saving file")
else :
    print(f"Response code: {response.status_code}")
    print(response.content)