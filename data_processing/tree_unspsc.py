import collections
from csv import reader


names = ['Version', 'Key',
         'Segment', 'Segment Title', 'Segment Definition',
         'Family', 'Family Title', 'Family Definition', 'Column1',
         'Class', 'Class Title', 'Class Definition',
         'Commodity', 'Commodity Title', 'Definition', 'Synonym', 'Acronym']

class UNSPSCRoot:
    def __init__(self):
        self.segments = dict()
        with open('../UNSPSC_English.csv', 'r', encoding="utf8") as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # skip headers
            for _ in range(10):
                next(csv_reader)
            # Iterate over each row in the csv using reader object
            i = 0
            for row in csv_reader:
                # print(row)
                i += 1
                # read values from the row
                values = collections.defaultdict(str)
                for name, part in zip(names, row):
                    values[name] = part
                # parse values to segment, family, class and commodity
                curr_segment = Segment(values['Segment'], values['Segment Title'], values['Segment Definition'])
                curr_family = Family(values['Family'], values['Family Title'], values['Family Definition'], values['Column1'])
                curr_class = Class(values['Class'], values['Class Title'], values['Class Definition'])
                curr_commodity = Commodity(values['Commodity'], values['Commodity Title'], values['Commodity Definition'],
                                           values['Synonym'], values['Acronym'])
                # build the tree
                if curr_segment.id:
                    if curr_segment.id not in self.segments:
                        self.segments[curr_segment.id] = curr_segment
                    else:
                        curr_segment = self.segments[curr_segment.id]
                else:
                    continue

                if curr_family.id:
                    if curr_family.id not in curr_segment.families:
                        curr_segment.families[curr_family.id] = curr_family
                    else:
                        curr_family = curr_segment.families[curr_family.id]
                else:
                    continue

                if curr_class.id:
                    if curr_class.id not in curr_family.classes:
                        curr_family.classes[curr_class.id] = curr_class
                    else:
                        curr_class = curr_family.classes[curr_class.id]
                else:
                    continue

                if curr_commodity.id and curr_commodity.id not in curr_class.commodities:
                    curr_class.commodities[curr_commodity.id] = curr_commodity

class Segment:
    def __init__(self, id, title, definition):
        self.id = id
        self.title = title
        self.definition = definition
        self.families = dict()

    def __str__(self):
        return f"Seg_id={self.id}, Seg_title={self.title}, Seg_def={self.definition}, families={self.families}"


class Family:
    def __init__(self, id, title, definition, column1):
        self.id = id
        self.title = title
        self.definition = definition
        self.column1 = column1
        self.classes = dict()

    def __str__(self):
        return f"Fam_id={self.id}, Fam_title={self.title}, Fam_def={self.definition}, Fam_column1={self.column1}, classes={self.classes}"


class Class:
    def __init__(self, id, title, definition):
        self.id = id
        self.title = title
        self.definition = definition
        self.commodities = dict()

    def __str__(self):
        return f"Class_id={self.id}, Class_title={self.title}, Class_def={self.definition}, commodities={self.commodities}"


class Commodity:
    def __init__(self, id, title, definition, synonyms, acronyms):
        self.id = id
        self.title = title
        self.definition = definition
        self.synonyms = synonyms
        self.acronyms = acronyms

    def __str__(self):
        return f"Commodity_id={self.id}, Commodity_title={self.title}, Commodity_def={self.definition}," \
               f" Commodity_synonyms={self.synonyms},Commodity_acronyms={self.acronyms}"

