## Requirements
- Python 3.11+
- A proxy list file in the format `ip:port:user:pass` (e.g. for 10,000 views, 50 good proxies is usually enough).
  
   _Tip: You can buy 100 proxies for less than $5 at [webshare.io](https://www.webshare.io/)_


## Installation
1. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python main.py
   ```

## Notes
- The stronger your CPU, the more threads (views) you can run at once.
- Make sure your proxies are working and not blocked.

## Files
- `main.py` – main program file
- `requirements.txt` – required libraries
- `proxies.txt` – your proxy list (ip:port:user:pass)

---
**Disclaimer:**
This project is for educational purposes only. The author takes no responsibility for any use or misuse of this code. Use at your own risk.