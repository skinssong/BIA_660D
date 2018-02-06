import spacy
npl = spacy.load('en')

def process_data(path_to_file):
    if not isinstance(path_to_file, str):
        return Exception('{} is not a string'.format(path_to_file))
    with open(path_to_file) as infile:
        return [line.strip() for line in infile if not line[0] in ['$','#','=']]

'''
Ralational 
(Person, Likes, Person)
(Person, Has, Objects)
(Person, Travels, Place)
(Person, Travels, When)
'''