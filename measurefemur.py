"""
Script to measure the femur
"""

import sys
import os
import argparse
os.environ['ETS_TOOLKIT']='wx'
import numpy as np
from gias2.fieldwork.field import geometric_field
from gias2.musculoskeletal import fw_femur_measurements

_selfdir = os.path.split(__file__)[0]
FEMUR_LEFT_ENS = os.path.join(_selfdir, 'data', 'femur_left_quartic_flat.ens')
FEMUR_LEFT_MESH = os.path.join(_selfdir, 'data', 'femur_left_quartic_flat.mesh')
FEMUR_RIGHT_ENS = os.path.join(_selfdir, 'data', 'femur_right_quartic_flat.ens')
FEMUR_RIGHT_MESH = os.path.join(_selfdir, 'data', 'femur_right_quartic_flat.mesh')

# measurement function
def measure(gf, saveFilename=None):
    
    # geometric measurements
    m = fw_femur_measurements.FemurMeasurements(gf)
    m.calcMeasurements()

    # add some extra ones
    m.measurements['head_centre'] = fw_femur_measurements.measurement(
        'head_centre',
        m.measurements['head_diameter'].centre
        )

    m.printMeasurements()
        
    if saveFilename is not None:
        _write_measurements(m, saveFilename)
        
    return m

def _write_measurements(m, filename):
    mnames = list(m.measurements.keys())
    mnames.sort()

    with open(filename, 'w') as f:
        for mi in mnames:
            f.write('{} : {}\n'.format(mi, m.measurements[mi].value))

def load_model(geofpath, side):
    if side=='l':
        gf = geometric_field.load_geometric_field(
            geofpath, FEMUR_LEFT_ENS, FEMUR_LEFT_MESH
            )
    elif side=='r':
        gf = geometric_field.load_geometric_field(
            geofpath, FEMUR_RIGHT_ENS, FEMUR_RIGHT_MESH
            )
    else:
        raise ValueError('Invalid side {}'.format(side))

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
    v.addGeometricField('femur', m.GF, gfeval)

    # anatomical landmarks
    # landmark_coords = np.array([m.measurements['landmarks'].value[n] for n in m.landmarks])
    # v.addData('landmarks', landmark_coords, renderArgs=landmark_render_args)

    # launch viewer
    v.configure_traits()

    # show objects
    # v._drawData('landmarks')
    v._drawGeometricField('femur')

    # labels

    return v

def main(args):
    gf = load_model(args.geof, args.side)
    m = measure(gf, args.outfile)
    if args.view:
        view(m)

parser = argparse.ArgumentParser(description='Measure a femur model.')
parser.add_argument(
    'geof',
    help='file path of the model .geof file.'
    )
parser.add_argument(
    'side',
    choices=['l', 'r'],
    help='Side of the femur [l|r].'
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

