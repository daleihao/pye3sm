#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system import define_global_variables
from eslib.system.define_global_variables import *


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree


def elm_save_variable_wrap(iCase_index):   
    sCase = "{:0d}".format(iCase_index)   
    elm_save_variable_halfdegree(sFilename_configuration, iCase_index,\
         iYear_start_in = 1980, \
            iYear_end_in = 2008,  \
         iFlag_same_grid_in = 1,\
              sDate_in = sDate)

if __name__ == '__main__':
    #parser = argparse.ArgumentParser()        
    #parser.add_argument("--iIndex_start", help = "the path",   type = int)      
    #parser.add_argument("--iIndex_end", help = "the path",   type = int)          
    #pArgs = parser.parse_args()       
    #iIndex_start = pArgs.iIndex_start
    #iIndex_end = pArgs.iIndex_end
    sModel = 'h2sc'
    sRegion = 'global'
    
    sDate = '20200212'
    sVariable = 'ZWT'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
            + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    
    #start loop
    iIndex_start =1
    iIndex_end = 1
    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end


    #iCase_index_start = int (config['iCase_index_start'] )
    #iCase_index_end = int (config['iCase_index_end'] )

    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240       
    for iCase_index in (aCase_index):
        sCase = "{:03d}".format(iCase_index)
        elm_save_variable_wrap(iCase_index)
    
    
    print('finished')