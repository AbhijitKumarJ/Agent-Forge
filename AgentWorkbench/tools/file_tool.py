from core import BaseTool

class FileTool(BaseTool):
    """A tool for reading and writing text files."""
    def use(self, filepath, content=None, mode='r'):
        try:
            if mode == 'r':
                with open(filepath, 'r') as f:
                    data = f.read()
                    print(f"[FileTool] Read from {filepath}: {data}")
                    return data
            elif mode == 'w' and content is not None:
                with open(filepath, 'w') as f:
                    f.write(content)
                    print(f"[FileTool] Wrote to {filepath}: {content}")
                    return True
            else:
                print(f"[FileTool] Invalid mode or missing content.")
                return False
        except Exception as e:
            print(f"[FileTool] Error: {e}")
            return None
