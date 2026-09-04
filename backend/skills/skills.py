import json
from pathlib import Path
from langchain_core.tools import tool
from pydantic import BaseModel, Field

SKILLS_DIR = Path(__file__).parent


class SkillMeta(BaseModel):
    """Skill 元数据。"""
    name: str
    description: str
    file_path: str


def _discover_skills() -> list[SkillMeta]:
    """扫描 skills 目录，发现所有 skill。"""
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        meta_file = skill_dir / "meta.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            skills.append(SkillMeta(
                name=meta["name"],
                description=meta["description"],
                file_path=str(skill_dir / "SKILL.md"),
            ))
    return skills


class LoadSkillArgs(BaseModel):
    skill_name: str = Field(description="要加载的 skill 名称")


@tool(args_schema=LoadSkillArgs)
def load_skill(skill_name: str) -> str:
    """加载指定 skill 的完整内容，获取该场景下的行为规则和工具说明。"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return f"Skill '{skill_name}' 不存在"

    content = skill_file.read_text(encoding="utf-8")
    return content[:3000]


@tool
def list_skills() -> str:
    """列出所有可用的 skill 及其描述。"""
    skills = _discover_skills()
    if not skills:
        return "暂无可用 skill"
    return "\n".join(f"- {s.name}: {s.description}" for s in skills)


SKILL_TOOLS = [load_skill, list_skills]