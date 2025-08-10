import re

text = """
## 3. RESUME OPTIMIZATION GUIDE 
- **Keyword Integration Recommendations:**  
  - Incorporate keywords such as "deep learning," "data analysis," "supervised learning," and "neural networks" to enhance ATS visibility.  
- **Layout and Formatting Improvements:**  
  - Utilize standard headings (e.g., Experience, Education, Skills) for better ATS compatibility.  
  - Ensure consistent font size and type throughout the document.  
- **Content Restructuring Suggestions:**  
  - Prioritize listing internships before education to highlight relevant experience.  
- **ATS Optimization Tips:**  
  - Use bullet points for job responsibilities and achievements.  
  - Avoid images or unusual formatting that ATS could misinterpret.  

---

## 4. CUSTOMIZED COVER LETTER TEMPLATE ##  
"""

# Allow a space after ##
pattern = r'(.*\s*3\..*?\n)(.*?)(\n.*\s*4\..*)'
match = re.search(pattern, text, re.S)

if match:
    headline_3 = match.group(1).strip()
    points_inside_3 = match.group(2).strip()
    headline_4 = match.group(3).strip()

    print("Headline 3:", headline_3)
    print("\nPoints inside 3:\n", points_inside_3)
    print("\nHeadline 4:", headline_4)
