PY_PID=`ps -ef | grep reverse_image_search_main | grep py | awk '{print $2}'`
if [ ! $PY_PID ];
then
        echo 'no runing'
        python3 reverse_image_search_main.py >>/dev/null 2>&1 &
else
        echo 'is runing'
fi
