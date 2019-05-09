PORT=8080
if pgrep "node" > /dev/null
then
        echo "Node is currently running. "
else
        echo "Starting node js app"
	nohup npm start > npm.log &
fi
