from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import csv

# Setup Edge
options = Options()
options.add_argument("--start-maximized")

edge_driver_path = "C:/Users/Swank/Downloads/edgedriver_win64/msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service, options=options)

# Step 1: Go to product page
product_url = "https://www.ebay.com/itm/406109000959"
driver.get(product_url)
time.sleep(3)

# Step 2: Try to find store link
feedback_url = None
try:
    store_link = driver.find_element(By.XPATH, "//a[contains(@href, '/str/')]")
    store_url = store_link.get_attribute("href")
    print("🛍️ Store URL:", store_url)
    driver.get(store_url)
    time.sleep(3)

    # Step 3: Construct feedback tab URL
    username = store_url.split("/")[-1].split("?")[0]
    feedback_tab_url = f"https://www.ebay.com/str/{username}?_tab=feedback"
    print("📄 Feedback Tab URL:", feedback_tab_url)
    driver.get(feedback_tab_url)
    time.sleep(3)

    # Step 4: Click feedback profile button
    feedback_button = driver.find_element(By.XPATH, "//a[contains(@href, 'feedback_profile')]")
    feedback_url = feedback_button.get_attribute("href")
    print("🔗 Feedback Profile URL:", feedback_url)
    driver.get(feedback_url)
    time.sleep(3)

except Exception as e:
    print("⚠️ Store link or feedback tab not found, trying fallback:", e)

    # Fallback 1: Try direct feedback profile link on product page
    try:
        feedback_button = driver.find_element(By.XPATH, "//a[contains(@href, '/fdbk/feedback_profile/')]")
        feedback_url = feedback_button.get_attribute("href")
        print("🔗 Fallback Feedback Profile URL:", feedback_url)
        driver.get(feedback_url)
        time.sleep(3)
    except:
        # Fallback 2: Try "View all feedback" button in seller card
        try:
            feedback_button = driver.find_element(By.XPATH, "//a[contains(@class, 'fdbk-detail-list___btn-container___btn')]")
            feedback_url = feedback_button.get_attribute("href")
            print("🔗 Seller Card Feedback URL:", feedback_url)
            driver.get(feedback_url)
            time.sleep(3)
        except Exception as final_e:
            print("❌ Couldn't find any feedback link:", final_e)
            driver.quit()
            exit()

# Step 5: Confirm we're on feedback profile page
print("✅ Final Page Title:", driver.title)

# Step 6: Scrape feedback sentiment and comment
try:
    feedback_cards = driver.find_elements(By.CSS_SELECTOR, "div.card_text")

    with open("feedback_data.csv", "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Sentiment", "Comment"])

        for card in feedback_cards:
            try:
                sentiment_svg = card.find_element(By.CSS_SELECTOR, "div.card_rating svg[aria-label]")
                sentiment = sentiment_svg.get_attribute("aria-label")

                comment_span = card.find_element(By.CSS_SELECTOR, "span[data-testid='fdbk-comment-undefined']")
                comment = comment_span.text.strip()

                print("📊 Sentiment:", sentiment)
                print("📝 Feedback:", comment)
                print("-" * 60)

                writer.writerow([sentiment, comment])

            except Exception as inner_e:
                print(f"⚠️ Error extracting feedback: {inner_e}")

except Exception as e:
    print("❌ Couldn't scrape feedback:", e)

# Done
driver.quit()
