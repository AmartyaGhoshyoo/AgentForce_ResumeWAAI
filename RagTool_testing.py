from crewai_tools.tools.rag_tool import RagTool

# # Example: Loading from a file
# rag_tool = RagTool().from_file('path/to/your/file.txt')

# # Example: Loading from a directory
# rag_tool = RagTool().from_directory('path/to/your/directory')

# Example: Loading from a web page
rag_tool = RagTool().from_web_page('https://github.com/AzadTom')
rag_tool.run()