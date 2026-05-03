#!/usr/bin/env python3
"""Convert COMPLETE_DOCUMENTATION.md to HTML with styling."""

import sys
import os

# Try importing markdown
try:
    import markdown
    from markdown.extensions import extra, toc
    has_markdown = True
except ImportError:
    has_markdown = False
    print("Warning: markdown module not found, using basic conversion")

def basic_markdown_to_html(md_text):
    """Basic markdown to HTML conversion without external dependencies."""
    import re
    
    html = md_text
    
    # Escape HTML special characters in code blocks first
    def escape_code_block(match):
        code = match.group(1)
        return f'<pre><code>{code}</code></pre>'
    
    html = re.sub(r'```(?:.*?)\n(.*?)```', escape_code_block, html, flags=re.DOTALL)
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Lists
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', html)
    
    # Horizontal rules
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    
    # Paragraphs (simple approach)
    lines = html.split('\n')
    result = []
    in_para = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<') or stripped == '':
            if in_para:
                result.append('</p>')
                in_para = False
            result.append(line)
        else:
            if not in_para:
                result.append('<p>')
                in_para = True
            result.append(line)
    
    if in_para:
        result.append('</p>')
    
    html = '\n'.join(result)
    
    return html

def convert_markdown_file(input_file, output_file):
    """Convert markdown file to HTML."""
    
    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    if has_markdown:
        print("Using markdown library for conversion...")
        html_body = markdown.markdown(
            md_content,
            extensions=['extra', 'toc', 'tables', 'fenced_code']
        )
    else:
        print("Using basic conversion...")
        html_body = basic_markdown_to_html(md_content)
    
    # Create full HTML document with styling
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Documentation - Robotic Microscope System</title>
    <style>
        body {{
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }}
        
        h1 {{
            color: #007acc;
            border-bottom: 3px solid #007acc;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        
        h2 {{
            color: #0066a1;
            border-bottom: 2px solid #ddd;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        
        h3 {{
            color: #004d80;
            margin-top: 25px;
        }}
        
        h4 {{
            color: #003d66;
            margin-top: 20px;
        }}
        
        pre {{
            background: #f6f8fa;
            padding: 16px;
            overflow-x: auto;
            border-left: 4px solid #007acc;
            border-radius: 3px;
            font-size: 14px;
            line-height: 1.45;
        }}
        
        code {{
            background: #f6f8fa;
            padding: 3px 6px;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 90%;
        }}
        
        pre code {{
            background: transparent;
            padding: 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        td, th {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}
        
        th {{
            background: #007acc;
            color: white;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        a {{
            color: #007acc;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 20px;
            margin-left: 0;
            color: #666;
            font-style: italic;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        
        ul, ol {{
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        .toc {{
            background: #f6f8fa;
            padding: 20px;
            border-radius: 5px;
            margin: 30px 0;
        }}
        
        @media print {{
            body {{
                max-width: 100%;
                font-size: 12pt;
            }}
            
            pre {{
                page-break-inside: avoid;
            }}
            
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
{body}
</body>
</html>"""
    
    full_html = html_template.format(body=html_body)
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Successfully converted {input_file} to {output_file}")
    print(f"Output size: {len(full_html):,} bytes")

if __name__ == '__main__':
    input_file = 'COMPLETE_DOCUMENTATION.md'
    output_file = 'COMPLETE_DOCUMENTATION.html'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        sys.exit(1)
    
    convert_markdown_file(input_file, output_file)
