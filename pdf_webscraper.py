import pypdf
import pandas as pd
import re
import json
import os

def parse_listings_from_text(full_text):
    # [same function as before...]
    listings = []
    listing_blocks = re.split(r'Listing\s+Number\s*:', full_text, flags=re.IGNORECASE)
    if len(listing_blocks) < 2:
        return []

    for block in listing_blocks[1:]:
        data = {
            'Name': 'N/A',
            'Location': 'N/A',
            'Price': 'N/A',
            'Down Payment': 'N/A',
            'Listing Number': 'N/A',
            'Discretionary Earnings': 'N/A',
            'Sales Revenue': 'N/A',
            'Notes/Details': 'N/A'
        }
        current_block_text = "Listing Number :" + block

        patterns = {
            'Listing Number': r'Listing\s+Number\s*:\s*([\w-]+)',
            'Price': r'Price\s*:\s*(\$[\d,]+(?:\.\d{2})?)',
            'Down Payment': r'Down\s+Payment\s*:\s*(\$[\d,]+(?:\.\d{2})?)',
            'Discretionary Earnings': r'Disc\.\s+Earnings\s*:\s*([$\d,.-]+)',
            'Sales Revenue': r'Sales\s+Revenue\s*:\s*([$\d,.-]+)',
            'Location': r'([\w\s]+,\s*Florida\s*USA)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, current_block_text, flags=re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()

        details_match = re.search(
            r'Sales\s+Revenue\s*:\s*[^\n]+\n(.+?)Click for more details',
            current_block_text,
            flags=re.IGNORECASE | re.DOTALL
        )
        if details_match:
            details_text = details_match.group(1).strip()
            lines = [line.strip() for line in details_text.split('\n') if line.strip()]
            if lines:
                data['Name'] = lines[0]
                data['Notes/Details'] = ' '.join(lines[1:]) if len(lines) > 1 else 'N/A'

        listings.append(data)

    return listings


def scrape_pdf(config_path="config.json"):
    """Reads config.json, extracts listings from a PDF, saves to Excel."""
    try:
        # Load config
        with open(config_path, "r") as f:
            config = json.load(f)

        pdf_dir = config.get("pdf_directory", ".")
        pdf_file = config.get("pdf_filename")

        if not pdf_file:
            print("❌ ERROR: 'pdf_filename' missing in config.json")
            return

        pdf_path = os.path.join(pdf_dir, pdf_file)

        # Read PDF
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        print(f"✅ Extracted text from {len(reader.pages)} pages.")

        listings_data = parse_listings_from_text(full_text)

        if not listings_data:
            print("⚠️ No listings parsed. Saving raw text...")
            raw_output = "ebitda_raw_text.txt"
            with open(raw_output, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"📄 Raw text saved to {raw_output}")
            return

        # Save to Excel
        df = pd.DataFrame(listings_data)
        output_filename = "ebitda_listings.xlsx"
        df.to_excel(output_filename, index=False)

        print(f"🎉 Parsed {len(listings_data)} listings → {output_filename}")

        # Print sample to console
        print("\n🔎 First 2 listings:")
        print(df.head(2).to_string(index=False))

    except FileNotFoundError:
        print(f"❌ ERROR: File '{pdf_file}' not found in '{pdf_dir}'")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    scrape_pdf()
