# AIPipe

**AIPipe** is a text processing API built with **FastAPI** and **Celery**, designed for text operations such as:

- ✏️ `rewrite` – rephrasing input text  
- 🔍 `summarize` – generating concise summaries  
- 🌍 `translate` – translating text into a specified language  
- ➕ `expand` – enriching text with additional context and detail  

The service supports both **single-task execution** and **multi-step pipelines**.

---

## 🧱 Technologies

- **FastAPI** – web API framework  
- **Celery** – asynchronous task queue  
- **RabbitMQ** – message broker  
- **Redis** – task result backend & pipeline storage  
- **Docker** – containerized deployment  

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Wojtek321/AIPipe.git
cd AIPipe/docker
```

### 2. Create .env file
Create a .env file in the docker folder to provide your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your-openai-key-here" > .env
```

### 3. Run the service
Requires docker and docker-compose.
```bash
docker-compose up --build
```

## 📦 API Endpoints

### 🔧 Single Tasks – `/tasks`

#### `POST /tasks/summarize`  
**Description**: Generate a summary from input text  
**Body**:  
```json
{
  "text": "Your long text here..."
}
```

#### `POST /tasks/rewrite`  
**Description**: Rephrase the given text  
**Body**:  
```json
{
  "text": "Input text"
}
```

#### `POST /tasks/translate`  
**Description**: Translate input text into a target language  
**Body**:  
```json
{
  "text": "Hello",
  "target_language": "Polish"
}
```

#### `POST /tasks/expand`  
**Description**: Expand and enrich input text with more details  
**Body**:  
```json
{
  "text": "Short paragraph..."
}
```

#### `GET /tasks/{task_id}`  
**Description**: Get status or result of a submitted task

---

### 🔗 Pipelines – `/pipelines`

#### `POST /pipelines`  
**Description**: Start a sequence of text-processing steps  
**Body**:  
```json
{
  "input_data": "Your input text",
  "steps": [
    { "name": "summarize" },
    { "name": "translate", "params": { "target_language": "English" } }
  ]
}
```

#### `GET /pipelines/{pipeline_id}`  
**Description**: Retrieve the status and results of the entire pipeline
