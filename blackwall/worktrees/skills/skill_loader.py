"""
Skill Loader: Loads skills from nested markdown files.
Based on whiteboard: "MCP UI implemented with nested md files"
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from .skill import Skill


class SkillLoader:
    """
    Loads skills from nested markdown files.
    Skills are defined with YAML frontmatter and markdown content.
    """
    
    def __init__(self, skills_path: Optional[Path] = None):
        """
        Initialize skill loader.
        
        Args:
            skills_path: Path to skills directory (defaults to .skills)
        """
        self.skills_path = skills_path or Path(".skills")
        self.skills_path.mkdir(parents=True, exist_ok=True)
    
    def load_skill(self, skill_file: Path) -> Optional[Skill]:
        """
        Load a skill from a markdown file.
        
        Expected format:
        ---
        name: skill-name
        description: Skill description
        version: 1.0.0
        tools: [tool1, tool2]
        resources: [resource1]
        ---
        
        # Skill Name
        
        ## Workflow
        1. Step one
        2. Step two
        
        ## Examples
        - Example 1
        - Example 2
        """
        if not skill_file.exists():
            return None
        
        try:
            content = skill_file.read_text()
            
            # Parse YAML frontmatter
            frontmatter_match = re.match(
                r'^---\s*\n(.*?)\n---\s*\n(.*)$',
                content,
                re.DOTALL
            )
            
            if not frontmatter_match:
                # Try without frontmatter
                return self._load_skill_from_content(content, skill_file)
            
            yaml_content = frontmatter_match.group(1)
            markdown_content = frontmatter_match.group(2)
            
            # Parse YAML
            frontmatter = yaml.safe_load(yaml_content) or {}
            
            # Extract workflow and examples from markdown
            workflow = self._extract_section(markdown_content, "Workflow")
            examples = self._extract_section(markdown_content, "Examples")
            
            # Create skill
            skill = Skill(
                name=frontmatter.get("name", skill_file.stem),
                description=frontmatter.get("description", ""),
                version=frontmatter.get("version", "1.0.0"),
                tools=frontmatter.get("tools", []),
                resources=frontmatter.get("resources", []),
                workflow=workflow,
                examples=examples,
                metadata=frontmatter.get("metadata", {}),
                file_path=skill_file
            )
            
            return skill
            
        except Exception as e:
            print(f"Error loading skill {skill_file}: {e}")
            return None
    
    def _load_skill_from_content(self, content: str, file_path: Path) -> Skill:
        """Load skill from content without frontmatter."""
        # Try to extract name from first heading
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = name_match.group(1) if name_match else file_path.stem
        
        workflow = self._extract_section(content, "Workflow")
        examples = self._extract_section(content, "Examples")
        
        return Skill(
            name=name,
            description="",
            tools=[],
            resources=[],
            workflow=workflow,
            examples=examples,
            file_path=file_path
        )
    
    def _extract_section(self, content: str, section_name: str) -> List[str]:
        """Extract a section from markdown content."""
        pattern = rf'##\s+{section_name}\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return []
        
        section_content = match.group(1).strip()
        
        # Extract list items
        items = []
        for line in section_content.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                items.append(line[1:].strip())
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                items.append(re.sub(r'^\d+\.\s*', '', line))
        
        return items
    
    def load_all_skills(self) -> Dict[str, Skill]:
        """
        Load all skills from the skills directory.
        Supports nested directories.
        
        Returns:
            Dictionary mapping skill names to Skill objects
        """
        skills = {}
        
        if not self.skills_path.exists():
            return skills
        
        # Recursively find all .md files
        for md_file in self.skills_path.rglob("*.md"):
            skill = self.load_skill(md_file)
            if skill:
                skills[skill.name] = skill
        
        return skills
    
    def save_skill(self, skill: Skill, skill_file: Optional[Path] = None):
        """
        Save a skill to a markdown file.
        
        Args:
            skill: Skill to save
            skill_file: Path to save to (defaults to skills_path/{name}.md)
        """
        if skill_file is None:
            skill_file = self.skills_path / f"{skill.name}.md"
        
        # Build frontmatter
        frontmatter = {
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
            "tools": skill.tools,
            "resources": skill.resources,
            "metadata": skill.metadata
        }
        
        # Build markdown content
        content_parts = [f"# {skill.name}\n"]
        
        if skill.description:
            content_parts.append(f"{skill.description}\n")
        
        if skill.workflow:
            content_parts.append("## Workflow\n")
            for i, step in enumerate(skill.workflow, 1):
                content_parts.append(f"{i}. {step}\n")
            content_parts.append("\n")
        
        if skill.examples:
            content_parts.append("## Examples\n")
            for example in skill.examples:
                content_parts.append(f"- {example}\n")
            content_parts.append("\n")
        
        # Combine
        yaml_content = yaml.dump(frontmatter, default_flow_style=False)
        markdown_content = "".join(content_parts)
        
        full_content = f"---\n{yaml_content}---\n\n{markdown_content}"
        
        skill_file.write_text(full_content)
        skill.file_path = skill_file


class SkillRegistry:
    """
    Registry for managing skills.
    Provides lookup and organization of skills.
    """
    
    def __init__(self, skills_path: Optional[Path] = None):
        """
        Initialize skill registry.
        
        Args:
            skills_path: Path to skills directory
        """
        self.loader = SkillLoader(skills_path)
        self.skills: Dict[str, Skill] = {}
        self._reload()
    
    def _reload(self):
        """Reload all skills from disk."""
        self.skills = self.loader.load_all_skills()
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict]:
        """List all registered skills."""
        return [skill.to_dict() for skill in self.skills.values()]
    
    def register_skill(self, skill: Skill):
        """Register a skill."""
        self.skills[skill.name] = skill
    
    def get_skills_by_tool(self, tool_name: str) -> List[Skill]:
        """Get all skills that use a specific tool."""
        return [skill for skill in self.skills.values() 
                if tool_name in skill.tools]
    
    def reload(self):
        """Reload skills from disk."""
        self._reload()
