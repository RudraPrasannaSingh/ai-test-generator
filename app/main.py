from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.models import TestRequest, TestResponse
from app.services import AITestService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Test Generator",
    description="Generate intelligent test cases with AI",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
test_service = AITestService()

# Simple HTML interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Test Generator</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        textarea, select { width: 100%; padding: 12px; border: 2px solid #ecf0f1; border-radius: 4px; font-family: 'Courier New', monospace; }
        textarea { height: 200px; resize: vertical; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-right: 10px; }
        button:hover { background: #2980b9; }
        .results { margin-top: 30px; }
        .code-output { background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 4px; font-family: 'Courier New', monospace; white-space: pre-wrap; max-height: 500px; overflow-y: auto; }
        .metrics { background: #e8f5e8; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .loading { color: #3498db; font-style: italic; }
        .error { color: #e74c3c; background: #fdf2f2; padding: 15px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Test Generator</h1>
        <p>Paste your code below and get intelligent test cases generated instantly!</p>
        
        <form id="testForm">
            <div class="form-group">
                <label for="code">Your Code:</label>
                <textarea id="code" placeholder="def calculate_tax(income, rate):
    if income < 0 or rate < 0:
        raise ValueError('Income and rate must be positive')
    return income * rate" required></textarea>
            </div>
            
            <div class="form-group">
                <label for="language">Language:</label>
                <select id="language">
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="csharp">C#</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="framework">Testing Framework:</label>
                <select id="framework">
                    <option value="pytest">pytest</option>
                    <option value="unittest">unittest</option>
                    <option value="jest">Jest</option>
                    <option value="xunit">xUnit</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="edgeCases" checked> Include Edge Cases
                </label>
            </div>
            
            <button type="submit">🧪 Generate Tests</button>
            <button type="button" onclick="clearResults()">🗑️ Clear</button>
        </form>
        
        <div id="results" class="results" style="display: none;">
            <div id="metrics" class="metrics"></div>
            <div id="output" class="code-output"></div>
        </div>
    </div>

    <script>
        document.getElementById('testForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const resultsDiv = document.getElementById('results');
            const metricsDiv = document.getElementById('metrics');
            const outputDiv = document.getElementById('output');
            
            // Show loading
            resultsDiv.style.display = 'block';
            metricsDiv.innerHTML = '<div class="loading">🤖 AI is analyzing your code and generating tests...</div>';
            outputDiv.textContent = '';
            
            const formData = {
                code: document.getElementById('code').value,
                language: document.getElementById('language').value,
                framework: document.getElementById('framework').value,
                include_edge_cases: document.getElementById('edgeCases').checked
            };
            
            try {
                const response = await fetch('/generate-tests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Generation failed');
                
                const result = await response.json();
                
                metricsDiv.innerHTML = `
                    <strong>✅ Tests Generated Successfully!</strong><br>
                    📊 Test Count: ${result.test_count} | 
                    🎯 Confidence: ${(result.confidence_score * 100).toFixed(0)}% | 
                    ⚡ Generated in: ${result.processing_time_ms}ms
                    ${result.suggestions.length > 0 ? '<br>💡 Suggestions: ' + result.suggestions.join(', ') : ''}
                `;
                
                outputDiv.textContent = result.generated_tests;
                
            } catch (error) {
                metricsDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                outputDiv.textContent = '';
            }
        });
        
        function clearResults() {
            document.getElementById('results').style.display = 'none';
            document.getElementById('code').value = '';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.get("/health")
async def health():
    return {"status": "🚀 AI Test Generator is running!", "version": "1.0.0"}

@app.post("/generate-tests", response_model=TestResponse)
async def generate_tests(request: TestRequest):
    try:
        logger.info(f"Generating {request.framework} tests for {request.language} code")
        
        result = await test_service.create_tests(request)
        
        logger.info(f"✅ Generated {result['test_count']} tests in {result['processing_time_ms']}ms")
        
        return TestResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this at the end of app/main.py
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use Render's PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    # CRITICAL: Must bind to 0.0.0.0 for Render
    uvicorn.run(app, host="0.0.0.0", port=port)

