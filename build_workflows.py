#!/usr/bin/env python3
"""Build five local-only n8n workflows. No external credentials."""

import json
import uuid
from pathlib import Path

OUT = Path("/Users/hysamkhan/n8n-portfolio-workflows")


def uid():
    return str(uuid.uuid4())


class Flow:
    def __init__(self, wid, name, description):
        self.wid = wid
        self.name = name
        self.description = description
        self.nodes = []
        self.connections = {}

    def add(self, name, typ, version, params, x, y):
        self.nodes.append(
            {
                "id": uid(),
                "name": name,
                "type": typ,
                "typeVersion": version,
                "position": [x, y],
                "parameters": params,
            }
        )
        return name

    def sticky(self, content, x, y, w=560, h=260, color=4):
        self.add(
            content.split("\n", 1)[0][:40],
            "n8n-nodes-base.stickyNote",
            1,
            {"content": content, "height": h, "width": w, "color": color},
            x,
            y,
        )

    def manual(self, name, x, y):
        return self.add(name, "n8n-nodes-base.manualTrigger", 1, {}, x, y)

    def code(self, name, js, x, y):
        return self.add(
            name,
            "n8n-nodes-base.code",
            2,
            {"mode": "runOnceForAllItems", "jsCode": js},
            x,
            y,
        )

    def iff(self, name, expr, right, x, y):
        return self.add(
            name,
            "n8n-nodes-base.if",
            2.2,
            {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "typeValidation": "loose",
                        "version": 2,
                    },
                    "combinator": "and",
                    "conditions": [
                        {
                            "id": uid(),
                            "leftValue": expr,
                            "rightValue": right,
                            "operator": {"type": "number", "operation": "gte"},
                        }
                    ],
                },
                "options": {},
            },
            x,
            y,
        )

    def link(self, src, dst, src_out=0):
        bucket = self.connections.setdefault(src, {"main": []})
        while len(bucket["main"]) <= src_out:
            bucket["main"].append([])
        bucket["main"][src_out].append({"node": dst, "type": "main", "index": 0})

    def dump(self, path):
        doc = {
            "id": self.wid,
            "name": self.name,
            "description": self.description,
            "active": False,
            "settings": {"executionOrder": "v1"},
            "nodes": self.nodes,
            "connections": self.connections,
        }
        path.write_text(json.dumps(doc, indent=2))
        return doc


def map_js(prelude, body):
    return (
        prelude
        + "\nconst rows = $input.all().map((item) => item.json);\n"
        + "return rows.map((row) => {\n"
        + body
        + "\n});\n"
    )


def pass_js(extra_lines):
    return map_js(
        "",
        "  const next = { ...row };\n" + extra_lines + "\n  return { json: next };",
    )


HASH_FN = """
function fingerprint(value) {
  const text = JSON.stringify(value);
  let hash = 2166136261;
  for (let i = 0; i < text.length; i++) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
}
"""


def build_orders():
    flow = Flow(
        "OrderCmdCenter01",
        "Order Command Center",
        "Local order desk: validate, score fraud and margin, then route quarantine, rejection, review, backorder, parcel, and pickup. Sample data only.",
    )
    orders = []

    def add(**kwargs):
        row = {
            "id": kwargs["id"],
            "customer": kwargs.get("customer", ""),
            "sku": kwargs.get("sku", "BRS-MUG"),
            "qty": kwargs.get("qty", 1),
            "unit_price": kwargs.get("unit_price", 80),
            "margin": kwargs.get("margin", 0.34),
            "billing": kwargs.get("billing", "US"),
            "ship": kwargs.get("ship", "US"),
            "card": kwargs.get("card", "US"),
            "new_customer": kwargs.get("new_customer", 0),
            "velocity_1h": kwargs.get("velocity_1h", 1),
            "mode": kwargs.get("mode", "parcel"),
            "stock": kwargs.get("stock", 40),
            "tax_rate": kwargs.get("tax_rate", 0.08),
            "title": kwargs.get("title", kwargs["id"]),
        }
        orders.append(row)

    add(id="ORD-1001", customer="", sku="BRS-MUG", title="Blank customer")
    add(id="ORD-1002", customer="Pell & Loom", sku="", title="Missing SKU")
    add(id="ORD-1003", customer="North Glass", qty=0, title="Zero quantity")
    add(id="ORD-1004", customer="Kindling Co", unit_price=-5, title="Negative price")
    add(id="ORD-1005", customer="Veldt Supply", billing="US", ship="DE", card="GB", velocity_1h=5, unit_price=420, qty=2, title="Cross-border burst")
    add(id="ORD-1006", customer="Iona Market", billing="US", ship="FR", card="SG", velocity_1h=6, new_customer=1, unit_price=900, qty=3, title="New account burst")
    add(id="ORD-1007", customer="Cairn Goods", billing="CA", ship="US", card="BR", velocity_1h=4, unit_price=640, qty=2, title="Card country mismatch")
    add(id="ORD-1008", customer="Moth & Pine", billing="US", ship="JP", card="US", velocity_1h=5, unit_price=300, qty=1, title="Velocity plus border")
    add(id="ORD-1009", customer="Sable Post", billing="GB", ship="US", card="NG", new_customer=1, velocity_1h=4, unit_price=250, qty=2, title="Stacked fraud signals")
    add(id="ORD-1010", customer="Harbor Thread", billing="US", ship="DE", new_customer=1, unit_price=90, qty=1, title="Border and new account")
    add(id="ORD-1011", customer="Lumen Paper", margin=0.05, unit_price=140, qty=2, title="Thin margin")
    add(id="ORD-1012", customer="Kite Postal", margin=0.08, unit_price=220, qty=1, title="Margin under floor")
    add(id="ORD-1013", customer="Brass Foundry", unit_price=1800, qty=1, margin=0.4, title="High gross review")
    add(id="ORD-1014", customer="Wren Studio", billing="US", ship="CA", unit_price=110, qty=1, title="Mild border risk")
    add(id="ORD-1015", customer="Ochre Home", margin=0.09, unit_price=75, qty=4, title="Discount leak")
    add(id="ORD-1016", customer="Field Radio", new_customer=1, billing="US", ship="MX", unit_price=60, qty=1, title="New cross-border")
    add(id="ORD-1017", customer="Aster Mail", unit_price=1600, qty=1, title="Large but clean")
    # in-stock parcels
    for i, name in enumerate(
        ["Cedar Batch", "Nimble Jar", "Olive Press", "Quiet Lamp", "Red Docket", "Salt Atelier", "Tin Wharf", "Umber Line", "Violet Rack", "Willow Bin"]
    ):
        add(id=f"ORD-11{i:02d}", customer=name, qty=2, unit_price=90 + i * 7, mode="parcel", stock=40, title=name)
    # backorders
    add(id="ORD-1201", customer="Yellow Kiln", qty=6, stock=2, unit_price=70, mode="parcel", title="Mug backorder")
    add(id="ORD-1202", customer="Zinc Cooperative", qty=4, stock=1, unit_price=110, mode="parcel", title="Lamp backorder")
    add(id="ORD-1203", customer="Alder Freight", qty=8, stock=3, unit_price=55, mode="parcel", title="Bin backorder")
    # pickups
    for i, name in enumerate(["Birch Counter", "Cobalt Till", "Dune Register", "Elm Kiosk", "Fern Window", "Gilt Counter"]):
        add(id=f"ORD-13{i:02d}", customer=name, qty=1, unit_price=65 + i * 9, mode="pickup", stock=10, title=name)

    flow.sticky(
        "## 1. Intake\nSample order book. No store API and no payment gateway. The manual trigger is the local run button.",
        -80, -280, 700, 200, 4,
    )
    flow.sticky(
        "## 2. Risk and margin\nFraud points: country mismatch, card mismatch, new account, velocity, and a high gross. Margin under 12% or gross over 1500 goes to review.",
        900, -280, 760, 220, 6,
    )
    flow.sticky(
        "## 3. Desks\nInvalid orders never reach stock. Rejections, reviews, backorders, parcels, and pickups each finish on their own desk.",
        1680, -280, 780, 220, 3,
    )

    data = json.dumps(orders)
    start = flow.manual("Run Order Command", 0, 180)
    load = flow.code(
        "Load Order Book",
        f"const orders = {data};\nreturn orders.map((order) => ({{ json: order }}));",
        300, 180,
    )
    normalize = flow.code(
        "Normalize Orders",
        map_js(
            "",
            """
  const problems = [];
  if (!row.customer) problems.push("missing_customer");
  if (!row.sku) problems.push("missing_sku");
  if (!(Number(row.qty) > 0)) problems.push("bad_qty");
  if (!(Number(row.unit_price) > 0)) problems.push("bad_price");
  const qty = Number(row.qty) || 0;
  const unitPrice = Number(row.unit_price) || 0;
  const validFlag = problems.length ? 0 : 1;
  const net = validFlag ? Math.round(qty * unitPrice * 100) / 100 : 0;
  return { json: { ...row, qty, unit_price: unitPrice, problems, valid_flag: validFlag, net } };
""",
        ),
        620, 180,
    )
    tier = flow.code(
        "Assign Customer Tier",
        pass_js(
            """
  next.tier = next.net >= 800 ? "gold" : next.net >= 250 ? "silver" : "standard";
"""
        ),
        940, 180,
    )
    tax = flow.code(
        "Calculate Tax",
        pass_js(
            """
  const tax = next.valid_flag ? Math.round(next.net * Number(next.tax_rate || 0) * 100) / 100 : 0;
  next.tax = tax;
  next.gross = Math.round((Number(next.net || 0) + tax) * 100) / 100;
  next.amount = next.gross;
"""
        ),
        1260, 180,
    )
    fraud = flow.code(
        "Score Fraud And Margin",
        map_js(
            "",
            """
  let fraud = 0;
  if (row.valid_flag && row.billing !== row.ship) fraud += 25;
  if (row.valid_flag && Number(row.gross) > 2000) fraud += 20;
  if (row.valid_flag && Number(row.new_customer) === 1) fraud += 15;
  if (row.valid_flag && row.card && row.card !== row.billing) fraud += 30;
  if (row.valid_flag && Number(row.velocity_1h) > 3) fraud += 25;
  fraud = Math.min(99, fraud);
  const rejectFlag = row.valid_flag && fraud >= 75 ? 1 : 0;
  const reviewFlag = row.valid_flag && !rejectFlag && (fraud >= 40 || Number(row.margin) < 0.12 || Number(row.gross) > 1500) ? 1 : 0;
  const fulfill = row.valid_flag && !rejectFlag && !reviewFlag ? 1 : 0;
  const parcelFlag = fulfill && row.mode === "parcel" ? 1 : 0;
  const pickupFlag = fulfill && row.mode !== "parcel" ? 1 : 0;
  const backorderFlag = parcelFlag && Number(row.qty) > Number(row.stock) ? 1 : 0;
  let lane = "pickup";
  if (!row.valid_flag) lane = "quarantine";
  else if (rejectFlag) lane = "reject";
  else if (reviewFlag) lane = "review";
  else if (backorderFlag) lane = "backorder";
  else if (parcelFlag) lane = "parcel";
  const actionByLane = {
    quarantine: "Send the order back to entry. Do not reserve stock.",
    reject: "Decline the payment and email the customer a plain reason.",
    review: "Hold the order for a person. Do not capture payment yet.",
    backorder: "Take payment, promise the revised ship date, and place a purchase order.",
    parcel: "Capture payment, pick, and hand the parcel to the carrier.",
    pickup: "Capture payment and hold the order at the counter."
  };
  return { json: { ...row, fraud_score: fraud, reject_flag: rejectFlag, review_flag: reviewFlag, parcel_flag: parcelFlag, pickup_flag: pickupFlag, backorder_flag: backorderFlag, lane, action: actionByLane[lane] } };
""",
        ),
        1580, 180,
    )
    sla = flow.code(
        "Apply SLA Clock",
        pass_js(
            """
  const hours = { quarantine: 4, reject: 1, review: 8, backorder: 24, parcel: 12, pickup: 6 };
  next.sla_hours = hours[next.lane] || 12;
  next.sla_label = next.sla_hours <= 4 ? "same-shift" : next.sla_hours <= 12 ? "same-day" : "next-day";
"""
        ),
        1900, 180,
    )
    digest = flow.code(
        "Executive Digest",
        HASH_FN
        + """
const rows = $input.all().map((item) => item.json);
const lanes = {};
for (const row of rows) {
  if (!lanes[row.lane]) lanes[row.lane] = { count: 0, amount: 0, samples: [] };
  lanes[row.lane].count += 1;
  lanes[row.lane].amount = Math.round((lanes[row.lane].amount + Number(row.amount || 0)) * 100) / 100;
  if (lanes[row.lane].samples.length < 3) {
    lanes[row.lane].samples.push({ id: row.id, customer: row.customer || "(blank)", amount: row.amount, action: row.action, fraud_score: row.fraud_score });
  }
}
const captured = (lanes.parcel?.amount || 0) + (lanes.pickup?.amount || 0) + (lanes.backorder?.amount || 0);
return [{ json: {
  project: "Order Command Center",
  generated_at: new Date().toISOString(),
  records: rows.length,
  lanes,
  captured_gross: Math.round(captured * 100) / 100,
  held_gross: Math.round(((lanes.review?.amount || 0) + (lanes.reject?.amount || 0)) * 100) / 100,
  fingerprint: fingerprint(rows.map((row) => [row.id, row.lane, row.amount])),
  headline: rows.length + " orders scored locally. Captured gross sits on parcel, pickup, and backorder. Review and reject stay uncaptured."
} }];
""",
        2220, 180,
    )

    valid = flow.iff("Valid Order?", "={{ $json.valid_flag }}", 1, 1580, 520)
    quarantine = flow.code(
        "Quarantine Desk",
        pass_js(
            """
  next.desk = "quarantine";
  next.notice = "We could not accept order " + next.id + " because " + (next.problems || []).join(", ") + ".";
"""
        ),
        1900, 700,
    )
    reject_if = flow.iff("Fraud Reject?", "={{ $json.reject_flag }}", 1, 1900, 520)
    reject = flow.code(
        "Rejection Desk",
        pass_js(
            """
  next.desk = "rejection";
  next.notice = "Order " + next.id + " was declined. Fraud score " + next.fraud_score + ". No stock was reserved.";
"""
        ),
        2220, 860,
    )
    review_if = flow.iff("Needs Human Review?", "={{ $json.review_flag }}", 1, 2220, 520)
    review = flow.code(
        "Review Desk",
        pass_js(
            """
  next.desk = "review";
  next.packet = next.customer + " / " + next.tier + " / fraud " + next.fraud_score + " / margin " + next.margin;
"""
        ),
        2540, 700,
    )
    ship_if = flow.iff("Parcel Path?", "={{ $json.parcel_flag }}", 1, 2540, 520)
    reserve = flow.code(
        "Reserve Inventory",
        pass_js(
            """
  next.reserved = Math.min(Number(next.qty), Number(next.stock));
  next.shortfall = Math.max(0, Number(next.qty) - Number(next.stock));
"""
        ),
        2860, 520,
    )
    back_if = flow.iff("Backorder?", "={{ $json.backorder_flag }}", 1, 3180, 520)
    backorder = flow.code(
        "Backorder Desk",
        pass_js(
            """
  next.desk = "backorder";
  next.promise = "Ship " + next.reserved + " now and the remaining " + next.shortfall + " when the purchase order lands.";
"""
        ),
        3500, 700,
    )
    rate = flow.code(
        "Parcel Rate Shop",
        pass_js(
            """
  const pounds = Math.max(1, Number(next.qty));
  const candidates = [
    { carrier: "Road", price: Math.round((6.5 + pounds * 1.4) * 100) / 100, days: 5 },
    { carrier: "Air", price: Math.round((11 + pounds * 2.6) * 100) / 100, days: 2 }
  ];
  candidates.sort((a, b) => a.price - b.price);
  next.carrier = candidates[0].carrier;
  next.freight = candidates[0].price;
  next.transit_days = candidates[0].days;
"""
        ),
        3500, 360,
    )
    invoice = flow.code(
        "Parcel Invoice",
        map_js(
            "",
            """
  const sequence = 8100 + rows.indexOf(row);
  return { json: { ...row, desk: "parcel", invoice_no: "INV-2026-" + sequence, amount_due: Math.round((Number(row.gross) + Number(row.freight || 0)) * 100) / 100 } };
""",
        ),
        3820, 360,
    )
    pickup = flow.code(
        "Pickup Counter",
        map_js(
            "",
            """
  const sequence = 9100 + rows.indexOf(row);
  return { json: { ...row, desk: "pickup", invoice_no: "PU-2026-" + sequence, hold_bin: "BIN-" + String(sequence).slice(-3), ready_in_hours: 3 } };
""",
        ),
        2860, 900,
    )

    flow.link(start, load)
    flow.link(load, normalize)
    flow.link(normalize, tier)
    flow.link(tier, tax)
    flow.link(tax, fraud)
    flow.link(fraud, sla)
    flow.link(sla, digest)
    flow.link(sla, valid)
    flow.link(valid, quarantine, 0)
    flow.link(valid, reject_if, 1)
    flow.link(reject_if, reject, 0)
    flow.link(reject_if, review_if, 1)
    flow.link(review_if, review, 0)
    flow.link(review_if, ship_if, 1)
    flow.link(ship_if, reserve, 0)
    flow.link(ship_if, pickup, 1)
    flow.link(reserve, back_if)
    flow.link(back_if, backorder, 0)
    flow.link(back_if, rate, 1)
    flow.link(rate, invoice)

    # Fix Valid Order true/false. valid_flag >= 1 is TRUE output 0.
    # I linked valid output 0 to quarantine and output 1 to reject. That is backwards.
    # Rebuild those two links below by reconstructing connections for Valid Order.
    flow.connections["Valid Order?"] = {
        "main": [
            [{"node": reject_if, "type": "main", "index": 0}],
            [{"node": quarantine, "type": "main", "index": 0}],
        ]
    }
    return flow


def build_revenue():
    flow = Flow(
        "RevReconcile0001",
        "Revenue Reconciliation and Leak Audit",
        "Match a local invoice book to payments, refunds, and chargebacks. Age the open items and separate leaks, collections, overpayments, and cleared cash.",
    )
    books = []

    def add(**kwargs):
        books.append(
            {
                "id": kwargs["id"],
                "customer": kwargs["customer"],
                "amount": kwargs["amount"],
                "payment": kwargs.get("payment", 0),
                "refund": kwargs.get("refund", 0),
                "chargeback": kwargs.get("chargeback", 0),
                "age_days": kwargs.get("age_days", 10),
                "title": kwargs["customer"],
            }
        )

    add(id="INV-501", customer="Aster Mail", amount=1200, payment=1200, age_days=12)
    add(id="INV-502", customer="Birch Counter", amount=860, payment=860, age_days=6)
    add(id="INV-503", customer="Cobalt Till", amount=440, payment=440, age_days=21)
    add(id="INV-504", customer="Dune Register", amount=2100, payment=2100, age_days=4)
    add(id="INV-505", customer="Elm Kiosk", amount=310, payment=310, refund=40, age_days=18)
    add(id="INV-506", customer="Fern Window", amount=980, payment=980, age_days=9)
    add(id="INV-507", customer="Gilt Counter", amount=150, payment=150, age_days=30)
    add(id="INV-508", customer="Harbor Thread", amount=760, payment=760, age_days=14)
    add(id="INV-509", customer="Iona Market", amount=540, payment=540, age_days=2)
    add(id="INV-510", customer="Quiet Lamp", amount=1280, payment=1280, age_days=11)
    add(id="INV-511", customer="Lumen Paper", amount=400, payment=250, age_days=12)
    add(id="INV-512", customer="Kite Postal", amount=900, payment=400, age_days=20)
    add(id="INV-513", customer="Moth and Pine", amount=650, payment=100, age_days=33)
    add(id="INV-514", customer="Nimble Jar", amount=2200, payment=500, age_days=50)
    add(id="INV-515", customer="Olive Press", amount=1750, payment=0, age_days=61)
    add(id="INV-516", customer="Pell and Loom", amount=980, payment=200, age_days=70)
    add(id="INV-517", customer="Red Docket", amount=640, payment=0, age_days=80)
    add(id="INV-518", customer="Salt Atelier", amount=430, payment=430, chargeback=430, age_days=22)
    add(id="INV-519", customer="Tin Wharf", amount=890, payment=890, chargeback=890, age_days=16)
    add(id="INV-520", customer="Umber Line", amount=1500, payment=1500, chargeback=600, age_days=27)
    add(id="INV-521", customer="Violet Rack", amount=300, payment=450, age_days=8)
    add(id="INV-522", customer="Willow Bin", amount=720, payment=900, age_days=15)
    add(id="INV-523", customer="Yellow Kiln", amount=260, payment=500, refund=20, age_days=19)
    add(id="INV-524", customer="Zinc Cooperative", amount=1100, payment=1100, age_days=7)
    add(id="INV-525", customer="Alder Freight", amount=480, payment=480, age_days=25)
    add(id="INV-526", customer="Cedar Batch", amount=670, payment=0, age_days=15)

    flow.sticky("## Books\nEach row is an invoice plus the cash, refunds, and chargebacks applied to it. This is a closed sample, not a live ledger.", -40, -260, 720, 200, 5)
    flow.sticky("## Lanes\nChargeback, overpaid, collections (open and older than 45 days), still-open, and cleared.", 1100, -260, 700, 200, 6)

    data = json.dumps(books)
    start = flow.manual("Run Reconciliation", 0, 200)
    load = flow.code("Load Invoice Book", f"const books = {data};\nreturn books.map((row) => ({{ json: row }}));", 320, 200)
    norm = flow.code(
        "Normalize Money",
        pass_js(
            """
  next.amount = Math.round(Number(next.amount) * 100) / 100;
  next.payment = Math.round(Number(next.payment || 0) * 100) / 100;
  next.refund = Math.round(Number(next.refund || 0) * 100) / 100;
  next.chargeback = Math.round(Number(next.chargeback || 0) * 100) / 100;
  next.net_paid = Math.round((next.payment - next.refund - next.chargeback) * 100) / 100;
  next.gap = Math.round((next.amount - next.net_paid) * 100) / 100;
"""
        ),
        640, 200,
    )
    match = flow.code(
        "Match Cash To Invoices",
        map_js(
            "",
            """
  const gap = Number(row.gap);
  const chargebackFlag = Number(row.chargeback) > 0 ? 1 : 0;
  const overpaidFlag = !chargebackFlag && gap < -0.01 ? 1 : 0;
  const openFlag = !chargebackFlag && !overpaidFlag && gap > 0.01 ? 1 : 0;
  const collectionsFlag = openFlag && Number(row.age_days) > 45 ? 1 : 0;
  const stillOpenFlag = openFlag && !collectionsFlag ? 1 : 0;
  const clearedFlag = !chargebackFlag && !overpaidFlag && !openFlag ? 1 : 0;
  let lane = "cleared";
  if (chargebackFlag) lane = "chargeback";
  else if (overpaidFlag) lane = "overpaid";
  else if (collectionsFlag) lane = "collections";
  else if (stillOpenFlag) lane = "open";
  const action = {
    chargeback: "Open a representment file and freeze the related payout.",
    overpaid: "Refund the extra cash or leave it as customer credit, and say which.",
    collections: "Send the aged balance to collections with the invoice and the last payment.",
    open: "Send a reminder. The balance is still inside terms.",
    cleared: "File the invoice as matched. No cash action."
  }[lane];
  return { json: { ...row, chargeback_flag: chargebackFlag, overpaid_flag: overpaidFlag, collections_flag: collectionsFlag, open_flag: stillOpenFlag, cleared_flag: clearedFlag, lane, action, title: row.customer } };
""",
        ),
        960, 200,
    )
    age = flow.code(
        "Bucket Aging",
        pass_js(
            """
  const age = Number(next.age_days);
  next.aging_bucket = age <= 30 ? "0-30" : age <= 45 ? "31-45" : age <= 60 ? "46-60" : "61+";
"""
        ),
        1280, 200,
    )
    digest = flow.code(
        "Controller Pack",
        HASH_FN
        + """
const rows = $input.all().map((item) => item.json);
const lanes = {};
for (const row of rows) {
  if (!lanes[row.lane]) lanes[row.lane] = { count: 0, amount: 0, gap: 0, samples: [] };
  lanes[row.lane].count += 1;
  lanes[row.lane].amount = Math.round((lanes[row.lane].amount + Number(row.amount)) * 100) / 100;
  lanes[row.lane].gap = Math.round((lanes[row.lane].gap + Number(row.gap)) * 100) / 100;
  if (lanes[row.lane].samples.length < 3) lanes[row.lane].samples.push({ id: row.id, customer: row.customer, gap: row.gap, age_days: row.age_days, action: row.action });
}
const leakage = Math.round(rows.filter((row) => row.lane === "chargeback" || row.lane === "collections").reduce((sum, row) => sum + Math.max(0, Number(row.gap)), 0) * 100) / 100;
return [{ json: {
  project: "Revenue Reconciliation and Leak Audit",
  generated_at: new Date().toISOString(),
  records: rows.length,
  lanes,
  leakage_gap: leakage,
  fingerprint: fingerprint(rows.map((row) => [row.id, row.lane, row.gap])),
  headline: rows.length + " invoices matched locally. Leakage is the chargeback and aged-collection gap."
} }];
""",
        1600, 200,
    )
    cb_if = flow.iff("Chargeback?", "={{ $json.chargeback_flag }}", 1, 1280, 560)
    cb = flow.code("Chargeback File", pass_js('  next.desk = "chargeback";\n  next.file = "CB-" + next.id + " amount " + next.chargeback;'), 1600, 780)
    over_if = flow.iff("Overpaid?", "={{ $json.overpaid_flag }}", 1, 1600, 560)
    over = flow.code("Credit Desk", pass_js('  next.desk = "overpaid";\n  next.credit = Math.abs(Number(next.gap));'), 1920, 860)
    col_if = flow.iff("Collections?", "={{ $json.collections_flag }}", 1, 1920, 560)
    col = flow.code("Collections Desk", pass_js('  next.desk = "collections";\n  next.dossier = next.id + " is " + next.age_days + " days old with " + next.gap + " still open.";'), 2240, 740)
    open_if = flow.iff("Still Open?", "={{ $json.open_flag }}", 1, 2240, 560)
    open_desk = flow.code("Reminder Desk", pass_js('  next.desk = "open";\n  next.reminder = "Balance " + next.gap + " on " + next.id + ", bucket " + next.aging_bucket + ".";'), 2560, 740)
    cleared = flow.code("Cleared Ledger", pass_js('  next.desk = "cleared";\n  next.stamp = "matched";'), 2560, 1040)

    for a, b in [(start, load), (load, norm), (norm, match), (match, age), (age, digest), (age, cb_if)]:
        flow.link(a, b)
    flow.link(cb_if, cb, 0)
    flow.link(cb_if, over_if, 1)
    flow.link(over_if, over, 0)
    flow.link(over_if, col_if, 1)
    flow.link(col_if, col, 0)
    flow.link(col_if, open_if, 1)
    flow.link(open_if, open_desk, 0)
    flow.link(open_if, cleared, 1)
    return flow


def build_support():
    flow = Flow(
        "SupportDesk00001",
        "Support Command Desk",
        "Classify a local ticket queue by intent, sentiment, SLA risk, and legal language, then write an escalation, a priority packet, or an auto-reply.",
    )
    tickets = []

    def add(**kwargs):
        tickets.append(
            {
                "id": kwargs["id"],
                "customer": kwargs["customer"],
                "intent": kwargs["intent"],
                "sentiment": kwargs["sentiment"],
                "age_hours": kwargs["age_hours"],
                "vip": kwargs.get("vip", 0),
                "legal": kwargs.get("legal", 0),
                "repeats": kwargs.get("repeats", 1),
                "channel": kwargs.get("channel", "email"),
                "title": kwargs["intent"] + " / " + kwargs["customer"],
                "body": kwargs["body"],
            }
        )

    add(id="T-01", customer="Aster Mail", intent="refund", sentiment=-0.2, age_hours=3, body="The mug arrived cracked. I would like a refund.")
    add(id="T-02", customer="Birch Counter", intent="order-status", sentiment=0.1, age_hours=2, body="Where is order ORD-1104?")
    add(id="T-03", customer="Cobalt Till", intent="address-change", sentiment=0.2, age_hours=1, body="Please change the ship-to before it leaves.")
    add(id="T-04", customer="Dune Register", intent="invoice-copy", sentiment=0.4, age_hours=5, body="Can you resend invoice INV-504?")
    add(id="T-05", customer="Elm Kiosk", intent="password", sentiment=0.0, age_hours=1, repeats=1, body="I cannot reset my password.")
    add(id="T-06", customer="Fern Window", intent="order-status", sentiment=0.3, age_hours=4, body="Has the pickup been packed?")
    add(id="T-07", customer="Gilt Counter", intent="refund", sentiment=-0.1, age_hours=6, body="Wrong color. Please refund the difference.")
    add(id="T-08", customer="Harbor Thread", intent="invoice-copy", sentiment=0.2, age_hours=2, body="Need a PDF of last month's invoice.")
    add(id="T-09", customer="Iona Market", intent="legal", sentiment=-0.4, age_hours=5, legal=1, body="My lawyer asked for the contract and the charge record.")
    add(id="T-10", customer="Quiet Lamp", intent="charge", sentiment=-0.85, age_hours=9, vip=1, body="This charge is outrageous and I am furious.")
    add(id="T-11", customer="Kite Postal", intent="threat", sentiment=-0.7, age_hours=3, legal=1, body="I will take this to small claims if you do not reply today.")
    add(id="T-12", customer="Lumen Paper", intent="outage", sentiment=-0.9, age_hours=2, vip=1, body="Your portal has been down and this is unacceptable.")
    add(id="T-13", customer="Moth and Pine", intent="refund", sentiment=-0.75, age_hours=7, body="I have asked three times and I am done being polite.")
    add(id="T-14", customer="Nimble Jar", intent="order-status", sentiment=-0.2, age_hours=14, repeats=4, body="Fourth time asking where the carton is.")
    add(id="T-15", customer="Olive Press", intent="refund", sentiment=-0.3, age_hours=20, repeats=3, body="Still waiting on the refund you promised.")
    add(id="T-16", customer="Pell and Loom", intent="damage", sentiment=-0.4, age_hours=11, repeats=2, body="Two damaged lamps in the same delivery.")
    add(id="T-17", customer="Red Docket", intent="billing", sentiment=0.0, age_hours=16, vip=1, body="Please explain the extra line on the gold-tier invoice.")
    add(id="T-18", customer="Salt Atelier", intent="shipping", sentiment=-0.1, age_hours=10, repeats=3, body="Tracking has not moved since Monday.")
    add(id="T-19", customer="Tin Wharf", intent="order-status", sentiment=0.5, age_hours=1, body="Thanks, just checking the pickup window.")
    add(id="T-20", customer="Umber Line", intent="address-change", sentiment=0.1, age_hours=2, body="Suite number was missing.")
    add(id="T-21", customer="Violet Rack", intent="invoice-copy", sentiment=0.0, age_hours=3, body="Accounts payable needs the invoice resent.")
    add(id="T-22", customer="Willow Bin", intent="password", sentiment=-0.1, age_hours=2, body="Reset link expired.")
    add(id="T-23", customer="Yellow Kiln", intent="order-status", sentiment=0.2, age_hours=6, body="Can you confirm the backorder date?")
    add(id="T-24", customer="Zinc Cooperative", intent="refund", sentiment=-0.05, age_hours=4, body="One item from the set was missing.")
    add(id="T-25", customer="Alder Freight", intent="damage", sentiment=-0.8, age_hours=1, legal=0, body="The crate was crushed and I want this escalated now.")
    add(id="T-26", customer="Cedar Batch", intent="shipping", sentiment=-0.15, age_hours=18, repeats=1, body="Promised Friday, now it says next week.")
    add(id="T-27", customer="Wren Studio", intent="billing", sentiment=-0.2, age_hours=9, repeats=4, vip=0, body="You charged the card twice.")
    add(id="T-28", customer="Ochre Home", intent="order-status", sentiment=0.6, age_hours=1, body="All good, sending a thank-you and a sizing question.")

    flow.sticky("## Queue\nTwenty-eight sample tickets. Sentiment and intent are already on the row so the desk can run without an AI credential.", -40, -260, 740, 200, 4)
    flow.sticky("## Routing\nLegal language, very negative sentiment, or an angry VIP goes to a person. Repeat contacts and old tickets go to the priority queue. The rest get a drafted reply.", 1000, -260, 820, 220, 3)

    data = json.dumps(tickets)
    start = flow.manual("Run Support Desk", 0, 200)
    load = flow.code("Load Ticket Queue", f"const tickets = {data};\nreturn tickets.map((row) => ({{ json: row }}));", 320, 200)
    classify = flow.code(
        "Classify Intent And Risk",
        map_js(
            "",
            """
  const sentiment = Number(row.sentiment);
  const escalate = Number(row.legal) === 1 || sentiment <= -0.7 || (Number(row.vip) === 1 && sentiment < -0.4) ? 1 : 0;
  const priority = !escalate && (Number(row.age_hours) >= 10 || Number(row.repeats) >= 3) ? 1 : 0;
  const autoFlag = !escalate && !priority ? 1 : 0;
  let lane = "autoresolve";
  if (escalate) lane = "escalate";
  else if (priority) lane = "priority";
  const action = {
    escalate: "A person answers. Do not send the macro.",
    priority: "Keep it in the one-hour queue and attach the prior tickets.",
    autoresolve: "Send the drafted reply and close if the customer does not answer."
  }[lane];
  return { json: { ...row, sentiment, escalate_flag: escalate, priority_flag: priority, auto_flag: autoFlag, lane, action, amount: 0 } };
""",
        ),
        660, 200,
    )
    sla = flow.code(
        "SLA And Staffing",
        pass_js(
            """
  next.breach = Number(next.age_hours) >= 12 ? 1 : 0;
  next.queue_minutes = next.lane === "escalate" ? 15 : next.lane === "priority" ? 60 : 5;
"""
        ),
        980, 200,
    )
    digest = flow.code(
        "Ops Brief",
        HASH_FN
        + """
const rows = $input.all().map((item) => item.json);
const lanes = {};
for (const row of rows) {
  if (!lanes[row.lane]) lanes[row.lane] = { count: 0, amount: 0, samples: [] };
  lanes[row.lane].count += 1;
  if (lanes[row.lane].samples.length < 3) lanes[row.lane].samples.push({ id: row.id, customer: row.customer, intent: row.intent, sentiment: row.sentiment, action: row.action });
}
const breaches = rows.filter((row) => row.breach).length;
return [{ json: {
  project: "Support Command Desk",
  generated_at: new Date().toISOString(),
  records: rows.length,
  lanes,
  sla_breaches: breaches,
  fingerprint: fingerprint(rows.map((row) => [row.id, row.lane, row.sentiment])),
  headline: rows.length + " tickets routed locally. " + breaches + " are already outside a 12-hour first response."
} }];
""",
        1300, 200,
    )
    esc_if = flow.iff("Escalate?", "={{ $json.escalate_flag }}", 1, 980, 560)
    esc = flow.code(
        "Escalation Desk",
        pass_js(
            """
  next.desk = "escalate";
  next.note = next.legal ? "Legal wording. Do not argue the claim in the macro." : "High emotion. A person owns the next reply.";
"""
        ),
        1300, 780,
    )
    pri_if = flow.iff("Priority Queue?", "={{ $json.priority_flag }}", 1, 1300, 560)
    pri = flow.code(
        "Priority Desk",
        pass_js(
            """
  next.desk = "priority";
  next.packet = next.repeats + " contacts, " + next.age_hours + " hours old, intent " + next.intent + ".";
"""
        ),
        1640, 760,
    )
    macro = flow.code(
        "Draft Auto Reply",
        map_js(
            "",
            """
  const replies = {
    refund: "We can see the refund request for " + row.customer + ". A credit memo will be issued against the original payment.",
    "order-status": "Your order is in the local queue. We will send the next tracking or pickup update within one business day.",
    "address-change": "If the parcel has not been handed to the carrier, we will apply the address change.",
    "invoice-copy": "A copy of the invoice is attached in the local packet for " + row.customer + ".",
    password: "Use the reset link within 30 minutes. If it expires, reply and a person will check the account.",
    damage: "We are sorry the goods arrived damaged. Keep the photos with this ticket.",
    shipping: "Tracking is being checked against the carrier scan history.",
    billing: "The extra line is under review against the original order total.",
    charge: "A person will look at the charge. This macro is not used when the ticket is escalated.",
    threat: "A person will answer.",
    legal: "A person will answer.",
    outage: "A person will answer."
  };
  return { json: { ...row, desk: "autoresolve", reply: replies[row.intent] || "Thanks for writing. We are checking this now." } };
""",
        ),
        1640, 1040,
    )
    for a, b in [(start, load), (load, classify), (classify, sla), (sla, digest), (sla, esc_if)]:
        flow.link(a, b)
    flow.link(esc_if, esc, 0)
    flow.link(esc_if, pri_if, 1)
    flow.link(pri_if, pri, 0)
    flow.link(pri_if, macro, 1)
    return flow


def build_content():
    flow = Flow(
        "ContentOpsFactory1",
        "Content Operations Factory",
        "Turn a local brief list into a compliance hold, a revision, or an approved pack with a social cut, a newsletter cut, and a calendar slot.",
    )
    briefs = []

    def add(**kwargs):
        briefs.append(
            {
                "id": kwargs["id"],
                "topic": kwargs["topic"],
                "channel": kwargs.get("channel", "blog"),
                "words": kwargs.get("words", 900),
                "brand_score": kwargs.get("brand_score", 8),
                "risk": kwargs.get("risk", 0),
                "owner": kwargs.get("owner", "editorial"),
                "title": kwargs["topic"],
            }
        )

    add(id="B-01", topic="How a local kiln schedules a backorder", brand_score=9, words=1200)
    add(id="B-02", topic="What a same-day pickup bin looks like", brand_score=8, words=700, channel="newsletter")
    add(id="B-03", topic="A week of parcel rate shopping", brand_score=8, words=1000)
    add(id="B-04", topic="Guaranteed cure for late shipments", brand_score=6, risk=1, words=500)
    add(id="B-05", topic="Double your revenue with this ledger trick", brand_score=5, risk=1, words=400)
    add(id="B-06", topic="Risk-free returns and zero effort growth", brand_score=4, risk=1, words=350)
    add(id="B-07", topic="Why the gold tier exists", brand_score=9, words=800)
    add(id="B-08", topic="Invoice aging in plain language", brand_score=8, words=1100)
    add(id="B-09", topic="A short note on cracked mugs", brand_score=7, words=280, channel="social")
    add(id="B-10", topic="Pickup window reminders", brand_score=8, words=220, channel="social")
    add(id="B-11", topic="The collections desk, without the jargon", brand_score=6, words=900)
    add(id="B-12", topic="New SKU announcement, first draft", brand_score=5, words=600)
    add(id="B-13", topic="Carrier air versus road", brand_score=8, words=950)
    add(id="B-14", topic="How we write a customer credit", brand_score=9, words=840)
    add(id="B-15", topic="Status page wording for a checkout slowdown", brand_score=7, words=500, channel="newsletter")
    add(id="B-16", topic="Three-line social post for the spring mug", brand_score=8, words=80, channel="social")
    add(id="B-17", topic="Chargeback files, a staff primer", brand_score=6.5, words=1000)
    add(id="B-18", topic="Medical claim for better sleep from a lamp", brand_score=3, risk=1, words=450)

    flow.sticky("## Briefs\nRisk flags are claims the brand will not publish: guaranteed outcomes, risk-free money, and medical claims. They are sample briefs, not live campaigns.", -40, -250, 780, 210, 2)
    flow.sticky("## Factory\nHeld briefs stop. Weak brand scores go back to the writer. Approved briefs leave with a social cut, a newsletter cut, and a weekday slot.", 980, -250, 780, 210, 4)

    data = json.dumps(briefs)
    start = flow.manual("Run Content Factory", 0, 220)
    load = flow.code("Load Briefs", f"const briefs = {data};\nreturn briefs.map((row) => ({{ json: row }}));", 320, 220)
    score = flow.code(
        "Score Brand And Risk",
        map_js(
            "",
            """
  const riskFlag = Number(row.risk) === 1 ? 1 : 0;
  const revisionFlag = !riskFlag && Number(row.brand_score) < 7 ? 1 : 0;
  const approvedFlag = !riskFlag && !revisionFlag ? 1 : 0;
  const longform = approvedFlag && Number(row.words) >= 500 ? 1 : 0;
  let lane = "approved";
  if (riskFlag) lane = "compliance";
  else if (revisionFlag) lane = "revision";
  else if (longform) lane = "longform";
  else lane = "social";
  const action = {
    compliance: "Do not publish. Rewrite without the claim.",
    revision: "Return to the writer. Brand score is under 7.",
    longform: "Approve the outline, then cut social and newsletter versions.",
    social: "Approve the short post and put it on the calendar."
  }[lane];
  return { json: { ...row, risk_flag: riskFlag, revision_flag: revisionFlag, approved_flag: approvedFlag, longform_flag: longform, lane, action, amount: 0 } };
""",
        ),
        660, 220,
    )
    calendar = flow.code(
        "Assign Calendar Slot",
        map_js(
            "",
            """
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const index = rows.indexOf(row);
  return { json: { ...row, slot: days[index % days.length] + " 09:30" } };
""",
        ),
        980, 220,
    )
    digest = flow.code(
        "Editorial Digest",
        HASH_FN
        + """
const rows = $input.all().map((item) => item.json);
const lanes = {};
for (const row of rows) {
  if (!lanes[row.lane]) lanes[row.lane] = { count: 0, amount: 0, samples: [] };
  lanes[row.lane].count += 1;
  if (lanes[row.lane].samples.length < 3) lanes[row.lane].samples.push({ id: row.id, title: row.topic, slot: row.slot, action: row.action, brand_score: row.brand_score });
}
return [{ json: {
  project: "Content Operations Factory",
  generated_at: new Date().toISOString(),
  records: rows.length,
  lanes,
  fingerprint: fingerprint(rows.map((row) => [row.id, row.lane, row.brand_score])),
  headline: rows.length + " briefs judged locally. Compliance holds never reach the calendar as publishable copy."
} }];
""",
        1300, 220,
    )
    risk_if = flow.iff("Compliance Hold?", "={{ $json.risk_flag }}", 1, 980, 580)
    hold = flow.code(
        "Compliance Desk",
        pass_js(
            """
  next.desk = "compliance";
  next.hold_reason = "Brief contains a banned claim. Remove guaranteed, risk-free, or medical wording before another pass.";
"""
        ),
        1300, 800,
    )
    rev_if = flow.iff("Needs Revision?", "={{ $json.revision_flag }}", 1, 1300, 580)
    rev = flow.code(
        "Revision Desk",
        pass_js(
            """
  next.desk = "revision";
  next.note = "Brand score " + next.brand_score + ". Ask the writer for a second pass before cuts are made.";
"""
        ),
        1640, 800,
    )
    long_if = flow.iff("Longform?", "={{ $json.longform_flag }}", 1, 1640, 580)
    outline = flow.code(
        "Build Longform Pack",
        pass_js(
            """
  next.desk = "longform";
  next.outline = ["What the reader can do after reading", "One concrete local example", "The limit of the advice", "A single next step"];
  next.social_cut = next.topic + " — a short version for the feed. No claims beyond the brief.";
  next.newsletter_cut = "This week: " + next.topic + ". Full note is " + next.words + " words.";
"""
        ),
        1980, 460,
    )
    social = flow.code(
        "Build Social Pack",
        pass_js(
            """
  next.desk = "social";
  next.social_cut = next.topic + " (" + next.words + " words). Slot " + next.slot + ".";
"""
        ),
        1980, 860,
    )
    for a, b in [(start, load), (load, score), (score, calendar), (calendar, digest), (calendar, risk_if)]:
        flow.link(a, b)
    flow.link(risk_if, hold, 0)
    flow.link(risk_if, rev_if, 1)
    flow.link(rev_if, rev, 0)
    flow.link(rev_if, long_if, 1)
    flow.link(long_if, outline, 0)
    flow.link(long_if, social, 1)
    return flow


def build_incidents():
    flow = Flow(
        "IncidentCommand01",
        "Incident Command and Postmortem",
        "Correlate a local alert stream into incidents, open a bridge for severity 1, draft a status note for customer-facing issues, and file internal noise.",
    )
    alerts = []

    def burst(service, symptom, severity, customer, count, start_minute):
        for index in range(count):
            alerts.append(
                {
                    "id": f"A-{service[:3].upper()}-{start_minute + index}",
                    "service": service,
                    "symptom": symptom,
                    "severity": severity,
                    "customer_facing": customer,
                    "minute": start_minute + index * 2,
                    "region": "local",
                    "title": service + " " + symptom,
                }
            )

    burst("checkout-api", "latency", 1, 1, 4, 0)
    burst("ledger-worker", "crash-loop", 1, 1, 3, 20)
    burst("auth-gateway", "error-rate", 1, 1, 3, 40)
    burst("email-worker", "delay", 2, 1, 3, 60)
    burst("cdn-cache", "stale", 2, 1, 2, 80)
    burst("search-index", "typo-regression", 3, 0, 4, 100)
    burst("docs-site", "404", 4, 0, 3, 120)
    burst("billing-pdf", "slow-render", 3, 0, 3, 140)

    flow.sticky("## Alerts\nTwenty-five sample alerts. Correlation collapses repeats of the same service and symptom into one incident.", -40, -250, 700, 200, 1)
    flow.sticky("## Command\nSeverity 1 opens a bridge and a rollback note. Other customer-facing incidents get a status draft. Internal noise is filed, not paged.", 1000, -250, 760, 210, 6)

    data = json.dumps(alerts)
    start = flow.manual("Run Incident Command", 0, 220)
    load = flow.code("Load Alert Stream", f"const alerts = {data};\nreturn alerts.map((row) => ({{ json: row }}));", 320, 220)
    correlate = flow.code(
        "Correlate Into Incidents",
        f"""
const alerts = {data};
const groups = {{}};
for (const alert of alerts) {{
  const key = alert.service + "|" + alert.symptom;
  if (!groups[key]) {{
    groups[key] = {{ ...alert, id: "INC-" + alert.service, alert_count: 0, first_minute: alert.minute, last_minute: alert.minute, title: alert.service + " / " + alert.symptom }};
  }}
  groups[key].alert_count += 1;
  groups[key].first_minute = Math.min(groups[key].first_minute, alert.minute);
  groups[key].last_minute = Math.max(groups[key].last_minute, alert.minute);
  groups[key].severity = Math.min(groups[key].severity, alert.severity);
}}
return Object.values(groups).map((incident) => {{
  const sev1 = incident.severity === 1 ? 1 : 0;
  const customer = !sev1 && Number(incident.customer_facing) === 1 ? 1 : 0;
  const internal = !sev1 && !customer ? 1 : 0;
  let lane = "internal";
  if (sev1) lane = "sev1";
  else if (customer) lane = "status";
  const duration = incident.last_minute - incident.first_minute + 2;
  const action = {{
    sev1: "Open the bridge, freeze deploys, and roll back the last change if the error budget is burning.",
    status: "Draft a status note. No bridge unless it worsens to severity 1.",
    internal: "File it. Do not page the customer owner."
  }}[lane];
  return {{ json: {{ ...incident, sev1_flag: sev1, status_flag: customer, internal_flag: internal, lane, duration_minutes: duration, amount: duration, action }} }};
}});
""",
        680, 220,
    )
    impact = flow.code(
        "Estimate Customer Impact",
        pass_js(
            """
  const weight = next.customer_facing ? (next.severity === 1 ? 40 : 12) : 0;
  next.impact_score = weight * Number(next.alert_count);
  next.customer_minutes = next.customer_facing ? Number(next.duration_minutes) * (next.severity === 1 ? 25 : 8) : 0;
"""
        ),
        1020, 220,
    )
    digest = flow.code(
        "Incident Brief",
        HASH_FN
        + """
const rows = $input.all().map((item) => item.json);
const lanes = {};
let customerMinutes = 0;
let alerts = 0;
for (const row of rows) {
  if (!lanes[row.lane]) lanes[row.lane] = { count: 0, amount: 0, samples: [] };
  lanes[row.lane].count += 1;
  lanes[row.lane].amount += Number(row.customer_minutes || 0);
  alerts += Number(row.alert_count || 0);
  customerMinutes += Number(row.customer_minutes || 0);
  if (lanes[row.lane].samples.length < 3) lanes[row.lane].samples.push({ id: row.id, title: row.title, alerts: row.alert_count, action: row.action, customer_minutes: row.customer_minutes });
}
return [{ json: {
  project: "Incident Command and Postmortem",
  generated_at: new Date().toISOString(),
  records: rows.length,
  source_alerts: alerts,
  lanes,
  customer_minutes: customerMinutes,
  fingerprint: fingerprint(rows.map((row) => [row.id, row.lane, row.alert_count])),
  headline: alerts + " alerts collapsed into " + rows.length + " incidents. Customer impact is an estimate from severity and duration, not a live status page."
} }];
""",
        1360, 220,
    )
    sev_if = flow.iff("Severity 1?", "={{ $json.sev1_flag }}", 1, 1020, 580)
    bridge = flow.code(
        "Open Bridge",
        pass_js(
            """
  next.desk = "sev1";
  next.bridge = "Bridge for " + next.service + ". Freeze deploys. Owner: service on-call. First action: roll back the last change if the new error rate started after it.";
  next.runbook = ["Confirm the symptom on the local dashboard", "Freeze deploys", "Roll back the last change", "Watch the error rate for 15 minutes", "Draft the customer note if users still see failures"];
"""
        ),
        1360, 800,
    )
    post = flow.code(
        "Postmortem Stub",
        pass_js(
            """
  next.postmortem = {
    incident: next.id,
    summary: next.service + " reported " + next.symptom + " across " + next.alert_count + " alerts.",
    impact: next.customer_minutes + " estimated customer-minutes.",
    followups: ["Add an alert that pages only after the third repeat", "Write the rollback as a one-page run card"]
  };
"""
        ),
        1700, 800,
    )
    status_if = flow.iff("Customer Facing?", "={{ $json.status_flag }}", 1, 1360, 1120)
    status = flow.code(
        "Status Draft",
        pass_js(
            """
  next.desk = "status";
  next.status_note = "We are investigating slower " + next.service + " (" + next.symptom + "). Some customers may see a delay. We will update this note when the next scan is clean.";
"""
        ),
        1700, 1120,
    )
    internal = flow.code(
        "Internal File",
        pass_js(
            """
  next.desk = "internal";
  next.file_note = next.service + " / " + next.symptom + " stayed internal. No customer note.";
"""
        ),
        1700, 1420,
    )
    for a, b in [(start, load), (load, correlate), (correlate, impact), (impact, digest), (impact, sev_if)]:
        flow.link(a, b)
    flow.link(sev_if, bridge, 0)
    flow.link(bridge, post)
    flow.link(sev_if, status_if, 1)
    flow.link(status_if, status, 0)
    flow.link(status_if, internal, 1)
    return flow


def main():
    builders = [build_orders, build_revenue, build_support, build_content, build_incidents]
    manifest = []
    for builder in builders:
        flow = builder()
        path = OUT / f"{flow.wid}.json"
        flow.dump(path)
        manifest.append(
            {
                "id": flow.wid,
                "name": flow.name,
                "file": path.name,
                "nodes": len(flow.nodes),
                "description": flow.description,
            }
        )
        print(f"{flow.wid}: {len(flow.nodes)} nodes -> {path.name}")
    (OUT / "portfolio-manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
