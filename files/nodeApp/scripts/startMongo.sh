if pgrep "mongod" > /dev/null
then
	echo "Mongo DB is currently running. "
else
	echo "Starting Mongo DB"
	nohup mongod --dbpath /opt/scripts/nodeEnmCapabilityMonitor/data/ > mongo.log &
fi
