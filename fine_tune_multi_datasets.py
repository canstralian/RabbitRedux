from datasets import load_dataset, concatenate_datasets
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('WhiteRabbitNeo/Code-Classification-Model')

# Load datasets
datasets = {
    'WRN-Chapter-1': load_dataset('WhiteRabbitNeo/WRN-Chapter-1'),
    'WRN-Chapter-2': load_dataset('WhiteRabbitNeo/WRN-Chapter-2'),
    'Code-Functions-Level-General': load_dataset('WhiteRabbitNeo/Code-Functions-Level-General'),
    'Code-Functions-Level-Cyber': load_dataset('WhiteRabbitNeo/Code-Functions-Level-Cyber'),
    'agent-challenge': load_dataset('replit/agent-challenge')
}

# Tokenize datasets
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)

tokenized_datasets = {name: dataset.map(tokenize_function, batched=True) for name, dataset in datasets.items()}

# Combine datasets
train_datasets = concatenate_datasets([tokenized_datasets[name]['train'] for name in datasets])
test_datasets = concatenate_datasets([tokenized_datasets[name]['test'] for name in datasets])

# Load model
model = AutoModelForSequenceClassification.from_pretrained('WhiteRabbitNeo/Code-Classification-Model', num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    fp16=True  # Enable mixed precision training
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_datasets,
    eval_dataset=test_datasets
)

# Train the model
trainer.train()