import math
import random
import numpy as np
from core.neural_network import NeuralNetwork

def split_dataset(dataset, split_ratio=0.8):
    # Create a copy so we don't mutate the original list outside
    data_copy = list(dataset)
    random.shuffle(data_copy)
    split_idx = int(len(data_copy) * split_ratio)
    return data_copy[:split_idx], data_copy[split_idx:]

def evaluate(network, dataset):
    if not dataset:
        return 0.0, 0.0
    num_classes = network.layer_sizes[-1]
    total_loss = 0.0
    correct = 0
    
    for matrix, label in dataset:
        input_vector = (matrix.flatten() / 255.0).astype(np.float32)
                
        output = network.forward(input_vector)
        epsilon = 1e-15
        loss = -math.log(max(output[label], epsilon))
        total_loss += loss
        
        pred = np.argmax(output)
        if pred == label:
            correct += 1
            
    avg_loss = total_loss / len(dataset)
    accuracy = (correct / len(dataset)) * 100
    return avg_loss, accuracy

def train(network, dataset, epochs=100, learning_rate=0.01):
    """
    Trains the neural network manually using SGD.
    Flattens images and normalizes to 0-1.
    Splits data 80/20 train/validation.
    """
    num_classes = network.layer_sizes[-1]
    
    train_data, val_data = split_dataset(dataset, 0.8)
    print(f"Dataset split: {len(train_data)} train, {len(val_data)} validation")
    
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        # Training phase
        total_train_loss = 0.0
        random.shuffle(train_data)
        
        for matrix, label in train_data:
            # Flatten image
            input_vector = (matrix.flatten() / 255.0).astype(np.float32)
                    
            # Create one-hot target vector
            target = [0.0] * num_classes
            target[label] = 1.0
            
            # Forward pass
            output = network.forward(input_vector)
            
            # Compute loss
            epsilon = 1e-15
            loss = -math.log(max(output[label], epsilon))
            total_train_loss += loss
            
            # Backward pass
            network.backward(target, learning_rate)
            
        avg_train_loss = total_train_loss / max(len(train_data), 1)
        
        # Validation phase
        val_loss, val_accuracy = evaluate(network, val_data)
        
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.4f} - Val Loss: {val_loss:.4f} - Val Acc: {val_accuracy:.2f}%")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Save the best weights
            network.save_weights('data/best_model_weights.json')
            
    return network
