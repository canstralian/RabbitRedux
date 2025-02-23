import numpy as np
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

# Constants
MODEL_NAME = 'distilbert-base-uncased'
OUTPUT_DIR = './model_output'
EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 5e-5
MAX_LENGTH = 512

def load_and_preprocess_data(dataset_name: str, tokenizer: AutoTokenizer, batch_size: int) -> dict:
    """Loads and preprocesses the dataset."""
    validate_inputs(dataset_name, tokenizer, batch_size)

    dataset = load_dataset(dataset_name)
    tokenized_datasets = dataset.map(
        lambda examples: tokenizer(examples['text'], truncation=True, padding=True, max_length=MAX_LENGTH),
        batched=True,
        batch_size=batch_size
    )
    return tokenized_datasets

def validate_inputs(dataset_name: str, tokenizer: AutoTokenizer, batch_size: int):
    """Validates the inputs for data loading and preprocessing."""
    if not isinstance(dataset_name, str):
        raise ValueError(f"Expected 'dataset_name' to be a string, got {type(dataset_name)}.")
    if not isinstance(tokenizer, AutoTokenizer):
        raise ValueError(f"Expected 'tokenizer' to be an instance of AutoTokenizer, got {type(tokenizer)}.")
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError(f"Expected 'batch_size' to be a positive integer, got {batch_size}.")

def initialize_model(model_name: str, num_labels: int) -> AutoModelForSequenceClassification:
    """Initializes the model."""
    validate_model_inputs(model_name, num_labels)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    return model

def validate_model_inputs(model_name: str, num_labels: int):
    """Validates the inputs for model initialization."""
    if not isinstance(model_name, str):
        raise ValueError(f"Expected 'model_name' to be a string, got {type(model_name)}.")
    if not isinstance(num_labels, int) or num_labels <= 0:
        raise ValueError(f"Expected 'num_labels' to be a positive integer, got {num_labels}.")

def train_model(model, train_dataset, eval_dataset, output_dir: str, epochs: int, batch_size: int, learning_rate: float):
    """Trains the model."""
    validate_training_inputs(model, train_dataset, eval_dataset, output_dir, epochs, batch_size, learning_rate)

    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        fp16=True  # Enable mixed precision training for faster training
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset['train'],
        eval_dataset=eval_dataset['test'],
    )

    trainer.train()
    trainer.save_model(output_dir)
    return trainer

def validate_training_inputs(model, train_dataset, eval_dataset, output_dir, epochs, batch_size, learning_rate):
    """Validates training inputs."""
    if not isinstance(model, AutoModelForSequenceClassification):
        raise ValueError(f"Expected 'model' to be an instance of AutoModelForSequenceClassification, got {type(model)}.")
    if not isinstance(train_dataset, dict) or 'train' not in train_dataset:
        raise ValueError(f"Expected 'train_dataset' to be a dictionary with a 'train' key, got {type(train_dataset)}.")
    if not isinstance(eval_dataset, dict) or 'test' not in eval_dataset:
        raise ValueError(f"Expected 'eval_dataset' to be a dictionary with a 'test' key, got {type(eval_dataset)}.")
    if not isinstance(output_dir, str):
        raise ValueError(f"Expected 'output_dir' to be a string, got {type(output_dir)}.")
    if not isinstance(epochs, int) or epochs <= 0:
        raise ValueError(f"Expected 'epochs' to be a positive integer, got {epochs}.")
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError(f"Expected 'batch_size' to be a positive integer, got {batch_size}.")
    if not isinstance(learning_rate, (float, int)) or learning_rate <= 0:
        raise ValueError(f"Expected 'learning_rate' to be a positive number, got {learning_rate}.")

def main():
    """Main function."""
    tokenized_datasets = load_and_preprocess_data(
        'WhiteRabbitNeo/Code-Functions-Level-Cyber',
        AutoTokenizer.from_pretrained(MODEL_NAME),
        BATCH_SIZE
    )

    model = initialize_model(MODEL_NAME, num_labels=2)

    train_model(
        model=model,
        train_dataset=tokenized_datasets,
        eval_dataset=tokenized_datasets,
        output_dir=OUTPUT_DIR,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE
    )

if __name__ == "__main__":
    main()


