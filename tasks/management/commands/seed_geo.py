from cities_light.models import City, Country, Region, SubRegion
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Charge un petit jeu géographique de démonstration (FR + US)."

    def handle(self, *args, **options):
        City.objects.all().delete()
        SubRegion.objects.all().delete()
        Region.objects.all().delete()
        Country.objects.all().delete()

        gid = iter(range(900000, 999999))
        data = {
            "FR": ("France", {
                "Occitanie": {"Hérault": ["Montpellier", "Lunel"]},
                "Île-de-France": {"Paris": ["Paris"]},
            }),
            "US": ("United States", {
                "California": {"Los Angeles County": ["Los Angeles", "Long Beach"]},
                "New York": {"New York County": ["New York"]},
            }),
        }
        for code2, (cname, regions) in data.items():
            country = Country.objects.create(name=cname, code2=code2, geoname_id=next(gid))
            for rname, subs in regions.items():
                region = Region.objects.create(name=rname, country=country, geoname_id=next(gid))
                for sname, cities in subs.items():
                    sub = SubRegion.objects.create(
                        name=sname, region=region, country=country, geoname_id=next(gid)
                    )
                    for cty in cities:
                        City.objects.create(
                            name=cty, subregion=sub, region=region, country=country,
                            geoname_id=next(gid),
                        )
        self.stdout.write(self.style.SUCCESS(
            f"Géo : {Country.objects.count()} pays, {Region.objects.count()} régions, "
            f"{SubRegion.objects.count()} sous-régions, {City.objects.count()} villes."
        ))
