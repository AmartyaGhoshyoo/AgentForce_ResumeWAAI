try :
    from crewai.tools import BaseTool 
    print('Imported successfully')
except ImportError as e:
    print(e)
try:
    from crewai_tools import PDFSearchTool, DOCXSearchTool
    print("Imported Successfully")
except ImportError as e:
    print(e)

