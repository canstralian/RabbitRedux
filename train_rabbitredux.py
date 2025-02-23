import logging
import torch
import random
from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from torch.nn.utils import prune
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ----- Setup Logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----- Utility: Data Augmentation for Code Snippets -----
def augment_code(example):
    """Applies code-specific data augmentation to the input example."""
    if random.random() < 0.5:  # 50% chance to augment
        text = example['text']
        # Variable renaming (simple example; replace with more robust logic)
        if random.random() < 0.5:
            text = text.replace('variable_name', 'renamed_variable')
        # Code formatting: convert tabs to spaces
        if random.random() < 0.5:
            text = text.replace('\t', '  ')
        # Comment addition or removal
        if random.random() < 0.5:
            if '# ' in text:
                text = text.replace('# ', '')
            else:
                text += '\n# Added comment'
        example['text'] = text
    return example

# ----- Load Tokenizer and Model -----
model_id = 'canstralian/RabbitRedux'
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=2)

# ----- Load and Prepare Datasets -----
# Load multiple datasets and combine them
datasets = {
    'WRN-Chapter-1': load_dataset('WhiteRabbitNeo/WRN-Chapter-1'),
    'WRN-Chapter-2': load_dataset('WhiteRabbitNeo/WRN-Chapter-2'),
    'Code-Functions-Level-General': load_dataset('WhiteRabbitNeo/Code-Functions-Level-General'),
    'Code-Functions-Level-Cyber': load_dataset('WhiteRabbitNeo/Code-Functions-Level-Cyber'),
    'agent-challenge': load_dataset('replit/agent-challenge')
}

# Apply data augmentation
augmented_datasets = {
    name: dataset.map(augment_code, batched=False)
    for name, dataset in datasets.items()
}

# Tokenization function
def tokenize_function(examples):
    return tokenizer(examples['text'], truncation=True)

# Tokenize each dataset
tokenized_datasets = {
    name: dataset.map(tokenize_function, batched=True)
    for name, dataset in augmented_datasets.items()
}

# Combine datasets for training and evaluation
train_datasets = concatenate_datasets(
    [tokenized_datasets[name]['train'] for name in datasets]
)
eval_datasets = concatenate_datasets(
    [tokenized_datasets[name]['test'] for name in datasets]
)

# ----- Data Collator for Dynamic Padding -----
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# ----- Training Arguments with Advanced Techniques -----
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    fp16=True,  # Mixed precision training (ensure compatible hardware)
    gradient_accumulation_steps=2,
    logging_dir='./logs',
    logging_steps=50,
    save_steps=500,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model='f1'  # Using F1 for potentially imbalanced datasets
)

# ----- Compute Metrics Function -----
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# ----- Initialize the Trainer -----
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_datasets,
    eval_dataset=eval_datasets,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# ----- Start Training -----
logger.info("Starting training...")
train_result = trainer.train()
trainer.save_model()  # Saves the model and tokenizer

# ----- Evaluate the Model -----
logger.info("Evaluating the model...")
eval_results = trainer.evaluate()
logger.info(f"Evaluation results: {eval_results}")

# ----- Optional: Model Pruning -----
def apply_model_pruning(model, amount=0.2):
    """Apply L1 unstructured pruning to all Linear layers in the model."""
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            prune.l1_unstructured(module, name="weight", amount=amount)
            prune.remove(module, "weight")

logger.info("Applying model pruning...")
apply_model_pruning(model, amount=0.2)
model.save_pretrained('./pruned_model')
tokenizer.save_pretrained('./pruned_model')
logger.info("Pruned model saved to './pruned_model'")