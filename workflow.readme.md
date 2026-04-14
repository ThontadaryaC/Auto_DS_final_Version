# AutoDS AI: Project Workflow & Documentation

**AutoDS AI** is an "AI-powered Data Scientist" platform designed to automate the end-to-end data science workflow, from data ingestion and cleaning to advanced machine learning and strategic planning.

---

## 🚀 Project Workflow

### 1. Data Ingestion & Preprocessing
*   **Upload**: Supports CSV, Excel (.xlsx, .xls), and XML formats.
*   **Parsing**: Files are parsed into Pandas DataFrames for processing.
*   **Auto-Cleaning**: The system automatically:
    *   Drops completely empty rows and columns.
    *   Removes duplicate records.
    *   **Intelligent Imputation**: Fills missing numeric values with the mean and categorical values with the mode (or "Unknown").
    *   **Type Inference**: Automatically detects and converts data types (e.g., strings to numbers where applicable).
*   **Storage**: 
    *   **Local**: Files are saved in the `backend/uploads` directory.
    *   **Registry**: Upload history is tracked in a local SQLite database (`data.db`).
    *   **Cloud Persistence**: Data is synced to **MongoDB Atlas** for long-term storage.

### 2. Exploratory Data Analysis (EDA) & Visualization
*   **Immediate AI Observation**: Upon upload, an LLM analyzes the schema and a sample of the data to provide a human-readable summary of what the dataset contains.
*   **Dynamic Dashboard**: Generates industrial-grade charts using Plotly, including distributions, correlations, and trend lines.
*   **AI-Generated Reports**: Users can generate deep-dive textual reports where the AI interprets specific dashboard views to provide context and business meaning.

### 3. Strategic AI Orchestration ("Think-then-Execute")
The core innovation of the platform is the **Strategic AI Orchestration** workflow:
1.  **Thinking Phase**: The AI agent (Master Data Scientist) analyzes the dataset's domain and columns.
2.  **Strategic Plan**: It proposes a 3-part plan:
    *   **Clustering Strategy**: Recommended features and the optimal number of groups (K).
    *   **Anomaly Strategy**: Suggested contamination rates for detecting outliers.
    *   **AutoML Strategy**: Identification of the most important "Target" column and the type of task (Regression or Classification).
3.  **Execution**: The user reviews the plan and triggers the machine learning models.

### 4. Advanced Machine Learning
*   **Predictive Trends**: Forecasts future values based on historical data patterns.
*   **Clustering**: Groups similar data points to reveal hidden segments in the data.
*   **Anomaly Detection**: Uses Isolation Forests to flag unusual or suspicious records.
*   **AutoML Pro**: Automatically builds, trains, and evaluates machine learning models, reporting accuracy and performance metrics.

---

## 🛠️ Technology Stack
*   **Frontend**: React (Vite), Tailwind CSS (for styling), Axios (API calls).
*   **Backend**: FastAPI (Python), Pandas, Scikit-Learn (ML), Plotly.
*   **AI/LLM**: LangChain, OpenRouter (Gemini/GPT models).
*   **Database**: SQLite (local registry), MongoDB Atlas (cloud persistence).

---

## 💡 How It Is Helpful

1.  **Simplifies Complex Data Science**: Makes data science accessible to users without coding or statistical expertise.
2.  **Saves Time**: Automates the most time-consuming parts of data work (cleaning and model selection).
3.  **Strategic Guidance**: Acts as a "Digital Consultant" by suggesting *what* to analyze next based on the data's unique characteristics.
4.  **Actionable Results**: Moves beyond simple charts to provide predictions and strategic recommendations that drive business decisions.
5.  **Professional Standards**: Ensures that data cleaning and machine learning follow industry best practices automatically.
