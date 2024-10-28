# train.py

import numpy as np
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

# Constants
MODEL_NAME = 'distilbert-base-uncased'
OUTPUT_DIR = './model_output'
EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 5e-5

# Load dataset (example: IMDb sentiment analysis dataset)
dataset = load_dataset('imdb')

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Preprocess data
def preprocess_function(examples):
    return tokenizer(examples['text'], truncation=True)

tokenized_datasets = dataset.map(preprocess_function, batched=True)

# Load model
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    evaluation_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
)

# Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
)

# Train the model
trainer.train()

# Save the model
trainer.save_model(OUTPUT_DIR)

print("Model trained and saved!")
