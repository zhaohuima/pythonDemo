#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/3 14:05
#@File : course28demo.py
#@Software: PyCharm

article = '''This is a photograph of our village.
Our village is in a valley.
It is between two hills.
The village is on a river.
Here is another photograph of the village.
My wife and I are walking along the banks of the river.
We are on the left.
There is a boy in the water.
He is swimming across the river.
Here is another photograph.
This is the school building.
It is beside a park.
The park is on the right.
Some children are coming out of the building.
Some of them are going into the park.
'''
new_words = [
  'photograph',
  'village',
  'valley',
  'between',
  'hills',
  'another',
  'prep',
  'wife',
  'along',
  'banks',
  'water',
  'swimming',
  'building',
  'park',
  'into'
]
def wordcount(list):
    list = article.lower().replace('.', '').split()
    word_account = {}
    for i in list:
        if i in word_account:
            word_account[i] += 1
        else:
            word_account[i] = 1
    return word_account

print(wordcount(article))

difficulty = 0

for i in new_words:
    if i in wordcount(article):
        difficulty += 5 * wordcount(article)[i]
print(difficulty)

