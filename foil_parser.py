import requests

def extract_actions():
    actions = set()
    with open('planner/pr-domain.pddl') as f:
        for line in f:
            if (line.strip().startswith(("(:action"))):
                # print(line.strip()[len("(:action "):])
                actions.add(line.strip()[len("(:action "):])
    return actions

def extract_vocab(actions):
    vocab = set()
    for action in actions:
        listOfWords = action.lower().split('_')
        vocab.update(listOfWords)

    vocab.add('brickyard')
    vocab.add('brick')
    vocab.add('yard')
    vocab.add('transport')
    vocab.add('medi')
    vocab.add('medical')
    vocab.add('fire')
    vocab.add('chief')
    # vocab.add('engine')
    vocab.add('admin')
    vocab.add('apache')
    vocab.add('sub')
    vocab.add('court')
    vocab.add('phoenix')
    vocab.add('scottsdale')
    vocab.add('station')
    vocab.add('help')
    vocab.add('line')
    # vocab.add('ambulance')
    vocab.add('mesa')
    # vocab.add('ladder')
    # vocab.add('car')
    vocab.add('market')
    vocab.add('place')
    # vocab.add('helicopter')
    vocab.add('men')
    # vocab.add('bulldozer')


    return vocab

def clean_user_foil(user_foil, vocab):
    user_foil = user_foil.lower()
    user_foil = user_foil.replace('\'', "")
    if "phoenix" in user_foil:
        user_foil = user_foil.replace("phoenix", "phx")
    if "brickyard" in user_foil:
        user_foil = user_foil.replace("brickyard", "byeng")
    if "scottsdale" in user_foil:
        user_foil = user_foil.replace("scottsdale", "scotts")
    if "medical" in user_foil:
        user_foil = user_foil.replace("medical", "medi")
    words = user_foil.split(" ")

    additional_vocab = get_additional_vocab()
    for i in range(0, len(words)):
        if words[i] not in vocab and words[i] not in additional_vocab:
            similar_sounding_word_list = get_similar_sounding_words(words[i])
            for similar_word in similar_sounding_word_list:
                if similar_word in vocab:
                    print("replacing", words[i], "with", similar_word)
                    words[i] = similar_word

    word_list = []
    word_list.append(words[0])
    for i in range(1, len(words)):
        temp = word_list[len(word_list) - 1] + words[i]
        if temp in vocab:
            word_list.pop()
            word_list.append(temp)
        else:
            word_list.append(words[i])
    return word_list

def get_actions_in_foil(word_list, action_set, vocab):
    action_list = []
    action = ""
    for word in word_list:
        if word in vocab:
            if len(action) == 0:
                action += word.upper()
            else:
                action = action + "_" + word.upper()
            if action in action_set:
                action_list.append(action)
                action = ""

    return action_list

action_set = extract_actions()
vocab = extract_vocab(action_set)

def get_actions(user_foil, current_plan):
    word_list = clean_user_foil(user_foil, vocab)
    actions_in_foil = get_actions_in_foil(word_list, action_set, vocab)
    current_plan_actions = []
    user_suggested_actions = []

    for action in actions_in_foil:
        if action in current_plan:
            current_plan_actions.append(action)
        else:
            user_suggested_actions.append(action)

    return current_plan_actions, user_suggested_actions

def get_similar_sounding_words(word):
    similar_sounding_word_list = []
    url = "https://api.datamuse.com/words?sl=" + word + "&max=400"
    response = requests.get(url)
    for word_dict in response.json():
        similar_sounding_word_list.append(word_dict['word'])
    return similar_sounding_word_list

def get_additional_vocab():
    # adding additional words for the similar sounding words logic
    additional_vocab = set()
    additional_vocab.add("why")
    additional_vocab.add("and")
    additional_vocab.add("not")
    return additional_vocab