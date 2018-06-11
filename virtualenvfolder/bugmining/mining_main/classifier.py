import random
import math

PATH = 0
ADDED = 1
DELETED = 2
CHANGESET = 3
BUG = 4
MEAN=0
SDV=1
def load_file(file_location):
    file_attributes_list = []
    with open(file_location, "r") as file:
        for line in file:
            file_attributes = line.split()
            file_attributes_list.append(file_attributes)
    return file_attributes_list

def splitDataSet(all_data_set, split_ratio):
    testing_size = int(len(all_data_set)*split_ratio)
    testing_set = []
    training_set = list(all_data_set)
    while len(testing_set) < testing_size:
        index = random.randrange(len(training_set))
        testing_set.append(training_set.pop(index))
    return [training_set, testing_set]

def separate_by_defect(training_set):
    defect_list = []
    non_defect_list = []
    for item in training_set:
        if item[BUG] == "1":
            defect_list.append(item)
        else:
            non_defect_list.append(item)
    return [non_defect_list, defect_list]

def get_mean(data_set):
    return sum(data_set)/len(data_set)

def get_sdv(data_set):
    """
    Use N-1 for unbiased estimation of the population variance
    """
    mean = get_mean(data_set)
    variance = sum([pow(i-mean,2) for i in data_set])/(len(data_set)-1)
    return math.sqrt(variance)

def cal_attributes(file_attributes_list):
    all_attributes_lists = list(zip(*file_attributes_list))
    # all_metrics = [PATH, ADDED, DELETED]
    metrics_lists = all_attributes_lists[ADDED:(CHANGESET+1)]
    print(metrics_lists)
    cal_attributes = []
    for file_attribute_list in metrics_lists:
        cal_attributes.append((get_mean(list(map(float, file_attribute_list))),
                                get_sdv(list(map(float, file_attribute_list)))))
    return cal_attributes

def cal_attributes_by_defect(data_set):
    separate_sets = separate_by_defect(data_set)
    summary = []
    for set in separate_sets:
        summary.append(cal_attributes(set))
    return summary

def cal_probability(x, mean, sdv):
    exponent = math.exp(-(math.pow(float(x)-mean,2)/(2*math.pow(sdv,2))))
    return (1/(math.sqrt(2*math.pi)*sdv))*exponent

def cal_probability_defect(summary, file_metric_input):
    probs = []
    for metrics in summary:
        final_prob = 1
        for i in range(len(metrics)):
            mean = metrics[i][MEAN]
            sdv = metrics[i][SDV]
            x = file_metric_input[i+1]
            final_prob *= cal_probability(x, mean, sdv)
        probs.append(final_prob)
    return probs

def predict_defect(summary, file_metric_input):
    probs = cal_probability_defect(summary, file_metric_input)
    prediction = None
    best_prob = -1
    defect_status = 0
    for prob in probs:
        if best_prob is None or prob > best_prob:
            best_prob = prob
            prediction = defect_status
            defect_status += 1
    print(prediction)
    return prediction

def predict_defect_set(summary, testing_set):
    predictions = []
    for test in testing_set:
        predict = predict_defect(summary, test)
        predictions.append(predict)
    return predictions

def get_accuracy(testing_set, predictions):
    correct_counter = 0
    for i in range(len(testing_set)):
        print(testing_set[i][-1])
        if int(testing_set[i][-1]) == predictions[i]:
            correct_counter += 1
    return (correct_counter/(len(testing_set))*100)


if __name__ == '__main__':
    file_attributes_list = load_file("data_set.txt")
    split_ratio = 1/2
    training_set, testing_set = splitDataSet(file_attributes_list,split_ratio)
    print("Training set: ", len(training_set))
    print("Testing set: ", len(testing_set))

    summary = cal_attributes_by_defect(training_set)
    predictions = predict_defect_set(summary, testing_set)
    accuracy = get_accuracy(testing_set, predictions)
    print("Accuracy: ", accuracy, "%")
