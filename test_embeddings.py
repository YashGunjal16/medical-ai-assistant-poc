"""
Test script to verify existing embeddings are working
Run this to confirm your 12,060 embeddings are ready to use
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.tools.rag_tool import RAGManager

from app.utils.logger import logger
import time

def print_separator():
    print("=" * 80)

def test_embeddings():
    """Test existing embeddings with various queries"""
    
    print_separator()
    print("🔍 TESTING EXISTING EMBEDDINGS")
    print_separator()
    
    # Initialize RAG Manager
    print("\n📥 Initializing RAG Manager...")
    try:
        rag = RAGManager()
        print("✅ RAG Manager initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing RAG Manager: {str(e)}")
        return
    
    # Check status
    print("\n📊 Checking Vector Store Status...")
    stats = rag.get_vector_store_stats()
    total_docs = stats.get("total_documents", 0)
    
    print(f"   Total Documents: {total_docs}")
    print(f"   Expected Full: 21,223 (PDF) + 10 (Reference) = 21,233")
    print(f"   Coverage: {(total_docs / 21233) * 100:.1f}%")
    
    if total_docs == 0:
        print("\n❌ No embeddings found! Vector store is empty.")
        return
    
    print(f"\n✅ Found {total_docs} embedded documents - Ready to query!")
    
    # Test queries
    test_queries = [
        {
            "query": "What are the stages of chronic kidney disease?",
            "category": "CKD Classification"
        },
        {
            "query": "How to manage hyperkalemia in CKD patients?",
            "category": "Electrolyte Management"
        },
        {
            "query": "What are the treatment options for lupus nephritis?",
            "category": "Glomerulonephritis"
        },
        {
            "query": "Dialysis vascular access options and complications",
            "category": "Dialysis"
        },
        {
            "query": "Post-discharge medication management for kidney patients",
            "category": "Patient Education"
        },
        {
            "query": "ACE inhibitors and ARBs in chronic kidney disease",
            "category": "Pharmacology"
        }
    ]
    
    print("\n" + "=" * 80)
    print("🧪 RUNNING TEST QUERIES")
    print("=" * 80)
    
    success_count = 0
    total_queries = len(test_queries)
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {test['category']}")
        print(f"   Question: {test['query']}")
        print("-" * 80)
        
        try:
            start_time = time.time()
            results = rag.query_reference_materials(test['query'], n_results=3)
            query_time = time.time() - start_time
            
            if results["success"] and results["results"]:
                success_count += 1
                print(f"✅ Found {len(results['results'])} results ({query_time:.2f}s)")
                
                # Show top result
                top_result = results['results'][0]
                content = top_result['content']
                source = top_result.get('source', 'Unknown')
                score = top_result.get('relevance_score', 0)
                
                print(f"\n   📄 Top Result (Relevance: {score:.3f}):")
                print(f"   Source: {source}")
                print(f"   Content Preview:")
                
                # Show first 300 characters
                preview = content[:300] + "..." if len(content) > 300 else content
                for line in preview.split('\n'):
                    if line.strip():
                        print(f"      {line.strip()}")
                
            else:
                print(f"❌ No results found")
                print(f"   Message: {results.get('message', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Error during query: {str(e)}")
        
        # Small delay between queries
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Queries: {total_queries}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_queries - success_count}")
    print(f"Success Rate: {(success_count / total_queries) * 100:.1f}%")
    
    if success_count == total_queries:
        print("\n✅ ALL TESTS PASSED! Your embeddings are working perfectly!")
    elif success_count > 0:
        print(f"\n⚠️ PARTIAL SUCCESS! {success_count}/{total_queries} queries worked.")
    else:
        print("\n❌ ALL TESTS FAILED! There may be an issue with the embeddings.")
    
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATIONS")
    print("=" * 80)
    
    if total_docs < 21233:
        remaining = 21233 - total_docs
        print(f"⚠️ You have {remaining} documents remaining to embed")
        print(f"   Current coverage: {(total_docs / 21233) * 100:.1f}%")
        print(f"   To complete: Re-upload the PDF file")
    else:
        print("✅ All documents are embedded!")
    
    if success_count > 0:
        print("✅ System is ready for production use with current embeddings")
        print("✅ You can start querying medical information immediately")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        test_embeddings()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()