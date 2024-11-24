# configuration is now : docker desktop and put in bashrc of autologin user
# that way the dispaly runtime is already available
# use pip3
cd /home/jonathan
echo "running python"
sleep 1


now="$(date --iso-8601)"

echo "start" > /home/jonathan/python-input-$now.log

python3 ./input.py >> /home/jonathan/python-input-$now.log
 


# DBG_ARGS= --remote-debugging-port=9222 <- needs forwarding address only works headless
# nano ~/.config/wayfire.ini
# 
# [autostart]
# start_app = chromium-browser --kiosk $URL_TO_OPEN --Landscape=true --ignore-certificate-errors
# input_start= $HOME/starter.sh


