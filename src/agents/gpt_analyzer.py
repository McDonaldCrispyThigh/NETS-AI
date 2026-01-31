"""
GPT-4o-mini Business Status Classifier
Analyzes business data to determine status, employment, and reliability
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class GPTAnalyzer:
 """
 Uses GPT-4o-mini to analyze business data and make intelligent classifications
 """
 
 def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
 api_key = os.getenv("OPENAI_API_KEY")
 if not api_key:
 raise ValueError("OPENAI_API_KEY not found in environment variables")
 
 self.client = OpenAI(api_key=api_key)
 self.model = model
 self.temperature = temperature
 
 def classify_business_status(self, business_data: Dict) -> Dict:
 """
 Classify if a business is Active or Inactive based on multiple signals
 
 Args:
 business_data: Dict containing:
 - name: Business name
 - review_count: Number of reviews
 - last_review_date: Date of most recent review
 - operating_hours: Opening hours text
 - website_status: 200, 404, or None
 - google_rating: Star rating
 - full_reviews: List of all review dicts (optional)
 
 Returns:
 Dict with classification results
 """
 today = datetime.now().strftime('%Y-%m-%d')
 
 # Extract recent review text from full_reviews if available
 recent_reviews_text = business_data.get('review_snippets', 'None')
 full_reviews = business_data.get('full_reviews', [])
 if full_reviews:
 # Get last 20 reviews for context
 recent_20 = full_reviews[-20:] if len(full_reviews) > 20 else full_reviews
 recent_reviews_text = "\n".join([
 f"[{r.get('review_datetime_utc', 'N/A')[:10]}] {r.get('review_rating')}: {(r.get('review_text') or '')[:200]}"
 for r in recent_20
 ])
 
 system_prompt = f"""You are a business analyst. Today is {today}.
Your task is to determine if a business is currently ACTIVE or INACTIVE (closed/defunct).

ACTIVE indicators:
- Recent reviews (within 6 months)
- Operating hours listed
- Website accessible (status 200)
- High rating with many reviews

INACTIVE indicators:
- No reviews in 12+ months
- Last review mentions "closed permanently"
- Website 404 error
- Google Maps shows "Permanently closed"

Be conservative: if unclear, classify as "Uncertain"."""

 user_prompt = f"""Business: {business_data.get('name', 'Unknown')}
Review Count: {business_data.get('review_count', 0)}
Last Review: {business_data.get('last_review_date', 'Never')}
Hours: {business_data.get('operating_hours', 'Not listed')}
Website Status: {business_data.get('website_status', 'Unknown')}
Rating: {business_data.get('google_rating', 'N/A')}
Recent Reviews:
{recent_reviews_text}

Return JSON:
{{
 "status": "Active/Inactive/Uncertain",
 "confidence": "High/Medium/Low",
 "reasoning": "Brief explanation of key signals",
 "risk_factors": ["List any closure warning signs"]
}}"""

 try:
 response = self.client.chat.completions.create(
 model=self.model,
 messages=[
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": user_prompt}
 ],
 temperature=self.temperature
 )
 
 result = json.loads(
 response.choices[0].message.content
 .replace("```json", "")
 .replace("```", "")
 .strip()
 )
 
 return result
 
 except Exception as e:
 return {
 "status": "Error",
 "confidence": "Low",
 "reasoning": f"Analysis failed: {str(e)[:100]}",
 "risk_factors": ["Analysis error"]
 }
 
 def estimate_employment(self, business_data: Dict) -> Dict:
 """
 Estimate number of employees based on available signals including review analysis
 
 Args:
 business_data: Dict with business characteristics + full_reviews
 
 Returns:
 Employment estimate with confidence
 """
 # Extract staff mentions from full reviews if available
 staff_mentions = business_data.get('staff_mentions', 'None')
 full_reviews = business_data.get('full_reviews', [])
 if full_reviews:
 # Sample reviews mentioning staff
 staff_related = []
 keywords = ['staff', 'employee', 'worker', 'bartender', 'waiter', 'barista', 'trainer', 'manager']
 for r in full_reviews:
 text = (r.get('review_text') or '').lower()
 if any(kw in text for kw in keywords):
 staff_related.append(f"[{r.get('review_rating')}] {text[:150]}")
 if len(staff_related) >= 10:
 break
 if staff_related:
 staff_mentions = "\n".join(staff_related)
 
 system_prompt = """You are an employment analyst.
Estimate the number of employees based on business characteristics and review content.

Guidelines:
- Coffee shop: 3-8 employees typically
- Gym: 10-30 employees typically
- Library: 5-20 employees typically
- Consider: size mentions, review mentions of staff, operating hours, review density
- Review density (reviews/month) correlates with customer volume and staffing needs

Provide a range (min-max) and best estimate."""

 reviews_per_month = business_data.get('reviews_per_month', 0)
 total_reviews = business_data.get('total_reviews_collected', business_data.get('review_count', 0))
 
 user_prompt = f"""Business: {business_data.get('name')}
Type: {business_data.get('category', 'Unknown')}
Price Level: {business_data.get('price_level', 'Unknown')}
Operating Hours: {business_data.get('operating_hours', 'Unknown')}
Total Reviews: {total_reviews}
Reviews/Month: {reviews_per_month}
Size Indicators: {business_data.get('size_indicators', 'None')}
Staff Mentions in Reviews:
{staff_mentions}

Return JSON:
{{
 "min_employees": <number>,
 "max_employees": <number>,
 "best_estimate": <number>,
 "confidence": "High/Medium/Low",
 "reasoning": "Brief explanation"
}}"""

 try:
 response = self.client.chat.completions.create(
 model=self.model,
 messages=[
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": user_prompt}
 ],
 temperature=self.temperature
 )
 
 result = json.loads(
 response.choices[0].message.content
 .replace("```json", "")
 .replace("```", "")
 .strip()
 )
 
 return result
 
 except Exception as e:
 return {
 "min_employees": None,
 "max_employees": None,
 "best_estimate": None,
 "confidence": "Low",
 "reasoning": f"Estimation failed: {str(e)[:100]}"
 }
 
 def verify_naics_classification(self, business_data: Dict, target_naics: str, definition: str) -> Dict:
 """
 Verify if a business matches the target NAICS classification
 
 Args:
 business_data: Business characteristics
 target_naics: Expected NAICS code
 definition: NAICS category definition
 
 Returns:
 Verification result
 """
 system_prompt = f"""You are a business classification expert.
Target Category: NAICS {target_naics}
Definition: {definition}

Determine if this business truly belongs to this category."""

 user_prompt = f"""Business: {business_data.get('name')}
Google Category: {business_data.get('google_types', [])}
Operating Hours: {business_data.get('operating_hours', 'Unknown')}
Attributes: {business_data.get('attributes', 'Unknown')}
Review Keywords: {business_data.get('review_keywords', 'None')}

Does this match NAICS {target_naics}?

Return JSON:
{{
 "is_match": true/false,
 "confidence": "High/Medium/Low",
 "actual_naics_suggestion": "6-digit code",
 "reasoning": "Explanation of classification"
}}"""

 try:
 response = self.client.chat.completions.create(
 model=self.model,
 messages=[
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": user_prompt}
 ],
 temperature=self.temperature
 )
 
 result = json.loads(
 response.choices[0].message.content
 .replace("```json", "")
 .replace("```", "")
 .strip()
 )
 
 return result
 
 except Exception as e:
 return {
 "is_match": None,
 "confidence": "Low",
 "actual_naics_suggestion": None,
 "reasoning": f"Classification failed: {str(e)[:100]}"
 }
 
 def analyze_business_comprehensive(self, business_data: Dict, target_naics: str, definition: str) -> Dict:
 """
 Comprehensive analysis combining all GPT capabilities
 
 Returns:
 Complete business analysis
 """
 return {
 'status': self.classify_business_status(business_data),
 'employment': self.estimate_employment(business_data),
 'naics_verification': self.verify_naics_classification(business_data, target_naics, definition)
 }


# Example usage
if __name__ == "__main__":
 analyzer = GPTAnalyzer()
 
 test_business = {
 'name': 'Spyhouse Coffee',
 'review_count': 245,
 'last_review_date': '2026-01-15',
 'operating_hours': 'Mon-Fri: 6AM-6PM, Sat-Sun: 7AM-5PM',
 'website_status': 200,
 'google_rating': 4.5,
 'review_snippets': 'Great espresso! ... Love this place ... Best coffee in town'
 }
 
 status = analyzer.classify_business_status(test_business)
 print(f"Status Analysis: {status}")
