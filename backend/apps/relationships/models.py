"""
关系管理模块数据模型

该模块定义了家族成员之间的关系数据模型，包括血缘关系、婚姻关系等。
遵循Django最佳实践和Google Python Style Guide。
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel, SoftDeleteModel, VisibilityChoices


# 关系类型枚举
class RelationshipTypeChoices(models.TextChoices):
    """关系类型选择枚举"""

    # 血缘关系
    PARENT = "parent", _("父母")
    CHILD = "child", _("子女")
    SIBLING = "sibling", _("兄弟姐妹")
    GRANDPARENT = "grandparent", _("祖父母/外祖父母")
    GRANDCHILD = "grandchild", _("孙子女/外孙子女")
    UNCLE_AUNT = "uncle_aunt", _("叔伯/姑姨")
    NEPHEW_NIECE = "nephew_niece", _("侄子女/外甥女")
    COUSIN = "cousin", _("堂兄弟姐妹/表兄弟姐妹")

    # 婚姻关系
    SPOUSE = "spouse", _("配偶")
    EX_SPOUSE = "ex_spouse", _("前配偶")

    # 姻亲关系
    PARENT_IN_LAW = "parent_in_law", _("岳父母/公婆")
    CHILD_IN_LAW = "child_in_law", _("女婿/儿媳")
    SIBLING_IN_LAW = "sibling_in_law", _("姐夫/妹夫/嫂子/弟媳")

    # 其他关系
    ADOPTIVE_PARENT = "adoptive_parent", _("养父母")
    ADOPTIVE_CHILD = "adoptive_child", _("养子女")
    STEPPARENT = "stepparent", _("继父母")
    STEPCHILD = "stepchild", _("继子女")
    GODPARENT = "godparent", _("干父母")
    GODCHILD = "godchild", _("干子女")


class ConfidenceLevelChoices(models.TextChoices):
    """可信度选择枚举"""

    HIGH = "high", _("高")
    MEDIUM = "medium", _("中")
    LOW = "low", _("低")
    UNKNOWN = "unknown", _("未知")


class MarriageStatusChoices(models.TextChoices):
    """婚姻状态选择枚举"""

    MARRIED = "married", _("已婚")
    DIVORCED = "divorced", _("已离婚")
    SEPARATED = "separated", _("分居")
    WIDOWED = "widowed", _("丧偶")
    ANNULLED = "annulled", _("婚姻无效")


class Relationship(SoftDeleteModel):
    """
    家族关系模型

    存储家族成员之间的关系信息，包括血缘关系、婚姻关系等。
    """

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name="家族ID",
        help_text="所属家族ID，逻辑关联families.id",
        db_comment="家族ID，逻辑关联families.id",
    )

    # 关系双方的成员ID（逻辑关联）
    from_member_id = models.BigIntegerField(
        verbose_name="起始成员ID",
        help_text="关系起始成员ID，逻辑关联family_members.id",
        db_comment="关系起始成员ID，逻辑关联family_members.id",
    )

    to_member_id = models.BigIntegerField(
        verbose_name="目标成员ID",
        help_text="关系目标成员ID，逻辑关联family_members.id",
        db_comment="关系目标成员ID，逻辑关联family_members.id",
    )

    # 关系类型
    relationship_type = models.CharField(
        max_length=20,
        choices=RelationshipTypeChoices.choices,
        verbose_name="关系类型",
        help_text="成员之间的关系类型",
        db_comment="关系类型：parent-父母，child-子女，spouse-配偶等",
    )

    # 关系的具体描述
    relationship_detail = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="关系详情",
        help_text='关系的具体描述，如"长子"、"次女"等',
        db_comment="关系详情描述",
    )

    # 关系确认状态
    is_confirmed = models.BooleanField(
        default=False,
        verbose_name="是否确认",
        help_text="关系是否已被相关成员确认",
        db_comment="是否确认：1-已确认，0-未确认",
    )

    # 关系的可信度
    confidence_level = models.CharField(
        max_length=10,
        choices=ConfidenceLevelChoices.choices,
        default=ConfidenceLevelChoices.MEDIUM,
        verbose_name="可信度",
        help_text="关系信息的可信度",
        db_comment="可信度：high-高，medium-中，low-低，unknown-未知",
    )

    # 关系开始时间（如结婚时间）
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="开始时间",
        help_text="关系开始的时间",
        db_comment="关系开始时间",
    )

    # 关系结束时间（如离婚时间、去世时间）
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="结束时间",
        help_text="关系结束的时间",
        db_comment="关系结束时间",
    )

    # 关系是否仍然有效
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否有效",
        help_text="关系是否仍然有效",
        db_comment="是否有效：1-有效，0-无效",
    )

    # 关系备注
    notes = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="备注",
        help_text="关系的备注信息",
        db_comment="关系备注信息",
    )

    # 可见性设置
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name="可见性",
        help_text="关系信息的可见性设置",
        db_comment="可见性设置",
    )

    # 创建者ID
    creator_id = models.BigIntegerField(
        verbose_name="创建者ID",
        help_text="创建此关系记录的用户ID，逻辑关联users.id",
        db_comment="创建者ID，逻辑关联users.id",
    )

    # 确认者ID
    confirmed_by_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="确认者ID",
        help_text="确认此关系的用户ID，逻辑关联users.id",
        db_comment="确认者ID，逻辑关联users.id",
    )

    # 确认时间
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="确认时间",
        help_text="关系被确认的时间",
        db_comment="关系确认时间",
    )

    class Meta:
        db_table = "family_relationships"
        verbose_name = "家族关系"
        verbose_name_plural = "家族关系"
        indexes = [
            models.Index(fields=["family_id"]),
            models.Index(fields=["from_member_id"]),
            models.Index(fields=["to_member_id"]),
            models.Index(fields=["relationship_type"]),
            models.Index(fields=["is_confirmed"]),
            models.Index(fields=["is_active"]),
        ]
        unique_together = [
            ("from_member_id", "to_member_id", "relationship_type"),  # 防止重复关系
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"成员{self.from_member_id}与成员{self.to_member_id}的{self.get_relationship_type_display()}关系"

    def get_reverse_relationship_type(self):
        """获取反向关系类型"""
        reverse_map = {
            "parent": "child",
            "child": "parent",
            "sibling": "sibling",
            "grandparent": "grandchild",
            "grandchild": "grandparent",
            "uncle_aunt": "nephew_niece",
            "nephew_niece": "uncle_aunt",
            "cousin": "cousin",
            "spouse": "spouse",
            "ex_spouse": "ex_spouse",
            "parent_in_law": "child_in_law",
            "child_in_law": "parent_in_law",
            "sibling_in_law": "sibling_in_law",
            "adoptive_parent": "adoptive_child",
            "adoptive_child": "adoptive_parent",
            "stepparent": "stepchild",
            "stepchild": "stepparent",
            "godparent": "godchild",
            "godchild": "godparent",
        }
        return reverse_map.get(self.relationship_type, self.relationship_type)

    def confirm_relationship(self, confirmed_by_id):
        """确认关系"""
        from django.utils import timezone

        self.is_confirmed = True
        self.confirmed_by_id = confirmed_by_id
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_by_id", "confirmed_at"])

    def is_blood_relation(self):
        """是否为血缘关系"""
        blood_relations = [
            "parent",
            "child",
            "sibling",
            "grandparent",
            "grandchild",
            "uncle_aunt",
            "nephew_niece",
            "cousin",
        ]
        return self.relationship_type in blood_relations

    def is_marriage_relation(self):
        """是否为婚姻关系"""
        marriage_relations = ["spouse", "ex_spouse"]
        return self.relationship_type in marriage_relations

    def is_in_law_relation(self):
        """是否为姻亲关系"""
        in_law_relations = ["parent_in_law", "child_in_law", "sibling_in_law"]
        return self.relationship_type in in_law_relations


class Marriage(BaseModel):
    """
    婚姻记录模型

    专门记录婚姻信息，包括结婚、离婚等详细信息。
    """

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name="家族ID",
        help_text="所属家族ID，逻辑关联families.id",
        db_comment="所属家族ID，逻辑关联families.id",
    )

    # 夫妻双方的成员ID（逻辑关联）
    husband_id = models.BigIntegerField(
        verbose_name="丈夫ID",
        help_text="丈夫的成员ID，逻辑关联family_members.id",
        db_comment="丈夫的成员ID，逻辑关联family_members.id",
    )

    wife_id = models.BigIntegerField(
        verbose_name="妻子ID",
        help_text="妻子的成员ID，逻辑关联family_members.id",
        db_comment="妻子的成员ID，逻辑关联family_members.id",
    )

    # 婚姻状态
    status = models.CharField(
        max_length=20,
        choices=MarriageStatusChoices.choices,
        default=MarriageStatusChoices.MARRIED,
        verbose_name="婚姻状态",
        db_comment="婚姻状态：married-已婚，divorced-已离婚，separated-分居，widowed-丧偶，annulled-婚姻无效",
    )

    # 结婚信息
    marriage_date = models.DateField(
        blank=True, null=True, verbose_name="结婚日期", db_comment="结婚日期"
    )

    marriage_place = models.CharField(
        max_length=100, blank=True, verbose_name="结婚地点", db_comment="结婚地点"
    )

    # 离婚信息
    divorce_date = models.DateField(
        blank=True, null=True, verbose_name="离婚日期", db_comment="离婚日期"
    )

    divorce_reason = models.CharField(
        max_length=200, blank=True, verbose_name="离婚原因", db_comment="离婚原因"
    )

    # 婚姻序号（第几次婚姻）
    marriage_order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="婚姻序号",
        help_text="第几次婚姻",
        db_comment="第几次婚姻",
    )

    # 子女数量
    children_count = models.PositiveIntegerField(
        default=0,
        verbose_name="子女数量",
        help_text="这段婚姻中的子女数量",
        db_comment="这段婚姻中的子女数量",
    )

    # 婚姻备注
    notes = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="备注",
        help_text="婚姻的备注信息",
        db_comment="婚姻备注信息",
    )

    # 可见性设置
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name="可见性",
        db_comment="可见性设置",
    )

    # 创建者ID
    creator_id = models.BigIntegerField(
        verbose_name="创建者ID",
        help_text="创建此婚姻记录的用户ID，逻辑关联users.id",
        db_comment="创建者ID，逻辑关联users.id",
    )

    class Meta:
        db_table = "family_marriages"
        verbose_name = "婚姻记录"
        verbose_name_plural = "婚姻记录"
        indexes = [
            models.Index(fields=["family_id"]),
            models.Index(fields=["husband_id"]),
            models.Index(fields=["wife_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["marriage_date"]),
        ]
        unique_together = [
            ("husband_id", "wife_id", "marriage_order"),  # 防止重复的婚姻记录
        ]
        ordering = ["-marriage_date", "-created_at"]

    def __str__(self):
        return f"成员{self.husband_id}与成员{self.wife_id}的婚姻记录"

    def get_duration(self):
        """获取婚姻持续时间"""
        if not self.marriage_date:
            return None

        from datetime import date

        end_date = self.divorce_date if self.divorce_date else date.today()

        if self.status in ["divorced", "annulled"]:
            end_date = self.divorce_date or date.today()
        elif self.status == "widowed":
            # 需要从成员信息中获取去世日期
            end_date = date.today()  # 简化处理
        else:
            end_date = date.today()

        duration = end_date - self.marriage_date
        return duration.days

    def is_current_marriage(self):
        """是否为当前婚姻"""
        return self.status == "married"

    def end_marriage(self, end_date, reason="", status="divorced"):
        """结束婚姻"""
        self.status = status
        self.divorce_date = end_date
        if reason:
            self.divorce_reason = reason
        self.save(update_fields=["status", "divorce_date", "divorce_reason"])


class FamilyTree(BaseModel):
    """
    家族树结构模型

    存储家族树的结构信息，用于快速查询和显示族谱。
    """

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name="家族ID",
        help_text="所属家族ID，逻辑关联families.id",
        db_comment="所属家族ID，逻辑关联families.id",
    )

    # 成员ID（逻辑关联）
    member_id = models.BigIntegerField(
        verbose_name="成员ID",
        help_text="成员ID，逻辑关联family_members.id",
        db_comment="成员ID，逻辑关联family_members.id",
    )

    # 父亲ID（逻辑关联）
    father_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="父亲ID",
        help_text="父亲的成员ID，逻辑关联family_members.id",
        db_comment="父亲的成员ID，逻辑关联family_members.id",
    )

    # 母亲ID（逻辑关联）
    mother_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="母亲ID",
        help_text="母亲的成员ID，逻辑关联family_members.id",
        db_comment="母亲的成员ID，逻辑关联family_members.id",
    )

    # 配偶ID（逻辑关联）
    spouse_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="配偶ID",
        help_text="配偶的成员ID，逻辑关联family_members.id",
        db_comment="配偶的成员ID，逻辑关联family_members.id",
    )

    # 世代
    generation = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="世代",
        help_text="成员在家族中的世代",
        db_comment="成员在家族中的世代",
    )

    # 在同世代中的位置
    position_in_generation = models.PositiveIntegerField(
        default=1,
        verbose_name="世代内位置",
        help_text="在同世代中的位置序号",
        db_comment="在同世代中的位置序号",
    )

    # 子女数量
    children_count = models.PositiveIntegerField(
        default=0, verbose_name="子女数量", db_comment="子女数量"
    )

    # 后代数量
    descendants_count = models.PositiveIntegerField(
        default=0,
        verbose_name="后代数量",
        help_text="所有后代的总数量",
        db_comment="所有后代的总数量",
    )

    # 是否为根节点
    is_root = models.BooleanField(
        default=False,
        verbose_name="是否为根节点",
        help_text="是否为家族树的根节点",
        db_comment="是否为家族树的根节点：1-是，0-否",
    )

    # 树路径（用于快速查询祖先和后代）
    tree_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="树路径",
        help_text="从根节点到当前节点的路径，用/分隔",
        db_comment="从根节点到当前节点的路径，用/分隔",
    )

    # 最后更新时间
    last_updated = models.DateTimeField(
        auto_now=True, verbose_name="最后更新时间", db_comment="最后更新时间"
    )

    class Meta:
        db_table = "family_trees"
        verbose_name = "家族树"
        verbose_name_plural = "家族树"
        indexes = [
            models.Index(fields=["family_id"]),
            models.Index(fields=["member_id"]),
            models.Index(fields=["father_id"]),
            models.Index(fields=["mother_id"]),
            models.Index(fields=["spouse_id"]),
            models.Index(fields=["generation"]),
            models.Index(fields=["is_root"]),
            models.Index(fields=["tree_path"]),
        ]
        unique_together = [
            ("family_id", "member_id"),  # 每个成员在家族中只有一个树节点
        ]
        ordering = ["generation", "position_in_generation"]

    def __str__(self):
        return f"家族{self.family_id}成员{self.member_id}的树节点"

    def get_ancestors(self):
        """获取祖先节点ID列表"""
        if not self.tree_path:
            return []
        path_parts = self.tree_path.strip("/").split("/")
        return [int(part) for part in path_parts if part.isdigit()]

    def get_depth(self):
        """获取节点深度"""
        return len(self.get_ancestors())

    def update_tree_path(self):
        """更新树路径"""
        ancestors = []
        if self.father_id:
            # 获取父亲的树路径
            try:
                father_node = FamilyTree.objects.get(
                    family_id=self.family_id, member_id=self.father_id
                )
                if father_node.tree_path:
                    ancestors.extend(father_node.get_ancestors())
                ancestors.append(self.father_id)
            except FamilyTree.DoesNotExist:
                pass

        self.tree_path = "/" + "/".join(map(str, ancestors)) + "/" if ancestors else "/"
        self.save(update_fields=["tree_path"])

    def update_descendants_count(self):
        """更新后代数量"""
        # 这里需要递归计算所有后代
        # 简化实现，实际应该使用更高效的算法
        descendants = FamilyTree.objects.filter(
            family_id=self.family_id,
            tree_path__startswith=self.tree_path + str(self.member_id) + "/",
        ).count()

        self.descendants_count = descendants
        self.save(update_fields=["descendants_count"])
