import math

def getLatDiff(dist: float) -> float :
    # Assumption, distance is given in kilometers
    res = (1 / 110.574) * dist
    return res

def getLongDiff(dist: float, lat: float) -> float :
    latInRad = math.radians(lat)
    res = (1 / (111.320 * math.cos(latInRad))) * dist
    return res

def addLat(valA: float, valB: float) -> float :
    res = valA + valB
    if abs(res) > 90 :
        tmp = 90 - abs(res)
        res = -tmp if res > 0 else tmp

    return res

def addLong(valA: float, valB: float) -> float :
    res = valA + valB
    if abs(res) > 180 :
        tmp = 180 - abs(res)
        res = -tmp if res > 0 else tmp

    return res

def getCoords(initLong: float, initLat: float) -> tuple[list[float | list[float]]] :
    # Step 1
    # Coords 50KM East
    NELat = initLat
    NELong = addLong(initLong, getLongDiff(50, NELat))

    # Step 2
    # 50 KM South from last pos
    SELat = addLat(NELat, -getLatDiff(50))
    SELong = NELong

    # Step 3
    # 50 KM West from last pos
    SWLat = SELat
    SWLong = addLong(SELong, -getLongDiff(50, SWLat))

    allCoords = [[SWLong, SWLat], [SELong, SELat], [NELong, NELat], [initLong, initLat]]
    bbox = [SELong, SELat, initLong, initLat]

    return (allCoords, bbox)

if __name__ == "__main__" :
    initLong = 0
    initLat = 0

    allCoords, bbox = getCoords(initLong, initLat)

    print(f'allCoords: {allCoords}')
    print(f'\nBbox: {bbox}')