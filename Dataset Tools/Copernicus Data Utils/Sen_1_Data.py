from AuthClient import SessionData
from utils.aspectRatio import calculate_aspect_ratio
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

ratio = calculate_aspect_ratio(boxCoords[::-1])

img_height = 2500
# img_width = int(img_height * ratio)
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

# TODO Location data and season data

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
                        "from": "2024-11-29T23:59:59Z",
                        "to": "2024-12-01T00:00:00Z"
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
                    "type": "image/jpeg"
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
    with open("testImages/TestImageRes4.jpeg", 'wb') as fp :
        fp.write(response.content)
        print("Done saving file")
else :
    print(f"Response code: {response.status_code}")
    print(response.content)