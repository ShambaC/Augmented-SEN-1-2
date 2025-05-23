var greenland = ee.Geometry.Rectangle([-52, 74, -48, 75]); // Autumn (September, 2024)
var china = ee.Geometry.Rectangle([97, 31, 107, 37]); // Summer (April, 2023)
var australia = ee.Geometry.Rectangle([120, -28, 125, -23]); // Spring (October, 2022)
var namibia = ee.Geometry.Rectangle([15, -25, 19, -20]); // Winter (May, 2023)
var argentina = ee.Geometry.Rectangle([-71, -49, -67, -45]); //Summer (December, 2020)
var kazakhstan = ee.Geometry.Rectangle([67, 44, 75, 48]); //Spring (March, 2019)
var northUS = ee.Geometry.Rectangle([-116, 51, -109, 55]); // Winter (January, 2021)
 
// Define the regions with their corresponding season and date ranges
var regions = [
  { name: "Greenland", region: greenland, folder_name: '146', season: "Autumn", startDate: '2023-09-01', endDate: '2023-09-30' },
  { name: "China", region: china, folder_name: '142', season: "Summer", startDate: '2023-04-01', endDate: '2023-04-30' },
  { name: "Australia", region: australia, folder_name: '149', season: "Spring", startDate: '2022-10-01', endDate: '2022-10-31' },
  { name: "Namibia", region: namibia, folder_name: '147', season: "Winter", startDate: '2023-05-01', endDate: '2023-05-31' },
  { name: "Argentina", region: argentina, folder_name: '142', season: "Summer", startDate: '2020-12-01', endDate: '2020-12-31' },
  { name: "Kazakhstan", region: kazakhstan, folder_name: '149', season: "Spring", startDate: '2019-03-01', endDate: '2019-03-31' },
  { name: "North America", region: northUS, folder_name: '147', season: "Winter", startDate: '2021-01-01', endDate: '2021-01-31' }
];
 
// Function to determine temperature zone based on latitude
function getTemperatureZone(lat) {
  if (lat <= 23.5 && lat >= -23.5) {
    return "Tropical";
  }
  else if ((lat > 23.5 && lat <= 66.5) || (lat < -23.5 && lat >= -66.5)) {
    return "Temperate";
  }
  else {
    return "Arctic";
  }
}
 
// Function to generate Sentinel-1 and Sentinel-2 mosaics and export them
function exportMosaic(area, regionInfo, latInfo, idx) {
  var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
           .filterBounds(area)
           .filterDate(regionInfo.startDate, regionInfo.endDate)
           .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
           .filter(ee.Filter.eq('instrumentMode', 'IW'))
           .select('VV')
           .mosaic();
 
  var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
           .filterBounds(area)
           .filterDate(regionInfo.startDate, regionInfo.endDate)
           .select(['B4','B3', 'B2'])
           .mosaic();
  
  var thumbParams = {
    region: area,
    dimensions: 256,
    format: 'png'
  };

  var s1_thumb = null;
  var s2_thumb = null;

  // Generate Sentinel-1 thumbnail if not empty
  if (s1.bandNames().size().getInfo() > 0) {
    s1_thumb = s1.visualize({bands: ['VV'], min: -25, max: 0}).getThumbURL(thumbParams);
  } else {
    s1_thumb = "No Image Available";
  }

  // Generate Sentinel-2 thumbnail if not empty
  if (s2.bandNames().size().getInfo() > 0) {
    s2_thumb = s2.visualize({bands: ['B4','B3','B2'], min: 500, max: 3500}).getThumbURL(thumbParams);
  } else {
    s2_thumb = "No Image Available";
  }

  return [s1_thumb, s2_thumb];
}
 
var k = 0;
 
// Function to generate labeled points for a given region
function generateSamples(regionInfo, numPoints) {
  var samplePoints = ee.FeatureCollection.randomPoints(regionInfo.region, numPoints).toList(500).getInfo();
  print(samplePoints);
  
  var featCol = [];
 
  for (var i = 0; i < samplePoints.length; i++) {
    var point = samplePoints[i];
    k += 1;
    print(point);
    // Get latitude
    var lat = point.geometry.coordinates[1];
    
    // Define a 256x256 pixel bounding box (scale: 20m for Sentinel-2)
    var bufferSize = 5120; // 256 pixels * 20m per pixel
    var pointBuffer = ee.Geometry.Point(point.geometry.coordinates).buffer(bufferSize).bounds();
 
    var latInfo = getTemperatureZone(lat);
    var linkList = exportMosaic(pointBuffer, regionInfo, latInfo, k);
    
    if (linkList === null) {
      continue;
    }
    
    print(linkList);
 
    var feat = ee.Feature(point.geometry, {
      'sentinel1_filePath': regionInfo.season + '/s1_' + regionInfo.folder_name + '/' + regionInfo.season + '_img_' + latInfo + '_p' + k + '.png', 
      'sentinel2_filePath': regionInfo.season + '/s2_' + regionInfo.folder_name + '/' + regionInfo.season + '_img_' + latInfo + '_p' + k + '.png',
      'prompt': 'Season: ' + regionInfo.season + ' Region: ' + latInfo,
      's1_thumb': linkList[0],
      's2_thumb': linkList[1]
    });
    
    print(feat);
    
    featCol.push(feat);
  }
  print(featCol);
  
  return ee.FeatureCollection(featCol);
}
 
// Generate samples for all regions
var allSamples0 = ee.FeatureCollection(generateSamples(regions[0], 200));
var allSamples1 = ee.FeatureCollection(generateSamples(regions[1], 200));
var allSamples2 = ee.FeatureCollection(generateSamples(regions[2], 200));
var allSamples3 = ee.FeatureCollection(generateSamples(regions[3], 200));
var allSamples4 = ee.FeatureCollection(generateSamples(regions[4], 200));
var allSamples5 = ee.FeatureCollection(generateSamples(regions[5], 200));
var allSamples6 = ee.FeatureCollection(generateSamples(regions[6], 200));

var allSamples = allSamples0
  .merge(allSamples1)
  .merge(allSamples2)
  .merge(allSamples3)
  .merge(allSamples4)
  .merge(allSamples5)
  .merge(allSamples6)

print(allSamples);
 
// Export the dataset as CSV to Google Drive
Export.table.toDrive({
  collection: allSamples,
  description: 'Sentinel_Image_Samples',
  fileFormat: 'CSV',
});