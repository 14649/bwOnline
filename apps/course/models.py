from datetime import datetime

# 课程信息表
from django.db import models
from organization.models import CourseOrg,Teacher
from DjangoUeditor.models import UEditorField


class Course(models.Model):
    DEGREE_CHOICES = (
        ("cj", u"初级"),
        ("zj", u"中级"),
        ("gj", u"高级")
    )
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    # TextField允许我们不输入长度。可以输入到无限大。暂时定义为TextFiled，之后更新为富文本
    # detail = models.TextField(verbose_name=u"课程详情")
    detail = UEditorField(verbose_name=u'课程详情', width=600, height=300, imagePath="courses/ueditor/",
                          filePath="courses/ueditor/", default='')
    degree = models.CharField(choices=DEGREE_CHOICES, max_length=2)
    # 使用分钟做后台记录(存储最小单位)前台转换
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    # 保存学习人数:点击开始学习才算
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(
        upload_to="courses/%Y/%m",
        verbose_name=u"封面图",
        max_length=100)
    # 保存点击量，点进页面就算
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name="所属机构", null=True, blank=True)
    category = models.CharField("课程类别",max_length=20, default="")
    tag = models.CharField('课程标签',default='',max_length=10)
    youneed_know = models.CharField('课程须知',max_length=300,default='')
    teacher_tell = models.CharField('老师告诉你',max_length=300,default='')
    is_banner = models.BooleanField('是否轮播',default=False)
    teacher = models.ForeignKey(Teacher,verbose_name='讲师',null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        #获取课程的章节数
        return self.lesson_set.all().count()
    get_zj_nums.short_description = '章节数'   #在后台显示的名称

    def get_course_lesson(self):
        #获取课程的章节
        return self.lesson_set.all()

    def get_learn_users(self):
        #获取这门课程的学习用户
        return self.usercourse_set.all()[:5]

    def go_to(self):
        from django.utils.safestring import mark_safe
        #mark_safe后就不会转义
        return mark_safe("<a href='https://home.cnblogs.com/u/derek1184405959/'>跳转</a>")
    go_to.short_description = "跳转"

    def __str__(self):
        return self.name

# 章节
class Lesson(models.Model):
    # 因为一个课程对应很多章节。所以在章节表中将课程设置为外键。
    # 作为一个字段来让我们可以知道这个章节对应那个课程
    course = models.ForeignKey(Course, verbose_name=u"课程", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    def get_lesson_vedio(self):
        #获取章节所有视频
        return self.video_set.all()

    def __str__(self):
        return '《{0}》课程的章节 >> {1}'.format(self.course, self.name)

# 每章视频
class Video(models.Model):
    # 因为一个章节对应很多视频。所以在视频表中将章节设置为外键。
    # 作为一个字段来存储让我们可以知道这个视频对应哪个章节.
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=u"视频名")
    url = models.CharField('访问地址',default='',max_length=200)
    learn_times = models.IntegerField("学习时长(分钟数)",default=0)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 课程资源
class CourseResource(models.Model):
    # 因为一个课程对应很多资源。所以在课程资源表中将课程设置为外键。
    # 作为一个字段来让我们可以知道这个资源对应那个课程
    course = models.ForeignKey(Course, verbose_name=u"课程", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=u"名称")
    # 这里定义成文件类型的field，后台管理系统中会直接有上传的按钮。
    # FileField也是一个字符串类型，要指定最大长度。
    download = models.FileField(
        upload_to="course/resource/%Y/%m",
        verbose_name=u"资源文件",
        max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name

class BannerCourse(Course):
    '''显示轮播课程'''
    class Meta:
        verbose_name = '轮播课程'
        verbose_name_plural = verbose_name
        #这里必须设置proxy=True，这样就不会再生成一张表，同时还具有Model的功能
        proxy = True