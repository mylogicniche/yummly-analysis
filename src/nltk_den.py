from nltk import pos_tag

s = 'coconut water'
tagged_sent = pos_tag(s.split())

print(tagged_sent)

t = [word for word,pos in tagged_sent if pos == 'NN' or pos == 'NNS']

print(t)