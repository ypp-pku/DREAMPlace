rm -rf build
rm -rf install
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=~/class-EDA/DREAMPlace/install -DPYTHON_EXECUTABLE=$(which python)