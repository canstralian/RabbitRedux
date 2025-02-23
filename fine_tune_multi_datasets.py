import logging
from datasets import load_dataset, concatenate_datasets
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding, EvalPrediction
from sklearn.metrics import accuracy_score, f1_score

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
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

    # Tokenize datasets with dynamic padding
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding=True, truncation=True)

    tokenized_datasets = {name: dataset.map(tokenize_function, batched=True) for name, dataset in datasets.items()}

    # Combine datasets
    train_datasets = concatenate_datasets([tokenized_datasets[name]['train'] for name in datasets])
    test_datasets = concatenate_datasets([tokenized_datasets[name]['test'] for name in datasets])

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained('WhiteRabbitNeo/Code-Classification-Model', num_labels=2)

    # Define training arguments with mixed precision training
    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy='epoch',
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        fp16=True,  # Enable mixed precision training
        logging_dir='./logs',
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model='f1' # Changed to f1
    )

    # Initialize DataCollator for dynamic padding - Corrected
    data_collator = DataCollatorWithPadding(tokenizer)

    # Define compute metrics function
    def compute_metrics(eval_pred: EvalPrediction):
        predictions = eval_pred.predictions.argmax(axis=-1)
        labels = eval_pred.label_ids
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')  # Example: weighted F1
        return {"accuracy": accuracy, "f1": f1}


    # Initialize Trainer - Added compute_metrics
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_datasets,
        eval_dataset=test_datasets,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # Train the model
    logger.info("Starting training...")
    trainer.train()

    # Save the trained model and tokenizer
    logger.info("Saving model and tokenizer...")
    model.save_pretrained('./model')
    tokenizer.save_pretrained('./model')

    # Evaluate the model
    logger.info("Evaluating the model...")
    eval_results = trainer.evaluate()
    logger.info(f"Evaluation results: {eval_results}")

except Exception as e:
    logger.error(f"An error occurred: {e}")

