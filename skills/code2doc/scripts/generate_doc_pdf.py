#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Documentation Generator
코드 분석 결과를 PDF 형식의 기술 문서로 생성

Features:
- 테이블 컬럼 너비 명시적 지정 (텍스트 겹침 방지)
- 페이지 번호/헤더 자동 추가
- 본문 + 부록 분리 구조
- 가독성 최적화

Usage:
    python generate_doc_pdf.py --project "ProjectName" --output "/path/to/output"

Dependencies:
    pip install reportlab --break-system-packages
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Preformatted, KeepTogether
)
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =============================================================================
# 폰트 설정
# =============================================================================
FONT_PATHS = {
    'main': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
}

for name, path in FONT_PATHS.items():
    if os.path.exists(path):
        font_name = f'DocFont_{name}'
        pdfmetrics.registerFont(TTFont(font_name, path))

FONT_MAIN = 'DocFont_main'
FONT_BOLD = 'DocFont_bold'
FONT_MONO = 'DocFont_mono'

# =============================================================================
# 색상 팔레트
# =============================================================================
COLORS = {
    'primary': HexColor('#1a365d'),
    'secondary': HexColor('#2c5282'),
    'accent': HexColor('#3182ce'),
    'text': HexColor('#2d3748'),
    'light_text': HexColor('#718096'),
    'bg_light': HexColor('#f7fafc'),
    'border': HexColor('#cbd5e0'),
    'success': HexColor('#38a169'),
    'warning': HexColor('#dd6b20'),
}

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 2 * cm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


# =============================================================================
# 페이지 번호 콜백
# =============================================================================
def add_page_number(canvas, doc):
    """페이지 번호와 헤더 추가"""
    page_num = canvas.getPageNumber()
    canvas.saveState()
    
    # 페이지 번호 (하단 중앙)
    canvas.setFont(FONT_MAIN, 9)
    canvas.setFillColor(COLORS['text'])
    canvas.drawCentredString(PAGE_WIDTH / 2, 1.5 * cm, f"- {page_num} -")
    
    # 헤더 (2페이지부터)
    if page_num > 1:
        canvas.setFont(FONT_MAIN, 8)
        canvas.setFillColor(COLORS['light_text'])
        canvas.drawString(MARGIN, PAGE_HEIGHT - 1.2 * cm, 
                         f"{doc.project_name} - Technical Documentation")
        canvas.setStrokeColor(COLORS['border'])
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, PAGE_HEIGHT - 1.4 * cm, 
                   PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 1.4 * cm)
    
    canvas.restoreState()


# =============================================================================
# 스타일 정의
# =============================================================================
def create_styles():
    """문서 스타일 생성"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='DocTitle', fontName=FONT_BOLD, fontSize=28,
        textColor=white, alignment=TA_CENTER, spaceAfter=15, leading=34
    ))
    
    styles.add(ParagraphStyle(
        name='DocSubtitle', fontName=FONT_MAIN, fontSize=14,
        textColor=HexColor('#a0aec0'), alignment=TA_CENTER, spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='ChapterTitle', fontName=FONT_BOLD, fontSize=18,
        textColor=COLORS['primary'], spaceBefore=25, spaceAfter=15, leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle', fontName=FONT_BOLD, fontSize=12,
        textColor=COLORS['secondary'], spaceBefore=18, spaceAfter=10, leading=15
    ))
    
    styles.add(ParagraphStyle(
        name='SubsectionTitle', fontName=FONT_BOLD, fontSize=10,
        textColor=COLORS['accent'], spaceBefore=12, spaceAfter=6, leading=13
    ))
    
    styles.add(ParagraphStyle(
        name='Body', fontName=FONT_MAIN, fontSize=10,
        textColor=COLORS['text'], alignment=TA_JUSTIFY, spaceAfter=8, leading=15
    ))
    
    styles.add(ParagraphStyle(
        name='BodyIndent', fontName=FONT_MAIN, fontSize=10,
        textColor=COLORS['text'], spaceAfter=6, leading=15, leftIndent=15
    ))
    
    styles.add(ParagraphStyle(
        name='TipBox', fontName=FONT_MAIN, fontSize=9,
        textColor=HexColor('#276749'), backColor=HexColor('#c6f6d5'),
        leftIndent=10, rightIndent=10, spaceBefore=8, spaceAfter=8,
        borderPadding=8, leading=13
    ))
    
    styles.add(ParagraphStyle(
        name='WarningBox', fontName=FONT_MAIN, fontSize=9,
        textColor=HexColor('#744210'), backColor=HexColor('#fefcbf'),
        leftIndent=10, rightIndent=10, spaceBefore=8, spaceAfter=8,
        borderPadding=8, leading=13
    ))
    
    styles.add(ParagraphStyle(
        name='CodeStyle', fontName=FONT_MONO, fontSize=8,
        textColor=COLORS['text'], backColor=COLORS['bg_light'],
        leftIndent=5, spaceBefore=5, spaceAfter=5, leading=11
    ))
    
    styles.add(ParagraphStyle(
        name='TOCEntry', fontName=FONT_MAIN, fontSize=11,
        textColor=COLORS['text'], spaceAfter=8, leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='AppendixTitle', fontName=FONT_BOLD, fontSize=14,
        textColor=COLORS['secondary'], spaceBefore=20, spaceAfter=12
    ))
    
    return styles


# =============================================================================
# 테이블 생성 헬퍼
# =============================================================================
def create_table(data: List[List[str]], col_widths: List[float], 
                 header_bg=None) -> Table:
    """
    테이블 생성 - 컬럼 너비를 명시적으로 지정
    
    Args:
        data: 2D 리스트 (첫 행이 헤더)
        col_widths: 각 컬럼의 너비 리스트 (cm 단위)
        header_bg: 헤더 배경색
    
    Returns:
        Table: 스타일이 적용된 테이블
    """
    if header_bg is None:
        header_bg = COLORS['primary']
    
    # cm를 포인트로 변환
    widths = [w * cm for w in col_widths]
    
    table = Table(data, colWidths=widths)
    table.setStyle(TableStyle([
        # 헤더 스타일
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # 데이터 행 스타일
        ('FONTNAME', (0, 1), (-1, -1), FONT_MAIN),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        
        # 테두리 및 패딩
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        
        # 줄무늬 배경
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLORS['bg_light']]),
    ]))
    return table


# =============================================================================
# PDF 문서 생성기 클래스
# =============================================================================
class PDFDocGenerator:
    """PDF 문서 생성기"""
    
    def __init__(self, project_name: str, output_dir: str = "/mnt/user-data/outputs"):
        self.project_name = project_name
        self.output_dir = output_dir
        self.styles = create_styles()
        self.story: List = []
        
    def add_cover(self, subtitle: str = "Technical Documentation", 
                  description: str = ""):
        """표지 추가"""
        self.story.append(Spacer(1, 2*cm))
        
        # 표지 배경
        cover_data = [['']]
        cover_table = Table(cover_data, colWidths=[CONTENT_WIDTH], rowHeights=[8*cm])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['primary']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        self.story.append(cover_table)
        
        self.story.append(Spacer(1, -7*cm))
        self.story.append(Paragraph(self.project_name, self.styles['DocTitle']))
        self.story.append(Paragraph(subtitle, self.styles['DocSubtitle']))
        
        if description:
            self.story.append(Paragraph(description, self.styles['DocSubtitle']))
            
        self.story.append(Spacer(1, 5*cm))
        self.story.append(Paragraph(
            datetime.now().strftime("%Y-%m-%d"), 
            self.styles['Body']
        ))
        self.story.append(PageBreak())
        
    def add_toc(self, sections: List[Tuple[str, str]]):
        """목차 추가 (섹션명, 페이지번호)"""
        self.story.append(Paragraph("Table of Contents", self.styles['ChapterTitle']))
        self.story.append(Spacer(1, 0.5*cm))
        
        for title, page in sections:
            if title:
                dots = '.' * 50
                toc_text = f"{title} {dots} {page}"
                self.story.append(Paragraph(toc_text, self.styles['TOCEntry']))
            else:
                self.story.append(Spacer(1, 0.3*cm))
                
        self.story.append(PageBreak())
        
    def add_chapter(self, title: str):
        """챕터 제목 추가"""
        self.story.append(Paragraph(title, self.styles['ChapterTitle']))
        
    def add_section(self, title: str):
        """섹션 제목 추가"""
        self.story.append(Paragraph(title, self.styles['SectionTitle']))
        
    def add_subsection(self, title: str):
        """소섹션 제목 추가"""
        self.story.append(Paragraph(title, self.styles['SubsectionTitle']))
        
    def add_paragraph(self, text: str):
        """본문 단락 추가"""
        self.story.append(Paragraph(text, self.styles['Body']))
        
    def add_tip(self, text: str):
        """팁 박스 추가"""
        self.story.append(Paragraph(text, self.styles['TipBox']))
        
    def add_warning(self, text: str):
        """경고 박스 추가"""
        self.story.append(Paragraph(text, self.styles['WarningBox']))
        
    def add_code(self, code: str):
        """코드 블록 추가"""
        self.story.append(Preformatted(code, self.styles['CodeStyle']))
        
    def add_bullet_list(self, items: List[str]):
        """글머리 기호 목록 추가"""
        for item in items:
            self.story.append(Paragraph(f"  *  {item}", self.styles['BodyIndent']))
            
    def add_table(self, data: List[List[str]], col_widths: List[float]):
        """테이블 추가"""
        self.story.append(create_table(data, col_widths))
        self.story.append(Spacer(1, 0.3*cm))
        
    def add_page_break(self):
        """페이지 넘김"""
        self.story.append(PageBreak())
        
    def add_spacer(self, height_cm: float = 0.5):
        """여백 추가"""
        self.story.append(Spacer(1, height_cm * cm))
        
    def add_appendix_title(self, title: str):
        """부록 제목 추가"""
        self.story.append(Paragraph(title, self.styles['AppendixTitle']))
        
    def save(self, filename: Optional[str] = None) -> str:
        """문서 저장"""
        if filename is None:
            filename = f"{self.project_name.lower().replace(' ', '_')}_documentation.pdf"
            
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=MARGIN, leftMargin=MARGIN,
            topMargin=2.5*cm, bottomMargin=2*cm
        )
        doc.project_name = self.project_name
        
        doc.build(self.story, 
                  onFirstPage=add_page_number, 
                  onLaterPages=add_page_number)
        
        return filepath


# =============================================================================
# 사용 예시
# =============================================================================
def example_usage():
    """사용 예시"""
    doc = PDFDocGenerator("Sample Project")
    
    # 표지
    doc.add_cover(
        subtitle="Technical Documentation",
        description="For Junior Developers"
    )
    
    # 목차
    doc.add_toc([
        ("1. Introduction", "3"),
        ("2. Architecture", "4"),
        ("3. Workflow", "5"),
        ("", ""),
        ("Appendix A. Details", "7"),
    ])
    
    # 챕터 1
    doc.add_chapter("1. Introduction")
    doc.add_section("What is this project?")
    doc.add_paragraph(
        "This is a sample project documentation. It demonstrates how to "
        "use the PDF generator to create professional technical documents."
    )
    doc.add_tip(
        "<b>Tip:</b> Use analogies to explain complex concepts to juniors."
    )
    
    # 테이블 예시
    doc.add_section("Project Structure")
    doc.add_table(
        data=[
            ['Folder', 'Purpose', 'Notes'],
            ['src/', 'Source code', 'Main implementation'],
            ['tests/', 'Test files', 'Unit and integration tests'],
            ['docs/', 'Documentation', 'This document'],
        ],
        col_widths=[3, 5, 5.5]  # cm 단위
    )
    
    # 코드 블록
    doc.add_section("Code Example")
    doc.add_code("""
def hello_world():
    print("Hello, World!")
    return True
    """)
    
    doc.add_page_break()
    
    # 부록
    doc.add_appendix_title("Appendix A. Technical Details")
    doc.add_paragraph("This section contains detailed technical information.")
    
    # 저장
    filepath = doc.save()
    print(f"PDF saved: {filepath}")
    
    return filepath


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate PDF documentation")
    parser.add_argument("--project", default="Project", help="Project name")
    parser.add_argument("--output", default="/mnt/user-data/outputs", help="Output directory")
    parser.add_argument("--example", action="store_true", help="Generate example document")
    
    args = parser.parse_args()
    
    if args.example:
        example_usage()
    else:
        print(f"Creating template for: {args.project}")
        doc = PDFDocGenerator(args.project, args.output)
        doc.add_cover()
        doc.add_chapter("1. Introduction")
        doc.add_paragraph("Add your content here.")
        filepath = doc.save()
        print(f"Template saved: {filepath}")
