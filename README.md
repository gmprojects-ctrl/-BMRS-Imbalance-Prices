# BMRS Imbalance-Prices
Project for a certain company


### TODO
[X] - Create an API caller

[X] - Clean the inputs and produce two half hourly time series

[X] - Generate a message that provides the total daily imbalance cost and the daily imbalance unit rate.

[X] - Report which Hour had the highest absolute imbalance volumes.

[X] - Extra analysis or plotting will be appreciated.


### TO RUN

1.) Create a virtual environment in Python and install the requirements.txt

2.) In the virtual environment and inside the folder rune

```sh

python -m streamlit run app.py
```

### Sources
https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/settlement/system-prices/%7BsettlementDate%7D


https://quoteddata.com/wp-content/uploads/2021/06/210630-Elexon-Imbalance-Pricing-Guidance-Note.pdf