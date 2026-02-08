import pandas as pd
import os

OUTPUT_DIR = r"d:\backup\ptspRag\revision\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_table_2b():
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            caption { font-weight: bold; margin-bottom: 10px; text-align: left; }
        </style>
    </head>
    <body>
    """
    
    # Table II-B: Detailed System Configuration Parameters
    # CORRECTED VALUES: Chunk Overlap 200, Temperature 0.6
    table_data = {
        'Component': [
            'Dataset Quality', 'Embedding Model', 'Chunk Size', 'Chunk Overlap',
            'VOR k / Threshold', 'EVR k / Threshold', 'Hybrid Score α',
            'Debate Phase', 'LLM Model', 'Max Tokens', 'Temperature'
        ],
        'Legacy': [
            'Outdated/noisy', 'all-MiniLM-L6-v2', '1,200 chars', '200 chars',
            '12 / 0.75', '24 / 0.60', '0.7',
            'No', 'Llama-3.3-70B', '8,000', '0.6'
        ],
        'Enhanced': [
            'Cleaned', 'all-MiniLM-L6-v2', '1,200 chars', '200 chars',
            '12 / 0.75', '24 / 0.60', '0.7',
            'No', 'Llama-3.3-70B', '8,000', '0.6'
        ],
        'MAF-RAG': [
            'Cleaned', 'all-MiniLM-L6-v2', '1,200 chars', '200 chars',
            '12 / 0.75', '24 / 0.60', '0.7',
            'Yes (k=4, r_max=3)', 'Llama-3.3-70B', '8,000', '0.6'
        ]
    }
    
    df = pd.DataFrame(table_data)
    html_content += "<caption>TABLE II-B: DETAILED SYSTEM CONFIGURATION PARAMETERS</caption>"
    html_content += df.to_html(index=False)
    
    html_content += "</body></html>"
    
    output_path = os.path.join(OUTPUT_DIR, 'table_2b_configuration.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    generate_table_2b()
