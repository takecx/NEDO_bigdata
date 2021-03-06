"""
Description     : Simple Python implementation of the Apriori Algorithm

Usage:
    $python apriori.py -f DATASET.csv -s minSupport  -k maxKulczynski

    $python apriori.py -f DATASET.csv -s 0.15 -k 0.1
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

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

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
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


def runApriori_neg(data_iter, minSupport, maxKul):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    # データ取得
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k - 1] = currentLSet
        # 一つ大きい要素数の組み合わせを作成する
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

    # 要素の組み合わせとその時のsupport値を計算する
    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])
    toRetRules = []
    # minSupport以上の全組み合わせ
    allSet = []
    for key, value in list(largeSet.items()):
        for i in value:
            allSet.append(i)

    # item1とitem2はset()
    for item1 in allSet:
        for item2 in allSet:
            # 共通の要素が無い場合
            if len(item1 & item2) == 0:
                # item_union = item1 U item2
                item_union = item1.union(item2)

                # 和集合の出現回数を計算する
                if freqSet[item_union] == 0:
                    for transaction in transactionList:
                        if item_union.issubset(transaction):
                            freqSet[item_union] += 1
                # Kulczynski 尺度基準を計算
                # 前提：アイテム集合XとYは頻出である
                # (P(X|Y) + P(Y|X)) / 2 < e
                # conf(A => B) = P(B|A) = sup(A U B)/sup(A)
                p_xy = getSupport(item_union) / getSupport(item1)
                p_yx = getSupport(item_union) / getSupport(item2)
                kulc = (p_xy + p_yx) / 2
                # 算出したkulcに従ってルールとするかどうかを判定する
                if kulc < maxKul:
                        toRetRules.append(((tuple(item1), tuple(item2)), p_xy, kulc))

    return toRetItems, toRetRules

def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    item_list = sorted(items, key=lambda x: x[1])
    for item, support in item_list:
        print("item: %s , %.3f" % (str(item), support))
    print("\n------------------------ RULES:")
    rule_list = sorted(rules, key=lambda x: x[2])
    for rule, confidence,kulc in rule_list:
        pre, post = rule
        print("Rule: %s ==> %s , conf=%.3f, kulc=%.3f" % (str(pre), str(post), confidence,kulc))

def dataFromFile(fname):
        """Function which reads from the file and yields a generator"""
        file_iter = open(fname, 'r')
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
    # こいつがイプシロン
    optparser.add_option('-k', '--maxKul',
                         dest='maxK',
                         help='maximum kulczynski value',
                         default=0.1,
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
    maxKul = options.maxK
    items, rules = runApriori_neg(inFile, minSupport, maxKul)
    printResults(items, rules)
