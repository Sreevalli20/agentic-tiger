# GraphProbe AI Demo Questions

These questions are answerable from the 40-document production corpus (`backend/corpus_production.jsonl`).

## Olympic Question (Primary Demo)
**Question:** "Who won the gold medal in the men's 20 kilometres walk athletics event at the Summer Olympics held immediately before 2016?"

**Expected Answer:** Chen Ding (China)

**Source Document:** Athletics at the 2012 Summer Olympics – Men's 20 kilometres walk

**Evidence:** The 2012 Summer Olympics (immediately before 2016) men's 20km walk gold medalist was Chen Ding from China.

## Additional Demo Questions

### Question A — Direct Factual Retrieval
**Question:** "Who won the gold medal in the women's road time trial at the 2012 Summer Olympics?"

**Expected Answer:** Kristin Armstrong (USA)

**Source Document:** Cycling at the 2012 Summer Olympics – Women's road time trial

### Question B — Entity Relationship  
**Question:** "Which country won the gold medal in men's K-2 1000 metres canoeing at the 2012 Summer Olympics?"

**Expected Answer:** Hungary (Rudolf Dombi and Roland Kökény)

**Source Document:** Canoeing at the 2012 Summer Olympics – Men's K-2 1000 metres

### Question C — Multi-hop Investigation
**Question:** "Who won the gold medal in the men's 110 metres hurdles at the 2008 Summer Olympics, and what was their winning time?"

**Expected Answer:** Dayron Robles (Cuba) with a time of 12.93 seconds

**Source Document:** Athletics at the 2008 Summer Olympics – Men's 110 metres hurdles

### Question D — Verification
**Question:** "Did the United States win any medals in the men's 400 metres hurdles at the 2004 Summer Olympics?"

**Expected Answer:** No - the United States did not win any medals in this event (the streak ended)

**Source Document:** Athletics at the 2004 Summer Olympics – Men's 400 metres hurdles

## Performance Characteristics

All questions should complete within the new timeout bounds:
- **Agentic timeout:** 20 seconds maximum
- **Frontend timeout:** 30 seconds maximum  
- **Maximum iterations:** 3
- **Expected completion time:** 3-8 seconds for simple questions

The Olympic question was tested and completed successfully in 4.2 seconds with 3 iterations.