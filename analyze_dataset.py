import json
import sys

def analyze_dataset():
    try:
        with open('d:/backup/ptspRag/data/default_docs_meta.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = data.get('texts', [])
        print(f"Total chunks: {len(texts)}")
        
        # Analyze source distribution
        sources = {}
        for text in texts:
            lines = text.split('\n')
            source_line = next((line for line in lines if line.startswith('Source:')), None)
            if source_line:
                source = source_line.replace('Source: ', '').strip()
                sources[source] = sources.get(source, 0) + 1
        
        print(f"\nTotal unique sources: {len(sources)}")
        print(f"Top 10 sources by chunk count:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {source}: {count} chunks")
        
        # Check for recent years in sources
        recent_sources = 0
        old_sources = 0
        for source in sources.keys():
            if any(year in source for year in ['2023', '2024', '2025']):
                recent_sources += 1
            elif any(year in source for year in ['2017', '2018', '2019', '2020']):
                old_sources += 1
        
        print(f"\nSources from 2017-2020: {old_sources}")
        print(f"Sources from 2023-2025: {recent_sources}")
        
        # Sample a few chunks to see content quality
        print(f"\nSample chunks (first 3):")
        for i, text in enumerate(texts[:3]):
            lines = text.split('\n')
            source_line = next((line for line in lines if line.startswith('Source:')), "No source")
            content_preview = ' '.join(lines[4:6])[:200] + "..."
            print(f"\n{i+1}. {source_line}")
            print(f"   Content: {content_preview}")
        
    except Exception as e:
        print(f"Error analyzing dataset: {e}")

if __name__ == "__main__":
    analyze_dataset()