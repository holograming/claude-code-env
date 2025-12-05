---
name: splitting-pdf-chapters
description: Splits large PDF files into individual chapters based on PDF bookmarks. Use when splitting PDFs by chapters, extracting chapters from PDFs, or dividing large PDFs into smaller parts.
---

# Splitting PDF Chapters

Splits large PDF files into individual chapter files based on the PDF's built-in bookmarks or outline structure.

## Instructions

When splitting a PDF, follow this workflow:

1. **Get PDF path**: Ask the user for the path to their PDF file
2. **Confirm output location**: Ask where to save chapters (default: "chapters" directory)
3. **Determine extraction scope**: Ask if they want all chapters or specific chapters
4. **Execute split**: Run the script with appropriate arguments:
   - `python skills/splitting-pdf-chapters/scripts/split_pdf.py -p <pdf_path> -o <output_dir>` for all chapters
   - `python skills/splitting-pdf-chapters/scripts/split_pdf.py -p <pdf_path> -c "1,3,5-7"` for specific chapters
   - `python skills/splitting-pdf-chapters/scripts/split_pdf.py -p <pdf_path> --list-only` to preview chapters
5. **Report results**: Display the chapter count, filenames, and page ranges

**Prerequisites**:
- PDF must contain bookmarks or outline (table of contents)
- Python 3.7+ available
- pypdf library (included in requirements.txt)

**Output format**: Chapter files are named as `{number:02d}_{chapter_name}.pdf` (e.g., `01_Introduction.pdf`, `02_Chapter 1. Getting Started.pdf`)

For detailed command-line options and technical details, see [FORMS.md](FORMS.md) and [REFERENCE.md](REFERENCE.md).

## Examples

### Split all chapters from a PDF

```bash
python scripts/split_pdf.py -p "book.pdf"
```

Result: Creates `chapters/` directory with numbered PDF files for each chapter.

### Preview chapters without splitting

```bash
python scripts/split_pdf.py -p "book.pdf" --list-only
```

Result: Displays all available chapters with page ranges and lengths.

### Extract specific chapters

```bash
python scripts/split_pdf.py -p "textbook.pdf" -c "1,3,5-7"
```

Result: Creates files for chapters 1, 3, 5, 6, and 7 only.

### Extract to custom directory

```bash
python scripts/split_pdf.py -p "manual.pdf" -o "output_folder"
```

Result: Creates `output_folder/` instead of `chapters/` with split PDFs.
