"""
Family应用Schema层单元测试

测试Family应用的数据序列化和验证，包括输入验证、输出格式化、字段映射等。
遵循Django Ninja和Pydantic最佳实践。
"""

import pytest

from django.contrib.auth import get_user_model

from pydantic import ValidationError as PydanticValidationError

from ..schemas import (
    # 基础Schema
    FamilyBaseSchema,
    FamilyCreateSchema,
    FamilyUpdateSchema,
    FamilyModelSchema,
    
    # 设置Schema
    FamilySettingsSchema,
    FamilySettingsModelSchema,
    
    # 邀请Schema
    FamilyInvitationCreateSchema,
    FamilyInvitationModelSchema,
    
    # 查询Schema
    FamilyFilterSchema,
    FamilyQuerySchema,
    PublicFamilyQuerySchema,
    
    # 统计Schema
    FamilyStatisticsSchema,
    
    # 枚举
    FamilyVisibility,
    InvitationStatus,
    TreeLayout,
    ExportFormat,
    
    # 其他Schema
    FamilyJoinRequestSchema,
    FamilyTreeConfigSchema,
    FamilyExportSchema,
    FamilyImportSchema,
)
from ..models import Family, FamilySettings, FamilyInvitation

User = get_user_model()

@pytest.mark.django_db
class TestFamilyEnums:
    """Family应用枚举测试"""
    
    def test_family_visibility_enum(self):
        """测试家族可见性枚举"""
        # 测试所有有效值
        valid_values = ['public', 'family', 'private']
        for value in valid_values:
            assert value in FamilyVisibility.__members__.values()
        
        # 测试枚举属性
        assert FamilyVisibility.PUBLIC == 'public'
        assert FamilyVisibility.FAMILY == 'family'
        assert FamilyVisibility.PRIVATE == 'private'
    
    def test_invitation_status_enum(self):
        """测试邀请状态枚举"""
        valid_statuses = ['pending', 'accepted', 'rejected', 'expired']
        for status in valid_statuses:
            assert status in InvitationStatus.__members__.values()
        
        assert InvitationStatus.PENDING == 'pending'
        assert InvitationStatus.ACCEPTED == 'accepted'
        assert InvitationStatus.REJECTED == 'rejected'
        assert InvitationStatus.EXPIRED == 'expired'
    
    def test_tree_layout_enum(self):
        """测试树形布局枚举"""
        valid_layouts = ['vertical', 'horizontal', 'circular', 'fan']
        for layout in valid_layouts:
            assert layout in TreeLayout.__members__.values()
    
    def test_export_format_enum(self):
        """测试导出格式枚举"""
        valid_formats = ['pdf', 'png', 'svg', 'gedcom']
        for format_type in valid_formats:
            assert format_type in ExportFormat.__members__.values()

@pytest.mark.django_db
class TestFamilyBaseSchemas:
    """Family基础Schema测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.valid_family_data = {
            'name': '测试家族',
            'description': '这是一个测试家族',
            'visibility': 'family',
            'allow_join': True,
            'tags': '测试,家族',
            'origin_location': '北京',
            'motto': '团结友爱'
        }
    
    def test_family_base_schema_validation_success(self):
        """测试家族基础Schema验证成功"""
        schema = FamilyBaseSchema(**self.valid_family_data)
        
        assert schema.name == '测试家族'
        assert schema.description == '这是一个测试家族'
        assert schema.visibility == 'family'
        assert schema.allow_join is True
        assert schema.tags == '测试,家族'
        assert schema.origin_location == '北京'
        assert schema.motto == '团结友爱'
    
    def test_family_base_schema_name_validation(self):
        """测试家族基础Schema名称验证"""
        # 测试空名称
        invalid_data = self.valid_family_data.copy()
        invalid_data['name'] = ''
        
        with pytest.raises(PydanticValidationError) as exc_info:
            FamilyBaseSchema(**invalid_data)
        assert 'name' in str(exc_info.value)
        
        # 测试名称过长
        invalid_data['name'] = 'A' * 101
        with pytest.raises(PydanticValidationError):
            FamilyBaseSchema(**invalid_data)
        
        # 测试名称只包含空格
        invalid_data['name'] = '   '
        with pytest.raises(PydanticValidationError):
            FamilyBaseSchema(**invalid_data)
    
    def test_family_base_schema_description_validation(self):
        """测试家族基础Schema描述验证"""
        # 测试描述过长
        invalid_data = self.valid_family_data.copy()
        invalid_data['description'] = 'A' * 1001
        
        with pytest.raises(PydanticValidationError):
            FamilyBaseSchema(**invalid_data)
        
        # 测试空描述（应该允许）
        valid_data = self.valid_family_data.copy()
        valid_data['description'] = ''
        schema = FamilyBaseSchema(**valid_data)
        assert schema.description == ''
    
    def test_family_base_schema_visibility_validation(self):
        """测试家族基础Schema可见性验证"""
        # 测试有效可见性
        for visibility in ['public', 'family', 'private']:
            data = self.valid_family_data.copy()
            data['visibility'] = visibility
            schema = FamilyBaseSchema(**data)
            assert schema.visibility == visibility
        
        # 测试无效可见性
        invalid_data = self.valid_family_data.copy()
        invalid_data['visibility'] = 'invalid'
        
        with pytest.raises(PydanticValidationError):
            FamilyBaseSchema(**invalid_data)
    
    def test_family_create_schema_validation(self):
        """测试家族创建Schema验证"""
        schema = FamilyCreateSchema(**self.valid_family_data)
        
        # 验证所有必需字段
        assert schema.name == '测试家族'
        assert schema.description == '这是一个测试家族'
        
        # 测试可选字段默认值
        minimal_data = {'name': '最小家族'}
        schema = FamilyCreateSchema(**minimal_data)
        assert schema.name == '最小家族'
        assert schema.visibility == 'family'  # 默认值
        assert schema.allow_join is True  # 默认值
    
    def test_family_update_schema_validation(self):
        """测试家族更新Schema验证"""
        update_data = {
            'name': '更新后的家族名称',
            'description': '更新后的描述'
        }
        
        schema = FamilyUpdateSchema(**update_data)
        assert schema.name == '更新后的家族名称'
        assert schema.description == '更新后的描述'
        
        # 测试部分更新
        partial_data = {'name': '仅更新名称'}
        schema = FamilyUpdateSchema(**partial_data)
        assert schema.name == '仅更新名称'

@pytest.mark.django_db
class TestFamilyModelSchemas:
    """Family模型Schema测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='schemauser',
            email='schema@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='Schema测试家族',
            description='用于测试Schema',
            creator=self.user,
            visibility='family',
            allow_join=True,
            member_count=5,
            generation_count=3,
            tags='测试,Schema',
            origin_location='上海',
            motto='测试座右铭'
        )
    
    def test_family_model_schema_from_orm(self):
        """测试从ORM模型创建Schema"""
        schema = FamilyModelSchema.from_orm(self.family)
        
        assert schema.id == self.family.id
        assert schema.name == self.family.name
        assert schema.description == self.family.description
        assert schema.creator_id == self.family.creator_id
        assert schema.visibility == self.family.visibility
        assert schema.is_active == self.family.is_active
        assert schema.allow_join == self.family.allow_join
        assert schema.member_count == self.family.member_count
        assert schema.generation_count == self.family.generation_count
        assert schema.tags == self.family.tags
        assert schema.origin_location == self.family.origin_location
        assert schema.motto == self.family.motto
        assert schema.created_at == self.family.created_at
        assert schema.updated_at == self.family.updated_at
    
    def test_family_model_schema_serialization(self):
        """测试家族模型Schema序列化"""
        schema = FamilyModelSchema.from_orm(self.family)
        data = schema.dict()
        
        # 验证序列化数据
        assert data['id'] == self.family.id
        assert data['name'] == self.family.name
        assert data['creator_id'] == self.family.creator_id
        assert isinstance(data['created_at'], datetime)
        assert isinstance(data['updated_at'], datetime)
    
    def test_family_model_schema_json_serialization(self):
        """测试家族模型Schema JSON序列化"""
        schema = FamilyModelSchema.from_orm(self.family)
        json_data = schema.json()
        
        # 验证JSON序列化
        assert isinstance(json_data, str)
        
        # 解析JSON并验证
        import json
        parsed_data = json.loads(json_data)
        assert parsed_data['name'] == self.family.name
        assert parsed_data['id'] == self.family.id

@pytest.mark.django_db
class TestFamilySettingsSchemas:
    """Family设置Schema测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='settingsuser',
            email='settings@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='设置Schema测试家族',
            creator=self.user
        )
        
        self.settings = FamilySettings.objects.create(
            family=self.family,
            tree_layout='horizontal',
            show_photos=False,
            show_birth_dates=True,
            theme='modern',
            privacy_level='private',
            require_approval=False
        )
    
    def test_family_settings_schema_validation(self):
        """测试家族设置Schema验证"""
        settings_data = {
            'tree_layout': 'vertical',
            'show_photos': True,
            'show_birth_dates': True,
            'show_death_dates': False,
            'theme': 'classic',
            'privacy_level': 'family',
            'require_approval': True
        }
        
        schema = FamilySettingsSchema(**settings_data)
        
        assert schema.tree_layout == 'vertical'
        assert schema.show_photos is True
        assert schema.theme == 'classic'
        assert schema.privacy_level == 'family'
    
    def test_family_settings_schema_tree_layout_validation(self):
        """测试家族设置Schema树形布局验证"""
        # 测试有效布局
        valid_layouts = ['vertical', 'horizontal', 'circular', 'fan']
        for layout in valid_layouts:
            data = {'tree_layout': layout}
            schema = FamilySettingsSchema(**data)
            assert schema.tree_layout == layout
        
        # 测试无效布局
        with pytest.raises(PydanticValidationError):
            FamilySettingsSchema(tree_layout='invalid_layout')
    
    def test_family_settings_model_schema_from_orm(self):
        """测试从ORM模型创建设置Schema"""
        schema = FamilySettingsModelSchema.from_orm(self.settings)
        
        assert schema.family_id == self.family.id
        assert schema.tree_layout == 'horizontal'
        assert schema.show_photos is False
        assert schema.show_birth_dates is True
        assert schema.theme == 'modern'
        assert schema.privacy_level == 'private'
        assert schema.require_approval is False

@pytest.mark.django_db
class TestFamilyInvitationSchemas:
    """Family邀请Schema测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.inviter = User.objects.create_user(
            username='inviter',
            email='inviter@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='邀请Schema测试家族',
            creator=self.inviter
        )
        
        self.invitation = FamilyInvitation.objects.create(
            family=self.family,
            inviter=self.inviter,
            invitee_email='invitee@example.com',
            invitee_name='被邀请者',
            invitation_code='test_code_123',
            expires_at=timezone.now() + timedelta(days=7),
            message='欢迎加入我们的家族'
        )
    
    def test_family_invitation_create_schema_validation(self):
        """测试家族邀请创建Schema验证"""
        invitation_data = {
            'invitee_email': 'newuser@example.com',
            'invitee_name': '新用户',
            'message': '欢迎加入我们的家族'
        }
        
        schema = FamilyInvitationCreateSchema(**invitation_data)
        
        assert schema.invitee_email == 'newuser@example.com'
        assert schema.invitee_name == '新用户'
        assert schema.message == '欢迎加入我们的家族'
    
    def test_family_invitation_create_schema_email_validation(self):
        """测试家族邀请创建Schema邮箱验证"""
        # 测试有效邮箱
        valid_data = {
            'invitee_email': 'valid@example.com',
            'invitee_name': '有效用户'
        }
        schema = FamilyInvitationCreateSchema(**valid_data)
        assert schema.invitee_email == 'valid@example.com'
        
        # 测试无效邮箱
        invalid_data = {
            'invitee_email': 'invalid_email',
            'invitee_name': '无效用户'
        }
        with pytest.raises(PydanticValidationError):
            FamilyInvitationCreateSchema(**invalid_data)
    
    def test_family_invitation_create_schema_phone_validation(self):
        """测试家族邀请创建Schema手机号验证"""
        # 测试有效手机号
        valid_data = {
            'invitee_email': 'user@example.com',
            'invitee_name': '用户',
            'invitee_phone': '+86-13800138000'
        }
        schema = FamilyInvitationCreateSchema(**valid_data)
        assert schema.invitee_phone == '+86-13800138000'
        
        # 测试无效手机号
        invalid_data = {
            'invitee_email': 'user@example.com',
            'invitee_name': '用户',
            'invitee_phone': '123'
        }
        with pytest.raises(PydanticValidationError):
            FamilyInvitationCreateSchema(**invalid_data)
    
    def test_family_invitation_process_schema_validation(self):
        """测试家族邀请处理Schema验证"""
        # 测试接受邀请
        accept_data = {
            'action': 'accept'
        }
        schema = FamilyInvitationProcessSchema(**accept_data)
        assert schema.action == 'accept'
        
        # 测试拒绝邀请
        reject_data = {
            'action': 'reject',
            'rejection_reason': '暂时不想加入'
        }
        schema = FamilyInvitationProcessSchema(**reject_data)
        assert schema.action == 'reject'
        assert schema.rejection_reason == '暂时不想加入'
        
        # 测试无效操作
        with pytest.raises(PydanticValidationError):
            FamilyInvitationProcessSchema(action='invalid_action')
    
    def test_family_invitation_model_schema_from_orm(self):
        """测试从ORM模型创建邀请Schema"""
        schema = FamilyInvitationModelSchema.from_orm(self.invitation)
        
        assert schema.id == self.invitation.id
        assert schema.family_id == self.family.id
        assert schema.inviter_id == self.inviter.id
        assert schema.invitee_email == 'invitee@example.com'
        assert schema.invitee_name == '被邀请者'
        assert schema.status == 'pending'
        assert schema.invitation_code == 'test_code_123'
        assert schema.message == '欢迎加入我们的家族'

@pytest.mark.django_db
class TestFamilyQuerySchemas:
    """Family查询Schema测试"""
    
    def test_family_filter_schema_validation(self):
        """测试家族过滤Schema验证"""
        filter_data = {
            'visibility': 'public',
            'allow_join': True,
            'is_active': True,
            'search': '测试家族',
            'tags': '测试,家族',
            'origin_location': '北京'
        }
        
        schema = FamilyFilterSchema(**filter_data)
        
        assert schema.visibility == 'public'
        assert schema.allow_join is True
        assert schema.is_active is True
        assert schema.search == '测试家族'
        assert schema.tags == '测试,家族'
        assert schema.origin_location == '北京'
    
    def test_family_query_schema_pagination(self):
        """测试家族查询Schema分页"""
        query_data = {
            'page': 2,
            'page_size': 20,
            'ordering': '-created_at'
        }
        
        schema = FamilyQuerySchema(**query_data)
        
        assert schema.page == 2
        assert schema.page_size == 20
        assert schema.ordering == '-created_at'
    
    def test_family_query_schema_validation_limits(self):
        """测试家族查询Schema验证限制"""
        # 测试页码限制
        with pytest.raises(PydanticValidationError):
            FamilyQuerySchema(page=0)  # 页码不能为0
        
        # 测试页面大小限制
        with pytest.raises(PydanticValidationError):
            FamilyQuerySchema(page_size=101)  # 页面大小不能超过100
        
        with pytest.raises(PydanticValidationError):
            FamilyQuerySchema(page_size=0)  # 页面大小不能为0
    
    def test_public_family_query_schema_restrictions(self):
        """测试公开家族查询Schema限制"""
        # 公开查询应该有更严格的限制
        query_data = {
            'search': '公开搜索',
            'page': 1,
            'page_size': 10
        }
        
        schema = PublicFamilyQuerySchema(**query_data)
        
        assert schema.search == '公开搜索'
        assert schema.page == 1
        assert schema.page_size == 10

@pytest.mark.django_db
class TestFamilyStatisticsSchemas:
    """Family统计Schema测试"""
    
    def test_family_statistics_schema_validation(self):
        """测试家族统计Schema验证"""
        stats_data = {
            'total_members': 50,
            'active_members': 45,
            'total_generations': 5,
            'male_members': 25,
            'female_members': 25,
            'average_age': 35.5,
            'oldest_member_age': 85,
            'youngest_member_age': 1
        }
        
        schema = FamilyStatisticsSchema(**stats_data)
        
        assert schema.total_members == 50
        assert schema.active_members == 45
        assert schema.total_generations == 5
        assert schema.male_members == 25
        assert schema.female_members == 25
        assert schema.average_age == 35.5
        assert schema.oldest_member_age == 85
        assert schema.youngest_member_age == 1
    
    def test_family_membership_schema_validation(self):
        """测试家族成员关系Schema验证"""
        membership_data = {
            'user_id': 1,
            'family_id': 1,
            'role': 'admin',
            'status': 'active',
            'joined_at': timezone.now(),
            'permissions': ['view', 'edit', 'manage']
        }
        
        schema = FamilyMembershipSchema(**membership_data)
        
        assert schema.user_id == 1
        assert schema.family_id == 1
        assert schema.role == 'admin'
        assert schema.status == 'active'
        assert isinstance(schema.joined_at, datetime)
        assert schema.permissions == ['view', 'edit', 'manage']

@pytest.mark.django_db
class TestFamilyOtherSchemas:
    """Family其他Schema测试"""
    
    def test_family_join_request_schema_validation(self):
        """测试家族加入请求Schema验证"""
        request_data = {
            'message': '我想加入这个家族',
            'relationship': '远房亲戚'
        }
        
        schema = FamilyJoinRequestSchema(**request_data)
        
        assert schema.message == '我想加入这个家族'
        assert schema.relationship == '远房亲戚'
    
    def test_family_tree_config_schema_validation(self):
        """测试家族树配置Schema验证"""
        config_data = {
            'layout': 'vertical',
            'show_photos': True,
            'show_dates': True,
            'theme': 'modern',
            'zoom_level': 1.0
        }
        
        schema = FamilyTreeConfigSchema(**config_data)
        
        assert schema.layout == 'vertical'
        assert schema.show_photos is True
        assert schema.show_dates is True
        assert schema.theme == 'modern'
        assert schema.zoom_level == 1.0
    
    def test_family_export_schema_validation(self):
        """测试家族导出Schema验证"""
        export_data = {
            'format': 'pdf',
            'include_photos': True,
            'include_private_info': False,
            'generations': 5
        }
        
        schema = FamilyExportSchema(**export_data)
        
        assert schema.format == 'pdf'
        assert schema.include_photos is True
        assert schema.include_private_info is False
        assert schema.generations == 5
    
    def test_family_import_schema_validation(self):
        """测试家族导入Schema验证"""
        import_data = {
            'format': 'gedcom',
            'merge_duplicates': True,
            'validate_data': True
        }
        
        schema = FamilyImportSchema(**import_data)
        
        assert schema.format == 'gedcom'
        assert schema.merge_duplicates is True
        assert schema.validate_data is True
    
    def test_family_path_params_schema_validation(self):
        """测试家族路径参数Schema验证"""
        path_data = {
            'family_id': 123
        }
        
        schema = FamilyPathParamsSchema(**path_data)
        
        assert schema.family_id == 123
        
        # 测试无效ID
        with pytest.raises(PydanticValidationError):
            FamilyPathParamsSchema(family_id=0)
        
        with pytest.raises(PydanticValidationError):
            FamilyPathParamsSchema(family_id=-1)

@pytest.mark.django_db
class TestDynamicSchemaGeneration:
    """动态Schema生成测试"""
    
    def test_create_dynamic_family_schema_basic(self):
        """测试基础动态家族Schema创建"""
        fields = ['name', 'description', 'visibility']
        DynamicSchema = create_dynamic_family_schema(fields)
        
        # 验证Schema类型
        assert issubclass(DynamicSchema, Schema)
        
        # 验证字段
        schema_data = {
            'name': '动态家族',
            'description': '动态创建的家族',
            'visibility': 'public'
        }
        
        schema = DynamicSchema(**schema_data)
        assert schema.name == '动态家族'
        assert schema.description == '动态创建的家族'
        assert schema.visibility == 'public'
    
    def test_create_dynamic_family_schema_with_optional_fields(self):
        """测试包含可选字段的动态家族Schema创建"""
        fields = ['name', 'description', 'tags', 'motto']
        optional_fields = ['tags', 'motto']
        
        DynamicSchema = create_dynamic_family_schema(
            fields, 
            optional_fields=optional_fields
        )
        
        # 测试必需字段
        minimal_data = {
            'name': '最小动态家族',
            'description': '最小数据'
        }
        
        schema = DynamicSchema(**minimal_data)
        assert schema.name == '最小动态家族'
        assert schema.description == '最小数据'
    
    def test_create_dynamic_family_schema_validation(self):
        """测试动态家族Schema验证"""
        fields = ['name', 'visibility']
        DynamicSchema = create_dynamic_family_schema(fields)
        
        # 测试有效数据
        valid_data = {
            'name': '验证测试家族',
            'visibility': 'family'
        }
        schema = DynamicSchema(**valid_data)
        assert schema.name == '验证测试家族'
        
        # 测试无效数据
        invalid_data = {
            'name': '',  # 空名称
            'visibility': 'family'
        }
        with pytest.raises(PydanticValidationError):
            DynamicSchema(**invalid_data)

@pytest.mark.django_db
class TestSchemaPerformance:
    """Schema性能测试"""
    
    def test_schema_validation_performance(self):
        """测试Schema验证性能"""
        import time
        
        # 准备大量测试数据
        test_data = []
        for i in range(1000):
            test_data.append({
                'name': f'性能测试家族{i}',
                'description': f'第{i}个性能测试家族',
                'visibility': 'public' if i % 2 == 0 else 'family',
                'allow_join': i % 3 == 0,
                'tags': f'测试,性能,{i}',
                'origin_location': f'城市{i % 10}',
                'motto': f'座右铭{i}'
            })
        
        # 测试验证性能
        start_time = time.time()
        
        schemas = []
        for data in test_data:
            schema = FamilyCreateSchema(**data)
            schemas.append(schema)
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # 验证性能要求
        assert validation_time < 2.0  # 应该在2秒内完成
        assert len(schemas) == 1000
    
    def test_schema_serialization_performance(self):
        """测试Schema序列化性能"""
        # 创建测试用户和家族
        user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='testpass123'
        )
        
        families = []
        for i in range(100):
            family = Family.objects.create(
                name=f'序列化测试家族{i}',
                creator=user,
                description=f'第{i}个序列化测试家族'
            )
            families.append(family)
        
        start_time = time.time()
        
        # 序列化所有家族
        serialized_data = []
        for family in families:
            schema = FamilyModelSchema.from_orm(family)
            data = schema.dict()
            serialized_data.append(data)
        
        end_time = time.time()
        serialization_time = end_time - start_time
        
        # 验证性能要求
        assert serialization_time < 1.0  # 应该在1秒内完成
        assert len(serialized_data) == 100

if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])