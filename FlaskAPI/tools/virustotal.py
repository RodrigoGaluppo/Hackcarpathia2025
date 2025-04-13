from virustotal_python import Virustotal
from base64 import urlsafe_b64encode

class VirusTotalClient:
    def __init__(self, api_key):
        self.vtotal = Virustotal(API_KEY=api_key)
    
    def analyze_url(self, url):
        with self.vtotal as vt:
            # Submit URL for analysis
            submission = vt.request("urls", data={"url": url}, method="POST")
            
            # Get analysis report
            url_id = urlsafe_b64encode(url.encode()).decode().strip("=")
            report = vt.request(f"urls/{url_id}")
            
            # Extract full malicious vendor reports
            analysis_results = report.data['attributes']['last_analysis_results']
            malicious_reports = {
                vendor: details for vendor, details in analysis_results.items()
                if details['category'] == 'malicious'
            }
            
            return {
                "url": url,
                "malicious_count": report.data['attributes']['last_analysis_stats']['malicious'],
                "malicious_reports": malicious_reports,
                "suspicious_count": report.data['attributes']['last_analysis_stats']['suspicious']
            }

