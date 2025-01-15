import numpy as np
import argparse
import matplotlib.pyplot as plt
from copy import deepcopy
from sklearn.decomposition import PCA
from oxDNA_analysis_tools.UTILS.RyeReader import describe, strand_describe, get_confs, inbox, write_conf, write_top
from oxDNA_analysis_tools.UTILS.data_structures import System, Configuration

def cli_parser(prog="assemble_filament.py"):
    parser = argparse.ArgumentParser(prog=prog, description="Assemble tiles into a tube")
    parser.add_argument('configuration', type=str)
    parser.add_argument('topology', type=str)
    parser.add_argument('n_layers', type=int)
    parser.add_argument('tiles_per_layer', type=int)
    parser.add_argument('filament_radius', type=float)
    return parser

def align_vectors(v1, v2):
    #https://stackoverflow.com/a/59204638/9738112
    v1 = v1/np.linalg.norm(v1)
    v2 = v2/np.linalg.norm(v2)

    v = np.cross(v1, v2)
    c = np.dot(v1, v2)
    s = np.linalg.norm(v)

    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rot = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rot

def get_rotation_matrix(angle):
    # rotates around the x-axis
    r = np.array([
        [1, 0, 0], 
        [0, np.cos(angle), -np.sin(angle)],
        [0, np.sin(angle), np.cos(angle)]
    ])

    return r

def get_z_rotation(angle):
    # rotates around the z-axis
    r = np.array ([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0], 
        [0, 0, 1]
    ])

    return r

def get_y_rotation(angle):
    # rotates around the y-axis
    r = np.array ([
        [np.cos(angle), 0, np.sin(angle)],
        [0, 1, 0],
        [-np.sin(angle), 0, np.cos(angle)], 
        
    ])

    return r

def main():
    parser = cli_parser()
    args = parser.parse_args()

    conf_file = args.configuration
    top_file = args.topology
    nl = args.n_layers
    tpl = args.tiles_per_layer
    radius = args.filament_radius

    ti, di = describe(top_file, conf_file)
    sys, ele = strand_describe(top_file)
    conf = get_confs(ti, di, 0, 1)[0]
    conf = inbox(conf, center=True)

    # Let's assume the tile is roughly rectangular so PCA will give us the axis
    pca = PCA(n_components=2).fit(conf.positions)
    pc1 = pca.components_[0] * pca.explained_variance_[0]
    pc2 = pca.components_[1] * pca.explained_variance_[1]

    #fig = plt.figure()
    #ax = fig.add_subplot(projection='3d')
    #ax.scatter(conf.positions.T[0], conf.positions.T[1], conf.positions.T[2])
    #ax.plot([0, pc1[0]], [0, pc1[1]], [0, pc1[2]], label='pc1')
    #ax.plot([0, pc2[0]], [0, pc2[1]], [0, pc2[2]], label='pc2')
    #plt.legend()
    #plt.show()

    # Align pc1 to the x-axis and pc2 to the y
    r1 = align_vectors(pc1, np.array([1, 0, 0]))
    pc2 = r1.dot(pc2)
    r2 = align_vectors(pc2, np.array([0, -1, 0]))
    r = r2@r1
    conf.positions = (r@conf.positions.T).T
    conf.a1s = (r@conf.a1s.T).T
    conf.a3s = (r@conf.a3s.T).T

    r3 = get_rotation_matrix(-3*np.pi/12)
    r4 = get_y_rotation(np.pi/15)
    r5 = get_z_rotation(np.pi/22)

    r = r4@r5@r3
    conf.positions = (r@conf.positions.T).T
    conf.a1s = (r@conf.a1s.T).T
    conf.a3s = (r@conf.a3s.T).T

    #pc1 = r.dot(pc1)
    #pc2 = r2.dot(pc2)
    #fig = plt.figure()
    #ax = fig.add_subplot(projection='3d')
    #ax.scatter(conf.positions.T[0], conf.positions.T[1], conf.positions.T[2])
    #ax.plot([0, pc1[0]], [0, pc1[1]], [0, pc1[2]], label='pc1')
    #ax.plot([0, pc2[0]], [0, pc2[1]], [0, pc2[2]], label='pc2')
    #plt.legend()
    #plt.show()

    #write_conf('axes.dat', conf, False)

    # create new system
    n_tiles = nl * tpl
    new_conf = Configuration(0, np.array([1000, 1000, 1000]), np.array([0, 0, 0]), np.empty((ti.nbases*n_tiles, 3)), np.empty((ti.nbases*n_tiles, 3)), np.empty((ti.nbases*n_tiles, 3)))
    new_sys = System([])

    # tile offset
    angle = 2 * np.pi / tpl
    x_offset = np.linalg.norm(pc1)

    # insert tiles into the system
    for i in range(n_tiles):
        tile = deepcopy(conf)
        tile.positions += np.array([(np.floor(i/tpl)*x_offset), 0, radius])
        r = get_rotation_matrix(angle * (i%tpl) + (angle / 2 * (np.floor(i/tpl)%2)))
        tile.positions = tile.positions @ r 
        tile.a1s = tile.a1s @ r
        tile.a3s = tile.a3s @ r

        new_conf.positions[i*ti.nbases:i*ti.nbases+ti.nbases] = tile.positions
        new_conf.a1s[i*ti.nbases:i*ti.nbases+ti.nbases] = tile.a1s
        new_conf.a3s[i*ti.nbases:i*ti.nbases+ti.nbases] = tile.a3s

        new_sys.append(deepcopy(sys.strands[0]))
          
    write_conf('filament.dat', new_conf, False)
    write_top('filament.top', new_sys, True)

if __name__ == "__main__":
    main()