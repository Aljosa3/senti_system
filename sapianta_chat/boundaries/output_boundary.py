"""
Output Boundary — explicit end of Chat responsibility.
"""

class OutputBoundary:
    def close(self, intent):
        return intent
