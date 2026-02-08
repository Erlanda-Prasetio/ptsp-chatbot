from graphviz import Digraph
import os

OUTPUT_DIR = r"d:\backup\ptspRag\revision\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_fig1():
    dot = Digraph('Figure1', comment='Cosine Similarity Pipeline')
    dot.attr(rankdir='LR', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
    
    dot.node('Q', 'User Query')
    dot.node('D', 'Documents')
    dot.node('C', 'Chunking')
    dot.node('E1', 'Encoder\n(all-MiniLM-L6-v2)')
    dot.node('E2', 'Encoder\n(all-MiniLM-L6-v2)')
    dot.node('QV', 'Query Vector\n(384-d)')
    dot.node('DV', 'Doc Vectors\n(384-d)')
    dot.node('CS', 'Cosine Similarity\nComputation')
    dot.node('S', 'Similarity Scores')
    dot.node('R', 'Ranked Results\n(Confidence Score)')
    
    dot.edge('Q', 'E1')
    dot.edge('E1', 'QV')
    
    dot.edge('D', 'C')
    dot.edge('C', 'E2')
    dot.edge('E2', 'DV')
    
    dot.edge('QV', 'CS')
    dot.edge('DV', 'CS')
    dot.edge('CS', 'S')
    dot.edge('S', 'R')
    
    output_path = os.path.join(OUTPUT_DIR, 'Figure_1_Cosine_Pipeline')
    dot.render(output_path, format='png', cleanup=True)
    print(f"Saved {output_path}.png")

def create_fig2():
    dot = Digraph('Figure2', comment='MAF-RAG Pipeline')
    dot.attr(rankdir='TB', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='white')
    
    dot.node('Start', 'User Query', shape='ellipse', fillcolor='#e1f5fe')
    
    # Phase 1: VOR
    with dot.subgraph(name='cluster_0') as c:
        c.attr(label='Phase 1: Vector-Only Retrieval (VOR)', style='dashed')
        c.node('VOR', 'VOR Retrieval\n(k=12)')
        c.node('Check1', 'Confidence >= 0.75?', shape='diamond', fillcolor='#fff9c4')
    
    # Phase 2: EVR
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='Phase 2: Enhanced Vector Retrieval (EVR)', style='dashed')
        c.node('EVR', 'EVR Retrieval\n(k=24, Hybrid)', fillcolor='#fff3e0')
        c.node('Check2', 'Confidence >= 0.60?', shape='diamond', fillcolor='#fff9c4')
        
    # Phase 3: MAF-RAG
    with dot.subgraph(name='cluster_2') as c:
        c.attr(label='Phase 3: Multi-Agent Fallback (MAF-RAG)', style='dashed')
        c.node('Debate', 'Multi-Agent Debate\n(3 Rounds)', fillcolor='#e1bee7')
        c.node('Check3', 'Consensus Reached?', shape='diamond', fillcolor='#fff9c4')
        
    # Phase 4: Internet
    dot.node('Internet', 'Internet Fallback', fillcolor='#ffcdd2')
    dot.node('End', 'Final Response', shape='ellipse', fillcolor='#c8e6c9')
    
    # Edges
    dot.edge('Start', 'VOR')
    dot.edge('VOR', 'Check1')
    dot.edge('Check1', 'End', label='Yes')
    dot.edge('Check1', 'EVR', label='No')
    
    dot.edge('EVR', 'Check2')
    dot.edge('Check2', 'End', label='Yes')
    dot.edge('Check2', 'Debate', label='No')
    
    dot.edge('Debate', 'Check3')
    dot.edge('Check3', 'End', label='Yes')
    dot.edge('Check3', 'Internet', label='No')
    
    dot.edge('Internet', 'End')
    
    output_path = os.path.join(OUTPUT_DIR, 'Figure_2_Escalation_Pipeline')
    dot.render(output_path, format='png', cleanup=True)
    print(f"Saved {output_path}.png")

def create_fig3():
    dot = Digraph('Figure3', comment='Debate Architecture')
    dot.attr(rankdir='TB', dpi='300')
    
    dot.node('Input', 'Query + Top-4 Docs', shape='box')
    
    with dot.subgraph(name='cluster_agents') as c:
        c.attr(label='Debate Round t', color='blue')
        c.node('A1', 'Agent 1\n(Doc 1)', shape='component')
        c.node('A2', 'Agent 2\n(Doc 2)', shape='component')
        c.node('A3', 'Agent 3\n(Doc 3)', shape='component')
        c.node('A4', 'Agent 4\n(Doc 4)', shape='component')
        
    dot.node('Agg', 'Aggregator Agent\n(Synthesize & Check)', shape='hexagon', fillcolor='gold', style='filled')
    dot.node('Check', 'Converged?', shape='diamond')
    dot.node('Output', 'Final Answer', shape='ellipse')
    
    dot.edge('Input', 'A1')
    dot.edge('Input', 'A2')
    dot.edge('Input', 'A3')
    dot.edge('Input', 'A4')
    
    dot.edge('A1', 'Agg')
    dot.edge('A2', 'Agg')
    dot.edge('A3', 'Agg')
    dot.edge('A4', 'Agg')
    
    dot.edge('Agg', 'Check')
    dot.edge('Check', 'Output', label='Yes')
    dot.edge('Check', 'A1', label='No (Feedback)', style='dashed')
    dot.edge('Check', 'A2', label='No (Feedback)', style='dashed')
    
    output_path = os.path.join(OUTPUT_DIR, 'Figure_3_Debate_Architecture')
    dot.render(output_path, format='png', cleanup=True)
    print(f"Saved {output_path}.png")

if __name__ == "__main__":
    try:
        create_fig1()
        create_fig2()
        create_fig3()
        print("All diagrams generated in d:\\backup\\ptspRag\\revision\\figures")
    except Exception as e:
        print(f"Error: {e}")
        print("Ensure Graphviz is installed and in your PATH.")
