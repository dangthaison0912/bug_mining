import random
import math

PATH = 0
ADDED = 1
DELETED = 2
AVG_ADDED = 3
AVG_DELETED = 4
CHANGESET = 5
INVOVLED = 6
BUG = 7
MEAN=0
SDV=1
TRUE_POSITIVE = 0
TRUE_NEGATIVE = 1
FALSE_POSITIVE = 2
FALSE_NEGATIVE = 3

# def load_file(file_location):
#     """
#     Extract data from file into the following form:
#     FILE_PATH ADDED DELETED CHANGESET IS_DEFECT
#     """
#     file_attributes_list = []
#     with open(file_location, "r") as file:
#         for line in file:
#             file_attributes = line.split()
#             file_attributes_list.append(file_attributes)
#     return file_attributes_list

def splitDataSet(all_data_set, split_ratio):
    """
    Split the data set into training set and testing set, given
    the split ratio.
    """
    testing_size = int(len(all_data_set)*split_ratio)
    testing_set = []
    training_set = list(all_data_set)
    while len(testing_set) < testing_size:
        index = random.randrange(len(training_set))
        testing_set.append(training_set.pop(index))
    return [training_set, testing_set]

def ten_fold_cross_validation(all_data_set):
    sets = []
    set_size = int(len(all_data_set)/10)
    copy = list(all_data_set)
    for i in range(10):
        sets.append([])
        while (len(copy) > 0) and (len(sets[i]) < set_size):
            index = random.randrange(len(copy))
            sets[i].append(copy.pop(index))
        print(len(sets[i]))
    return sets

def separate_by_defect(training_set):
    """
    Separate data set into defect and non-defect sets to
    calculate probability.
    """
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
    """
    Calculate the mean and standard deviation of all attributes
    from the given list of files
    """
    all_attributes_lists = list(zip(*file_attributes_list))
    # all_metrics = [PATH, ADDED, DELETED, AVG_ADDED, AVG_DELETED CHANGSET, INVOVLED]
    metrics_lists = all_attributes_lists[1:-1]
    # print("\n".join(metrics_lists[3]))
    # print(max(map(int, metrics_lists[0])), max(metrics_lists[1]), max(metrics_lists[2]))
    cal_attributes = []
    for file_attribute_list in metrics_lists:
        cal_attributes.append((get_mean(list(map(float, file_attribute_list))),
                                get_sdv(list(map(float, file_attribute_list)))))
    return cal_attributes

def cal_attributes_by_defect(data_set):
    """
    Calculate the mean and standard deviation of all attributes
    from the given data set, separated by type of files:
    defect and non defect
    """
    separate_sets = separate_by_defect(data_set)
    summary = []
    for set in separate_sets:
        summary.append(cal_attributes(set))
    return summary

def cal_probability(x, mean, sdv):
    """
    Calculate the probability of value x in the population with
    the given mean and standard deviation
    """
    exponent = math.exp(-(math.pow(float(x)-mean,2)/(2*math.pow(sdv,2))))
    return (1/(math.sqrt(2*math.pi)*sdv))*exponent

def cal_probability_defect(summary, file_metric_input, list_of_metrics):
    """
    Calculate probability of a file being defect or non-defect using
    a number of metrics
    """
    probs = []
    defect_status = 0
    final_prob = 0.32
    for class_type in summary:
        # final_prob = 0.5
        for i in list_of_metrics:
            mean = class_type[i][MEAN]
            sdv = class_type[i][SDV]
            # print(i,mean,sdv,"\n")
            # add one since the first elem of a file input is PATH
            x = file_metric_input[i+1]
            # print(defect_status, cal_probability(x, mean, sdv))
            final_prob *= cal_probability(x, mean, sdv)
        probs.append(final_prob)
        final_prob = 0.68
        defect_status += 1
    return probs

def predict_defect(summary, file_metric_input, list_of_metrics):
    """
    Given the probability, conduct a prediction of whether a file
    is defect or non-defect based on which has higher probability
    """
    probs = cal_probability_defect(summary, file_metric_input, list_of_metrics)
    prediction = None
    best_prob = -1
    defect_status = 0
    for prob in probs:
        if best_prob is None or prob > best_prob:
            best_prob = prob
            prediction = defect_status
            defect_status += 1
    return prediction

def predict_defect_set(summary, testing_set, list_of_metrics):
    """
    Predict the testing set if they are defect or not using the summary
    from the training set
    """
    predictions = []
    for test in testing_set:
        predict = predict_defect(summary, test, list_of_metrics)
        predictions.append(predict)
    return predictions

def get_accuracy(testing_set, predictions):
    """
    Get statistic about the prediction: True/False Positive, True/False Negative
    """
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    for i in range(len(testing_set)):
        actual_status = int(testing_set[i][-1])
        if actual_status == 0:
            if actual_status == predictions[i]:
                true_negative += 1
            else:
                false_positive += 1
        else:
            if actual_status == predictions[i]:
                true_positive += 1
            else:
                false_negative += 1
    return [true_positive, true_negative, false_positive, false_negative]

def classifier_defect(data_set, split_ratio):
    training_set, testing_set = splitDataSet(data_set,split_ratio)
    print("Training set: ", len(training_set))
    print("Testing set: ", len(testing_set))

    summary = cal_attributes_by_defect(training_set)
    list_of_metrics=[0,1,2]
    predictions = predict_defect_set(summary, testing_set, list_of_metrics)
    accuracy = get_accuracy(testing_set, predictions)

    for class_type in summary:
        for i in list_of_metrics:
            mean = class_type[i][MEAN]
            sdv = class_type[i][SDV]
            print(i,mean,sdv,"\n")

    TP = accuracy[TRUE_POSITIVE]
    TN = accuracy[TRUE_NEGATIVE]
    FP = accuracy[FALSE_POSITIVE]
    FN = accuracy[FALSE_NEGATIVE]
    print(TP, TN, FP, FN)
    recall = TP/(TP+FN)
    false_alarm = FP/(FP+TN)
    precision = TP/(TP+FP)
    return [recall, false_alarm, precision]

def classifier_defect_fold(data_set, list_of_metrics):
    """
    Apply 10-fold cross validation to run the classifierself.
    Return recall, false alarm, precision and F1 in %
    """
    ten_sets = ten_fold_cross_validation(data_set)
    results = []
    for i in range(len(ten_sets)):
        copy = list(ten_sets)
        testing_set = copy.pop(i)
        training_set = [x for n in copy for x in n]
        summary = cal_attributes_by_defect(training_set)
        # list_of_metrics=[0,1,2]
        predictions = predict_defect_set(summary, testing_set, list_of_metrics)
        accuracy = get_accuracy(testing_set, predictions)

        TP = accuracy[TRUE_POSITIVE]
        TN = accuracy[TRUE_NEGATIVE]
        FP = accuracy[FALSE_POSITIVE]
        FN = accuracy[FALSE_NEGATIVE]

        print(TP, TN, FP, FN)
        recall = TP/(TP+FN)
        false_alarm = FP/(FP+TN)
        precision = TP/(TP+FP)
        f1 = round(2*recall*precision/(recall+precision)*100, 2)
        recall = round(recall*100, 2)
        false_alarm = round(false_alarm*100, 2)
        precision = round(precision*100, 2)
        print(list_of_metrics[0])
        results.append([recall, false_alarm, precision, f1])
        # results.append([TP, TN, FP, FN])
    return results

if __name__ == '__main__':
    file_attributes_list = load_file("data_set.txt")
    split_ratio = 1/5
    results = classifier_defect(file_attributes_list, split_ratio)
    print("Recall: ", round(results[0]*100,2))
    print("False alarm: ", round(results[1]*100,2))
    print("Precision: ", round(results[2]*100,2))
