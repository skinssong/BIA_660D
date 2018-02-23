# coding: utf-8

# In[ ]:


import re
import spacy
from pyclausie import ClausIE

nlp = spacy.load('en')
re_spaces = re.compile(r'\s+')
cl = ClausIE.get_instance()

# In[ ]:


from collections import namedtuple

FIELD_NAMES = ('index', 'subject', 'predicate', 'object', 'confidence')


class Triple(namedtuple('Triple', FIELD_NAMES)):
    """ Inherits from namedtuple. This tuple contains the fields index,
        subject, predicate, object, and confidence.
    """

    def __repr__(self):
        items = [(field, getattr(self, field, None)) for field in FIELD_NAMES]
        fields = ['%s=%r' % (k, v) for k, v in items if v is not None]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(fields))


# In[ ]:


class Person(object):
    def __init__(self, name, likes=None, has=None, travels=None):
        self.name = name
        self.likes = [] if likes is None else likes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels

    def __repr__(self):
        return self.name

    def add_like(self, other_person):
        if other_person in self.likes:
            pass
        else:
            self.likes.append(other_person)

    def add_pet(self, pet):
        if pet in self.has:
            pass
        elif len(self.has) == 1 and self.has[0].name is None:
            self.has[0].name = pet.name
        else:
            self.has.append(pet)

    def add_trip(self, trip):
        if trip in self.travels:
            pass
        else:
            self.travels.append(trip)


class Pet(object):
    def __init__(self, pet_type, master, name=None):
        self.type = pet_type
        self.name = name
        assert isinstance(master, Person)
        self.master = master

    def __repr__(self):
        if self.name == None:
            return self.type + ' with no name'
        else:
            return self.type + ' ' + self.name


class Trip(object):
    def __init__(self, time, destination):
        self.time = time
        self.destination = destination

    def __repr__(self):
        return self.time + self.destination


# In[ ]:


persons = []
pets = []
trips = []


# In[ ]:


def select_person(name):
    for person in persons:
        if person.name == name:
            return person
    else:
        return None


def add_person(name):
    person = select_person(name)
    if person is None:
        new_person = Person(name)
        persons.append(new_person)
        return new_person
    else:
        return person


# In[ ]:


def select_pet(name):
    for pet in pets:
        if pet.name == name:
            return pet
    return None


def add_pet(pet_type, master, name=None):
    if name is None:
        new_pet = Pet(pet_type, master)
        return new_pet
    else:
        pet = select_pet(name)
        if pet is None:
            new_pet = Pet(pet_type, master, name)
            pets.append(new_pet)
            return new_pet
        return pet


def get_person_pet(person_name):
    person = select_person(person_name)

    for thing in person.has:
        if isinstance(thing, Pet):
            return thing


# In[ ]:


def add_trip(time, destination):
    if len(trips) == 0:
        new_trip = Trip(time, destination)
        trips.append(new_trip)
        return new_trip
    else:
        for trip in trips:
            if trip.time == time and trip.destination == destination:
                return trip
        new_trip = Trip(time, destination)
        trips.append(new_trip)
        return new_trip


def get_trip(destination):
    for trip in trips:
        if trip.destination == destination:
            return trip
    return None


def get_data_from_file(file_path):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if not line.startswith(('$$$', '###', '==='))]
    return cleaned_lines


def generate_triplet(file_path='./assignment_01.data'):
    sents = get_data_from_file(file_path)
    cl = ClausIE.get_instance()
    triples = [(sent, cl.extract_triples([sent])) for sent in sents]
    return triples



def process_relation_triplet(mytuple):
    sentence = mytuple[0]
    doc = nlp(unicode(sentence))
    triplet = mytuple[1]

    for triple in triplet:
        # PERSON like Person
        if triple.predicate in ('like', 'likes'):
            if triple.subject in [e.text for e in doc.ents if e.label_ in ('PERSON', 'ORG')] and triple.object in [
                e.text for e in doc.ents if e.label_ == 'PERSON']:
                subj_name = triple.subject
                obj_name = triple.object
                subj_person = add_person(subj_name)
                obj_person = add_person(obj_name)
                subj_person.add_like(obj_person)

        if triple.predicate in ('is', 'are') and triple.object.startswith('friends with'):
            if triple.subject in [e.text for e in doc.ents if e.label_ == 'PERSON'] and 'PERSON' in [e.label_ for e in
                                                                                                     doc.ents]:
                subj_name = triple.subject
                subj_person = add_person(subj_name)
                obj_names = [e.text for e in doc.ents if e.label_ == 'PERSON' and e.text in triple.object]
                for obj_name in obj_names:
                    obj_person = add_person(obj_name)
                    subj_person.add_like(obj_person)
                    obj_person.add_like(subj_person)

        # (PERSON, has, PET)
        if triple.predicate in ('has', 'have'):
            if triple.subject in [e.text for e in doc.ents if e.label_ == 'PERSON'] and (
                    'dog' in triple.object or 'cat' in triple.object):
                subj_name = triple.subject
                subj_person = add_person(subj_name)
                obj_pet_type = 'dog' if 'dog' in triple.object else 'cat'
                obj_pet_name = None
                obj_entity = [e.text for e in doc.ents if e.label_ == 'ORG']
                if len(obj_entity) > 0:
                    obj_pet_name = obj_entity[0]
                obj_pet = add_pet(obj_pet_type, subj_person, obj_pet_name)
                subj_person.add_pet(obj_pet)

        # (PET, has, name)
        if triple.subject.endswith('name') and ('dog' in triple.subject or 'cat' in triple.subject):
            obj_pet_name = triple.object
            subj_name = [e.text for e in doc.ents if e.label_ == 'PERSON'][0]
            subj_person = add_person(subj_name)
            obj_pet_type = 'dog' if 'dog' in triple.subject else 'cat'
            obj_pet = add_pet(obj_pet_type, subj_person, obj_pet_name)
            subj_person.add_pet(obj_pet)

        # (PERSON, travels, TRIP)
        if triple.predicate in ('is flying', 'are taking', 'leaves for', 'is going'):
            subj_names = [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG']
            place = [e.text for e in doc.ents if e.label_ == 'GPE'][0]
            time = " ".join([e.text for e in doc.ents if e.label_ == 'DATE'])
            new_trip = add_trip(time, place)
            for subj_name in subj_names:
                subj_person = add_person(subj_name)
                subj_person.add_trip(new_trip)



def person_has_pet(pet_type):
    answer = '{} has a {} named {}.'
    pet_type_pets = [pet for pet in pets if pet.type is pet_type]
    for pet in pet_type_pets:
        pet_master = pet.master.name
        pet_name = pet.name
        print(answer.format(pet_master, pet_type, pet_name))


def do_person_likes_person(name_a, name_b):
    person_a = select_person(name_a)
    if person_a is None:
        print('person {} not found.'.format(name_a))
    else:
        person_b = select_person(name_b)
        if person_b is None:
            print('person {} not found.'.format(name_b))
        elif person_b not in person_a.likes:
            print("I don't know".format(name_a, name_b))
        else:
            print('person {} likes person {}'.format(name_a, name_b))



def who_likes_person(name_b):
    person_b = select_person(name_b)
    if person_b is None:
        print('person {} not found.'.format(name_b))
    for person_a in persons:
        if person_b in person_a.likes:
            print('person {} likes person {}'.format(person_a.name, person_b.name))


def person_likes_who(name_a):
    person_a = select_person(name_a)
    if person_a is None:
        print("I don't know".format(name_a))
    else:
        if len(person_a.likes) == 0:
            print("I don't know".format(name_a))
        for person_b in person_a.likes:
            print('person {} likes person {}'.format(person_a.name, person_b.name))


def person_pet_name(person_name, pet_type):
    person = select_person(person_name)
    if person is None:
        print("I don't know".format(person_name))
    else:
        if len(person.has) == 0 or person.has[0].type != pet_type:
            print('{} does not have {}'.format(person_name, pet_type))
        else:
            pet_name = person.has[0].name
            print("{}'s {}'s name is {}".format(person_name, pet_type, pet_name))



def person_travel(name_a):
    person_a = select_person(name_a)
    if person_a is None:
        print('person {} not found.'.format(name_a))
    else:
        return person_a.travels


def who_to_place(place_name):
    for person in persons:
        travel_places = [trip.destination for trip in person.travels]
        if place_name in travel_places:
            print('{} is traveling to {}'.format(person.name, place_name))


def when_person_to_place(person_name, place_name):
    person = select_person(person_name)
    if person_name is None:
        print('person {} not found.'.format(person_name))
    else:
        travel_places = [trip.destination for trip in person.travels]
        if place_name not in travel_places:
            print('{} is not planning to travel to {}'.format(person_name, place_name))
        else:
            trip = get_trip(place_name)
            print('{} is planning to travel to {} at {}'.format(person_name, place_name, trip.time))



def preprocess_question(question):
    # remove a, an, the
    q_words = question.strip().split(' ')
    stop_word = ('a', 'an', 'the')
    question_new = " ".join([word for word in q_words if word not in stop_word])
    return re.sub(re_spaces, " ", question_new)


def has_question_word(question):
    for q_word in ('who', 'what', 'when', 'does'):
        if q_word in question.lower():
            return True
    return False


def answer_question(question):
    question = preprocess_question(question)

    q_trip = Triple(0, '', '', '', '')
    try:
        q_trip = cl.extract_triples([preprocess_question(question)])[0]
    except Exception as e:
        print(e)

    doc = nlp(unicode(question))

    # Who has a <pet_type>?
    if q_trip.subject.lower() == 'who' and q_trip.object == 'dog':
        person_has_pet('dog')
    elif q_trip.subject.lower() == 'who' and q_trip.object == 'cat':
        person_has_pet('cat')

    # What's the name of <person>'s <pet_type>?
    if 'what' in question and 'name' in question:
        person_name = [e.text for e in doc.ents if e.label_ == 'PERSON' or 'ORG'][0]
        pet_type = 'dog' if 'dog' in question else 'cat'
        person_pet_name(person_name, pet_type)

    # Who is [going to|flying to|traveling to] <place>?
    if q_trip.subject.lower() == 'who' and q_trip.predicate in ('is going', 'is flying', 'is traveling'):
        place_name = [e.text for e in doc.ents if e.label_ == 'GPE']
        if len(place_name) == 0:
            pass
        else:
            place_name = place_name[0]
            who_to_place(place_name)

    # When is <person> [going to|flying to|traveling to] <place>?
    if question.strip().split(' ')[0].lower() == 'when' and q_trip.predicate in (
    'is going', 'is flying', 'is traveling'):
        place_name = [e.text for e in doc.ents if e.label_ == 'GPE']
        if len(place_name) == 0:
            pass
        else:
            place_name = place_name[0]
            person_name = q_trip.subject
            when_person_to_place(person_name, place_name)

    # Does <person> like <person>?
    if question.strip().split(' ')[0] in ('Does', 'does') and (
            'like' in q_trip.predicate or 'likes' in q_trip.predicate):
        persons = [e.text for e in doc.ents if e.label_ == 'PERSON']
        if len(persons) == 0:
            return
        else:
            obj_name = [person_name for person_name in persons if person_name == q_trip.object]
            if len(obj_name) == 0:
                return
            else:
                subj_name = list(set(persons) - set(obj_name))[0]
                obj_name = obj_name[0]
                do_person_likes_person(subj_name, obj_name)

    # Who likes person?
    if q_trip.subject.lower() == 'who' and q_trip.predicate in ('like', 'likes'):
        person_name = q_trip.object
        who_likes_person(person_name)

    # Who does person like?
    if q_trip.object.lower() == 'who' and 'like' in q_trip.predicate and q_trip.subject in [e.text for e in doc.ents if
                                                                                            e.label_ == 'PERSON']:
        person_name = q_trip.subject
        person_likes_who(person_name)


temp = nlp(u"Who likes Bob?")
[(e.text, e.label_) for e in temp.ents]


def main():
    triples = generate_triplet()
    for triple in triples:
        process_relation_triplet(triple)

    question = ' '
    while question[-1] != '?':
        question = raw_input("Please enter your question: ")
        if question[-1] != '?':
            print('This is not a question... please try again')

        if not has_question_word(question):
            print('only support questions with who, what, when, does... please try again')

    answer_question(question)

if __name__ == '__main__':
    main()
