import json
import requests
import os
import smtplib
from bs4 import BeautifulSoup
from email.message import EmailMessage


with open("shops.json") as f:
    config = json.load(f)


with open("last_status.json") as f:
    old_status = json.load(f)


new_status = {}

found = []

print("🔍 Starting Midea PortaSplit stock check...\n")

def check_shop(shop):

    try:

        r = requests.get(
            shop["url"],
            timeout=20,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        text = BeautifulSoup(
            r.text,
            "lxml"
        ).get_text(
            " ",
            strip=True
        ).lower()


        product = any(
            x.lower() in text
            for x in config["product_keywords"]
        )


        stock = any(
            x.lower() in text
            for x in config["stock_keywords"]
        )


        status = product and stock

        return status


    except Exception as e:
        print(f"   ❌ Error checking {shop['name']}: {e}")
        return False



for shop in config["shops"]:

    available = check_shop(shop)

    new_status[shop["name"]] = available

    status_icon = "✅" if available else "❌"
    print(f"{status_icon} {shop['name']}: {available}")

    if available and not old_status.get(shop["name"]):

        found.append(shop)
        print(f"   🎉 NEW! {shop['name']} has stock!")



with open(
    "last_status.json",
    "w"
) as f:

    json.dump(
        new_status,
        f,
        indent=2
    )

print(f"\n📊 Results saved. Found {len(found)} new items in stock.\n")

if found:

    print("📧 Sending email...\n")

    body = "Midea PortaSplit gevonden:\n\n"


    for shop in found:

        body += (
            shop["name"]
            + "\n"
            + shop["url"]
            + "\n\n"
        )


    msg = EmailMessage()

    msg["Subject"] = (
        "Midea PortaSplit voorraad gevonden"
    )

    msg["From"] = os.environ["MAIL_FROM"]
    msg["To"] = os.environ["MAIL_TO"]

    msg.set_content(body)



    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            os.environ["MAIL_FROM"],
            os.environ["MAIL_PASSWORD"]
        )

        smtp.send_message(msg)
        print("✅ Email sent successfully!\n")

else:
    print("❌ No new stock found.\n")
