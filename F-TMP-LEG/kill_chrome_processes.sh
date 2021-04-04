kill $(ps aux | grep 'chromium' | awk '{print $2}')
kill $(ps aux | grep 'chrome' | awk '{print $2}')

