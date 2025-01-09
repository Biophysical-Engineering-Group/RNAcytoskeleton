import argparse
import numpy as np
from scipy.optimize import curve_fit
from oxDNA_analysis_tools.UTILS.RyeReader import describe, strand_describe, linear_read
import math
import csv
import pandas as pd

#Read the arguments
def parse_list(arg):
    # Convert a comma-separated string to a list of integers
    return [int(x) for x in arg.split(',')]

def cli_parser(prog="persistencelength_simulation.py"):
    parser = argparse.ArgumentParser(prog=prog, description="Process 1um long filament (helical pitch and persistence length)")
    parser.add_argument('trajectory', type=str)
    parser.add_argument('topology', type=str)
    parser.add_argument('tile_per_layer', type=int)
    parser.add_argument('--remove', type=float, 
                        default=None, 
                        help="portion to remove from each end (e.g 0.1 (for 10%))")
    parser.add_argument('--start_positions', type=parse_list,
                        default=None, 
                        help="Comma-separated list of start positions (e.g. 0,5)."
                        )
    parser.add_argument('--end_positions', type=parse_list,
                        default=None, 
                        help="Comma-separated list of end positions (e.g. 0,5)."
                        )
    return parser


#Read the topology and generate id list
def read_traj(top, tpl, remove, start_positions, end_positions):
    #Get tile and filament info
    sy, ele = strand_describe(top)
    tile_len = sy.strands[0].get_length() #Get 1 tile (1 strand) length
    nb_layer = len(sy.strands)//tpl #get number of layers
    if nb_layer*10%10 != 0:
        raise ValueError("nb_layer is not an integer") 

    #get tile id list as an array of format [[tile0 ids],[tile1 ids],[tile2 ids],etc...]
    tile_idlist = [np.arange(tile_len*i,tile_len*(i+1)) for i in range (len(sy.strands))]
    

    #Take into account only the chosen part of each tile from arguments     
    tile_sliced = []
    if start_positions is None or end_positions is None:
        print('No slicing defined, the whole tile is taken into calculations')
        tile_sliced = tile_idlist
    else: 
        if len(start_positions) != len(end_positions):
            raise ValueError("Start and end positions arrays must have the same length")
        print('Positions (start array, end array) below are taken into calculation:',start_positions, end_positions)
        for i in range(0, len(sy.strands)):
            sliced_array = []
            for start, end in zip(start_positions, end_positions):
                sliced_array.extend(tile_idlist[i][start:end+1])
            tile_sliced.append(sliced_array)

    #get layer id list based on tile_idlist
    layer_idlist=[]
    for i in range(0, len(sy.strands), tpl):
        merged_array = []
        for j in range(i, i+tpl):
            merged_array.extend(tile_sliced[j])
        layer_idlist.append(merged_array)

    #Remove a percentage of layers from the two ends
    if remove is None:
        print('No slicing defined, the whole filament is taken into calculations')
        layer_removed = layer_idlist
    else: 
        print('Each end of the filament is removed of ',remove*100, 'percent')
        beginslice=round(remove*nb_layer)
        endslice=nb_layer-beginslice
        layer_removed = layer_idlist[beginslice:endslice]
        tile_sliced = tile_sliced [beginslice*tpl:endslice*tpl]
    #return tile and layer id list
    return tile_sliced,layer_removed


#math function for MSED method
def contourlength(coords):
    deltalist = np.linalg.norm(np.diff(coords, axis=0), axis=1)
    length = np.sum(deltalist)
    return length, deltalist

def meansq(coords, s=1):
    def plRsq(x,P):
        return 2*s*P*x*(1-(s*P/x*(1-np.exp(-x/(s*P)))))
    Rsq=[]
    contour=[]
    n = len(coords)
    length, deltalist = contourlength(coords)
    for i in range (0,n-2):
        for j in range (i+2,n):
            Rsq.append(np.linalg.norm(coords[j]-coords[i])**2)
            contour.append(np.sum(deltalist[i:j]))

     
    testpl, cov = curve_fit(plRsq, contour, Rsq) 
    # print(design,testpl)
    fit_y = plRsq(np.array(contour),testpl)
    #Remove outlier
    # Calculate residuals
    residuals = Rsq - fit_y
    # print(residuals)

    # Calculate mean and standard deviation of residuals
    mean_residuals = np.mean(residuals)
    std_residuals = np.std(residuals)
    #  Mask data points where residuals > 1 * std_residuals
    mask = np.abs(residuals) <= 1*std_residuals
    # Apply mask to x and y
    x_masked = np.asarray(contour)[mask]
    y_masked = np.asarray(Rsq)[mask]
    #Plot the masked data
    pl, covariance =curve_fit(plRsq, x_masked, y_masked) 
    std = (np.sqrt(np.diag(covariance)))
    # print(testpl_mask,np.sqrt(np.diag(cov_mask)))
    # fit_y_masked = plRsq(np.array(x_masked),testpl_mask)
  

    print(pl,std,s)
    return pl, std, contour, Rsq  

#process function to get persistence length and helical pitch
def process(traj,tile,layer,tpl):
    # cos=[]
    pl_mean =[]
    std_mean = []

    #read top and traj
    top_info, traj_info = describe(None, traj)
    #process
    for chunk in linear_read(traj_info, top_info):
        for conf in chunk:
            # Calculate midpoint of each tile and layer
            m_tile = np.array([np.mean(conf.positions[ntile], axis=0) for ntile in tile])
            m_layer = np.array([np.mean(conf.positions[nlayer], axis=0) for nlayer in layer])

            # #calculate helical pitch
            # for i in range (tpl*2):
            #     vector=[] #vector pointing from midlayer to midtile
            #     step_length=[] #length of one step from layer of tile to layer of tile+tpl*2 (2 because the design repeats the position every 2 layer)
            #     for j in range(i,len(tile),tpl*2):
            #         vector.append((m_tile[j]-m_layer[j//tpl])/np.linalg.norm(m_tile[j]-m_layer[j//tpl]))
            #     for j in range(len(layer)//2):
            #         step_length.append(np.linalg.norm(m_layer[j+2]-m_layer[j]))
            # for k in range(len(vector)-1):
            #     #calculate cos(angle) between two consecutive vectors
            #     cos_temp=(np.dot(vector[k+1],vector[k])/(np.linalg.norm(vector[k])*np.linalg.norm(vector[k+1])))
            #     #append into a list
            #     cos.append(cos_temp)
            
            #calculate pl_length
            plength, std, contour, y_axis = meansq(m_layer, s=1)
            pl_mean.append(plength)
            std_mean.append(std)
    return pl_mean, std_mean


#main
def main():
    parser = cli_parser()
    args = parser.parse_args()
    
    #pass in arguments
    traj = args.trajectory
    top = args.topology
    tpl = args.tile_per_layer
    remove = args.remove
    start_positions = args.start_positions
    end_positions = args.end_positions

    #process
    tile, layer = read_traj(top, tpl, remove, start_positions, end_positions)
    pl_mean, std_mean = process(traj,tile,layer,tpl)
    #change cos list to angle list and write into a csv
    # final_angles = [math.degrees(math.acos(cos_value)) for cos_value in cos]

    # Write both persistence length list and angle list into csv file
    # with open('final_angles.csv', 'w', newline='') as csvfile1:
    #     writer1 = csv.writer(csvfile1)
    #     writer1.writerow(['Helical_pitch[deg]'])  # Write header
    #     for item in final_angles:
    #         writer1.writerow([item])
    

    # with open('plength_traj.csv', 'w', newline='') as csvfile2:
    #     writer2 = csv.writer(csvfile2)
    #     writer2.writerow(['plength[a.u]'])  # 1 unit of length = 0.8518 nm
    #     for item in pl_mean:
    #         writer2.writerow([item])
    df = pd.DataFrame({"plength": pl_mean, "std": std_mean})
    df.to_csv("new_plength_traj.csv",index=False)

if __name__ == '__main__':
    main()
