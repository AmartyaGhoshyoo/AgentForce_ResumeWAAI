import re

text = """
### 3. RESUME OPTIMIZATION GUIDE
- **Keyword Integration Recommendations:** Incorporate specific keywords such as "Generative AI," "Machine Learning," "Data Analysis," "Python," "Neural Networks," and "Deep Learning."
  
- **Layout and Formatting Improvements:** 
  - Use clean, professional layouts; consider singular font types and sizes consistently throughout.
  - Ensure sections like "Education" and "Projects" are prominent to catch attention easily.
  
- **Content Restructuring Suggestions:** Arrange content in reverse chronological order, with strong highlights on recent relevant projects.
  
- **ATS Optimization Tips:** Use common job titles and required qualifications exactly as they appear in job descriptions to increase ATS compatibility.

### 4. CUSTOMIZED COVER LETTER TEMPLATE
"""

# Allow a space after ##
pattern = r'(#+\s*3\..*?\n)(.*?)(\n#+\s*4\..*)'
match = re.search(pattern, text, re.S)

if match:
    headline_3 = match.group(1).strip()
    points_inside_3 = match.group(2).strip()
    headline_4 = match.group(3).strip()

    print("Headline 3:", headline_3)
    print("\nPoints inside 3:\n", points_inside_3)
    print("\nHeadline 4:", headline_4)
