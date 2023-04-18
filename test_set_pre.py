import json
import os
from pathlib import Path

def countFreq(arr, n):
     
    # Mark all array elements as not visited
    visited = [False for i in range(n)]
 
    # Traverse through array elements
    # and count frequencies
    for i in range(n):
         
        # Skip this element if already
        # processed
        if (visited[i] == True):
            continue
 
        # Count frequency
        count = 1
        for j in range(i + 1, n, 1):
            if (arr[i] == arr[j]):
                visited[j] = True
                count += 1
        if count > 1:
            print(arr[i], count)

def main():
    test_set_path = Path("/home/dhruv/Downloads/broadcasts-v1/data")
    file_list = os.listdir(test_set_path)
    entity_list = []
    for file in file_list:
        fname = test_set_path / file
        with open(fname, "rt") as f:
            c=0
            for line in f:
                line = line.rstrip()
                line = json.loads(line)
                people_list = line["people"]
                for person in people_list:
                    link = person["link"]
                    if link is not None and link["candidates"] is not None:
                        entity_list.extend(link["candidates"])
    
    print(len(entity_list))
    print(len(set(entity_list)))
    
    with open("test_unique_entities_list.txt", "w") as f:
        for unique_entity in set(entity_list):
            # Writing data to a file
            f.write(f"{unique_entity}\n")

if __name__ == "__main__":
    main()