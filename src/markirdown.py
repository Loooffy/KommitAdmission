from markitdown import MarkItDown

class MarkdownConverter:
    def convert_markdown(self, input_file_name):
        md = MarkItDown()
        result = md.convert(input_file_name)
        return result