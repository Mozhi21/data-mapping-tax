import json
from styleframe import StyleFrame, utils


class AvalaraRoot():
    def __init__(self):
        # sf = StyleFrame.read_excel("Avalara_goods_and_services.xlsx", skiprows=[0, 2], header=0, read_style=True)
        # changed by mozhi
        sf = StyleFrame.read_excel("../Avalara_goods_and_services.xlsx", read_style=True)

        indices = sf.row_indexes
        # added buy mozhi
        sf.rename(
            columns={"Unnamed: 0": "Tax code", "AvaTax System Tax Codes": "Description", "Unnamed: 2": "Information"},
            inplace=True)

        self.general_type = dict()
        # print(self.general_type)
        # print(sf["Description"])
        for i in range(2, len(indices) - 1):
            if sf["Description"][i].style.font_color == "FF0081C6":
                # print(sf["Description"][i].style.font_color)
                currGeneral = GeneralType(str(sf['Tax code'][i]), str(sf["Description"][i]), str(sf["Information"][i]))
                self.general_type[str(sf["Description"][i])] = currGeneral
            else:
                currSpecific = SpecificType(str(sf['Tax code'][i]), str(sf["Description"][i]), str(sf["Information"][i]))
                currGeneral.specificTypeDict[str(sf["Description"][i])] = currSpecific
            # if i == 30:
            #     break



class GeneralType():
    def __init__(self, taxCode, generalTypeName, information):
        self.taxCode = taxCode
        self.generalTypeName = generalTypeName
        self.information = information
        self.specificTypeDict = dict()

    def __str__(self):
        return f"taxCode={self.taxCode}, generalTypeName={self.generalTypeName}, " \
               f"information={self.information}, specificTypeDict={self.specificTypeDict}"


class SpecificType():
    def __init__(self, taxCode, specificTypeName, information):
        self.taxCode = taxCode
        self.specificTypeName = specificTypeName
        self.information = information

    def __str__(self):
        return f"taxCode={self.taxCode}, specificTypeName={self.specificTypeName}, " \
               f"information={self.information}"


# a = AvalaraRoot().general_type
# print("number of general_type: " + str(len(a)))
# print("number of specific_type: " + str(2547 - 3 - len(a)))
# number of general_type: 159
# number of specific_type: 2385
# with open("tree_avalara.json", "w") as outfile:
#     json.dump(data, outfile, default=lambda o: getattr(o, '__dict__', str(o)), indent=4, ensure_ascii=False)