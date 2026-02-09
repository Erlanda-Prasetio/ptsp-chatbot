import argparse
import os
import re
import json
import time
import logging
import torch
import string
from datetime import datetime
from tqdm import tqdm
from typing import List
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, set_seed

# Setup logging for MADAM debate process
def setup_madam_logger():
    """Configure logging for MADAM debate tracking."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"madam_debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logger = logging.getLogger("madam_debate")
    logger.setLevel(logging.DEBUG)
    
    # File handler - UTF-8 for full Unicode support
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler - ASCII only to avoid Windows encoding issues
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter for file (with emojis)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formatter for console (plain ASCII, no emojis)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_file

logger, log_file = setup_madam_logger()

def normalize_answer(s: str) -> str:
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)
    def white_space_fix(text):
        return ' '.join(text.split())
    def remove_punc(text):
        return ''.join(ch for ch in text if ch not in string.punctuation)
    def lower(text):
        return text.lower()
    return white_space_fix(remove_articles(remove_punc(lower(s))))

def call_llm(prompt: str, generator, max_new_tokens: int = 128) -> str:
    messages = [{"role": "user", "content": prompt}]
    output = generator(
                messages,
                max_new_tokens=max_new_tokens,
                top_p=None,
                do_sample=False)
    return output[0]["generated_text"][-1]['content'].strip()


def agent_response(query: str, document: str, generator, history: str = ""):
    if history:
        prompt = f"""You are an agent reading a document to answer a question.

Question: {query}
Document: {document}

The following reponses are from other agents as additional information.
{history}
Answer the question based on the document and other agents' response. Provide your answer and a step-by-step reasoning explanation.  
Please follow the format: 'Answer: {{}}. Explanation: {{}}.''"""
    else:
        prompt = f"""You are an agent reading a document to answer a question.

Question: {query}
Document: {document}

Answer the question based only on this document. Provide your answer and a step-by-step reasoning explanation.
Please follow the format: 'Answer: {{}}. Explanation: {{}}.''"""

    output = call_llm(prompt, generator)
    return output


def aggregate_responses(query: str, responses: List[str], generator):
    joined = "\n".join([f"Agent {i+1}: {r}" for i, r in enumerate(responses)])
    prompt = f"""You are an aggregator reading answers from multiple agents.

If there are multiple answers, please provide all possible correct answers and also provide a step-by-step reasoning explanation. If there is no correct answer, please reply 'unknown'.
Please follow the format: 'All Correct Answers: []. Explanation: {{}}.'

The following are examples:
Question: In which year was Michael Jordan born?
Agent responses:
Agent 1: Answer: 1963. Explanation: The document clearly states that Michael Jeffrey Jordan was born on February 17, 1963. 
Agent 2: Answer: 1956. Explanation: The document states that Michael Irwin Jordan was born on February 25, 1956. However, it's important to note that this document seems to be about a different Michael Jordan, who is an American scientist, not the basketball player. The other agents' responses do not align with the information provided in the document.
Agent 3: Answer: 1998. Explanation: The According to the document provided, Michael Jeffrey Jordan was born on February 17, 1998.
Agent 4: Answer: Unknown. Explanation: The provided document focuses on Jordan's college and early professional career, mentioning his college championship in 1982 and his entry into the NBA in 1984, but it does not include information about his birth year.
All Correct Answers: ["1963", "1956"]. Explanation: Agent 1 is talking about the basketball player Michael Jeffrey Jordan, who was born on Februray 17, 1963, so 1963 is correct. Agent 2 is talking about another person named Michael Jordan, who is an American scientist, and he was born in 1956. Therefore, the answer 1956 from Agent 2 is also correct. Agent 3 provides an error stating Michael Jordan's birth year as 1998, which is incorrect. Based on the correct information from Agent 1, Michael Jeffrey Jordan was born on February 17, 1963. Agent 4 does not provide any useful information.

Question: {query}
Agent responses:
{joined}
"""
    return call_llm(prompt, generator)


def multi_agent_debate(query: str, documents: List[str], generator, num_rounds: int = 3):
    """Multi-agent debate with comprehensive logging."""
    if documents is None:
        logger.error("Received None for documents")
        return {}
    if query is None:
        query = "Unknown Query"
        
    records = {}
    num_agents = len(documents)
    agent_outputs = []
    
    debate_start_time = time.time()
    logger.info("="*80)
    logger.info("MADAM DEBATE STARTED")
    logger.info(f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}")
    logger.info(f"Agents: {num_agents}, Rounds: {num_rounds}")
    logger.info(f"Documents: {len(documents)} available")
    logger.info("="*80)

    # Round 1
    records["round1"] = {"answers": [], "explanations": []}
    logger.info(f"\nROUND 1 - Initial Agent Responses")
    logger.info(f"{''*80}")
    
    round1_start = time.time()
    for i, doc in enumerate(documents):
        if doc is None:
            doc = ""
            
        agent_start = time.time()
        logger.info(f"\n  Agent {i+1}/{num_agents}")
        logger.info(f"     Document: {doc[:80]}..." if len(doc) > 80 else f"     Document: {doc}")
        
        response = agent_response(query, doc, generator) or "Unknown response"
        agent_elapsed = time.time() - agent_start
        
        answer = response[response.find("Answer: ") + len("Answer: "):response.find("Explanation")].strip()
        explanation = response[response.find("Explanation: ") + len("Explanation: "):]
        
        records["round1"]["answers"].append(answer)
        records["round1"]["explanations"].append(explanation)
        agent_outputs.append(response)
        
        logger.info(f"     [OK] Agent response received ({agent_elapsed:.2f}s)")
        logger.info(f"     Answer: {answer[:100]}..." if len(answer) > 100 else f"     Answer: {answer}")
        
        # Rate limit protection removed for timing evaluation
        # if i < len(documents) - 1:
        #     logger.info(f"     [WAIT] 8s gap between agents...")
        #     time.sleep(8)
    
    # Aggregation for Round 1
    logger.info(f"\n  Round 1 Aggregation")
    agg_start = time.time()
    # logger.info(f"     [WAIT] 5s gap before aggregation...")
    # time.sleep(5)
    
    logger.info(f"     [WORK] Aggregating {len(agent_outputs)} agent responses...")
    records["round1"]["aggregation"] = aggregate_responses(query, agent_outputs, generator)
    agg_elapsed = time.time() - agg_start
    
    logger.info(f"     [OK] Aggregation complete ({agg_elapsed:.2f}s)")
    logger.info(f"     Aggregated: {records['round1']['aggregation'][:150]}..." if len(records['round1']['aggregation']) > 150 else f"     Aggregated: {records['round1']['aggregation']}")
    
    round1_elapsed = time.time() - round1_start
    logger.info(f"\n  Round 1 Total Time: {round1_elapsed:.2f}s")
    
    # Initialize final_aggregation with Round 1 result in case strict loop condition met or num_rounds=1
    final_aggregation = records['round1']['aggregation']

    # Additional rounds with convergence checking
    for t in range(1, num_rounds):
        round_key = f"round{t+1}"
        logger.info(f"\n{round_key.upper()} - Iterative Refinement")
        logger.info(f"{''*80}")
        
        records[round_key] = {"answers": [], "explanations": []}
        new_outputs = []
        
        # 10s gap removed for timing evaluation
        # logger.info(f"  [WAIT] 10s gap before {round_key}...")
        # time.sleep(10)
        
        round_start = time.time()
        for i, doc in enumerate(documents):
            agent_start = time.time()
            logger.info(f"\n  Agent {i+1}/{num_agents}")
            
            history = "\n".join([f"Agent {j+1}: {agent_outputs[j]}" for j in range(num_agents) if j != i])
            response = agent_response(query, doc, generator, history)
            agent_elapsed = time.time() - agent_start
            
            answer = response[response.find("Answer: ") + len("Answer: "):response.find("Explanation")].strip()
            explanation = response[response.find("Explanation: ") + len("Explanation: "):]
            
            records[round_key]["answers"].append(answer)
            records[round_key]["explanations"].append(explanation)
            new_outputs.append(response)
            
            logger.info(f"     [OK] Agent response received ({agent_elapsed:.2f}s)")
            logger.info(f"     Answer: {answer[:100]}..." if len(answer) > 100 else f"     Answer: {answer}")
            
            # 8s gap removed for timing evaluation
            # if i < len(documents) - 1:
            #     logger.info(f"     [WAIT] 8s gap between agents...")
            #     time.sleep(8)
        
        agent_outputs = new_outputs
        
        # Check convergence
        pred_ans_list = []
        for ans in records[round_key]["answers"]:
            pred_ans_list.append(normalize_answer(ans))
        prev_pred_ans_list = []
        for ans in records[f"round{t}"]["answers"]:
            prev_pred_ans_list.append(normalize_answer(ans))
        
        assert len(pred_ans_list) == len(prev_pred_ans_list)
        
        flag = True
        for k in range(len(pred_ans_list)):
            if pred_ans_list[k] in prev_pred_ans_list[k] or prev_pred_ans_list[k] in pred_ans_list[k]:
                continue
            else:
                flag = False
        
        logger.info(f"\n  {round_key.upper()} Aggregation")
        agg_start = time.time()
        # logger.info(f"     [WAIT] 5s gap before aggregation...")
        # time.sleep(5)
        
        logger.info(f"     [WORK] Aggregating {len(new_outputs)} agent responses...")
        records[round_key]["aggregation"] = aggregate_responses(query, agent_outputs, generator)
        agg_elapsed = time.time() - agg_start
        
        logger.info(f"     [OK] Aggregation complete ({agg_elapsed:.2f}s)")
        logger.info(f"     Aggregated: {records[round_key]['aggregation'][:150]}..." if len(records[round_key]['aggregation']) > 150 else f"     Aggregated: {records[round_key]['aggregation']}")
        
        round_elapsed = time.time() - round_start
        logger.info(f"\n  {round_key.upper()} Total Time: {round_elapsed:.2f}s")
        
        # Convergence check logging
        if flag:
            logger.info(f"\n[OK] CONVERGENCE DETECTED - Answers consistent with previous round")
            final_aggregation = records[f"round{t}"]["aggregation"]
            break
        else:
            logger.info(f"\n[WARN] NO CONVERGENCE - Continuing to next round")
            final_aggregation = records[round_key]["aggregation"]

    records["final_aggregation"] = final_aggregation
    
    # Summary logging
    debate_elapsed = time.time() - debate_start_time
    logger.info(f"\n{'='*80}")
    logger.info(f"[DONE] MADAM DEBATE COMPLETED")
    logger.info(f"Time: {debate_elapsed:.2f}s ({debate_elapsed/60:.1f} minutes)")
    if final_aggregation:
        logger.info(f"Final Answer: {final_aggregation[:200]}..." if len(final_aggregation) > 200 else f"Final Answer: {final_aggregation}")
    else:
        logger.info("Final Answer: None/Empty (Debate Failed to Aggregate)")
    logger.info(f"{'='*80}\n")
    
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--cache_dir", type=str, default="./cache")
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--num_rounds", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    hf_token = os.getenv('HF_TOKEN', None)
    args.output_path = f"{args.data_path}_madam_rag_{args.model_name.split('/')[-1]}_rounds{args.num_rounds}.jsonl"

    set_seed(42)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        cache_dir=args.cache_dir,
        token=hf_token,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, cache_dir=args.cache_dir, token=hf_token)
    tokenizer.pad_token_id = tokenizer.eos_token_id
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, trust_remote_code=True, device_map="auto")

    with open(args.data_path, "r") as f:
        all_data = [json.loads(line.strip()) for line in f]

    results = []
    for i in tqdm(range(len(all_data)), desc="Running MADAM-RAG"):
        entry = all_data[i]
        documents = [doc["text"] for doc in entry["documents"]]
        result = multi_agent_debate(entry["question"], documents, generator, num_rounds=args.num_rounds)
        results.append(result)

    with open(args.output_path, "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")

if __name__ == "__main__":
    main()