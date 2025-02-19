import json
import torch
import torch.nn as nn

class Dataset(): 

    def __init__(self, train_file, dev_file, test_file, word_to_idx, tag_to_idx):
        # word_to_idx/tag_to_idx: both are functions, whose input is a string and output an int

        self.train_file = train_file
        self.dev_file = dev_file
        self.test_file = test_file

        self.word_to_idx = word_to_idx
        self.tag_to_idx = tag_to_idx

    def trainset(self, batch_size=1, drop_last=False):
        for batch in self.sample_batches(self.train_file, batch_size=batch_size, drop_last=drop_last):
            yield batch
            
    def devset(self, batch_size=1, drop_last=False):
        for batch in self.sample_batches(self.dev_file, batch_size=batch_size, drop_last=drop_last):
            yield batch

    def testset(self, batch_size=1, drop_last=False):
        for batch in self.sample_batches(self.test_file, batch_size=batch_size, drop_last=drop_last):
            yield batch

    def sentence_to_tensor(self, s):
        # s: string or list
        # return: 1-d long tensor of shape (seq_len)
        return torch.LongTensor([self.word_to_idx(w) for w in s])

    def pad_sequence(self, s):
        # TODO pad to 512?
        return nn.utils.rnn.pad_sequence(s, batch_first=True)

    def samples(self, file_path):

        with open(file_path, 'r') as f:

            labels = f.readline().strip().split('\t') # Omit tsv header

            is_train = file_path == self.train_file

            print (f'labels: {labels}')
            for line in f:
                line = line.strip().split('\t')

                # Since the trainset is different from devset and testset
                if is_train:
                    sent1 = line[labels.index('premise')]
                    sent2 = line[labels.index('hypo')]
                    tag = line[labels.index('label')]

                else: 
                    language = line[labels.index('language')]
                    if language != 'zh': continue
                    sent1 = line[labels.index('sentence1')]
                    sent2 = line[labels.index('sentence2')]
                    tag = line[labels.index('gold_label')]

                # sent1, sent2, tag = ''.join(sent1.split()), ''.join(sent2.split()), tag
                # print (sent1, sent2, tag)
                # input ()
                yield ''.join(sent1.split()), ''.join(sent2.split()), tag
                


   
    def sample_batches(self, file_path, batch_size=1, drop_last=False):
        # drop_last: drop the last incomplete batch if True
        cnt = 0

        # Input
        sent1_batch, sent2_batch = [], [] # (batch_size, seq_len)
        # Target
        tag_batch = [] # (batch_size)

        for sent1, sent2, tag in self.samples(file_path):
            # all string-like

            sent1_batch.append(self.sentence_to_tensor(sent1))
            sent2_batch.append(self.sentence_to_tensor(sent2))
            tag_batch.append(self.tag_to_idx(tag))

            cnt += 1

            if cnt >= batch_size:
                yield self.pad_sequence(sent1_batch), self.pad_sequence(sent2_batch), torch.LongTensor(tag_batch)
                sent1_batch, sent2_batch, tag_batch = [], [], []
                cnt = 0

        if cnt > 0 and not drop_last:
            yield self.pad_sequence(sent1_batch), self.pad_sequence(sent2_batch), torch.LongTensor(tag_batch)




if __name__ == '__main__': 
    # Usage
    train_file = 'XNLI-MT-1.0/multinli/multinli.train.zh.tsv'
    dev_file = 'XNLI-1.0/xnli.dev.tsv'
    test_file = 'XNLI-1.0/xnli.test.tsv'

    def word_to_idx(w):
        w2i = {'当': 1, '希': 2}
        return w2i.get(w, 0)

    def tag_to_idx(tag):
        t2i = {'neutral':0, 'entailment': 1, 'contradictory': 2, 'contradiction': 2}
        return t2i[tag]

    dataset = Dataset(train_file=train_file, dev_file=dev_file, test_file=test_file, word_to_idx=word_to_idx, tag_to_idx=tag_to_idx)

    cnt = 0
    for sent1_batch, sent2_batch, tag_batch in dataset.trainset(batch_size=10, drop_last=False):
        # print (f'sent1_batch: {sent1_batch.shape}, sent2_batch: {sent2_batch.shape}, tag_batch: {tag_batch.shape}')
        # input ()
        cnt += sent1_batch.shape[0]
    print (f'trainset: {cnt}')
    
    cnt = 0
    for sent1_batch, sent2_batch, tag_batch in dataset.devset(batch_size=10, drop_last=False):
        # print (f'sent1_batch: {sent1_batch.shape}, sent2_batch: {sent2_batch.shape}, tag_batch: {tag_batch.shape}')
        # input ()
        cnt += sent1_batch.shape[0]
    print (f'devset: {cnt}')

    cnt = 0
    for sent1_batch, sent2_batch, tag_batch in dataset.testset(batch_size=10, drop_last=False):
        print (f'sent1_batch: {sent1_batch.shape}, sent2_batch: {sent2_batch.shape}, tag_batch: {tag_batch.shape}')
        input ()
        cnt += sent1_batch.shape[0]
    print (f'testset: {cnt}')
