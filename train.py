import numpy as np
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

# Constants
MODEL_NAME = 'distilbert-base-uncased'
OUTPUT_DIR = './model_output'
EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 5e-5

def load_and_preprocess_data(dataset_name: str, tokenizer: AutoTokenizer, batch_size: int) -> dict:
    """
    Loads and preprocesses the dataset for training and evaluation.

    Args:
        dataset_name (str): The name of the dataset to load.
        tokenizer (AutoTokenizer): The tokenizer to use for preprocessing.
        batch_size (int): The batch size for tokenization.

    Returns:
        dict: A dictionary containing the tokenized training and evaluation datasets.
    """
    # Validate inputs
    if not isinstance(dataset_name, str):
        raise ValueError(f"Expected 'dataset_name' to be a string, got {type(dataset_name)}.")
    if not isinstance(tokenizer, AutoTokenizer):
        raise ValueError(f"Expected 'tokenizer' to be an instance of AutoTokenizer, got {type(tokenizer)}.")
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError(f"Expected 'batch_size' to be a positive integer, got {batch_size}.")

    # Load dataset
    dataset = load_dataset(dataset_name)

    # Preprocess data
    def preprocess_function(examples):
        return tokenizer(examples['text'], truncation=True, padding=True, max_length=512)

    tokenized_datasets = dataset.map(preprocess_function, batched=True, batch_size=batch_size)
    return tokenized_datasets

def initialize_model(model_name: str, num_labels: int) -> AutoModelForSequenceClassification:
    """
    Initializes the model for sequence classification.

    Args:
        model_name (str): The name of the pre-trained model.
        num_labels (int): The number of labels for classification.

    Returns:
        AutoModelForSequenceClassification: The initialized model.
    """
    # Validate inputs
    if not isinstance(model_name, str):
        raise ValueError(f"Expected 'model_name' to be a string, got {type(model_name)}.")
    if not isinstance(num_labels, int) or num_labels <= 0:
        raise ValueError(f"Expected 'num_labels' to be a positive integer, got {num_labels}.")

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    return model

def train_model(model, train_dataset, eval_dataset, output_dir: str, epochs: int, batch_size: int, learning_rate: float):
    """
    Trains the model using the provided datasets and parameters.

    Args:
        model (AutoModelForSequenceClassification): The model to train.
        train_dataset (Dataset): The training dataset.
        eval_dataset (Dataset): The evaluation dataset.
        output_dir (str): The directory to save the trained model.
        epochs (int): The number of training epochs.
        batch_size (int): The batch size for training.
        learning_rate (float): The learning rate for training.

    Returns:
        Trainer: The Trainer instance used for training.
    """
    # Validate inputs
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

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
    )

    # Create Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset['train'],
        eval_dataset=eval_dataset['test'],
    )

    # Train the model
    trainer.train()

    # Save the model
    trainer.save_model(output_dir)
    return trainer

def main():
    """
    Main function to load data, initialize the model, and train it.
    """
    # Load and preprocess data
    tokenized_datasets = load_and_preprocess_data('imdb', AutoTokenizer.from_pretrained(MODEL_NAME), BATCH_SIZE)

    # Initialize model
    model = initialize_model(MODEL_NAME, num_labels=2)

    # Train the model
    trainer = train_model(
        model=model,
        train_dataset=tokenized_datasets,
        eval_dataset=tokenized_datasets,
        output_dir=OUTPUT_DIR,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE
    )

    print("Model trained and saved!")

if __name__ == '__main__':
    main()