# dmas
Code for DMAS

Install requirements with `pip install -r requirements.txt` after you've
created a virtualenv as usual. Installing OpenCV in a virtualenv can be a bit
more painful, I had to copy
`/usr/lib/python2.7/dist-packages/cv2.x86_64-linux-gnu.so` to
`virtualenv/lib/python2.7/site-packages/` to get it working on debian. This
.so file is installed from the package `python-opencv` from the system's
package manager.
