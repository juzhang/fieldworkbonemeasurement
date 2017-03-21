Bone Measurement Scripts
========================

This module contains scripts for taking anatomical measurements on fieldwork
bone models.

Run either measurefemur.py or measurepelvis.py in the command prompt using
python by passing the file path of the .geof model file and a outfile file
with the measurements in text, e.g.

    python measurefemur.py data/femur_left_mean_LLP26.geof l -o testfemurl.txt

To see the explanation for each commandline argument, run

    python measurefemur.py --help

or 

    python measurepelvis.py --help

To run with 3D visualisation, the scripts must be run from within IPython with 
the -v flag e.g.

    ipython
    run measurepelvis data/pelvis_combined_mean_LLP26.geof -o testpelvis.txt -v

The data folder contains .ens and .mesh files required to load fieldwork femur
and pelvis models. The folder also contains example .geof files for the left
femur, right femur, and pelvis.