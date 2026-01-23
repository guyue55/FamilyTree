"""
Family应用测试配置和工具

提供Family应用测试的配置、工具函数、测试数据工厂等。
遵循Django和pytest最佳实践。
"""

import os
import django
from django.conf import settings

# 确保Django设置已配置
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
    django.setup()

import pytest
import factory
from typing import Dict, Any, List
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import override_settings

from ..models import Family, FamilySettings, FamilyInvitation
from apps.members.models import FamilyMembership

User = get_user_model()

# 测试配置
TEST_SETTINGS = {
    "DJANGO_SETTINGS_MODULE": "config.settings.testing",
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    },
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "CELERY_TASK_ALWAYS_EAGER": True,
    "CELERY_TASK_EAGER_PROPAGATES": True,
}


# 测试数据工厂
class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return

        password = extracted or "testpass123"
        obj.set_password(password)
        obj.save()


class FamilyFactory(factory.django.DjangoModelFactory):
    """家族工厂"""

    class Meta:
        model = Family

    name = factory.Faker("company")
    description = factory.Faker("text", max_nb_chars=200)
    creator = factory.SubFactory(UserFactory)
    visibility = factory.Iterator(["public", "family", "private"])
    is_active = True
    allow_join = True
    member_count = 1
    generation_count = 1
    tags = factory.LazyFunction(lambda: ["测试", "家族"])
    origin_location = factory.Faker("city")
    motto = factory.Faker("sentence", nb_words=6)


class FamilySettingsFactory(factory.django.DjangoModelFactory):
    """家族设置工厂"""

    class Meta:
        model = FamilySettings

    family = factory.SubFactory(FamilyFactory)
    tree_layout = factory.Iterator(["vertical", "horizontal", "circular"])
    show_photos = True
    show_birth_dates = True
    show_death_dates = True
    show_occupation = True
    theme = factory.Iterator(["classic", "modern", "elegant"])
    font_family = "Arial"
    font_size = 14
    privacy_level = factory.Iterator(["public", "family", "private"])
    require_approval = False
    allow_comments = True
    enable_notifications = True


class FamilyInvitationFactory(factory.django.DjangoModelFactory):
    """家族邀请工厂"""

    class Meta:
        model = FamilyInvitation

    family = factory.SubFactory(FamilyFactory)
    inviter = factory.SubFactory(UserFactory)
    invitee_email = factory.Faker("email")
    invitee_name = factory.Faker("name")
    message = factory.Faker("text", max_nb_chars=100)
    invitation_code = factory.Faker("uuid4")
    status = "pending"
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class FamilyMembershipFactory(factory.django.DjangoModelFactory):
    """家族成员工厂"""

    class Meta:
        model = FamilyMembership

    family = factory.SubFactory(FamilyFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.Iterator(["member", "admin", "moderator"])
    status = "active"
    joined_at = factory.LazyFunction(timezone.now)


# 测试数据生成器
class FamilyTestDataGenerator:
    """家族测试数据生成器"""

    @staticmethod
    def create_user(username: str = None, email: str = None, **kwargs) -> User:
        """创建测试用户"""
        if username:
            kwargs["username"] = username
        if email:
            kwargs["email"] = email

        return UserFactory(**kwargs)

    @staticmethod
    def create_family(creator: User = None, **kwargs) -> Family:
        """创建测试家族"""
        if creator:
            kwargs["creator"] = creator

        return FamilyFactory(**kwargs)

    @staticmethod
    def create_family_with_settings(
        creator: User = None, **kwargs
    ) -> tuple[Family, FamilySettings]:
        """创建带设置的家族"""
        family = FamilyTestDataGenerator.create_family(creator=creator, **kwargs)
        settings = FamilySettingsFactory(family=family)
        return family, settings

    @staticmethod
    def create_family_with_members(
        creator: User = None, member_count: int = 3, **kwargs
    ) -> tuple[Family, List[FamilyMembership]]:
        """创建带成员的家族"""
        family = FamilyTestDataGenerator.create_family(creator=creator, **kwargs)

        memberships = []
        for i in range(member_count):
            user = UserFactory()
            membership = FamilyMembershipFactory(
                family=family, user=user, role="admin" if i == 0 else "member"
            )
            memberships.append(membership)

        # 更新成员数量
        family.member_count = member_count + 1  # +1 for creator
        family.save()

        return family, memberships

    @staticmethod
    def create_invitation(
        family: Family = None, inviter: User = None, **kwargs
    ) -> FamilyInvitation:
        """创建邀请"""
        if family:
            kwargs["family"] = family
        if inviter:
            kwargs["inviter"] = inviter

        return FamilyInvitationFactory(**kwargs)

    @staticmethod
    def create_test_scenario(scenario_type: str) -> Dict[str, Any]:
        """创建测试场景"""
        scenarios = {
            "basic_family": FamilyTestDataGenerator._create_basic_family_scenario,
            "family_with_members": FamilyTestDataGenerator._create_family_with_members_scenario,
            "family_with_invitations": FamilyTestDataGenerator._create_family_with_invitations_scenario,
            "multi_family": FamilyTestDataGenerator._create_multi_family_scenario,
            "privacy_test": FamilyTestDataGenerator._create_privacy_test_scenario,
        }

        if scenario_type not in scenarios:
            raise ValueError(f"未知的测试场景类型: {scenario_type}")

        return scenarios[scenario_type]()

    @staticmethod
    def _create_basic_family_scenario() -> Dict[str, Any]:
        """创建基本家族场景"""
        creator = UserFactory()
        family, settings = FamilyTestDataGenerator.create_family_with_settings(
            creator=creator
        )

        return {"creator": creator, "family": family, "settings": settings}

    @staticmethod
    def _create_family_with_members_scenario() -> Dict[str, Any]:
        """创建带成员的家族场景"""
        creator = UserFactory()
        family, memberships = FamilyTestDataGenerator.create_family_with_members(
            creator=creator, member_count=5
        )
        settings = FamilySettingsFactory(family=family)

        return {
            "creator": creator,
            "family": family,
            "settings": settings,
            "memberships": memberships,
            "members": [m.user for m in memberships],
        }

    @staticmethod
    def _create_family_with_invitations_scenario() -> Dict[str, Any]:
        """创建带邀请的家族场景"""
        creator = UserFactory()
        family = FamilyTestDataGenerator.create_family(creator=creator)

        invitations = []
        for i in range(3):
            invitation = FamilyInvitationFactory(
                family=family,
                inviter=creator,
                status="pending" if i < 2 else "accepted",
            )
            invitations.append(invitation)

        return {"creator": creator, "family": family, "invitations": invitations}

    @staticmethod
    def _create_multi_family_scenario() -> Dict[str, Any]:
        """创建多家族场景"""
        users = [UserFactory() for _ in range(3)]
        families = []

        for i, user in enumerate(users):
            family = FamilyTestDataGenerator.create_family(
                creator=user, visibility=["public", "family", "private"][i]
            )
            families.append(family)

        return {
            "users": users,
            "families": families,
            "public_family": families[0],
            "family_visible": families[1],
            "private_family": families[2],
        }

    @staticmethod
    def _create_privacy_test_scenario() -> Dict[str, Any]:
        """创建隐私测试场景"""
        creator = UserFactory()
        member = UserFactory()
        outsider = UserFactory()

        # 创建不同可见性的家族
        public_family = FamilyTestDataGenerator.create_family(
            creator=creator, visibility="public"
        )

        family_visible = FamilyTestDataGenerator.create_family(
            creator=creator, visibility="family"
        )

        private_family = FamilyTestDataGenerator.create_family(
            creator=creator, visibility="private"
        )

        # 添加成员到家族可见家族
        FamilyMembershipFactory(family=family_visible, user=member, role="member")

        return {
            "creator": creator,
            "member": member,
            "outsider": outsider,
            "public_family": public_family,
            "family_visible": family_visible,
            "private_family": private_family,
        }


# 测试工具函数
class FamilyTestUtils:
    """家族测试工具类"""

    @staticmethod
    def assert_family_data(family: Family, expected_data: Dict[str, Any]):
        """断言家族数据"""
        for field, expected_value in expected_data.items():
            actual_value = getattr(family, field)
            assert actual_value == expected_value, (
                f"字段 {field} 不匹配: 期望 {expected_value}, 实际 {actual_value}"
            )

    @staticmethod
    def assert_family_settings(settings: FamilySettings, expected_data: Dict[str, Any]):
        """断言家族设置数据"""
        for field, expected_value in expected_data.items():
            actual_value = getattr(settings, field)
            assert actual_value == expected_value, (
                f"设置字段 {field} 不匹配: 期望 {expected_value}, 实际 {actual_value}"
            )

    @staticmethod
    def assert_invitation_data(
        invitation: FamilyInvitation, expected_data: Dict[str, Any]
    ):
        """断言邀请数据"""
        for field, expected_value in expected_data.items():
            actual_value = getattr(invitation, field)
            assert actual_value == expected_value, (
                f"邀请字段 {field} 不匹配: 期望 {expected_value}, 实际 {actual_value}"
            )

    @staticmethod
    def create_api_test_data() -> Dict[str, Any]:
        """创建API测试数据"""
        return {
            "create_data": {
                "name": "API测试家族",
                "description": "用于API测试的家族",
                "visibility": "public",
                "allow_join": True,
                "tags": ["API", "测试"],
                "origin_location": "北京",
                "motto": "团结就是力量",
            },
            "update_data": {
                "description": "更新后的描述",
                "motto": "新的座右铭",
                "allow_join": False,
            },
            "settings_data": {
                "tree_layout": "horizontal",
                "show_photos": True,
                "show_birth_dates": False,
                "theme": "modern",
                "privacy_level": "family",
            },
            "invitation_data": {
                "invitee_email": "newmember@example.com",
                "invitee_name": "新成员",
                "message": "欢迎加入我们的家族",
            },
        }

    @staticmethod
    def create_performance_test_data(count: int = 100) -> List[Dict[str, Any]]:
        """创建性能测试数据"""
        return [
            {
                "name": f"性能测试家族{i}",
                "description": f"用于性能测试的家族{i}",
                "visibility": "public" if i % 2 == 0 else "family",
                "tags": ["性能", "测试", f"批次{i // 10}"],
            }
            for i in range(count)
        ]

    @staticmethod
    def cleanup_test_data():
        """清理测试数据"""
        # 删除所有测试创建的数据
        FamilyInvitation.objects.all().delete()
        FamilyMembership.objects.all().delete()
        FamilySettings.objects.all().delete()
        Family.objects.all().delete()
        User.objects.all().delete()

    @staticmethod
    def measure_execution_time(func, *args, **kwargs) -> tuple[Any, float]:
        """测量函数执行时间"""
        import time

        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        return result, execution_time

    @staticmethod
    def create_mock_request(user: User = None, method: str = "GET", data: Dict = None):
        """创建模拟请求"""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = getattr(factory, method.lower())("/", data=data or {})

        if user:
            request.user = user

        return request


# 测试装饰器
def with_test_settings(func):
    """测试设置装饰器"""
    return override_settings(**TEST_SETTINGS)(func)


def skip_if_no_db(func):
    """如果没有数据库则跳过测试"""
    return pytest.mark.skipif(
        not hasattr(pytest, "mark") or not pytest.mark.django_db,
        reason="需要数据库支持",
    )(func)


# pytest fixtures
@pytest.fixture
def user_factory():
    """用户工厂fixture"""
    return UserFactory


@pytest.fixture
def family_factory():
    """家族工厂fixture"""
    return FamilyFactory


@pytest.fixture
def family_settings_factory():
    """家族设置工厂fixture"""
    return FamilySettingsFactory


@pytest.fixture
def family_invitation_factory():
    """家族邀请工厂fixture"""
    return FamilyInvitationFactory


@pytest.fixture
def test_data_generator():
    """测试数据生成器fixture"""
    return FamilyTestDataGenerator


@pytest.fixture
def test_utils():
    """测试工具fixture"""
    return FamilyTestUtils


@pytest.fixture
def basic_family_scenario():
    """基本家族场景fixture"""
    return FamilyTestDataGenerator.create_test_scenario("basic_family")


@pytest.fixture
def family_with_members_scenario():
    """带成员家族场景fixture"""
    return FamilyTestDataGenerator.create_test_scenario("family_with_members")


@pytest.fixture
def privacy_test_scenario():
    """隐私测试场景fixture"""
    return FamilyTestDataGenerator.create_test_scenario("privacy_test")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """为所有测试启用数据库访问"""
    pass


@pytest.fixture(scope="function")
def clean_test_data():
    """清理测试数据fixture"""
    yield
    FamilyTestUtils.cleanup_test_data()


# 测试标记
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.family_app,
]


# 测试配置类
class FamilyTestConfig:
    """家族测试配置类"""

    # API端点
    API_ENDPOINTS = {
        "families_list": "/api/families/",
        "family_detail": "/api/families/{id}/",
        "family_settings": "/api/families/{id}/settings/",
        "family_invitations": "/api/families/{id}/invitations/",
        "family_members": "/api/families/{id}/members/",
        "family_statistics": "/api/families/{id}/statistics/",
        "family_export": "/api/families/{id}/export/",
        "family_import": "/api/families/import/",
    }

    # 测试数据限制
    MAX_TEST_FAMILIES = 1000
    MAX_TEST_MEMBERS = 100
    MAX_TEST_INVITATIONS = 50

    # 性能基准
    API_RESPONSE_TIME_LIMIT = 1.0  # 秒
    DATABASE_QUERY_TIME_LIMIT = 0.5  # 秒
    CACHE_ACCESS_TIME_LIMIT = 0.01  # 秒

    # 并发测试配置
    CONCURRENT_THREADS = 10
    CONCURRENT_OPERATIONS = 50

    @classmethod
    def get_endpoint(cls, name: str, **kwargs) -> str:
        """获取API端点URL"""
        endpoint = cls.API_ENDPOINTS.get(name)
        if not endpoint:
            raise ValueError(f"未知的端点名称: {name}")

        return endpoint.format(**kwargs)


if __name__ == "__main__":
    # 运行测试配置验证
    print("Family应用测试配置加载完成")
    print(
        f"支持的测试场景: {list(FamilyTestDataGenerator.create_test_scenario.__annotations__.keys())}"
    )
    print(f"API端点数量: {len(FamilyTestConfig.API_ENDPOINTS)}")
    print("测试工具和工厂已准备就绪")
