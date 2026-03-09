"""
LSP (Language Server Protocol) manager for agent system.
Checks for and manages LSP plugins for code intelligence.
"""

import subprocess
import shutil
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class LSPManager:
    """
    Manages LSP plugins and language server binaries.
    Checks availability and provides installation guidance.
    """
    
    # LSP plugin mappings from Claude documentation
    LSP_PLUGINS = {
        "python": {
            "plugin": "pyright-lsp@claude-plugins-official",
            "binary": "pyright-langserver",
            "description": "Python code intelligence"
        },
        "typescript": {
            "plugin": "typescript-lsp@claude-plugins-official",
            "binary": "typescript-language-server",
            "description": "TypeScript/JavaScript code intelligence"
        },
        "rust": {
            "plugin": "rust-analyzer-lsp@claude-plugins-official",
            "binary": "rust-analyzer",
            "description": "Rust code intelligence"
        },
        "go": {
            "plugin": "gopls-lsp@claude-plugins-official",
            "binary": "gopls",
            "description": "Go code intelligence"
        },
        "java": {
            "plugin": "jdtls-lsp@claude-plugins-official",
            "binary": "jdtls",
            "description": "Java code intelligence"
        },
        "c": {
            "plugin": "clangd-lsp@claude-plugins-official",
            "binary": "clangd",
            "description": "C/C++ code intelligence"
        },
        "cpp": {
            "plugin": "clangd-lsp@claude-plugins-official",
            "binary": "clangd",
            "description": "C/C++ code intelligence"
        },
        "csharp": {
            "plugin": "csharp-lsp@claude-plugins-official",
            "binary": "csharp-ls",
            "description": "C# code intelligence"
        },
        "lua": {
            "plugin": "lua-lsp@claude-plugins-official",
            "binary": "lua-language-server",
            "description": "Lua code intelligence"
        },
        "php": {
            "plugin": "php-lsp@claude-plugins-official",
            "binary": "intelephense",
            "description": "PHP code intelligence"
        },
        "swift": {
            "plugin": "swift-lsp@claude-plugins-official",
            "binary": "sourcekit-lsp",
            "description": "Swift code intelligence"
        }
    }
    
    def __init__(self):
        """Initialize LSP manager."""
        self.available_lsps = {}
        self.installed_plugins = {}
        self._check_available_lsps()
    
    def _check_available_lsps(self):
        """Check which language servers are available in PATH."""
        for lang, config in self.LSP_PLUGINS.items():
            binary = config["binary"]
            if shutil.which(binary):
                self.available_lsps[lang] = {
                    "binary": binary,
                    "path": shutil.which(binary),
                    "plugin": config["plugin"],
                    "description": config["description"]
                }
    
    def detect_project_languages(self, project_path: str) -> List[str]:
        """
        Detect programming languages used in a project.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            List of detected language identifiers
        """
        project = Path(project_path)
        languages = set()
        
        # Check for common files that indicate languages
        language_indicators = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "*.py"],
            "typescript": ["package.json", "tsconfig.json", "*.ts", "*.tsx"],
            "javascript": ["package.json", "*.js", "*.jsx"],
            "rust": ["Cargo.toml", "*.rs"],
            "go": ["go.mod", "go.sum", "*.go"],
            "java": ["pom.xml", "build.gradle", "*.java"],
            "c": ["*.c", "*.h"],
            "cpp": ["*.cpp", "*.hpp", "CMakeLists.txt"],
            "csharp": ["*.cs", "*.csproj"],
            "lua": ["*.lua"],
            "php": ["composer.json", "*.php"],
            "swift": ["Package.swift", "*.swift"]
        }
        
        for lang, indicators in language_indicators.items():
            for indicator in indicators:
                if indicator.startswith("*."):
                    # Check for file extension
                    ext = indicator[1:]
                    if list(project.rglob(f"*{ext}")):
                        languages.add(lang)
                else:
                    # Check for specific file
                    if (project / indicator).exists() or list(project.rglob(indicator)):
                        languages.add(lang)
        
        return list(languages)
    
    def get_required_lsps(self, languages: List[str]) -> List[Dict]:
        """
        Get required LSP plugins for detected languages.
        
        Args:
            languages: List of language identifiers
            
        Returns:
            List of LSP plugin configurations needed
        """
        required = []
        
        for lang in languages:
            if lang in self.LSP_PLUGINS:
                config = self.LSP_PLUGINS[lang]
                binary_available = lang in self.available_lsps
                
                required.append({
                    "language": lang,
                    "plugin": config["plugin"],
                    "binary": config["binary"],
                    "binary_available": binary_available,
                    "description": config["description"]
                })
        
        return required
    
    def check_lsp_status(self, language: str) -> Dict:
        """
        Check status of LSP for a language.
        
        Args:
            language: Language identifier
            
        Returns:
            Status dictionary
        """
        if language not in self.LSP_PLUGINS:
            return {
                "supported": False,
                "message": f"LSP not available for {language}"
            }
        
        config = self.LSP_PLUGINS[language]
        binary_available = language in self.available_lsps
        
        status = {
            "supported": True,
            "language": language,
            "plugin": config["plugin"],
            "binary": config["binary"],
            "binary_available": binary_available,
            "description": config["description"]
        }
        
        if not binary_available:
            status["message"] = f"Binary '{config['binary']}' not found in PATH. Install it to use LSP."
            status["install_command"] = self._get_install_command(config["binary"])
        else:
            status["message"] = f"LSP ready for {language}"
            status["binary_path"] = self.available_lsps[language]["path"]
        
        return status
    
    def _get_install_command(self, binary: str) -> str:
        """Get installation command for a language server binary."""
        install_commands = {
            "pyright-langserver": "npm install -g pyright",
            "typescript-language-server": "npm install -g typescript-language-server",
            "rust-analyzer": "rustup component add rust-analyzer",
            "gopls": "go install golang.org/x/tools/gopls@latest",
            "clangd": "brew install llvm  # or apt-get install clangd",
            "jdtls": "Download from Eclipse JDT Language Server",
            "lua-language-server": "npm install -g lua-language-server",
            "intelephense": "npm install -g intelephense",
            "sourcekit-lsp": "Included with Xcode",
            "csharp-ls": "dotnet tool install -g csharp-ls"
        }
        
        return install_commands.get(binary, f"Install {binary} manually")
    
    def generate_installation_script(self, languages: List[str]) -> str:
        """
        Generate installation script for required LSP plugins and binaries.
        
        Args:
            languages: List of languages to support
            
        Returns:
            Installation script as string
        """
        script_lines = [
            "#!/bin/bash",
            "# LSP Installation Script",
            "# Generated by Blackwall Agent System",
            "",
            "echo 'Installing LSP plugins and binaries...'",
            ""
        ]
        
        required = self.get_required_lsps(languages)
        
        # Install binaries first
        script_lines.append("# Install language server binaries")
        for req in required:
            if not req["binary_available"]:
                install_cmd = self._get_install_command(req["binary"])
                binary_name = req["binary"]
                script_lines.append(f"echo 'Installing {binary_name}...'")
                script_lines.append(f"# {install_cmd}")
                script_lines.append("")
        
        # Install Claude plugins
        script_lines.append("# Install Claude LSP plugins")
        script_lines.append("# Run these commands in Claude Code:")
        script_lines.append("")
        for req in required:
            script_lines.append(f"# /plugin install {req['plugin']}")
        
        return "\n".join(script_lines)
    
    def get_installation_commands(self, languages: List[str]) -> List[str]:
        """
        Get Claude plugin installation commands.
        
        Args:
            languages: List of languages to support
            
        Returns:
            List of /plugin install commands
        """
        required = self.get_required_lsps(languages)
        commands = []
        
        for req in required:
            commands.append(f"/plugin install {req['plugin']}")
        
        return commands
    
    def verify_lsp_setup(self, language: str) -> Tuple[bool, str]:
        """
        Verify LSP is properly set up for a language.
        
        Args:
            language: Language identifier
            
        Returns:
            Tuple of (is_ready, message)
        """
        if language not in self.LSP_PLUGINS:
            return False, f"LSP not supported for {language}"
        
        config = self.LSP_PLUGINS[language]
        binary_available = language in self.available_lsps
        
        if not binary_available:
            return False, f"Binary '{config['binary']}' not found. Install it first."
        
        # Check if plugin is installed (would need to check Claude plugin registry)
        # For now, assume plugin needs to be installed
        return True, f"LSP ready for {language}. Install plugin: {config['plugin']}"
