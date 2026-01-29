# API Cost Analysis

## Overview
This document provides a detailed cost comparison between AI-BDD and the NETS database, with transparent unit costs for each API used in the pipeline.

## Cost Comparison Summary

| Data Source | Annual Cost | Update Frequency | Data Quality | Coverage |
|------------|-------------|------------------|--------------|----------|
| NETS Database | $50,000+ | Annual | 67% imputed | National (US) |
| AI-BDD | <$5,000 | On-demand | Direct observation | Configurable |
| Savings | >90% | - | - | - |

## AI-BDD Cost Components

### 1. Google Maps API

**Places Text Search**
- Unit cost: $0.032 per query
- Typical use: 9 ZIP codes × 1 category = 9 queries
- Cost per category: $0.288

**Place Details**
- Unit cost: $0.017 per place
- Typical use: 100 places (after deduplication)
- Cost per category: $1.70

**Data Returned**
- Address, phone, website
- Ratings, review counts, review text
- Operating hours
- Coordinates

**Subtotal per category**: $1.99

### 2. OpenAI GPT-4o-mini API

**Pricing**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Per business (3 calls)**
- Status classification
- Employment estimation
- NAICS verification

**Estimated cost per business**: $0.00048

**100 businesses**: $0.048

### 3. Wayback Machine API
- Cost: $0.00 (public service)
- Used for historical validation

## Example Costs

### Minneapolis (Single Category)
- Google Maps: $1.99
- GPT-4o-mini: $0.05
- Wayback: $0.00
- Total: $2.04

### Minneapolis (All 7 Categories)
- Estimated places: ~690
- Total: ~$15

### 10 Cities × 7 Categories
- Estimated places: ~6,900
- Total: ~$150 per collection cycle

## NETS vs AI-BDD

**NETS**
- High annual subscription cost
- 24-month closure detection lag
- 67% imputed employment data

**AI-BDD**
- Low per-run cost
- Near real-time updates
- Fully traceable raw data

## Cost Optimization Strategies

1. **Stage execution**
   - Run Google Maps only
   - Add Wayback validation
   - Run GPT analysis only for high-value records

2. **Limit processing**
   - Use `--limit` for testing
   - Target specific ZIP codes

3. **Batch scheduling**
   - Monthly or quarterly runs to balance cost and timeliness

## References
- Crane & Decker (2019): NETS imputation and closure lag critique
- OpenAI pricing: https://platform.openai.com/pricing
- Google Maps pricing: https://developers.google.com/maps/billing-and-pricing
