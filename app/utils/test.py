from datetime import datetime
import time

dt = datetime.utcnow()
tt = time.time()
tf = time.time() + 600000
print(tt, tf)