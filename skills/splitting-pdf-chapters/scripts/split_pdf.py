#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Large PDF Splitter

This script splits a PDF file into individual chapters based on PDF bookmarks.
It extracts each chapter and saves it as a separate PDF file.

Usage:
    python split_pdf.py --pdf-path <path> [--output-dir <dir>] [--chapters <list>] [--list-only]

Examples:
    # List available chapters without splitting
    python split_pdf.py -p book.pdf --list-only

    # Split all chapters
    python split_pdf.py -p book.pdf -o chapters

    # Extract specific chapters (1, 3, 5-7)
    python split_pdf.py -p book.pdf -c "1,3,5-7" -o chapters
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Set
from pypdf import PdfReader, PdfWriter

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a filename by removing invalid Windows filename characters.

    Args:
        filename: The original filename to sanitize
        max_length: Maximum filename length (Windows limit is 255)

    Returns:
        A sanitized filename safe for Windows
    """
    # Remove invalid Windows filename characters: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()

    return sanitized or "chapter"


def extract_bookmarks(pdf_reader: PdfReader) -> List[Tuple[str, int]]:
    """
    Extract bookmarks (outline) from the PDF.

    Args:
        pdf_reader: PdfReader object

    Returns:
        List of tuples containing (bookmark_title, page_number)
    """
    bookmarks = []

    def extract_outline(outline, bookmarks_list):
        """Recursively extract bookmarks from the outline."""
        for item in outline:
            if isinstance(item, dict):
                title = item.get('/Title', 'Unknown')
                page_num = pdf_reader.get_destination_page_number(item)
                if page_num is not None:
                    bookmarks_list.append((title, page_num))
            else:
                # If item is a list/outline, recursively process it
                extract_outline(item, bookmarks_list)

    try:
        outline = pdf_reader.outline
        if outline:
            extract_outline(outline, bookmarks)
    except Exception as e:
        print(f"Warning: Could not extract bookmarks: {e}")

    return bookmarks


def parse_chapter_selection(chapters_str: str, max_chapters: int) -> Optional[Set[int]]:
    """
    Parse chapter selection string like '1,3,5-7' into a set of chapter numbers.

    Args:
        chapters_str: Selection string (e.g., "1,3,5-7")
        max_chapters: Maximum chapter number (total chapters)

    Returns:
        Set of selected chapter numbers (1-indexed), or None if invalid format
    """
    selected = set()

    try:
        parts = chapters_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle range like "5-7"
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > max_chapters or start > end:
                    print(f"Error: Invalid range {part}. Valid range is 1-{max_chapters}")
                    return None
                selected.update(range(start, end + 1))
            else:
                # Handle single number
                num = int(part)
                if num < 1 or num > max_chapters:
                    print(f"Error: Chapter {num} is out of range (1-{max_chapters})")
                    return None
                selected.add(num)

        return selected if selected else None
    except (ValueError, AttributeError):
        print(f"Error: Invalid chapter selection format: {chapters_str}")
        print("Valid formats: '1,3,5' or '5-10' or '1,3,5-7'")
        return None


def list_chapters(pdf_path: Path) -> bool:
    """
    List available chapters in the PDF without splitting.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        True if successful, False otherwise
    """
    # Verify PDF exists
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return False

    try:
        # Read the PDF
        print(f"Reading PDF: {pdf_path}")
        pdf_reader = PdfReader(pdf_path)
        total_pages = len(pdf_reader.pages)

        # Extract bookmarks
        bookmarks = extract_bookmarks(pdf_reader)

        if not bookmarks:
            print("No bookmarks found in PDF.")
            return False

        # Sort bookmarks by page number
        bookmarks.sort(key=lambda x: x[1])

        print(f"\nFound {len(bookmarks)} chapters in '{pdf_path.name}':\n")

        for chapter_num, (title, start_page) in enumerate(bookmarks, 1):
            # Determine end page
            if chapter_num < len(bookmarks):
                end_page = bookmarks[chapter_num][1]
            else:
                end_page = total_pages

            num_pages = end_page - start_page
            safe_title = title.encode('utf-8', errors='replace').decode('utf-8')
            print(f"  {chapter_num:3d}. {safe_title:<50} (pages {start_page + 1:4d}-{end_page:4d}, {num_pages:4d} pages)")

        return True

    except Exception as e:
        print(f"Error reading PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def split_pdf(pdf_path: Path, output_dir: Path, selected_chapters: Optional[Set[int]] = None) -> bool:
    """
    Split a PDF into chapters based on bookmarks.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory where chapter PDFs will be saved
        selected_chapters: Optional set of specific chapters to extract (1-indexed)

    Returns:
        True if successful, False otherwise
    """
    # Verify PDF exists
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return False

    try:
        # Read the PDF
        print(f"Reading PDF: {pdf_path}")
        pdf_reader = PdfReader(pdf_path)
        total_pages = len(pdf_reader.pages)
        print(f"Total pages: {total_pages}")

        # Extract bookmarks
        bookmarks = extract_bookmarks(pdf_reader)

        if not bookmarks:
            print("Error: No bookmarks found in PDF. Cannot split by chapters.")
            return False

        print(f"Found {len(bookmarks)} chapters from bookmarks")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {output_dir}")

        # Sort bookmarks by page number to ensure proper order
        bookmarks.sort(key=lambda x: x[1])

        # Filter chapters if specified
        chapters_to_extract = bookmarks
        if selected_chapters:
            chapters_to_extract = [
                bookmarks[i - 1] for i in sorted(selected_chapters)
                if 1 <= i <= len(bookmarks)
            ]
            print(f"Extracting {len(chapters_to_extract)} selected chapters")

        # Extract and save each chapter
        extracted_count = 0
        for chapter_num, (title, start_page) in enumerate(bookmarks, 1):
            # Skip if not selected
            if selected_chapters and chapter_num not in selected_chapters:
                continue

            # Determine end page (start of next chapter or end of PDF)
            if chapter_num < len(bookmarks):
                end_page = bookmarks[chapter_num][1]
            else:
                end_page = total_pages

            # Create filename
            sanitized_title = sanitize_filename(title)
            filename = f"{chapter_num:02d}_{sanitized_title}.pdf"
            output_path = output_dir / filename

            # Extract pages for this chapter
            pdf_writer = PdfWriter()
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # Save chapter PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            num_pages = end_page - start_page
            safe_title = title.encode('utf-8', errors='replace').decode('utf-8')
            print(f"  {chapter_num:3d}. {safe_title:<50} (pages {start_page + 1:4d}-{end_page:4d}, {num_pages:4d} pages) -> {filename}")

            extracted_count += 1

        print(f"\nSuccessfully extracted {extracted_count} chapters!")
        print(f"Chapters saved to: {output_dir}")
        return True

    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Split a PDF into chapters based on bookmarks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -p book.pdf                          # Split all chapters
  %(prog)s -p book.pdf -o output                # Split to custom directory
  %(prog)s -p book.pdf -l                       # List chapters without splitting
  %(prog)s -p book.pdf -c "1,3,5-7"             # Extract specific chapters
  %(prog)s -p book.pdf -c "1,3,5-7" -o output   # Extract specific chapters to custom directory
        """
    )

    parser.add_argument(
        '-p', '--pdf-path',
        required=True,
        help='Path to the PDF file to split'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default='chapters',
        help='Output directory for chapter files (default: chapters)'
    )

    parser.add_argument(
        '-c', '--chapters',
        help='Specific chapters to extract (e.g., "1,3,5-7")'
    )

    parser.add_argument(
        '-l', '--list-only',
        action='store_true',
        help='List available chapters without splitting'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    pdf_path = Path(args.pdf_path)
    output_dir = Path(args.output_dir)

    print("=" * 80)
    print("Large PDF Splitter")
    print("=" * 80)

    # Handle list-only mode
    if args.list_only:
        success = list_chapters(pdf_path)
        if not success:
            return 1
        return 0

    # Parse chapter selection if provided
    selected_chapters = None
    if args.chapters:
        # First list chapters to get count
        if not pdf_path.exists():
            print(f"Error: PDF file not found at {pdf_path}")
            return 1

        try:
            pdf_reader = PdfReader(pdf_path)
            bookmarks = extract_bookmarks(pdf_reader)
            if not bookmarks:
                print("Error: No bookmarks found in PDF.")
                return 1

            selected_chapters = parse_chapter_selection(args.chapters, len(bookmarks))
            if selected_chapters is None:
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1

    # Split the PDF
    success = split_pdf(pdf_path, output_dir, selected_chapters)

    if success:
        print("\n[OK] PDF splitting completed successfully!")
    else:
        print("\n[ERROR] PDF splitting failed!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
