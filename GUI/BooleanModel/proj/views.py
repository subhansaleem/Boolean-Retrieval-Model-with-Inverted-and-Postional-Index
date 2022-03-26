from django.shortcuts import render
#for punctuation
import re
#for writing dictionary to file
import json
#for tokenization
from nltk.tokenize import word_tokenize
#for stemming
from nltk.stem import PorterStemmer

def home(request):
    return render(request, 'index.html')


def result(request):
    if request.method =='POST':
        query = request.POST['query']
        invertedindex()
        r = querytype(query)

        dic = [{
            'result' : r
        }]


        return render(request,'result.html',{'dict':dic})
    return render(request,'result.html',{})


ps = PorterStemmer()

stopwords = []
# created a dictionary dic for inverted index
dic = {}

def invertedindex():
    f = open("D:/projects/IR/Assignment1/GUI/BooleanModel/proj/Stopword-List.txt", "r")
    text = f.read()
    stopwords = (word_tokenize(text.lower()))

    # looping over all the files
    for i in range(1, 449):
        # reading from file
        f = open(f"D:/projects/IR/Assignment1/GUI/BooleanModel/proj/Abstracts/{i}.txt", "r")
        text = f.read().lower()

        # removing punctuation
        text = re.sub(r'[^\w\s]', ' ', text)

        # tokenization  with nltk
        words = word_tokenize(text)

        # removing stopwords
        words = [word for word in words if word not in stopwords]

        # stemming with nltk - Porter Stemmnig

        for index, items in enumerate(words):
            words[index] = ps.stem(items)

        # writing cleaned data to file
        ff = open(f"D:/projects/IR/Assignment1/GUI/BooleanModel/proj/Cleaned/{i}.txt", "w")
        for word in words:
            ff.write(word + " ")

        # Appending to dictionary
        # dic = {
        #     'word': {
        #         'doc' : [list of position]
        #     }
        # }
        for index, item in enumerate(words):
            # item not present
            if item == 'autoencoders':
                print(i)
            if item not in dic:
                dic[item] = {}
                dic[item][i] = [index + 1]
            # item present
            else:
                temp = dic[item]
                # doc present
                if i in temp:
                    dic[item][i].append(index + 1)
                # doc not present
                else:
                    dic[item][i] = [index + 1]

    #writing dictionary to file
    json.dump(dic, open("invertedIndex.txt", 'w'))





# Query Function
def booleanquery(query):
    # tokenization of query
    words = word_tokenize(query)
    words = [word for word in words if word not in stopwords]

    # operators
    op = ['AND', 'OR', 'NOT']

    # stemming query words that are not operators
    for index, item in enumerate(words):
        if item not in op:
            item = item.lower()
            words[index] = ps.stem(item)

    # words in query
    queryList = [item for item in words if item not in op]
    # operators in query
    operatorList = [item for item in words if item in op]
    # document output list
    docList = []

    temp = set()

    # appending docList if query word is found
    for index, items in enumerate(queryList):
        # if query is present in the document
        if queryList[index] in dic:
            ls = []
            for key in dic[queryList[index]]:
                ls.append(key)
            if len(operatorList) > 0:
                # if NOT comes at first position
                if operatorList[0] == 'NOT' and index == 0:
                    for j in dic:
                        for k in dic[j]:
                            temp.add(k)
                    ls = list(set(temp) - set(ls))

            docList.append(ls)
            # print(docList)

    i = 0
    result = []

    # if any document is found
    if docList:
        # for simple boolean query
        if len(operatorList) == 0:
            print("Result: ",docList)
            return docList

        elif operatorList[0] == 'NOT' and len(operatorList) == 1:
            print("Result: ",docList)
            return docList

        # for complex boolean query
        else:
            # loop until there are operators in the query
            while i < len(operatorList):
                if operatorList[0] == 'NOT':
                    operator = operatorList[1]
                else:
                    operator = operatorList[i]
                doc1 = docList[i]
                if i < len(docList) - 1:
                    doc2 = docList[i + 1]
                else:
                    doc2 = docList[i]

                if i == 0:
                    # for AND and OR for first iteration
                    if operator == 'AND':
                        result = list(set(doc1) & set(doc2))
                    elif operator == 'OR':
                        result = list(set(doc1) | set(doc2))
                else:
                    # for AND and OR and NOT for rest of the iterations
                    if operator == 'AND':
                        # print("-->",result doc2)
                        result = list(set(result) & set(doc2))
                    elif operator == 'OR':
                        result = list(set(result) | set(doc2))
                    else:
                        result = list(set(result) - set(doc2));
                i = i + 1

            result.sort()
            # result
            print("\n\nResult: ",result)
            return result


def proximityquery(query,displacement):
    #removing puntution
    text = re.sub(r'[^\w\s]', ' ', query).lower()
    #tokenization
    text = word_tokenize(text)
    words = []
    #stemming
    for word in text:
        if not word.isdigit():
            words.append(ps.stem(word))

    #dictionary with positions
    dicList = {}
    #dictionary with doc
    docList=[]


    for item in words:
        if item in dic:
            dicList[item] = dic[item]

    for index, items in enumerate(words):
        # if query is present in the document
        if words[index] in dic:
            ls = []
            for key in dic[words[index]]:
                ls.append(key)
            docList.append(ls)

    #finding documents with query words
    result = list(set(docList[0]) & set(docList[1]))
    result.sort()

    #final result = having documents which have correct proximity
    finalResult = []

    #loop over documents
    for index, item in enumerate(result):
        p1 = dicList[words[0]][item]
        p2 = dicList[words[1]][item]
        i,j = 0,0

        #loop over list of positions in the document
        while i < len(p1) and j < len(p2):
            #if displacement is less than or equal to proximiy
            if abs(p1[i] - p2[j]) <= (int(displacement)+1):
                finalResult.append(item)
                break
            #displacement is larger than proximity
            else:
                # if i is small
                if i < j:
                    i=i+1
                #if i is large
                elif i > j:
                    j = j+1
                #if both are equal
                else:
                    i=i+1
                    j=j+1
    #final result
    print("\n\nResult:",finalResult)
    return result


def querytype(query):
    flag = False
    displacement=0
    words = query.split(' ')
    for word in words:
        if '/' in word:
            for i,a in enumerate(word):
                if a == '/' and word[i+1].isdigit():
                    displacement = word[i+1]
                    flag=True

    if flag == False:
        return booleanquery(query)
    else:
        return proximityquery(query,displacement)
# def main():
#     while True:
#         print("\n\n1. Search Query\n2. Exit")
#         inp = input()
#         if int(inp) == 1:
#
#             # reading from file and making inverted list, includes cleaning, tokenization, stemming
#             invertedindex()
#
#             # for not making inverted index everytime
#             # dic = json.load(open("invertedIndex.txt"))
#
#             query = input("Enter Query: ")
#
#             # checking query type
#             querytype(query)
#         else:
#             exit()



