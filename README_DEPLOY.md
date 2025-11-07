# AI Data Analytics Copilot — Deployment & Run Guide

## Local setup
1. Create virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key as an environment variable
   ```bash
   export OPENAI_API_KEY="sk-..."
   # Windows PowerShell: $env:OPENAI_API_KEY = "sk-..."
   ```
3. Run the Streamlit app
   ```bash
   streamlit run app.py
   ```
4. Open the app at http://localhost:8501

## Streamlit Cloud deployment
1. Create a new GitHub repository and push all files.
2. Go to https://streamlit.io/cloud and create a new app, connecting your GitHub repo.
3. In the Streamlit Cloud app settings, add an environment variable named `OPENAI_API_KEY` and paste your key.
4. Deploy the app. Streamlit will install from `requirements.txt` automatically.

## Security & Production notes
- This template uses a lightweight AST check to reduce risk of dangerous code execution. **It is not production-grade**. For production, use a hardened remote sandbox or containerized execution for running untrusted code.
- Monitor API usage and set cost/timeout limits on your OpenAI usage.
