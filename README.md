# 5800 Final Project Report
## Xinyi Feng, Mozhi Shen, Jing Ye   
###

### Main target:
* Mapping 2385 tax codes from specific categories in avalara.xlsx file as much and accurately as possible with the commodity in the UNSPSC.csv file. 


### How to run: 
* put <u>Avalara_goods_and_services.xlsx</u> & <u>UNSPSC_English.csv</u> in this file and run any .py in main generator based on which version you want

***

### data_processing:
* contains the tree_builder and JSON file for both avalara and UNSPSC.
* contains <u>deny_words generator.</u>

### main_generator:
contains the function that output the final report:
 * <u>v1, v2: </u> unsuccessful attempt, not runnable.
 * <u>v3 to v5: </u> runnable generators that output first,second,find mapping result.

### result:
contains 3 version of result with a 20 elements random_sampling:
 * <u>first:</u> dynamic_brute_searching, manuel deny_words, naive scoring system
 * <u>second:</u> dynamic_brute_searching, manuel deny_words, cos-similarity without cut_off points
 * <u>final:</u> dynamic_brute_searching, generated deny_words,cos-similarity with cut_off points