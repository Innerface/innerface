from django.db import models


# Create your models here.

class Synonyms(models.Model):
    word = models.CharField(max_length=64, blank=False)
    parent_id = models.IntegerField()
    count = models.IntegerField()
    status = models.SmallIntegerField()
    create_time = models.DateTimeField()


class Emotional(models.Model):
    word = models.CharField(max_length=16, blank=False)
    table_type = models.CharField(max_length=32, blank=False)
    emotion_type = models.CharField(max_length=32, blank=False)
    count = models.IntegerField()
    status = models.SmallIntegerField()
    create_time = models.DateTimeField()


class Sensitive(models.Model):
    word = models.CharField(max_length=16, blank=False)
    table_type = models.CharField(max_length=32, blank=False)
    count = models.IntegerField()
    status = models.SmallIntegerField()
    create_time = models.DateTimeField()


class Business_formula(models.Model):
    name = models.CharField(max_length=64, null=False)
    descript = models.CharField(max_length=255, null=False)
    business_id = models.IntegerField()
    keywords = models.CharField(max_length=64, null=False)
    params = models.CharField(max_length=128, null=False)
    formula = models.CharField(max_length=128, null=False)
    status = models.SmallIntegerField()
    table_type = models.SmallIntegerField()

    class Meta:
        index_together = [('name',), ('business_id',)]
        # unique_together = [('name', 'business_id')]


class Business_operation(models.Model):
    name = models.CharField(max_length=64, null=False)
    step = models.SmallIntegerField()
    description = models.TextField()
    item = models.CharField(max_length=64, null=False)
    keywords = models.CharField(max_length=64, null=False)
    status = models.SmallIntegerField()
    table_type = models.SmallIntegerField()
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        index_together = [('name',), ('item',)]
        # unique_together = [('name',), ('item',)]


class Business_production(models.Model):
    product = models.CharField(max_length=32, null=False)
    name = models.CharField(max_length=32, null=False)
    business_id = models.IntegerField()
    description = models.CharField(max_length=255, null=False)
    keywords = models.CharField(max_length=32, null=False)
    status = models.SmallIntegerField()
    table_type = models.SmallIntegerField()

    class Meta:
        index_together = [('name',), ('business_id',), ('product',)]
        # unique_together = [('name',), ('business_id',)]


class Business_structure(models.Model):
    name = models.CharField(max_length=64, null=False)
    parent_id = models.IntegerField()
    level = models.IntegerField()
    path = models.CharField(max_length=255, null=False)
    bank = models.CharField(max_length=64, null=False)
    area = models.CharField(max_length=64, null=False)
    status = models.SmallIntegerField()
    table_type = models.SmallIntegerField()

    class Meta:
        index_together = [('name',), ('parent_id',), ('bank',)]


class Business_keywords(models.Model):
    keyword = models.CharField(max_length=64, null=False)
    type_id = models.SmallIntegerField()
    type_name = models.CharField(max_length=16, null=False)
    created_by = models.CharField(max_length=16, null=False)
    status = models.SmallIntegerField()
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        index_together = [('keyword',), ('type_id',)]


class Question_auto(models.Model):
    question = models.CharField(max_length=128, null=False)
    answer = models.TextField()
    agrees = models.IntegerField()
    words = models.CharField(max_length=64, null=True)
    platform = models.CharField(max_length=8, null=True)
    simi = models.CharField(max_length=32, null=True)

    class Meta:
        unique_together = [('question',)]


class Synonym_sentence(models.Model):
    type = models.IntegerField()
    sentence = models.CharField(max_length=256)
    rel_sentence_id = models.BigIntegerField(null=True)
    qid = models.IntegerField()
    flag = models.IntegerField()
    create_time = models.DateTimeField()
    create_by = models.BigIntegerField()
    update_time = models.DateTimeField()
    update_by = models.BigIntegerField()


class Question_t(models.Model):
    qid = models.IntegerField(primary_key=True)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    keyword_item = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    created_time = models.DateTimeField(null=True)
    update_time = models.DateTimeField(null=True)
    so_pair = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    is_fresh = models.IntegerField()
    q_category_id = models.BigIntegerField()
    guide_flag = models.BigIntegerField()
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
