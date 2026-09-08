import sys, os, json, time, re, math
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
