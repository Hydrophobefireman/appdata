def when_ready(server):
    # touch app-initialized when ready
    try:
        open('/tmp/app-initialized', 'w').close()
    except:
        pass

bind = 'unix:///tmp/nginx.socket'
workers = 4
threads = 4
timeout = 500