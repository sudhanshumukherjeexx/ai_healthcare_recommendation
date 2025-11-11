# Phoenix AI Recommendation Engine

An intelligent AI-powered wellness recommendation system that analyzes comprehensive health data to provide personalized supplement and peptide recommendations.

## 🎯 What It Does

The Phoenix AI system:
- 📊 **Analyzes 8 data sources** (500+ users, 59,000+ health records)
- 🤖 **Uses OpenAI GPT-4o-mini** to generate personalized recommendations
- 💊 **Recommends power-packed supplement stacks** with specific dosages
- 🧬 **Suggests therapeutic peptides** (BPC-157, TB-500, Semax, etc.)
- 🧠 **Provides nootropic recommendations** for cognitive enhancement
- 🏥 **Includes lifestyle tips** for sleep, exercise, nutrition, and stress management
- ✅ **Personalizes to individual health** (sleep quality, HRV, activity, medications)

## ⚡ Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Get Recommendations

```bash
# Option A: Command Line (fastest)
python agent.py -u ecb00e33-3b89-4ca0-b5ca-34dfe47809a9

# Option B: Web App (interactive)
streamlit run app.py

# Option C: Python Script
python -c "from rec_engine import build_recommendations; print(build_recommendations('user-id'))"
```

## 📋 Use Cases

### Use Case 1: Quick Recommendation for a User

```bash
python agent.py -u ecb00e33-3b89-4ca0-b5ca-34dfe47809a9
```

**Output:** Personalized recommendations in 4 sections with specific dosages.

---

### Use Case 2: Get Recommendations as JSON

```bash
python agent.py -u user-id > recommendations.json
```

**Output:** Structured JSON with all recommendation details and source data.

---

### Use Case 3: Web Interface (Interactive)

```bash
streamlit run app.py
```

1. Open browser to `http://localhost:8501`
2. Enter a user ID
3. View formatted recommendations
4. See which data sources were used

---

### Use Case 4: List Available Users

```bash
python -c "from rec_engine import DataBundle; b = DataBundle.load(); print(b.pilot_user['user_id'].unique()[:10])"
```

**Output:** First 10 available user IDs.

---

### Use Case 5: Verify Data Loading

```bash
python verify_data.py
```

**Output:**
```
Pilot user data:      (500, 9)        ✅ LOADED
Lab results:         (10593, 10)       ✅ LOADED
Wearable data:       (45000, 8)        ✅ LOADED
... and more
```

---

### Use Case 6: Batch Process Users (Python)

```python
from rec_engine import build_recommendations

user_ids = ['user1', 'user2', 'user3']

for user_id in user_ids:
    result = build_recommendations(user_id)
    print(f"User: {user_id}")
    print(f"Engine: {result['engine']}")
    print(f"Recommendations:\n{result['recommendations_text']}\n")
```

---

### Use Case 7: Check Data for a Specific User

```python
from rec_engine import DataBundle, extract_user_profile

bundle = DataBundle.load()
profile = extract_user_profile(bundle, 'user-id')

# View collected signals
print(profile['signals'])
```

---

## 🏗️ System Architecture

```
User ID Input
    ↓
Load Data (8 CSV files + 1 Excel file)
    ├─ pilot_user_data.csv (demographics)
    ├─ structured_lab_results.csv (biomarkers)
    ├─ wearable_daily_aggregates.csv (sleep, HRV, steps)
    ├─ microbiome_summary.csv (gut health)
    ├─ metabolomics_summary.csv (metabolites)
    ├─ genomic_summary.csv (genetic markers)
    ├─ medication_history.csv (current meds)
    ├─ surveys_adherence_logs.csv (preferences)
    └─ main.xlsx (peptide catalog)
    ↓
Extract User Profile
    ├─ Demographic data
    ├─ Lab biomarkers (Vitamin D, CRP, HbA1c, etc.)
    ├─ Wearable metrics (sleep hours, HRV, resting HR, steps)
    ├─ Genetic information
    ├─ Current medications
    └─ Health preferences
    ↓
Generate Recommendations
    ├─ LLM (Primary): GPT-4o-mini with comprehensive prompt
    └─ Rule-based (Fallback): If API unavailable
    ↓
Output (4 Sections)
    ├─ Power-Packed Supplement Stack (with dosages)
    ├─ Therapeutic Peptides (BPC-157, TB-500, Semax, etc.)
    ├─ Nootropics (L-Theanine, Rhodiola, Bacopa, etc.)
    └─ General Wellness Tips (sleep, exercise, nutrition, stress)
```

## 📊 Data Sources

| File | Records | Purpose |
|------|---------|---------|
| pilot_user_data.csv | 500 | Demographics (age, sex, weight, BMI) |
| structured_lab_results.csv | 10,593 | Lab biomarkers (Vitamin D, CRP, etc.) |
| wearable_daily_aggregates.csv | 45,000 | Sleep, HRV, resting HR, steps |
| microbiome_summary.csv | 2,500 | Bacterial composition |
| metabolomics_summary.csv | 500 | Metabolite concentrations |
| genomic_summary.csv | 500 | Genetic markers |
| medication_history.csv | 1,038 | Current medications/supplements |
| surveys_adherence_logs.csv | 6,154 | User preferences and goals |
| main.xlsx | 58,583 | Peptide catalog |

**Total: 59,286+ health records**

## 🔑 Configuration

### .env File

Create a `.env` file in the root directory:

```properties
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

**Important:** 
- No spaces around `=` sign
- No quotes around the API key
- Correct format: `KEY=value`

**Getting an API Key:**
1. Visit https://platform.openai.com
2. Sign in or create an account
3. Go to API keys section
4. Generate a new secret key
5. Add to `.env` file

## 📦 Installation

### Requirements
- Python 3.8+
- pip

### Setup

```bash
# Clone/navigate to project
cd d:\Dev\Phoenix-AI

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Configuration section above)
echo "OPENAI_API_KEY=your-key" > .env

# Verify installation
python verify_data.py
```

## 🚀 Usage

### Option 1: Command Line (Recommended for Quick Use)

```bash
# Get recommendations
python agent.py -u <user-id>

# Example
python agent.py -u ecb00e33-3b89-4ca0-b5ca-34dfe47809a9
```

### Option 2: Web Interface (Recommended for Exploration)

```bash
# Start Streamlit app
streamlit run app.py

# Opens at http://localhost:8501
```

Features:
- User ID input field
- Real-time recommendations
- Data source tracking
- Error handling

### Option 3: Python API (Recommended for Integration)

```python
from rec_engine import build_recommendations

# Get recommendations
result = build_recommendations("user-id")

# Check which engine was used
engine = result.get("engine")  # "llm" or "rule_based"

# Get recommendations text
recommendations = result.get("recommendations_text")

print(recommendations)
```

## 📋 Output Format

### Recommendation Structure (4 Sections)

```
### 1. POWER-PACKED SUPPLEMENT STACK
- Vitamin D3: 2000-4000 IU daily
- Magnesium Glycinate: 200-400 mg daily
- Omega-3 Fatty Acids: 1000-2000 mg daily
[... more supplements with dosages ...]

### 2. THERAPEUTIC PEPTIDES
- BPC-157: 200-500 mcg daily (tissue repair)
- NAD+: 250-500 mg daily (cellular energy)
- Semax: 300-600 mcg daily (cognitive enhancement)
[... more peptides ...]

### 3. NOOTROPICS
- L-Theanine: 100-200 mg daily
- Rhodiola Rosea: 200-400 mg daily
- Bacopa Monnieri: 300-600 mg daily
[... more nootropics ...]

### 4. GENERAL WELLNESS TIPS
- Sleep Optimization: 7-9 hours daily
- Exercise: 150+ minutes per week
- Stress Management: Meditation/yoga daily
- Nutrition: Whole foods, balanced diet
```

## ⚠️ Important Disclaimers

**This system is for informational purposes only:**
- ❌ NOT a substitute for professional medical advice
- ❌ NOT a replacement for healthcare provider consultation
- ⚠️ Always consult a qualified clinician before starting any supplements
- ⚠️ Check for interactions with current medications
- ⚠️ Verify peptide legality and sourcing in your region

All recommendations include explicit disclaimers reminding users to consult healthcare professionals.

## 🛠️ Troubleshooting

### Issue: "User ID not found"

```bash
# List available users
python -c "from rec_engine import DataBundle; b = DataBundle.load(); print(b.pilot_user['user_id'].unique()[:5])"

# Use one of the listed IDs
```

### Issue: "API key error"

```bash
# Check .env format
cat .env

# Should show: OPENAI_API_KEY=sk-proj-...
# NOT: OPENAI_API_KEY = "sk-proj-..."

# Verify key loads
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(len(os.getenv('OPENAI_API_KEY', '')))"
```

### Issue: "Data files not found"

```bash
# Verify data directory structure
ls -R data/

# Should see:
# data/pilot_user_data.csv
# data/structured_lab_results.csv
# etc.
```

### Issue: "Module not found"

```bash
# Install missing package
pip install -r requirements.txt

# Specific package
pip install openai pandas streamlit python-dotenv openpyxl
```

## 📊 Example Output

### For User 1 (Active, Good Sleep, High HRV)

```
POWER-PACKED SUPPLEMENT STACK:
✅ Vitamin D3: 2000-4000 IU daily
✅ CoQ10: 100-200 mg daily (maintenance)
✅ Omega-3: 1000-2000 mg daily

THERAPEUTIC PEPTIDES:
✅ BPC-157: 200-500 mcg daily
✅ NAD+: 250-500 mg daily

NOOTROPICS:
✅ L-Theanine: 100-200 mg daily
✅ Bacopa: 300-600 mg daily

GENERAL WELLNESS:
✅ Continue 10K+ steps daily
✅ Sleep: 7-9 hours (maintain)
✅ Stress: Consider meditation
```

### For User 2 (Low Activity, Low HRV, Poor Sleep)

```
POWER-PACKED SUPPLEMENT STACK:
🎯 Magnesium: 200-400 mg daily (EMPHASIZED for HRV)
🎯 Vitamin D3: 1000-2000 IU daily
🎯 Omega-3: 1000-2000 mg daily (anti-inflammatory)
🎯 L-Theanine: 100-200 mg daily (stress support)

THERAPEUTIC PEPTIDES:
🎯 BPC-157: 200-300 mcg daily (recovery)
🎯 Semax: 300-600 mcg daily (cognitive support)
🎯 NAD+: 250-500 mg daily (energy)

NOOTROPICS:
🎯 Rhodiola: 200-400 mg daily (fatigue)
🎯 Lion's Mane: 500-1000 mg daily (cognition)

GENERAL WELLNESS:
🎯 INCREASE steps to 10,000 daily
🎯 Sleep: Optimize with dark room, consistency
🎯 Stress: 10-15 min daily meditation (HRV focus)
```

## 🔄 How Recommendations Are Generated

1. **Data Collection**: System gathers health data from all 9 files
2. **Profile Extraction**: Aggregates into user health signals
3. **Analysis**: Identifies patterns and health needs
4. **Recommendation Generation**:
   - Primary: OpenAI API (GPT-4o-mini) - personalized, sophisticated
   - Fallback: Rule-based engine (if API unavailable) - basic recommendations
5. **Output**: 4-section format with specific dosages and disclaimers

## 📞 Common Questions

**Q: How personalized are the recommendations?**
A: Fully personalized to user's sleep, HRV, activity, lab biomarkers, genetic markers, current medications, and preferences.

**Q: Can I use this without an API key?**
A: Yes! The system falls back to rule-based recommendations if API is unavailable, but LLM recommendations are more sophisticated.

**Q: How long does it take to generate recommendations?**
A: 2-5 seconds with API, instant with fallback engine.

**Q: Are these medical recommendations?**
A: No. These are informational wellness suggestions only. Always consult healthcare professionals.

**Q: What if I want to add more users?**
A: Add data to the CSV files in the `data/` directory. The system will automatically load new records.

## 🚀 Production Deployment

For production use:

1. **Set environment variable** instead of .env file:
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

2. **Deploy with Streamlit Cloud**:
   ```bash
   streamlit run app.py --logger.level=error
   ```

3. **Or deploy as API** (FastAPI/Flask):
   ```python
   from flask import Flask
   from rec_engine import build_recommendations
   
   app = Flask(__name__)
   
   @app.route('/recommend/<user_id>')
   def recommend(user_id):
       return build_recommendations(user_id)
   
   if __name__ == '__main__':
       app.run(debug=False)
   ```

## 📄 Files

```
d:\Dev\Phoenix-AI\
├── README.md                          # This file
├── rec_engine.py                      # Core recommendation engine
├── agent.py                           # CLI interface
├── app.py                             # Streamlit web app
├── .env                               # Configuration (API key)
├── .env.example                       # Example configuration
├── requirements.txt                   # Python dependencies
├── verify_data.py                     # Data verification script
├── main.xlsx                          # Peptide catalog (58K+ peptides)
└── data/
    ├── pilot_user_data.csv            # 500 users
    ├── structured_lab_results.csv     # 10K+ lab results
    ├── wearable_daily_aggregates.csv  # 45K+ wearable records
    ├── microbiome_summary.csv         # 2.5K records
    ├── metabolomics_summary.csv       # 500 profiles
    ├── genomic_summary.csv            # 500 profiles
    ├── medication_history.csv         # 1K medications
    └── surveys_adherence_logs.csv     # 6K survey responses
```

## ✅ Version Information

- **Python**: 3.8+
- **OpenAI API**: gpt-4o-mini
- **Status**: Production Ready ✅
- **Last Updated**: November 11, 2025

## 📝 License

For internal use - Phoenix AI project.

---

**Start using:**
```bash
python agent.py -u ecb00e33-3b89-4ca0-b5ca-34dfe47809a9
```

**Questions?** Check the Troubleshooting section above.
