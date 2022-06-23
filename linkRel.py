import math
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectFromModel
from basicAtts import BasicAtts
import numpy as np
from collections import defaultdict
from asn_attr import asn_attr
from imblearn.over_sampling import SMOTE


ba = BasicAtts('./basic_data/asrel.txt')
asn = asn_attr("./202107data/asn-list.txt")

triple = set()
result_triple = set()
nodes = set(ba.graph.nodes())
for name in ['0', '1']:
    with open('./hidden-data/triplet_miss' + name + '.txt') as f:
        for line in f:
            if line == '\n':
                continue
            tri = line.strip().split('&')[1].split('#')
            for t in tri:
                t = t.split('|')
                if len(set(t) & nodes) != 3:
                    continue
                if ba.graph.degree(t[0]) > ba.graph.degree(t[2]) or (ba.graph.degree(t[0]) == ba.graph.degree(t[2]) and int(t[0]) > int(t[2])):
                    t = (t[2], t[1], t[0])
                triple.add(tuple(t))

for name in ['0', '1']:
    with open('./hidden-data/futher' + name + '.txt') as f:
        for line in f:
            if line == '\n':
                continue
            t = line.strip().split('|')
            if len(set(t) & nodes) != 3:
                continue
            if ba.graph.degree(t[0]) > ba.graph.degree(t[2]) or (ba.graph.degree(t[0]) == ba.graph.degree(t[2]) and int(t[0]) > int(t[2])):
                t = (t[2], t[1], t[0])
            result_triple.add(tuple(t))
triple = list(triple)
result_triple = list(result_triple)


X = []
for tri in triple:
    tmp = []
    (a, b, c) = tri
    tmp.extend(asn.get_feature(tri))
    tmp.extend([math.log10(ba.graph.degree(a)), math.log10(ba.graph.degree(b)), math.log10(ba.graph.degree(c))])
    tmp.extend([ba.distance[a], ba.distance[b], ba.distance[c]])
    tmp.extend([ba.getHierarchy(a), ba.getHierarchy(b), ba.getHierarchy(c)])
    tmp.extend([math.log10(len(ba.customer[a])+1), math.log10(len(ba.peer[a])+1), math.log10(len(ba.provider[a])+1)])
    tmp.extend([math.log10(len(ba.customer[b])+1), math.log10(len(ba.peer[b])+1), math.log10(len(ba.provider[b])+1)])
    tmp.extend([math.log10(len(ba.customer[c])+1), math.log10(len(ba.peer[c])+1), math.log10(len(ba.provider[c])+1)])
    tmp.extend([ba.getRel(a, b), ba.getRel(b, c)])
    tmp.append(ba.getRel(a, c))
    X.append(tmp)

Y = []
for tri in result_triple:
    tmp = []
    (a, b, c) = tri
    tmp.extend(asn.get_feature(tri))
    tmp.extend([math.log10(ba.graph.degree(a)), math.log10(ba.graph.degree(b)), math.log10(ba.graph.degree(c))])
    tmp.extend([ba.distance[a], ba.distance[b], ba.distance[c]])
    tmp.extend([ba.getHierarchy(a), ba.getHierarchy(b), ba.getHierarchy(c)])
    tmp.extend([math.log10(len(ba.customer[a])+1), math.log10(len(ba.peer[a])+1), math.log10(len(ba.provider[a])+1)])
    tmp.extend([math.log10(len(ba.customer[b])+1), math.log10(len(ba.peer[b])+1), math.log10(len(ba.provider[b])+1)])
    tmp.extend([math.log10(len(ba.customer[c])+1), math.log10(len(ba.peer[c])+1), math.log10(len(ba.provider[c])+1)])
    tmp.extend([ba.getRel(a, b), ba.getRel(b, c)])
    Y.append(tmp)

X = np.array(X)
Y = np.array(Y)

train_x = X[:int(len(X) * 0.7), 0:-1]
train_y = X[:int(len(X) * 0.7), -1]
test_x = X[int(len(X) * 0.7):, 0:-1]
test_y = X[int(len(X) * 0.7):, -1]

smo = SMOTE(random_state=42)
train_x, train_y = smo.fit_resample(train_x, train_y)
model = XGBClassifier(eta=0.2, min_child_weight=4, gamma=0, n_estimators=600, max_depth=14,
                      eval_metric=['logloss', 'auc', 'error'], use_label_encoder=False)
model.fit(train_x, train_y)

predictions = model.predict(test_x)
accuracy = accuracy_score(test_y, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
print("feature importance", model.feature_importances_)


thresholds = np.sort(model.feature_importances_)


predictions = model.predict(Y)
result_dict = defaultdict(lambda: [0, 0, 0])
for i in range(len(result_triple)):
    (a, b, c) = result_triple[i]
    result_dict[(a, c)][int(predictions[i])] += 1
fout = open('./202107data/asrel_hidden.txt', 'w')
for key in result_dict:
    cnt = result_dict[key]
    (a, b) = key
    if cnt[1] >= cnt[0] and cnt[1] >= cnt[2]:
        if int(a) < int(b):
            fout.write(a + '|' + b + '|0\n')
        else:
            fout.write(b + '|' + a + '|0\n')
    elif cnt[0] >= cnt[1] and cnt[0] >= cnt[2]:
        fout.write(b + '|' + a + '|-1\n')
    elif cnt[2] >= cnt[0] and cnt[2] >= cnt[1]:
        fout.write(a + '|' + b + '|-1\n')
fout.close()