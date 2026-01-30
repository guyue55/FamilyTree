"""
Kinship API Controller
"""

from typing import List
from ninja import Router
from apps.common.authentication import JWTAuth
from apps.common.utils import create_success_response
from apps.common.exceptions import NotFoundError
from .schemas import (
    KinshipCalculateRequest,
    KinshipResponse,
    KinshipTitleSchema,
    BatchKinshipRequest,
    BatchKinshipResponse
)
from .services import KinshipService

router = Router(tags=["Kinship"])
service = KinshipService()


@router.post("/calculate", response=KinshipResponse, auth=None)
def calculate_kinship(request, data: KinshipCalculateRequest):
    """计算两个成员之间的称呼"""
    result = service.calculate_kinship(
        family_id=data.family_tree_id,
        from_id=data.from_member_id,
        to_id=data.to_member_id,
        dialect=data.dialect
    )
    
    if not result:
        # 如果没有找到路径，可能需要返回一个特定的状态或空结果
        # 这里为了演示，抛出 NotFoundError
        raise NotFoundError("无法计算这两个成员之间的关系（无路径连接）")
        
    return result


@router.post("/batch-calculate", response=BatchKinshipResponse, auth=None)
def batch_calculate_kinship(request, data: BatchKinshipRequest):
    """批量计算一个成员到家族中所有其他成员的称呼"""
    results = service.calculate_all_kinship(
        family_id=data.family_tree_id,
        from_id=data.from_member_id,
        dialect=data.dialect
    )
    return {"results": results}


@router.get("/titles", response=List[KinshipTitleSchema], auth=None)
def get_titles(request, dialect: str = "standard"):
    """获取称呼字典"""
    # 将服务中的字典转换为 Schema 列表
    results = []
    for path, (title, _, gen_diff) in service.TITLES.items():
        results.append({
            "relationship_path": path,
            "title": title,
            "dialect": dialect,
            "generation_diff": gen_diff,
            "is_direct": True # 简化
        })
    return results
