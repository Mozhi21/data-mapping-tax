import json
import random
import re
import time
from functools import lru_cache

from data_processing.tree_avalara import AvalaraRoot
from data_processing.tree_unspsc import UNSPSCRoot


deny_list = ["", "the", "is", "a", "an", "or", "to", "and", "in", "on",
             "segment", "family", "class", "use", "for", "with", "of", "this", "that", "as", "by"]
split_str = '\,|\.|\(|\-|\)|\/| '
# function stored in main()
# needs 7.5 hours to compute on m1 pro.


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


# initial version of grading.
def _do_get_match_score(matching_source, matching_target):
    matching_source = [word for word in matching_source if word not in deny_list]
    matching_target = [word for word in matching_target if word not in deny_list]
    score = 0
    for word in matching_source:
        if word in deny_list:
            continue
        if word in matching_target:
            score += 1
    if score == 0:
        return 0
    return score/(len(matching_source)*len(matching_target))


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
    max_segment_score = 0
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


def _do_get_match_score(matching_source, matching_target):
    matching_source = [word for word in matching_source if word not in deny_list]
    matching_target = [word for word in matching_target if word not in deny_list]
    score = 0
    for word in matching_source:
        if word in deny_list:
            continue
        if word in matching_target:
            score += 1
    if score == 0:
        return 0
    return score/(len(matching_source)*len(matching_target))


avalara_root = AvalaraRoot()
unspsc_root = UNSPSCRoot()


commodity_keywords = get_commodity_path_keywords(unspsc_root)
print("constructed commodity keywords map. size:", len(commodity_keywords))
running_time = time.time()
res = dict()

for general_type in avalara_root.general_type.values():
    for specific_type in general_type.specificTypeDict.values():
        max_comm_score = 0
        max_comm = None
        specific_type_keywords = get_specific_type_keywords(specific_type)
        print("searching specific_type", specific_type)
        for commodity, keywords in commodity_keywords.items():
            comm_score = _do_get_match_score(specific_type_keywords, keywords)
            if comm_score > max_comm_score:
                max_comm_score = comm_score
                max_comm = commodity
                print(comm_score)
                print(commodity)
        if max_comm:
            print("=== Found Commodity ===")
            print("specific_type", specific_type)
            print("max score", max_comm_score)
            print("commodity", max_comm)
            res[str(specific_type)] = str(max_comm.title) + " " + str(max_comm.id) + " " + str(max_comm.definition)
        else:
            print("No commodity found for", specific_type)

        print()

print("total running time in s: " + str(time.time()-running_time))
res_sampling = random.sample(res.items(), 20)

with open("first_mapping_brute.json", "w", encoding="utf-8") as writeJsonfile:
     json.dump(res, writeJsonfile, indent=4, default=str)

with open("first_mapping_brute_sampling.json", "w", encoding="utf-8") as writeJsonfile2:
    json.dump(res_sampling, writeJsonfile2, indent=4, default=str)

exit(0)