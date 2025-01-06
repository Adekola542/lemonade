# Service to monitor
SERVICE="laravel-backend"

# Threshold
CPU_THRESHOLD=80

# Log file
LOG_FILE="/var/log/laravel_cpu_monitor.log"

echo "Monitoring CPU usage for $SERVICE..." | tee -a $LOG_FILE

while true; do
    # Get CPU usage as an integer
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d. -f1)

    if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
        echo "$(date): CPU usage ($CPU_USAGE%) exceeded threshold ($CPU_THRESHOLD%). Restarting $SERVICE..." | tee -a $LOG_FILE
        systemctl restart $SERVICE
        sleep 5  # Wait before checking again
    fi

    sleep 10  # Poll interval
done
