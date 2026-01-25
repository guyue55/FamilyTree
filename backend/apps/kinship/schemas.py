"""
Kinship Schemas
"""

from typing import List, Optional
from ninja import Schema
from pydantic import Field


class KinshipCalculateRequest(Schema):
    """称呼计算请求"""
    family_tree_id: int
    from_member_id: str  # 假设ID是字符串
    to_member_id: str
    dialect: str = "standard"


class PathDetail(Schema):
    """路径详情"""
    from_id: str
    to_id: str
    relationship: str


class KinshipResponse(Schema):
    """称呼计算响应"""
    relationship_path: str
    title: str
    reverse_title: str
    generation_diff: int
    is_direct: bool
    path_details: List[PathDetail]


class KinshipTitleSchema(Schema):
    """称呼字典项"""
    relationship_path: str
    title: str
    dialect: str
    generation_diff: int
    is_direct: bool
