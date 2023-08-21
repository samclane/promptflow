
<p align="center">
  <img src="promptflow/res/Logo_full_1.png" alt="PromptFlow logo"/>
</p>

---

# 🧩💡 PromptFlow

Want to quickly prototype your Large Language Model (LLM) application without a ton of code? Unleash your creativity with **PromptFlow**, a low-code tool that empowers you to craft executable flowcharts. Seamlessly integrate LLMs, prompts, Python functions, and conditional logic to create intricate workflows. With PromptFlow, you can visualize your ideas and bring them to life, all without getting tangled in code or complex logic.

<p align="center">
  <img src="screenshots/readme/heroscreenshot.png" alt="PromptFlow screenshot"/>
</p>

#### 🎮 Join the conversation on our [Discord Server](https://discord.gg/5MmV3FNCtN)

## 🔗 How it works

The core of PromptFlow is a visual flowchart editor that lets you design nodes and establish Connections between them. Each node can represent a Prompt, a Python function, or an LLM. The connections between nodes embody conditional logic, dictating the flow of your program.

When run your flowchart, PromptFlow executes each node in the sequence defined by the connections, transferring text data between nodes as required. If a node returns a value, that value is forwarded to the next node in the flow as a string. More information on the inner workings of PromptFlow can be found in our [documentation](https://www.promptflow.org/en/latest/).

## 🛠️ Initial Setup 

Before starting, make sure to populate the `.env` file with the appropriate values. The `.env` file should be located in the root directory of the project.

## 🚀 Launching

## Docker Compose

The easiest way to run PromptFlow is with Docker Compose. To do so, run the following command:

```bash
docker compose up --build
```

This will run the DB, Redis, API (Backend), Celery Worker, and Frontend containers. The API will run on port `8069` by default, with the frontend
on port `4200`.

## 📚 Documentation

[![Documentation Status](https://readthedocs.org/projects/promptflow/badge/?version=latest)](https://www.promptflow.org/en/latest/?badge=latest)

Check out our official docs:

#### 🌐 [promptflow.org](https://www.promptflow.org/en/latest/)

### 🏗️ Building from source

To compile the Sphinx documentation, execute:

```bash
cd docs
make html
```

Then, navigate to `docs/build/html/index.html` in your browser.

## 🤝 Contributing

Want to contribute to PromptFlow? Get started by [building a node](https://www.promptflow.org/en/latest/development.html#starting-point-adding-a-node).

Stumbled upon a bug? Don't hesitate to create an issue, open a PR, or let us know on [Discord](https://discord.gg/5MmV3FNCtN).

## Feedback

We're interested in your feedback! If you've used PromptFlow, please fill out [this questionnaire](https://forms.gle/oaB71zRmZmD8Lc8M6).

