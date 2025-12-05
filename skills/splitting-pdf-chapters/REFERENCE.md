# Technical Reference

Deep technical reference and implementation details for the PDF chapter splitting skill.

## Architecture Overview

The skill provides a command-line interface to the underlying `pypdf` library, automating the process of:
1. Reading PDF bookmark/outline structure
2. Mapping bookmarks to page ranges
3. Extracting pages for each chapter
4. Generating output PDF files

## Core Workflow

```
Input PDF
    ↓
Parse PDF Structure & Bookmarks
    ↓
Extract Bookmark Hierarchy
    ↓
Map Bookmarks to Page Ranges
    ↓
Validate Chapter Selection (if specified)
    ↓
Create Output Directory
    ↓
For Each Chapter: Extract Pages → Save PDF
    ↓
Report Results
```

## PDF Bookmarks and Outline Structure

### Understanding PDF Bookmarks

PDF bookmarks (outline entries) are hierarchical navigation elements that link to specific pages. The skill extracts this structure to identify chapters.

**Bookmark properties**:
- Title: Chapter or section name
- Target: The page number this bookmark points to
- Hierarchy: Bookmarks can be nested (parent-child relationships)

### How Chapters Are Identified

1. **Read Outline**: Extracts all top-level bookmarks from PDF
2. **Get Page Numbers**: For each bookmark, determines target page
3. **Create Ranges**: Chapter N spans from bookmark N's page to bookmark N+1's page (or end of document)
4. **Handle Nesting**: Only uses top-level bookmarks; nested levels are flattened

## Page Range Calculation

Given bookmarks at pages [2, 12, 25, 50, 725]:

| Chapter | Start Page | End Page | Pages |
|---------|-----------|----------|-------|
| 1       | 2         | 11       | 10    |
| 2       | 12        | 24       | 13    |
| 3       | 25        | 49       | 25    |
| 4       | 50        | 724      | 675   |
| 5       | 725       | 725      | 1     |

The last chapter extends to the end of the PDF document.

## Filename Handling

### Character Sanitization

Invalid Windows filename characters are removed:

**Removed characters**: `< > : " / \ | ? *`

**Process**:
1. Extract chapter name from bookmark: `"Chapter 2: Getting Started"`
2. Remove invalid chars: `"Chapter 2 Getting Started"`
3. Enforce maximum length: 200 characters (Windows limit is 255)
4. Format output: `02_Chapter 2 Getting Started.pdf`

### Unicode Support

The skill properly handles international characters:
- PDF bookmarks in multiple languages
- Chinese, Japanese, Arabic, Cyrillic, etc.
- Windows-compatible UTF-8 encoding

## Dependencies

### pypdf Library

**Version**: >= 4.0.0 (Modern, actively maintained)

**Used for**:
- Reading PDF structure and bookmarks
- Extracting page ranges
- Creating new PDF documents
- Accessing PDF metadata

**Why pypdf**:
- Pure Python implementation
- No system dependencies
- Cross-platform compatible
- Active maintenance and updates

### Python Standard Library Modules

- **pathlib**: Cross-platform file path handling
- **re**: Regular expressions for filename sanitization
- **sys**: System-level operations (encoding, exit codes)
- **argparse**: Command-line argument parsing
- **typing**: Type hints for code clarity

## Implementation Details

### Bookmark Extraction Algorithm

```
function extract_bookmarks(pdf_reader):
    bookmarks = []

    function extract_recursive(outline_items):
        for each item in outline_items:
            if item is a bookmark:
                title = item.title
                page = pdf_reader.get_destination_page_number(item)
                if page is not None:
                    bookmarks.append((title, page))
            elif item is a sub-outline:
                extract_recursive(item)

    extract_recursive(pdf_reader.outline)
    sort bookmarks by page number
    return bookmarks
```

### Page Extraction Process

For each selected chapter:
1. Create new PdfWriter object
2. For each page in the chapter's range:
   - Add page from original PDF to new document
3. Save new document with formatted filename
4. Record statistics (page count, filename)

## Error Handling

### Graceful Degradation

If PDF has issues:
- Missing bookmarks → Inform user, exit cleanly
- Invalid chapter selection → Skip invalid chapters, process valid ones
- Permission issues → Detailed error message with path
- Corrupted page → Skip page and continue with warning

### Validation

**Before splitting**:
1. Verify PDF file exists and is readable
2. Check PDF has bookmarks
3. Validate chapter selection syntax
4. Check output directory is writable (create if needed)

**During splitting**:
1. Verify each page is readable
2. Monitor file write operations
3. Confirm output file integrity

## Limitations and Constraints

### PDF Requirements

**Must have**:
- Valid PDF structure
- Bookmarks/outline entries
- Readable pages

**Cannot handle**:
- PDFs without bookmarks
- Encrypted/password-protected PDFs (without password)
- Severely corrupted PDFs
- Non-standard PDF variants

### Performance Constraints

- **Memory**: Loads one page at a time (memory-efficient)
- **Disk**: Requires space for output files (typically 20-50% of original)
- **Time**: Linear with PDF size and chapter count

### Platform-Specific Notes

**Windows**:
- Filename character restrictions enforced
- Path length limit: 255 characters per filename
- Case-insensitive filesystem

**macOS/Linux**:
- More permissive filename rules
- Forward slashes in paths required
- Case-sensitive filesystem

## Security Considerations

**Safe operations**:
- Read-only access to input PDF
- Filesystem operations only in output directory
- No external network access
- No code execution beyond PDF processing

**Trust model**:
- Trusts PDF structure (assumed valid)
- Assumes output directory is trusted location
- No validation against malicious PDFs (handled by pypdf)

## Troubleshooting Guide

### Common Issues and Technical Solutions

**Issue**: Script hangs or runs very slowly

**Causes**: Large PDF, slow disk, many chapters
**Solutions**:
- Use `--chapters` to process subset
- Check disk space and read/write performance
- Try on faster system if available

**Issue**: Output files are smaller than expected

**Causes**: This is normal - each chapter is subset of original
**Solutions**:
- Verify page counts shown in output are correct
- Check chapter range selection

**Issue**: Chapter names appear truncated

**Causes**: Filename length limit (255 chars) or sanitization
**Solutions**:
- This is expected for very long chapter names
- Check FORMS.md for naming details

**Issue**: Memory usage is high

**Causes**: Very large PDF or system resources
**Solutions**:
- Process smaller PDFs or use `--chapters` to limit
- Close other applications
- Check available system RAM

## Version Information

**Script version**: Based on pypdf >= 4.0.0
**Python requirement**: 3.7+
**Tested on**: Windows, macOS, Linux

## API Reference

### Script Interface

**Entry point**: `split_pdf.py`
**Language**: Python 3
**Execution**: `python split_pdf.py [arguments]`

### Output Format

**Return codes**:
- 0: Success
- 1: Error (details shown in console)

**Console output**:
- Formatted table of chapters
- Summary statistics
- Error messages with suggested resolutions

**Created files**:
- `{output_dir}/{chapter_number:02d}_{name}.pdf`
- One file per selected chapter

## Advanced Usage

### Batch Processing

To split multiple PDFs:

```bash
for file in *.pdf; do
  python scripts/split_pdf.py -p "$file" -o "output_${file%.pdf}"
done
```

### Integration with Other Tools

The output PDF files can be used with:
- PDF viewers and readers
- Document management systems
- Indexing and search tools
- OCR systems (if needed)
- Print systems

### Monitoring and Logging

No built-in logging, but console output shows:
- Processing progress
- Any errors or warnings
- Final summary

Capture output with:
```bash
python scripts/split_pdf.py -p input.pdf > output.log 2>&1
```

## Future Enhancement Possibilities

**Potential improvements**:
- Filtering chapters by name or page count
- Custom output naming patterns
- Metadata preservation from original PDF
- Concurrent chapter processing (for large PDFs)
- Progress bar for slow operations
- Logging to file option
