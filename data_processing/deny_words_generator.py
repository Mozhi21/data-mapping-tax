from collections import Counter

from data_processing.tree_avalara import AvalaraRoot
from data_processing.tree_unspsc import UNSPSCRoot
from functools import lru_cache
import re

avalara_root = AvalaraRoot()
unspsc_root = UNSPSCRoot()

split_str = '\,|\.|\(|\-|\)|\/| '


def lower_list(string_list):
    return list(map(lambda x: x.lower(), string_list))


def avalara_high_freq_words(avalara_root):
    holder = []
    for general_type in avalara_root.general_type.values():
        general_keywords = lower_list(re.split(split_str, general_type.generalTypeName)) + lower_list(
        re.split(split_str, general_type.information))
        holder += general_keywords
        for specific_type in general_type.specificTypeDict.values():
            specific_keywords = lower_list(re.split(split_str, specific_type.specificTypeName)) + lower_list(
                re.split(split_str, specific_type.information))
            holder += specific_keywords

    return Counter(holder).most_common(100)


@lru_cache
def unspsc_high_freq_words(unspsc_root):
    print(1)
    # commodity_keywords = dict()
    holder =[]
    for segment in unspsc_root.segments.values():
        segment_keywords = lower_list(re.split(split_str, segment.title)) + lower_list(re.split(split_str, segment.definition))
        # print(segment_keywords)
        holder += segment_keywords
        for family in segment.families.values():
            family_keywords = lower_list(re.split(split_str, family.title)) + lower_list(re.split(split_str, family.definition))
            holder += family_keywords
            for commodity_class in family.classes.values():
                class_keywords = lower_list(re.split(split_str, commodity_class.title)) + lower_list(re.split(split_str, commodity_class.definition))
                holder += class_keywords
                for commodity in commodity_class.commodities.values():
                    # commodity_keywords[commodity] = segment_keywords + family_keywords + class_keywords + lower_list(re.split(split_str, commodity.title)) * 10 + lower_list(re.split(split_str, commodity.definition)) * 10
                    holder += lower_list(re.split(split_str, commodity.title))
                    holder += lower_list(re.split(split_str, commodity.definition))

    return Counter(holder).most_common(100)


unspsc_words_list_pairs = unspsc_high_freq_words(unspsc_root)
unspsc_hifreq_words_list = [i[0] for i in unspsc_words_list_pairs]
# print(unspsc_words_list_pairs)
print(unspsc_hifreq_words_list)

avalara_words_list_pairs = avalara_high_freq_words(avalara_root)
avalara_hifreq_words_list = [j[0] for j in avalara_words_list_pairs]
# print(avalara_words_list_pairs)
print(avalara_hifreq_words_list)

hifreq_words_list = []
for i in avalara_hifreq_words_list:
    if i in unspsc_hifreq_words_list:
        print(i)
        hifreq_words_list.append(i)
print(hifreq_words_list)