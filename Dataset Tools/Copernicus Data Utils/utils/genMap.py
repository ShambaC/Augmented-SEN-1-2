import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from matplotlib.patches import Rectangle

regions = [
    (69, -54, 62, -40),
    (110.53, 44.12, 108.25, 44.99),
    (-10, 110, -45, 155),
    (-15, 10, -35, 40),
    (-45.45, 53.48, -109.44, 66.68),
    (-20, -58, -1, 37),
    (52, 63, 43, 77),
    (61, -122, 42, -101),
    (3.837160765147294, 101.02924793136883, 2.4879317744244784, 102.77607410324383),
    (40.17147954557868, 69.06685797151498, 37.65007089513811, 73.36251226838998),
    (28.718101270763515, 68.53721319020808, 25.552799970763516, 77.99638789020796),
    (-28.121675224583992, 114.98501992533467, -33.734642679244914, 123.5323832065846),
    (-1.2116032492636872, 21.534222209485957, -5.356704864626569, 25.906780803235957),
    (-45.515152695647686, -71.23516634588509, -46.75976200006818, -73.24017122869759)
]

fig = plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

ax.coastlines()
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

for lat1, lon1, lat2, lon2 in regions :
    width = lon2 - lon1
    height = lat2 - lat1

    rect = Rectangle((lon1, lat2), width, height, linewidth=2, facecolor='blue', transform=ccrs.PlateCarree())
    ax.add_patch(rect)

plt.title("Map")
plt.show()