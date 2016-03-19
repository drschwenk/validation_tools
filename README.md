# Tools to validate VIND motion dataset

## Confirm Cuts
A tool with a simple cv based gui to manually examine and accept videos correcty cropped by turkers.

## Instalation

virtualenv venv --system-site-packages --python=/usr/local/Cellar/python3/3.5.0/bin/python3.5
echo "/usr/local/Cellar/opencv3/3.1.0_1/lib/python3.5/site-packages" >> venv/lib/python3.5/site-packages/cv2.pth
source venv/bin/activate
pip install -r requirements.txt
```
You will need to run this command prior to running any commands:
```bash
source venv/bin/activate
