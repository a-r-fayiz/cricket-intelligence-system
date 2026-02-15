# 🏏 Cricket Intelligence System (CIS)

Cricket Intelligence System (CIS) is a **Streamlit-based interactive dashboard** that provides detailed cricket statistics analysis for **India (Team ID: 6)** across formats (**Test, ODI, T20**) from **2011 to 2025**.

🚀 Live App: https://cricket-intelligence-system.streamlit.app/

---

## ✨ Features

### 🔍 Player Wise Analysis
- Player performance summary across Test, ODI, and T20
- Batting insights: Runs, Strike Rate, Average, Boundaries (4s/6s)
- Bowling insights: Wickets, Economy Rate, Bowling Average
- Interactive charts and tables

### 📊 Format Wise Analysis
- Top 5 batting performers in each format
- Top 5 bowling performers in each format
- Filter by custom year range (2011–2025)

### 📅 Year Wise Analysis
- Select a year and visualize:
  - Batting contribution distribution (Pie chart)
  - Bowling contribution distribution (Pie chart)
- Separate breakdown for Test, ODI, and T20

### ⚔️ Player Comparison
- Compare 2 players across formats
- Runs / Wickets comparison year-wise
- Batting and bowling metrics comparison

### 🧠 Optimal Team Selector (Best XI)
- Select format + year range
- Automatically generates **Best Playing XI**
- Uses **Linear Programming (PuLP)** optimization
- Assigns player roles:
  - Batter
  - Bowler

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pandas / NumPy**
- **Plotly**
- **PuLP (Linear Programming Optimization)**
- **Playwright (Web Scraping - Data Collection)**

---

## 📂 Project Structure

```bash
cricket-intelligence-system/
│── app.py
│── cricket_data.json
│── requirements.txt
│── scrap_data.py
│── convert.py
│── cricket_stats/
│   ├── test_batting_2011.csv
│   ├── test_bowling_2011.csv
│   ├── ...
│   ├── odi_batting_2025.csv
│   ├── t20_bowling_2025.csv
```

---

## ⚙️ Installation & Setup (Run Locally)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/a-r-fayiz/cricket-intelligence-system.git
cd cricket-intelligence-system
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Streamlit app
```bash
streamlit run app.py
```

---

## 📌 Data Source
The cricket statistics are scraped from:

- **ESPN Cricinfo Stats Engine**
  https://stats.espncricinfo.com/

Data includes:
- Batting statistics
- Bowling statistics
- Year-wise and format-wise records

---

## 🚀 Deployment
This project is deployed using **Streamlit Community Cloud**.

Live App Link:  
👉 https://cricket-intelligence-system.streamlit.app/

---

## 👨‍💻 Author
**Abdul Rahiman Fayiz**  
📍 Karnataka, India  

- LinkedIn: https://linkedin.com/in/abdul-rahiman-fayiz  
- Email: arfayiz02@gmail.com  

---

## ⭐ Support
If you found this project useful, consider giving it a ⭐ on GitHub!
