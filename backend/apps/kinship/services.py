"""
Kinship Services

核心称呼计算逻辑。
目前实现一个简化版，基于图搜索（BFS）查找最短路径，并根据路径特征计算称呼。
"""

from typing import List, Dict, Optional, Tuple, Set
from collections import deque
from loguru import logger

from apps.relationships.models import Relationship
from apps.members.models import Member
from .schemas import PathDetail


class KinshipService:
    """称呼计算服务"""

    # 简化版称呼字典 (Standard Dialect)
    # Key: 路径特征字符串 (e.g., "parent,parent")
    # Value: (Title, ReverseTitle, GenerationDiff)
    # 路径代号: F(Father), M(Mother), H(Husband), W(Wife), S(Son), D(Daughter), B(Brother), Z(Sister)
    # 为了简化，我们先用 generic terms: parent, child, spouse, sibling
    TITLES = {
        # 直系
        "parent": ("父亲/母亲", "儿子/女儿", 1),
        "child": ("儿子/女儿", "父亲/母亲", -1),
        "spouse": ("配偶", "配偶", 0),
        "sibling": ("兄弟姐妹", "兄弟姐妹", 0),
        
        # 祖辈
        "parent,parent": ("祖父母/外祖父母", "孙子女/外孙子女", 2),
        "child,child": ("孙子女/外孙子女", "祖父母/外祖父母", -2),
        
        # 叔伯姑舅姨
        "parent,sibling": ("叔伯姑舅姨", "侄子侄女/外甥外甥女", 1),
        "sibling,child": ("侄子侄女/外甥外甥女", "叔伯姑舅姨", -1),
        
        # 堂表亲
        "parent,sibling,child": ("堂表兄弟姐妹", "堂表兄弟姐妹", 0),
    }

    def calculate_kinship(
        self, family_id: int, from_id: str, to_id: str, dialect: str = "standard"
    ) -> Dict:
        """
        计算两个成员之间的称呼
        
        Args:
            family_id: 族谱ID
            from_id: 起始成员ID
            to_id: 目标成员ID
            dialect: 方言 (暂未实现多方言)
            
        Returns:
            Dict: 包含称呼、反向称呼、世代差等信息的字典
        """
        if from_id == to_id:
            return {
                "relationship_path": "self",
                "title": "自己",
                "reverse_title": "自己",
                "generation_diff": 0,
                "is_direct": True,
                "path_details": []
            }

        # 1. 构建图
        graph = self._build_graph(family_id)
        
        # 2. 查找最短路径 (BFS)
        path = self._find_shortest_path(graph, from_id, to_id)
        
        if not path:
            return None

        # 3. 解析路径并生成结果
        return self._resolve_path_to_title(path, from_id, to_id)

    def calculate_all_kinship(self, family_id: int, from_id: str, dialect: str = "standard") -> Dict[str, Dict]:
        """
        计算一个成员到家族中所有其他成员的称呼
        """
        # 1. 构建图
        graph = self._build_graph(family_id)
        
        # 2. 单次BFS计算所有最短路径
        all_paths = self._find_all_paths(graph, str(from_id))
        
        results = {}
        for target_id, path in all_paths.items():
            if target_id == str(from_id):
                continue
                
            # 3. 解析路径
            if path:
                result = self._resolve_path_to_title(path, from_id, target_id)
                if result:
                    results[target_id] = result
                
        return results

    def _build_graph(self, family_id: int) -> Dict[str, List[Dict]]:
        """
        构建家族关系图
        Returns:
            Dict: {member_id: [{target_id, type, direction}]}
        """
        relationships = Relationship.objects.filter(family_id=family_id)
        graph = {}
        
        for rel in relationships:
            # 统一转为字符串ID，避免类型不匹配
            from_id = str(rel.from_member_id)
            to_id = str(rel.to_member_id)
            
            # 添加正向边
            if from_id not in graph:
                graph[from_id] = []
            graph[from_id].append({
                "target": to_id,
                "type": rel.relationship_type,
                "direction": "out"
            })
            
            # 添加反向边
            if to_id not in graph:
                graph[to_id] = []
            
            reverse_type = self._get_reverse_type(rel.relationship_type)
            graph[to_id].append({
                "target": from_id,
                "type": reverse_type,
                "direction": "in"
            })
            
        return graph

    def _get_reverse_type(self, rel_type: str) -> str:
        """获取反向关系类型"""
        mapping = {
            "parent": "child",
            "child": "parent",
            "spouse": "spouse",
            "sibling": "sibling",
        }
        return mapping.get(rel_type, "unknown")

    def _find_shortest_path(self, graph: Dict, start: str, end: str) -> List[Dict]:
        """BFS 查找最短路径"""
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            if current == end:
                return path
            
            if current in graph:
                for edge in graph[current]:
                    neighbor = edge["target"]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = path + [{
                            "from": current,
                            "to": neighbor,
                            "type": edge["type"]
                        }]
                        queue.append((neighbor, new_path))
        
        return None

    def _find_all_paths(self, graph: Dict, start: str) -> Dict[str, List[Dict]]:
        """
        BFS 查找从起点到所有可达节点的路径
        
        Returns:
            Dict: {target_id: path_list}
        """
        paths = {start: []}
        queue = deque([start])
        visited = {start}
        
        while queue:
            current = queue.popleft()
            current_path = paths[current]
            
            if current in graph:
                for edge in graph[current]:
                    neighbor = edge["target"]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = current_path + [{
                            "from": current,
                            "to": neighbor,
                            "type": edge["type"]
                        }]
                        paths[neighbor] = new_path
                        queue.append(neighbor)
        
        return paths

    def _resolve_path_to_title(self, path: List[Dict], from_id: str, to_id: str) -> Dict:
        """将路径转换为称呼"""
        # 生成路径特征字符串
        path_types = [step["type"] for step in path]
        path_key = ",".join(path_types)
        
        # 查找字典
        # 简单匹配，实际应该更复杂（考虑性别）
        title_info = self.TITLES.get(path_key)
        
        if not title_info:
            # 尝试根据世代差推断
            return self._infer_by_generation(path, from_id, to_id)
            
        title, reverse_title, gen_diff = title_info
        
        # 获取性别信息以细化称呼
        try:
            target_member = Member.objects.get(id=to_id)
            from_member = Member.objects.get(id=from_id)
            
            # 这里可以添加更细致的逻辑，例如 "父亲/母亲" 根据 target 性别变为 "父亲" 或 "母亲"
            if "/" in title:
                parts = title.split("/")
                if len(parts) == 2:
                    title = parts[0] if target_member.gender == 'male' else parts[1]
            
            if "/" in reverse_title:
                parts = reverse_title.split("/")
                if len(parts) == 2:
                    reverse_title = parts[0] if from_member.gender == 'male' else parts[1]
                    
        except Member.DoesNotExist:
            pass

        path_details = [
            PathDetail(from_id=step["from"], to_id=step["to"], relationship=step["type"])
            for step in path
        ]

        return {
            "relationship_path": path_key,
            "title": title,
            "reverse_title": reverse_title,
            "generation_diff": gen_diff,
            "is_direct": "spouse" not in path_key and "sibling" not in path_key, # 粗略判断
            "path_details": path_details
        }

    def _infer_by_generation(self, path: List[Dict], from_id: str, to_id: str) -> Dict:
        """根据世代差推断通用称呼"""
        gen_diff = 0
        for step in path:
            if step["type"] == "parent":
                gen_diff += 1
            elif step["type"] == "child":
                gen_diff -= 1
        
        title = "长辈" if gen_diff > 0 else "晚辈"
        if gen_diff == 0:
            title = "平辈"
            
        path_details = [
            PathDetail(from_id=step["from"], to_id=step["to"], relationship=step["type"])
            for step in path
        ]
        
        return {
            "relationship_path": "complex",
            "title": f"{title} ({gen_diff}代)",
            "reverse_title": "相关亲属",
            "generation_diff": gen_diff,
            "is_direct": False,
            "path_details": path_details
        }
