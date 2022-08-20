from datetime import datetime
from django.utils import timezone
import time

nows = datetime.now()
x = isinstance(nows, time)
print(x)