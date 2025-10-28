# 🌍 AI Travel Planner Agentic Application

Welcome to the **AI Travel Planner Agentic Application**! This project leverages advanced AI (LangChain, LLMs) to help users plan trips interactively via a chat interface. The app generates detailed travel itineraries and visualizes the planning process.

---

## 🚀 Features
- **Conversational Trip Planning:** Chat with an AI agent to plan your trip.
- **Custom Itineraries:** Get personalized travel plans based on your preferences.
- **Graph Visualization:** Generates a visual representation of the planning process.
- **Modern UI:** Built with Streamlit for a responsive, user-friendly experience.
- **API Backend:** FastAPI powers the backend for robust, scalable performance.

---

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** FastAPI
- **AI/LLM:** LangChain,Langgraph OpenAI, Groq, Google Places, Tavily
- **Other:** Pydantic, Uvicorn, Requests, Python-dotenv

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AItravelplanner.git
cd AItravelplanner
```

### 2. Install Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory and add any required API keys or environment variables (see `.env.example` if provided).

---

## 🏃‍♂️ Running the Application

### 1. Start the Backend (FastAPI)
```bash
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend (Streamlit)
```bash
streamlit run streamlitapp.py
```

The Streamlit app will be available at [http://localhost:8501](http://localhost:8501).

---

## 🐳 Docker
You can run the entire application using Docker:

```bash
docker build -t aitravelplanner .
docker run -p 8501:8501 aitravelplanner
```

---

## 🌐 Live Demo
The backend is deployed on Render:
- **Render API Link:** ([https://aitravel-planner-gy4l.onrender.com/](https://aitravel-planner-frontend.onrender.com/))

To deploy your own version, connect your repository to [Render](https://render.com/) and follow their Python/Streamlit deployment guides.

---

## 📝 Usage
- Open the Streamlit app in your browser.
- Enter your travel preferences in the chat (e.g., "Plan a trip to Goa for 5 days").
- The AI will generate a detailed itinerary and display it in the chat.
- A graph visualization of the planning process is saved as `my_graph.png`.

---

## 📁 Project Structure
```
.
├── streamlitapp.py        # Streamlit frontend
├── main.py                # FastAPI backend
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker setup
├── setup.py               # Project metadata
├── my_graph.png           # Generated graph
├── ... (other folders: agent/, utils/, tools/, etc.)
```

---

## 🙏 Credits
- **Author:** krish shah ([shahkrish551@gmail.com](mailto:shahkrish551@gmail.com))
- Built with [LangChain](https://langchain.com/), [Streamlit](https://streamlit.io/), [FastAPI](https://fastapi.tiangolo.com/), and more.

---

## 📄 License
This project is for educational and demonstration purposes. Please verify all travel information before making plans.
