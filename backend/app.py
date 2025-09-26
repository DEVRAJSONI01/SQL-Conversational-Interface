from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
import json
from datetime import datetime
import openai
from typing import Dict, List, Any
import re
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'business_data.db')

class SQLAgent:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.schema_info = self._analyze_schema()
    
    def _analyze_schema(self) -> Dict[str, Any]:
        """Analyze database schema to understand structure"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema = {}
            for table in tables:
                # Get column information
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                sample_data = cursor.fetchall()
                
                schema[table] = {
                    'columns': [{'name': col[1], 'type': col[2], 'nullable': not col[3]} for col in columns],
                    'sample_data': sample_data[:3] if sample_data else []
                }
            
            conn.close()
            return schema
        except Exception as e:
            print(f"Error analyzing schema: {e}")
            return {}
    
    def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        schema_context = self._format_schema_for_prompt()
        
        prompt = f"""
        You are an expert SQL analyst. Given the following database schema and a business question, 
        generate an appropriate SQL query.
        
        Database Schema:
        {schema_context}
        
        Business Question: {question}
        
        Important guidelines:
        1. Handle cases where column names might be unclear or abbreviated
        2. Use appropriate JOINs when data spans multiple tables
        3. Apply proper filtering and aggregation
        4. Consider data quality issues (nulls, duplicates, inconsistent formats)
        5. Return only the SQL query, no explanations
        
        SQL Query:
        """
        
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0.1,
                stop=["\\n\\n"]
            )
            
            sql_query = response.choices[0].text.strip()
            return sql_query
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return None
    
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            
            return {
                'success': True,
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'columns': [],
                'row_count': 0
            }
    
    def generate_insights(self, question: str, query_results: Dict[str, Any]) -> str:
        """Generate natural language insights from query results"""
        if not query_results['success']:
            return "I encountered an error while analyzing the data. Please try rephrasing your question."
        
        data_summary = self._summarize_data(query_results['data'])
        
        prompt = f"""
        Based on the following business question and data analysis results, provide a comprehensive 
        natural language answer with key insights.
        
        Question: {question}
        
        Data Summary:
        {data_summary}
        
        Provide a clear, business-focused answer that:
        1. Directly answers the question
        2. Highlights key findings and trends
        3. Provides actionable insights
        4. Mentions any data quality concerns if relevant
        
        Answer:
        """
        
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Analysis completed, but I couldn't generate detailed insights. Raw results: {len(query_results['data'])} records found."
    
    def _format_schema_for_prompt(self) -> str:
        """Format schema information for AI prompt"""
        schema_text = ""
        for table, info in self.schema_info.items():
            schema_text += f"\\nTable: {table}\\n"
            for col in info['columns']:
                schema_text += f"  - {col['name']} ({col['type']})\\n"
            if info['sample_data']:
                schema_text += f"  Sample data: {info['sample_data'][0]}\\n"
        return schema_text
    
    def _summarize_data(self, data: List[Dict]) -> str:
        """Create a summary of query results for AI analysis"""
        if not data:
            return "No data returned"
        
        summary = f"Dataset contains {len(data)} records\\n"
        
        # Get column info
        if data:
            columns = list(data[0].keys())
            summary += f"Columns: {', '.join(columns)}\\n"
            
            # Basic statistics for numeric columns
            df = pd.DataFrame(data)
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary += "\\nNumeric summaries:\\n"
                for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    summary += f"{col}: min={df[col].min()}, max={df[col].max()}, avg={df[col].mean():.2f}\\n"
        
        return summary

# Initialize agent
sql_agent = SQLAgent()

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Generate SQL query
        sql_query = sql_agent.generate_sql_query(question)
        if not sql_query:
            return jsonify({'error': 'Could not generate SQL query'}), 500
        
        # Execute query
        results = sql_agent.execute_query(sql_query)
        
        # Generate insights
        insights = sql_agent.generate_insights(question, results)
        
        return jsonify({
            'question': question,
            'sql_query': sql_query,
            'results': results,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/schema', methods=['GET'])
def get_schema():
    return jsonify(sql_agent.schema_info)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)