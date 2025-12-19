#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Documentation Generator
코드 분석 결과를 Markdown 형식의 기술 문서로 생성

Usage:
    python generate_doc_md.py --project "ProjectName" --output "/path/to/output"
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

class MarkdownDocGenerator:
    """Markdown 문서 생성기"""
    
    def __init__(self, project_name: str, output_dir: str = "/mnt/user-data/outputs"):
        self.project_name = project_name
        self.output_dir = output_dir
        self.content: List[str] = []
        
    def add_title(self, title: str, level: int = 1):
        """제목 추가"""
        self.content.append(f"{'#' * level} {title}\n")
        
    def add_paragraph(self, text: str):
        """단락 추가"""
        self.content.append(f"{text}\n")
        
    def add_code_block(self, code: str, language: str = ""):
        """코드 블록 추가"""
        self.content.append(f"```{language}\n{code}\n```\n")
        
    def add_mermaid(self, diagram: str):
        """Mermaid 다이어그램 추가"""
        self.content.append(f"```mermaid\n{diagram}\n```\n")
        
    def add_table(self, headers: List[str], rows: List[List[str]]):
        """테이블 추가"""
        # Header
        self.content.append("| " + " | ".join(headers) + " |")
        # Separator
        self.content.append("| " + " | ".join(["---"] * len(headers)) + " |")
        # Rows
        for row in rows:
            self.content.append("| " + " | ".join(row) + " |")
        self.content.append("")
        
    def add_bullet_list(self, items: List[str], indent: int = 0):
        """글머리 기호 목록 추가"""
        prefix = "  " * indent + "- "
        for item in items:
            self.content.append(f"{prefix}{item}")
        self.content.append("")
        
    def add_numbered_list(self, items: List[str]):
        """번호 목록 추가"""
        for i, item in enumerate(items, 1):
            self.content.append(f"{i}. {item}")
        self.content.append("")
        
    def add_blockquote(self, text: str):
        """인용문 추가"""
        lines = text.split('\n')
        for line in lines:
            self.content.append(f"> {line}")
        self.content.append("")
        
    def add_horizontal_rule(self):
        """구분선 추가"""
        self.content.append("\n---\n")
        
    def add_toc(self, sections: List[str]):
        """목차 추가"""
        self.add_title("Table of Contents", 2)
        for section in sections:
            anchor = section.lower().replace(" ", "-").replace(".", "")
            self.content.append(f"- [{section}](#{anchor})")
        self.content.append("")
        
    def generate_header(self):
        """문서 헤더 생성"""
        self.add_title(f"{self.project_name} Technical Documentation")
        self.add_paragraph(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        self.add_horizontal_rule()
        
    def generate_overview_section(self, overview: Dict):
        """개요 섹션 생성"""
        self.add_title("1. Overview", 2)
        
        if "purpose" in overview:
            self.add_title("Purpose", 3)
            self.add_paragraph(overview["purpose"])
            
        if "features" in overview:
            self.add_title("Key Features", 3)
            self.add_bullet_list(overview["features"])
            
        if "tech_stack" in overview:
            self.add_title("Technology Stack", 3)
            self.add_table(
                ["Category", "Technology"],
                [[k, v] for k, v in overview["tech_stack"].items()]
            )
            
    def generate_architecture_section(self, architecture: Dict):
        """아키텍처 섹션 생성"""
        self.add_title("2. Architecture", 2)
        
        if "description" in architecture:
            self.add_paragraph(architecture["description"])
            
        if "diagram" in architecture:
            self.add_mermaid(architecture["diagram"])
            
        if "components" in architecture:
            self.add_title("Components", 3)
            for comp in architecture["components"]:
                self.add_title(comp["name"], 4)
                self.add_paragraph(comp.get("description", ""))
                if "responsibilities" in comp:
                    self.add_bullet_list(comp["responsibilities"])
                    
    def generate_workflow_section(self, workflow: Dict):
        """워크플로우 섹션 생성"""
        self.add_title("3. Workflow", 2)
        
        if "description" in workflow:
            self.add_paragraph(workflow["description"])
            
        if "diagram" in workflow:
            self.add_mermaid(workflow["diagram"])
            
        if "steps" in workflow:
            self.add_title("Process Steps", 3)
            for i, step in enumerate(workflow["steps"], 1):
                self.add_title(f"Step {i}: {step['name']}", 4)
                self.add_paragraph(step.get("description", ""))
                if "code" in step:
                    self.add_code_block(step["code"], step.get("language", ""))
                    
    def generate_functions_section(self, functions: List[Dict]):
        """주요 함수 섹션 생성"""
        self.add_title("4. Key Functions", 2)
        
        for func in functions:
            self.add_title(f"`{func['name']}`", 3)
            
            if "purpose" in func:
                self.add_paragraph(f"**Purpose**: {func['purpose']}")
                
            if "analogy" in func:
                self.add_paragraph(f"**Analogy**: {func['analogy']}")
                
            if "params" in func:
                self.add_paragraph("**Parameters**:")
                self.add_bullet_list([f"`{p['name']}`: {p['description']}" for p in func["params"]])
                
            if "returns" in func:
                self.add_paragraph(f"**Returns**: {func['returns']}")
                
            if "example" in func:
                self.add_paragraph("**Example**:")
                self.add_code_block(func["example"], func.get("language", ""))
                
    def generate_build_section(self, build: Dict):
        """빌드 섹션 생성"""
        self.add_title("5. Build & Run", 2)
        
        if "prerequisites" in build:
            self.add_title("Prerequisites", 3)
            self.add_bullet_list(build["prerequisites"])
            
        if "commands" in build:
            self.add_title("Build Commands", 3)
            self.add_code_block(build["commands"], "bash")
            
        if "run" in build:
            self.add_title("Run", 3)
            self.add_code_block(build["run"], "bash")
            
    def save(self, filename: Optional[str] = None) -> str:
        """문서 저장"""
        if filename is None:
            filename = f"{self.project_name.lower()}_documentation.md"
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.content))
            
        return filepath
        
    def get_content(self) -> str:
        """전체 콘텐츠 반환"""
        return '\n'.join(self.content)


# =============================================================================
# 템플릿 함수들
# =============================================================================

def create_basic_template(project_name: str) -> MarkdownDocGenerator:
    """기본 템플릿으로 문서 생성"""
    doc = MarkdownDocGenerator(project_name)
    
    # Header
    doc.generate_header()
    
    # TOC
    doc.add_toc([
        "1. Overview",
        "2. Architecture", 
        "3. Workflow",
        "4. Key Functions",
        "5. Build & Run"
    ])
    
    return doc


def example_usage():
    """사용 예시"""
    doc = create_basic_template("MyProject")
    
    # Overview
    doc.generate_overview_section({
        "purpose": "This project does amazing things.",
        "features": ["Feature 1", "Feature 2", "Feature 3"],
        "tech_stack": {
            "Language": "Python 3.10",
            "Framework": "FastAPI",
            "Database": "PostgreSQL"
        }
    })
    
    # Architecture
    doc.generate_architecture_section({
        "description": "The system follows a layered architecture.",
        "diagram": """flowchart TD
    A[Client] --> B[API Gateway]
    B --> C[Service Layer]
    C --> D[Database]""",
        "components": [
            {
                "name": "API Gateway",
                "description": "Handles incoming requests",
                "responsibilities": ["Authentication", "Rate limiting", "Routing"]
            }
        ]
    })
    
    # Workflow
    doc.generate_workflow_section({
        "description": "Main processing workflow",
        "diagram": """sequenceDiagram
    Client->>API: Request
    API->>Service: Process
    Service->>DB: Query
    DB-->>Service: Result
    Service-->>API: Response
    API-->>Client: Result""",
        "steps": [
            {"name": "Receive Request", "description": "API receives client request"},
            {"name": "Process", "description": "Business logic execution"},
            {"name": "Return Response", "description": "Send result back to client"}
        ]
    })
    
    # Functions
    doc.generate_functions_section([
        {
            "name": "process_data()",
            "purpose": "Main data processing function",
            "params": [
                {"name": "data", "description": "Input data dictionary"},
                {"name": "options", "description": "Processing options"}
            ],
            "returns": "Processed result dictionary",
            "example": "result = process_data(data, {'mode': 'fast'})"
        }
    ])
    
    # Build
    doc.generate_build_section({
        "prerequisites": ["Python 3.10+", "pip", "PostgreSQL"],
        "commands": "pip install -r requirements.txt",
        "run": "python main.py"
    })
    
    # Save
    filepath = doc.save()
    print(f"Document saved: {filepath}")
    
    return doc


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Markdown documentation")
    parser.add_argument("--project", default="Project", help="Project name")
    parser.add_argument("--output", default="/mnt/user-data/outputs", help="Output directory")
    parser.add_argument("--example", action="store_true", help="Generate example document")
    
    args = parser.parse_args()
    
    if args.example:
        example_usage()
    else:
        print(f"Creating template for: {args.project}")
        doc = create_basic_template(args.project)
        doc.output_dir = args.output
        filepath = doc.save()
        print(f"Template saved: {filepath}")
