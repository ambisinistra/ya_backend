import requests
import json
import os

server_address = "http://0.0.0.0:8080/"

ac_answers = []
ri_requests = []
ri_answers = []

sum = 0

#read all jsons in test folder
test_files = []

for root_address, dirs, files in os.walk(os.getcwd()):
    test_files.append([])
    for file_ in sorted(files):
        if file_.endswith("json"):
            test_files[-1].append(root_address + '/' + file_)

for dir_ in test_files:
    for file_ in dir_:
        print (file_)
        with open(file_, mode='r') as input_file:
            a_, b_ = input_file.read().split("|||||")
            # print (type(a_), a_)
            # print (type(b_), b_)
            ri_requests.append(a_)
            ri_answers.append(b_)
        
        test = json.loads(ri_requests[-1])
        if test["type"].lower() == "post":
            data = json.dumps(test["body"])
            response = requests.post(server_address + test["address"], data=data, headers={'Content-Type': 'application/json'})
        if test["type"].lower() == "get":
            response = requests.get(server_address + test["address"])
        if test["type"].lower() == "patch":
            data = json.dumps(test["body"])
            response = requests.patch(server_address + test["address"], data=data, headers={'Content-Type': 'application/json'})
        
        re_json = {}
        re_json["code"] = response.status_code
        re_json["body"] = response.text
        re_json = json.dumps(re_json)

        ac_answers.append(response)
        if re_json != ri_answers[-1]:
            print ("TEST FAILED")
            print ("expected", ri_answers[-1], sep="\n")
            print ("got", re_json, sep="\n")

        
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