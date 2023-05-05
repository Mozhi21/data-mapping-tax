import json
import math
import random
from collections import Counter
from data_processing.tree_avalara import AvalaraRoot
from data_processing.tree_unspsc import UNSPSCRoot
import re
from functools import lru_cache
import time

start_time = time.time()

# from deny_words_generator.py
deny_list = ['', 'and', 'to', 'the', 'a', 'or', 'for', 'of', 'that', 'with', 'services', 'are', 'related', 'as', 'in',
             'by', 'on', 'non', 'other', 'health', 'this', 'code', 'from', 'products']
split_str = '\,|\.|\(|\-|\)|\/| '
# cut score for cosine similarity
CUT_SCORE = 0.26


def lower_list(string_list):
    return list(map(lambda x: x.lower(), string_list))


# with cos-similarity grading implemented.
def get_matching_score(group, alavara_good):
    # print(f"comparing {group.id} with {alavara_good.taxCode}")
    title_words = lower_list(re.split(split_str, group.title))
    def_words = lower_list(re.split(split_str, group.definition))
    matching_target = title_words + def_words
    alavara_type_name = lower_list(re.split(split_str, alavara_good.specificTypeName))
    alavara_type_info = lower_list(re.split(split_str, alavara_good.information))
    matching_source = alavara_type_name + alavara_type_info
    return _do_get_match_score(matching_source, matching_target)


def _do_get_match_score(matching_source, matching_target):
    matching_source = Counter([word for word in matching_source if word not in deny_list])
    matching_target = Counter([word for word in matching_target if word not in deny_list])
    intersection = set(matching_source.keys()) & set(matching_target.keys())
    numerator = sum([matching_source[x] * matching_target[x] for x in intersection])

    sum1 = sum([matching_source[x] ** 2 for x in list(matching_source.keys())])
    sum2 = sum([matching_target[x] ** 2 for x in list(matching_target.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


@lru_cache
def get_all_families():
    return [family for segment in unspsc_root.segments.values() for family in segment.families.values()]


@lru_cache
def get_all_classes():
    return [commodity_class for family in get_all_families() for commodity_class in family.classes.values()]


@lru_cache
def get_classes_by_segment(segment):
    return [commodity_class for family in segment.families.values() for commodity_class in family.classes.values()]


@lru_cache
def get_all_commodities():
    return [commodity for commodity_class in get_all_classes() for commodity in commodity_class.commodities.values()]


@lru_cache
def get_commodities_by_segment(segment):
    return [commodity for commodity_class in get_classes_by_segment(segment) for commodity in
            commodity_class.commodities.values()]


@lru_cache
def get_commodities_by_family(family):
    return [commodity for commodity_class in family.classes.values() for commodity in
            commodity_class.commodities.values()]


def locate_segment(general_type, unspsc_root):
    segment_keywords = get_path_keywords(unspsc_root)
    general_type_keywords = get_general_type_keywords(general_type)
    max_segment_score = CUT_SCORE
    max_segment = None
    for segment, keywords in segment_keywords.items():
        segment_score = _do_get_match_score(general_type_keywords, keywords)
        if segment_score > max_segment_score:
            max_segment_score = segment_score
            max_segment = segment
    print("max segment score:", max_segment_score)
    return max_segment


def get_general_type_keywords(general_type):
    keywords = []
    for specific_type in general_type.specificTypeDict.values():
        keywords += get_specific_type_keywords(specific_type)
    return keywords


def get_specific_type_keywords(specific_type):
    keywords = []
    keywords += lower_list(re.split(split_str, specific_type.specificTypeName))
    keywords += lower_list(re.split(split_str, specific_type.information))
    # dedup
    return keywords


@lru_cache
# used all imformation from a segment including inner elements。
def get_path_keywords(unspsc_root):
    segment_keywords = dict()
    for segment in unspsc_root.segments.values():
        keywords = []
        keywords += lower_list(re.split(split_str, segment.title))
        keywords += lower_list(re.split(split_str, segment.definition))
        for family in segment.families.values():
            keywords += lower_list(re.split(split_str, family.title))
            keywords += lower_list(re.split(split_str, family.definition))
            for commodity_class in family.classes.values():
                keywords += lower_list(re.split(split_str, commodity_class.title))
                keywords += lower_list(re.split(split_str, commodity_class.definition))
                for commodity in commodity_class.commodities.values():
                    keywords += lower_list(re.split(split_str, commodity.title))
                    keywords += lower_list(re.split(split_str, commodity.definition))
        segment_keywords[segment] = keywords
    return segment_keywords


@lru_cache
def get_commodity_path_keywords(unspsc_root):
    commodity_keywords = dict()
    for segment in unspsc_root.segments.values():
        segment_keywords = lower_list(re.split(split_str, segment.title)) + lower_list(
            re.split(split_str, segment.definition))
        for family in segment.families.values():
            family_keywords = lower_list(re.split(split_str, family.title)) + lower_list(
                re.split(split_str, family.definition))
            for commodity_class in family.classes.values():
                class_keywords = lower_list(re.split(split_str, commodity_class.title)) + lower_list(
                    re.split(split_str, commodity_class.definition))
                for commodity in commodity_class.commodities.values():
                    commodity_keywords[commodity] = segment_keywords + family_keywords + class_keywords + lower_list(
                        re.split(split_str, commodity.title)) * 10 + lower_list(
                        re.split(split_str, commodity.definition)) * 10
    return commodity_keywords


avalara_root = AvalaraRoot()
unspsc_root = UNSPSCRoot()
res = dict()
running_time = time.time()

# iterate thru each specific type
for general_type in avalara_root.general_type.values():
    # mozhi: changed segment to max_segment
    max_segment = locate_segment(general_type, unspsc_root)

    for specific_type in general_type.specificTypeDict.values():
        # mozhi: changed segment to max_segment
        if max_segment:  # found target segment
            print("searching families in segment:", max_segment.title)
            family_candidates = max_segment.families.values()
        else:
            family_candidates = get_all_families()
            print("searching in all families. num:", len(family_candidates))

        # locate family
        max_family_score = CUT_SCORE - 0.01
        max_family = None
        for family in family_candidates:
            family_score = get_matching_score(family, specific_type)
            if family_score > max_family_score:
                max_family_score = family_score
                max_family = family
        if max_family:  # found target family
            print("family max score:", max_family_score)
            print("searching classes in family:", family.title)
            class_candidates = max_family.classes.values()
        elif max_segment:
            print("searching in all classes in segment:", max_segment.title)
            class_candidates = get_classes_by_segment(max_segment)
        else:
            class_candidates = get_all_classes()
            print("searching in all classes. num:", len(class_candidates))

        # locate class
        # setting  cut_off bar
        max_class_score = CUT_SCORE -0.02
        max_class = None
        for commodity_class in class_candidates:
            class_score = get_matching_score(commodity_class, specific_type)
            # only mappings that get score higher than the bar would be kept.
            if class_score > max_class_score:
                max_class_score = class_score
                max_class = commodity_class
        if max_class:
            print("class max score:", max_class_score)
            print("searching commodities in class:", commodity_class.title)
            commodity_candidates = max_class.commodities.values()
        elif max_family:
            print("searching in all commodities in family:", max_family.title)
            commodity_candidates = get_commodities_by_family(max_family)
        elif max_segment:
            print("searching in all commodities in segment:", max_segment.title)
            commodity_candidates = get_commodities_by_segment(max_segment)
        else:
            commodity_candidates = get_all_commodities()
            print("searching in all commodities. num:", len(commodity_candidates))

        # locate commodities
        max_comm_score = CUT_SCORE-0.03
        max_comm = None
        for comm in commodity_candidates:
            comm_score = get_matching_score(comm, specific_type)
            if comm_score > max_comm_score:
                max_comm_score = comm_score
                max_comm = comm
        if max_comm:
            print("Commodity max score", max_comm_score)
            print("Commodity found for", specific_type)
            print(max_comm)
            res[str(specific_type)] = str(max_comm.title) + " " + str(max_comm.id) + " " + str(max_comm.definition)

        else:
            print("No commodity found for", specific_type)

        print("Running time for this round: " + str(time.time() - running_time))
        running_time = time.time()
        print()


res_sampling = random.sample(res.items(), 20)
with open("../result/final_mapping.json", "w", encoding="utf-8") as writeJsonfile:
    json.dump(res, writeJsonfile, indent=4, default=str)

with open("../result/final_mapping_random_sampling.json", "w", encoding="utf-8") as writeJsonfile2:
    json.dump(res_sampling, writeJsonfile2, indent=4, default=str)

print("total running time in s: " + str(time.time() - start_time))