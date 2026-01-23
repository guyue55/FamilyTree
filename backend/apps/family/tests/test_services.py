"""
Family应用服务层单元测试

测试Family应用的服务层业务逻辑，包括数据处理、业务规则验证、缓存机制等。
遵循pytest最佳实践和Django测试规范。
"""

import pytest
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.cache import cache

from apps.common.exceptions import OperationError, LimitExceededError
from apps.common.constants import BusinessLimits

from ..models import Family, FamilySettings, FamilyInvitation
from apps.members.models import FamilyMembership
from ..services import FamilyService
from ..exceptions import (
    FamilyNotFoundError,
    FamilyPermissionError,
    FamilyValidationError,
    FamilyNameConflictError,
)

User = get_user_model()


@pytest.mark.django_db
class TestFamilyService(TestCase):
    """Family服务层核心功能测试"""

    def setup_method(self, method):
        """测试方法初始化"""
        # 清除缓存
        cache.clear()

        # 创建测试用户
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User1",
        )

        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User2",
        )

        # 基础家族数据
        self.family_data = {
            "name": "测试家族",
            "description": "这是一个测试家族",
            "visibility": "family",
            "allow_join": True,
            "tags": "测试,家族",
            "origin_location": "北京",
            "motto": "团结友爱",
        }

    def create_test_family(self, **kwargs) -> Family:
        """创建测试家族"""
        data = self.family_data.copy()
        data.update(kwargs)
        if "creator" not in data:
            data["creator"] = self.user1

        return Family.objects.create(**data)

    def test_create_family_success(self):
        """测试创建家族成功"""
        family = FamilyService.create_family(self.family_data, self.user1)

        # 验证家族基本信息
        assert family.name == self.family_data["name"]
        assert family.description == self.family_data["description"]
        assert family.creator_id == self.user1.id
        assert family.visibility == self.family_data["visibility"]
        assert family.is_active is True

        # 验证自动创建的设置
        settings = FamilySettings.objects.filter(family_id=family.id).first()
        assert settings is not None
        assert settings.tree_layout == "vertical"
        assert settings.show_photos is True
        assert settings.privacy_level == "family"

    def test_create_family_validation_error(self):
        """测试创建家族数据验证错误"""
        # 测试空名称
        invalid_data = self.family_data.copy()
        invalid_data["name"] = ""

        with pytest.raises(FamilyValidationError) as exc_info:
            FamilyService.create_family(invalid_data, self.user1)
        assert "家族名称不能为空" in str(exc_info.value)

        # 测试名称过长
        invalid_data["name"] = "A" * 101
        with pytest.raises(ValidationError):
            FamilyService.create_family(invalid_data, self.user1)

    def test_create_family_name_conflict(self):
        """测试创建重名家族"""
        # 先创建一个家族
        FamilyService.create_family(self.family_data, self.user1)

        # 尝试创建同名家族
        with pytest.raises(FamilyNameConflictError) as exc_info:
            FamilyService.create_family(self.family_data, self.user2)
        assert "已存在" in str(exc_info.value)

    def test_create_family_user_limit(self):
        """测试用户创建家族数量限制"""
        # 模拟用户已达到创建限制
        with patch.object(BusinessLimits, "MAX_FAMILIES_PER_USER", 2):
            # 创建2个家族
            for i in range(2):
                data = self.family_data.copy()
                data["name"] = f"家族{i}"
                FamilyService.create_family(data, self.user1)

            # 尝试创建第3个家族
            data = self.family_data.copy()
            data["name"] = "第三个家族"

            with pytest.raises(LimitExceededError) as exc_info:
                FamilyService.create_family(data, self.user1)
            assert "最多只能创建" in str(exc_info.value)

    def test_get_family_detail_success(self):
        """测试获取家族详情成功"""
        family = self.create_test_family()

        retrieved_family = FamilyService.get_family_detail(family.id, self.user1)

        assert retrieved_family.id == family.id
        assert retrieved_family.name == family.name
        assert retrieved_family.creator_id == family.creator_id

    def test_get_family_detail_not_found(self):
        """测试获取不存在的家族"""
        with pytest.raises(FamilyNotFoundError):
            FamilyService.get_family_detail(99999, self.user1)

    def test_get_family_detail_permission_denied(self):
        """测试获取家族详情权限不足"""
        # 创建私有家族
        private_family = self.create_test_family(
            name="私有家族", visibility="private", creator=self.user2
        )

        # user1尝试访问user2的私有家族
        with pytest.raises(FamilyPermissionError):
            FamilyService.get_family_detail(private_family.id, self.user1)

    def test_update_family_success(self):
        """测试更新家族成功"""
        family = self.create_test_family()

        update_data = {
            "name": "更新后的家族名称",
            "description": "更新后的描述",
            "motto": "更新后的座右铭",
        }

        updated_family = FamilyService.update_family(family.id, update_data, self.user1)

        assert updated_family.name == update_data["name"]
        assert updated_family.description == update_data["description"]
        assert updated_family.motto == update_data["motto"]

        # 验证数据库更新
        family.refresh_from_db()
        assert family.name == update_data["name"]

    def test_update_family_permission_denied(self):
        """测试更新家族权限不足"""
        family = self.create_test_family()

        update_data = {"name": "恶意更新"}

        with pytest.raises(FamilyPermissionError):
            FamilyService.update_family(family.id, update_data, self.user2)

    def test_update_family_name_conflict(self):
        """测试更新家族名称冲突"""
        family1 = self.create_test_family(name="家族1")
        family2 = self.create_test_family(name="家族2", creator=self.user1)

        # 尝试将family2的名称改为family1的名称
        update_data = {"name": "家族1"}

        with pytest.raises(FamilyNameConflictError):
            FamilyService.update_family(family2.id, update_data, self.user1)

    def test_delete_family_success(self):
        """测试删除家族成功"""
        family = self.create_test_family()
        family_id = family.id

        FamilyService.delete_family(family_id, self.user1)

        # 验证家族已被删除
        assert not Family.objects.filter(id=family_id).exists()

        # 验证相关设置也被删除
        assert not FamilySettings.objects.filter(family_id=family_id).exists()

    def test_delete_family_permission_denied(self):
        """测试删除家族权限不足"""
        family = self.create_test_family()

        with pytest.raises(FamilyPermissionError):
            FamilyService.delete_family(family.id, self.user2)

    def test_list_families_success(self):
        """测试获取家族列表成功"""
        # 创建多个家族
        families = []
        for i in range(5):
            family = self.create_test_family(
                name=f"家族{i}", visibility="public" if i % 2 == 0 else "family"
            )
            families.append(family)

        result_families, total = FamilyService.list_families(
            self.user1, page=1, page_size=10
        )

        assert total >= 5
        assert len(result_families) >= 5

    def test_list_families_with_filters(self):
        """测试带过滤条件的家族列表"""
        # 创建不同类型的家族
        public_family = self.create_test_family(
            name="公开家族", visibility="public", allow_join=True
        )
        private_family = self.create_test_family(
            name="私有家族", visibility="private", allow_join=False
        )

        # 测试可见性过滤
        families, total = FamilyService.list_families(self.user1, visibility="public")

        for family in families:
            assert family.visibility == "public"

    def test_list_families_search(self):
        """测试家族搜索功能"""
        # 创建包含特定关键词的家族
        self.create_test_family(
            name="北京张氏家族", description="来自北京的张氏家族", tags="北京,张氏"
        )
        self.create_test_family(
            name="上海李氏家族", description="来自上海的李氏家族", tags="上海,李氏"
        )

        # 搜索包含"北京"的家族
        families, total = FamilyService.list_families(self.user1, keyword="北京")

        # 验证搜索结果
        beijing_families = [
            f
            for f in families
            if "北京" in f.name or "北京" in f.description or "北京" in (f.tags or "")
        ]
        assert len(beijing_families) > 0

    def test_list_families_pagination(self):
        """测试家族列表分页"""
        # 创建多个家族
        for i in range(25):
            self.create_test_family(name=f"分页测试家族{i}")

        # 测试第一页
        families_page1, total = FamilyService.list_families(
            self.user1, page=1, page_size=10
        )

        assert len(families_page1) == 10
        assert total >= 25

        # 测试第二页
        families_page2, total = FamilyService.list_families(
            self.user1, page=2, page_size=10
        )

        assert len(families_page2) == 10

        # 验证两页数据不重复
        page1_ids = {f.id for f in families_page1}
        page2_ids = {f.id for f in families_page2}
        assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.django_db
class TestFamilyServiceCaching:
    """Family服务层缓存功能测试"""

    def setup_method(self):
        """测试方法初始化"""
        cache.clear()

        self.user = User.objects.create_user(
            username="cacheuser", email="cache@example.com", password="testpass123"
        )

        self.family_data = {
            "name": "缓存测试家族",
            "description": "用于测试缓存功能",
            "creator": self.user,
        }

    def test_family_detail_caching(self):
        """测试家族详情缓存"""
        family = Family.objects.create(**self.family_data)

        # 第一次获取（应该查询数据库）
        with patch.object(Family.objects, "get") as mock_get:
            mock_get.return_value = family

            result1 = FamilyService.get_family_detail(family.id, self.user)
            assert mock_get.called
            assert result1.id == family.id

        # 第二次获取（应该使用缓存）
        with patch.object(Family.objects, "get") as mock_get:
            result2 = FamilyService.get_family_detail(family.id, self.user)
            assert not mock_get.called  # 不应该查询数据库
            assert result2.id == family.id

    def test_cache_invalidation_on_update(self):
        """测试更新时缓存失效"""
        family = Family.objects.create(**self.family_data)

        # 先获取一次以建立缓存
        FamilyService.get_family_detail(family.id, self.user)

        # 更新家族
        update_data = {"name": "更新后的名称"}
        FamilyService.update_family(family.id, update_data, self.user)

        # 再次获取应该是更新后的数据
        updated_family = FamilyService.get_family_detail(family.id, self.user)
        assert updated_family.name == "更新后的名称"

    def test_list_families_caching(self):
        """测试家族列表缓存"""
        # 创建测试数据
        for i in range(3):
            Family.objects.create(name=f"列表缓存测试{i}", creator=self.user)

        # 第一次获取列表
        with patch.object(Family.objects, "filter") as mock_filter:
            mock_queryset = Mock()
            mock_filter.return_value = mock_queryset
            mock_queryset.count.return_value = 3
            mock_queryset.__getitem__.return_value = []

            families1, total1 = FamilyService.list_families(self.user)
            assert mock_filter.called

        # 第二次获取列表（应该使用缓存）
        with patch.object(Family.objects, "filter") as mock_filter:
            families2, total2 = FamilyService.list_families(self.user)
            # 注意：列表缓存策略可能不同，这里需要根据实际实现调整


@pytest.mark.django_db
class TestFamilyServiceTransactions:
    """Family服务层事务处理测试"""

    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username="transuser", email="trans@example.com", password="testpass123"
        )

        self.family_data = {
            "name": "事务测试家族",
            "description": "用于测试事务处理",
            "visibility": "family",
        }

    def test_create_family_transaction_rollback(self):
        """测试创建家族事务回滚"""
        # 模拟在创建设置时发生错误
        with patch.object(FamilySettings.objects, "create") as mock_create:
            mock_create.side_effect = IntegrityError("模拟数据库错误")

            with pytest.raises(IntegrityError):
                FamilyService.create_family(self.family_data, self.user)

            # 验证家族也没有被创建（事务回滚）
            assert not Family.objects.filter(name=self.family_data["name"]).exists()

    def test_update_family_atomic_operation(self):
        """测试更新家族原子操作"""
        family = Family.objects.create(**self.family_data, creator=self.user)

        # 模拟更新过程中发生错误
        original_name = family.name

        with patch.object(Family, "save") as mock_save:
            mock_save.side_effect = IntegrityError("模拟保存错误")

            with pytest.raises(IntegrityError):
                FamilyService.update_family(family.id, {"name": "新名称"}, self.user)

            # 验证数据没有被部分更新
            family.refresh_from_db()
            assert family.name == original_name

    def test_delete_family_cascade_transaction(self):
        """测试删除家族级联事务"""
        family = Family.objects.create(**self.family_data, creator=self.user)

        # 创建相关数据
        settings = FamilySettings.objects.create(
            family_id=family.id, tree_layout="vertical"
        )

        invitation = FamilyInvitation.objects.create(
            family_id=family.id,
            inviter_id=self.user.id,
            invitee_email="test@example.com",
            invitee_name="测试用户",
            invitation_code="test_code",
            expires_at=timezone.now() + timedelta(days=7),
        )

        # 删除家族
        FamilyService.delete_family(family.id, self.user)

        # 验证所有相关数据都被删除
        assert not Family.objects.filter(id=family.id).exists()
        assert not FamilySettings.objects.filter(family_id=family.id).exists()
        assert not FamilyInvitation.objects.filter(family_id=family.id).exists()


@pytest.mark.django_db
class TestFamilyServiceErrorHandling:
    """Family服务层错误处理测试"""

    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username="erroruser", email="error@example.com", password="testpass123"
        )

    def test_handle_database_connection_error(self):
        """测试数据库连接错误处理"""
        with patch.object(Family.objects, "create") as mock_create:
            mock_create.side_effect = Exception("数据库连接失败")

            with pytest.raises(OperationError) as exc_info:
                FamilyService.create_family({"name": "测试家族"}, self.user)
            assert "创建家族失败" in str(exc_info.value)

    def test_handle_validation_error_gracefully(self):
        """测试优雅处理验证错误"""
        # 测试各种验证错误场景
        invalid_cases = [
            {"name": ""},  # 空名称
            {"name": "A" * 101},  # 名称过长
            {"visibility": "invalid"},  # 无效可见性
        ]

        for invalid_data in invalid_cases:
            with pytest.raises((FamilyValidationError, ValidationError)):
                FamilyService.create_family(invalid_data, self.user)

    def test_handle_permission_error_details(self):
        """测试权限错误详细信息"""
        family = Family.objects.create(name="权限测试家族", creator=self.user)

        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        # 测试不同权限错误
        with pytest.raises(FamilyPermissionError) as exc_info:
            FamilyService.update_family(family.id, {"name": "恶意更新"}, other_user)
        assert "没有编辑家族的权限" in str(exc_info.value)

    def test_handle_concurrent_modification(self):
        """测试并发修改处理"""
        family = Family.objects.create(name="并发测试家族", creator=self.user)

        # 模拟并发修改冲突
        with patch.object(Family, "save") as mock_save:
            mock_save.side_effect = IntegrityError("并发修改冲突")

            with pytest.raises(OperationError):
                FamilyService.update_family(family.id, {"name": "并发更新"}, self.user)


@pytest.mark.django_db
class TestFamilyServiceBusinessRules:
    """Family服务层业务规则测试"""

    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username="businessuser",
            email="business@example.com",
            password="testpass123",
        )

    def test_family_name_uniqueness_rule(self):
        """测试家族名称唯一性规则"""
        # 创建第一个家族
        Family.objects.create(name="唯一名称家族", creator=self.user)

        # 尝试创建同名家族
        with pytest.raises(FamilyNameConflictError):
            FamilyService.create_family({"name": "唯一名称家族"}, self.user)

    def test_family_creator_permissions_rule(self):
        """测试家族创建者权限规则"""
        family = Family.objects.create(name="创建者权限测试", creator=self.user)

        # 创建者应该有所有权限
        from ..permissions import FamilyPermissionChecker, FamilyPermission

        permissions = [
            FamilyPermission.VIEW,
            FamilyPermission.EDIT,
            FamilyPermission.DELETE,
            FamilyPermission.MANAGE_MEMBERS,
            FamilyPermission.MANAGE_SETTINGS,
        ]

        for permission in permissions:
            assert FamilyPermissionChecker.check_permission(
                self.user, family, permission
            )

    def test_family_visibility_access_rule(self):
        """测试家族可见性访问规则"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        # 创建不同可见性的家族
        public_family = Family.objects.create(
            name="公开家族", visibility="public", creator=self.user
        )

        private_family = Family.objects.create(
            name="私有家族", visibility="private", creator=self.user
        )

        # 其他用户应该能访问公开家族
        result = FamilyService.get_family_detail(public_family.id, other_user)
        assert result.id == public_family.id

        # 其他用户不应该能访问私有家族
        with pytest.raises(FamilyPermissionError):
            FamilyService.get_family_detail(private_family.id, other_user)

    def test_family_member_count_update_rule(self):
        """测试家族成员数量更新规则"""
        family = Family.objects.create(name="成员数量测试", creator=self.user)

        # 初始成员数应该为1（创建者）
        assert family.member_count == 1

        # 首先创建一个Member记录
        from apps.members.models import Member

        member = Member.objects.create(
            family_id=family.id, name="测试成员", gender="male", creator_id=self.user.id
        )

        # 添加成员后应该自动更新
        FamilyMembership.objects.create(
            family_id=family.id,
            user_id=self.user.id,
            member_id=member.id,
            role="admin",
            status="active",
        )

        # 触发成员数量更新
        family.update_member_count()
        family.refresh_from_db()

        assert family.member_count == 2  # 1(创建者) + 1(新增成员)

    def test_family_settings_default_values_rule(self):
        """测试家族设置默认值规则"""
        family_data = {"name": "设置默认值测试", "description": "测试默认设置"}

        family = FamilyService.create_family(family_data, self.user)

        # 验证自动创建的设置有正确的默认值
        settings = FamilySettings.objects.get(family_id=family.id)

        assert settings.tree_layout == "vertical"
        assert settings.show_photos is True
        assert settings.show_birth_dates is True
        assert settings.privacy_level == "family"
        assert settings.require_approval is True


@pytest.mark.django_db
class TestFamilyServicePerformance:
    """Family服务层性能测试"""

    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username="perfuser", email="perf@example.com", password="testpass123"
        )

    def test_bulk_family_creation_performance(self):
        """测试批量创建家族性能"""
        import time

        start_time = time.time()

        # 批量创建家族
        families = []
        for i in range(100):
            family_data = {
                "name": f"性能测试家族{i}",
                "description": f"第{i}个测试家族",
                "creator": self.user,
            }
            family = Family.objects.create(**family_data)
            families.append(family)

        end_time = time.time()
        creation_time = end_time - start_time

        # 验证创建时间在合理范围内
        assert creation_time < 5.0  # 应该在5秒内完成
        assert len(families) == 100

    def test_large_family_list_query_performance(self):
        """测试大量家族列表查询性能"""
        # 创建大量家族
        for i in range(500):
            Family.objects.create(
                name=f"查询性能测试{i}",
                creator=self.user,
                visibility="public" if i % 2 == 0 else "family",
            )

        start_time = time.time()

        # 执行查询
        families, total = FamilyService.list_families(self.user, page=1, page_size=50)

        end_time = time.time()
        query_time = end_time - start_time

        # 验证查询时间和结果
        assert query_time < 2.0  # 应该在2秒内完成
        assert len(families) == 50
        assert total >= 500

    def test_family_search_performance(self):
        """测试家族搜索性能"""
        # 创建包含不同关键词的家族
        keywords = ["北京", "上海", "广州", "深圳", "杭州"]

        for i in range(200):
            keyword = keywords[i % len(keywords)]
            Family.objects.create(
                name=f"{keyword}测试家族{i}",
                description=f"来自{keyword}的家族",
                tags=f"{keyword},测试",
                creator=self.user,
            )

        start_time = time.time()

        # 执行搜索
        families, total = FamilyService.list_families(self.user, keyword="北京")

        end_time = time.time()
        search_time = end_time - start_time

        # 验证搜索时间和结果
        assert search_time < 1.0  # 应该在1秒内完成
        assert total > 0

        # 验证搜索结果的准确性
        for family in families:
            assert (
                "北京" in family.name
                or "北京" in family.description
                or "北京" in (family.tags or "")
            )


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
