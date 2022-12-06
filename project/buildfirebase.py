import requests
import pandas as pd
import json

firebase_url = 'https://project-76289-default-rtdb.firebaseio.com/root'


def ls(directory):
    split_directory = directory.split("/")  # ['', 'user', 'john']
    request_url = firebase_url

    path = ""
    res = ""
    for i in range(1, len(split_directory)):
        path = path + '/' + split_directory[i]  # current directory (nested)

        request_url = firebase_url + path  # request url

        r = requests.get(request_url + ".json")  # get the information based on this path's url from Firebase

        current_content = r.json()

        if current_content is None:
            return ("No Such Directory! " + split_directory[i])

            # print the final answer
    # if it does have content in current directory, only print the key of the pairs
    result = []
    if type(current_content) is not list:
        for i in list(current_content.keys()):
            if i is not '0':
                doc_name = requests.get(firebase_url + path + '/' + i + '/0.json').json()
                result.append(str(doc_name))
        return (result)

    # if the current directory has nothing in it, print corresponding message
    else:
        if current_content[0] != split_directory[len(split_directory) - 1]:
            return ('Invalid input, this is a file instead of directory!')
        else:
            return ("This is an empty directory!")
    return


def mkdir(directory):
    split_directory = directory.split("/")
    request_url = firebase_url

    path = ""
    for i in range(1, len(split_directory)):
        path = path + '/' + split_directory[i]
        request_url = firebase_url + path

        # get the information based on this path's url from Firebase
        r = requests.get(request_url + ".json")
        current_content = r.json()

        # if it is deepest directory that we want to create
        if (i == len(split_directory) - 1):
            if current_content is not None:
                return ("Error: the new-created directory '" + split_directory[i] + "' has already existed!")
            else:
                new_pair = {split_directory[i]: {'0': split_directory[i]}}
                new_json = json.dumps(new_pair)
                new_length = len(request_url) - (len(split_directory[i]) + 1)
                new_url = request_url[: new_length]
                requests.patch(new_url + ".json", data=new_json)
                return "Directory created successfully !"
                # if not the deepest node
        else:
            if current_content is None:
                return ("Error: invalid directory, the path '" + split_directory[i] + "' does not exist!")
            else:
                path = path


def put(file_name, directory, k):
    # 我们来存储real data的地方。之后可以改 ！！
    partition_url = 'https://project-76289-default-rtdb.firebaseio.com/actual'  # PARTITION——URL来存real data
    split_directory = directory.split("/")
    request_url = firebase_url

    # pre-process the file name first
    split_file_name = file_name.split('.')

    path = ""
    for i in range(1, len(split_directory)):
        path = path + '/' + split_directory[i]
        request_url = firebase_url + path

        # get the information based on this path's url from Firebase
        r = requests.get(request_url + ".json")
        current_content = r.json()

        # if it is deepest directory that we want to create
        if (i == len(split_directory) - 1):
            # if the directory does not exit, print error message
            if current_content is None:
                return ("Error: invalid directory, the path '" + split_directory[i] + "' does not exist")

            # time to partition the file into K parts
            df = pd.read_csv(file_name)
            partition_number = len(df.index) // k

            # store the partition location for each partition
            location = {}
            location[0] = file_name

            begin_index = 0
            counter = 1  # record the partition number
            for i in range(1, k):
                end_index = begin_index + partition_number - 1

                # upload the current partition to real data
                curr_partition = df.loc[begin_index: end_index]
                location_url = partition_url + '/' + split_file_name[0] + str(
                    counter) + '/' + ".json"  # location of current partition
                requests.put(location_url, data=curr_partition.to_json(orient='index'))

                # upload the current partition to meta data
                location[counter] = location_url

                begin_index = end_index + 1  # update the starting point for next partition
                counter += 1

            # upload the last partition (if necessary)
            last_partition = df.loc[begin_index:]
            last_location_url = partition_url + '/' + split_file_name[0] + str(counter) + '/' + ".json"

            if (len(last_partition) > 0):
                location[counter] = last_location_url
                requests.put(last_location_url, data=last_partition.to_json(orient='index'))

            final_meta_data = {split_file_name[0]: location}
            final_json = json.dumps(final_meta_data)  # convert to json format

            requests.patch(request_url + ".json", data=final_json)  # REQUEST_URL 是存mata data的地方
            return ("File " + file_name + " uploaded successfully !")

        # if not the deepest node
        else:
            # if the directory does not exit, print error message
            if current_content is None:
                return ("Error: invalid directory, the path '" + split_directory[i] + "' does not exist")
            # continue going to the deep
            else:
                path = path


def getPartitionLocations(file):
    split_directory = file.split("/")
    request_url = firebase_url

    path = ""
    for i in range(1, len(split_directory)):
        path = path + '/' + split_directory[i].split('.')[0]
        request_url = firebase_url + path

        # get the information based on this path's url from Firebase
        r = requests.get(request_url + ".json")
        current_content = r.json()

        # if it is deepest file that we want to access
        if (i == len(split_directory) - 1):
            # if the file does not exit, print error message
            if current_content is None:
                return ("Error: File Not Found")

            # if the file exists, get its partition locations
            locations = requests.get(request_url + ".json").json()

            print(locations[1:])  # print the content for the users
            return (locations[1:])  # return the locations for later use

        # if not the deepest node
        else:
            # if the directory does not exit, print error message
            if current_content is None:
                return ("Error: invalid directory, the path '" + split_directory[i] + "' does not exist!")
            # continue going to the deep
            else:
                path = path


def readPartition(file, partition_number):
    split_directory = file.split("/")
    request_url = firebase_url

    path = ""
    for i in range(1, len(split_directory)):
        # path = path + split_directory[i].split('.')[0]
        path = path + '/' + split_directory[i].split('.')[0]

        request_url = firebase_url + path

        # get the information based on this path's url from Firebase
        r = requests.get(request_url + ".json")
        current_content = r.json()

        # if it is deepest file that we want to access
        if (i == len(split_directory) - 1):
            # if the file does not exit, print error message
            if current_content is None:
                return ("Error: File Not Found")

            # if the file exists, get its partition locations
            locations = requests.get(request_url + ".json").json()[1:]

            if (partition_number == 0 or partition_number > len(locations)):
                return ("Error: invalid partition number!")
            else:
                partition_location = locations[partition_number - 1]
                partition_content = requests.get(partition_location).json()
                if type(partition_content) is dict:
                    data = list(partition_content.values())
                    df = pd.DataFrame.from_dict(pd.json_normalize(data), orient='columns')
                    return (df)
                else:
                    new_list = []
                    for i in partition_content:
                        if i is not None:
                            new_list.append(i)
                    data = new_list
                    df = pd.DataFrame.from_dict(pd.json_normalize(data), orient='columns')
                    return (df)
                    # if not the deepest node
        else:
            # if the directory does not exit, print error message
            if current_content is None:
                return ("Error: invalid directory, the path'" + split_directory[i] + "' does not exist")
            # continue going to the deep
            else:
                # path = path + "/"
                path = path


def cat(file):
    split_directory = file.split("/")
    request_url = firebase_url

    path = ""
    for i in range(1, len(split_directory)):
        # path = path + split_directory[i].split('.')[0]
        path = path + '/' + split_directory[i].split('.')[0]
        request_url = firebase_url + path

        # get the information based on this path's url from Firebase
        r = requests.get(request_url + ".json")
        current_content = r.json()

        # if it is deepest file that we want to access
        if (i == len(split_directory) - 1):
            # if the file does not exit, print error message
            if current_content is None:
                return "Error: File Not Found"

            # if the file exists, get its partition locations
            else:
                locations = requests.get(request_url + ".json").json()[1:]
                output = []
                for location in locations:
                    partition_content = requests.get(location).json()
                    if type(partition_content) is dict:
                        data = list(partition_content.values())
                        for i in data:
                            output.append(i)
                    else:
                        for i in partition_content:
                            if i is not None:
                                output.append(i)
                df = pd.DataFrame.from_dict(pd.json_normalize(output), orient='columns')
                return (df)
        # if not the deepest node
        else:
            # if the directory does not exit, print error message
            if current_content is None:
                return ("Error: invalid directory, the path '" + split_directory[i] + "' does not exist!")
            # continue going to the deep
            else:
                path = path

def rm(file):
    split_directory = file.split("/")

    if '.' not in split_directory[-1]:
        return ('Invalid input: Not a invalid file name')

    request_url = firebase_url

    path = ""
    for i in range(1, len(split_directory)):
        path = path + split_directory[i].split('.')[0]
        request_url = firebase_url + '/' + path

        # get the information based on this path's url from Firebase
        r = requests.get(request_url + ".json")
        current_content = r.json()

        # if it is deepest file that we want to access
        if (i == len(split_directory) - 1):
            # if the file does not exit, print error message
            if current_content is None:
                return "Error: File Not Found !"

            # if the file exists, get its partition locations
            locations = requests.get(request_url + ".json").json()[1:]

            for location in locations:
                requests.delete(location)  # delete each partition

            # after deleting all actual data, delete the meta data now

            requests.delete(request_url + ".json")
            return ("File " + split_directory[-1] + " has been removed successfully !")


        # if not the deepest node
        else:
            # if the directory does not exit, print error message
            if current_content is None:
                return "Error: invalid directory, the path does not exist"
            # continue going to the deep
            else:
                path = path + "/"
