+++
title = "Take a picture with OpenCv and Galileo"
date = "2016-01-16"
draft = true
+++

Hello,

I will give you step by step tutorial how take your picture with the Intel Galileo and the OpenCv (and a camera, of course). So, conect your camera in the USB output of the Galileo (you can check if it’s ok seeing the device appears in `/dev`).

If you don’t have the OpenCv in your computer (opkg list-installed | grep python-opencv), then add the repositories available in the file *.conf [¹](https://communities.intel.com/thread/56046).

```bash
$ cat > /etc/opkg/iot-devkit.conf <<EOF
> src iot-devkit-i586 http://iotdk.intel.com/repos/1.1/iotdk/i586 
> EOF

$ opkg update
 
$ opkg upgrade

$ opkg install python-opencv
```

You can use this code [²](http://codeplasma.com/2012/12/03/getting-webcam-images-with-python-and-opencv-2-for-real-this-time/) python to take the picture with the camera using the OpenCv.

```python
import cv2
 
# Camera 0 is the integrated web cam on my netbook
camera_port = 0
 
# Number of frames to throw away while the camera adjusts to light levels
ramp_frames = 30
 
# Now we can initialize the camera capture object with the cv2.VideoCapture class.
# All it needs is the index to a camera port.
camera = cv2.VideoCapture(camera_port)
 
# Captures a single image from the camera and returns it in PIL format
def get_image():
	# read is the easiest way to get a full image out of a VideoCapture object.
	retval, im = camera.read()
	return im
 
# Ramp the camera - these frames will be discarded and are only used to allow v4l2
# to adjust light levels, if necessary
for i in xrange(ramp_frames):
	temp = get_image()

print("capturing...")
# Take the actual image we want to keep
camera_capture = get_image()
file = "/home/root/opencv_image.png"

# A nice feature of the imwrite method is that it will automatically choose the
# correct format based on the file extension you provide. Convenient!
cv2.imwrite(file, camera_capture)
 
# You'll want to release the camera, otherwise you won't be able to create a new
# capture object until your script exits
del(camera)
```

Maybe, you want the image, right? So, you can send it to you using ssh.

```bash
$ scp <source path>/opencv_image.png <user>@<ip>:/<destination path>/
```
