from flask import Flask, request, jsonify, render_template_string
from textblob import TextBlob
import datetime
import json
import os

app = Flask(__name__)

history = []

HISTORY_FILE = 'history.json'

def load_history():
    global history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
            history = history[-50:]  # cap 50
        except:
            history = []
    else:
        history = []

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except:
        pass

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Sentimind</title>

<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {
    margin: 0;
    font-family: 'Poppins', sans-serif;

    background:
        radial-gradient(circle at top left, rgba(99,102,241,0.35), transparent 40%),
        radial-gradient(circle at bottom right, rgba(168,85,247,0.35), transparent 45%),
        linear-gradient(135deg, #070716, #14142b);

    display: flex;
    color: #e5e7eb;
}

/* SIDEBAR */
.sidebar {
    width: 280px;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(20px);
    padding: 15px;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.clear-btn {
    width: 100%;
    padding: 10px;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 8px;
    margin-bottom: 10px;
    cursor: pointer;
}

/* CHAT HISTORY */
.chat {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.msg {
    padding: 10px;
    border-radius: 12px;
    max-width: 95%;
    font-size: 13px;
    line-height: 1.4;
}

.msg.positive { background: #065f46; }
.msg.negative { background: #7f1d1d; }
.msg.neutral { background: #374151; }

small { opacity: 0.7; }

/* MAIN */
.main {
    flex: 1;
    padding: 25px;
}

/* HEADER */
.title {
    font-family: Orbitron;
    font-size: 48px;
    text-align: center;
    margin: 0;
    background: linear-gradient(90deg,#60a5fa,#a855f7,#22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    font-size: 13px;
    margin-bottom: 15px;
}

/* CARDS */
.cards {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 12px;
    margin-bottom: 20px;
}

.card {
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
}

/* INPUT */
.input-box {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

input {
    flex: 1;
    padding: 12px;
    border-radius: 10px;
    background: rgba(0,0,0,0.35);
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
}

button {
    padding: 12px;
    border-radius: 10px;
    background: #3b82f6;
    color: white;
    border: none;
}

/* CHARTS */
.charts {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.chart-box {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 10px;
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* INSIGHT */
.insight {
    margin-top: 15px;
    padding: 12px;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
    font-size: 14px;
}
canvas {
    width: 100% !important;
    height: 100% !important;
}
</style>
</head>

<body>

<!-- SIDEBAR -->
<div class="sidebar">
<button class="clear-btn" onclick="clearHistory()">Clear All</button>
<div style="height:15px;"></div>
<h3 style="margin:0 0 15px 0; color:#60a5fa;">📜 HISTORY ({{total}})</h3>
<div id="history" class="chat"></div>
</div>

<!-- MAIN -->
<div class="main">

<h1 class="title">SENTIMIND</h1>
<div class="subtitle">AI SENTIMENT INTELLIGENCE ANALYZER</div>

<div class="cards">
<div class="card total">Total<br>{{total}}</div>
<div class="card positive">Positive<br>{{pos}}</div>
<div class="card negative">Negative<br>{{neg}}</div>
<div class="card neutral">Neutral<br>{{neu}}</div>
</div>

<div class="input-box">
<input id="text" placeholder="Type something...">
<button onclick="analyze()">Analyze</button>
</div>

<div class="charts">
<div class="chart-box"><canvas id="pie"></canvas></div>
<div class="chart-box"><canvas id="line"></canvas></div>
</div>

<div class="insight" id="insightBox">
Start analyzing text...
</div>

</div>

<script>
let pie, line;

function initCharts() {

pie = new Chart(document.getElementById("pie"), {
type:"doughnut",
data:{
labels:["Positive","Neutral","Negative"],
datasets:[{
data:{{pie_data|tojson}},
backgroundColor:["#22c55e","#94a3b8","#ef4444"]
}]
},
options:{
maintainAspectRatio:false,
plugins:{legend:{labels:{color:"#e5e7eb"}}}
}
});

line = new Chart(document.getElementById("line"), {
type:"line",
data:{
labels:{{line_labels|tojson}},
datasets:[{
data:{{line_data|tojson}},
borderColor:"#60a5fa",
fill:false
}]
},
options:{
maintainAspectRatio:false,
scales:{
x:{ticks:{color:"#e5e7eb"}},
y:{ticks:{color:"#e5e7eb"}}
},
plugins:{legend:{labels:{color:"#e5e7eb"}}}
}
});
}

/* HISTORY RENDER */
function renderHistory(data){
let box=document.getElementById("history");
box.innerHTML="";

data.forEach(h=>{
let div=document.createElement("div");
div.className="msg "+h.sentiment.toLowerCase();

let ai =
h.sentiment==="Positive"?"AI: Positive emotion 😊":
h.sentiment==="Negative"?"AI: Negative tone ⚠️":
"AI: Neutral statement 😐";

div.innerHTML=`${h.text}<br><small>${h.sentiment} | ${ai}</small>`;
box.appendChild(div);
});
}

/* ANALYZE */
async function analyze(){

let text=document.getElementById("text").value;
if(!text.trim()) return;
document.getElementById("insightBox").innerHTML = "🤖 Analyzing...";

let res=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
let data=await res.json();

renderHistory(data.history);

/* cards */
document.querySelector(".total").innerHTML=`Total<br>${data.total}`;
document.querySelector(".positive").innerHTML=`Positive<br>${data.pos}`;
document.querySelector(".negative").innerHTML=`Negative<br>${data.neg}`;
document.querySelector(".neutral").innerHTML=`Neutral<br>${data.neu}`;

/* charts */
pie.data.datasets[0].data=data.pie_data;
pie.update();

line.data.labels=data.line_labels;
line.data.datasets[0].data=data.line_data;
line.update();

/* insight */
document.getElementById("insightBox").innerHTML=data.insight;

document.getElementById("text").value="";
}

/* CLEAR */
async function clearHistory(){
    await fetch("/clear_history",{method:"POST"});
    renderHistory([]);
    
    document.querySelector(".total").innerHTML="Total<br>0";
    document.querySelector(".positive").innerHTML="Positive<br>0";
    document.querySelector(".negative").innerHTML="Negative<br>0";
    document.querySelector(".neutral").innerHTML="Neutral<br>0";

    pie.data.datasets[0].data=[0,0,0];
    pie.update();

    line.data.labels=[];
    line.data.datasets[0].data=[];
    line.update();

    document.getElementById("insightBox").innerHTML="Start analyzing text...";
}
const initialHistory = {{ history | tojson }};
document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    renderHistory({{history|tojson}});
    
    // Auto-update history every 3s
    setInterval(async () => {
        try {
            const res = await fetch('/history');
            const data = await res.json();
            renderHistory(data);
        } catch(e) {}
    }, 3000);
});
</script>

</body>
</html>
"""

@app.route("/")
def home():
    load_history()
    pos=sum(1 for h in history if h["sentiment"]=="Positive")
    neg=sum(1 for h in history if h["sentiment"]=="Negative")
    neu=sum(1 for h in history if h["sentiment"]=="Neutral")
    
    # Initial insight
    pos_pct = (pos / max(len(history),1)) * 100
    neg_pct = (neg / max(len(history),1)) * 100
    avg_sentiment = "Optimistic" if pos_pct > 50 else "Pessimistic" if neg_pct > 50 else "Neutral"
    insight = f"AI Insight: {pos_pct:.0f}% positive, {neg_pct:.0f}% negative ({avg_sentiment})."

    line_labels=[h["time"] for h in history[-20:]]
    line_data=[1 if h["sentiment"]=="Positive" else -1 if h["sentiment"]=="Negative" else 0 for h in history[-20:]]

    return render_template_string(HTML_PAGE,
        total=len(history),
        pos=pos,
        neg=neg,
        neu=neu,
        pie_data=[pos,neu,neg],
        line_labels=line_labels,
        line_data=line_data,
        history=history[::-1],
        insight=insight
    )

@app.route("/analyze",methods=["POST"])
def analyze():
    try:
        text = request.json.get("text", "").strip()
        if not text:
            return jsonify({"error":"Empty text"}), 400

        polarity = TextBlob(text).sentiment.polarity
        sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

        history.append({
            "text": text,
            "sentiment": sentiment,
            "time": datetime.datetime.now().strftime("%H:%M")
        })
        history[:] = history[-50:]  # cap
        save_history()

        pos = sum(1 for h in history if h["sentiment"]=="Positive")
        neg = sum(1 for h in history if h["sentiment"]=="Negative")
        neu = sum(1 for h in history if h["sentiment"]=="Neutral")

        # Enhanced insight
        recent = history[-10:]
        pos_pct = (pos / max(len(history),1)) * 100
        neg_pct = (neg / max(len(history),1)) * 100
        
        trend = "Strong positive vibe! 😊 Keep it up" if pos > neg + 2 else "Negative leaning ⚠️ Consider adjusting tone" if neg > pos + 2 else "Balanced neutral ⚖️ Steady sentiment"
        avg_sentiment = "Optimistic" if pos_pct > 50 else "Pessimistic" if neg_pct > 50 else "Neutral"
        
        insight = f"{trend}. Overall: {pos_pct:.0f}% positive, {neg_pct:.0f}% negative ({avg_sentiment})."

        line_labels = [h["time"] for h in history[-20:]]
        line_data = [1 if h["sentiment"]=="Positive" else -1 if h["sentiment"]=="Negative" else 0 for h in history[-20:]]

        return jsonify({
            "history": history[::-1],
            "pos": pos,
            "neg": neg,
            "neu": neu,
            "total": len(history),
            "pie_data": [pos, neu, neg],
            "line_labels": line_labels,
            "line_data": line_data,
            "insight": insight
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear_history",methods=["POST"])
def clear():
    global history
    history = []
    save_history()
    return jsonify({"ok":True})

@app.route("/history")
def get_history():
    load_history()
    return jsonify(history[::-1])

if __name__=="__main__":
    app.run(debug=True) this is thr frontend
