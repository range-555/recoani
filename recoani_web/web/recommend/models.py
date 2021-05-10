from django.db import models


class AnimeCast(models.Model):
    anime = models.ForeignKey('Animes', models.DO_NOTHING, blank=True, null=True)
    cast = models.ForeignKey('Casts', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'anime_cast'


class AnimeGenre(models.Model):
    anime = models.ForeignKey('Animes', models.DO_NOTHING, blank=True, null=True)
    genre = models.ForeignKey('Genres', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'anime_genre'


class AnimeListPages(models.Model):
    initial = models.CharField(unique=True, max_length=10, blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'anime_list_pages'


class AnimeOtherInformation(models.Model):
    anime = models.ForeignKey('Animes', models.DO_NOTHING, blank=True, null=True)
    other_information = models.ForeignKey('OtherInformations', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'anime_other_information'


class AnimeStaff(models.Model):
    anime = models.ForeignKey('Animes', models.DO_NOTHING, blank=True, null=True)
    staff = models.ForeignKey('Staffs', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'anime_staff'


class Animes(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    title_full = models.TextField(blank=True, null=True)
    work_id = models.IntegerField(blank=True, null=True)
    outline_entire = models.TextField(blank=True, null=True)
    doc_vec = models.TextField(blank=True, null=True)
    recommend_list = models.TextField(blank=True, null=True)
    favorite = models.IntegerField(blank=True, null=True)
    producted_year = models.CharField(max_length=255, blank=True, null=True)
    is_new = models.IntegerField(blank=True, null=True)
    is_delivery = models.IntegerField(blank=True, null=True)
    is_ongoing = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=1023, blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    thumbnail_url = models.CharField(max_length=1023, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()
    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'animes'


class Casts(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    tag_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'casts'


class Genres(models.Model):
    genre = models.CharField(max_length=255, blank=True, null=True)
    genre_cd = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'genres'


class OtherInformations(models.Model):
    other_information = models.CharField(max_length=255, blank=True, null=True)
    tag_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'other_informations'


class OutlineEachEpisode(models.Model):
    anime = models.ForeignKey(Animes, models.DO_NOTHING, blank=True, null=True)
    episode_number = models.CharField(max_length=11, blank=True, null=True)
    outline = models.TextField(blank=True, null=True)
    json = models.TextField(blank=True, null=True)
    part_id = models.CharField(max_length=11, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'outline_each_episode'


class RelatedAnimes(models.Model):
    anime = models.ForeignKey(Animes, models.DO_NOTHING, blank=True, null=True)
    related_anime_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'related_animes'


class Staffs(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    tag_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'staffs'

