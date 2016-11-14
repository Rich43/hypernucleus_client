#!/bin/bash
FILENAME=hypernucleus_10_64.tar.bz2
rm $FILENAME
rm -rf build
make
python3 freeze_setup.py build
cd build
mv * hn
tar cjvf $FILENAME hn
cp $FILENAME ../
cd ..
rm -rf build
