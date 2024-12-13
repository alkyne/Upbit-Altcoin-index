from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

def process(item):
    # Simulate some work taking varying amounts of time
    # Using sleep to mimic I/O or some blocking operation
    # time.sleep(random.uniform(0.1, 1.0))
    return f"Processed {item}"

items = [1, 2, 3, 4, 5]

# Run the loop concurrently
with ThreadPoolExecutor(max_workers=50) as executor:
    # Submit all tasks
    futures = [executor.submit(process, item) for item in items]
    
    # As results become available, print them
    for future in as_completed(futures):
        result = future.result()
        print(result)