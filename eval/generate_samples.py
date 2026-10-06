import json, os, random
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

random.seed(42)  # same samples every run
VENDORS = [
    ("Verma Kirana Traders", "VKT", "INR"), ("Gupta Office Supplies", "GOS", "INR"),
    ("Rao Electronics", "RAO", "INR"), ("Northwind Stationers", "NWS", "USD"),
    ("Bluepeak Logistics", "BPL", "USD"),
]
ITEMS = [("Notebook A4", 45), ("Ballpoint Pens Box", 120), ("Printer Paper Ream", 380),
         ("USB Cable 1m", 150), ("Wireless Mouse", 650), ("Desk Lamp", 900),
         ("Stapler", 210), ("Whiteboard Marker Set", 175), ("HDMI Cable", 320),
         ("Keyboard", 1100), ("Courier Charge", 250), ("Packing Material", 90)]

os.makedirs("eval/samples", exist_ok=True)
truth = {}

for n in range(1, 41):
    name, code, cur = random.choice(VENDORS)
    inv_no = f"{code}/2026/{1000 + n}"
    lines = []
    for desc, rate in random.sample(ITEMS, random.randint(2, 6)):
        qty = random.randint(1, 5)
        lines.append((desc, qty, rate, round(qty * rate, 2)))
    sub = round(sum(l[3] for l in lines), 2)
    tax = round(sub * random.choice([0.05, 0.12, 0.18]), 2)
    total = round(sub + tax, 2)
    inv_date = date(2026, 9, 1) + timedelta(days=n)
    due = inv_date + timedelta(days=30) if random.random() < 0.6 else None
    alt = n % 2 == 0  # layout B: different labels and date format
    fmt = (lambda d: d.strftime("%d/%m/%Y")) if alt else (lambda d: d.strftime("%d-%b-%Y"))

    fname = f"inv_{n:02d}.pdf"
    c = canvas.Canvas(f"eval/samples/{fname}", pagesize=A4)
    y = 790
    c.setFont("Helvetica-Bold", 16); c.drawString(50, y, "INVOICE" if alt else "TAX INVOICE"); y -= 24
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, name); y -= 14
    c.setFont("Helvetica", 10); c.drawString(50, y, "SAMPLE DOCUMENT - fictitious data"); y -= 22
    c.drawString(50, y, f"{'Bill No.' if alt else 'Invoice No:'} {inv_no}"); y -= 14
    c.drawString(50, y, f"Date: {fmt(inv_date)}"); y -= 14
    if due:
        c.drawString(50, y, f"Due Date: {fmt(due)}"); y -= 14
    c.drawString(50, y, f"Currency: {cur}"); y -= 26
    c.setFont("Helvetica-Bold", 10)
    for x, t in ((50, "Description"), (300, "Qty"), (360, "Rate"), (450, "Amount")):
        c.drawString(x, y, t)
    y -= 6; c.line(50, y, 545, y); y -= 15; c.setFont("Helvetica", 10)
    for d, q, r, a in lines:
        c.drawString(50, y, d); c.drawString(300, y, str(q))
        c.drawString(360, y, f"{r:.2f}"); c.drawString(450, y, f"{a:.2f}"); y -= 15
    y -= 8
    c.drawString(330, y, "Subtotal:"); c.drawString(450, y, f"{sub:.2f}"); y -= 14
    c.drawString(330, y, "Tax:"); c.drawString(450, y, f"{tax:.2f}"); y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(330, y, "Net Payable:" if alt else "Grand Total:"); c.drawString(450, y, f"{total:.2f}")
    c.save()

    truth[fname] = {"vendor": name, "invoice_no": inv_no, "currency": cur,
                    "total": total, "tax": tax, "due_date": due.isoformat() if due else ""}

json.dump(truth, open("eval/truth.json", "w"), indent=2)
print("generated", len(truth), "invoices")