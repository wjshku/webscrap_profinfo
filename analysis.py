# Basic tools for extracting research areas, titles, filter

import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import torchtext.vocab as vocab
import numpy as np

work_dirs = '/Users/wjs/Library/CloudStorage/OneDrive-Personal/Coding, ML & DL/work_dirs'

# prof_df = pd.DataFrame()

def list_sum_unique_elements(nested_list:list):
    unqiue_elements = list(set(sum(nested_list,[])))
    unqiue_elements = [e for e in unqiue_elements if e != '']
    return unqiue_elements

def filter_by_title(x, title = 'Young Prof'):
    return title in x

# cache_dir是保存golve词典的缓存路径
cache_dir = '.vector_cache/glove'
# dim是embedding的维度
glove = vocab.GloVe(name='6B', dim=50, cache=cache_dir) 

def split_proper_text(text):
    # 将逗号替换为空格
    text = text.replace(',', '')
    text = text.replace('-', '')
    text = text.replace('(', '')
    text = text.replace(')', '')
    # 按空格分割字符串
    words = text.split()
    if len(words)  == 0:
        words = [' ']
    return words

def sentence_to_token(sentences: list[str]):
    wordsequence = [split_proper_text(sentence) for sentence in sentences]
    return wordsequence

def find_embedding_matrix(sentences: list[str],index_names=None):
    ri_sequence = sentence_to_token(sentences)
    if index_names is not None:
        ri_matrix = pd.DataFrame([np.mean((glove.get_vecs_by_tokens(ri_words, True)).numpy(),axis=0) for ri_words in ri_sequence],index=index_names).T.reset_index(drop=True)
    else:
        ri_matrix = pd.DataFrame([np.mean((glove.get_vecs_by_tokens(ri_words, True)).numpy(),axis=0) for ri_words in ri_sequence]).T.reset_index(drop=True)
    ri_matrix = ri_matrix[ri_matrix.sum()[ri_matrix.sum()!=0].index]
    return ri_matrix

def get_cor_withembedmatrix(input, embed_matrix):
    input = split_proper_text(input)
    input_emd = pd.Series(np.mean((glove.get_vecs_by_tokens(input, True)).numpy(),axis=0))
    return embed_matrix.corrwith(input_emd)

def filter_for_listofstrings(listofstrings:list,texts=['AI']):
    tempstring = ' '.join(listofstrings)
    for text in texts:
        if text in tempstring:
            return True
    return False