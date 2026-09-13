// Sentinel-2 NDVI + NDWI for Tana River upper basin, last 12 months
var tanaBasin = ee.FeatureCollection('WWF/HydroSHEDS/v1/Basins/hybas_7')
  .filterBounds(ee.Geometry.Point([37.65, -0.35])); // adjust to actual basin polygon

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(tanaBasin)
  .filterDate(ee.Date(Date.now()).advance(-12, 'month'), ee.Date(Date.now()))
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

var addIndices = function(img) {
  var ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI');
  return img.addBands([ndvi, ndwi]);
};

var indexed = s2.map(addIndices);

Export.table.toDrive({
  collection: indexed.select(['NDVI', 'NDWI']).getRegion(tanaBasin, 10),
  description: 'tana_basin_ndvi_ndwi_export',
  fileFormat: 'GeoJSON'
});
