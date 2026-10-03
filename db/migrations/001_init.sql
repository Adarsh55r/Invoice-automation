CREATE TABLE IF NOT EXISTS vendors (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  approved BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS invoices (
  id SERIAL PRIMARY KEY,
  vendor TEXT,
  invoice_no TEXT,
  amount NUMERIC(12,2),
  tax NUMERIC(12,2),
  currency TEXT,
  due_date DATE,
  line_items JSONB,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending / auto_posted / approved / rejected
  confidence INT,
  issues JSONB,
  dedupe_hash TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  invoice_id INT REFERENCES invoices(id),
  action TEXT NOT NULL,
  actor TEXT NOT NULL,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS llm_calls (
  id SERIAL PRIMARY KEY,
  execution_id TEXT,
  model TEXT,
  input_tokens INT,
  output_tokens INT,
  cost_usd NUMERIC(10,6),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workflow_errors (
  id SERIAL PRIMARY KEY,
  workflow TEXT,
  node TEXT,
  message TEXT,
  execution_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO vendors (name) VALUES ('Acme Supplies'), ('Globex Corp'), ('Initech')
ON CONFLICT DO NOTHING;