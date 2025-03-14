import redis
import datetime

r = redis.Redis(host="node1", port=6301, db=0)

r.set('zxz', '1')

start_time, end_time = 0, 0
while(True):
    try:
        v = r.get('zxz')
    except:
        print("Start downtime")
        start_time = datetime.datetime.now();
        break

while(True):
    try:
        v = r.get('zxz')
    except:
        continue
    else:
        if v.decode() == '1':
            print("Start runing")
        end_time = datetime.datetime.now();
        break
    
print("Downtime:", end_time - start_time)

