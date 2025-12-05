# Command-Line Forms and Options

Complete reference for using the PDF splitting script with all available options and forms.

## Script Location

```
scripts/split_pdf.py
```

## Basic Command Format

```bash
python scripts/split_pdf.py --pdf-path <FILE> [OPTIONS]
```

## Required Arguments

### `--pdf-path` / `-p`

**Description**: Path to the PDF file to split

**Format**:
```bash
python scripts/split_pdf.py --pdf-path "path/to/file.pdf"
python scripts/split_pdf.py -p "file.pdf"
```

**Notes**:
- Accepts relative paths (e.g., `"./documents/book.pdf"`)
- Accepts absolute paths (e.g., `"/Users/name/Documents/book.pdf"`)
- File must exist and be readable
- File must be a valid PDF with bookmarks

## Optional Arguments

### `--output-dir` / `-o`

**Description**: Directory where chapter PDF files will be saved

**Default**: `chapters`

**Format**:
```bash
python scripts/split_pdf.py -p "input.pdf" --output-dir "output_folder"
python scripts/split_pdf.py -p "input.pdf" -o "my_chapters"
```

**Notes**:
- Directory will be created if it doesn't exist
- All chapter files saved with this as the parent directory
- Relative or absolute paths supported

### `--chapters` / `-c`

**Description**: Extract only specific chapters (selective extraction)

**Format**:
```bash
# Single chapters
python scripts/split_pdf.py -p "input.pdf" -c "1"
python scripts/split_pdf.py -p "input.pdf" -c "1,3,5"

# Chapter ranges
python scripts/split_pdf.py -p "input.pdf" -c "5-10"

# Mixed single and range
python scripts/split_pdf.py -p "input.pdf" -c "1,3,5-7,10"
```

**Syntax**:
- Single chapter: `"1"` (chapter 1 only)
- Multiple chapters: `"1,3,5"` (chapters 1, 3, and 5)
- Range: `"5-10"` (chapters 5 through 10, inclusive)
- Combined: `"1,3,5-7,10"` (chapters 1, 3, 5-7, and 10)

**Notes**:
- Chapter numbers are 1-indexed (first chapter is 1, not 0)
- Whitespace is ignored: `"1, 3, 5"` is same as `"1,3,5"`
- Invalid chapter numbers are skipped with warning
- Ranges are inclusive: `"5-7"` includes chapters 5, 6, and 7

### `--list-only` / `-l`

**Description**: Display available chapters without creating files

**Format**:
```bash
python scripts/split_pdf.py -p "input.pdf" --list-only
python scripts/split_pdf.py -p "input.pdf" -l
```

**Output**:
Shows all chapters with:
- Chapter number
- Chapter name (from PDF bookmarks)
- Page range (start-end)
- Number of pages

**Use cases**:
- Preview chapter structure before splitting
- Decide which chapters to extract
- Verify PDF has required bookmarks

## Usage Examples

### Form 1: Split Everything

**User need**: Split entire PDF into all chapters

```bash
python scripts/split_pdf.py -p "Professional_CMake.pdf"
```

**Output**:
- Creates `chapters/` directory
- Saves all chapters as 01_*.pdf, 02_*.pdf, etc.
- Console shows progress and final count

### Form 2: Split to Custom Directory

**User need**: Split entire PDF but save to specific folder

```bash
python scripts/split_pdf.py -p "book.pdf" --output-dir "split_files"
```

**Output**:
- Creates `split_files/` directory
- Saves all chapters there

### Form 3: Preview Before Splitting

**User need**: See what chapters exist before splitting

```bash
python scripts/split_pdf.py -p "textbook.pdf" --list-only
```

**Output**:
```
Found 15 chapters in 'textbook.pdf':
  1. Introduction (pages 1-10, 10 pages)
  2. Chapter 1: Getting Started (pages 11-45, 35 pages)
  3. Chapter 2: Core Concepts (pages 46-89, 44 pages)
  ...
  15. Index (pages 280-295, 15 pages)
```

### Form 4: Extract Single Chapter

**User need**: Get only one specific chapter

```bash
python scripts/split_pdf.py -p "manual.pdf" -c "5"
```

**Output**:
- Creates `chapters/` directory
- Saves only chapter 5 as `05_Chapter_Name.pdf`

### Form 5: Extract Multiple Specific Chapters

**User need**: Get chapters 1, 3, and 7-9

```bash
python scripts/split_pdf.py -p "guide.pdf" -c "1,3,7-9"
```

**Output**:
- Creates `chapters/` directory
- Saves 5 files: 01_*.pdf, 03_*.pdf, 07_*.pdf, 08_*.pdf, 09_*.pdf

### Form 6: Extract Range

**User need**: Get chapters 5 through 15 only

```bash
python scripts/split_pdf.py -p "book.pdf" -c "5-15"
```

**Output**:
- Creates `chapters/` directory
- Saves 11 files: 05_*.pdf through 15_*.pdf

### Form 7: Combined Options

**User need**: Extract chapters 1-3 and 10-12 to a custom folder

```bash
python scripts/split_pdf.py -p "book.pdf" -c "1-3,10-12" -o "selected_chapters"
```

**Output**:
- Creates `selected_chapters/` directory
- Saves 6 files: 01_*.pdf, 02_*.pdf, 03_*.pdf, 10_*.pdf, 11_*.pdf, 12_*.pdf

## Error Messages and Solutions

### "PDF file not found"

**Cause**: The specified path doesn't exist

**Solution**:
1. Verify the file path is correct
2. Check file exists in the specified location
3. Use absolute path if relative path doesn't work
4. Ensure no typos in filename

### "PDF has no bookmarks"

**Cause**: PDF doesn't have outline/table of contents

**Solution**:
1. Check if PDF has bookmarks (use `--list-only` to verify)
2. Some scanned PDFs lack bookmarks
3. Try with a different PDF that has bookmarks

### "Invalid chapter selection: Chapter X is out of range"

**Cause**: Requested chapter number exceeds available chapters

**Solution**:
1. Use `--list-only` to see available chapter numbers
2. Adjust chapter selection to valid range
3. Example: If PDF has 15 chapters, don't request chapter 20

### "Permission denied"

**Cause**: Can't read input PDF or write to output directory

**Solution**:
1. Check file permissions are readable
2. Verify output directory is writable
3. Try a different output location
4. Run with appropriate permissions if needed

## Output File Naming

Generated chapter files follow this pattern:

```
{chapter_number:02d}_{chapter_name}.pdf
```

**Components**:
- `{chapter_number:02d}`: Chapter number with zero-padding (01, 02, ... 99, 100)
- `{chapter_name}`: Chapter name from PDF bookmarks, with invalid characters removed
- Extension: `.pdf`

**Examples**:
- `01_Introduction.pdf`
- `02_Chapter 1. Getting Started.pdf`
- `15_Appendix A. Code Examples.pdf`
- `100_Final Index.pdf`

## Performance Notes

- **Small PDFs** (< 100 pages): Usually instant
- **Medium PDFs** (100-500 pages): Few seconds
- **Large PDFs** (500-1000+ pages): May take 10-30 seconds
- **Very large PDFs** (1000+ pages): Depends on system resources

Processing time increases with:
- Total number of pages
- Number of chapters to extract
- PDF complexity
