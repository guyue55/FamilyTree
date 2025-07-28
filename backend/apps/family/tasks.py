"""
Family应用异步任务

使用Celery处理家族相关的异步任务，如邮件发送、数据清理等。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from loguru import logger

from .models import Family, FamilyInvitation

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_family_invitation_email(self, invitation_id: int):
    """
    发送家族邀请邮件
    
    Args:
        invitation_id: 邀请ID
        
    Returns:
        Dict[str, Any]: 发送结果
    """
    try:
        invitation = FamilyInvitation.objects.get(id=invitation_id)
        family = invitation.family
        
        # 构建邀请链接
        invitation_url = f"{settings.FRONTEND_URL}/invitations/{invitation.invitation_code}"
        
        # 构建邮件内容
        subject = f"您收到了来自{family.name}的家族邀请"
        message = f"""
亲爱的 {invitation.invitee_name or invitation.invitee_email}，

您好！

您收到了来自"{family.name}"家族的邀请。

邀请详情：
- 家族名称：{family.name}
- 邀请码：{invitation.invitation_code}
- 过期时间：{invitation.expires_at.strftime('%Y-%m-%d %H:%M:%S')}

请点击以下链接接受邀请：
{invitation_url}

如果您无法点击链接，请复制以上链接到浏览器地址栏中打开。

此邀请将在 {invitation.expires_at.strftime('%Y-%m-%d %H:%M:%S')} 过期。

感谢您的使用！

家族树团队
        """.strip()
        
        # 发送邮件
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.invitee_email],
            fail_silently=False
        )
        
        logger.info(f"Invitation email sent: invitation_id={invitation_id}")
        return {
            'success': True,
            'invitation_id': invitation_id,
            'email': invitation.invitee_email
        }
        
    except FamilyInvitation.DoesNotExist:
        logger.error(f"Invitation not found: id={invitation_id}")
        return {'success': False, 'error': 'Invitation not found'}
    
    except Exception as e:
        logger.error(f"Failed to send invitation email: {e}")
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying invitation email: attempt {self.request.retries + 1}")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {'success': False, 'error': str(e)}


@shared_task
def send_family_welcome_email(user_id: int, family_id: int):
    """
    发送家族欢迎邮件
    
    Args:
        user_id: 用户ID
        family_id: 家族ID
        
    Returns:
        Dict[str, Any]: 发送结果
    """
    try:
        user = User.objects.get(id=user_id)
        family = Family.objects.get(id=family_id)
        
        # 构建家族链接
        family_url = f"{settings.FRONTEND_URL}/families/{family_id}"
        
        # 构建邮件内容
        subject = f"欢迎加入{family.name}家族"
        message = f"""
亲爱的 {user.get_full_name() or user.username}，

欢迎您加入"{family.name}"家族！

您现在可以：
- 查看家族成员信息
- 浏览家族树结构
- 参与家族活动
- 分享家族故事

请访问以下链接开始探索：
{family_url}

如果您有任何问题，请随时联系我们。

祝您使用愉快！

家族树团队
        """.strip()
        
        # 发送邮件
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        logger.info(f"Welcome email sent: user_id={user_id}, family_id={family_id}")
        return {
            'success': True,
            'user_id': user_id,
            'family_id': family_id
        }
        
    except (User.DoesNotExist, Family.DoesNotExist) as e:
        logger.error(f"User or family not found: {e}")
        return {'success': False, 'error': 'User or family not found'}
    
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_expired_invitations():
    """
    清理过期的邀请
    
    Returns:
        Dict[str, Any]: 清理结果
    """
    try:
        # 查找过期的待处理邀请
        expired_invitations = FamilyInvitation.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        
        count = expired_invitations.count()
        
        # 批量更新状态
        expired_invitations.update(status='expired')
        
        logger.info(f"Cleaned up {count} expired invitations")
        return {
            'success': True,
            'cleaned_count': count
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired invitations: {e}")
        return {'success': False, 'error': str(e)}