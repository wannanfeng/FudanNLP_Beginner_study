from torch.utils.data import DataLoader,Dataset
from torch.nn.utils.rnn import pad_sequence
import torch

def pre_process(data):
    sentences = list()  #储存所有文档的句子
    tags = list()
    sentence = list()  #储存单个文档句子
    tag = list()
    for line in data:
        if line == '\n':    #检查当前读取的行是否为空行
            if sentence:    #if 不为空
                sentences.append(sentence)
                tags.append(tag)
                sentence = list()
                tag = list()
            else:
                elements = line.split()  #按空格分隔
                if elements[0] == '-DOCSTART-':  #代表某一个文档开始词
                    continue
                sentence.append(elements[0].upper())
                tag.append(elements[-1])
    if sentence:
        sentences.append(sentence)
        tags.append(tag)
    return list(zip(sentences, tags))

class Glove_embedding():
    def __init__(self, train_zip, test_zip, trained_dict = None):
        if trained_dict is None:
            trained_dict = dict()
        self.dict_words = dict()
        self.trained_dict = trained_dict
        train_zip.sort(key = lambda x: len(x[0]))  #每个元素的第一个元素的长度来对列表进行排序。
        test_zip.sort(key = lambda x: len(x[0]))
        self.train_x, self.train_y = zip(*train_zip)
        self.test_x, self.test_y = zip(*test_zip)
        self.train_x_matrix = list()
        self.test_x_matrix = list()
        self.train_y_matrix = list()
        self.test_y_matrix = list()
        self.len_words = 1
        self.len_tag = 3
        self.longest = 0
        self.embedding = list()
        self.tag_dict = {'<pad>': 0, '<begin>': 1, '<end>': 2}

    def get_words(self):
        self.embedding.append([0]*50)
        for term in self.train_x:
            for word in term:
                if word not in self.dict_words:
                    self.dict_words[word] = len(self.dict_words) + 1
                    if word in self.trained_dict:
                        self.embedding.append(self.trained_dict[word])
                    else:
                        # print(word)
                        # raise Exception("words not found!")
                        self.embedding.append([0] * 50)
        for tags in self.train_y:
            for tag in tags:
                if tag not in self.tag_dict:
                    self.tag_dict[tag] = len(self.tag_dict)
        for tags in self.test_y:
            for tag in tags:
                if tag not in self.tag_dict:
                    self.tag_dict[tag] = len(self.tag_dict)
        self.len_tag = len(self.tag_dict)
        self.len_words = len(self.dict_words) + 1

    def get_id(self): #获取每句中每个单词的ID
        for term in self.train_x:
            item = [self.dict_words[word] for word in term]
            self.longest = max(self.longest, len(item))
            self.train_x_matrix.append(item)
        for term in self.test_x:
            item = [self.dict_words[word] for word in term]
            self.longest = max(self.longest, len(item))
            self.test_x_matrix.append(item)
        for tags in self.train_y:
            item = [self.tag_dict[tag] for tag in tags]
            self.train_y_matrix.append(item)
        for tags in self.test_y:
            item = [self.tag_dict[tag] for tag in tags]
            self.test_y_matrix.append(item)
class ClsDataset(Dataset):
    def __init__(self, sentence, tag):
        self.sentence = sentence
        self.tag = tag
    def __getitem__(self, item):
        return self.sentence[item], self.tag[item]
    def __len__(self):
        return len(self.tag)
def collate_fn(batch):
    sentence, tag = zip(*batch)
    sentences = [torch.LongTensor(sent) for sent in sentence]
    padded_sentences = pad_sequence(sentences, batch_first=True, padding_value=0)
    tags = [torch.LongTensor(t) for t in tag]
    padded_tags = pad_sequence(tags, batch_first=True, padding_value=0)
    return torch.LongTensor(padded_sentences), torch.LongTensor(padded_tags)

def get_batch(x, y, batch_size):
    dataset = ClsDataset(x, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, drop_last=True, collate_fn=collate_fn)
    return dataloader


