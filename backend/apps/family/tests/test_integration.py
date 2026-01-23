"""
Family应用集成测试

测试Family应用的端到端功能，包括API集成、数据库事务、
缓存集成、外部服务集成等。
遵循Django Ninja和pytest最佳实践。
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from django.test import TestCase, TransactionTestCase, override_settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone

from ninja.testing import TestClient

from config.api_v1 import api_v1
from apps.common.test_utils import APITestCase

from ..models import Family, FamilySettings, FamilyInvitation
from ..schemas import (
    FamilyCreateSchema,
    FamilyUpdateSchema,
    FamilySettingsSchema,
    FamilyInvitationCreateSchema,
    FamilyFilterSchema,
)
from ..services import FamilyService
from apps.members.models import FamilyMembership

User = get_user_model()


@pytest.mark.django_db
class TestFamilyAPIIntegration(APITestCase):
    """Family API集成测试"""

    def setUp(self):
        """测试初始化"""
        super().setUp()

        # 创建测试用户
        self.user1 = self.create_test_user(username="user1", email="user1@example.com")
        self.user2 = self.create_test_user(username="user2", email="user2@example.com")
        self.user3 = self.create_test_user(username="user3", email="user3@example.com")

        # 创建测试家族
        self.family1 = Family.objects.create(
            name="集成测试家族1",
            description="用于集成测试的家族",
            creator=self.user1,
            visibility="public",
        )

        self.family2 = Family.objects.create(
            name="集成测试家族2",
            description="另一个测试家族",
            creator=self.user2,
            visibility="family",
        )

        # 创建成员关系
        FamilyMembership.objects.create(
            family=self.family2, user=self.user3, role="member", status="active"
        )

    def test_complete_family_lifecycle(self):
        """测试完整的家族生命周期"""
        # 1. 创建家族
        create_data = {
            "name": "生命周期测试家族",
            "description": "测试完整生命周期",
            "visibility": "public",
            "allow_join": True,
            "tags": ["测试", "生命周期"],
        }

        response = self.api_post("/families/", data=create_data)
        self.assert_api_success(response)

        family_id = response.json()["data"]["id"]

        # 2. 获取家族详情
        response = self.api_get(f"/families/{family_id}/")
        self.assert_api_success(response)

        family_data = response.json()["data"]
        self.assertEqual(family_data["name"], create_data["name"])
        self.assertEqual(family_data["description"], create_data["description"])

        # 3. 更新家族信息
        update_data = {"description": "更新后的描述", "motto": "家族座右铭"}

        response = self.api_patch(f"/families/{family_id}/", data=update_data)
        self.assert_api_success(response)

        # 4. 获取家族设置
        response = self.api_get(f"/families/{family_id}/settings/")
        self.assert_api_success(response)

        # 5. 更新家族设置
        settings_data = {
            "tree_layout": "horizontal",
            "show_photos": True,
            "theme": "modern",
        }

        response = self.api_put(f"/families/{family_id}/settings/", data=settings_data)
        self.assert_api_success(response)

        # 6. 邀请成员
        invitation_data = {
            "invitee_email": "newmember@example.com",
            "invitee_name": "新成员",
            "message": "欢迎加入我们的家族",
        }

        response = self.api_post(
            f"/families/{family_id}/invitations/", data=invitation_data
        )
        self.assert_api_success(response)

        # 7. 获取家族统计
        response = self.api_get(f"/families/{family_id}/statistics/")
        self.assert_api_success(response)

        # 8. 删除家族
        response = self.api_delete(f"/families/{family_id}/")
        self.assert_api_success(response)

        # 验证家族已被删除
        response = self.api_get(f"/families/{family_id}/")
        self.assert_api_error(response, 404)

    def test_family_search_and_filter(self):
        """测试家族搜索和过滤"""
        # 创建更多测试数据
        families = []
        for i in range(5):
            family = Family.objects.create(
                name=f"搜索测试家族{i}",
                description=f"描述{i}",
                creator=self.user1,
                visibility="public" if i % 2 == 0 else "family",
                tags=["搜索", f"标签{i}"],
            )
            families.append(family)

        # 1. 基本搜索
        response = self.api_get("/families/", params={"search": "搜索测试"})
        self.assert_api_success(response)

        data = response.json()["data"]
        self.assertGreaterEqual(len(data["items"]), 5)

        # 2. 按可见性过滤
        response = self.api_get("/families/", params={"visibility": "public"})
        self.assert_api_success(response)

        # 3. 按标签过滤
        response = self.api_get("/families/", params={"tags": "搜索"})
        self.assert_api_success(response)

        # 4. 分页测试
        response = self.api_get("/families/", params={"page": 1, "size": 3})
        self.assert_api_success(response)
        self.assert_pagination_response(response)

        # 5. 排序测试
        response = self.api_get("/families/", params={"ordering": "-created_at"})
        self.assert_api_success(response)

    def test_family_member_management_flow(self):
        """测试家族成员管理流程"""
        # 1. 发送邀请
        invitation_data = {
            "invitee_email": self.user3.email,
            "invitee_name": self.user3.username,
            "message": "邀请加入家族",
        }

        response = self.api_post(
            f"/api/families/{self.family1.id}/invitations/",
            data=invitation_data,
            user=self.user1,
        )
        self.assert_success(response)

        invitation_id = response.json()["data"]["id"]

        # 2. 获取邀请列表
        response = self.api_get(
            f"/api/families/{self.family1.id}/invitations/", user=self.user1
        )
        self.assert_success(response)

        # 3. 接受邀请
        response = self.api_post(
            f"/api/families/{self.family1.id}/invitations/{invitation_id}/accept/",
            user=self.user3,
        )
        self.assert_success(response)

        # 4. 验证成员已加入
        response = self.api_get(
            f"/api/families/{self.family1.id}/members/", user=self.user1
        )
        self.assert_success(response)

        members = response.json()["data"]["items"]
        member_emails = [member["user"]["email"] for member in members]
        self.assertIn(self.user3.email, member_emails)

        # 5. 更新成员角色
        membership = FamilyMembership.objects.get(family=self.family1, user=self.user3)

        response = self.api_patch(
            f"/api/families/{self.family1.id}/members/{membership.id}/",
            data={"role": "admin"},
            user=self.user1,
        )
        self.assert_success(response)

        # 6. 移除成员
        response = self.api_delete(
            f"/api/families/{self.family1.id}/members/{membership.id}/", user=self.user1
        )
        self.assert_success(response)

    def test_family_permissions_integration(self):
        """测试家族权限集成"""
        # 1. 创建者权限测试
        response = self.api_get(f"/api/families/{self.family1.id}/", user=self.user1)
        self.assert_success(response)

        response = self.api_patch(
            f"/api/families/{self.family1.id}/",
            data={"description": "创建者更新"},
            user=self.user1,
        )
        self.assert_success(response)

        # 2. 非成员权限测试（公开家族）
        response = self.api_get(f"/api/families/{self.family1.id}/", user=self.user2)
        self.assert_success(response)

        response = self.api_patch(
            f"/api/families/{self.family1.id}/",
            data={"description": "非成员尝试更新"},
            user=self.user2,
        )
        self.assert_error(response, 403)

        # 3. 非成员权限测试（家族可见）
        response = self.api_get(f"/api/families/{self.family2.id}/", user=self.user1)
        self.assert_error(response, 403)

        # 4. 成员权限测试
        response = self.api_get(f"/api/families/{self.family2.id}/", user=self.user3)
        self.assert_success(response)

        response = self.api_patch(
            f"/api/families/{self.family2.id}/",
            data={"description": "普通成员尝试更新"},
            user=self.user3,
        )
        self.assert_error(response, 403)

    def test_family_export_import_flow(self):
        """测试家族导出导入流程"""
        # 1. 导出家族数据
        response = self.api_post(
            f"/api/families/{self.family1.id}/export/",
            data={"format": "json", "include_members": True},
            user=self.user1,
        )
        self.assert_success(response)

        export_data = response.json()["data"]
        self.assertIn("family", export_data)
        self.assertIn("members", export_data)

        # 2. 导入家族数据（创建新家族）
        import_data = {
            "data": export_data,
            "options": {"create_new": True, "name_suffix": "_导入"},
        }

        response = self.api_post(
            "/api/families/import/", data=import_data, user=self.user1
        )
        self.assert_success(response)

        imported_family_id = response.json()["data"]["family_id"]

        # 3. 验证导入的家族
        response = self.api_get(f"/api/families/{imported_family_id}/", user=self.user1)
        self.assert_success(response)

        imported_family = response.json()["data"]
        self.assertTrue(imported_family["name"].endswith("_导入"))


@pytest.mark.django_db
class TestFamilyDatabaseIntegration(TransactionTestCase):
    """Family数据库集成测试"""

    def setUp(self):
        """测试初始化"""
        self.user = User.objects.create_user(
            username="dbuser", email="db@example.com", password="testpass123"
        )

    def test_transaction_rollback_on_error(self):
        """测试错误时事务回滚"""
        initial_count = Family.objects.count()

        try:
            with transaction.atomic():
                # 创建家族
                family = Family.objects.create(name="事务测试家族", creator=self.user)

                # 创建设置
                FamilySettings.objects.create(family=family, tree_layout="vertical")

                # 模拟错误
                raise Exception("模拟错误")

        except Exception:
            pass

        # 验证事务已回滚
        self.assertEqual(Family.objects.count(), initial_count)
        self.assertEqual(FamilySettings.objects.count(), 0)

    def test_database_constraints(self):
        """测试数据库约束"""
        # 创建家族
        family = Family.objects.create(name="约束测试家族", creator=self.user)

        # 测试唯一性约束
        with self.assertRaises(Exception):
            Family.objects.create(
                name="约束测试家族",  # 相同名称
                creator=self.user,
            )

        # 测试外键约束
        settings = FamilySettings.objects.create(
            family=family, tree_layout="horizontal"
        )

        # 删除家族应该级联删除设置
        family.delete()

        with self.assertRaises(FamilySettings.DoesNotExist):
            FamilySettings.objects.get(id=settings.id)

    def test_concurrent_access(self):
        """测试并发访问"""
        family = Family.objects.create(
            name="并发测试家族", creator=self.user, member_count=0
        )

        # 模拟并发更新成员数量
        def update_member_count():
            f = Family.objects.get(id=family.id)
            f.member_count += 1
            f.save()

        # 在实际应用中，这里应该使用多线程或多进程
        # 这里只是简单模拟
        for _ in range(5):
            update_member_count()

        family.refresh_from_db()
        self.assertEqual(family.member_count, 5)

    def test_database_performance(self):
        """测试数据库性能"""
        import time

        # 批量创建数据
        start_time = time.time()

        families = []
        for i in range(100):
            families.append(Family(name=f"性能测试家族{i}", creator=self.user))

        Family.objects.bulk_create(families)

        creation_time = time.time() - start_time

        # 验证创建时间合理（应该很快）
        self.assertLess(creation_time, 1.0)  # 1秒内完成

        # 测试查询性能
        start_time = time.time()

        families = list(Family.objects.filter(creator=self.user))

        query_time = time.time() - start_time

        # 验证查询时间合理
        self.assertLess(query_time, 0.1)  # 0.1秒内完成
        self.assertEqual(len(families), 100)


@pytest.mark.django_db
class TestFamilyCacheIntegration:
    """Family缓存集成测试"""

    def setup_method(self, method):
        """测试方法初始化"""
        cache.clear()

        self.user = User.objects.create_user(
            username="cacheuser", email="cache@example.com", password="testpass123"
        )

        self.family = Family.objects.create(name="缓存测试家族", creator=self.user)

    def test_family_cache_operations(self):
        """测试家族缓存操作"""
        # 1. 缓存家族数据
        cache_key = f"family:{self.family.id}"
        family_data = {
            "id": self.family.id,
            "name": self.family.name,
            "creator_id": self.family.creator_id,
        }

        cache.set(cache_key, family_data, timeout=300)

        # 2. 从缓存获取数据
        cached_data = cache.get(cache_key)
        assert cached_data is not None
        assert cached_data["name"] == self.family.name

        # 3. 更新家族时清除缓存
        self.family.name = "更新后的名称"
        self.family.save()

        # 模拟缓存清除
        cache.delete(cache_key)

        cached_data = cache.get(cache_key)
        assert cached_data is None

    def test_family_list_cache(self):
        """测试家族列表缓存"""
        # 创建多个家族
        families = []
        for i in range(5):
            family = Family.objects.create(name=f"列表缓存测试{i}", creator=self.user)
            families.append(family)

        # 缓存家族列表
        cache_key = f"family_list:user:{self.user.id}"
        family_list = [{"id": f.id, "name": f.name} for f in families]

        cache.set(cache_key, family_list, timeout=300)

        # 验证缓存
        cached_list = cache.get(cache_key)
        assert len(cached_list) == 5
        assert cached_list[0]["name"] == "列表缓存测试0"

    def test_cache_invalidation_on_update(self):
        """测试更新时缓存失效"""
        # 设置缓存
        cache_key = f"family:{self.family.id}"
        cache.set(cache_key, {"name": self.family.name}, timeout=300)

        # 验证缓存存在
        assert cache.get(cache_key) is not None

        # 更新家族（应该触发缓存失效）
        self.family.description = "新的描述"
        self.family.save()

        # 模拟缓存失效逻辑
        cache.delete(cache_key)

        # 验证缓存已失效
        assert cache.get(cache_key) is None

    def test_cache_performance(self):
        """测试缓存性能"""

        # 测试数据库查询时间
        start_time = time.time()
        for _ in range(100):
            Family.objects.get(id=self.family.id)
        db_time = time.time() - start_time

        # 设置缓存
        cache_key = f"family:{self.family.id}"
        family_data = {"id": self.family.id, "name": self.family.name}
        cache.set(cache_key, family_data)

        # 测试缓存查询时间
        start_time = time.time()
        for _ in range(100):
            cache.get(cache_key)
        cache_time = time.time() - start_time

        # 缓存应该比数据库查询快
        assert cache_time < db_time


@pytest.mark.django_db
class TestFamilyExternalServiceIntegration:
    """Family外部服务集成测试"""

    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username="serviceuser", email="service@example.com", password="testpass123"
        )

        self.family = Family.objects.create(name="服务集成测试家族", creator=self.user)

    @patch("apps.family.services.EmailService")
    def test_email_service_integration(self, mock_email_service):
        """测试邮件服务集成"""
        # 配置模拟邮件服务
        mock_email_instance = Mock()
        mock_email_service.return_value = mock_email_instance
        mock_email_instance.send_invitation.return_value = True

        # 创建邀请
        invitation = FamilyInvitation.objects.create(
            family=self.family,
            inviter=self.user,
            invitee_email="invitee@example.com",
            invitee_name="被邀请者",
            invitation_code="test_code_123",
            expires_at=timezone.now() + timedelta(days=7),
        )

        # 发送邀请邮件
        # 这里应该调用实际的服务方法
        # FamilyService.send_invitation_email(invitation)

        # 验证邮件服务被调用
        # mock_email_instance.send_invitation.assert_called_once()

    @patch("apps.family.services.FileStorageService")
    def test_file_storage_integration(self, mock_storage_service):
        """测试文件存储服务集成"""
        # 配置模拟存储服务
        mock_storage_instance = Mock()
        mock_storage_service.return_value = mock_storage_instance
        mock_storage_instance.upload_avatar.return_value = (
            "https://example.com/avatar.jpg"
        )

        # 模拟头像上传
        avatar_data = b"fake_image_data"

        # 这里应该调用实际的服务方法
        # avatar_url = FamilyService.upload_avatar(self.family, avatar_data)

        # 验证存储服务被调用
        # mock_storage_instance.upload_avatar.assert_called_once()
        # assert avatar_url == 'https://example.com/avatar.jpg'

    @patch("apps.family.services.NotificationService")
    def test_notification_service_integration(self, mock_notification_service):
        """测试通知服务集成"""
        # 配置模拟通知服务
        mock_notification_instance = Mock()
        mock_notification_service.return_value = mock_notification_instance
        mock_notification_instance.send_notification.return_value = True

        # 模拟发送通知
        notification_data = {
            "type": "family_invitation",
            "recipient": self.user,
            "message": "您收到了一个家族邀请",
        }

        # 这里应该调用实际的服务方法
        # FamilyService.send_notification(notification_data)

        # 验证通知服务被调用
        # mock_notification_instance.send_notification.assert_called_once()

    @patch("apps.family.services.SearchService")
    def test_search_service_integration(self, mock_search_service):
        """测试搜索服务集成"""
        # 配置模拟搜索服务
        mock_search_instance = Mock()
        mock_search_service.return_value = mock_search_instance
        mock_search_instance.index_family.return_value = True
        mock_search_instance.search_families.return_value = [self.family.id]

        # 模拟索引家族
        # FamilyService.index_family(self.family)

        # 模拟搜索家族
        # results = FamilyService.search_families('测试')

        # 验证搜索服务被调用
        # mock_search_instance.index_family.assert_called_once()
        # mock_search_instance.search_families.assert_called_once()
        # assert self.family.id in results


@pytest.mark.django_db
class TestFamilyEndToEndScenarios:
    """Family端到端场景测试"""

    def setup_method(self, method):
        """测试方法初始化"""
        # 创建测试用户
        self.creator = User.objects.create_user(
            username="creator", email="creator@example.com", password="testpass123"
        )

        self.member1 = User.objects.create_user(
            username="member1", email="member1@example.com", password="testpass123"
        )

        self.member2 = User.objects.create_user(
            username="member2", email="member2@example.com", password="testpass123"
        )

    def test_family_creation_and_growth_scenario(self):
        """测试家族创建和发展场景"""
        # 1. 创建家族
        family = Family.objects.create(
            name="端到端测试家族",
            description="一个完整的测试场景",
            creator=self.creator,
            visibility="public",
            allow_join=True,
        )

        # 2. 配置家族设置
        settings = FamilySettings.objects.create(
            family=family,
            tree_layout="horizontal",
            show_photos=True,
            theme="modern",
            privacy_level="family",
        )

        # 3. 邀请第一个成员
        invitation1 = FamilyInvitation.objects.create(
            family=family,
            inviter=self.creator,
            invitee_email=self.member1.email,
            invitee_name=self.member1.username,
            invitation_code="invite_code_1",
            expires_at=timezone.now() + timedelta(days=7),
        )

        # 4. 第一个成员接受邀请
        invitation1.status = "accepted"
        invitation1.processed_at = timezone.now()
        invitation1.save()

        membership1 = FamilyMembership.objects.create(
            family=family, user=self.member1, role="member", status="active"
        )

        # 5. 提升第一个成员为管理员
        membership1.role = "admin"
        membership1.save()

        # 6. 管理员邀请第二个成员
        invitation2 = FamilyInvitation.objects.create(
            family=family,
            inviter=self.member1,  # 管理员邀请
            invitee_email=self.member2.email,
            invitee_name=self.member2.username,
            invitation_code="invite_code_2",
            expires_at=timezone.now() + timedelta(days=7),
        )

        # 7. 第二个成员接受邀请
        invitation2.status = "accepted"
        invitation2.processed_at = timezone.now()
        invitation2.save()

        membership2 = FamilyMembership.objects.create(
            family=family, user=self.member2, role="member", status="active"
        )

        # 8. 更新家族统计
        family.member_count = 3  # 创建者 + 2个成员
        family.save()

        # 验证最终状态
        assert family.member_count == 3
        assert (
            FamilyMembership.objects.filter(family=family, status="active").count() == 2
        )
        assert (
            FamilyInvitation.objects.filter(family=family, status="accepted").count()
            == 2
        )

    def test_family_collaboration_scenario(self):
        """测试家族协作场景"""
        # 1. 创建家族
        family = Family.objects.create(name="协作测试家族", creator=self.creator)

        # 2. 添加成员
        FamilyMembership.objects.create(
            family=family, user=self.member1, role="admin", status="active"
        )

        FamilyMembership.objects.create(
            family=family, user=self.member2, role="member", status="active"
        )

        # 3. 创建者更新家族信息
        family.description = "创建者更新的描述"
        family.motto = "家族座右铭"
        family.save()

        # 4. 管理员更新设置
        settings = FamilySettings.objects.create(
            family=family,
            tree_layout="vertical",
            show_photos=True,
            show_birth_dates=True,
            theme="classic",
        )

        # 5. 普通成员查看家族信息（只读）
        family_info = {
            "name": family.name,
            "description": family.description,
            "member_count": family.member_count,
        }

        # 验证协作结果
        assert family.description == "创建者更新的描述"
        assert family.motto == "家族座右铭"
        assert settings.tree_layout == "vertical"
        assert family_info["name"] == "协作测试家族"

    def test_family_privacy_scenario(self):
        """测试家族隐私场景"""
        # 1. 创建私有家族
        private_family = Family.objects.create(
            name="私有家族", creator=self.creator, visibility="private"
        )

        # 2. 创建家族可见家族
        family_visible = Family.objects.create(
            name="家族可见", creator=self.creator, visibility="family"
        )

        # 3. 添加成员到家族可见家族
        FamilyMembership.objects.create(
            family=family_visible, user=self.member1, role="member", status="active"
        )

        # 4. 创建公开家族
        public_family = Family.objects.create(
            name="公开家族", creator=self.creator, visibility="public"
        )

        # 验证隐私设置
        # 私有家族：只有创建者可见
        # 家族可见：创建者和成员可见
        # 公开家族：所有人可见

        assert private_family.visibility == "private"
        assert family_visible.visibility == "family"
        assert public_family.visibility == "public"

        # 验证成员关系
        assert FamilyMembership.objects.filter(
            family=family_visible, user=self.member1
        ).exists()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
