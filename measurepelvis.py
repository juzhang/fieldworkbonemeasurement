"""
Script to measure the pelvis
"""

import sys
import os
import argparse
import json
os.environ['ETS_TOOLKIT']='wx'
import numpy as np
from gias2.fieldwork.field import geometric_field
from gias2.musculoskeletal import fw_pelvis_measurements



_selfdir = os.path.split(__file__)[0]
PELVIS_ENS = os.path.join(_selfdir, 'data', 'pelvis_combined_cubic_flat.ens')
PELVIS_MESH = os.path.join(_selfdir, 'data', 'pelvis_combined_cubic_flat.mesh')

# Use literature constants for HJC regression models.
fw_pelvis_measurements.HJC._literatureData = fw_pelvis_measurements.HJC._literatureDataBell

# measurement function
def measure(gf, saveFilename=None, sex=None):
    
    # geometric measurements
    m = fw_pelvis_measurements.PelvisMeasurements(gf, acs='isb')
    m.calcMeasurements()

    if sex is None:
        popclass = 'adults'
    elif sex=='m':
        popclass = 'men'
    elif sex=='f':
        popclass = 'women'
    else:
        raise ValueError('Invalid sex {}'.format(sex))
    m.calcHJCPredictions(popclass)

    # add some extra ones
    m.measurements['hip_joint_centre_l'] = fw_pelvis_measurements.Measurement(
        'hip_joint_centre_l',
        m.measurements['left_acetabulum_diameter'].centre
        )
    m.measurements['hip_joint_centre_r'] = fw_pelvis_measurements.Measurement(
        'hip_joint_centre_r',
        m.measurements['right_acetabulum_diameter'].centre
        )

    m.printMeasurements()
        
    if saveFilename is not None:
        _write_measurements(m, saveFilename)
        
    return m

def _write_measurements(m, filename):
    mnames = list(m.measurements.keys())
    mnames.sort()

    # mdict = {}
    # for mn in mnames:
    #     mdict[mn] = str(m.measurements[mn].value)

    with open(filename, 'w') as f:
        # json.dump(mdict, f, indent=True, sort_keys=True)

        for mi in mnames:
            if m.measurements[mi] is not None:
                f.write('{} : {}\n'.format(mi, m.measurements[mi].value))


def load_model(geofpath):
    gf = geometric_field.load_geometric_field(
            geofpath, PELVIS_ENS, PELVIS_MESH
            )

    return gf

def view(m):
    from gias2.visualisation import fieldvi
    disc = [6,6]
    hjc_render_args = {'mode':'sphere','scale_factor':3.0, 'scale_mode':'none'}
    landmark_render_args = {'mode':'sphere','scale_factor':3.0, 'scale_mode':'none'}

    v = fieldvi.Fieldvi()
    v.GFD = disc
    v.displayGFNodes = False
    gfeval = geometric_field.makeGeometricFieldEvaluatorSparse(m.GF, disc)
    v.addGeometricField('pelvis', m.GF, gfeval)
    v.addGeometricField('pelvis aligned', m.GFACS, gfeval)

    # hip join centres
    hjc_names = ['Bell', 'Tylkowski', 'Andriacchi', 'Seidel', 'Harrington', 'mesh']
    left_hjc_coords = np.array([m.measurements['left_HJC_{}'.format(n)].value for n in hjc_names])
    right_hjc_coords = np.array([m.measurements['right_HJC_{}'.format(n)].value for n in hjc_names])
    v.addData('HJCs_left', left_hjc_coords, renderArgs=hjc_render_args)
    v.addData('HJCs_right', right_hjc_coords, renderArgs=hjc_render_args)

    # anatomical landmarks
    landmark_coords = np.array([m.measurements['landmarks_ACS'].value[n] for n in m.landmarks])
    v.addData('landmarks_aligned', landmark_coords, renderArgs=landmark_render_args)

    # launch viewer
    v.configure_traits()

    # show objects
    v._drawData('HJCs_left')
    v._drawData('HJCs_right')
    v._drawGeometricField('pelvis aligned')

    # labels
    for i in range(len(hjc_names)):
        v.scene.mlab.text3d(
            left_hjc_coords[i][0], left_hjc_coords[i][1]-5.0,left_hjc_coords[i][2],
            hjc_names[i], color=(0,0,0), scale=2.0
            )
        v.scene.mlab.text3d(
            right_hjc_coords[i][0], right_hjc_coords[i][1]-5.0,right_hjc_coords[i][2],
            hjc_names[i], color=(0,0,0), scale=2.0
            )

    return v

def main(args):
    gf = load_model(args.geof)
    m = measure(gf, args.outfile, args.sex)
    if args.view:
        view(m)

parser = argparse.ArgumentParser(description='Measure a pelvis model.')
parser.add_argument(
    'geof',
    help='file path of the model .geof file.'
    )
parser.add_argument(
    '-s', '--sex',
    choices=['m', 'f'],
    help='Sex of the subject for HJC regression models [m|f]. If not provided, uses the generic adult models.'
    )
parser.add_argument(
    '-v', '--view',
    action='store_true',
    help='Visualise measurements and model in 3D'
    )
parser.add_argument('-o', '--outfile',
                    help='file path of the output measurements.')

if __name__ == '__main__':
    main(parser.parse_args())

