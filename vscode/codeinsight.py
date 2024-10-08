import os
import argparse
import ast
import re
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_code_structure(code, language):
    if language == 'python':
        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            return {"functions": functions, "classes": classes}
        except SyntaxError:
            return {"error": "Unable to parse Python code. Syntax error detected."}
    elif language == 'javascript':
        functions = re.findall(r'function\s+(\w+)', code)
        classes = re.findall(r'class\s+(\w+)', code)
        return {"functions": functions, "classes": classes}
    else:
        return {"error": "Structural analysis not supported for this language."}

def calculate_complexity(code, language):
    if language == 'python':
        tree = ast.parse(code)
        complexity = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef)))
        return {"complexity": complexity}
    elif language == 'javascript':
        complexity = len(re.findall(r'\b(if|for|while|function)\b', code))
        return {"complexity": complexity}
    else:
        return {"error": "Complexity calculation not supported for this language."}

def detect_code_smells(code, language):
    prompt = f"Analyze the following {language} code for potential code smells and suggest refactoring:\n\n{code}\n\nAnalysis:"
    return {"smells": generate_response(prompt)}

def suggest_performance_improvements(code, language):
    prompt = f"Suggest performance improvements for the following {language} code:\n\n{code}\n\nImprovements:"
    return {"improvements": generate_response(prompt)}

def generate_documentation(code, language):
    prompt = f"Generate comprehensive documentation for the following {language} code:\n\n{code}\n\nDocumentation:"
    return {"documentation": generate_response(prompt)}

def generate_response(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert software engineer specializing in code analysis and improvement."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="CodeInsight: Advanced Code Analysis Tool")
    parser.add_argument("file", help="Path to the file containing the code")
    parser.add_argument("--language", choices=['python', 'javascript'], required=True, help="Programming language of the code")
    parser.add_argument("--structure", action="store_true", help="Analyze code structure")
    parser.add_argument("--complexity", action="store_true", help="Calculate code complexity")
    parser.add_argument("--smells", action="store_true", help="Detect code smells")
    parser.add_argument("--performance", action="store_true", help="Suggest performance improvements")
    parser.add_argument("--document", action="store_true", help="Generate documentation")
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"The file {args.file} was not found."}))
        return
    except Exception as e:
        print(json.dumps({"error": f"An error occurred while opening the file: {str(e)}"}))
        return

    results = {}

    if args.structure:
        results["structure"] = analyze_code_structure(code, args.language)

    if args.complexity:
        results["complexity"] = calculate_complexity(code, args.language)

    if args.smells:
        results["smells"] = detect_code_smells(code, args.language)

    if args.performance:
        results["performance"] = suggest_performance_improvements(code, args.language)

    if args.document:
        results["documentation"] = generate_documentation(code, args.language)

    print(json.dumps(results))

if __name__ == "__main__":
    main()