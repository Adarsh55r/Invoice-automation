import json, subprocess, time
import requests

URL = "http://localhost:5678/webhook/eval-invoice"
truth = json.load(open("eval/truth.json"))

def sql(q):
    r = subprocess.run(
        ["docker", "compose", "exec", "-T", "postgres", "psql", "-U", "n8n", "-d", "n8n",
         "-t", "-A", "-F", "|", "-c", q], capture_output=True, text=True)
    return r.stdout.strip()

print("Clearing test invoices and audit log (dev only)...")
sql("TRUNCATE invoices, audit_log RESTART IDENTITY CASCADE;")

FIELDS = ["vendor", "invoice_no", "currency", "total", "tax", "due_date"]
ok = {f: 0 for f in FIELDS}
exact = missing = 0
statuses, rows_out = {}, []

for fname, exp in truth.items():
    with open(f"eval/samples/{fname}", "rb") as f:
        requests.post(URL, files={"invoice": (fname, f, "application/pdf")}, timeout=30)

    row = ""
    for _ in range(40): 
        row = sql("SELECT vendor, invoice_no, currency, amount, tax, COALESCE(due_date::text,''), "
                  f"confidence, status FROM invoices WHERE invoice_no = '{exp['invoice_no']}';")
        if row:
            break
        time.sleep(2)
    if not row:
        missing += 1
        print(f"{fname}: NO ROW (pipeline failed or was skipped)")
        continue

    v, no, cur, amt, tax, due, conf, status = row.split("|")
    got = {"vendor": v, "invoice_no": no, "currency": cur,
           "total": float(amt or 0), "tax": float(tax or 0), "due_date": due}
    res = {
        "vendor": got["vendor"].strip().lower() == exp["vendor"].lower(),
        "invoice_no": got["invoice_no"] == exp["invoice_no"],
        "currency": got["currency"].upper() == exp["currency"],
        "total": abs(got["total"] - exp["total"]) < 0.01,
        "tax": abs(got["tax"] - exp["tax"]) < 0.01,
        "due_date": got["due_date"] == exp["due_date"],
    }
    for f in FIELDS:
        ok[f] += res[f]
    exact += all(res.values())
    statuses[status] = statuses.get(status, 0) + 1
    rows_out.append({"file": fname, "confidence": int(conf), "status": status,
                     "wrong_fields": [f for f in FIELDS if not res[f]]})
    print(f"{fname}: {'OK' if all(res.values()) else 'WRONG ' + str([f for f in FIELDS if not res[f]])}")

n = len(truth)
processed = n - missing
print("\n=== RESULTS ===")
print(f"Invoices tested: {n}, processed: {processed}, no row: {missing}")
for f in FIELDS:
    print(f"{f:12s} {ok[f]}/{processed} = {100 * ok[f] / max(processed, 1):.1f}%")
print(f"All fields correct: {exact}/{n} = {100 * exact / n:.1f}%")
print("Status counts:", statuses)
json.dump({"n": n, "missing": missing, "field_correct": ok, "exact": exact,
           "statuses": statuses, "rows": rows_out}, open("eval/results.json", "w"), indent=2)