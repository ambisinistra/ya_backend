import requests
import json
import os

server_address = "http://0.0.0.0:8080/"

jsons = []
answers = []

sum = 0

#read all jsons in test folder
test_files = []

for root_address, dirs, files in os.walk(os.getcwd()):
    test_files.append([])
    print (root_address, files)
    for file_ in sorted(files):
        if file_.endswith("json"):
            test_files[-1].append(root_address + '/' + file_)

for dir_ in test_files:
    for file_ in dir_:
        print (file_)




        
"""
for i, testing in enumerate(zip(tests, answers)):
    test, answer = testing
    data = json.dumps(test["body"])
    if test["type"].lower() == "post":
        response = requests.post(server_address + test["address"], data=data, headers={'Content-Type': 'application/json'})
    
    resp_dejson = json.loads(response.text)
    print ("expected :", answer)
    print ("got      :", (response.status_code, resp_dejson))

    if answer == (response.status_code, resp_dejson):
        print (f"test {i} passed")
        sum += 1
    else:
        print (f"test {i} failed")

print (f"there were {i+1} tess completed, {sum} successfully")

"""