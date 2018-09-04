import json
import sys

# infile = sys.argv[1]
# training_data = open(infile,"r")              #import via console

training_data = open("en_train_tagged.txt","r")    #hardcode import
model_params = open("hmmmodel.txt", "w")

lines = training_data.readlines()

word_set = set() #stores list of all words
tag_set = set() #stores list of all tags
entity_dict = dict() #dictionary of entities. Entity = (word : tag)
actual_tag_count_dict = dict()  #stores count of all the tags
last_tag_count_dict = dict() #stores count of all the tags occuring as the last tag in sentence
modified_tag_count_dict = dict() #stores count of tags not ocuring as the last tag
sentence_count = 0
transition = dict() #stores transitions

for each_line in lines:
    sentence_count+= 1
    prev_tag = 'q0' #q0 is the start state
    entities = each_line.split() #entities is 1D array of all tokens in 1 line. Elements of array are tokens
    for each_entity in entities:
        entity_dict[each_entity] = entity_dict.get(each_entity,0)+1
        token = each_entity.rsplit('/',1)
        word_set.add(token[0])
        tag_set.add(token[1])
        actual_tag_count_dict[token[1]] = actual_tag_count_dict.get(token[1],0) +1
        transition[prev_tag] = transition.get(prev_tag,{})
        transition[prev_tag][token[1]] = transition[prev_tag].get(token[1],0)+1
        prev_tag=token[1]
    last_tag_count_dict[token[1]] = last_tag_count_dict.get(token[1],0)+1

modified_tag_count_dict['q0'] = sentence_count
for tag in actual_tag_count_dict.keys():
    modified_tag_count_dict[tag] = actual_tag_count_dict.get(tag,0)  - last_tag_count_dict.get(tag,0)


##calculate transition matrix (probabilities)
prev_states =  {'q0'}
prev_states = prev_states.union(tag_set)
transition_matrix=transition

for prev_state in prev_states:
    for tag in tag_set:
        transition_matrix[prev_state] = transition_matrix.get(prev_state, {})
        if(modified_tag_count_dict[prev_state]==0):
            transition_matrix[prev_state][tag]=0
        else:
            transition_matrix[prev_state][tag] = (transition_matrix[prev_state].get(tag,0)+1)/(modified_tag_count_dict[prev_state]+len(tag_set))
        # if(transition_matrix[prev_state][tag]==0):
        #     transition_matrix[prev_state][tag] = 1/(modified_tag_count_dict[prev_state]+1)


#print('******************************************************************')
#print()


data = {'tag_set': str(tag_set),'word_set': str(word_set),
        'entity_dict': entity_dict, 'actual_tag_count_dict': actual_tag_count_dict,
        'modified_tag_count_dict': modified_tag_count_dict,'transition_matrix': transition_matrix }
model_params.write(json.dumps(data))

print(data)
# print()
# print('entity_dict')
# print(entity_dict)
# print('word_set')
# print(word_set)
# print('tag_set')
# print(tag_set)
# print('actual tag count dict')
# print(actual_tag_count_dict)
# print('modified tag count dict')
# print(modified_tag_count_dict)
# print('transition')
# print(transition)
# print('transition_matrix')
# print(transition_matrix)

