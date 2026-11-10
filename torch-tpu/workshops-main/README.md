# Workshops & Labs

A collection of hands-on workshops, labs, and interactive notebooks focusing on PyTorch, TPU acceleration, and LLM fine-tuning.

---

## 📚 Labs & Notebooks

| Lab | Description | Open in Colab |
| :--- | :--- | :---: |
| **01. CNN Training on Torch TPU (v5e)** | Introduction to running PyTorch on Google Cloud TPU v5e: set up Torch-XLA, configure the TPU runtime, and train a Convolutional Neural Network (CNN). | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chrisachard/workshops/blob/main/Training_01_cnn_training_torchtpu_v5e.ipynb) |
| **02. Gemma LoRA Fine-Tuning on TPU (v5e)** | Parameter-efficient fine-tuning (PEFT) using LoRA on Google's Gemma model, accelerated on Cloud TPU v5e hardware. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chrisachard/workshops/blob/main/Training_02_lora_training_gemma_v5e.ipynb) |
| **03. TorchTitan Distributed Training on TPU** | Distributed model training and scaling using PyTorch's native TorchTitan framework on TPU architecture. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chrisachard/workshops/blob/main/Training_03_torchtitan_training_tpu.ipynb) |

---

## 🚀 Getting Started

1. Click any **"Open in Colab"** badge above.
2. The notebooks are configured to automatically select a **TPU v5e** runtime. If "TPU" is not selected automatically:
   - Navigate to **Runtime** > **Change runtime type**.
   - Under **Hardware accelerator**, select **TPU** (and choose **TPU v5e** if prompted).
