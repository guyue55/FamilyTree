from django.core.management.base import BaseCommand
from datetime import date

class Command(BaseCommand):
    help = "Load sample family/members/relationships data for integration testing"

    def handle(self, *args, **options):
        from apps.family.models import Family
        from apps.members.models import Member
        from apps.relationships.models import Relationship

        family, _ = Family.objects.get_or_create(
            name='张氏家族',
            defaults={
                'creator_id': 1,
                'description': '测试数据家族',
                'visibility': 'public',
                'member_count': 1,
                'generation_count': 1
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Family ID: {family.id}"))

        members = {}

        def add_member(name, gender, birth, death, gen):
            m, _ = Member.objects.get_or_create(
                family_id=family.id,
                name=name,
                defaults={
                    'gender': gender,
                    'birth_date': birth,
                    'death_date': death,
                    'generation': gen,
                    'sort_order': 1,
                    'creator_id': 1
                }
            )
            members[name] = m
            return m

        add_member('张德高','male',date(1350,1,1),date(1420,12,31),1)
        add_member('李氏','female',date(1355,1,1),date(1425,12,31),1)
        add_member('张文华','male',date(1375,1,1),date(1448,12,31),2)
        add_member('张文武','male',date(1378,1,1),date(1451,12,31),2)
        add_member('张文秀','female',date(1380,1,1),date(1455,12,31),2)
        add_member('王氏','female',date(1378,1,1),date(1450,12,31),2)
        add_member('陈氏','female',date(1380,1,1),date(1453,12,31),2)
        add_member('张志远','male',date(1400,1,1),date(1475,12,31),3)
        add_member('张志明','male',date(1403,1,1),date(1478,12,31),3)
        add_member('张志强','male',date(1405,1,1),date(1480,12,31),3)
        add_member('张志华','male',date(1408,1,1),None,3)
        add_member('张志兰','female',date(1410,1,1),date(1485,12,31),3)
        add_member('刘氏','female',date(1402,1,1),date(1477,12,31),3)
        add_member('赵氏','female',date(1405,1,1),date(1480,12,31),3)
        add_member('张国栋','male',date(1425,1,1),date(1500,12,31),4)
        add_member('张国梁','male',date(1428,1,1),date(1503,12,31),4)
        add_member('张国华','male',date(1430,1,1),None,4)
        add_member('张国强','male',date(1432,1,1),None,4)
        add_member('张国秀','female',date(1435,1,1),None,4)
        add_member('孙氏','female',date(1427,1,1),date(1502,12,31),4)
        add_member('周氏','female',date(1430,1,1),date(1505,12,31),4)
        add_member('张家兴','male',date(1450,1,1),None,5)
        add_member('张家旺','male',date(1453,1,1),None,5)
        add_member('张家富','male',date(1455,1,1),None,5)
        add_member('张家贵','male',date(1457,1,1),None,5)
        add_member('张家慧','female',date(1460,1,1),None,5)

        def rel(t, a, b):
            Relationship.objects.get_or_create(
                family_id=family.id,
                from_member_id=members[a].id,
                to_member_id=members[b].id,
                relationship_type=t,
                defaults={'creator_id': 1}
            )

        rel('spouse','张德高','李氏')
        rel('parent','张德高','张文华')
        rel('parent','张德高','张文武')
        rel('parent','张德高','张文秀')
        rel('spouse','张文华','王氏')
        rel('spouse','张文武','陈氏')
        rel('parent','张文华','张志远')
        rel('parent','张文华','张志明')
        rel('parent','张文武','张志强')
        rel('parent','张文武','张志华')
        rel('parent','张文武','张志兰')
        rel('spouse','张志远','刘氏')
        rel('spouse','张志明','赵氏')
        rel('parent','张志远','张国栋')
        rel('parent','张志远','张国梁')
        rel('parent','张志明','张国华')
        rel('parent','张志华','张国强')
        rel('parent','张志华','张国秀')
        rel('spouse','张国栋','孙氏')
        rel('spouse','张国梁','周氏')
        rel('parent','张国栋','张家兴')
        rel('parent','张国栋','张家旺')
        rel('parent','张国梁','张家富')
        rel('parent','张国强','张家贵')
        rel('parent','张国强','张家慧')

        self.stdout.write(self.style.SUCCESS(f"Loaded members: {len(members)} and relationships"))
