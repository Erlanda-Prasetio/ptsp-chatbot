"""Test how the RAG system handles irrelevant queries"""
from src.enhanced_rag import EnhancedRAG

rag = EnhancedRAG()

test_queries = [
    'what is the weather today',
    'latest news about Indonesia', 
    'covid-19 statistics 2024',
    'how to make pizza',
    'bitcoin price today'
]

for query in test_queries:
    print(f'\n🔍 Query: {query}')
    result = rag.ask(query)
    answer = result['answer']
    print(f'Answer: {answer[:150]}...')
    print(f'Sources found: {len(result.get("sources", []))}')
