'''
Author: xiaoyichao xiao_yi_chao@163.com
Date: 2023-02-28 18:58:21
LastEditors: xiaoyichao xiao_yi_chao@163.com
LastEditTime: 2023-02-28 19:06:14
FilePath: /bert_transformer/bert/also_cool.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoModel, AutoTokenizer, AutoConfig
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
config = AutoConfig.from_pretrained('bert-base-uncased', num_labels=2)
model = AutoModel.from_pretrained('bert-base-uncased', config=config)

# define training and testing data
texts = ["This is a positive sentence.", "This is a negative sentence."]
labels = [1, 0]

# split the data into training and testing sets
train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# tokenize the texts
train_encodings = tokenizer(train_texts, truncation=True, padding=True)
test_encodings = tokenizer(test_texts, truncation=True, padding=True)

# convert the labels to tensors
train_labels = torch.tensor(train_labels)
test_labels = torch.tensor(test_labels)

# define the batch size and create data loaders
batch_size = 2
train_dataset = torch.utils.data.TensorDataset(torch.tensor(train_encodings['input_ids']),
                                               torch.tensor(train_encodings['attention_mask']),
                                               train_labels)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

test_dataset = torch.utils.data.TensorDataset(torch.tensor(test_encodings['input_ids']),
                                              torch.tensor(test_encodings['attention_mask']),
                                              test_labels)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size)

# define the model
class BERTClassifier(nn.Module):
    def __init__(self, bert):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state[:, 0]
        logits = self.classifier(last_hidden_state)
        return logits

# define hyperparameters
epochs = 2
lr = 1e-5

# define the optimizer and loss function
optimizer = optim.Adam(model.parameters(), lr=lr)
criterion = nn.CrossEntropyLoss()

# define the training loop
def train(model, loader, optimizer, criterion):
    model.train()
    epoch_loss = 0
    epoch_acc = 0
    for batch in loader:
        input_ids, attention_mask, labels = batch
        optimizer.zero_grad()
        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = logits.last_hidden_state
        loss = criterion(logits.view(-1, config.num_labels), labels)
        acc = accuracy_score(labels.tolist(), logits.argmax(dim=1).tolist())
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
        epoch_acc += acc
    return epoch_loss / len(loader), epoch_acc / len(loader)

# define the evaluation loop
def evaluate(model, loader, criterion):
    model.eval()
    epoch_loss = 0
    epoch_acc = 0
    with torch.no_grad():
        for batch in loader:
            input_ids, attention_mask, labels = batch
            logits = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(logits.view(-1, config.num_labels), labels)
            acc = accuracy_score(labels.tolist(), logits.argmax(dim=1).tolist())
            epoch_loss += loss.item()
            epoch_acc += acc


for epoch in range(epochs):
    train_loss, train_acc = train(model,train_loader,optimizer, criterion)
    test_loss, test_acc = evaluate(model, test_dataset, criterion)
    
    print(f"Epoch {epoch+1}")
    print(f"\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc*100:.2f}%")
    print(f"\tTest Loss: {test_loss:.3f} | Test Acc: {test_acc*100:.2f}%")
