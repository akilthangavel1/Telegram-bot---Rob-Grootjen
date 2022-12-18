import pickle
# take user input to take the amount of data


def insert_data_into_pickle(opData):
    data = []
    data.append(opData)
    # open a file, where you ant to store the data
    file = open('openpositions', 'wb')
    # dump information to that file
    pickle.dump(data, file)
    # close the file
    file.close()


def read_data_pickle():
    import pickle
    # open a file, where you stored the pickled data
    file = open('openpositions', 'rb')
    # dump information to that file
    data = pickle.load(file)
    # close the file
    file.close()
    return data[0]

insert_data_into_pickle("No Open positions added")
a = read_data_pickle()
print(a)