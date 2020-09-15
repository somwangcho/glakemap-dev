
# -------------------Process S1 Data-----------------------#

import time
start_time = time.time()
from dirext.dirextmngmt import DirMngmt
from sentinel1.s1processor import ProcessSARData
from sentinel1.s1processor import Reprojections
from sentinel1.s1processor import MosaicDatastet
dir_path = "E:\Poiqu_GL\Poiqu" # Change the file path
directory = DirMngmt(dir_path, '', '','')
main_directory = directory.main_direc()
print(main_directory)



band_polarisation = ['VV'] # Add the band polarisation to be processed. Also supports multi-polarisation e.g. ['VV', 'VH']
process_data = ProcessSARData(main_directory, "Sentinel1", "s1_unziped_data", 's1_processed_data', ".zip", ".safe", band_polarisation)
process_data.makefolders()                   
process_data.unzipfiles()
process_data.process_sar_data()



from sptref.spatialref import SpatialReference
spatial_ref = SpatialReference()
gcs = spatial_ref.gcs(4326)
pcs = spatial_ref.pcs(32645)
processed_band_pol2 = ['_VV_db.img'] # Add the band polarisation to be processed. Also supports multi-polarisation e.g. ['_VV_db.img', '_VH_db.img']
repro = Reprojections(main_directory, "Sentinel1", "s1_unziped_data", 's1_processed_data', '', '', processed_band_pol2, gcs)
repro.reprojection()



from sptref.spatialref import SpatialReference
spatial_ref = SpatialReference()
gcs = spatial_ref.gcs(4326)
pcs = spatial_ref.pcs(32645)
filter_dB = ['*_VV_db_COPY.tif'] # Add the band polarisation to be processed. Also supports multi-polarisation e.g. ['*_VV_db_COPY.tif', '*_VH_db_COPY.tif']
mosaic_data = MosaicDatastet(main_directory, "Sentinel1", "s1_unziped_data", 's1_processed_data', '', '', filter_dB, gcs)
mosaic_data.makefolders()
mosaic_data.mosaic()



# -------------------Process S2 Data-----------------------#

import os
import time
from sentinel2.s2processor import CalculateNDWI
from sentinel2.s2processor import MosaicNDWIData
from sptref.spatialref import SpatialReference

dir_path = "E:\Poiqu_GL\Poiqu" # Change the file path
from dirext.dirextmngmt import DirMngmt
directory = DirMngmt(dir_path, '', '','')
main_directory = directory.main_direc()
print(main_directory)
os.listdir(main_directory)

start_time = time.time()



dir_mngmt = CalculateNDWI(main_directory, 'Sentinel2', 's2_unziped_data', 's2_processed_data', '.zip', '_MSIL1C.xml', '')
dir_mngmt.makefolders()
dir_mngmt.unzipfiles()
dir_mngmt.calculate_ndwi()



spatial_ref = SpatialReference()
gcs = spatial_ref.gcs(4326)
pcs = spatial_ref.pcs(32645)
extens = ['Green.tif', 'Blue.tif'] # Static
mosaic_extens = MosaicNDWIData(main_directory, 'Sentinel2', 's2_unziped_data', 's2_processed_data', '', extens, '')
mosaic_extens.makefolders()
mosaic_extens.list_files()
mosaic_extens.mosaic_ndwi(gcs)

end_time = time.time()
print('Time taken to process Sentinel-2 data: {} minutes'.format((end_time-start_time)/60))


# -------------------Process Dem Data-----------------------#

import os
dir_path = "E:\Poiqu_GL\Poiqu" # Change the file path
from dirext.dirextmngmt import DirMngmt
directory = DirMngmt(dir_path, '', '','')
main_directory = directory.main_direc()
print(main_directory)
os.listdir(main_directory)


from dem.demprocessor import MoveDemFiles
move_files = MoveDemFiles(main_directory, "Dem", "dem_unziped_data", 'dem_processed_data', ".zip", ".hgt", '')
src_dir = r'C:\\Users\\Sonam\\.snap\\auxdata\\dem\\SRTM 1Sec HGT'
move_files.move_over(src_dir, 'test')



from dem.demprocessor import DemProcessor
from sptref.spatialref import SpatialReference
spatial_ref = SpatialReference()
gcs = spatial_ref.gcs(4326)
pcs = spatial_ref.pcs(32645)

dem = DemProcessor(main_directory, "Dem", "dem_unziped_data", 'dem_processed_data', ".zip", ".hgt", '')
dem.unzipfiles()
dem.makefolders()
dem.mosaic_dem_cal_slp('SRTM1_GDB.gdb', 'SRTM1_Mosaic', 'SRTM1_Mosaiced.tif', gcs, 'SRTM1_Slope', 'SRTM1_Slope.tif', 0.00001036)



# -------------------Rule-based ImgSeg-----------------------#
import os
dir_path = "E:\Poiqu_GL\Poiqu" # Change the file path
from dirext.dirextmngmt import DirMngmt
directory = DirMngmt(dir_path, '', '','')
main_directory = directory.main_direc()
print(main_directory)
os.listdir(main_directory)

from imgseg.imgseg import ReadDatasets
from imgseg.imgseg import Thresholds
from imgseg.imgseg import RuleBasedSegmentation
from sptref.spatialref import SpatialReference as spt
from imgseg.imgseg import GlacierDataset as gd

data = ReadDatasets(main_directory, "rule-imgseg", "", "", "", "", "")
data.makefolders()
def reading_data(file_exten):
       try:
              return data.read_data(file_exten)
              
       except UnboundLocalError:
              print("------------> {} File NOT found!\n".format(file_exten))


sar_data = reading_data('_VV.tif')
ndwi_blue_data = reading_data('NDWI_Mosaiced_Blue.tif')
ndwi_green_data = reading_data('NDWI_Mosaiced_Green.tif')

# slope_data = reading_data('Resam_SRTM1_Slope.tif')

thresh = Thresholds()

ndwi_bluet = thresh.threshold(0.5)
ndwi_green_t1 = thresh.threshold(0.3)
ndwi_green_t2 = thresh.threshold(0.05)
backscattert = thresh.threshold(-14.0)

# glacier_path = gd.glacier_data("F:\datasets\Glacier_data\glims_db_20200630\glims_polygons.shp")

glacier_path = gd.glacier_dir("E:\Glacier_GL_Data\GLIMS\glims_db_20190530\glims_polygons.shp")
lake_size = 0.05 # in km2
lake_searh_distance = 10000 # in meter

ruleimgseg = RuleBasedSegmentation(main_directory, "rule-imgseg", "raster2polygon", "", spt.pcs(32645), spt.gcs(4326), glacier_path, lake_size, lake_searh_distance)

ruleimgseg.makefolders()
ruleimgseg.rule_based_imgseg('Glacial_Lakes_Segmented.tif', ndwi_blue_data, ndwi_green_data, sar_data,
ndwi_bluet, ndwi_green_t1, ndwi_green_t2, backscattert)




""""
#...............................
       #sub modules
# import MosaicS2Data
#............................... 
import DataForDEM # Check Sentinel2DataProcessing.py
 
import DemDataProcessing
#********************Main and Post-Processing********************#

import RuleBasedSegmentation
#...............................
       #sub modules
#import Zonal_Stat_App

#import Zonal_Stat_Train
#...............................  

#Change Python Environemnt: Random Forest (Python 37)
#Perform Random forest classification
import random_forest_classification_csv_V0  # for building model 

import GLakeMap_Model_Prediction  # for predicting class label

#Change Python Environemnt back to Python 27 64 bit
#Append Random Forest Predictions (value==1) and select polygons

#import Append_Pred_V0

#----------------------------------------------------------------------------------------------
from Append_Pred_V1 import Convert_shp_to_CSV
from Append_Pred_V1 import Extract_glacial_lakes
from Append_Pred_V1 import CSV_filepath_direc

from Append_Pred_V1 import Convert_To_CSV_File

from Append_Pred_V1 import*
from MainDirectory import MainDirectory
main_directory=MainDirectory()#Main_Directory

shp_to_csv = Convert_shp_to_CSV(main_directory, "Data_predicted.csv", 'Location_V0.shp')

csv_file, shp_file = shp_to_csv.read_pred_csv_file()

egl = Extract_glacial_lakes(main_directory, shp_file, csv_file, 'RasterToPolygon', 'Swiss_Alps_gl.shp')
sa = egl.selectAnalysis()

cfd = CSV_filepath_direc(main_directory, "Predicted_Dataset")
out_dir, f_dir, f_na = cfd.csv_file_name()
print(out_dir)

ctcf = Convert_To_CSV_File(sa, out_dir, f_na + ".csv")
out_csv_file = ctcf.csv_file()
print(out_csv_file)
