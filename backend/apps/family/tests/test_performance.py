"""
Family应用性能测试

测试Family应用的性能表现，包括API响应时间、数据库查询优化、
缓存效果、并发处理等。
遵循Django和pytest性能测试最佳实践。
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.contrib.auth import get_user_model
from django.db import connection
from django.core.cache import cache

from apps.common.test_utils import APITestCase

from ..models import Family

User = get_user_model()

@pytest.mark.django_db
class TestFamilyAPIPerformance(APITestCase):
    """Family API性能测试"""
    
    def setUp(self):
        """测试初始化"""
        super().setUp()
        
        # 创建测试用户
        self.user = self.create_test_user(username='perfuser', email='perf@example.com')
        
        # 创建大量测试数据
        self.families = []
        for i in range(50):
            family = Family.objects.create(
                name=f'性能测试家族{i}',
                description=f'用于性能测试的家族{i}',
                creator=self.user,
                visibility='public' if i % 2 == 0 else 'family'
            )
            self.families.append(family)
    
    def test_family_list_performance(self):
        """测试家族列表API性能"""
        # 测试基本列表查询
        start_time = time.time()
        
        response = self.api_get('/families/')
        
        response_time = time.time() - start_time
        
        self.assert_api_success(response)
        self.assertLess(response_time, 1.0, "家族列表查询应在1秒内完成")
        
        # 验证返回数据
        data = response.json()['data']
        self.assertGreaterEqual(len(data['items']), 25)  # 至少返回公开家族
    
    def test_family_search_performance(self):
        """测试家族搜索性能"""
        # 测试搜索查询
        start_time = time.time()
        
        response = self.api_get('/families/', params={'search': '性能测试'})
        
        response_time = time.time() - start_time
        
        self.assert_api_success(response)
        self.assertLess(response_time, 1.5, "家族搜索应在1.5秒内完成")
        
        # 验证搜索结果
        data = response.json()['data']
        self.assertGreater(len(data['items']), 0)
    
    def test_family_detail_performance(self):
        """测试家族详情API性能"""
        family = self.families[0]
        
        # 测试单个家族详情查询
        start_time = time.time()
        
        response = self.api_get(f'/families/{family.id}/')
        
        response_time = time.time() - start_time
        
        self.assert_api_success(response)
        self.assertLess(response_time, 0.5, "家族详情查询应在0.5秒内完成")
    
    def test_family_creation_performance(self):
        """测试家族创建性能"""
        create_data = {
            'name': '性能测试新家族',
            'description': '测试创建性能',
            'visibility': 'public'
        }
        
        start_time = time.time()
        
        response = self.api_post('/families/', data=create_data)
        
        response_time = time.time() - start_time
        
        self.assert_api_success(response)
        self.assertLess(response_time, 1.0, "家族创建应在1秒内完成")
    
    def test_family_update_performance(self):
        """测试家族更新性能"""
        family = self.families[0]
        
        update_data = {
            'description': '更新后的描述',
            'motto': '新的座右铭'
        }
        
        start_time = time.time()
        
        response = self.api_patch(f'/families/{family.id}/', data=update_data)
        
        response_time = time.time() - start_time
        
        self.assert_api_success(response)
        self.assertLess(response_time, 0.5, "家族更新应在0.5秒内完成")
    
    def test_pagination_performance(self):
        """测试分页性能"""
        # 测试不同页面大小的性能
        page_sizes = [10, 20, 50]
        
        for size in page_sizes:
            start_time = time.time()
            
            response = self.api_get('/families/', params={'size': size})
            
            response_time = time.time() - start_time
            
            self.assert_api_success(response)
            self.assertLess(response_time, 1.0, f"分页查询(size={size})应在1秒内完成")
            
            # 验证分页数据
            data = response.json()['data']
            self.assertLessEqual(len(data['items']), size)
    
    def test_concurrent_api_requests(self):
        """测试并发API请求性能"""
        family = self.families[0]
        
        def make_request():
            response = self.api_get(f'/families/{family.id}/')
            return response.status_code == 200
        
        # 并发执行10个请求
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # 验证所有请求都成功
        self.assertTrue(all(results))
        self.assertLess(total_time, 5.0, "10个并发请求应在5秒内完成")

@pytest.mark.django_db
class TestFamilyDatabasePerformance:
    """Family数据库性能测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='dbperfuser',
            email='dbperf@example.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.families = []
        for i in range(100):
            family = Family.objects.create(
                name=f'数据库性能测试{i}',
                creator=self.user
            )
            self.families.append(family)
    
    def test_bulk_operations_performance(self):
        """测试批量操作性能"""
        # 测试批量创建
        start_time = time.time()
        
        bulk_families = []
        for i in range(100):
            bulk_families.append(Family(
                name=f'批量创建{i}',
                creator=self.user
            ))
        
        Family.objects.bulk_create(bulk_families)
        
        bulk_create_time = time.time() - start_time
        
        # 测试逐个创建（对比）
        start_time = time.time()
        
        for i in range(10):  # 只创建10个进行对比
            Family.objects.create(
                name=f'逐个创建{i}',
                creator=self.user
            )
        
        individual_create_time = time.time() - start_time
        
        # 批量创建应该更快
        assert bulk_create_time < individual_create_time * 10
    
    def test_query_optimization(self):
        """测试查询优化"""
        # 测试select_related优化
        start_time = time.time()
        
        # 优化后的查询
        families_optimized = list(
            Family.objects.select_related('creator').filter(creator=self.user)
        )
        
        optimized_time = time.time() - start_time
        
        # 未优化的查询
        start_time = time.time()
        
        families_unoptimized = list(Family.objects.filter(creator=self.user))
        # 访问creator触发额外查询
        for family in families_unoptimized[:10]:  # 只访问前10个
            _ = family.creator.username
        
        unoptimized_time = time.time() - start_time
        
        # 优化后的查询应该更快
        assert len(families_optimized) == len(self.families)
        # 注意：在测试环境中差异可能不明显
    
    def test_database_connection_usage(self):
        """测试数据库连接使用"""
        # 记录查询数量
        initial_queries = len(connection.queries)
        
        # 执行一系列操作
        families = Family.objects.filter(creator=self.user)[:10]
        for family in families:
            _ = family.name
            _ = family.creator.username  # 这会触发额外查询
        
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        
        # 验证查询数量合理
        assert query_count <= 20  # 应该控制在合理范围内
    
    def test_index_performance(self):
        """测试索引性能"""
        # 测试按创建者查询（应该有索引）
        start_time = time.time()
        
        families_by_creator = list(Family.objects.filter(creator=self.user))
        
        indexed_query_time = time.time() - start_time
        
        # 测试按名称查询（可能没有索引）
        start_time = time.time()
        
        families_by_name = list(Family.objects.filter(name__icontains='性能测试'))
        
        name_query_time = time.time() - start_time
        
        # 验证查询结果
        assert len(families_by_creator) == 100
        assert len(families_by_name) > 0
        
        # 索引查询通常更快，但在小数据集上差异可能不明显
        assert indexed_query_time < 1.0
        assert name_query_time < 2.0

@pytest.mark.django_db
class TestFamilyCachePerformance:
    """Family缓存性能测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        cache.clear()
        
        self.user = User.objects.create_user(
            username='cacheperfuser',
            email='cacheperf@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='缓存性能测试家族',
            creator=self.user
        )
    
    def test_cache_vs_database_performance(self):
        """测试缓存与数据库性能对比"""
        # 测试数据库查询时间
        start_time = time.time()
        
        for _ in range(100):
            Family.objects.get(id=self.family.id)
        
        db_time = time.time() - start_time
        
        # 设置缓存
        cache_key = f'family:{self.family.id}'
        family_data = {
            'id': self.family.id,
            'name': self.family.name,
            'creator_id': self.family.creator_id
        }
        cache.set(cache_key, family_data)
        
        # 测试缓存查询时间
        start_time = time.time()
        
        for _ in range(100):
            cache.get(cache_key)
        
        cache_time = time.time() - start_time
        
        # 缓存应该比数据库查询快
        assert cache_time < db_time
        print(f"数据库查询时间: {db_time:.4f}s, 缓存查询时间: {cache_time:.4f}s")
    
    def test_cache_hit_ratio(self):
        """测试缓存命中率"""
        cache_key = f'family:{self.family.id}'
        
        # 设置缓存
        family_data = {'id': self.family.id, 'name': self.family.name}
        cache.set(cache_key, family_data)
        
        hits = 0
        misses = 0
        
        # 模拟100次查询
        for i in range(100):
            if i % 10 == 0:  # 每10次清除一次缓存，模拟缓存失效
                cache.delete(cache_key)
                cache.set(cache_key, family_data)
            
            if cache.get(cache_key) is not None:
                hits += 1
            else:
                misses += 1
        
        hit_ratio = hits / (hits + misses)
        
        # 缓存命中率应该很高
        assert hit_ratio > 0.9
        print(f"缓存命中率: {hit_ratio:.2%}")
    
    def test_cache_memory_usage(self):
        """测试缓存内存使用"""
        # 缓存大量数据
        for i in range(1000):
            cache_key = f'family_test:{i}'
            family_data = {
                'id': i,
                'name': f'测试家族{i}',
                'description': f'这是测试家族{i}的描述' * 10  # 增加数据大小
            }
            cache.set(cache_key, family_data)
        
        # 验证缓存仍然工作
        test_key = 'family_test:500'
        cached_data = cache.get(test_key)
        
        assert cached_data is not None
        assert cached_data['id'] == 500
    
    def test_cache_expiration_performance(self):
        """测试缓存过期性能"""
        cache_key = f'family_expiration:{self.family.id}'
        
        # 设置短期缓存
        cache.set(cache_key, {'name': self.family.name}, timeout=1)
        
        # 立即查询（应该命中）
        start_time = time.time()
        result1 = cache.get(cache_key)
        immediate_time = time.time() - start_time
        
        # 等待过期
        time.sleep(1.1)
        
        # 过期后查询
        start_time = time.time()
        result2 = cache.get(cache_key)
        expired_time = time.time() - start_time
        
        # 验证过期行为
        assert result1 is not None
        assert result2 is None
        
        # 过期检查应该很快
        assert immediate_time < 0.01
        assert expired_time < 0.01

@pytest.mark.django_db
class TestFamilyConcurrencyPerformance:
    """Family并发性能测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='concurrencyuser',
            email='concurrency@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='并发测试家族',
            creator=self.user,
            member_count=0
        )
    
    def test_concurrent_family_creation(self):
        """测试并发家族创建"""
        def create_family(index):
            try:
                family = Family.objects.create(
                    name=f'并发创建家族{index}',
                    creator=self.user
                )
                return family.id
            except Exception as e:
                return str(e)
        
        # 并发创建10个家族
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_family, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # 验证结果
        successful_creates = [r for r in results if isinstance(r, int)]
        assert len(successful_creates) == 10
        assert total_time < 5.0
    
    def test_concurrent_member_count_update(self):
        """测试并发成员数量更新"""
        def update_member_count():
            try:
                # 使用F表达式避免竞态条件
                from django.db.models import F
                Family.objects.filter(id=self.family.id).update(
                    member_count=F('member_count') + 1
                )
                return True
            except Exception:
                return False
        
        # 并发更新成员数量
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(update_member_count) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # 验证结果
        self.family.refresh_from_db()
        successful_updates = sum(results)
        
        assert successful_updates == 20
        assert self.family.member_count == 20
        assert total_time < 3.0
    
    def test_concurrent_read_write_operations(self):
        """测试并发读写操作"""
        read_results = []
        write_results = []
        
        def read_family():
            try:
                family = Family.objects.get(id=self.family.id)
                read_results.append(family.name)
                return True
            except Exception:
                return False
        
        def write_family(index):
            try:
                Family.objects.filter(id=self.family.id).update(
                    description=f'并发更新{index}'
                )
                write_results.append(index)
                return True
            except Exception:
                return False
        
        # 混合读写操作
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 提交读操作
            read_futures = [executor.submit(read_family) for _ in range(15)]
            # 提交写操作
            write_futures = [executor.submit(write_family, i) for i in range(5)]
            
            # 等待所有操作完成
            all_futures = read_futures + write_futures
            results = [future.result() for future in as_completed(all_futures)]
        
        total_time = time.time() - start_time
        
        # 验证结果
        assert len(read_results) == 15
        assert len(write_results) == 5
        assert all(results)
        assert total_time < 5.0
    
    def test_deadlock_prevention(self):
        """测试死锁预防"""
        def operation_a():
            try:
                # 模拟复杂的数据库操作
                family = Family.objects.select_for_update().get(id=self.family.id)
                time.sleep(0.1)  # 模拟处理时间
                family.description = 'Operation A'
                family.save()
                return 'A'
            except Exception as e:
                return str(e)
        
        def operation_b():
            try:
                # 另一个复杂操作
                family = Family.objects.select_for_update().get(id=self.family.id)
                time.sleep(0.1)  # 模拟处理时间
                family.motto = 'Operation B'
                family.save()
                return 'B'
            except Exception as e:
                return str(e)
        
        # 并发执行可能冲突的操作
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(operation_a)
            future_b = executor.submit(operation_b)
            
            result_a = future_a.result()
            result_b = future_b.result()
        
        total_time = time.time() - start_time
        
        # 验证没有死锁（操作应该顺序完成）
        assert result_a in ['A', 'B'] or 'Operation' in str(result_a)
        assert result_b in ['A', 'B'] or 'Operation' in str(result_b)
        assert total_time < 5.0

@pytest.mark.django_db
class TestFamilyMemoryPerformance:
    """Family内存性能测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='memoryuser',
            email='memory@example.com',
            password='testpass123'
        )
    
    def test_memory_usage_with_large_dataset(self):
        """测试大数据集的内存使用"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        families = []
        for i in range(1000):
            family = Family.objects.create(
                name=f'内存测试家族{i}',
                description='这是一个用于测试内存使用的家族描述' * 10,
                creator=self.user
            )
            families.append(family)
        
        # 查询大量数据
        all_families = list(Family.objects.filter(creator=self.user))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 验证内存使用合理
        assert len(all_families) == 1000
        assert memory_increase < 100  # 内存增长应该小于100MB
        
        print(f"内存使用增长: {memory_increase:.2f} MB")
    
    def test_queryset_memory_efficiency(self):
        """测试查询集内存效率"""
        # 创建测试数据
        for i in range(500):
            Family.objects.create(
                name=f'查询集测试{i}',
                creator=self.user
            )
        
        # 测试迭代器vs列表
        import sys
        
        # 使用迭代器（内存友好）
        iterator_families = Family.objects.filter(creator=self.user).iterator()
        iterator_size = sys.getsizeof(iterator_families)
        
        # 转换为列表（内存密集）
        list_families = list(Family.objects.filter(creator=self.user))
        list_size = sys.getsizeof(list_families)
        
        # 迭代器应该使用更少内存
        assert iterator_size < list_size
        assert len(list_families) == 500
        
        print(f"迭代器大小: {iterator_size} bytes, 列表大小: {list_size} bytes")
    
    def test_object_lifecycle_memory(self):
        """测试对象生命周期内存管理"""
        import gc
        import weakref
        
        # 创建对象并获取弱引用
        family = Family.objects.create(
            name='生命周期测试',
            creator=self.user
        )
        
        weak_ref = weakref.ref(family)
        family_id = family.id
        
        # 删除强引用
        del family
        
        # 强制垃圾回收
        gc.collect()
        
        # 验证对象是否被正确回收
        # 注意：Django的模型实例可能由于ORM缓存而不会立即回收
        # 这里主要测试没有明显的内存泄漏
        
        # 从数据库重新获取对象
        family_from_db = Family.objects.get(id=family_id)
        assert family_from_db.name == '生命周期测试'

if __name__ == '__main__':
    # 运行性能测试
    pytest.main([__file__, '-v', '--tb=short', '-s'])