import json
import torch
import torch.nn as nn

class Dataset(): 

    def __init__(self, train_file, dev_file, test_file, vocab):
        # vocab: dict-like, map word to idx, e.g. vocab['a'] = 1

        self.train_file = train_file
        self.dev_file = dev_file
        self.test_file = test_file

        self.vocab = vocab

    def trainset(self, batch_size=1, drop_last=False):
        for batch in self.sample_batches(self.train_file, batch_size=batch_size, drop_last=drop_last):
            yield batch
            
    def devset(self, batch_size=1, drop_last=False):
        for batch in self.sample_batches(self.dev_file, batch_size=batch_size, drop_last=drop_last):
            yield batch

    def testset(self, batch_size=1, drop_last=False):
        for batch in self.sample_batches(self.test_file, batch_size=batch_size, drop_last=drop_last):
            yield batch
   
    def str_to_tensor(self, s):
        # s: string
        # return: 1-d long tensor of shape (seq_len)

        # TODO prune long str
        # OOV is of index 0
        # FIXME
        return torch.LongTensor([self.vocab.get(c, 0) for c in s])
        # return torch.LongTensor([self.vocab[c] for c in s])
    
    def pad_sequence(self, s):
        # TODO pad to 512?
        return nn.utils.rnn.pad_sequence(s, batch_first=True)

    def samples(self, file_path):

        with open(file_path, 'r') as f:
            data = json.load(f)
            data = data['data']

            # Input
            docs = [] #  (batch_size, doc_len)
            quests = [] # (batch_size, quest_len)
            # Target
            start_idxs = [] # (batch_size)
            end_idxs = [] # (batch_size)

            for d in data:

                for p in d['paragraphs']:
                    doc = p['context']

                    for qa in p['qas']:
                        quest = qa['question']

                        a_set = set()
                    
                        for ans in qa['answers']:
                            # devset with duplicate answers provided...
                            # only choose the first answer
                            if len(a_set) != 0: continue 
                            a_set.add(ans['text'])
                       
                            start_idx = ans['answer_start']
                            end_idx = start_idx + len(ans) - 1
                            yield doc, quest, start_idx, end_idx

   
    def sample_batches(self, file_path, batch_size=1, drop_last=False):
        # drop_last: drop the last incomplete batch if True
        cnt = 0

        # Input
        docs = [] #  (batch_size, doc_len)
        quests = [] # (batch_size, quest_len)
        # Target
        start_idxs = [] # (batch_size)
        end_idxs = [] # (batch_size)

        for doc, q, si, ei in self.samples(file_path):
            # all tensor-like

            docs.append(self.str_to_tensor(doc))
            quests.append(self.str_to_tensor(q))
            start_idxs.append(torch.LongTensor([si]))
            end_idxs.append(torch.LongTensor([ei]))

            cnt += 1

            if cnt >= batch_size:
                yield self.pad_sequence(docs), self.pad_sequence(quests), torch.cat(start_idxs), torch.cat(end_idxs)
                docs, quests, start_idxs, end_idxs = [], [], [], []
                cnt = 0

        if cnt > 0 and not drop_last:
            yield self.pad_sequence(docs), self.pad_sequence(quests), torch.cat(start_idxs), torch.cat(end_idxs)


if __name__ == '__main__': 
    # Usage
    train_file = 'cmrc2018/squad-style-data/cmrc2018_train.json'
    dev_file = 'cmrc2018/squad-style-data/cmrc2018_dev.json'
    test_file = 'cmrc2018/squad-style-data/cmrc2018_trial.json'

    # maps word to index, 0 for OOV, e.g. vocab['a'] = 1
    vocab = {}

    dataset = Dataset(train_file=train_file, dev_file=dev_file, test_file=test_file, vocab=vocab)

    cnt = 0
    for doc, quest, start_idx, end_idx in dataset.trainset(batch_size=100, drop_last=False):
        # print (f'doc: {doc.shape}, quest: {quest.shape}, start_idx: {start_idx.shape}, end_idx: {end_idx.shape}')
        # print (quest)
        # input ()
        cnt += doc.shape[0]

    print (f'trainset: {cnt}')
    

    cnt = 0
    for doc, quest, start_idx, end_idx in dataset.devset(batch_size=100, drop_last=False):
        # print (f'doc: {doc.shape}, quest: {quest.shape}, start_idx: {start_idx.shape}, end_idx: {end_idx.shape}')
        # print (quest)
        # input ()
        cnt += doc.shape[0]

    print (f'devset: {cnt}')

    cnt = 0
    for doc, quest, start_idx, end_idx in dataset.testset(batch_size=100, drop_last=False):
        # print (f'doc: {doc.shape}, quest: {quest.shape}, start_idx: {start_idx.shape}, end_idx: {end_idx.shape}')
        # print (quest)
        # input ()
        cnt += doc.shape[0]

    print (f'testset: {cnt}')

