import re 
import csv


# Read text file
with open("meeting_minutes.txt", "r", encoding="utf-8") as file:
    text = file.read()
    

# find email addresses
emails = re.findall(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    text
)


#Remove duplicates while preserving order
emails = list(dict.fromkeys(emails))


# Save to CSV
with open("emails.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    #Column heading
    writer.writerow(["Email"])
    
    #write each email
    for email in emails:
        writer.writerow([email])
        
print(f"{len(emails)} Unique email addresses extracted")
print("saved to emails.csv")