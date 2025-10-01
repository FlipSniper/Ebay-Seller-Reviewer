from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re
from typing import Optional
from bs4 import BeautifulSoup
import subprocess
import sys
import os


# Print Python executable for environment debugging
print("[API] Using Python executable:", sys.executable)

app = FastAPI()

# Print Python executable for environment debugging (after app is defined)
print("[API] Using Python executable:", sys.executable)
 
# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    print("Health check called! - FORCED RELOAD V2")
    return {"status": "ok", "debug": "print statement working - FORCED RELOAD V2", "timestamp": "2025-08-13"}

@app.get("/test-search/{product}")
def test_search(product: str):
    """Test endpoint to debug search functionality"""
    debug_info = []
    debug_info.append(f"=== TEST SEARCH CALLED FOR: {product} ===")
    debug_info.append("Calling searchEbay_scrape function...")
    
    search_result = searchEbay_scrape(product)
    debug_info.append(f"searchEbay_scrape returned: {search_result}")
    
    if isinstance(search_result, dict):
        item_id = search_result.get("item_id")
        search_debug = search_result.get("debug_info", [])
        debug_info.extend(search_debug)
    else:
        item_id = search_result
        search_debug = []
    
    result = {
        "product": product,
        "item_id": item_id,
        "success": item_id is not None,
        "debug": "FUNCTION UPDATED - SHOULD SHOW DEBUG OUTPUT",
        "console_output": "Check server console for debug messages",
        "debug_log": debug_info
    }
    debug_info.append(f"Returning result: {result}")
    return result

class AnalyseRequest(BaseModel):
    product: Optional[str] = None
    ebay_link: Optional[str] = None

# Helper functions (copied from main.py)
def extract_item_id(url):
    match = re.search(r'/itm/([^/?]+)', url)
    return match.group(1) if match else None

def searchEbay_scrape(prod):
    debug_info = []
    debug_info.append(f"🔍 searchEbay_scrape FUNCTION CALLED with product: {prod}")
    
    # Try mobile eBay first (sometimes less protected)
    search_url = f"https://m.ebay.com/sch/i.html?_nkw={prod}&_sacat=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": "1"
    }
    
    try:
        import time
        debug_info.append(f"Searching for: {prod}")
        debug_info.append("Adding small delay to look more human...")
        time.sleep(2)  # Small delay to look more human
        response = requests.get(search_url, headers=headers, timeout=15)
        debug_info.append(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            debug_info.append(f"Bad response: {response.text[:500]}")
            return {"item_id": None, "debug_info": debug_info}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors for item links
        item_link = None
        
        # Method 1: Look for s-item__link class
        item_link = soup.find('a', class_='s-item__link')
        if not item_link:
            # Method 2: Look for any link containing /itm/
            item_link = soup.find('a', href=re.compile(r'/itm/'))
        if not item_link:
            # Method 3: Look for links in search results
            item_link = soup.find('a', href=re.compile(r'ebay\.co\.uk/itm/'))
        
        if item_link and item_link.get('href'):
            item_url = item_link['href']
            debug_info.append(f"Found item URL: {item_url}")
            # Extract item ID from URL
            item_id = extract_item_id(item_url)
            debug_info.append(f"Extracted item ID: {item_id}")
            return {"item_id": item_id, "debug_info": debug_info}
        
        debug_info.append("No item link found. HTML preview:")
        debug_info.append(response.text[:1000])
        return {"item_id": None, "debug_info": debug_info}
        
    except Exception as e:
        debug_info.append(f"Error searching eBay: {e}")
        return {"item_id": None, "debug_info": debug_info}

def get_seller_info(item_id):
    debug_info = []
    debug_info.append(f"🔍 get_seller_info FUNCTION CALLED with item_id: {item_id}")
    
    # Scrape the item page directly
    item_url = f"https://www.ebay.com/itm/{item_id}"
    debug_info.append(f"Fetching item page: {item_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(item_url, headers=headers, timeout=15)
        debug_info.append(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            debug_info.append(f"Bad response: {response.text[:500]}")
            return {"debug_info": debug_info}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        debug_info.append("HTML parsed successfully")
        
        # Extract seller info
        seller_info = {"debug_info": debug_info}
        
        # Try multiple seller detection methods
        seller_found = False
        
        # Method 1: Look for mbgLink (old method)
        seller_link = soup.find('a', {'data-testid': 'mbgLink'})
        if seller_link:
            seller_info["username"] = seller_link.get_text(strip=True)
            debug_info.append(f"Found seller username via mbgLink: {seller_info['username']}")
            seller_found = True
        
        # Method 2: Look for /usr/ links
        if not seller_found:
            seller_link = soup.find('a', href=re.compile(r'/usr/'))
            if seller_link:
                seller_info["username"] = seller_link.get_text(strip=True)
                debug_info.append(f"Found seller username via /usr/ pattern: {seller_info['username']}")
                seller_found = True
        
        # Method 3: Look for seller in item details
        if not seller_found:
            seller_section = soup.find('div', string=re.compile(r'seller|Seller', re.IGNORECASE))
            if seller_section:
                debug_info.append(f"Found seller section: {seller_section.get_text()[:200]}")
                # Look for username in this section
                username_elem = seller_section.find('a') or seller_section.find('span')
                if username_elem:
                    seller_info["username"] = username_elem.get_text(strip=True)
                    debug_info.append(f"Found seller username in seller section: {seller_info['username']}")
                    seller_found = True
        
        # Method 4: Look for any text containing "seller" and extract nearby text
        if not seller_found:
            seller_text = soup.find(string=re.compile(r'seller|Seller', re.IGNORECASE))
            if seller_text:
                debug_info.append(f"Found seller text: {seller_text[:200]}")
                # Look for the parent element and find username
                parent = seller_text.parent
                if parent:
                    username_elem = parent.find('a') or parent.find('span')
                    if username_elem:
                        seller_info["username"] = username_elem.get_text(strip=True)
                        debug_info.append(f"Found seller username near seller text: {seller_info['username']}")
                        seller_found = True
        
        # Method 5: Look for any link that might be a seller
        if not seller_found:
            all_links = soup.find_all('a', href=True)
            for link in all_links[:20]:  # Check first 20 links
                href = link.get('href', '')
                if '/usr/' in href or 'seller' in href.lower() or 'user' in href.lower():
                    username = link.get_text(strip=True)
                    if username and len(username) > 2 and len(username) < 50:
                        seller_info["username"] = username
                        debug_info.append(f"Found potential seller username via link analysis: {username}")
                        seller_found = True
                        break
        
        if not seller_found:
            debug_info.append("No seller username found with any method")
            # Add some HTML preview to help debug
            debug_info.append("HTML preview (first 1000 chars):")
            debug_info.append(response.text[:1000])
        
        # Try to find feedback score
        feedback_elem = soup.find('span', string=re.compile(r'feedback'))
        if feedback_elem:
            feedback_text = feedback_elem.get_text()
            debug_info.append(f"Found feedback element: {feedback_text}")
            # Extract numbers from feedback text
            numbers = re.findall(r'\d+', feedback_text)
            if numbers:
                seller_info["feedbackScore"] = int(numbers[0])
                debug_info.append(f"Extracted feedback score: {seller_info['feedbackScore']}")
        else:
            debug_info.append("No feedback element found")
        
        debug_info.append(f"Final seller_info: {seller_info}")
        return seller_info
    except Exception as e:
        debug_info.append(f"Error getting seller info: {e}")
        return {"debug_info": debug_info}

def get_feedback_v1(username, limit=5):
    # Scrape the seller's profile page for feedback
    profile_url = f"https://www.ebay.co.uk/usr/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(profile_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        feedback_list = []
        
        # Look for feedback elements (this might need adjustment based on actual eBay HTML structure)
        feedback_elements = soup.find_all('div', class_=re.compile(r'feedback|review'))
        
        for i, elem in enumerate(feedback_elements[:limit]):
            feedback_text = elem.get_text(strip=True)
            if feedback_text and len(feedback_text) > 10:  # Filter out very short text
                feedback_list.append({
                    "comment": feedback_text[:200],  # Limit comment length
                    "rating": "positive",  # Default rating
                    "creationDate": "recent"
                })
        
        return feedback_list
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return []

@app.post("/analyze-seller")
def analyze_seller(req: AnalyseRequest):
    import pandas as pd
    debug_info = []
    debug_info.append(f"=== ANALYZE SELLER CALLED ===")
    print(f"[API] /analyze-seller called with: {req}")

    # Run CombinedFeedback.py synchronously to scrape feedback for the given eBay link
    if req.ebay_link:
        print(f"[API] Running CombinedFeedback.py for link: {req.ebay_link}")
        result_scrape = subprocess.run([sys.executable, "CombinedFeedback.py", req.ebay_link], cwd=".", capture_output=True, text=True)
        print(f"[API] CombinedFeedback.py output: {result_scrape.stdout}")
        print(f"[API] CombinedFeedback.py stderr: {result_scrape.stderr}")
        # Log to file for debugging
        with open("combinedfeedback_api_debug.log", "w", encoding="utf-8") as f:
            f.write("STDOUT:\n" + result_scrape.stdout + "\n\nSTDERR:\n" + result_scrape.stderr)
        def summarize_output(out):
            lines = out.splitlines()
            if len(lines) > 30:
                return '\n'.join(lines[:10] + ["... (output truncated) ..."] + lines[-10:])
            return out
        combined_output = summarize_output(result_scrape.stdout)
        combined_error = summarize_output(result_scrape.stderr)
        if result_scrape.returncode != 0:
            return {"error": "Failed to scrape feedback.", "details": combined_error, "output": combined_output}
        if not combined_output.strip() and not combined_error.strip():
            return {"warning": "CombinedFeedback.py ran but produced no output or error.", "output": combined_output, "stderr": combined_error}

        # If scraping succeeded, run AIAnalysis.py
        print(f"[API] Running AIAnalysis.py for analysis...")
        result_analysis = subprocess.run([sys.executable, "AIAnalysis.py"], cwd=".", capture_output=True, text=True)
        print(f"[API] AIAnalysis.py output: {result_analysis.stdout}")
        with open("aianalysis_api_debug.log", "w", encoding="utf-8") as f:
            f.write("STDOUT:\n" + result_analysis.stdout + "\n\nSTDERR:\n" + result_analysis.stderr)
        analysis_output = summarize_output(result_analysis.stdout)
        analysis_error = summarize_output(result_analysis.stderr)
        if result_analysis.returncode != 0:
            return {
                "error": "Failed to analyze feedback.",
                "scrape_output": combined_output,
                "scrape_stderr": combined_error,
                "analysis_stderr": analysis_error
            }

        # Parse test.csv for summary stats and recent feedbacks
        try:
            # After AIAnalysis.py, reload test.csv to get issues/final_sentiment columns
            df = pd.read_csv("test.csv")
            # If issues/final_sentiment not present, try to load from negative_reviews.csv or fallback
            if not ("issues" in df.columns and "final_sentiment" in df.columns):
                # Try to load from negative_reviews.csv (should have those columns)
                try:
                    df_neg = pd.read_csv("negative_reviews.csv")
                    if "issues" in df_neg.columns and "final_sentiment" in df_neg.columns:
                        # Merge negative review info into df
                        df = pd.merge(df, df_neg[["comment","issues","final_sentiment"]], on="comment", how="left")
                        df["issues"] = df["issues"].fillna("").apply(lambda x: x if isinstance(x, list) else [i.strip() for i in str(x).split(",") if i.strip()])
                        df["final_sentiment"] = df["final_sentiment"].fillna("")
                except Exception:
                    pass

            total_feedback = len(df)
            positive_count = (df["rating_type"].str.lower() == "positive").sum()
            neutral_count = (df["rating_type"].str.lower() == "neutral").sum() if "neutral" in df["rating_type"].str.lower().unique() else 0
            negative_count = (df["rating_type"].str.lower() == "negative").sum() if "negative" in df["rating_type"].str.lower().unique() else 0
            positive_percent = round(100 * positive_count / total_feedback, 2) if total_feedback else 0
            # Get most recent 5 feedbacks
            recent_feedbacks = df.head(5).to_dict(orient="records")
            # Issue sentiment summary (count by issue and sentiment)
            if "issues" in df.columns and "final_sentiment" in df.columns:
                summary = (
                    df.explode("issues")
                    .groupby(["issues", "final_sentiment"])
                    .size()
                    .reset_index(name="count")
                    .sort_values("count", ascending=False)
                )
                issue_sentiment_summary = summary.to_dict(orient="records")
            else:
                issue_sentiment_summary = []

            # Compose structured response
            seller_info = {
                "total_feedback": total_feedback,
                "positive_count": int(positive_count),
                "neutral_count": int(neutral_count),
                "negative_count": int(negative_count),
                "positive_percent": positive_percent,
                "recent_feedbacks": recent_feedbacks,
                "issue_sentiment_summary": issue_sentiment_summary,
                "scrape_output": combined_output,
                "scrape_stderr": combined_error,
                "analysis_output": analysis_output,
                "analysis_stderr": analysis_error
            }
            return seller_info
        except Exception as e:
            return {
                "error": f"Failed to parse test.csv: {e}",
                "scrape_output": combined_output,
                "scrape_stderr": combined_error,
                "analysis_output": analysis_output,
                "analysis_stderr": analysis_error
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8000")))
