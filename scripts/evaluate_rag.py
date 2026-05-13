#!/usr/bin/env python3
"""
RAG Retrieval Evaluation Script.
Runs benchmark questions against ChromaDB and calculates Hit@1, Hit@3, MRR.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import csv
from pathlib import Path
from engine.rag_retriever import RAGRetriever

# Benchmark questions with ground truth keywords
BENCHMARK = [
    {
        "question": "What is float in insurance?",
        "keywords": ["float", "money", "insurance", "premiums"],
        "expected_source": "buffett_wisdom_compilation.txt or 1992_letter.txt"
    },
    {
        "question": "Why did Buffett invest heavily in Coca-Cola?",
        "keywords": ["Coca-Cola", "brand", "distribution", "pricing"],
        "expected_source": "buffett_wisdom_compilation.txt"
    },
    {
        "question": "What is Buffett's circle of competence?",
        "keywords": ["circle of competence", "too hard pile"],
        "expected_source": "buffett_wisdom_compilation.txt"
    },
    {
        "question": "What is an economic moat?",
        "keywords": ["moat", "competitive advantage", "brand"],
        "expected_source": "buffett_wisdom_compilation.txt"
    },
    {
        "question": "What was Buffett's response to the 2008 financial crisis?",
        "keywords": ["Buy American", "Goldman Sachs", "crisis", "2008"],
        "expected_source": "missing_years_highlights.txt"
    },
    {
        "question": "Why did Buffett invest in Apple?",
        "keywords": ["Apple", "consumer products", "ecosystem", "Tim Cook"],
        "expected_source": "missing_years_highlights.txt"
    },
    {
        "question": "What is Buffett's advice for ordinary investors?",
        "keywords": ["S&P 500", "index fund", "low-cost"],
        "expected_source": "buffett_wisdom_compilation.txt"
    },
    {
        "question": "Why did Berkshire's textile business fail?",
        "keywords": ["textile", "terrible economics", "competition"],
        "expected_source": "1977_letter.txt or 1978_letter.txt"
    },
    {
        "question": "What makes a good manager according to Buffett?",
        "keywords": ["love the business", "owners", "integrity"],
        "expected_source": "buffett_wisdom_compilation.txt"
    },
    {
        "question": "How does Buffett view inflation?",
        "keywords": ["inflation", "pricing power", "tax"],
        "expected_source": "buffett_wisdom_compilation.txt"
    }
]

def evaluate_retrieval(db_path: str = "./chroma_data", collection_name: str = "buffett_letters"):
    retriever = RAGRetriever(db_path, collection_name)
    
    results = []
    hit_1 = 0
    hit_3 = 0
    reciprocal_ranks = []
    
    for i, item in enumerate(BENCHMARK):
        query = item["question"]
        keywords = item["keywords"]
        
        # Get Top-5 results
        top_5_text = retriever.retrieve(query, top_k=5)
        # Split by separator to get individual chunks
        chunks = top_5_text.split("\n\n---\n\n") if top_5_text else []
        
        # Check hits
        rank_hit = None
        for rank_idx, chunk in enumerate(chunks[:5]):
            chunk_lower = chunk.lower()
            if any(kw.lower() in chunk_lower for kw in keywords):
                rank_hit = rank_idx + 1  # 1-based rank
                break
        
        is_hit_1 = rank_hit == 1
        is_hit_3 = rank_hit is not None and rank_hit <= 3
        
        if is_hit_1: hit_1 += 1
        if is_hit_3: hit_3 += 1
        if rank_hit: reciprocal_ranks.append(1.0 / rank_hit)
        
        results.append({
            "#": i + 1,
            "Question": query,
            "Expected Source": item["expected_source"],
            "Rank Hit": rank_hit if rank_hit else "Miss",
            "Hit@1": "✅" if is_hit_1 else "❌",
            "Hit@3": "✅" if is_hit_3 else "❌"
        })
    
    # Print results table
    print(f"{'#':<3} {'Question':<45} {'Rank':<6} {'Hit@1':<6} {'Hit@3':<6}")
    print("-" * 70)
    for r in results:
        print(f"{r['#']:<3} {r['Question']:<45} {str(r['Rank Hit']):<6} {r['Hit@1']:<6} {r['Hit@3']:<6}")
    
    # Print metrics
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
    hit_1_rate = hit_1 / len(BENCHMARK) * 100
    hit_3_rate = hit_3 / len(BENCHMARK) * 100
    
    print("-" * 70)
    print(f"📊 Metrics:")
    print(f"   Hit@1: {hit_1_rate:.1f}% ({hit_1}/{len(BENCHMARK)}) [Target: >60%]")
    print(f"   Hit@3: {hit_3_rate:.1f}% ({hit_3}/{len(BENCHMARK)}) [Target: >80%]")
    print(f"   MRR:   {mrr:.3f} [Target: >0.5]")
    
    # Save to CSV
    output_path = Path("evaluation_results.csv")
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"💾 Results saved to: {output_path}")
    return hit_1_rate, hit_3_rate, mrr

if __name__ == "__main__":
    evaluate_retrieval()
