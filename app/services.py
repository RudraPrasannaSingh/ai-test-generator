import asyncio
import time
import ast
import re
import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class CodeAnalyzer:
    def analyze_python_code(self, code: str) -> Dict:
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node))
                    })
            
            return {'functions': functions, 'complexity': len(functions)}
        except SyntaxError as e:
            return {'error': f'Invalid Python syntax: {str(e)}', 'functions': []}

class TestGenerator:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Please add your GEMINI_API_KEY to .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_tests(self, code: str, language: str, framework: str, 
                           analysis: Dict, include_edge_cases: bool) -> str:
        prompt = f"""
Generate {framework} test cases for this {language} code:


Functions found: {[f['name'] for f in analysis.get('functions', [])]}

Requirements:
1. Write complete, runnable {framework} test cases
2. Include imports and proper setup
3. Test normal cases and {"edge cases (null, empty, invalid inputs)" if include_edge_cases else "basic scenarios"}
4. Use descriptive test names
5. Add meaningful assertions

Return ONLY the test code, no explanations.
"""
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text.strip()
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")

class AITestService:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.generator = TestGenerator()
    
    async def create_tests(self, request) -> Dict:
        start_time = time.time()
        
        if request.language == "python":
            analysis = self.analyzer.analyze_python_code(request.code)
        else:
            analysis = {"functions": [], "complexity": 0}
        
        if 'error' in analysis:
            raise Exception(analysis['error'])
        
        generated_tests = await self.generator.generate_tests(
            request.code, request.language, request.framework, 
            analysis, request.include_edge_cases
        )
        
        test_count = len(re.findall(r'def test_|it\(|Test.*\(', generated_tests))
        confidence = min(0.9, 0.5 + (test_count * 0.1))
        processing_time = int((time.time() - start_time) * 1000)
        
        suggestions = []
        if test_count < 3:
            suggestions.append("Consider adding more edge case tests")
        if analysis.get('complexity', 0) > 3:
            suggestions.append("Complex code detected - review test coverage")
        
        return {
            "generated_tests": generated_tests,
            "test_count": test_count,
            "confidence_score": round(confidence, 2),
            "processing_time_ms": processing_time,
            "suggestions": suggestions
        }
