"""
Description     : Simple Python implementation of the Apriori Algorithm

Usage:
    $python apriori.py -f DATASET.csv -s minSupport  -c minConfidence

    $python apriori.py -f DATASET.csv -s 0.15 -c 0.6
"""

import sys

from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser


def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        """calculates the support for items in the itemSet and returns a subset
       of the itemSet each of whose elements satisfies the minimum support"""
        _itemSet = set()
        localSet = defaultdict(int)

        # itemSet内の各要素について出現頻度をカウントする
        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        # しきい値以上のsupport値を持つ要素のみを結果として返す
        for item, count in localSet.items():
                support = float(count)/len(transactionList)

                if support >= minSupport:
                        _itemSet.add(item)

        return _itemSet


def joinSet(itemSet, length):
        """Join a set with itself and returns the n-element itemsets"""
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            # 全アイテムリストを作成（重複無し）
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


### modified ###
# def runApriori(data_iter, minSupport, minConfidence):
def runApriori(data_iter, minSupport, minConfidence,minLift):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
     
    ### added ###
    lift = P(B|A)/P(B)
         = P(A U B)/P(A)*P(B)
         = conf(A => B)/sup(B)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    # 初回の調査
    # itemSetの各要素は単一item
    # minSupport以上の要素が返ってくる
    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    # minSupport以上の要素がなくなるまで要素の結合と探索を繰り返す
    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        # 各要素の要素数が一つだけ大きくなるような集合を生成する
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return float(freqSet[item])/len(transactionList)

    # minSupport以上の組み合わせを列挙する
    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    # 相関(association)ルールを列挙する
    toRetRules = []
    print(largeSet.items())
    for key, value in list(largeSet.items())[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                ### added ###
                # item = element U remain
                remain = item.difference(element)
                if len(remain) > 0:
                    ### added ###
                    # conf(A => B) = P(B | A) = sup(A U B)/sup(A)
                    confidence = getSupport(item)/getSupport(element)
                    ### added ###
                    # lift = conf(A => B)/sup(B)
                    lift = confidence / getSupport(remain)
                    ### modified ###
                    #if confidence >= minConfidence:
                    if confidence >= minConfidence and lift >= minLift:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence,lift))
    return toRetItems, toRetRules


def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    item_list = sorted(items, key=lambda x: x[1])
    for item, support in item_list:
        print("item: %s , %.3f" % (str(item), support))
    print("\n------------------------ RULES:")
    rule_list = sorted(rules, key=lambda x: x[2])
    for rule, confidence,lift in rule_list:
        pre, post = rule
        print("Rule: %s ==> %s , conf=%.3f, lift=%.3f" % (str(pre), str(post), confidence, lift))


def dataFromFile(fname):
        """Function which reads from the file and yields a generator"""
        file_iter = open(fname, 'rU')
        for line in file_iter:
                line = line.strip().rstrip(',')                         # Remove trailing comma
                record = frozenset(line.split(','))
                yield record


if __name__ == "__main__":

    optparser = OptionParser()
    optparser.add_option('-f', '--inputFile',
                         dest='input',
                         help='filename containing csv',
                         default=None)
    optparser.add_option('-s', '--minSupport',
                         dest='minS',
                         help='minimum support value',
                         default=0.15,
                         type='float')
    optparser.add_option('-c', '--minConfidence',
                         dest='minC',
                         help='minimum confidence value',
                         default=0.6,
                         type='float')
    ### added ###
    # lift値の指定用の引数
    optparser.add_option('-l','--minLift',
                         dest='minL',
                         help='lift value',
                         default=1.0,
                         type='float')

    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is None:
            inFile = sys.stdin
    elif options.input is not None:
            inFile = dataFromFile(options.input)
    else:
            print('No dataset filename specified, system with exit\n')
            sys.exit('System will exit')

    minSupport = options.minS
    minConfidence = options.minC
    ### added ###
    # lift値
    minLift = options.minL

    ### modified ###
    # items, rules = runApriori(inFile, minSupport, minConfidence)
    items, rules = runApriori(inFile, minSupport, minConfidence,minLift)

    printResults(items, rules)
