import pandas as pd
import os

OUTPUT_DIR = r"d:\backup\ptspRag\revision\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_html_tables():
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
    <h1>Manuscript Tables</h1>
    """
    
    # Table I: Confidence Score Thresholds
    table1_data = {
        'Phase': ['VOR', 'EVR', 'MAF-RAG', 'Internet-Fallback'],
        'Confidence Threshold': ['≥ 0.75', '≥ 0.60', '≥ 0.65', '≥ 0.55'],
        'Action If Met': ['Accept and return result', 'Accept and return result', 'Accept if result not "unknown"', 'Always accept if results found'],
        'Action If Not Met': ['Escalate to EVR', 'Escalate to MAF-RAG', 'Escalate to Internet-Fallback', 'Return failure message']
    }
    df1 = pd.DataFrame(table1_data)
    html_content += "<caption>TABLE I: CONFIDENCE SCORE THRESHOLDS AND PHASE ESCALATION LOGIC</caption>"
    html_content += df1.to_html(index=False)
    
    # Table II: Escalation Workflows
    table2_data = {
        'Configuration': ['Legacy Baseline', 'Enhanced Baseline', 'MAF-RAG'],
        'Dataset': ['Old (Noisy)', 'New (Clean)', 'New (Clean)'],
        'Pipeline Sequence': ['VOR → EVR → Internet Fallback', 'VOR → EVR → Internet Fallback', 'VOR → EVR → Debate → Internet Fallback']
    }
    df2 = pd.DataFrame(table2_data)
    html_content += "<caption>TABLE II: ESCALATION WORKFLOWS ACROSS SYSTEM CONFIGURATIONS</caption>"
    html_content += df2.to_html(index=False)
    
    # Table III: Baseline Performance Comparison
    table3_data = {
        'Metric': ['Avg F1-Score', 'F1=1.0 Retrieval', 'Success Rate', 'Failed Retrieval'],
        'Legacy': ['0.327', '16 (32.7%)', '34.0%', '33 (66.0%)'],
        'Enhanced': ['0.468', '18 (36.7%)', '62.0%', '19 (38.0%)'],
        'Improvement': ['+43.1%', '+12.5%', '+82.5%', '-42.4%']
    }
    df3 = pd.DataFrame(table3_data)
    html_content += "<caption>TABLE III: BASELINE PERFORMANCE COMPARISON BASED ON DATASETS QUALITY</caption>"
    html_content += df3.to_html(index=False)
    
    # Table IV: Overall System Retrieval Performance
    table4_data = {
        'Metric': ['Avg F1-Score', 'F1=1.0 Retrieval', 'Success Rate', 'Failed Retrieval', 'Avg.Time (s)'],
        'Legacy': ['0.327', '16 (32.7%)', '34.0%', '33 (66.0%)', '14.5696'],
        'Enhanced': ['0.468', '18 (36.7%)', '62.0%', '19 (38.0%)', '11.0838'],
        'MAF-RAG': ['0.556', '19 (39.8%)', '78.0%', '11 (22.0%)', '11.6270'],
        'Δ (MAF vs Enhanced)': ['+18.8%', '+5.4%', '+26%', '-42.1%', '+4.9%']
    }
    df4 = pd.DataFrame(table4_data)
    html_content += "<caption>TABLE IV: OVERALL SYSTEM RETRIEVAL PERFORMANCE COMPARISON</caption>"
    html_content += df4.to_html(index=False)
    
    # Table V: Phase Utilization
    table5_data = {
        'Retrieval Phase': ['EVR', 'VOR', 'MAF-RAG', 'Internet Fallback'],
        'Legacy': ['20.0%', '14.0%', 'N/A', '66.0%'],
        'Enhanced': ['14.0%', '30.0%', 'N/A', '38.0%'],
        'MAF-RAG': ['38.0%', '30.0%', '30.0%', '2%']
    }
    df5 = pd.DataFrame(table5_data)
    html_content += "<caption>TABLE V: PHASE UTILIZATION ACROSS ALL THREE SYSTEM</caption>"
    html_content += df5.to_html(index=False)
    
    # Table VI: MAF-RAG Internal Phase Performance
    table6_data = {
        'Retrieval Phase': ['EVR', 'VOR', 'MAF-RAG'],
        'Queries': ['19', '15', '16'],
        '% of Total': ['38.0%', '30.0%', '32.0%'],
        'Mean F1': ['0.737', '0.627', '0.275'],
        'F1 = 1.0': ['11', '6', '2'],
        'Success Rate': ['89.5%', '93.3%', '50.0%'],
        'Failed Rate': ['2', '1', '8']
    }
    df6 = pd.DataFrame(table6_data)
    html_content += "<caption>TABLE VI: MAF-RAG INTERNAL PHASE PERFORMANCE</caption>"
    html_content += df6.to_html(index=False)
    
    # Table VII: Failure Analysis
    table7_data = {
        'Category': ['Procedure', 'Licensing', 'General'],
        'Failures': ['7', '3', '1'],
        '% of Total Failures': ['63.6%', '27.3%', '9.1%'],
        'Failure Rate within Category': ['29.2% (7/24)', '60.0% (3/5)', '14.3% (1/7)'],
        'Primary Cause': ['Multi-step synthesis complexity', 'Ambiguous regulatory definitions', 'Specific administrative entity lookup']
    }
    df7 = pd.DataFrame(table7_data)
    html_content += "<caption>TABLE VII: FAILURE ANALYSIS BY SEMANTIC CATEGORY</caption>"
    html_content += df7.to_html(index=False)
    
    html_content += "</body></html>"
    
    with open(os.path.join(OUTPUT_DIR, 'manuscript_tables.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved {os.path.join(OUTPUT_DIR, 'manuscript_tables.html')}")

if __name__ == "__main__":
    generate_html_tables()
