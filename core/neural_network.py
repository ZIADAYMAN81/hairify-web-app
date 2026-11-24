import math
import random
import json
import numpy as np

class NeuralNetwork:
    def __init__(self, layer_sizes):
        """
        Initializes weights and biases randomly for a fully connected network using NumPy.
        layer_sizes: e.g., [input_size, hidden_size, output_size]
        """
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []
        
        # Initialize weights and biases
        for i in range(len(layer_sizes) - 1):
            w = (np.random.rand(layer_sizes[i], layer_sizes[i+1]) - 0.5) * 0.1
            b = np.zeros(layer_sizes[i+1])
            self.weights.append(w)
            self.biases.append(b)
            
        self.activations = []
        self.z_values = []
        
    def _sigmoid(self, x):
        x = np.clip(x, -500, 500)
        return 1.0 / (1.0 + np.exp(-x))
        
    def _sigmoid_derivative(self, z):
        s = self._sigmoid(z)
        return s * (1.0 - s)
        
    def _softmax(self, z):
        z_shifted = z - np.max(z)
        exps = np.exp(z_shifted)
        return exps / np.sum(exps)
        
    def forward(self, input_vector):
        """
        Forward pass using NumPy.
        """
        if not isinstance(input_vector, np.ndarray):
            a = np.array(input_vector, dtype=np.float32)
        else:
            a = input_vector
            
        self.activations = [a]
        self.z_values = []
        
        # Hidden layers
        for i in range(len(self.weights) - 1):
            z = np.dot(a, self.weights[i]) + self.biases[i]
            self.z_values.append(z)
            a = self._sigmoid(z)
            self.activations.append(a)
            
        # Output layer with softmax
        i = len(self.weights) - 1
        z = np.dot(a, self.weights[i]) + self.biases[i]
        self.z_values.append(z)
        a = self._softmax(z)
        self.activations.append(a)
        
        return a
        
    def backward(self, target_vector, learning_rate):
        """
        Backpropagation using NumPy.
        """
        target = np.array(target_vector, dtype=np.float32)
        a_out = np.array(self.activations[-1], dtype=np.float32)
        
        # Compute gradient for output layer
        delta = a_out - target
        deltas = [delta]
        
        # Backpropagate errors
        for i in range(len(self.weights) - 2, -1, -1):
            w_next = self.weights[i + 1]
            delta_next = deltas[0]
            z = self.z_values[i]
            
            error = np.dot(w_next, delta_next)
            delta_curr = error * self._sigmoid_derivative(z)
            deltas.insert(0, delta_curr)
            
        # Update weights and biases
        for i in range(len(self.weights)):
            a_prev = np.array(self.activations[i], dtype=np.float32)
            d = deltas[i]
            
            grad_w = np.outer(a_prev, d)
            self.weights[i] -= learning_rate * grad_w
            self.biases[i] -= learning_rate * d

    def save_weights(self, path):
        """
        Dumps the weights and biases to a JSON file.
        """
        data = {
            "layer_sizes": self.layer_sizes,
            "weights": [w.tolist() for w in self.weights],
            "biases": [b.tolist() for b in self.biases]
        }
        with open(path, 'w') as f:
            json.dump(data, f)
        print(f"Saved network weights to {path}")

    def load_weights(self, path):
        """
        Reads model_weights.json and restores the network state.
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.layer_sizes = data["layer_sizes"]
            self.weights = [np.array(w, dtype=np.float32) for w in data["weights"]]
            self.biases = [np.array(b, dtype=np.float32) for b in data["biases"]]
            print(f"Loaded network weights from {path}")
        except FileNotFoundError:
            print(f"Weights file {path} not found.")

    def predict(self, input_vector, class_names):
        """
        Runs a forward pass and returns a dictionary with the highest confidence class.
        """
        output = self.forward(input_vector)
        max_idx = np.argmax(output)
        max_prob = output[max_idx]
        return {
            "class_index": int(max_idx),
            "class_name": class_names[max_idx] if max_idx < len(class_names) else "unknown",
            "confidence": float(max_prob)
        }
