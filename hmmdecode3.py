import json
import ast
import time
import sys


start_time = time.time()
model_params = open('hmmmodel.txt', 'r')
hmm_parameters = json.load(model_params)

# infile = sys.argv[1]
# test_data_pointer = open(infile, 'r')
# test_data_pointer = open('en_dev_raw.txt', 'r') #actual nlp project
test_data_pointer = open('quesfirst5.txt', 'r') #ict
test_data = test_data_pointer.readlines()

hmm_output_file = open('hmmoutput.txt', 'w')

entity_dict = hmm_parameters['entity_dict']
actual_tag_count = hmm_parameters['actual_tag_count_dict']
modified_tag_count = hmm_parameters['modified_tag_count_dict']
transition_matrix = hmm_parameters['transition_matrix']
tag_set = hmm_parameters['tag_set']
tag_set = (ast.literal_eval(tag_set))
word_set = hmm_parameters['word_set']
word_set = (ast.literal_eval(word_set))
#
# print('hmm_parameters:')
# print(tag_set)
# print(word_set)
# print(entity_dict)
# print(actual_tag_count)
# print(modified_tag_count)
# print(transition_matrix)
# print()

#transition_matrix = dict()
emission_matrix = dict()
max_prob_matrix = dict()
prob_matrix = dict()

#print('******************************************************************************')


for test_case in test_data:
    test_case_word_list = test_case.split()
    test_case_word_list = [word.strip() for word in test_case_word_list]

    for word in test_case_word_list:
            for tag in tag_set:
                if (word in word_set):
                    wt = word +'/'+tag
                    emission_matrix[tag] = emission_matrix.get(tag, {})
                    emission_matrix[tag][word] = entity_dict.get(wt,0)/actual_tag_count[tag]
                else:
                    emission_matrix[tag][word] = 1

    for tag in tag_set:
        max_prob_matrix[0] = max_prob_matrix.get(0,{})
        max_prob_matrix[0][tag] = max_prob_matrix[0].get(tag,{})
        max_prob_matrix[0][tag]['value'] = transition_matrix['q0'][tag] * emission_matrix[tag][test_case_word_list[0]]
        max_prob_matrix[0][tag]['pointer'] = 'q0'

    for i in range(1,len(test_case_word_list)):
        for curr in tag_set:
            max_prob_matrix[i] = max_prob_matrix.get(i,{})
            max_prob_matrix[i][curr] = max_prob_matrix[i].get(curr,{})
            max_prob_matrix[i][curr]['value'] = 0
            max_prob_matrix[i][curr]['pointer'] = {}
            if  emission_matrix[curr][test_case_word_list[i]] ==0:
                    continue
            for prev in tag_set:
                prob_matrix[i] = prob_matrix.get(i,{})
                prob_matrix[i][prev] = prob_matrix[i].get(prev,{})
                prob_matrix[i][prev][curr] = transition_matrix[prev][curr] * emission_matrix[curr][test_case_word_list[i]] * max_prob_matrix[i-1][prev]['value']
                if(prob_matrix[i][prev][curr]>max_prob_matrix[i][curr]['value']):
                    max_prob_matrix[i][curr]['value'] = prob_matrix[i][prev][curr]
                    max_prob_matrix[i][curr]['pointer'] = prev

    final_sentence = dict()

    i = len(test_case_word_list)-1
    maxnum = 0
    previous_state={}
    correct_tag = {}
    for tag in tag_set:
            if(max_prob_matrix[i][tag]['value'] >  maxnum):
                maxnum = max_prob_matrix[i][tag]['value']
                previous_state = max_prob_matrix[i][tag]['pointer']
                correct_tag = tag
            final_sentence[i] = final_sentence.get(i,{})
            final_sentence[i]['value'] = maxnum
            final_sentence[i]['backpointer'] = previous_state
            final_sentence[i]['tag'] = correct_tag

    for ii in range(1,len(test_case_word_list)):
        i = len(test_case_word_list)-ii-1
        maxnum = 0
        tag = previous_state
        previous_state = {}
        if(max_prob_matrix[i][tag]['value'] >  maxnum):
                maxnum = max_prob_matrix[i][tag]['value']
                previous_state = max_prob_matrix[i][tag]['pointer']
                correct_tag = tag
        final_sentence[i] = final_sentence.get(i,{})
        final_sentence[i]['value'] = maxnum
        final_sentence[i]['backpointer'] = previous_state
        final_sentence[i]['tag'] = correct_tag
        tag = previous_state


    output_testcase = ""
    for i in range(0,len(test_case_word_list)):
        output_testcase= output_testcase + test_case_word_list[i] + '/' +final_sentence[i]['tag']+' '
    hmm_output_file.write(output_testcase+'\n')
    print('\n' + output_testcase)

    countnoun=0
    words = 0
    for i in range(0,len(test_case_word_list)):

        if(final_sentence[i]['tag']=='NN'):
            countnoun += 1
        words+=1

    if countnoun/float(words)>=0.5 and words <=3:
        print("CHEATING!!")


print("total time {}".format(time.time() - start_time))

