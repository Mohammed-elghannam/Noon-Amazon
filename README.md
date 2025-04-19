# NOON vs Amazon Price Comparison

This project aims to **compare discounts and prices between Noon and Amazon** to gain insights into pricing strategies and deals offered by both e-commerce platforms.

## Project Overview

1. **Data Collection**  
   - Scraped data from both **Noon** and **Amazon** websites.
   - Raw CSV files are stored in the respective folders:
     - `noon/`
     - `amazon/`

2. **Data Preparation**  
   - Used Jupyter Notebooks to:
     - Clean and preprocess the data.
     - Combine the datasets into a unified format.
   - Cleaned and processed data are saved in the `Processed Data/` folder.

3. **Analysis & Visualization**  
   - A Power BI dashboard was created to:
     - Visualize price distributions.
     - Compare discounts across platforms.
     - Highlight product-wise pricing insights.
   - The Power BI file is available in the `power bi/` folder as `noon&amazon.pbix`.

## 📁 Project Structure

```text
NOON_AMAZON/
├── Notebooks/
│   ├── Data_Preperation.ipynb
│   ├── Preprocessing&Cleaning.ipynb
│   ├── amazon.py
│   └── noon.py
│
├── Processed Data/
│   ├── noon_combined.csv
│   ├── amazon_electronics.csv
│   ├── combined_electronics.csv
│   └── final_result.csv
│
├── noon/
│   └── [Raw CSV files related to Noon]
│
├── amazon/
│   └── [Raw CSV files related to Amazon]
│
└── power bi/
    └── noon&amazon.pbix
```


## Tools & Technologies

- **Python** (Pandas, selenium, etc.)
- **Jupyter Notebooks**
- **Power BI**

## Author
Mohammed Elghannam  
Computer Science Student | Data Enthusiast 

- Kaggle Account: [https://www.kaggle.com/mohamedelghannam15](https://www.kaggle.com/mohamedelghannam15)
- Dataset: [https://www.kaggle.com/datasets/mohamedelghannam15/noon-and-amazon/data](https://www.kaggle.com/datasets/mohamedelghannam15/noon-and-amazon/data)

 
