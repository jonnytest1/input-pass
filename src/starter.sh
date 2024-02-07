# configuration is now : docker desktop and put in bashrc of autologin user
# that way the dispaly runtime is already available
# use pip3
cd /home/jonathan
echo "running python"
sleep 1
echo "start" > /home/jonathan/python-input.log

python3 ./input.py >> /home/jonathan/python-input.log
 