"""
code_context — unified code context builder for LLM prompts.

Primary entry point:
    from utils.code_context import CodeContextBuilder, OutputMode

    result = CodeContextBuilder(project_root="/path", output_mode="signatures").build()
"""

from .code_context import (
    ASTAnalyzer,
    ClassInfo,
    CodeContextBuilder,
    CodeContextConfig,
    CodeContextResult,
    CodeExtractor,
    DirectoryTree,
    FileDiscovery,
    FileNode,
    FunctionCallAnalyzer,
    FunctionCallGraph,
    FunctionCallInfo,
    FunctionInfo,
    ModuleAST,
    OutputMode,
    SignatureBlock,
    SignatureExtractor,
)

__all__ = [
    "ASTAnalyzer",
    "ClassInfo",
    "CodeContextBuilder",
    "CodeContextConfig",
    "CodeContextResult",
    "CodeExtractor",
    "DirectoryTree",
    "FileDiscovery",
    "FileNode",
    "FunctionCallAnalyzer",
    "FunctionCallGraph",
    "FunctionCallInfo",
    "FunctionInfo",
    "ModuleAST",
    "OutputMode",
    "SignatureBlock",
    "SignatureExtractor",
]
