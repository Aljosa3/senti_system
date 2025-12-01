"""
FAZA 11 — AST Patch Template
Defines standard patch structures for safe transformations.
"""

class ASTPatchTemplate:
    @staticmethod
    def rename_function(old: str, new: str):
        return {
            "action": "rename_function",
            "old": old,
            "new": new
        }
