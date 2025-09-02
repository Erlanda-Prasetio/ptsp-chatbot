"""Test the smart enhanced RAG system with better domain detection"""
from src.smart_enhanced_rag import SmartEnhancedRAG

rag = SmartEnhancedRAG()

# Test relevant queries
relevant_queries = [
    'apa itu dpmptsp',
    'bagaimana cara mengurus izin usaha',
    'syarat investasi di jawa tengah',
    'prosedur perizinan online'
]

print("🔍 Testing RELEVANT queries:")
for query in relevant_queries:
    print(f'\n📝 Query: {query}')
    result = rag.ask(query)
    print(f'✅ Domain relevant: {result["enhanced_features"]["domain_relevant"]}')
    print(f'🎯 Confidence: {result["enhanced_features"]["confidence"]}')
    print(f'⏱️  Response time: {result["enhanced_features"]["response_time"]}')
    print(f'📄 Sources: {len(result["sources"])}')
    print(f'💬 Answer preview: {result["answer"][:150]}...')

print("\n" + "="*60)

# Test irrelevant queries
irrelevant_queries = [
    'what is the weather today',
    'bitcoin price',
    'how to make pizza',
    'latest news'
]

print("🔍 Testing IRRELEVANT queries:")
for query in irrelevant_queries:
    print(f'\n📝 Query: {query}')
    result = rag.ask(query)
    print(f'❌ Domain relevant: {result["enhanced_features"]["domain_relevant"]}')
    print(f'🎯 Confidence: {result["enhanced_features"]["confidence"]}')
    print(f'⏱️  Response time: {result["enhanced_features"]["response_time"]}')
    print(f'📄 Sources: {len(result["sources"])}')
    if 'reason' in result["enhanced_features"]:
        print(f'🔍 Reason: {result["enhanced_features"]["reason"]}')
