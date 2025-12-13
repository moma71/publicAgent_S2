import os
import re
import glob

def parse_markdown_to_html(md_content, title_num):
    lines = md_content.split('\n')
    html_lines = []
    
    # 1. HTML Header
    html_lines.append('<!DOCTYPE html>')
    html_lines.append('<html lang="ko">')
    html_lines.append('<head>')
    html_lines.append('    <meta charset="UTF-8">')
    html_lines.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_lines.append(f'    <title>구산구 AI 혁명기 - Episode {title_num}</title>')
    html_lines.append('    <link rel="stylesheet" href="../style.css">')
    html_lines.append('    <link rel="stylesheet" href="../episodes-common/episode.css">')
    html_lines.append('</head>')
    html_lines.append('<body>')
    html_lines.append('    <div id="common-header"></div>')
    html_lines.append('    <script src="../episodes-common/load-header.js" defer></script>')
    html_lines.append('')
    html_lines.append('    <div class="ep-container" style="padding-top:100px;">')
    html_lines.append('        <div class="episode-wrapper">')
    html_lines.append('')

    # 2. Content logic
    img_count = 1
    in_guide = False
    in_code_block = False
    
    # Extract titles safely
    ep_title_text = f"Episode {title_num}"
    series_title_text = "구산구 AI 혁명기" # Default

    # Pre-scan for specific title formats
    for line in lines[:5]:
        if line.strip().startswith('**') and 'Episode' in line:
            # Format: **구산구 AI 혁명기 - Episode 1**
            clean = line.strip().strip('*')
            parts = clean.split('-')
            if len(parts) > 0:
                series_title_text = parts[0].strip()
        if line.strip().startswith('# Ep'):
            # Format: # Ep 1: 추락
            ep_title_text = line.strip().replace('# Ep', 'Episode').strip()

    html_lines.append('            <div class="chapter-title">')
    html_lines.append(f'                <h1>🎤 {series_title_text}</h1>')
    html_lines.append(f'                <h2>{ep_title_text}</h2>')
    html_lines.append('                <div class="separator"></div>')
    html_lines.append('            </div>')
    html_lines.append('')

    iterator = iter(lines)
    for line in iterator:
        s_line = line.strip()
        
        # Check for footer marker [Ep X 완료] - User requested removal of last part
        if '[Ep' in s_line and '완료]' in s_line:
             break
        
        # Skip empty lines, but maybe preserve some spacing? 
        # HTML p tags handle spacing, so empty lines in MD usually mean new paragraph.
        if not s_line:
            continue

        # Skip the detailed title lines we already processed
        if s_line.startswith('# Ep') or (s_line.startswith('**') and 'Episode' in s_line and img_count == 1):
            continue
        
        # Separator
        if s_line == '---':
            if in_guide:
                 html_lines.append('            </div>') # Close guide if open
                 in_guide = False
            html_lines.append('            <div class="separator"></div>')
            continue

        # Guide Section Start
        if s_line.startswith('## 💡') or s_line.startswith('## 💬'):
            if in_guide:
                html_lines.append('            </div>')
                html_lines.append('            <div class="separator"></div>')
            
            in_guide = True
            html_lines.append('            <div class="ai-guide">')
            html_lines.append(f'                <h2>{s_line.replace("## ", "")}</h2>')
            continue

        # Standard Headers handling (Global)
        if s_line.startswith('### '):
             html_lines.append(f'            <h3>{s_line.replace("### ", "")}</h3>')
             continue
        
        if s_line.startswith('#### '):
             html_lines.append(f'            <h4>{s_line.replace("#### ", "")}</h4>')
             continue

        # Check for ## but not the guide ones handled above
        if s_line.startswith('## '):
             html_lines.append(f'            <h2>{s_line.replace("## ", "")}</h2>')
             continue

        # Code Block
        if s_line.startswith('```'):
            if in_code_block:
                html_lines.append('                </div>')
                in_code_block = False
            else:
                html_lines.append('                <div class="prompt-code">')
                in_code_block = True
            continue
        
        if in_code_block:
            html_lines.append(f'{line}') # Keep indentation
            continue

        # Images
        # Pattern: ![Alt](placeholder) or ![Alt](...png/jpg)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', s_line)
        if img_match:
            alt_text = img_match.group(1)
            # Ensure 2 digits: 01.png, 02.png...
            img_filename = f"{img_count:02d}.png" 
            html_lines.append(f'            <div class="scene-media"><img class="scene-image" src="{img_filename}" alt="{alt_text}"></div>')
            img_count += 1
            continue
            
        # Captions
        # Check if line is *Italic* 
        # Note: formatting can be *Text* or _Text_
        if (s_line.startswith('*') and s_line.endswith('*')) and not s_line.startswith('**'):
            caption_text = s_line.strip('*')
            html_lines.append(f'            <div class="caption">{caption_text}</div>')
            continue

        # Inside Guide Headers (Redundant if Global handled it? Yes, but inside guide usually we want same h2/h3)
        # Actually checking above will handle it.
        # Removing specific checks here to avoid double processing or incorrect order if I didn't remove them.
        # But wait, lines are processed in order. If I added the check BEFORE code block, it will catch it.
        # But wait, check `in_guide` logic.
        # The global headers check I inserted is BEFORE code block check and AFTER guide check.
        # So it will handle ## inside guide too?
        # Yes.
        # But `in_guide` needs to be open.
        # So I don't need these specific blocks anymore?
        # Let's remove them to be clean.


        # Bold Boxes (Email Box)
        # Check strict **Text**
        if s_line.startswith('**') and s_line.endswith('**'):
            content = s_line.strip('*')
            html_lines.append('            <div class="email-box">')
            html_lines.append(f'                <p><strong>{content}</strong></p>')
            html_lines.append('            </div>')
            continue

        # Blockquotes as Email Box
        if s_line.startswith('> '):
            content = s_line.replace('> ', '')
            html_lines.append('            <div class="email-box">')
            html_lines.append(f'                <p><strong>{content}</strong></p>')
            html_lines.append('            </div>')
            continue
            
        # Lists (Simple)
        if s_line.startswith('- '):
             html_lines.append(f'            <p>{s_line}</p>')
             continue

        # Tables (Simple passthrough or p)
        if s_line.startswith('|'):
             html_lines.append(f'            <p>{s_line}</p>')
             continue
             
        # Standard Text
        # Apply bold formatting inline? **bold** -> <strong>bold</strong>
        # Simple replace for now
        formatted_line = s_line
        formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_line)
        
        html_lines.append(f'            <p>{formatted_line}</p>')

    # Close tags
    if in_guide:
        html_lines.append('            </div>')
    
    html_lines.append('        </div>')
    html_lines.append('    </div>')
    html_lines.append('</body>')
    html_lines.append('</html>')

    return '\n'.join(html_lines)


def process_files():
    base_dir = r"c:\Users\wonders\Desktop\webNovele\publicAgent_S2"
    src_dir = os.path.join(base_dir, "src")
    
    # Process all Ep*_Story.md files including Ep1
    files = glob.glob(os.path.join(src_dir, "Ep*_Story.md"))
    for file_path in files:
        filename = os.path.basename(file_path)
        # Extract number "Ep1_..." -> 1 or "Ep10_..." -> 10
        match = re.search(r'Ep(\d+)_', filename)
        if match:
            ep_num = int(match.group(1))
            print(f"Processing Episode {ep_num}: {file_path}")
            
            # Destination folder
            dest_folder = os.path.join(base_dir, f"episode{ep_num}")
            os.makedirs(dest_folder, exist_ok=True)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            html_content = parse_markdown_to_html(content, ep_num)
            
            out_path = os.path.join(dest_folder, "index.html")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Written to {out_path}")

if __name__ == "__main__":
    process_files()
