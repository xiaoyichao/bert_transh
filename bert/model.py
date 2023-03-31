import torch
import torch.nn as nn
# from transformers4token import AutoModel, AutoTokenizer, AutoConfig, BertTokenizer, BertModel, BertConfig, DistilBertTokenizer, DistilBertModel, DistilBertConfig

class DistilBERTIntent(nn.Module):
    def __init__(self, distilbert, config):
        super(DistilBERTIntent, self).__init__()
        self.distilbert = distilbert
        self.linear_1 = nn.Linear(config.hidden_size, 512)
        self.linear_2 = nn.Linear(512, 128)
        self.linear_3 = nn.Linear(128, 64)
        self.class_layer = nn.Linear(64, config.num_labels)
        self.relu_layer = nn.GELU()

        # 冻结 DistilBERT 参数
        for param in self.distilbert.parameters():
            param.requires_grad = False

        # 确认 BERT 参数被冻结
        for name, param in self.distilbert.named_parameters():
            print("确认 BERT 参数被冻结", name, param.requires_grad)

    def forward(self, encoder_embedding_dict):
        bert_outputs = self.distilbert(input_ids=encoder_embedding_dict["input_ids"], attention_mask=encoder_embedding_dict["attention_mask"], token_type_ids=encoder_embedding_dict["token_type_ids"])
        pool_hidden_state = torch.mean(bert_outputs.last_hidden_state, dim=1)

        linear_1 = self.relu_layer(self.linear_1(pool_hidden_state))
        linear_2 = self.relu_layer(self.linear_2(linear_1))
        linear_3 = self.relu_layer(self.linear_3(linear_2))
        logits = self.class_layer(linear_3)
        pred = torch.argmax(logits, dim=1)
        return logits, pred


class DistilBERTClassifier(nn.Module):
    def __init__(self, distilbert, config):
        super(DistilBERTClassifier, self).__init__()
        self.distilbert = distilbert
        self.linear_1 = nn.Linear(config.hidden_size, config.hidden_size)
        self.linear_2 = nn.Linear(config.hidden_size, config.hidden_size)
        self.class_layer = nn.Linear(config.hidden_size, config.num_labels)
        self.relu_layer = nn.ReLU()
    
    def forward(self, encoder_embedding_dict):
        
        bert_outputs = self.distilbert(input_ids=encoder_embedding_dict["input_ids"], attention_mask=encoder_embedding_dict["attention_mask"], token_type_ids=encoder_embedding_dict["token_type_ids"]) #, token_type_ids=encoder_embedding_dict["token_type_ids"]
        pool_hidden_state = torch.mean(bert_outputs.last_hidden_state, dim=1)

        linear_1 = self.relu_layer(self.linear_1(pool_hidden_state))
        linear_2 = self.relu_layer(self.linear_2(linear_1))
        
        logits = self.class_layer(linear_2)
        pred = torch.argmax(logits, dim=1)
        return logits, pred


class BERTClassifier(nn.Module):
    def __init__(self, bert, config):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.linear_1 = nn.Linear(config.hidden_size, config.hidden_size)
        self.linear_2 = nn.Linear(config.hidden_size, config.hidden_size)
        self.class_layer = nn.Linear(config.hidden_size, config.num_labels)
        self.relu_layer = nn.ReLU()
    
    def forward(self, encoder_embedding_dict):
        
        bert_outputs = self.bert(input_ids=encoder_embedding_dict["input_ids"], attention_mask=encoder_embedding_dict["attention_mask"], token_type_ids=encoder_embedding_dict["token_type_ids"]) #, token_type_ids=encoder_embedding_dict["token_type_ids"]
        pool_hidden_state = torch.mean(bert_outputs.last_hidden_state, dim=1)

        linear_1 = self.relu_layer(self.linear_1(pool_hidden_state))
        linear_2 = self.relu_layer(self.linear_2(linear_1))

        logits = self.class_layer(linear_2)
        pred = torch.argmax(logits, dim=1)
        return logits, pred
