#!/bin/bash
FILENAME=hypernucleus_10_32.tar.bz2
make
python3 freeze_setup.py build
cd build
mv * hypernucleus
tar cjvf $FILENAME hypernucleus
cp $FILENAME ../
cd ..
rm -rf build
