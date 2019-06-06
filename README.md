


## About the Approach
This model was made using pjreddies YOLOv3 algorithm. The goal of the task was to find the flyable region within the inside of a target "gate" for a drone to fly through. I chose to instead look for the corners of each gate, as YOLO will only standardly look for a horizontal target box. Instead after finding each corner, I found the center of them, and built my coordinates as such. Using this method, my attempt was able to reach #6 on the Task 2 leaderboard. In this repository is the files needed to run the model. Please messege me if you would like access to the model itself.

![Figure](https://imgur.com/a/JM0nTbX.jpg "Shows the corners")

### pip3 install -r requirements.txt

To generate prediction labels for validation run below command and keep the test data in `testing/images`.

### python3 generate_submission.py 

Conversion and YOLO predictor license in LICENSE: https://github.com/xiaochus/YOLOv3
